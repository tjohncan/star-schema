select baily, anchor_hr, cluster_id, note
from {{ ref('almagest_placements') }}
