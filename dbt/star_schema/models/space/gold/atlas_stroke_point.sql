-- Stroke polylines resolved to render-ready points: every vertex carries its
-- star's position, magnitude, and identity.
select
    p.constellation,
    p.stroke_seq,
    s.stroke,
    s.comment,
    p.point_order,
    p.seq,
    m.baily,
    m.hr,
    m.ra_deg,
    m.dec_deg,
    m.vmag,
    m.is_placed
from {{ ref('src_almagest_stroke_points') }} p
join {{ ref('src_almagest_strokes') }} s using (constellation, stroke_seq)
join {{ ref('atlas_almagest_member') }} m
  on m.constellation = p.constellation
 and m.seq = p.seq
 and m.member_type = 'figure'
