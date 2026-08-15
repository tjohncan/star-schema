-- Exactly four entries are allowed to be unplaced — the four with no Hipparcos
-- counterpart star (Baily 191, 233, 449, 955). Unplaced is not unidentified: only
-- 233 is unidentified, graded 5 by V&vG. The other three they grade 1, a secure
-- identification (grade scale in models/sources.yml) — 191 and 449 are the
-- nebulous entries our captions call star-clusters, which have no single point
-- source to carry a HIP number, and 955 is secure but carries none either.
-- Any other unplaced star, or any of these four suddenly placed,
-- is a regression to investigate.
select baily, 'unexpectedly unplaced' as problem
from {{ ref('atlas_almagest_member') }}
where not is_placed and baily not in (191, 233, 449, 955)
union all
select baily, 'expected unplaced but placed' as problem
from {{ ref('atlas_almagest_member') }}
where is_placed and baily in (191, 233, 449, 955)
