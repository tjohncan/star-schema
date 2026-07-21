-- All 1,028 Almagest entries, render-ready: book text, Ptolemy's magnitude,
-- modern astrometry and names where the bridge lands, honest nulls where it
-- cannot (is_placed = false only for the four entries V&vG left unidentified).
select
    m.baily,
    m.constellation,
    m.member_type,
    m.seq,
    m.latin,
    m.english,
    m.caption,
    b.ptolemy_mag,
    b.mag_qualifier,
    b.id_quality,
    b.hip,
    b.hd,
    b.hr,
    b.ra_deg_j2000 as ra_deg,
    b.dec_deg_j2000 as dec_deg,
    coalesce(s.vmag, b.vmag_hip) as vmag,
    coalesce(s.b_v, b.b_v_hip) as b_v,
    coalesce(s.name, 'HIP ' || b.hip, 'Baily ' || m.baily) as name,
    coalesce(s.name_tier,
             case when b.hip is not null then 'hip' else 'baily' end) as name_tier,
    s.proper_name,
    s.sp_type,
    case when b.plx_mas is not null and b.plx_mas >= 1.0
         then round(1000.0 / b.plx_mas, 1) end as dist_pc,
    b.ra_deg_j2000 is not null as is_placed,
    w.origin as name_origin,
    w.language as name_language
from {{ ref('src_almagest_stars') }} m
join {{ ref('int_star_bridge') }} b using (baily)
left join {{ ref('atlas_star') }} s using (hr)
left join {{ ref('src_wgsn_star_name') }} w
  on w.proper_name = s.proper_name
