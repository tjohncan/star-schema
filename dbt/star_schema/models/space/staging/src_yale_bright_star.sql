-- Explicit casts pin down what the CSV sniffer must not decide for us.
select
    hr,
    name,
    cast(flamsteed as varchar) as flamsteed,
    bayer,
    cast(bayer_sup as varchar) as bayer_sup,
    cst,
    hd,
    sao,
    var_id,
    ra_deg_j2000,
    dec_deg_j2000,
    vmag,
    vmag_code,
    b_v,
    sp_type,
    pm_ra_arcsec,
    pm_de_arcsec,
    parallax_arcsec,
    cast(is_ghost as boolean) as is_ghost
from {{ source('prepared', 'yale_bright_star') }}
