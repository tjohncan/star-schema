select baily, constellation, member_type, seq, latin, english
from {{ ref('almagest_stars') }}
