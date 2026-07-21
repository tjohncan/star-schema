select baily, constellation, member_type, seq, latin, english, caption
from {{ ref('almagest_stars') }}
