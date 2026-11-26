# Module 06a — Decision memo (pending local benchmark)

**To:** Lea Winter and Yasmin Kaya  
**Subject:** Separating operational writes from the historical report

I recommend keeping live job updates, point lookups and write transactions in SQLite while preparing a separate Parquet-based history copy for DuckDB to analyze. The same dashboard and monthly queries should be checked for identical results in both engines before comparing five-run median timings. The SQLite dashboard median is **[run the script] ms** and the DuckDB dashboard median is **[run the script] ms**; the corresponding monthly medians and compression sizes should come from `metrics.json`. I would refresh the analytical copy at the end of every shift or nightly, verify row count and the summed price against SQLite, and publish only a validated copy. If a refresh fails silently, the monthly report could omit recent jobs despite running quickly, so every report needs a visible 'data as of' timestamp and refresh-failure alert. I would not move high-frequency single-row inserts and point lookups to DuckDB without measured evidence, since the workload is transaction-oriented rather than scan-oriented. I would also add stronger key-level reconciliation if the numbers are used for financial decisions, because equal counts and price totals do not prove equal rows.

> This file is an **evidence-safe placeholder**. `run_module6a.py` overwrites it with a short decision memo containing actual local measured numbers **only after all rounds succeed**. Do not submit bracketed placeholders as measured evidence.
