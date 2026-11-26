"""Optional: add Module 6a navigation to an existing portfolio root README.

Run from repo root: uv run python Module06a/update_portfolio_readme.py
Idempotent: existing Module 06a links are left unchanged.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / 'README.md'
INDEX = ('- [Module 06a — The Analytical Engine (DuckDB)](Module06a/README.md) '
         '— Parquet, verified SQL race, plan, OLTP boundary and memo\n')
HIGHLIGHT = '''## Module 06a highlights

- [DuckDB analytical lab](Module06a/README.md) recreates the Module 05 history as two million rows and checks a Parquet copy.
- [Reproducible benchmark](Module06a/run_module6a.py) checks equivalent queries and records SQLite-vs-DuckDB medians, plans and OLTP boundary tests.
- [Decision memo](Module06a/memo.md) · [Studio notes](Module06a/duckdb-notes.md) · [Reflection 06a](Reflections/ref06a.md).
- Local `.db`, `.csv` and `.parquet` artefacts remain excluded from GitHub.

'''


def main():
    if not README.exists():
        raise SystemExit('Root README.md missing. Run from your existing portfolio.')
    text = README.read_text(encoding='utf-8')
    if '(Module06a/README.md)' not in text:
        anchor = '## Module 01 highlights'
        if anchor not in text:
            raise SystemExit('README layout not recognized. Add Module 06a link manually.')
        text = text.replace(anchor, INDEX + '\n' + anchor, 1)
        print('Added module index link.')
    if '## Module 06a highlights' not in text:
        anchor = '## Task Pod'
        if anchor not in text:
            raise SystemExit('README layout not recognized. Add highlights manually.')
        text = text.replace(anchor, HIGHLIGHT + anchor, 1)
        print('Added highlights section.')
    README.write_text(text, encoding='utf-8')
    print('README.md updated (safe to rerun).')


if __name__ == '__main__':
    main()
