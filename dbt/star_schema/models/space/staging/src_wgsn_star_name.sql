select proper_name, designation, hip, hr, bayer_id, constellation,
       origin, language, adopted
from {{ source('prepared', 'wgsn_star_name') }}
