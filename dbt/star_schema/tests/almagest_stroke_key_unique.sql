-- Strokes must be uniquely keyed by (constellation, stroke_seq).
select constellation, stroke_seq, count(*) as n
from {{ ref('almagest_strokes') }}
group by constellation, stroke_seq
having count(*) > 1
