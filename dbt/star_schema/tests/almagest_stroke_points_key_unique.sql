-- Stroke points must be uniquely keyed by (constellation, stroke_seq, point_order).
select constellation, stroke_seq, point_order, count(*) as n
from {{ ref('almagest_stroke_points') }}
group by constellation, stroke_seq, point_order
having count(*) > 1
