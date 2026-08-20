"""Build dbt seeds from the museum's Almagest artifacts.

Reads   museum/almagest/almagest_stars.csv      (authoritative, hand-reviewed)
        museum/almagest/almagest_figures.toml   (authoritative, hand-edited)
Writes  dbt/star_schema/seeds/almagest/almagest_stars.csv          (verbatim copy)
        dbt/star_schema/seeds/almagest/almagest_constellations.csv (from TOML)
        dbt/star_schema/seeds/almagest/almagest_strokes.csv        (from TOML)
        dbt/star_schema/seeds/almagest/almagest_stroke_points.csv  (from TOML)

Validates the full artifact contract before writing anything; exits nonzero,
touching no output file, on any violation. Deterministic: rerunning on an
unchanged museum must leave `git diff` clean. Requires Python 3.11+ (tomllib).
"""

import csv
import shutil
import sys
import tomllib
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUSEUM = ROOT / "museum" / "almagest"
SEED_DIR = ROOT / "dbt" / "star_schema" / "seeds" / "almagest"

# Certified contract of the artifact (amend only knowingly, with the museum).
N_STARS = 1028
N_CONSTELLATIONS = 48
N_FIGURE = 920
N_UNFORMED = 108


def fail(msg):
    sys.exit(f"FAIL: {msg}")


def load_stars():
    with open(MUSEUM / "almagest_stars.csv", newline="", encoding="utf-8") as f:
        stars = list(csv.DictReader(f))
    if len(stars) != N_STARS:
        fail(f"expected {N_STARS} stars, found {len(stars)}")
    if sorted(int(r["baily"]) for r in stars) != list(range(1, N_STARS + 1)):
        fail(f"baily numbers are not exactly 1..{N_STARS}")
    counts = Counter(r["member_type"] for r in stars)
    if counts != {"figure": N_FIGURE, "unformed": N_UNFORMED}:
        fail(f"member_type counts off: {dict(counts)}")
    sections = defaultdict(list)
    for r in stars:
        if not r["latin"].strip() or not r["english"].strip():
            fail(f"empty latin/english at baily {r['baily']}")
        sections[(r["constellation"], r["member_type"])].append(int(r["seq"]))
    for key, seqs in sections.items():
        if sorted(seqs) != list(range(1, len(seqs) + 1)):
            fail(f"seq not contiguous 1..N in {key}")
    return stars, sections


def load_placements(baily_numbers):
    """The placement artifact: position anchors for the entries the Hipparcos
    bridge cannot reach, and the reason for the ones that stay unplaced.

    A row either names an anchor star (several per entry, averaged downstream)
    or carries the reason no position exists — never both, for one entry.
    Whether an entry is genuinely unreachable is a question about the carried
    crosswalk, so dbt asks it; here we only check the artifact against itself.
    """
    with open(MUSEUM / "almagest_placements.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_baily, seen = defaultdict(list), set()
    for r in rows:
        b, hr = r["baily"].strip(), r["anchor_hr"].strip()
        if not b.isdigit() or int(b) not in baily_numbers:
            fail(f"placements: {b!r} is not a catalogue entry")
        if not r["note"].strip():
            fail(f"placements: baily {b} has a row with no note")
        if hr and not hr.isdigit():
            fail(f"placements: baily {b} has a non-numeric anchor_hr {hr!r}")
        if (b, hr) in seen:
            fail(f"placements: duplicate row for baily {b}, anchor {hr or '-'}")
        seen.add((b, hr))
        by_baily[b].append(hr)
    for b, hrs in by_baily.items():
        anchors = [h for h in hrs if h]
        if anchors and len(anchors) != len(hrs):
            fail(f"placements: baily {b} mixes anchor rows with a reason row")
        if anchors and len(anchors) < 2:
            fail(f"placements: baily {b} has one anchor; averaging needs at least 2")
        # At most one reason row per entry needs no check of its own: reason
        # rows share the key (baily, ""), so a second one is a duplicate above.
    return rows, by_baily


def validate_figures(doc, sections):
    cons = doc.get("constellation", [])
    if len(cons) != N_CONSTELLATIONS:
        fail(f"expected {N_CONSTELLATIONS} constellations in TOML, found {len(cons)}")
    codes = [c["code"] for c in cons]
    if len(set(codes)) != len(codes):
        fail("duplicate constellation codes in TOML")
    csv_codes = {code for code, _ in sections}
    if set(codes) != csv_codes:
        fail(f"TOML/CSV constellation sets differ: {set(codes) ^ csv_codes}")
    for c in cons:
        code = c["code"]
        figure = set(sections.get((code, "figure"), []))
        n_unformed = len(sections.get((code, "unformed"), []))
        if c["stars_figure"] != len(figure):
            fail(f"{code}: declares {c['stars_figure']} figure stars, CSV has {len(figure)}")
        if c["stars_unformed"] != n_unformed:
            fail(f"{code}: declares {c['stars_unformed']} unformed stars, CSV has {n_unformed}")
        names, referenced = set(), set()
        for s in c.get("stroke", []):
            if s["name"] in names:
                fail(f"{code}: duplicate stroke name {s['name']!r}")
            names.add(s["name"])
            if len(s["stars"]) < 2:
                fail(f"{code}/{s['name']}: a stroke needs at least 2 points")
            bad = [p for p in s["stars"] if p not in figure]
            if bad:  # unformed stars can never be drawn: refs must be figure seqs
                fail(f"{code}/{s['name']}: references non-figure seq(s) {bad}")
            referenced.update(s["stars"])
        undrawn = figure - referenced
        if undrawn:
            fail(f"{code}: figure stars never drawn: {sorted(undrawn)}")
    return cons


def prose(text):
    # The museum TOML hard-wraps description prose; the wrapping is
    # typography, not content — collapse to single-spaced text for the seed.
    return " ".join(text.split())


def write_csv(path, header, rows):
    # lineterminator: csv writes CRLF on every platform; the seeds are LF.
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def main():
    stars, sections = load_stars()
    with open(MUSEUM / "almagest_figures.toml", "rb") as f:
        doc = tomllib.load(f)
    cons = validate_figures(doc, sections)
    placements, placed_by = load_placements({int(r["baily"]) for r in stars})

    SEED_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(MUSEUM / "almagest_stars.csv", SEED_DIR / "almagest_stars.csv")
    shutil.copyfile(MUSEUM / "almagest_placements.csv",
                    SEED_DIR / "almagest_placements.csv")

    con_rows, stroke_rows, point_rows = [], [], []
    for c in cons:
        con_rows.append([c["code"], c["name_latin"], c["name_english"],
                         c["stars_figure"], c["stars_unformed"], prose(c["description"])])
        for i, s in enumerate(c.get("stroke", []), start=1):
            stroke_rows.append([c["code"], i, s["name"], s["comment"]])
            for j, p in enumerate(s["stars"], start=1):
                point_rows.append([c["code"], i, j, p])

    write_csv(SEED_DIR / "almagest_constellations.csv",
              ["constellation", "name_latin", "name_english",
               "stars_figure", "stars_unformed", "description"], con_rows)
    write_csv(SEED_DIR / "almagest_strokes.csv",
              ["constellation", "stroke_seq", "stroke", "comment"], stroke_rows)
    write_csv(SEED_DIR / "almagest_stroke_points.csv",
              ["constellation", "stroke_seq", "point_order", "seq"], point_rows)

    anchored = sum(1 for hrs in placed_by.values() if any(hrs))
    print(f"validated: {len(stars)} stars | {len(cons)} constellations | "
          f"{len(stroke_rows)} strokes | {len(point_rows)} stroke points")
    print(f"           {len(placements)} placement rows: {anchored} entries anchored, "
          f"{len(placed_by) - anchored} left unplaced with a reason")
    print(f"seeds written to {SEED_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
