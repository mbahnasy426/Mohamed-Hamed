# Module 06b — Engine notes and one-page decision record

**Owner:** Adam Salman · **Case:** Kortmann plant.  
Sources: [Module 6b instructions](https://github.com/iotempire/iotempire-teaching/blob/main/full-classes/hsbi-databases-10d/modules/06b-polyglot-persistence.md), [Module 4 evidence](../Module04/results.txt), [Module 5 evidence](../Module05/results.txt), [Module 6a memo](../Module06a/memo.md), and [Module 6b experiment output](results.txt).

## Task 1 — shared PostgreSQL server (classroom observation)

**Actual classroom work on the instructor's pgweb server:** Connected successfully to database `pod15` and queried the existing `machine` table. The existing machine 1 row was at `guetersloh` and had `parts_produced=0`; machine 2 at `bielefeld` had `parts_produced=0`. Executed SELECT, used an explicit machine ID for INSERT / verified the row existed, and ran `UPDATE machine SET parts_produced = parts_produced + 1 WHERE machine_id = 1` in two separate browsers. The subsequent SELECT returned `parts_produced=3`: three increments had occurred across the attempts, **not** proof that two writers held conflicting transactions simultaneously.

**Actual server-outage observation:** The instructor stopped PostgreSQL; the pgweb query failed while the database service was unavailable. After the instructor restarted the service, the same query worked again. This verifies an additional remote-server failure mode, but does not by itself prove persistence across every failure scenario.

Three observations:
1. **Easier:** Two browser clients can access and update the same central database, without sharing a local SQLite file.
2. **Harder:** The client must connect to a remote endpoint with credentials, and depends on that service being available.
3. **Server-only failure mode:** Stopping the shared server made queries fail for clients even though their SQL did not change; when the service returned, querying worked again.

**Concurrent-writer lock/wait observation:** **Still unverified.** We ran fast autocommit updates, not a demonstrated transaction held open during a competing writer's attempt. If the instructor runs a locking demo, add the actual wait/block result here.

**Separate local fallback** (not the PostgreSQL evidence): `local_boundary.py` intentionally holds `BEGIN IMMEDIATE` open in SQLite. A second connection receives `database is locked`; after commit and retry the result is 2. The atomic SQL increment avoids an application-side read-modify-write race.

## Task 2 — JSON and key–value comparison

- **Why the vendor index works only in one query:** SQLite expression indexes are based on the *expression written in the query*. An index on `json_extract(meta, '$.vendor')` matches that expression and returns `SEARCH`; the semantically equivalent `meta ->> 'vendor'` is another expression and returns `SCAN`. [Measured plans](results.txt).
- **Why flexible JSON is still designed:** `CHECK(json_valid(meta))` rejected malformed JSON. JSON can add unknown vendor attributes without a migration. Frequently filtered stable fields could later become typed generated columns; arbitrary JSON keys need application documentation and deliberate indexes.
- **Session state choice:** `shelve` is easy for Python key lookup but has no SQL grouping; a SQLite primary-key table handles both lookup and cross-session analysis. Separate measured timings on the 20,000-key test host: shelve set/get **3.957/0.100 s**; SQLite set/get **0.027/0.095 s**. SQLite's writes used one batch transaction and shelve used `dbm.sqlite3`, so the large write difference must not be interpreted as pure engine superiority. The four grouping buckets each had 5,000 sessions and 25 distinct users.

### ACID, BASE, CAP in this portfolio

- **ACID:** Module 4's replay-safe UPSERT kept 11 readings after two CSV ingestions and rejected broken values via constraints. Transactional atomicity/isolation/durability matter for the source of truth.
- **BASE / eventual consistency analogy:** The nightly Parquet export proposed in Module 6a is a *potentially stale derived copy*, not itself a distributed BASE database. A new operational row may be absent until refresh. That is an eventual-freshness trade-off, not proof of BASE guarantees.
- **CAP:** CAP addresses consistency versus availability **during a network partition in a distributed system**. Single-file SQLite is not a distributed CAP system; one remotely accessed PostgreSQL server adds availability dependence on a network but is not automatically an AP/CP distributed cluster. A future replicated setup would need an explicit partition policy.

## One-page engine decision record

| Workload | Engine | Why / course evidence | Cost accepted | If unavailable or stale |
|---|---|---|---|---|
| Sensor/job ingest every 30 s | **SQLite** | Module 4's constraints rejected bad data; replaying CSV twice left **11 total rows and zero duplicate natural keys** | Single-writer coordination, backups | Treat as authoritative; retry transactions safely, never replace it with an unchecked copy |
| Month-end report over two years | **DuckDB reading checked Parquet copy** | Module 6a implemented an equivalent 2M-row history and comparison runner, but own-device performance measurements are **pending**; the professor's *reference example* is approx. **600 ms vs 6 ms** (not Adam's result). Module 5 *did* measure 57.603 ms for its 200k-row report query on a different workload | Separate snapshot, scheduled refresh, reconciliation, freshness timestamp | Missing or stale shift distorts report; keep last validated copy and show an “as of” time |
| Vendor metadata with changing fields | **SQLite JSON column** | 1,000-device generated dataset; malformed JSON rejected, new field read without migration; expression-index query **SEARCH** vs shorthand **SCAN** on 334 matching vendors | Weaker field-level typing; must match expression when filtering | Validate incoming JSON; stable promoted keys may need migration/index management |
| Dashboard session state | **SQLite key–value table** | This test environment: 20,000 keys, SQLite 0.027 s write / 0.095 s read, shelve 3.957 s write / 0.100 s read; `GROUP BY` across sessions possible | A SQL schema and explicit transaction management | Sessions can expire and be recreated; ensure TTL/privacy policy in production |
| Optional concurrent network users | **PostgreSQL server** *if required* | Shared pgweb SELECT/INSERT/UPDATE and server-outage/recovery observed in pod15; two-writer lock wait **not observed**; local SQLite fallback showed blocking | Network, authentication, deployment and outage risk | Server/network failure affects all remote users; use failover/retry plans if the requirement merits the cost |

**If Kortmann could run only one engine:** **SQLite.** It offers transactions, integrity checks, flexible JSON, and indexed lookups without additional server operations. **The first workload to suffer would be long historical reports** competing with operational writes; Module 6a proposes moving those scans to a checked Parquet copy, but its own-device speedup remains to be measured. At greater network-user concurrency, a server also becomes worth considering.

## Defence questions / change log

- Which engine choice is supported by actual *Adam* measurements, which by this execution environment, and which by instructor reference?
- Who refreshes Parquet, checks counts and price totals, and publishes a freshness timestamp?
- What happens with two simultaneous writers, and how do transactions prevent double counting?
- Why not several spreadsheets? We need constraints, joins, reproducible imports, audit and reliable queries.
- **Pod defence:** not yet performed. After a real cross-pod exchange, record the other pod's question, one changed decision row (if any), and why it changed.
- **Still missing:** own-device key-value results and Module 6a benchmark; PostgreSQL lock/wait observation; real peer defence.
