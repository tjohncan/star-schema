-- Exactly four entries are allowed to be unplaced
-- — the ones V&vG could not identify (Baily 191, 233, 449, 955).
-- Any other unplaced star, or any of these four suddenly placed,
-- is a regression to investigate.
select baily, 'unexpectedly unplaced' as problem
from {{ ref('atlas_almagest_member') }}
where not is_placed and baily not in (191, 233, 449, 955)
union all
select baily, 'expected unplaced but placed' as problem
from {{ ref('atlas_almagest_member') }}
where is_placed and baily in (191, 233, 449, 955)
