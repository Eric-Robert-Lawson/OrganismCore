"""
PAAD — Pancreatic Adenocarcinoma
Dataset Discovery Script
Phase 0 of OrganismCore Cancer Analysis Protocol

Scans GEO accessions for:
  - Human pancreatic adenocarcinoma
  - Normal pancreatic tissue / adjacent normal
  - RNA-seq or scRNA-seq
  - Adequate sample counts (n≥5 tumor, n≥3 normal)

Author: Eric Robert Lawson
Framework: OrganismCore
Date: 2026-03-01
Protocol: Phase 0 — Dataset Discovery
"""

import urllib.request
import sys
import time

# ============================================================
# CANDIDATE ACCESSIONS
# Four categories:
#   A: TCGA-PAAD derivatives on GEO
#   B: Known PAAD bulk RNA-seq datasets
#   C: PAAD scRNA-seq candidates
#   D: PAAD + normal pancreas candidates
# ============================================================

CANDIDATES = {

    # ---- CATEGORY A: TCGA-PAAD derivatives ----
    "GSE183795": "TCGA-PAAD derived — candidate",
    "GSE71729":  "PAAD bulk RNA-seq — Moffitt subtypes",
    "GSE62452":  "Pancreatic cancer + normal — Agilent",
    "GSE28735":  "Pancreatic tumor vs adjacent normal",
    "GSE15471":  "Pancreatic tumor vs normal tissue",
    "GSE16515":  "Pancreatic tumor vs normal",
    "GSE32676":  "Pancreatic cancer vs normal",
    "GSE41368":  "Pancreatic cancer RNA-seq",

    # ---- CATEGORY B: PAAD bulk RNA-seq ----
    "GSE93326":  "PAAD bulk RNA-seq candidate",
    "GSE101448": "PAAD bulk RNA-seq candidate",
    "GSE107610": "PAAD + normal candidate",
    "GSE114919": "PAAD candidate",
    "GSE119794": "PAAD candidate",
    "GSE133684": "PAAD + stellate cells",
    "GSE141017": "PAAD bulk candidate",
    "GSE145687": "PAAD candidate",

    # ---- CATEGORY C: scRNA-seq candidates ----
    "GSE155698": "PAAD scRNA-seq candidate",
    "GSE165399": "PAAD scRNA-seq candidate",
    "GSE202051": "PAAD scRNA-seq candidate",
    "GSE212966": "PAAD scRNA-seq — tumor microenv",
    "GSE217255": "PAAD scRNA-seq candidate",
    "GSE243302": "PAAD scRNA-seq candidate",
    "GSE246072": "PAAD scRNA-seq candidate",

    # ---- CATEGORY D: Pancreas normal + tumor ----
    "GSE50827":  "Pancreas normal + PAAD",
    "GSE85195":  "Pancreatic cancer subtypes",
    "GSE103154": "PAAD + normal pancreas",
    "GSE150290": "PAAD acinar/ductal candidate",
    "GSE173208": "Pancreas scRNA-seq candidate",
    "GSE178341": "PAAD + normal candidate",
    "GSE196800": "PAAD + adjacent normal",
    "GSE205013": "PAAD candidate",
}

# ============================================================
# RELEVANCE KEYWORDS
# ============================================================

REQUIRED_KEYWORDS = [
    "pancrea",
]

CANCER_KEYWORDS = [
    "adenocarcinoma", "paad", "pdac",
    "pancreatic cancer", "pancreatic tumor",
    "pancreatic carcinoma", "pancreatic ductal",
]

NORMAL_KEYWORDS = [
    "normal", "healthy", "adjacent",
    "control", "non-tumor", "nontumor",
    "non-neoplastic",
]

SCRNA_KEYWORDS = [
    "single cell", "single-cell", "scrna",
    "10x", "droplet", "seurat",
]

BULK_KEYWORDS = [
    "rna-seq", "rnaseq", "rna seq",
    "microarray", "expression profiling",
    "transcriptom",
]

EXCLUDE_KEYWORDS = [
    "mouse", "mus musculus", "murine",
    "rat ", "rattus",
    "cell line only", "in vitro only",
]

# ============================================================
# FETCH METADATA
# ============================================================

def fetch_geo_metadata(acc, timeout=20):
    url = (f"https://www.ncbi.nlm.nih.gov/geo/query/"
           f"acc.cgi?acc={acc}&targ=self"
           f"&form=text&view=quick")
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(
            req, timeout=timeout
        ) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        return f"ERROR: {e}"


def fetch_sample_metadata(acc, timeout=25):
    url = (f"https://www.ncbi.nlm.nih.gov/geo/query/"
           f"acc.cgi?acc={acc}&targ=gsm"
           f"&form=text&view=quick")
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(
            req, timeout=timeout
        ) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        return f"ERROR: {e}"

# ============================================================
# PARSE SERIES METADATA
# ============================================================

def parse_series(text):
    data = {}
    for line in text.split("\n"):
        for key in ["!Series_title",
                    "!Series_summary",
                    "!Series_overall_design",
                    "!Series_organism",
                    "!Series_sample_count",
                    "!Series_supplementary_file"]:
            if line.startswith(key):
                existing = data.get(key, "")
                addition = line.split("=", 1)[1].strip()
                data[key] = (existing + " " + addition
                             ).strip()
    return data


def parse_samples(text):
    samples = []
    current = {}
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
                "!Sample_source_name"):
            current["source"] = \
                line.split("=", 1)[1].strip()
        elif line.startswith(
                "!Sample_characteristics_ch1"):
            val = line.split("=", 1)[1].strip()
            current.setdefault(
                "chars", []
            ).append(val)
    if current:
        samples.append(current)
    return samples

# ============================================================
# SCORE DATASET
# ============================================================

def score_dataset(acc, series_text, sample_text,
                  note):
    if "ERROR" in series_text:
        return None

    series  = parse_series(series_text)
    samples = parse_samples(sample_text)

    full_series = " ".join(series.values()).lower()
    full_sample = sample_text.lower()
    combined    = full_series + " " + full_sample

    # Hard excludes
    for kw in EXCLUDE_KEYWORDS:
        if kw in combined:
            return {
                "acc": acc, "note": note,
                "verdict": "EXCLUDE",
                "reason": f"excluded: {kw}",
                "score": -1,
                "series": series,
                "n_samples": len(samples),
            }

    # Must be pancreatic
    if not any(kw in combined
               for kw in REQUIRED_KEYWORDS):
        return {
            "acc": acc, "note": note,
            "verdict": "NOT PANCREATIC",
            "reason": "pancrea not found",
            "score": 0,
            "series": series,
            "n_samples": len(samples),
        }

    # Must be human
    organism = series.get(
        "!Series_organism", ""
    ).lower()
    is_human = (
        "homo sapiens" in organism or
        "human" in combined
    )
    if not is_human:
        return {
            "acc": acc, "note": note,
            "verdict": "NOT HUMAN",
            "reason": f"organism: {organism}",
            "score": 0,
            "series": series,
            "n_samples": len(samples),
        }

    # Score
    score = 0
    flags = []

    # Cancer present
    has_cancer = any(kw in combined
                     for kw in CANCER_KEYWORDS)
    if has_cancer:
        score += 3
        flags.append("has_cancer")

    # Normal present
    has_normal = any(kw in combined
                     for kw in NORMAL_KEYWORDS)
    if has_normal:
        score += 3
        flags.append("has_normal")

    # Data type
    is_scrna = any(kw in combined
                   for kw in SCRNA_KEYWORDS)
    is_bulk  = any(kw in combined
                   for kw in BULK_KEYWORDS)
    if is_scrna:
        score += 2
        flags.append("scrna")
    elif is_bulk:
        score += 1
        flags.append("bulk")

    # Sample count
    n_str   = series.get("!Series_sample_count", "0")
    n_total = 0
    try:
        n_total = int(n_str.strip())
    except Exception:
        pass

    if n_total >= 50:
        score += 3
        flags.append(f"n={n_total}")
    elif n_total >= 20:
        score += 2
        flags.append(f"n={n_total}")
    elif n_total >= 8:
        score += 1
        flags.append(f"n={n_total}")
    else:
        flags.append(f"n={n_total}")

    # Supplementary files
    suppl = series.get(
        "!Series_supplementary_file", ""
    ).lower()
    if any(ext in suppl for ext in
           [".txt.gz", ".csv.gz", ".h5",
            "matrix.mtx", "count", "cpm", "tpm"]):
        score += 2
        flags.append("has_suppl_matrix")

    # Classify
    if score >= 9:
        verdict = "EXCELLENT"
    elif score >= 7:
        verdict = "STRONG"
    elif score >= 5:
        verdict = "CANDIDATE"
    elif score >= 3:
        verdict = "WEAK"
    else:
        verdict = "POOR"

    if not has_cancer:
        verdict = "NO_CANCER"
    if not has_normal and score < 6:
        verdict = "NO_NORMAL"

    return {
        "acc":       acc,
        "note":      note,
        "verdict":   verdict,
        "score":     score,
        "flags":     flags,
        "series":    series,
        "n_samples": n_total,
        "has_cancer": has_cancer,
        "has_normal": has_normal,
        "is_scrna":   is_scrna,
        "is_bulk":    is_bulk,
    }

# ============================================================
# PRINT RESULT
# ============================================================

def print_result(result):
    if result is None:
        return

    verdict = result["verdict"]
    acc     = result["acc"]
    score   = result.get("score", 0)
    flags   = result.get("flags", [])
    n       = result.get("n_samples", 0)

    # Only print relevant results
    if verdict in ["NOT PANCREATIC",
                   "NOT HUMAN", "POOR"]:
        print(f"  {acc}: {verdict}")
        return

    if verdict == "EXCLUDE":
        print(f"  {acc}: {verdict} "
              f"— {result['reason']}")
        return

    print(f"\n  {'='*58}")
    print(f"  {acc}  [{verdict}]  "
          f"score={score}  n={n}")
    print(f"  {'='*58}")

    series = result.get("series", {})
    title  = series.get(
        "!Series_title", ""
    )[:80]
    print(f"  Title  : {title}")

    summary = series.get(
        "!Series_summary", ""
    )[:200]
    print(f"  Summary: {summary}")

    design = series.get(
        "!Series_overall_design", ""
    )[:200]
    print(f"  Design : {design}")

    print(f"  Flags  : {', '.join(flags)}")

    suppl = series.get(
        "!Series_supplementary_file", ""
    )
    if suppl:
        for f in suppl.split(" "):
            if f.strip():
                print(f"  Suppl  : "
                      f"{f.strip()[-60:]}")

# ============================================================
# MAIN SCAN
# ============================================================

def main():
    print("=" * 65)
    print("PAAD — PANCREATIC ADENOCARCINOMA")
    print("DATASET DISCOVERY SCAN")
    print("OrganismCore Phase 0")
    print("Date: 2026-03-01")
    print("=" * 65)
    print(f"\nScanning {len(CANDIDATES)} candidates...")
    print("Criteria:")
    print("  Human")
    print("  Pancreatic adenocarcinoma")
    print("  Normal/adjacent tissue present")
    print("  RNA-seq or scRNA-seq")
    print("  Adequate sample counts")
    print()

    results     = []
    excellent   = []
    strong      = []
    candidates  = []
    errors      = []

    for i, (acc, note) in enumerate(
        CANDIDATES.items()
    ):
        sys.stdout.write(
            f"\r  Checking {i+1}/"
            f"{len(CANDIDATES)}: {acc}..."
        )
        sys.stdout.flush()

        series_text = fetch_geo_metadata(acc)
        time.sleep(0.3)  # be polite to NCBI

        if "ERROR" in series_text:
            errors.append(acc)
            continue

        sample_text = fetch_sample_metadata(acc)
        time.sleep(0.3)

        result = score_dataset(
            acc, series_text, sample_text, note
        )
        if result:
            results.append(result)
            v = result["verdict"]
            if v == "EXCELLENT":
                excellent.append(result)
            elif v == "STRONG":
                strong.append(result)
            elif v == "CANDIDATE":
                candidates.append(result)

    print("\n")
    print("=" * 65)
    print("SCAN COMPLETE")
    print("=" * 65)

    # Print excellent first
    if excellent:
        print(f"\n{'='*65}")
        print(f"EXCELLENT DATASETS ({len(excellent)})")
        print(f"{'='*65}")
        for r in sorted(
            excellent,
            key=lambda x: x["score"],
            reverse=True
        ):
            print_result(r)

    if strong:
        print(f"\n{'='*65}")
        print(f"STRONG DATASETS ({len(strong)})")
        print(f"{'='*65}")
        for r in sorted(
            strong,
            key=lambda x: x["score"],
            reverse=True
        ):
            print_result(r)

    if candidates:
        print(f"\n{'='*65}")
        print(f"CANDIDATE DATASETS ({len(candidates)})")
        print(f"{'='*65}")
        for r in sorted(
            candidates,
            key=lambda x: x["score"],
            reverse=True
        ):
            print_result(r)

    # Summary table
    print(f"\n{'='*65}")
    print("SUMMARY TABLE")
    print(f"{'='*65}")
    print(f"  {'Accession':<14} {'Verdict':<14} "
          f"{'Score':>6} {'n':>6} "
          f"{'Cancer':>8} {'Normal':>8} "
          f"{'scRNA':>7}")
    print(f"  {'-'*65}")

    show_verdicts = ["EXCELLENT", "STRONG",
                     "CANDIDATE", "WEAK",
                     "NO_NORMAL", "NO_CANCER"]
    for r in sorted(
        results,
        key=lambda x: x.get("score", 0),
        reverse=True
    ):
        if r["verdict"] in show_verdicts:
            print(
                f"  {r['acc']:<14} "
                f"{r['verdict']:<14} "
                f"{r.get('score',0):>6} "
                f"{r.get('n_samples',0):>6} "
                f"{'✓' if r.get('has_cancer') else '✗':>8} "
                f"{'✓' if r.get('has_normal') else '✗':>8} "
                f"{'✓' if r.get('is_scrna') else '✗':>7}"
            )

    if errors:
        print(f"\n  Fetch errors ({len(errors)}): "
              f"{', '.join(errors)}")

    print(f"\n  Total scanned : {len(CANDIDATES)}")
    print(f"  Excellent     : {len(excellent)}")
    print(f"  Strong        : {len(strong)}")
    print(f"  Candidate     : {len(candidates)}")
    print(f"  Errors        : {len(errors)}")

    # Recommendation
    print(f"\n{'='*65}")
    print("RECOMMENDATION")
    print(f"{'='*65}")

    top = (excellent + strong + candidates)
    top = sorted(
        top,
        key=lambda x: (
            x.get("score", 0) * 2 +
            (3 if x.get("has_normal") else 0) +
            (2 if x.get("is_scrna") else 0) +
            (1 if x.get("n_samples", 0) > 20
             else 0)
        ),
        reverse=True
    )

    if top:
        print(f"\n  PRIMARY RECOMMENDATION:")
        r = top[0]
        print(f"    Accession : {r['acc']}")
        print(f"    Verdict   : {r['verdict']}")
        print(f"    Score     : {r['score']}")
        print(f"    n samples : {r['n_samples']}")
        series = r.get("series", {})
        print(f"    Title     : "
              f"{series.get('!Series_title','')[:70]}")

        if len(top) > 1:
            print(f"\n  BACKUP OPTIONS:")
            for r in top[1:4]:
                series = r.get("series", {})
                print(
                    f"    {r['acc']} "
                    f"[{r['verdict']} "
                    f"score={r['score']} "
                    f"n={r['n_samples']}] "
                    f"{series.get('!Series_title','')[:50]}"
                )

    print(f"\n  Next step:")
    print(f"    Run structure check on top candidate")
    print(f"    Then proceed to Phase 1:")
    print(f"    State biological predictions")
    print(f"    before loading any data.")
    print(f"\n=== DISCOVERY SCAN COMPLETE ===")


if __name__ == "__main__":
    main()
