# SOURCES — the provenance ledger

This file accounts for every third-party source feeding this project:
what we took, where from, when, under what terms, and our citations.

## Policy

Sources fall into three tiers:

1. **Public domain.** Original work (translations, figure drawings,
   hand-curated seeds, code) and material derived from public-domain sources.
   Lives anywhere in the repository; covered by the CC0 dedication.
2. **Formally redistributable.** Openly licensed upstreams (e.g. CC-BY).
   Extracts are carried in `data/prepared/` under the upstream's terms, with
   attribution here.
3. **Customary scholarly use.** Upstreams that are freely usable with citation
   by academic convention but carry no formal open license (much of
   CDS/VizieR), or whose license carries obligations we'd rather not impose on
   this repository's users (share-alike) should stay out of the repo:
   fetch scripts show how to retrieve them into `data/fetched/` (gitignored)
   and extraction scripts derive what the warehouse needs.
   That is our stance, held to our best effort's extent:
   where we are tempted to break this rule is for one critical map
   bridging Baily numbers to HIP number indices,
   which we'd reeeeeeeally like to source minimally, with maximal credit
   to the masters Verbunt & van Gent
   (see `Verbunt & van Gent (2012), machine-readable Almagest` below).

**Build contract:** `dbt build` from a fresh clone does not access networks.
Any fetch scripts are operator-side provisioning tools, not build steps.

---
## Ledger

### Peters & Knobel (1915), *Ptolemy's Catalogue of Stars*

- **What**: The Carnegie Institution's critical edition of the Almagest star
  catalogue; source of our Latin text (the Trapezuntius translation, 1528).
- **Where**: https://archive.org/details/ptolemyscataloqu00ptoluoft
  (Internet Archive scan and its OCR text layer)
- **Retrieved**: 2026-07-17
- **Terms**: Public domain (published 1915).
- **We carry**: `museum/almagest/` — our extraction, translations,
  and figure drawings (tier 1, CC0).
- **Cite**: Peters, C. H. F. & Knobel, E. B. (1915),
  *Ptolemy's Catalogue of Stars: A Revision of the Almagest*,
  Carnegie Institution of Washington, Publication No. 86.
- **Status**: carried (museum).

### Strasbourg astronomical Data Center (CDS) / VizieR (umbrella reference)

Applies to every CDS-hosted catalogue in this ledger —
CDS encourages users of the VizieR portal to include acknowledgment:

```
 This research has made use of the VizieR catalogue access tool, CDS,
 Strasbourg, France (DOI : 10.26093/cds/vizier). The original description
 of the VizieR service was published in 2000, A&AS 143, 23
```

### Verbunt & van Gent (2012), machine-readable Almagest

- **What**: Machine-readable edition of Ptolemy's catalogue
  with modern Hipparcos identifications.
  Served as our parsing contract during extraction,
  and is the bridge from Baily numbers to modern astrometry.
- **Where**: CDS, catalogue J/A+A/544/A31 —
  https://cdsarc.cds.unistra.fr/viz-bin/cat/J/A+A/544/A31
- **Retrieved**: 2026-07-17
- **Terms**: Tier 3 — customary scholarly use with citation;
  no formal open license. The full table is fetch-only.
- **We carry** (planned): a thin crosswalk only — Baily number, HIP number,
  identification-quality grade (their credited scholarly contribution)
  plus Ptolemy's own magnitudes (ancient facts, transcribed by them).
  Modern coordinates and magnitudes are deliberately *not* duplicated from
  this table.
- **Cite**: Verbunt, F. & van Gent, R. H. (2012),
  *The star catalogues of Ptolemaios and Ulugh Beg. Machine-readable versions
  and comparison with the modern Hipparcos Catalogue*,
  Astronomy & Astrophysics, Volume 544, id.A31, 34 pp.,
  Bibcode: 2012A&A...544A..31V
- **Status**: fetch-only; crosswalk queued.
