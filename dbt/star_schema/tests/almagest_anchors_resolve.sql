-- The anchor mechanism, guarded at both ends.
--
-- An anchor must point at a real, positioned Bright Star Catalogue entry,
-- because its whole job is to contribute a carried coordinate to a mean.
-- And an anchor may only be declared for an entry the bridge cannot already
-- place: overriding carried astrometry with a hand-picked average would be
-- exactly the coordinate-authoring this design exists to avoid.
select p.baily, 'anchor HR is not a positioned BSC star' as problem
from {{ ref('src_almagest_placements') }} p
left join {{ ref('src_yale_bright_star') }} s on s.hr = p.anchor_hr
where p.anchor_hr is not null
  and (s.hr is null or s.is_ghost or s.ra_deg_j2000 is null)

union all

select p.baily, 'placement declared for an entry the bridge can already place' as problem
from {{ ref('src_almagest_placements') }} p
join {{ ref('src_vvg_crosswalk') }} x using (baily)
where x.hip is not null

union all

-- and, end to end: every anchored entry must actually land on its anchors
select m.baily, 'anchored entry did not land' as problem
from {{ ref('atlas_almagest_member') }} m
where m.baily in (
        select baily from {{ ref('src_almagest_placements') }}
        where anchor_hr is not null)
  and (not m.is_placed or m.placement_source != 'anchors')
