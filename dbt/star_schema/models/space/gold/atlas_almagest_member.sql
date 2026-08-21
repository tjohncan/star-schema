-- All 1,028 Almagest entries, render-ready: book text, Ptolemy's magnitude,
-- modern astrometry and names where the bridge lands, honest nulls where it
-- cannot (is_placed = false only for the four entries with no Hipparcos
-- counterpart star — most of which V&vG did identify securely, just without
-- supplying a HIP number; see tests/atlas_placement_pinned.sql).
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
    coalesce(s.vmag, b.vmag_hip, b.vmag_cluster) as vmag,
    coalesce(s.b_v, b.b_v_hip) as b_v,
    coalesce(s.name, 'HIP ' || b.hip, 'Baily ' || m.baily) as name,
    coalesce(s.name_tier,
             case when b.hip is not null then 'hip' else 'baily' end) as name_tier,
    s.proper_name,
    s.sp_type,
    -- full precision: rounding is presentation, and a rounded distance ties
    case when b.plx_mas is not null and b.plx_mas >= 1.0
         then 1000.0 / b.plx_mas end as dist_pc,
    b.ra_deg_j2000 is not null as is_placed,
    b.placement_source,
    p.note as placement_note,
    w.origin as name_origin,
    w.language as name_language
from {{ ref('src_almagest_stars') }} m
join {{ ref('int_star_bridge') }} b using (baily)
left join {{ ref('atlas_star') }} s using (hr)
left join {{ ref('src_wgsn_star_name') }} w
  on w.proper_name = s.proper_name
-- the museum's note on an entry the bridge cannot reach: what the object is
-- where we place it another way, or why we cannot place it at all. Anchor rows
-- are excluded, and an entry has at most one such row (build_seeds.py enforces
-- both), so this join can neither miss one nor fan out.
left join {{ ref('src_almagest_placements') }} p
  on p.baily = m.baily and p.anchor_hr is null
