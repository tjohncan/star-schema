"""Build the Almagest Atlas: a single self-contained index.html.

Reads   ../../dbt/star_schema/dev.duckdb   (after a fresh `dbt build`)
        template.html                      (layout, styles, renderer)
Writes  index.html                         (template + inlined window.ATLAS)

Formatting only — every field here traces to a mart column;
all astronomy lives in the warehouse.
Deterministic: same warehouse, same bytes.
Run:  py payloads/almagest_atlas/build.py
"""

import json
import sys
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DB = ROOT / "dbt" / "star_schema" / "dev.duckdb"
MARKER = "__ATLAS_JSON__"


def fail(msg):
    sys.exit(f"FAIL: {msg}")


def rows(con, sql):
    cur = con.sql(sql)
    cols = cur.columns
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def main():
    if not DB.exists():
        fail(f"warehouse not found at {DB} — run `dbt build` first")
    con = duckdb.connect(str(DB), read_only=True)

    stars = rows(con, """
        select hr, name, name_tier as tier, cst,
               round(ra_deg, 4) as ra, round(dec_deg, 4) as dec,
               round(vmag, 2) as v, round(b_v, 2) as bv
        from space.atlas_star
        order by hr
    """)

    members = rows(con, """
        select baily, constellation as cst, member_type, seq,
               latin, english, caption,
               ptolemy_mag as pt_mag, mag_qualifier as pt_qual,
               id_quality, hip, hd, hr,
               round(ra_deg, 4) as ra, round(dec_deg, 4) as dec,
               round(vmag, 2) as v, round(b_v, 2) as bv,
               name, name_tier as tier, proper_name, sp_type,
               round(dist_pc, 1) as dist_pc, is_placed,
               name_origin as origin, name_language as language
        from space.atlas_almagest_member
        order by baily
    """)

    cons = rows(con, """
        select constellation as code, name_latin, name_english,
               stars_figure, stars_unformed, description,
               view_ra_deg, view_dec_deg, fov_deg, n_unplaced,
               brightest_name, brightest_vmag,
               nearest_name, round(nearest_pc, 1) as nearest_pc,
               farthest_name, round(farthest_pc, 1) as farthest_pc
        from space.atlas_constellation
    """)

    points = rows(con, """
        select constellation as cst, stroke_seq, stroke, comment,
               point_order, seq
        from space.atlas_stroke_point
        order by constellation, stroke_seq, point_order
    """)

    if len(cons) != 48 or len(members) != 1028:
        fail(f"unexpected counts: {len(cons)} constellations, {len(members)} members")
    if len(points) != 1227:
        fail(f"unexpected stroke points: {len(points)}")

    # group stroke points into per-constellation stroke lists
    strokes = {}
    for p in points:
        key = (p["cst"], p["stroke_seq"])
        s = strokes.setdefault(key, {"name": p["stroke"], "comment": p["comment"], "seqs": []})
        s["seqs"].append(p["seq"])
    if len(strokes) != 336:
        fail(f"unexpected stroke count: {len(strokes)}")

    # book order for the index: order of first appearance in the stars seed
    book_order = [r["cst"] for r in rows(con, """
        select constellation as cst, min(baily) as first_baily
        from space.atlas_almagest_member group by 1 order by 2
    """)]
    cons_by_code = {c["code"]: c for c in cons}

    constellations = []
    for code in book_order:
        c = cons_by_code[code]
        constellations.append({
            "code": code,
            "latin": c["name_latin"],
            "english": c["name_english"],
            "n_figure": c["stars_figure"],
            "n_unformed": c["stars_unformed"],
            "n_unplaced": c["n_unplaced"],
            "description": c["description"],
            "view": {"ra": c["view_ra_deg"], "dec": c["view_dec_deg"], "fov": c["fov_deg"]},
            "stats": {
                "brightest": c["brightest_name"], "brightest_v": c["brightest_vmag"],
                "nearest": c["nearest_name"], "nearest_pc": c["nearest_pc"],
                "farthest": c["farthest_name"], "farthest_pc": c["farthest_pc"],
            },
            "strokes": [strokes[k] for k in sorted(strokes) if k[0] == code],
        })

    atlas = {
        "meta": {
            "schema_version": 1,
            "title": "Almagest Atlas",
            "counts": {"stars": len(stars), "members": len(members),
                       "constellations": 48, "strokes": len(strokes)},
            "credits": [
                "Latin text: Trapezuntius (1528) as printed in Peters & Knobel (1915), public domain",
                "Identifications: Verbunt & van Gent (2012), A&A 544, A31",
                "Astrometry: Hipparcos (ESA 1997, SP-1200)",
                "Photometry & designations: Yale Bright Star Catalogue, 5th rev. ed.",
                "Proper names & etymologies: IAU WGSN, Catalog of Star Names",
                "English translations, figure drawings, code: this project, CC0",
            ],
        },
        "stars": stars,
        "members": members,
        "constellations": constellations,
    }

    template = (HERE / "template.html").read_text(encoding="utf-8")
    if template.count(MARKER) != 1:
        fail(f"template must contain exactly one {MARKER} marker")
    payload = json.dumps(atlas, ensure_ascii=False, separators=(",", ":"))
    html = template.replace(MARKER, payload)
    out = HERE / "index.html"
    out.write_text(html, encoding="utf-8", newline="\n")

    print(f"atlas built: {len(stars)} backdrop stars | {len(members)} members | "
          f"48 scenes | {len(strokes)} strokes")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
