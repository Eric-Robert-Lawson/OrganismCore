"""
PAAD — Structure Check Round 2
Checking backup candidates in parallel

GSE28735  — 45 matched pairs tumor/normal
GSE62452  — 69 tumor + 61 adjacent normal
GSE183795 — 139 tumor + 102 adjacent normal

Author: Eric Robert Lawson
Framework: OrganismCore Phase 0
Date: 2026-03-01
"""

import urllib.request
import gzip
import io
import os
import time

BASE_DIR = "./paad_false_attractor/"
os.makedirs(BASE_DIR, exist_ok=True)

CANDIDATES = {
    "GSE28735": {
        "note": "45 matched pairs tumor/adjacent",
        "meta_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE28735&targ=gsm"
            "&form=text&view=full"
        ),
        "series_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE28735&targ=self"
            "&form=text&view=full"
        ),
    },
    "GSE62452": {
        "note": "69 tumor + 61 adjacent normal",
        "meta_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE62452&targ=gsm"
            "&form=text&view=full"
        ),
        "series_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE62452&targ=self"
            "&form=text&view=full"
        ),
    },
    "GSE183795": {
        "note": "139 tumor + 102 adjacent normal",
        "meta_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE183795&targ=gsm"
            "&form=text&view=full"
        ),
        "series_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE183795&targ=self"
            "&form=text&view=full"
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
                addition = line.split("=", 1)[1].strip()
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
        elif line.startswith(
                "!Sample_supplementary_file"):
            current.setdefault("files", []).append(
                line.split("=", 1)[1].strip()
            )
    if current:
        samples.append(current)
    return samples


def classify_samples(samples):
    tumor_list  = []
    normal_list = []
    other_list  = []

    for s in samples:
        combined = " ".join(
            str(v) for k, v in s.items()
            if k != "files"
        ).lower()

        is_normal = any(kw in combined for kw in [
            "adjacent", "non-tumor", "nontumor",
            "non-neoplastic", "normal pancrea",
            "healthy", "control",
        ])
        is_tumor = any(kw in combined for kw in [
            "tumor", "cancer", "pdac",
            "adenocarcinoma", "carcinoma",
            "malignant", "neoplasm",
        ])
        is_cell_line = any(kw in combined for kw in [
            "cell line", "cellline", "in vitro",
        ])

        if is_cell_line:
            other_list.append(s)
        elif is_normal:
            normal_list.append(s)
        elif is_tumor:
            tumor_list.append(s)
        else:
            other_list.append(s)

    return tumor_list, normal_list, other_list


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

    # Series metadata
    print("\n  --- Series ---")
    try:
        stext  = fetch(info["series_url"])
        series = parse_series(stext)
        for k, v in series.items():
            if k != "!Series_supplementary_file":
                print(f"  {k}: {v[:150]}")

        suppl_files = []
        for line in stext.split("\n"):
            if "!Series_supplementary_file" in line:
                fname = line.split("=", 1)[1].strip()
                suppl_files.append(fname)
                print(f"  Suppl: {fname[-70:]}")

    except Exception as e:
        print(f"  Series fetch error: {e}")
        suppl_files = []
        stext = ""

    time.sleep(0.5)

    # Sample metadata
    print("\n  --- Samples ---")
    try:
        mtext   = fetch(info["meta_url"])
        samples = parse_samples(mtext)
        tumor_s, normal_s, other_s = \
            classify_samples(samples)

        print(f"  Total    : {len(samples)}")
        print(f"  Tumor    : {len(tumor_s)}")
        print(f"  Normal   : {len(normal_s)}")
        print(f"  Other    : {len(other_s)}")

        # Show characteristic keys
        all_keys = set()
        for s in samples:
            for k in s.keys():
                if k not in ["gsm", "title",
                              "source", "files"]:
                    all_keys.add(k)
        print(f"  Char keys: {sorted(all_keys)}")

        # Show 3 tumor samples
        print(f"\n  First 3 TUMOR samples:")
        for s in tumor_s[:3]:
            print(f"    {s['gsm']} — "
                  f"{s.get('title','')[:60]}")
            for k, v in s.items():
                if k not in ["gsm", "title",
                              "files"]:
                    print(f"      {k}: {v}")

        # Show 3 normal samples
        print(f"\n  First 3 NORMAL samples:")
        for s in normal_s[:3]:
            print(f"    {s['gsm']} — "
                  f"{s.get('title','')[:60]}")
            for k, v in s.items():
                if k not in ["gsm", "title",
                              "files"]:
                    print(f"      {k}: {v}")

        # Check for subtypes in characteristics
        subtype_keys = [
            k for k in all_keys
            if any(t in k for t in [
                "subtype", "type", "class",
                "moffitt", "grade", "stage",
                "classical", "basal",
            ])
        ]
        if subtype_keys:
            print(f"\n  Subtype keys: {subtype_keys}")
            for k in subtype_keys:
                vals = {}
                for s in samples:
                    v = s.get(k, "NA")
                    vals[v] = vals.get(v, 0) + 1
                print(f"  {k}: {vals}")

    except Exception as e:
        print(f"  Sample fetch error: {e}")
        tumor_s  = []
        normal_s = []

    time.sleep(0.5)

    # Matrix peek
    print(f"\n  --- Matrix Peek ---")
    matrix_found = False
    for fname in suppl_files:
        flower = fname.lower()
        if any(ext in flower for ext in [
            ".txt.gz", ".csv.gz",
            "normalized", "matrix",
            "count", "express", "cpm", "tpm",
        ]):
            matrix_found = peek_matrix(fname, acc)
            if matrix_found:
                break
            time.sleep(0.3)

    if not matrix_found and suppl_files:
        print(f"  No direct matrix file found")
        print(f"  Available: "
              f"{[f[-40:] for f in suppl_files]}")

    # Verdict
    print(f"\n  --- VERDICT ---")
    n_t = len(tumor_s)
    n_n = len(normal_s)
    checks = {
        "Tumor n>=20":    n_t >= 20,
        "Normal n>=3":    n_n >= 3,
        "Has suppl file": len(suppl_files) > 0,
        "Matrix found":   matrix_found,
    }
    all_pass = True
    for c, v in checks.items():
        mark = "✓" if v else "✗"
        print(f"    {mark} {c}")
        if not v:
            all_pass = False

    print(f"\n  VERDICT: "
          f"{'✅ PROCEED' if all_pass else '⚠️  INVESTIGATE'}")
    print(f"  Tumor: {n_t}  Normal: {n_n}")

    return {
        "acc":     acc,
        "n_tumor": n_t,
        "n_normal": n_n,
        "pass":    all_pass,
        "suppl":   suppl_files,
        "matrix":  matrix_found,
    }

# ============================================================
# MAIN
# ============================================================

print("=" * 65)
print("PAAD — STRUCTURE CHECK ROUND 2")
print("Three backup candidates")
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
print(f"  {'Accession':<12} {'Tumor':>7} "
      f"{'Normal':>7} {'Matrix':>8} {'Pass':>6}")
print(f"  {'-'*44}")
for v in verdicts:
    print(
        f"  {v['acc']:<12} "
        f"{v['n_tumor']:>7} "
        f"{v['n_normal']:>7} "
        f"{'✓' if v['matrix'] else '✗':>8} "
        f"{'✅' if v['pass'] else '⚠️ ':>6}"
    )

# Pick winner
passed = [v for v in verdicts if v["pass"]]
if passed:
    best = max(
        passed,
        key=lambda x: x["n_tumor"] + x["n_normal"]
    )
    print(f"\n  RECOMMENDED: {best['acc']}")
    print(f"  Tumor: {best['n_tumor']}  "
          f"Normal: {best['n_normal']}")
else:
    best = max(
        verdicts,
        key=lambda x: x["n_tumor"] + x["n_normal"]
    )
    print(f"\n  BEST AVAILABLE: {best['acc']}")
    print(f"  Needs investigation")

print("\n=== STRUCTURE CHECK 2 COMPLETE ===")"""
PAAD — Structure Check Round 2
Checking backup candidates in parallel

GSE28735  — 45 matched pairs tumor/normal
GSE62452  — 69 tumor + 61 adjacent normal
GSE183795 — 139 tumor + 102 adjacent normal

Author: Eric Robert Lawson
Framework: OrganismCore Phase 0
Date: 2026-03-01
"""

import urllib.request
import gzip
import io
import os
import time

BASE_DIR = "./paad_false_attractor/"
os.makedirs(BASE_DIR, exist_ok=True)

CANDIDATES = {
    "GSE28735": {
        "note": "45 matched pairs tumor/adjacent",
        "meta_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE28735&targ=gsm"
            "&form=text&view=full"
        ),
        "series_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE28735&targ=self"
            "&form=text&view=full"
        ),
    },
    "GSE62452": {
        "note": "69 tumor + 61 adjacent normal",
        "meta_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE62452&targ=gsm"
            "&form=text&view=full"
        ),
        "series_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE62452&targ=self"
            "&form=text&view=full"
        ),
    },
    "GSE183795": {
        "note": "139 tumor + 102 adjacent normal",
        "meta_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE183795&targ=gsm"
            "&form=text&view=full"
        ),
        "series_url": (
            "https://www.ncbi.nlm.nih.gov/geo/query/"
            "acc.cgi?acc=GSE183795&targ=self"
            "&form=text&view=full"
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
                addition = line.split("=", 1)[1].strip()
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
        elif line.startswith(
                "!Sample_supplementary_file"):
            current.setdefault("files", []).append(
                line.split("=", 1)[1].strip()
            )
    if current:
        samples.append(current)
    return samples


def classify_samples(samples):
    tumor_list  = []
    normal_list = []
    other_list  = []

    for s in samples:
        combined = " ".join(
            str(v) for k, v in s.items()
            if k != "files"
        ).lower()

        is_normal = any(kw in combined for kw in [
            "adjacent", "non-tumor", "nontumor",
            "non-neoplastic", "normal pancrea",
            "healthy", "control",
        ])
        is_tumor = any(kw in combined for kw in [
            "tumor", "cancer", "pdac",
            "adenocarcinoma", "carcinoma",
            "malignant", "neoplasm",
        ])
        is_cell_line = any(kw in combined for kw in [
            "cell line", "cellline", "in vitro",
        ])

        if is_cell_line:
            other_list.append(s)
        elif is_normal:
            normal_list.append(s)
        elif is_tumor:
            tumor_list.append(s)
        else:
            other_list.append(s)

    return tumor_list, normal_list, other_list


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

    # Series metadata
    print("\n  --- Series ---")
    try:
        stext  = fetch(info["series_url"])
        series = parse_series(stext)
        for k, v in series.items():
            if k != "!Series_supplementary_file":
                print(f"  {k}: {v[:150]}")

        suppl_files = []
        for line in stext.split("\n"):
            if "!Series_supplementary_file" in line:
                fname = line.split("=", 1)[1].strip()
                suppl_files.append(fname)
                print(f"  Suppl: {fname[-70:]}")

    except Exception as e:
        print(f"  Series fetch error: {e}")
        suppl_files = []
        stext = ""

    time.sleep(0.5)

    # Sample metadata
    print("\n  --- Samples ---")
    try:
        mtext   = fetch(info["meta_url"])
        samples = parse_samples(mtext)
        tumor_s, normal_s, other_s = \
            classify_samples(samples)

        print(f"  Total    : {len(samples)}")
        print(f"  Tumor    : {len(tumor_s)}")
        print(f"  Normal   : {len(normal_s)}")
        print(f"  Other    : {len(other_s)}")

        # Show characteristic keys
        all_keys = set()
        for s in samples:
            for k in s.keys():
                if k not in ["gsm", "title",
                              "source", "files"]:
                    all_keys.add(k)
        print(f"  Char keys: {sorted(all_keys)}")

        # Show 3 tumor samples
        print(f"\n  First 3 TUMOR samples:")
        for s in tumor_s[:3]:
            print(f"    {s['gsm']} — "
                  f"{s.get('title','')[:60]}")
            for k, v in s.items():
                if k not in ["gsm", "title",
                              "files"]:
                    print(f"      {k}: {v}")

        # Show 3 normal samples
        print(f"\n  First 3 NORMAL samples:")
        for s in normal_s[:3]:
            print(f"    {s['gsm']} — "
                  f"{s.get('title','')[:60]}")
            for k, v in s.items():
                if k not in ["gsm", "title",
                              "files"]:
                    print(f"      {k}: {v}")

        # Check for subtypes in characteristics
        subtype_keys = [
            k for k in all_keys
            if any(t in k for t in [
                "subtype", "type", "class",
                "moffitt", "grade", "stage",
                "classical", "basal",
            ])
        ]
        if subtype_keys:
            print(f"\n  Subtype keys: {subtype_keys}")
            for k in subtype_keys:
                vals = {}
                for s in samples:
                    v = s.get(k, "NA")
                    vals[v] = vals.get(v, 0) + 1
                print(f"  {k}: {vals}")

    except Exception as e:
        print(f"  Sample fetch error: {e}")
        tumor_s  = []
        normal_s = []

    time.sleep(0.5)

    # Matrix peek
    print(f"\n  --- Matrix Peek ---")
    matrix_found = False
    for fname in suppl_files:
        flower = fname.lower()
        if any(ext in flower for ext in [
            ".txt.gz", ".csv.gz",
            "normalized", "matrix",
            "count", "express", "cpm", "tpm",
        ]):
            matrix_found = peek_matrix(fname, acc)
            if matrix_found:
                break
            time.sleep(0.3)

    if not matrix_found and suppl_files:
        print(f"  No direct matrix file found")
        print(f"  Available: "
              f"{[f[-40:] for f in suppl_files]}")

    # Verdict
    print(f"\n  --- VERDICT ---")
    n_t = len(tumor_s)
    n_n = len(normal_s)
    checks = {
        "Tumor n>=20":    n_t >= 20,
        "Normal n>=3":    n_n >= 3,
        "Has suppl file": len(suppl_files) > 0,
        "Matrix found":   matrix_found,
    }
    all_pass = True
    for c, v in checks.items():
        mark = "✓" if v else "✗"
        print(f"    {mark} {c}")
        if not v:
            all_pass = False

    print(f"\n  VERDICT: "
          f"{'✅ PROCEED' if all_pass else '⚠️  INVESTIGATE'}")
    print(f"  Tumor: {n_t}  Normal: {n_n}")

    return {
        "acc":     acc,
        "n_tumor": n_t,
        "n_normal": n_n,
        "pass":    all_pass,
        "suppl":   suppl_files,
        "matrix":  matrix_found,
    }

# ============================================================
# MAIN
# ============================================================

print("=" * 65)
print("PAAD — STRUCTURE CHECK ROUND 2")
print("Three backup candidates")
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
print(f"  {'Accession':<12} {'Tumor':>7} "
      f"{'Normal':>7} {'Matrix':>8} {'Pass':>6}")
print(f"  {'-'*44}")
for v in verdicts:
    print(
        f"  {v['acc']:<12} "
        f"{v['n_tumor']:>7} "
        f"{v['n_normal']:>7} "
        f"{'✓' if v['matrix'] else '✗':>8} "
        f"{'✅' if v['pass'] else '⚠️ ':>6}"
    )

# Pick winner
passed = [v for v in verdicts if v["pass"]]
if passed:
    best = max(
        passed,
        key=lambda x: x["n_tumor"] + x["n_normal"]
    )
    print(f"\n  RECOMMENDED: {best['acc']}")
    print(f"  Tumor: {best['n_tumor']}  "
          f"Normal: {best['n_normal']}")
else:
    best = max(
        verdicts,
        key=lambda x: x["n_tumor"] + x["n_normal"]
    )
    print(f"\n  BEST AVAILABLE: {best['acc']}")
    print(f"  Needs investigation")

print("\n=== STRUCTURE CHECK 2 COMPLETE ===")
