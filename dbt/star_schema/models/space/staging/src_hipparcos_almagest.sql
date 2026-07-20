-- ICRS positions at epoch J1991.25; propagation to J2000 happens downstream.
select hip, ra_deg, dec_deg, plx_mas, pm_ra_mas_yr, pm_de_mas_yr,
       vmag, b_v, hd
from {{ source('prepared', 'hipparcos_almagest') }}
