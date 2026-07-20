select constellation, name_latin, name_english,
       stars_figure, stars_unformed, description
from {{ ref('almagest_constellations') }}
