-- One scene per Ptolemaic constellation: names, museum prose, the fixed
-- camera, and sky stats.
-- Camera: unit-vector centroid of the placed figure stars (safe across the
-- RA 0/360 wrap); fov = twice the maximal member offset x 1.3 margin,
-- floored at 12 degrees for the tiny figures (Sagitta, Equuleus).
-- Centre from the figure, field from every member. The figure is what the
-- scene is about, so it stays centred -- but Ptolemy catalogued the unformed
-- stars too, and a frame that cannot show them is not showing his
-- constellation. Eleven scenes widen to hold them; the Southern Fish most,
-- because its unformed stars are the ones that later became Microscopium.
-- Nearest/farthest rank on the full-precision distance: at display precision
-- Arcturus and Muphrid both read 11.3 pc, and arg_min would pick by scan order.
with members as (
    select * from {{ ref('atlas_almagest_member') }}
),

figure_vec as (
    select
        constellation,
        cos(radians(dec_deg)) * cos(radians(ra_deg)) as x,
        cos(radians(dec_deg)) * sin(radians(ra_deg)) as y,
        sin(radians(dec_deg)) as z
    from members
    where member_type = 'figure' and is_placed
),

-- the same vectors over every placed member, figured or not: these set the
-- field of view, while figure_vec above still sets where the camera looks
member_vec as (
    select
        constellation,
        cos(radians(dec_deg)) * cos(radians(ra_deg)) as x,
        cos(radians(dec_deg)) * sin(radians(ra_deg)) as y,
        sin(radians(dec_deg)) as z
    from members
    where is_placed
),

centroid as (
    select constellation, avg(x) as cx, avg(y) as cy, avg(z) as cz
    from figure_vec
    group by constellation
),

cam as (
    select
        constellation,
        cx / sqrt(cx*cx + cy*cy + cz*cz) as ux,
        cy / sqrt(cx*cx + cy*cy + cz*cz) as uy,
        cz / sqrt(cx*cx + cy*cy + cz*cz) as uz
    from centroid
),

fov as (
    select
        f.constellation,
        greatest(12.0, round(
            2 * 1.3 * degrees(max(acos(least(1.0,
                f.x * c.ux + f.y * c.uy + f.z * c.uz)))), 1)) as fov_deg
    from member_vec f
    join cam c using (constellation)
    group by f.constellation
),

stats as (
    select
        constellation,
        count(*) filter (where member_type = 'figure') as n_figure,
        count(*) filter (where member_type = 'unformed') as n_unformed,
        count(*) filter (where not is_placed) as n_unplaced,
        arg_min(name, vmag) as brightest_name,
        min(vmag) as brightest_vmag,
        arg_min(name, dist_pc) as nearest_name,
        min(dist_pc) as nearest_pc,
        arg_max(name, dist_pc) as farthest_name,
        max(dist_pc) as farthest_pc
    from members
    group by constellation
)

select
    c.constellation,
    c.name_latin,
    c.name_english,
    c.stars_figure,
    c.stars_unformed,
    c.description,
    round(fmod(degrees(atan2(cam.uy, cam.ux)) + 360.0, 360.0), 3) as view_ra_deg,
    round(degrees(asin(cam.uz)), 3) as view_dec_deg,
    fov.fov_deg,
    stats.n_unplaced,
    stats.brightest_name,
    stats.brightest_vmag,
    stats.nearest_name,
    stats.nearest_pc,
    stats.farthest_name,
    stats.farthest_pc
from {{ ref('src_almagest_constellations') }} c
join cam on cam.constellation = c.constellation
join fov on fov.constellation = c.constellation
join stats on stats.constellation = c.constellation
