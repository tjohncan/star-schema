# star_schema — the warehouse

Joins Ptolemy's catalogue (the museum seeds) to the modern sky
(the carried extracts under `data/prepared/`) and serves render-ready
gold tables. One local DuckDB file, no network, deterministic:
`dbt build` from a fresh clone must go green offline.

## Layers

| layer | schema | what lives there |
|---|---|---|
| seeds `almagest/` | `ptolemy` | the museum, verbatim: stars (Latin, English, captions), constellations, strokes, stroke points |
| seeds `appendix/` | `lookup` | small hand-curated helpers (Greek alphabet) |
| sources | — | the four carried extracts, read in place from `../../data/prepared/*.csv` |
| `models/space/staging/` | `space_staging` | views: `src_*` typed pass-throughs, `int_star_bridge`, `int_star_name` |
| `models/space/gold/` | `space` | tables: `atlas_star`, `atlas_almagest_member`, `atlas_constellation`, `atlas_stroke_point` |

The spine is `int_star_bridge`: Baily → HIP
(Verbunt & van Gent's identifications) → HD (Hipparcos) → HR (Yale),
with Hipparcos positions propagated J1991.25 → J2000.
`int_star_name` runs the naming waterfall — proper name > Bayer >
Flamsteed > HR — and `atlas_almagest_member` puts it all on one row per
catalogue entry, honest nulls where the bridge cannot land
(exactly four entries, pinned by test).

## Build

```bash
dbt build        # seeds + models + all tests
```

Tests pin the shape of the sky: 1,028 members, 48 constellations,
336 strokes, every figured star captioned and drawn, the four
unidentifiable entries and no others unplaced.

## A taste

```sql
-- the heart of the Lion, end to end
select baily, name, caption, latin, vmag, ra_deg, dec_deg
from space.atlas_almagest_member
where constellation = 'Leo' and seq = 8 and member_type = 'figure';

-- every stroke of Draco, in drawing order
select stroke_seq, stroke, string_agg(seq, '-' order by point_order) as walk
from space.atlas_stroke_point
where constellation = 'Dra'
group by stroke_seq, stroke
order by stroke_seq;
```
