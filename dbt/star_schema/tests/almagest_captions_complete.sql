-- The caption contract: every figured member carries a standalone picture
-- caption; the unformed — never drawn — carry none.
select baily, 'figure star missing caption' as problem
from {{ ref('atlas_almagest_member') }}
where member_type = 'figure' and (caption is null or caption = '')
union all
select baily, 'unformed star has caption' as problem
from {{ ref('atlas_almagest_member') }}
where member_type = 'unformed' and caption is not null and caption != ''
