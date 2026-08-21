-- One row per Almagest entry (baily grain): modern astrometry plus the full
-- key bridge, baily -> HIP -> HD -> HR.
-- Positions: Hipparcos ICRS epoch J1991.25 propagated to J2000.0 with the
-- catalogue proper motions (delta-t = 8.75 yr; pmRA is mu_alpha*cos(dec)).
-- Two binaries lack a hip_main astrometric solution and fall back to the
-- BSC J2000 position via the HD bridge.
-- Below both of those sit two tiers for the entries that are not stars at all.
-- Where the object has its own catalogue entry, the museum names it and its
-- carried position is used outright; where it does not, the museum names the
-- BSC stars that mark where it lies and their mean stands in. See SOURCES.md
-- -- no coordinate is authored here, only the choice of object or of stars.
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
),

-- Unit-vector mean of the declared anchors' carried J2000 places. Vectors
-- rather than averaged angles, for the same reason atlas_constellation uses
-- them: an arithmetic mean of right ascensions breaks across the 0/360 wrap.
anchor_vec as (
    select
        p.baily,
        avg(cos(radians(s.dec_deg_j2000)) * cos(radians(s.ra_deg_j2000))) as x,
        avg(cos(radians(s.dec_deg_j2000)) * sin(radians(s.ra_deg_j2000))) as y,
        avg(sin(radians(s.dec_deg_j2000))) as z
    from {{ ref('src_almagest_placements') }} p
    join {{ ref('src_yale_bright_star') }} s on s.hr = p.anchor_hr
    group by p.baily
),

anchored as (
    select
        baily,
        fmod(degrees(atan2(y, x)) + 360.0, 360.0) as anchor_ra,
        degrees(asin(z / sqrt(x*x + y*y + z*z))) as anchor_dec
    from anchor_vec
),

-- A cluster carries its own measured place; nothing is averaged. Its
-- integrated magnitude comes along because that is the brightness the object
-- actually presents, and the atlas sizes what it draws by magnitude.
from_cluster as (
    select p.baily, g.ra_deg_j2000 as cluster_ra, g.dec_deg_j2000 as cluster_dec,
           g.vmag as vmag_cluster
    from {{ ref('src_almagest_placements') }} p
    join {{ ref('src_globular_cluster') }} g using (cluster_id)
)

select
    b.baily, b.hip, b.hd, b.hr, b.id_quality, b.ptolemy_mag, b.mag_qualifier,
    b.vmag_hip, b.b_v_hip, b.plx_mas, g.vmag_cluster,
    case when b.ra_deg is not null
         then fmod(b.ra_deg
                   + (coalesce(b.pm_ra_mas_yr, 0) * 8.75 / 3600000.0)
                     / cos(radians(b.dec_deg))
                   + 360.0, 360.0)
         when b.bsc_ra_deg is not null then b.bsc_ra_deg
         when g.cluster_ra is not null then g.cluster_ra
         else a.anchor_ra end as ra_deg_j2000,
    case when b.dec_deg is not null
         then b.dec_deg + coalesce(b.pm_de_mas_yr, 0) * 8.75 / 3600000.0
         when b.bsc_dec_deg is not null then b.bsc_dec_deg
         when g.cluster_dec is not null then g.cluster_dec
         else a.anchor_dec end as dec_deg_j2000,
    case when b.ra_deg is not null then 'hipparcos'
         when b.bsc_ra_deg is not null then 'bsc'
         when g.cluster_ra is not null then 'cluster'
         when a.anchor_ra is not null then 'anchors' end as placement_source
from bridged b
left join anchored a using (baily)
left join from_cluster g using (baily)
