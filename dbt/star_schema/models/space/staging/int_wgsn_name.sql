-- Every IAU proper name resolved to a Yale HR number, one name per star.
--
-- WGSN states an HR outright for most names ("HR 2491" for Sirius), but not
-- for multiple-star systems, which it designates by Bayer letter behind an
-- asterisk ("* alf Cru"), and not for stars it knows by HD or GJ number.
-- Taking only the outright ones reaches 415 of 597 names, and the 182 it drops
-- include Acrux, Alnitak, Algieba, Acrab, Acamar and Rasalgethi -- all of them
-- stars Ptolemy catalogued, left reading as bare Bayer letters in the atlas.
--
-- Three routes, tried in order, first match wins:
--   1. designation "HR n"          -- WGSN said it outright; nothing inferred
--   2. bayer_id greek letter + cst -- the greek_alphabet seed does the lookup
--   3. flamsteed number + cst      -- from bayer_id, else from the designation
--
-- Route 1 going first is what keeps the component confusion honest. Betelgeuse
-- holds HR 2061 against "Siwarha", whose bayer_id "alf Ori B" is its companion,
-- and Rigil Kentaurus holds HR 5459 against Proxima -- the very binaries
-- SOURCES.md flags as differing on component assignment. Routes 2 and 3 only
-- ever fill a star no name has claimed.
with wgsn as (
    select proper_name, designation, bayer_id
    from {{ ref('src_wgsn_star_name') }}
),

-- Route 1 may land on any BSC entry, because WGSN named it explicitly.
-- Routes 2 and 3 are our inference, so they may not: a positionless "ghost"
-- entry is never something we should deduce a proper name onto.
bsc as (
    select hr, bayer, bayer_sup, flamsteed, cst, vmag, is_ghost
    from {{ ref('src_yale_bright_star') }}
),

-- Pull the parts out of bayer_id / designation. The Greek letter is resolved
-- by joining the seed rather than by matching a character range, so the
-- alphabet stays declared in one place.
parsed as (
    select
        w.proper_name,
        case when w.designation like 'HR %'
              and regexp_full_match(trim(substr(w.designation, 4)), '\d+')
             then cast(trim(substr(w.designation, 4)) as bigint)
        end as hr_stated,
        g.abbr as bayer_abbr,
        -- superscript = a trailing digit on the letter token ("bet1 Sco")
        nullif(regexp_extract(regexp_extract(w.bayer_id, '^(\S+)', 1),
                              '(\d)$', 1), '') as bayer_sup,
        -- constellation = the token after the letter, whatever shape the
        -- letter took, and ignoring any trailing component ("alf Ori B")
        nullif(regexp_extract(w.bayer_id, '^\S+\s+(\w{3})', 1), '') as bayer_cst,
        -- one field supplies both halves of a Flamsteed designation, so the
        -- number and the constellation can never be taken from different rows
        coalesce(
            nullif(regexp_extract(w.bayer_id, '^\d+\s+\w{3}'), ''),
            nullif(regexp_extract(replace(w.designation, '* ', ''), '^\d+\s+\w{3}'), '')
        ) as flam_token
    from wgsn w
    -- WGSN writes the letter as Greek almost everywhere ("gam Cam" is the lone
    -- ASCII holdout), so accept either spelling against the same seed row.
    left join {{ ref('src_greek_alphabet') }} g
      on g.letter = substr(w.bayer_id, 1, 1)
      or lower(g.abbr) = lower(substr(w.bayer_id, 1, 3))
),

candidates as (
    select proper_name, hr_stated as hr, 1 as route, 'designation' as match_via
    from parsed
    where hr_stated is not null

    union all

    select p.proper_name, b.hr, 2 as route, 'bayer' as match_via
    from parsed p
    join bsc b on b.bayer = p.bayer_abbr and b.cst = p.bayer_cst
    where p.bayer_abbr is not null and not b.is_ghost
    -- an exact superscript wins ("bet1 Sco"); with none stated ("alf Cru")
    -- the brightest component carries the name
    qualify row_number() over (
        partition by p.proper_name
        order by case when p.bayer_sup is not null
                       and b.bayer_sup = p.bayer_sup then 0 else 1 end,
                 b.vmag asc nulls last, b.hr
    ) = 1

    union all

    select p.proper_name, b.hr, 3 as route, 'flamsteed' as match_via
    from parsed p
    join bsc b
      on b.flamsteed = regexp_extract(p.flam_token, '^(\d+)', 1)
     and b.cst = regexp_extract(p.flam_token, '(\w{3})$', 1)
    where p.flam_token is not null and not b.is_ghost
    qualify row_number() over (
        partition by p.proper_name order by b.vmag asc nulls last, b.hr
    ) = 1
),

-- Settle each name on its best route first. Deduping by star in the same pass
-- would let a name's losing candidate squat on an HR it was never going to
-- keep, and block the name that legitimately resolves there.
best_per_name as (
    select proper_name, hr, route, match_via
    from candidates
    qualify rank() over (partition by proper_name order by route) = 1
)

-- Then one name per star. Where two names claim one HR from different routes,
-- the one WGSN stated outright outranks the one we inferred -- which is how
-- Betelgeuse keeps HR 2061 and Rigil Kentaurus keeps HR 5459.
--
-- rank(), not row_number(), and the tie-break stops at route on purpose. Two
-- names arriving by the SAME route are genuinely ambiguous, and ordering them
-- alphabetically would be the silent guess this model exists to remove: both
-- tie at rank 1, both survive, and the unique test on hr fails loudly. Nothing
-- ties today; the point is what happens when a WGSN re-export makes one.
select proper_name, hr, match_via
from best_per_name
qualify rank() over (partition by hr order by route) = 1
