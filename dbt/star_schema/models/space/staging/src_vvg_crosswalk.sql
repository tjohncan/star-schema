select baily, hip, id_quality, ptolemy_mag, mag_qualifier
from {{ source('prepared', 'vvg_almagest_crosswalk') }}
