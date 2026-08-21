-- The placement artifact, guarded at both ends.
--
-- An anchor must point at a real, positioned Bright Star Catalogue entry, and
-- a cluster must be one we actually carry, because their whole job is to
-- contribute a carried coordinate. And neither may be declared for an entry
-- the bridge can already place: overriding carried astrometry with a
-- hand-picked object would be exactly the coordinate-authoring this design
-- exists to avoid.
select p.baily, 'anchor HR is not a positioned BSC star' as problem
from {{ ref('src_almagest_placements') }} p
left join {{ ref('src_yale_bright_star') }} s on s.hr = p.anchor_hr
where p.anchor_hr is not null
  and (s.hr is null or s.is_ghost or s.ra_deg_j2000 is null)

union all

select p.baily, 'cluster_id is not in the carried Harris slice' as problem
from {{ ref('src_almagest_placements') }} p
left join {{ ref('src_globular_cluster') }} g using (cluster_id)
where p.cluster_id is not null and g.cluster_id is null

union all

select p.baily, 'placement declared for an entry the bridge can already place' as problem
from {{ ref('src_almagest_placements') }} p
join {{ ref('src_vvg_crosswalk') }} x using (baily)
where x.hip is not null

union all

-- and, end to end: every declared placement must actually land, by its own route
select m.baily, 'declared placement did not land' as problem
from {{ ref('atlas_almagest_member') }} m
join (
    select baily,
           case when max(anchor_hr) is not null then 'anchors' else 'cluster' end as expect
    from {{ ref('src_almagest_placements') }}
    where anchor_hr is not null or cluster_id is not null
    group by baily
) d on d.baily = m.baily
where not m.is_placed or m.placement_source != d.expect
