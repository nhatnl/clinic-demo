# ICD-10-CM data import

This project imports the official **FY 2026 ICD-10-CM release effective April 1, 2026** from the CDC's National Center for Health Statistics (NCHS):

- [`icd10c-tabular-April-1-2026.xml`](data/icd10c-tabular-April-1-2026.xml) supplies the code hierarchy and parent-child relationships.
- [`icd10cm-order-April-1-2026.txt`](data/icd10cm-order-April-1-2026.txt) supplies the billable/submission flag, short name, and long description.

The original archives are available from the [CDC ICD-10-CM files page](https://www.cdc.gov/nchs/icd/icd-10-cm/files.html) and its [April 1, 2026 download directory](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2026-update/).

## Why use the release files instead of scraping ICD10Data.com?

The CDC/NCHS files are the authoritative, machine-readable release of ICD-10-CM. Pinning the April 1, 2026 files makes imports reproducible and reviewable, preserves the official hierarchy and submission-validity fields, and allows the importer to run without network access.

[ICD10Data.com](https://www.icd10data.com/ICD10CM/Codes) is useful for interactive lookup, but it is a third-party website intended for browsing. Scraping its HTML would couple the importer to page structure and site availability, could silently change the imported dataset, and would make it harder to prove which release was loaded.

## Commands

Run commands from the `backend` directory.

### Dry run

Parse and print a small sample without connecting to or writing to the database:

```bash
uv run python script/parse_icd10cm_data.py --limit 10
```

Omit `--limit 10` to validate the complete source files.

### Import

Apply the database migrations, then import the complete dataset:

```bash
uv run alembic upgrade head
uv run python script/import_icd10cm_data.py
```

The import is safe to run multiple times. It inserts new codes and updates existing rows matched by the `code` primary key.
