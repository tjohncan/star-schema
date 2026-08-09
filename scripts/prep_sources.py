"""Prepare carried extracts in data/prepared/ from fetched upstream bytes.

Roommate to build_seeds.py, same contract: validate everything first,
write deterministically, exit nonzero touching no output on any violation.

Reads   data/fetched/vvg_almagest/ptolema.dat   (CDS J/A+A/544/A31)
        data/fetched/yale_bsc5/ybsc5.gz         (Yale BSC5, Harvard TDC copy)
        data/fetched/hipparcos/hip_main.dat     (CDS I/239, ESA 1997)
        data/fetched/wgsn/iau_csn.csv           (IAU WGSN catalog: manual export)
Writes  data/prepared/vvg_almagest_crosswalk.csv
        data/prepared/yale_bright_star.csv
        data/prepared/hipparcos_almagest.csv    (thin slice: crosswalk HIPs only)
        data/prepared/wgsn_star_name.csv

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
    ("hipparcos/ReadMe", "https://cdsarc.cds.unistra.fr/ftp/I/239/ReadMe"),
    ("hipparcos/hip_main.dat", "https://cdsarc.cds.unistra.fr/ftp/I/239/hip_main.dat"),
    ("wgsn/iau_csn.csv",
     "MANUAL: export by hand from "
     "https://exopla.net/star-names/modern-iau-star-names/ — set the table "
     "to 'Show ALL entries', export as CSV, save to this path (the table is "
     "the WGSN's own site; there is no stable file URL)"),
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
        if url.startswith("MANUAL"):
            print(f"manual step for {rel}:\n  {url[8:]}")
            continue
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


def parse_hipparcos(hips):
    """Thin positional slice of hip_main.dat, restricted to the crosswalk's
    HIP set — we carry as little as does the job. Positions are ICRS at
    epoch J1991.25; epoch propagation is warehouse work, not prep work."""
    want = set(hips)
    rows = []
    with open(require("hipparcos/hip_main.dat"), encoding="latin-1") as f:
        for line in f:
            h = fld(line, 9, 14)
            if not h or int(h) not in want:
                continue
            rows.append({
                "hip": int(h),
                "ra_deg": float(fld(line, 52, 63)) if fld(line, 52, 63) else None,
                "dec_deg": float(fld(line, 65, 76)) if fld(line, 65, 76) else None,
                "plx_mas": float(fld(line, 80, 86)) if fld(line, 80, 86) else None,
                "pm_ra_mas_yr": float(fld(line, 88, 95)) if fld(line, 88, 95) else None,
                "pm_de_mas_yr": float(fld(line, 97, 104)) if fld(line, 97, 104) else None,
                "vmag": float(fld(line, 42, 46)) if fld(line, 42, 46) else None,
                "b_v": float(fld(line, 246, 251)) if fld(line, 246, 251) else None,
                "hd": int(fld(line, 391, 396)) if fld(line, 391, 396) else None,
            })
    rows.sort(key=lambda r: r["hip"])
    found = {r["hip"] for r in rows}
    missing = sorted(want - found)
    if missing:
        fail(f"hipparcos: crosswalk HIPs missing from hip_main: {missing}")
    no_pos = [r["hip"] for r in rows if r["ra_deg"] is None]
    for r in rows:
        if r["ra_deg"] is not None and not (0 <= r["ra_deg"] < 360 and -90 <= r["dec_deg"] <= 90):
            fail(f"hipparcos: HIP {r['hip']} position out of range")
    return rows, no_pos


def parse_wgsn():
    rows = []
    with open(require("wgsn/iau_csn.csv"), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            desig = (r.get("Designation") or "").strip()
            hip = (r.get("HIP") or "").strip()
            hr = None
            if desig.startswith("HR "):
                tail = desig[3:].strip()
                if tail.isdigit():
                    hr = int(tail)
            rows.append({
                "proper_name": (r.get("proper names") or "").strip(),
                "designation": desig or None,
                "hip": int(hip) if hip.isdigit() else None,
                "hr": hr,
                "bayer_id": (r.get("Bayer ID") or "").strip() or None,
                "constellation": (r.get("Constellation") or "").strip() or None,
                "origin": (r.get("Origin") or "").strip() or None,
                "language": (r.get("Language") or "").strip() or None,
                "adopted": (r.get("Date of Adoption") or "").strip() or None,
            })
    if len(rows) < 400:
        fail(f"wgsn: implausibly few rows: {len(rows)}")
    if any(not r["proper_name"] for r in rows):
        fail("wgsn: blank proper name")
    by_name = {r["proper_name"]: r for r in rows}
    for name, hip in [("Sirius", 32349), ("Vega", 91262), ("Polaris", 11767)]:
        if name not in by_name or by_name[name]["hip"] != hip:
            fail(f"wgsn: expected {name} = HIP {hip}")
    return rows


def write_csv(path, rows):
    # lineterminator: csv writes CRLF on every platform; the extracts are LF.
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    if "--fetch" in sys.argv:
        fetch()
    crosswalk = parse_crosswalk()
    bright = parse_bright_stars()
    hip_slice, no_pos = parse_hipparcos(r["hip"] for r in crosswalk if r["hip"])
    names = parse_wgsn()

    PREPARED.mkdir(parents=True, exist_ok=True)
    write_csv(PREPARED / "vvg_almagest_crosswalk.csv", crosswalk)
    write_csv(PREPARED / "yale_bright_star.csv", bright)
    write_csv(PREPARED / "hipparcos_almagest.csv", hip_slice)
    write_csv(PREPARED / "wgsn_star_name.csv", names)

    no_hip = sum(r["hip"] is None for r in crosswalk)
    no_hd = sum(r["hd"] is None for r in hip_slice)
    print(f"validated: crosswalk {len(crosswalk)} rows ({no_hip} without HIP id) | "
          f"bright stars {len(bright)} rows (14 ghosts)")
    print(f"           hipparcos slice {len(hip_slice)} stars "
          f"({len(no_pos)} without astrometry: {no_pos}) ({no_hd} without HD)")
    print(f"           wgsn {len(names)} proper names")
    print(f"prepared extracts written to {PREPARED.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
