select constellation, stroke_seq, point_order, seq
from {{ ref('almagest_stroke_points') }}
