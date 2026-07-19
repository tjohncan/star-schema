# Ptolemy's Star Catalogue — Latin, English, and Figure Edge Sets

Two companion files reconstruct the oldest surviving star catalogue — the 1,028
stars of Ptolemy's *Almagest* (c. 150 AD) — as modern, joinable seed data.

**`almagest_stars.csv`** — one row per star, exactly as the book orders them:
the Baily number (the scholarly standard numbering, 1–1028), the constellation
(as its modern 3-letter abbreviation; Ptolemy's 48 map onto 50 modern
constellations after Argo Navis was split), whether the star is part of the
constellation *figure* or one of Ptolemy's 108 *unformed* stars (ἀμόρφωτοι —
catalogued neighbours lying outside the figure), its sequence within that
section, the star's **Latin description** — its anatomical place in the figure
("Quae est in corde et vocatur Regulus": *the one in the heart, called
Regulus*) — and our **English translation**.

**`almagest_figures.toml`** — per-constellation figure prose and edge sets.
Each constellation carries a short description of its overall shape and story,
then named *strokes*: polylines through figure-star sequence numbers, with
comments at the star-group level. Strokes follow Ptolemy's anatomy wherever it
speaks (his *figura quadrilatera* in Ursa Major **is** the Big Dipper's bowl);
where the anatomy is silent the connections are our artistic license, and say
so. Unformed stars receive no edges, ever — Arcturus itself floats free beside
Boötes, exactly as Ptolemy left it.

**In this repository.** These two files are the authoritative artifacts; the
dbt seeds under `dbt/star_schema/seeds/almagest/` are generated from them by
`scripts/build_seeds.py`, which re-validates the full contract on every run
(1,028 stars with Baily numbers complete, per-section sequences contiguous,
declared figure/unformed counts matching the rows, every figure star drawn by
at least one stroke, unformed stars drawn by none). Generated seeds are never
hand-edited; to propose a correction, edit the museum files and regenerate.

**Sources & provenance.** The Latin text is the Trapezuntius translation
(1528), revised from the Greek, as printed in Peters & Knobel, *Ptolemy's
Catalogue of Stars* (Carnegie Institution, 1915; public domain) — extracted
from the Internet Archive's scan, then validated row-by-row against the
machine-readable catalogue of Verbunt & van Gent (A&A 544, A31, 2012), whose
per-constellation counts, formed/unformed flags, and sequence numbers served
as a parsing contract, and hand-reviewed against the page scans. To attach
modern identifiers (Hipparcos, and onward to Gaia), join `baily` against
Verbunt & van Gent's table — that mapping is theirs, cited, and deliberately
not duplicated here; see the repository's [SOURCES.md](../../SOURCES.md)
ledger. Greek terms the book left untranslated are restored as Greek
(γλυφίδος, the arrow's notch; χηνίσκου, the goose-head stern ornament).

English translations and edge sets are original work, released CC0.
Errors are ours.
