-- Every stroke point must land on a FIGURE star of its constellation;
-- unformed stars are never drawn (Arcturus floats free).
select p.*
from {{ ref('almagest_stroke_points') }} p
left join {{ ref('almagest_stars') }} s
  on s.constellation = p.constellation
 and s.seq = p.seq
 and s.member_type = 'figure'
where s.baily is null
