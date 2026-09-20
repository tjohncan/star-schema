-- The caption contract: every member carries a standalone picture caption,
-- figured and unformed alike. Drawing is a figure-star privilege; reading
-- out of order is not.
select baily, 'member missing caption' as problem
from {{ ref('atlas_almagest_member') }}
where caption is null or caption = ''
