# SOURCES — the provenance ledger

This file accounts for every third-party source feeding this project:
what we took, where from, when, under what terms, and our citations.

## Policy

Two kinds of content live in this repository:

- **Ours, or public domain** — the translations, figure drawings,
  hand-curated seeds, code, and anything derived from public-domain
  sources. Covered by the CC0 dedication, anywhere in the tree.
- **Theirs** — data taken from working scientists and institutions.
  It lives under `data/`, it is not covered by our CC0, and
  every file of it has a ledger entry below naming the owner,
  what we took, terms we found (quoted verbatim), and our best citation.

We take as little as does the job: full raw catalogues stay out of the
repository — `scripts/prep_sources.py` documents how to retrieve them
into `data/fetched/` (gitignored) and derives the carried extracts in
`data/prepared/` from them. Everything taken, we cite: loudly, proudly,
and as politely as possible. Where an upstream states no terms,
the ledger registers that plainly and points to a community norm;
where terms exist (citation, share-alike, commercial caveats),
the entry quotes them so downstream users can make informed calls.

**Build contract:** `dbt build` from a fresh clone does not access networks.
Any fetch scripts are operator-side provisioning tools, not build steps.

**No authored coordinates.** Every position in this repository is
a carried measurement or a stated derivation from one.
Two of Ptolemy's entries are not single stars —
Baily 191, the nebulous tip of Perseus's right hand, and
Baily 449, the Manger in the Crab's chest —
so no catalogue supplies a position for them.
Instead `museum/almagest/almagest_placements.csv` names the Bright
Star Catalogue stars that mark where each object lies, and `int_star_bridge`
places the entry at the unit-vector mean of *their* carried positions.
The judgement is ours and is CC0 — which stars mark the object,
and that the entry denotes an object at all;
the coordinates remain Yale's, cited below.
The anchors are position markers, not a claim about cluster membership;
for Baily 191 the mean falls 7.8′ east of
the h Persei centre Verbunt & van Gent adopt (2012, sect. 5.4),
displaced toward χ Persei because Ptolemy's entry is the pair,
not the one cluster.
Where even that is impossible the entry stays unplaced and says why —
Baily 233, which nobody has identified, and
Baily 955, ω Centauri, a cluster with no member bright enough to be here.
`atlas_placement_pinned` holds that set at two.

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
  figure drawings, and the placement judgements for the entries no catalogue
  can place (all ours, CC0; see "No authored coordinates" above).
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

Their Licence page (retrieved 2026-07-18) states, in part:

> The data retrieved with VizieR are free of usage in a scientific context;
> however, as it is the usage in scientific publication, the original authors
> and publication references including the publisher have to be [explicitly]
> cited. [...] The commercial usage of the data is subject to rules depending
> of the origin.

### Verbunt & van Gent (2012), machine-readable Almagest

- **What**: Machine-readable edition of Ptolemy's catalogue
  with modern Hipparcos identifications.
  Served as our parsing contract during extraction,
  and is the bridge from Baily numbers to modern astrometry.
- **Where**: CDS, catalogue J/A+A/544/A31 —
  https://cdsarc.cds.unistra.fr/viz-bin/cat/J/A+A/544/A31
- **Retrieved**: 2026-07-17
- **Terms**: Customary scholarly use with citation
  (VizieR licence quoted in the umbrella entry above); the catalogue's
  ReadMe adds an Acknowledgements naming Frank Verbunt (Radboud University
  Nijmegen) and no further terms. Everything beyond the crosswalk below is
  fetch-only.
- **We carry**: `data/prepared/vvg_almagest_crosswalk.csv` — five thin
  columns (baily, hip, id_quality: their credited scholarly contribution;
  ptolemy_mag, mag_qualifier: ancient facts, transcribed by them),
  generated by `scripts/prep_sources.py` from the fetched `ptolema.dat`.
  Modern coordinates and magnitudes are deliberately *not* duplicated from
  this table. This is the deepest cut we take from anyone — their
  identifications are judgment, not just measurement — carried because
  the Baily-to-HIP bridge is the spine of the whole Ptolemy project,
  credited accordingly. Their section 5.4 also settles the three entries that
  carry a secure identification but no HIP number, because they are not stars:
  Baily 191 is h Persei, 449 is Praesepe, and 955 is the globular cluster
  ω Centauri — which Ptolemy recorded as an ordinary fifth-magnitude star.
  We take that reading from the paper and cite it; the paper is open access.
- **Cite**: Verbunt, F. & van Gent, R. H. (2012),
  *The star catalogues of Ptolemaios and Ulugh Beg. Machine-readable versions
  and comparison with the modern Hipparcos Catalogue*,
  Astronomy & Astrophysics, Volume 544, id.A31, 34 pp.,
  Bibcode: 2012A&A...544A..31V
- **Status**: carried (thin crosswalk, 2026-07-18); everything else fetch-only.

### Yale Bright Star Catalogue, 5th revised edition

- **What**: The classic catalogue of the ~9,100 stars of the naked-eye sky
  (to visual magnitude ~6.5), keyed by HR number; our bridge from proper
  names and Bayer/Flamsteed designations to modern identifiers and positions.
- **Where**: http://tdc-www.harvard.edu/catalogs/bsc5.html (also CDS V/50)
- **Retrieved**: 2026-07-17
- **Terms**: No formal license found. The Harvard TDC page states no terms
  (checked 2026-07-18); the ReadMe of this version says
  "It has been made available only for dissemination on the Astronomical
  Data Center CD ROM" — a CD-ROM-era note on a "preliminary" edition that
  became the de facto BSC5, openly mirrored for decades by Harvard, CDS,
  HEASARC, and planetarium software everywhere.
  We carry an extract with citation.
- **We carry**: `data/prepared/yale_bright_star.csv` —
  identifiers (HR, HD, SAO, name fields), J2000 position, V magnitude,
  B−V, spectral type, proper motion, parallax;
  all 9,110 rows kept, including the 14 "ghost" entries (novae and friends)
  with blank positions, to preserve the numbering.
  Generated by `scripts/prep_sources.py` from the fetched `ybsc5.gz`.
  These positions do a second job: they are the anchors that place Ptolemy's
  two nebulous entries, whose mean stands in for an object no catalogue lists
  as a star (see "No authored coordinates" above).
- **Cite**: Hoffleit, D. & Warren, W. H. Jr. (1991),
  *The Bright Star Catalogue, 5th Revised Edition (Preliminary Version)*,
  Yale University Observatory.
  Bibcode: 1991bsc..book.....H
  (see also: 1964BS....C......0H
  / 1964cbs..book.....H 
  / 1995yCat.5050....0H)
- **Status**: carried (extract).

### Hipparcos (ESA 1997), the astrometric catalogue

- **What**: The main catalogue of ESA's astrometry mission (118,218 stars):
  positions, proper motions, parallaxes.
  Our source of modern positions for the Almagest stars,
  and of the HD numbers bridging HIP keys to Yale HR keys.
  The mission is named for Hipparchus, whose lost star catalogue
  Ptolemy built upon.
- **Where**: CDS, catalogue I/239 —
  https://cdsarc.cds.unistra.fr/viz-bin/cat/I/239 (`hip_main.dat` + ReadMe)
- **Retrieved**: 2026-07-19 (scripted; canonical URLs in
  `scripts/prep_sources.py`)
- **Terms**: Customary scholarly use with citation
  (CDS-hosted; VizieR licence in the umbrella entry above).
  No formal license stated in the ReadMe.
- **We carry**: `data/prepared/hipparcos_almagest.csv`
  — a thin slice of 1,021 stars,
  restricted to the V&vG crosswalk's HIP set:
  ICRS J1991.25 position, proper motion, parallax, V, B−V, HD.
  The other 117,197 stars are not carried.
- **Cite**: ESA (1997), *The Hipparcos and Tycho Catalogues*, ESA SP-1200.
  Bibcode: 1997ESASP1200.....E (catalogue: 1997HIP...C......0E).
- **Status**: carried (thin slice).

### IAU Working Group on Star Names (WGSN)

- **What**: The IAU's official catalog of proper star names (IAU-CSN;
  597 rows at our retrieval), with designations, HIP and Bayer
  identifiers, and the working group's etymology notes.
  Our only source of friendly names — everything else is catalogue
  numbers and Greek letters — and the atlas's etymological voice.
- **Where**: Two first-party homes; the live site is the authority.
  The live catalog with etymologies, from which our CSV was exported by
  hand ("Show ALL entries", then export CSV):
  https://exopla.net/star-names/modern-iau-star-names/
  An alternative ("static") record (fixed-width text, scriptable,
  "Last updated 2022-04-04")
  itself endeavours to link readers back to IAU/WGSN resources:
  https://www.pas.rochester.edu/~emamajek/WGSN/IAU-CSN.txt
  ... directing questions to an address at exopla.net,
  the working group's own outreach domain.
- **Retrieved**: 2026-07-17 (CSV export); 2026-07-19 (txt).
- **Terms**: No formal license found on either home. The site footer reads
  "© 2026 The Working Group on Star Names (WGSN) of the International
  Astronomical Union (IAU)" (site-wide, not attached to the data);
  the Imprint page states the group's public-good charter — naked-eye star
  names "treated with care ... aiming to increase cultural diversity and
  respect historical ideas", closing "this website tells its story.
  Enjoy!". Our stance: the names themselves are official IAU nomenclature,
  facts adopted expressly for community use; the etymology paragraphs are
  WGSN-authored prose that we'll quote with per-paragraph attribution.
- **We carry**: `data/prepared/wgsn_star_name.csv` — the full catalog:
  proper name, designation, HIP, Bayer ID, constellation,
  origin/etymology, language, adoption date.
  Cross-checked once (2026-07-19) against the alternative static record:
  every official name is present in our export;
  nine famous binaries differ on component HIP assignment
  (Proxima, Rigil Kentaurus, Toliman, Alcor, and friends).
- **Cite**: IAU Division C Working Group on Star Names
  (Chair S. Hoffmann, Secretary E. Mamajek at our retrieval),
  *IAU Catalog of Star Names* (IAU-CSN) — both homes above.
- **Status**: carried (full catalog).
