-- Exactly one entry is allowed to be unplaced. Four have no Hipparcos
-- counterpart star, and three of those are not stars at all: Baily 191 and 449
-- are the clusters our captions name, anchored onto Bright Star Catalogue
-- positions, and Baily 955 is omega Centauri, placed from its own entry in the
-- carried Harris slice (see almagest_placements.csv, and SOURCES.md).
--
-- What is left is Baily 233, which V&vG grade 5 -- not identified (grade scale
-- in models/sources.yml). Nobody has ever said what it is, so nothing can
-- place it, and no position will be invented for it. It carries a museum note
-- saying so.
--
-- Any other unplaced star, or this one suddenly placed,
-- is a regression to investigate.
select baily, 'unexpectedly unplaced' as problem
from {{ ref('atlas_almagest_member') }}
where not is_placed and baily not in (233)
union all
select baily, 'expected unplaced but placed' as problem
from {{ ref('atlas_almagest_member') }}
where is_placed and baily in (233)
union all
-- and whatever is unplaced must say why, or the panel has nothing to show
select baily, 'unplaced without a museum reason' as problem
from {{ ref('atlas_almagest_member') }}
where not is_placed and (placement_note is null or placement_note = '')
