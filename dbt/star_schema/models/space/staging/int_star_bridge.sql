-- One row per Almagest entry (baily grain): modern astrometry plus the full
-- key bridge, baily -> HIP -> HD -> HR.
-- Positions: Hipparcos ICRS epoch J1991.25 propagated to J2000.0 with the
-- catalogue proper motions (delta-t = 8.75 yr; pmRA is mu_alpha*cos(dec)).
-- Two binaries lack a hip_main astrometric solution and fall back to the
-- BSC J2000 position via the HD bridge.
with cross_hip as (
    select
        x.baily, x.hip, x.id_quality, x.ptolemy_mag, x.mag_qualifier,
        h.ra_deg, h.dec_deg, h.plx_mas, h.pm_ra_mas_yr, h.pm_de_mas_yr,
        h.vmag as vmag_hip, h.b_v as b_v_hip, h.hd
    from {{ ref('src_vvg_crosswalk') }} x
    left join {{ ref('src_hipparcos_almagest') }} h using (hip)
),

bridged as (
    select
        c.*,
        b.hr,
        b.ra_deg_j2000 as bsc_ra_deg,
        b.dec_deg_j2000 as bsc_dec_deg
    from cross_hip c
    left join {{ ref('src_yale_bright_star') }} b using (hd)
    -- a few HD numbers cover multiple BSC components: keep the brightest
    qualify row_number() over (
        partition by c.baily order by b.vmag asc nulls last, b.hr
    ) = 1
)

select
    baily, hip, hd, hr, id_quality, ptolemy_mag, mag_qualifier,
    vmag_hip, b_v_hip, plx_mas,
    case when ra_deg is not null
         then fmod(ra_deg
                   + (coalesce(pm_ra_mas_yr, 0) * 8.75 / 3600000.0)
                     / cos(radians(dec_deg))
                   + 360.0, 360.0)
         else bsc_ra_deg end as ra_deg_j2000,
    case when dec_deg is not null
         then dec_deg + coalesce(pm_de_mas_yr, 0) * 8.75 / 3600000.0
         else bsc_dec_deg end as dec_deg_j2000
from bridged
