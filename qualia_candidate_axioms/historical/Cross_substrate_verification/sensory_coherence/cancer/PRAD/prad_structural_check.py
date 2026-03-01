"""
PRAD — Structure Check Round 2
Three candidates checked together

GSE32571  — 59 tumor + 39 benign
            Gleason + ERG annotated
            Illumina microarray
            normalized matrix present

GSE55945  — Radical prostatectomy
            Gleason + ERG + T-stage
            RAW.tar only

GSE21034  — MSKCC large cohort
            Gleason + ERG
            Affymetrix exon arrays

Author: Eric Robert Lawson
Framework: OrganismCore Phase 0
Date: 2026-03-01
"""

import urllib.request
import gzip
import io
import os
import time

BASE_DIR = "./prad_false_attractor/"
os.makedirs(BASE_DIR, exist_ok=True)

CANDIDATES = {
    "GSE32571": {
        "note": "59 tumor + 39 benign "
                "Gleason + ERG annotated",
        "series_url": (
            "https://www.ncbi.nlm.nih.gov/geo/"
            "query/acc.cgi?acc=GSE32571"
            "&targ=self&form=text&view=full"
        ),
        "meta_url": (
            "https://www.ncbi.nlm.nih.gov/geo/"
            "query/acc.cgi?acc=GSE32571"
            "&targ=gsm&form=text&view=full"
        ),
    },
    "GSE55945": {
        "note": "Radical prostatectomy "
                "Gleason + ERG + T-stage",
        "series_url": (
            "https://www.ncbi.nlm.nih.gov/geo/"
            "query/acc.cgi?acc=GSE55945"
            "&targ=self&form=text&view=full"
        ),
        "meta_url": (
            "https://www.ncbi.nlm.nih.gov/geo/"
            "query/acc.cgi?acc=GSE55945"
            "&targ=gsm&form=text&view=full"
        ),
    },
    "GSE21034": {
        "note": "MSKCC large cohort "
                "Gleason + ERG Affymetrix",
        "series_url": (
            "https://www.ncbi.nlm.nih.gov/geo/"
            "query/acc.cgi?acc=GSE21034"
            "&targ=self&form=text&view=full"
        ),
        "meta_url": (
            "https://www.ncbi.nlm.nih.gov/geo/"
            "query/acc.cgi?acc=GSE21034"
            "&targ=gsm&form=text&view=full"
        ),
    },
}

# ============================================================
# FETCH
# ============================================================

def fetch(url, timeout=30):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(
        req, timeout=timeout
    ) as r:
        return r.read().decode("utf-8")

# ============================================================
# PARSE
# ============================================================

def parse_series(text):
    data = {}
    for line in text.split("\n"):
        for key in [
            "!Series_title",
            "!Series_summary",
            "!Series_overall_design",
            "!Series_organism",
            "!Series_sample_count",
            "!Series_supplementary_file",
        ]:
            if line.startswith(key):
                existing = data.get(key, "")
                addition = \
                    line.split("=", 1)[1].strip()
                data[key] = (
                    existing + " " + addition
                ).strip()
    return data


def parse_samples(text):
    samples, current = [], {}
    for line in text.split("\n"):
        if line.startswith("^SAMPLE"):
            if current:
                samples.append(current)
            current = {
                "gsm": line.split("=")[1].strip()
            }
        elif line.startswith("!Sample_title"):
            current["title"] = \
                line.split("=", 1)[1].strip()
        elif line.startswith(
                "!Sample_source_name_ch1"):
            current["source"] = \
                line.split("=", 1)[1].strip()
        elif line.startswith(
                "!Sample_characteristics_ch1"):
            val = line.split("=", 1)[1].strip()
            if ":" in val:
                k, v = val.split(":", 1)
                current[
                    k.strip().lower()
                    .replace(" ", "_")
                ] = v.strip()
    if current:
        samples.append(current)
    return samples


def classify(samples):
    tumor_s, normal_s, other_s = [], [], []
    for s in samples:
        combined = " ".join(
            str(v) for v in s.values()
        ).lower()
        if any(kw in combined for kw in [
            "normal", "benign", "adjacent",
            "non-tumor", "non-malignant",
            "non-cancer", "bph",
        ]):
            normal_s.append(s)
        elif any(kw in combined for kw in [
            "tumor", "cancer", "malignant",
            "carcinoma", "adenocarcinoma",
            "pca", "prad",
        ]):
            tumor_s.append(s)
        else:
            other_s.append(s)
    return tumor_s, normal_s, other_s


def peek_matrix(url, label):
    print(f"\n  Peeking: {label}")
    print(f"  URL: ...{url[-60:]}")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(
            req, timeout=30
        ) as r:
            raw = r.read(65536)
        try:
            with gzip.open(
                io.BytesIO(raw), "rt"
            ) as gz:
                lines = []
                for line in gz:
                    lines.append(line.rstrip())
                    if len(lines) >= 8:
                        break
            print(f"  Lines read: {len(lines)}")
            for i, l in enumerate(lines[:5]):
                print(f"    {i+1}: {l[:110]}")
            if lines:
                header = lines[0].split("\t")
                print(f"  Columns: {len(header)}")
                print(f"  First 5: {header[:5]}")
                print(f"  Last  5: {header[-5:]}")
            return True
        except Exception as e:
            print(f"  gz error: {e}")
            print(f"  Raw (150b): {raw[:150]}")
            return False
    except Exception as e:
        print(f"  Fetch error: {e}")
        return False

# ============================================================
# CHECK ONE DATASET
# ============================================================

def check_dataset(acc, info):
    print(f"\n{'='*65}")
    print(f"CHECKING: {acc}")
    print(f"Note: {info['note']}")
    print(f"{'='*65}")

    # Series
    print("\n  --- Series ---")
    try:
        stext  = fetch(info["series_url"])
        series = parse_series(stext)
        for k, v in series.items():
            if "supplementary" not in k:
                print(f"  {k}: {v[:150]}")

        suppl_files = []
        for line in stext.split("\n"):
            if "!Series_supplementary_file" \
                    in line:
                fname = \
                    line.split("=", 1)[1].strip()
                suppl_files.append(fname)
                print(f"  Suppl: {fname[-70:]}")

    except Exception as e:
        print(f"  Series error: {e}")
        suppl_files = []
        stext = ""

    time.sleep(0.5)

    # Samples
    print("\n  --- Samples ---")
    try:
        mtext   = fetch(info["meta_url"])
        samples = parse_samples(mtext)
        tumor_s, normal_s, other_s = \
            classify(samples)

        print(f"  Total  : {len(samples)}")
        print(f"  Tumor  : {len(tumor_s)}")
        print(f"  Normal : {len(normal_s)}")
        print(f"  Other  : {len(other_s)}")

        # All characteristic keys
        all_keys = set()
        for s in samples:
            for k in s.keys():
                if k not in [
                    "gsm", "title",
                    "source",
                ]:
                    all_keys.add(k)
        print(f"  Char keys: {sorted(all_keys)}")

        # Clinical annotations
        gleason_key = None
        erg_key     = None
        stage_key   = None

        for k in all_keys:
            kl = k.lower()
            if "gleason" in kl:
                gleason_key = k
            if "erg" in kl or "fusion" in kl:
                erg_key = k
            if "stage" in kl or "tstage" in kl:
                stage_key = k

        if gleason_key:
            print(f"\n  GLEASON KEY: '{gleason_key}'")
            gvals = {}
            for s in tumor_s:
                v = s.get(gleason_key, "NA")
                gvals[v] = gvals.get(v, 0) + 1
            print(f"  Gleason dist: {gvals}")

        if erg_key:
            print(f"\n  ERG KEY: '{erg_key}'")
            evals = {}
            for s in samples:
                v = s.get(erg_key, "NA")
                evals[v] = evals.get(v, 0) + 1
            print(f"  ERG dist: {evals}")

        if stage_key:
            print(f"\n  STAGE KEY: '{stage_key}'")
            stvals = {}
            for s in tumor_s:
                v = s.get(stage_key, "NA")
                stvals[v] = stvals.get(v, 0) + 1
            print(f"  Stage dist: {stvals}")

        # Show first 3 tumor
        print(f"\n  First 3 TUMOR samples:")
        for s in tumor_s[:3]:
            print(
                f"    {s['gsm']} — "
                f"{s.get('title','')[:55]}"
            )
            for k, v in s.items():
                if k not in ["gsm", "title"]:
                    print(f"      {k}: {v}")

        # Show first 3 normal
        print(f"\n  First 3 NORMAL samples:")
        for s in normal_s[:3]:
            print(
                f"    {s['gsm']} — "
                f"{s.get('title','')[:55]}"
            )
            for k, v in s.items():
                if k not in ["gsm", "title"]:
                    print(f"      {k}: {v}")

    except Exception as e:
        print(f"  Sample error: {e}")
        tumor_s  = []
        normal_s = []
        all_keys = set()
        gleason_key = None
        erg_key     = None

    time.sleep(0.5)

    # Matrix peek
    print(f"\n  --- Matrix Peek ---")
    matrix_found = False
    for fname in suppl_files:
        flower = fname.lower()
        if any(ext in flower for ext in [
            ".txt.gz", ".csv.gz",
            "normalized", "matrix",
            "count", "express",
            "cpm", "tpm", "signal",
        ]) and "raw" not in flower:
            matrix_found = peek_matrix(
                fname, acc
            )
            if matrix_found:
                break
            time.sleep(0.3)

    if not matrix_found and suppl_files:
        print(f"  No direct matrix — "
              f"RAW.tar only")
        print(f"  Files: "
              f"{[f[-35:] for f in suppl_files]}")

    # Verdict
    print(f"\n  --- VERDICT ---")
    n_t = len(tumor_s)
    n_n = len(normal_s)
    has_g = gleason_key is not None
    has_e = erg_key is not None

    checks = {
        "Tumor n>=20":     n_t >= 20,
        "Normal n>=3":     n_n >= 3,
        "Gleason present": has_g,
        "ERG present":     has_e,
        "Matrix/suppl":    len(suppl_files) > 0,
        "Matrix direct":   matrix_found,
    }
    all_pass = True
    for c, v in checks.items():
        mark = "✓" if v else "✗"
        print(f"    {mark} {c}")
        if not v:
            all_pass = False

    print(
        f"\n  VERDICT: "
        f"{'✅ PROCEED' if all_pass else '⚠️  INVESTIGATE'}"
    )
    print(f"  Tumor={n_t}  Normal={n_n}  "
          f"Gleason={'YES' if has_g else 'NO'}  "
          f"ERG={'YES' if has_e else 'NO'}")

    return {
        "acc":      acc,
        "n_tumor":  n_t,
        "n_normal": n_n,
        "gleason":  has_g,
        "erg":      has_e,
        "matrix":   matrix_found,
        "suppl":    suppl_files,
        "pass":     all_pass,
    }

# ============================================================
# MAIN
# ============================================================

print("=" * 65)
print("PRAD — STRUCTURE CHECK ROUND 2")
print("Three candidates")
print("Date: 2026-03-01")
print("=" * 65)

verdicts = []
for acc, info in CANDIDATES.items():
    result = check_dataset(acc, info)
    verdicts.append(result)
    time.sleep(1.0)

print(f"\n{'='*65}")
print("FINAL COMPARISON")
print(f"{'='*65}")
print(
    f"  {'Accession':<12} {'Tumor':>7} "
    f"{'Normal':>7} {'Gleason':>9} "
    f"{'ERG':>5} {'Matrix':>8} {'Pass':>6}"
)
print(f"  {'-'*56}")
for v in verdicts:
    print(
        f"  {v['acc']:<12} "
        f"{v['n_tumor']:>7} "
        f"{v['n_normal']:>7} "
        f"{'✓' if v['gleason'] else '✗':>9} "
        f"{'✓' if v['erg'] else '✗':>5} "
        f"{'✓' if v['matrix'] else '✗':>8} "
        f"{'✅' if v['pass'] else '⚠️ ':>6}"
    )

passed = [v for v in verdicts if v["pass"]]
if passed:
    best = max(
        passed,
        key=lambda x: (
            x["n_tumor"] + x["n_normal"]
            + (50 if x["gleason"] else 0)
            + (20 if x["erg"] else 0)
        ),
    )
    print(f"\n  RECOMMENDED: {best['acc']}")
    print(
        f"  T={best['n_tumor']}  "
        f"N={best['n_normal']}  "
        f"Gleason={'YES' if best['gleason'] else 'NO'}  "
        f"ERG={'YES' if best['erg'] else 'NO'}"
    )
else:
    print(
        "\n  No full pass — "
        "review all three manually"
    )

print("\n=== STRUCTURE CHECK 2 COMPLETE ===")
