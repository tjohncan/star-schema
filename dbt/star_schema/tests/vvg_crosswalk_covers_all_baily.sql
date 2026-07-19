-- The carried V&vG crosswalk and the museum seed must agree on the Baily
-- universe exactly: every seed row crosswalked, nothing extra carried.
select
    coalesce(s.baily, x.baily) as baily,
    case when s.baily is null then 'crosswalk-only' else 'seed-only' end as problem
from {{ ref('almagest_stars') }} s
full outer join {{ source('prepared', 'vvg_almagest_crosswalk') }} x
  on s.baily = x.baily
where s.baily is null or x.baily is null
