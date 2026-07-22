# star-schema

*Curating scientific information, with modern data tech.*

A map of stars, kept in a dimensional star schema.
This repository gathers astronomy's hottest & brightest data
into a small, reproducible [DuckDB](https://duckdb.org) warehouse
modeled with [dbt](https://www.getdbt.com): the constellations and their shapes,
stellar traits and names.
Seeds declare facts with provenance, models derive everything else,
and tests pin the numbers to uphold our sky's integrity.

[tjohncan.github.io/star-schema/](https://tjohncan.github.io/star-schema/)

## The museum

The centerpiece lives in `museum/almagest/`:
all 1,028 stars of Ptolemy's *Almagest* (c. 150 AD)
— the oldest surviving star catalogue —
in the 1528 Trapezuntius Latin as printed by Peters & Knobel (1915),
each star description paired with an original English translation
and a standalone picture caption
(Ptolemy's relative references — "the middle of them" — resolved,
so every star reads on its own),
plus figure descriptions and named stroke polylines
to draw all 48 ancient constellations.
The text was extracted from the public-domain 1915 edition,
validated row-by-row against the machine-readable catalogue
of Verbunt & van Gent (2012), and reviewed by hand against PDF page-scans.
The museum directory holds the artifacts.

## The warehouse

`dbt/star_schema/` joins the museum to the modern sky.
Four carried extracts (see [SOURCES.md](SOURCES.md)) bridge
Ptolemy's Baily numbers to Hipparcos identifiers,
onward to the Yale Bright Star Catalogue,
and to the IAU's official proper names —
so Baily 469, "the one in the heart, called Regulus,"
lands on α Leonis with J2000 coordinates,
a modern magnitude, and its etymology.
The gold layer serves four `atlas_*` tables:
every member placed, every figure drawable, every scene framed.

## The atlas

`payloads/almagest_atlas/` renders the whole catalogue as one
self-contained `index.html` — no server, no network, opens from a file.
`build.py` reads the warehouse and inlines everything;
the page draws each constellation on the real sky,
stroke by stroke over the naked-eye backdrop,
with every star tappable: its caption, its book line in Latin and English,
its modern identity, and its adjacent edges (as we've interpreted).

## Layout

```
star-schema/
├── museum/           # primary artifacts: public domain + our contributions (CC0)
│   └── almagest/     #  Ptolemy's 1,028 stars — Latin + English + captions CSV, figures TOML
├── data/             # third-party-derived data — upstream terms apply; see SOURCES.md
│   ├── fetched/      #  fetched upstream bytes (gitignored)
│   └── prepared/     #  carried extracts, each with a ledger entry
├── scripts/          # provisioning: fetchers, extractors, museum → seed builders
├── dbt/star_schema/  # the warehouse (dbt + DuckDB)
│   ├── seeds/        #  declared inputs — CC0; some static (ours), some museum-generated
│   ├── models/       #  staging views over seeds & sources → gold atlas tables
│   └── ...
├── payloads/         # deliverables built from the warehouse (the Almagest Atlas)
├── SOURCES.md        # license discussion / citations / provenance ledger
└── requirements.txt  # Python setup
```

Seeds generated from `museum/` are
built by script and never hand-edited; the cleanliness check is mechanical
(regenerate, and `git diff` must come back clean).
The same contract covers the atlas: rebuild it, and the bytes must not move.

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

Then, to see the sky:

```bash
python payloads/almagest_atlas/build.py   # writes payloads/almagest_atlas/index.html
```

... and open `index.html` in a browser.

## Licensing & provenance

Everything original to this repository — code, curated seeds, the museum
artifacts, the translations, captions, and figure drawings — is dedicated
to the public domain under [CC0](LICENSE).
The exception is `data/`, which holds material derived
from third-party scientific sources and retains each upstream's terms.
Every source — URL, retrieval date, terms, citation — is recorded in
[SOURCES.md](SOURCES.md), along with the carry-or-fetch policy behind it.
What we carry, we cite; what isn't carried may be fetched.
