# star-schema

*Curating scientific information, with modern data tech.*

A map of the stars, kept in a dimensional star schema.
This repository curates astronomy's reference data
into a small, reproducible [DuckDB](https://duckdb.org) warehouse
modeled with [dbt](https://www.getdbt.com): the constellations and their boundaries,
the bright stars and their names.
Seeds declare facts with provenance, models derive everything else,
and tests pin the numbers to uphold our sky's integrity.

## The museum

The centerpiece lives in `museum/almagest/`:
all 1,028 stars of Ptolemy's *Almagest* (c. 150 AD)
— the oldest surviving star catalogue —
in the 1528 Trapezuntius Latin as printed by Peters & Knobel (1915),
each star description paired with an original English translation,
plus figure descriptions and named stroke polylines
to draw all 48 ancient constellations.
The text was extracted from the public-domain 1915 edition,
validated row-by-row against the machine-readable catalogue
of Verbunt & van Gent (2012), and reviewed by hand against PDF page-scans.
The museum directory holds the artifacts.

## Layout

```
star-schema/
├── museum/           # primary artifacts: public domain + our contributions (CC0)
│   └── almagest/     #  Ptolemy's 1,028 stars — Latin + English CSV, figures TOML
├── data/             # third-party-derived data — upstream terms apply; see SOURCES.md
│   ├── fetched/      #  fetched upstream bytes (gitignored)
│   └── prepared/     #  carried extracts, each with a ledger entry
├── scripts/          # provisioning: fetchers, extractors, museum → seed builders
├── dbt/star_schema/  # the warehouse (dbt + DuckDB)
│   ├── seeds/        #  declared inputs — CC0; some static (ours), some museum-generated
│   ├── models/       #  outputs (toward query-ready tables)
│   └── ...
├── SOURCES.md        # license discussion / citations / provenance ledger
└── requirements.txt  # Python setup
```

Seeds generated from `museum/` are
built by script and never hand-edited; the cleanliness check is mechanical
(regenerate, and `git diff` must come back clean).

## Quickstart

```bash
# activate venv at repo-root
pip install -r requirements.txt
cd dbt/star_schema
dbt build
```

Everything materializes into a single local file, `dev.duckdb` — no server,
no credentials, and no network: a fresh clone builds offline by design.
Explore with any DuckDB client, for instance:

```python
import duckdb
print(duckdb.connect('dev.duckdb').sql('show all tables'))
```

## Licensing & provenance

Everything original to this repository — code, curated seeds, the museum
artifacts, the translations and figure drawings — is dedicated
to the public domain under [CC0](LICENSE).
The exception is `data/`, which holds material derived
from third-party scientific sources and retains each upstream's terms.
Every source — URL, retrieval date, terms, citation — is recorded in
[SOURCES.md](SOURCES.md), along with the carry-or-fetch policy behind it.
What we carry, we cite; what isn't carried may be fetched.
