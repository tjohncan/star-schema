select baily, anchor_hr, note
from {{ ref('almagest_placements') }}
