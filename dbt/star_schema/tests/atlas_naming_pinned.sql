-- The naming waterfall and the Baily -> HIP -> HD -> HR bridge can disagree
-- about which half of a visual double is "the" star. WGSN names the system
-- ("ksi UMa"), int_wgsn_name resolves that to the brighter component, and the
-- bridge landed the Almagest entry on the other one -- adjacent HR numbers,
-- same Bayer letter. Four entries sit in that gap and still show a Bayer or
-- Flamsteed name where an IAU proper name exists for their system.
-- Pinned rather than papered over, on the same contract as
-- atlas_placement_pinned: if this set moves, find out why before accepting it.
with mismatched as (
    select distinct m.baily
    from {{ ref('atlas_almagest_member') }} m
    join {{ ref('src_wgsn_star_name') }} w on w.hip = m.hip
    where m.proper_name is null
)

select baily, 'unexpected naming component mismatch' as problem
from mismatched
where baily not in (32, 44, 247, 692)

union all

select e.baily, 'expected mismatch but now carries its IAU name' as problem
from (values (32), (44), (247), (692)) as e(baily)
where e.baily not in (select baily from mismatched)
