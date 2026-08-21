select cluster_id, name, ra_deg_j2000, dec_deg_j2000, vmag
from {{ source('prepared', 'globular_cluster') }}
