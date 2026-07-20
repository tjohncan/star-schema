-- All 48 scenes must exist and be renderable.
select count(*) as n
from {{ ref('atlas_constellation') }}
having count(*) != 48
