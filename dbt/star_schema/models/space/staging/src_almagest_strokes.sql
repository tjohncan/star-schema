select constellation, stroke_seq, stroke, comment
from {{ ref('almagest_strokes') }}
