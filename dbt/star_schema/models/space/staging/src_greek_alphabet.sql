select greek_seq, abbr, name, letter
from {{ ref('greek_alphabet') }}
