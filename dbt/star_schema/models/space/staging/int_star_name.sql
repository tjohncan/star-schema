-- Best display name per Yale bright star — the naming waterfall:
-- WGSN proper name > Bayer (greek letter + constellation) > Flamsteed > HR.
with wgsn_by_hr as (
    select hr, min(proper_name) as proper_name
    from {{ ref('src_wgsn_star_name') }}
    where hr is not null
    group by hr
),

named as (
    select
        s.hr,
        w.proper_name,
        case when s.bayer is not null and g.letter is not null
             then g.letter || coalesce(s.bayer_sup, '') || ' ' || s.cst
        end as bayer_name,
        case when s.flamsteed is not null
             then s.flamsteed || ' ' || s.cst
        end as flamsteed_name
    from {{ ref('src_yale_bright_star') }} s
    left join wgsn_by_hr w using (hr)
    left join {{ ref('src_greek_alphabet') }} g on g.abbr = s.bayer
)

select
    hr, proper_name, bayer_name, flamsteed_name,
    coalesce(proper_name, bayer_name, flamsteed_name, 'HR ' || hr) as name,
    case when proper_name is not null then 'proper'
         when bayer_name is not null then 'bayer'
         when flamsteed_name is not null then 'flamsteed'
         else 'hr' end as name_tier
from named
