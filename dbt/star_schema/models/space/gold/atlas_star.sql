-- The backdrop pool: every placeable Yale bright star with its best name.
-- Ghost entries (novae etc., no positions) are excluded here by design.
select
    s.hr,
    n.name,
    n.name_tier,
    n.proper_name,
    n.bayer_name,
    n.flamsteed_name,
    s.cst,
    s.vmag,
    s.b_v,
    s.sp_type,
    s.ra_deg_j2000 as ra_deg,
    s.dec_deg_j2000 as dec_deg,
    case when s.parallax_arcsec is not null and s.parallax_arcsec >= 0.001
         then round(1.0 / s.parallax_arcsec, 1) end as dist_pc
from {{ ref('src_yale_bright_star') }} s
join {{ ref('int_star_name') }} n using (hr)
where not s.is_ghost
