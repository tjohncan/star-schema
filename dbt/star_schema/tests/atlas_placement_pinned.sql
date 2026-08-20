-- Exactly two entries are allowed to be unplaced. Four have no Hipparcos
-- counterpart star, but two of those are the nebulous ones our captions call
-- star-clusters, and the museum anchors them onto Bright Star Catalogue
-- positions (see almagest_placements.csv), so they draw.
--
-- What is left cannot be placed at all. Baily 233 is unidentified, graded 5 by
-- V&vG. Baily 955 they grade 1, a secure identification (grade scale in
-- models/sources.yml), but supply no HIP number and no object we can resolve
-- from carried data. Both carry a museum note saying so, and neither will get
-- a position invented for it.
--
-- Any other unplaced star, or either of these two suddenly placed,
-- is a regression to investigate.
select baily, 'unexpectedly unplaced' as problem
from {{ ref('atlas_almagest_member') }}
where not is_placed and baily not in (233, 955)
union all
select baily, 'expected unplaced but placed' as problem
from {{ ref('atlas_almagest_member') }}
where is_placed and baily in (233, 955)
union all
-- and the two that are unplaced must say why, or the panel has nothing to show
select baily, 'unplaced without a museum reason' as problem
from {{ ref('atlas_almagest_member') }}
where not is_placed and (placement_note is null or placement_note = '')
