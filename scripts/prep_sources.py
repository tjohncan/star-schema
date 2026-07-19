"""Prepare carried extracts in data/prepared/ from fetched upstream bytes.

Roommate to build_seeds.py, same contract: validate everything first,
write deterministically, exit nonzero touching no output on any violation.

Reads   data/fetched/vvg_almagest/ptolema.dat   (CDS J/A+A/544/A31)
        data/fetched/yale_bsc5/ybsc5.gz         (Yale BSC5, Harvard TDC copy)
Writes  data/prepared/vvg_almagest_crosswalk.csv
        data/prepared/yale_bright_star.csv

data/fetched/ is gitignored: inputs are provisioned by the operator, never by
the build (`dbt build` does not run this and touches no network).
Run with --fetch to download the inputs from the canonical URLs below,
or place previously retrieved copies there by hand.
Byte layouts follow each source's ReadMe (fetched alongside the data).
Requires Python 3.9+ (stdlib only).
"""

import csv
import gzip
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FETCHED = ROOT / "data" / "fetched"
PREPARED = ROOT / "data" / "prepared"

CANONICAL = [
    ("vvg_almagest/ReadMe", "https://cdsarc.cds.unistra.fr/ftp/J/A+A/544/A31/ReadMe"),
    ("vvg_almagest/ptolema.dat", "https://cdsarc.cds.unistra.fr/ftp/J/A+A/544/A31/ptolema.dat"),
    ("yale_bsc5/ybsc5.readme", "http://tdc-www.harvard.edu/catalogs/ybsc5.readme"),
    ("yale_bsc5/ybsc5.gz", "http://tdc-www.harvard.edu/catalogs/ybsc5.gz"),
]

# Shared stars: Ptolemy catalogues three stars twice (two Baily numbers each);
# the crosswalk must map both entries of a pair to the same HIP star.
SHARED_STARS = {25428: (230, 400), 76041: (96, 147), 113368: (670, 1011)}


def fail(msg):
    sys.exit(f"FAIL: {msg}")


def fetch():
    for rel, url in CANONICAL:
        dest = FETCHED / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"fetching {url}")
        urllib.request.urlretrieve(url, dest)


def require(rel):
    path = FETCHED / rel
    if not path.exists():
        fail(f"missing input {path}\n"
             f"  run `py scripts/prep_sources.py --fetch`, or place a "
             f"previously retrieved copy there (canonical URLs in this script)")
    return path


def fld(line, a, b):
    """1-based inclusive byte slice per CDS ReadMe convention."""
    return line[a - 1:b].strip()


def parse_crosswalk():
    rows = []
    with open(require("vvg_almagest/ptolema.dat"), encoding="ascii") as f:
        for line in f:
            hip = int(line[40:46])
            rows.append({
                "baily": int(line[0:4]),
                "hip": hip if hip else None,
                "id_quality": int(line[47:48]),
                "ptolemy_mag": int(line[37:38]),
                "mag_qualifier": line[38:39].strip() or None,
            })
    if sorted(r["baily"] for r in rows) != list(range(1, 1029)):
        fail("crosswalk: baily numbers are not exactly 1..1028")
    if not all(1 <= r["id_quality"] <= 6 for r in rows):
        fail("crosswalk: id_quality outside 1..6")
    by_baily = {r["baily"]: r for r in rows}
    for hip, (a, b) in SHARED_STARS.items():
        if not (by_baily[a]["hip"] == by_baily[b]["hip"] == hip):
            fail(f"crosswalk: shared star hip {hip} not at baily {a}/{b}")
    return rows


def parse_bright_stars():
    rows = []
    with gzip.open(require("yale_bsc5/ybsc5.gz"), "rt", encoding="latin-1") as f:
        for line in f:
            line = line.rstrip("\n").ljust(197)
            name = line[4:14]
            ghost = fld(line, 76, 77) == ""  # blank position: novae etc.
            if ghost:
                ra = dec = None
            else:
                ra = 15 * (int(fld(line, 76, 77)) + int(fld(line, 78, 79)) / 60
                           + float(fld(line, 80, 83)) / 3600)
                dec = (int(fld(line, 85, 86)) + int(fld(line, 87, 88)) / 60
                       + int(fld(line, 89, 90)) / 3600)
                if fld(line, 84, 84) == "-":
                    dec = -dec
            rows.append({
                "hr": int(fld(line, 1, 4)),
                "name": name.rstrip() or None,
                "flamsteed": name[0:3].strip() or None,
                "bayer": name[3:6].strip() or None,
                "bayer_sup": name[6:7].strip() or None,
                "cst": name[7:10].strip() or None,
                "hd": int(fld(line, 26, 31)) if fld(line, 26, 31) else None,
                "sao": int(fld(line, 32, 37)) if fld(line, 32, 37) else None,
                "var_id": fld(line, 52, 60) or None,
                "ra_deg_j2000": round(ra, 6) if ra is not None else None,
                "dec_deg_j2000": round(dec, 6) if dec is not None else None,
                "vmag": float(fld(line, 103, 107)) if fld(line, 103, 107) else None,
                "vmag_code": fld(line, 108, 108) or None,
                "b_v": float(fld(line, 110, 114)) if fld(line, 110, 114) else None,
                "sp_type": fld(line, 128, 147) or None,
                "pm_ra_arcsec": float(fld(line, 149, 154)) if fld(line, 149, 154) else None,
                "pm_de_arcsec": float(fld(line, 155, 160)) if fld(line, 155, 160) else None,
                "parallax_arcsec": float(fld(line, 162, 166)) if fld(line, 162, 166) else None,
                "is_ghost": "true" if ghost else "false",
            })
    if sorted(r["hr"] for r in rows) != list(range(1, 9111)):
        fail("bright stars: HR numbers are not exactly 1..9110")
    n_ghost = sum(r["is_ghost"] == "true" for r in rows)
    if n_ghost != 14:
        fail(f"bright stars: expected 14 ghost entries, found {n_ghost}")
    for r in rows:
        if r["is_ghost"] == "false":
            if not (0 <= r["ra_deg_j2000"] < 360 and -90 <= r["dec_deg_j2000"] <= 90):
                fail(f"bright stars: HR {r['hr']} position out of range")
            if r["vmag"] is None or not (-2 <= r["vmag"] <= 14):
                fail(f"bright stars: HR {r['hr']} vmag implausible: {r['vmag']}")
    by_hr = {r["hr"]: r for r in rows}
    if by_hr[2491]["cst"] != "CMa" or by_hr[2491]["vmag"] > -1:
        fail("bright stars: HR 2491 should be Sirius (CMa, brightest)")
    if by_hr[7001]["cst"] != "Lyr" or by_hr[7001]["vmag"] > 0.2:
        fail("bright stars: HR 7001 should be Vega (Lyr, ~0.03)")
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def main():
    if "--fetch" in sys.argv:
        fetch()
    crosswalk = parse_crosswalk()
    bright = parse_bright_stars()

    PREPARED.mkdir(parents=True, exist_ok=True)
    write_csv(PREPARED / "vvg_almagest_crosswalk.csv", crosswalk)
    write_csv(PREPARED / "yale_bright_star.csv", bright)

    no_hip = sum(r["hip"] is None for r in crosswalk)
    print(f"validated: crosswalk {len(crosswalk)} rows ({no_hip} without HIP id) | "
          f"bright stars {len(bright)} rows (14 ghosts)")
    print(f"prepared extracts written to {PREPARED.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
