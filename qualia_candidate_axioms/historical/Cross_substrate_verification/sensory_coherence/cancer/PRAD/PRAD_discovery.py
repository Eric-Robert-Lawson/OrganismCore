"""
PRAD — Prostate Adenocarcinoma
Dataset Discovery Script
Phase 0 of OrganismCore Cancer Analysis Protocol

Scans GEO accessions for:
  - Human prostate adenocarcinoma
  - Normal prostate tissue / adjacent normal
  - RNA-seq or microarray
  - Adequate sample counts (n>=5 tumor, n>=3 normal)
  - Primary PRAD preferred (untreated / AR positive)
  - Gleason score annotation preferred
  - ERG fusion status preferred

PRE-DATA PREDICTIONS LOCKED:
  Switch: NKX3-1/FOXA1/AR suppressed
  FA:     ERG/MKI67/EZH2 elevated
  EZH2:   ELEVATED — gain lock (3rd solid cancer)
  Drug:   AR pathway + EZH2 inhibitor

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
#   A: Primary PRAD tumor vs normal
#   B: PRAD with Gleason/grade annotation
#   C: PRAD with ERG fusion status
#   D: CRPC / treatment resistant
# ============================================================

CANDIDATES = {

    # ---- CATEGORY A: Primary PRAD tumor vs normal ----
    "GSE6919":   "PRAD tumor vs normal — large cohort",
    "GSE21032":  "PRAD Memorial Sloan Kettering",
    "GSE35988":  "PRAD tumor vs adjacent normal",
    "GSE46602":  "PRAD tumor vs normal microarray",
    "GSE55945":  "PRAD tumor vs normal",
    "GSE62667":  "PRAD tumor vs adjacent normal",
    "GSE70768":  "PRAD tumor vs normal RNA-seq",
    "GSE76260":  "PRAD tumor vs normal",
    "GSE104749": "PRAD tumor vs normal",
    "GSE134051": "PRAD tumor vs adjacent normal",
    "GSE141551": "PRAD tumor vs normal RNA-seq",

    # ---- CATEGORY B: Gleason / grade annotated ----
    "GSE17951":  "PRAD Gleason grade annotated",
    "GSE25136":  "PRAD Gleason score annotated",
    "GSE32571":  "PRAD Gleason annotated microarray",
    "GSE40272":  "PRAD Gleason score RNA-seq",
    "GSE54460":  "PRAD Gleason grade survival",
    "GSE79021":  "PRAD Gleason annotated",
    "GSE94767":  "PRAD Gleason annotated",
    "GSE116918": "PRAD Gleason + ERG annotated",

    # ---- CATEGORY C: ERG fusion annotated ----
    "GSE29079":  "PRAD ERG fusion status",
    "GSE30521":  "PRAD ERG/ETS fusion annotated",
    "GSE37199":  "PRAD ERG status annotated",
    "GSE45016":  "PRAD ERG fusion annotated",

    # ---- CATEGORY D: Large cohorts / TCGA derived ----
    "GSE21034":  "PRAD MSKCC large cohort",
    "GSE32894":  "PRAD large cohort microarray",
    "GSE51057":  "PRAD large cohort",
    "GSE84042":  "PRAD large cohort RNA-seq",
    "GSE102349": "PRAD large cohort",
    "GSE120052": "PRAD tumor vs normal large",
    "GSE153537": "PRAD RNA-seq tumor vs normal",
    "GSE169038": "PRAD RNA-seq candidate",
    "GSE193337": "PRAD tumor vs normal 2022",
    "GSE223648": "PRAD tumor vs normal 2023",
}

# ============================================================
# RELEVANCE KEYWORDS
# ============================================================

REQUIRED_KEYWORDS = [
    "prostat",
]

CANCER_KEYWORDS = [
    "adenocarcinoma", "prad", "prostate cancer",
    "prostate tumor", "prostate carcinoma",
    "prostate neoplasm",
]

NORMAL_KEYWORDS = [
    "normal", "adjacent", "benign",
    "non-tumor", "nontumor", "non-neoplastic",
    "healthy", "control",
]

GRADE_KEYWORDS = [
    "gleason", "grade", "stage",
    "psa", "biochemical",
]

ERG_KEYWORDS = [
    "erg", "tmprss2", "ets fusion",
    "fusion", "rearrangement",
]

SCRNA_KEYWORDS = [
    "single cell", "single-cell", "scrna",
    "10x", "droplet",
]

BULK_KEYWORDS = [
    "rna-seq", "rnaseq", "microarray",
    "expression profiling", "transcriptom",
    "affymetrix", "agilent",
]

EXCLUDE_KEYWORDS = [
    "mouse", "mus musculus", "murine",
    "rat ", "rattus",
    "neuroendocrine only",
    "bladder", "kidney", "colon",
]

# ============================================================
# FETCH
# ============================================================

def fetch(url, timeout=20):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(
            req, timeout=timeout
        ) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        return f"ERROR: {e}"

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
                addition = line.split(
                    "=", 1
                )[1].strip()
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

# ============================================================
# SCORE
# ============================================================

def score_dataset(acc, series_text,
                  sample_text, note):
    if "ERROR" in series_text:
        return None

    series   = parse_series(series_text)
    samples  = parse_samples(sample_text)
    full_ser = " ".join(series.values()).lower()
    full_sam = sample_text.lower()
    combined = full_ser + " " + full_sam

    # Hard excludes
    for kw in EXCLUDE_KEYWORDS:
        if kw in combined:
            return {
                "acc":     acc,
                "note":    note,
                "verdict": "EXCLUDE",
                "reason":  f"excluded: {kw}",
                "score":   -1,
                "series":  series,
                "n_samples": len(samples),
            }

    # Must be prostate
    if not any(kw in combined
               for kw in REQUIRED_KEYWORDS):
        return {
            "acc":     acc,
            "note":    note,
            "verdict": "NOT PROSTATE",
            "reason":  "prostat not found",
            "score":   0,
            "series":  series,
            "n_samples": len(samples),
        }

    # Must be human
    organism = series.get(
        "!Series_organism", ""
    ).lower()
    is_human = (
        "homo sapiens" in organism
        or "human" in combined
    )
    if not is_human:
        return {
            "acc":     acc,
            "note":    note,
            "verdict": "NOT HUMAN",
            "reason":  f"organism: {organism}",
            "score":   0,
            "series":  series,
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

    # Grade annotation
    has_grade = any(kw in combined
                    for kw in GRADE_KEYWORDS)
    if has_grade:
        score += 2
        flags.append("has_grade")

    # ERG annotation
    has_erg = any(kw in combined
                  for kw in ERG_KEYWORDS)
    if has_erg:
        score += 1
        flags.append("has_erg")

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
    n_str   = series.get(
        "!Series_sample_count", "0"
    )
    n_total = 0
    try:
        n_total = int(n_str.strip())
    except Exception:
        pass

    if n_total >= 100:
        score += 4
        flags.append(f"n={n_total}")
    elif n_total >= 50:
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
    if any(ext in suppl for ext in [
        ".txt.gz", ".csv.gz", ".h5",
        "matrix", "count", "cpm",
        "tpm", "normalized",
    ]):
        score += 2
        flags.append("has_suppl_matrix")

    # Classify verdict
    if score >= 12:
        verdict = "EXCELLENT"
    elif score >= 9:
        verdict = "STRONG"
    elif score >= 6:
        verdict = "CANDIDATE"
    elif score >= 3:
        verdict = "WEAK"
    else:
        verdict = "POOR"

    if not has_cancer:
        verdict = "NO_CANCER"
    if not has_normal and score < 7:
        verdict = "NO_NORMAL"

    return {
        "acc":        acc,
        "note":       note,
        "verdict":    verdict,
        "score":      score,
        "flags":      flags,
        "series":     series,
        "n_samples":  n_total,
        "has_cancer": has_cancer,
        "has_normal": has_normal,
        "has_grade":  has_grade,
        "has_erg":    has_erg,
        "is_scrna":   is_scrna,
        "is_bulk":    is_bulk,
    }

# ============================================================
# PRINT
# ============================================================

def print_result(result):
    if result is None:
        return

    verdict = result["verdict"]
    acc     = result["acc"]
    score   = result.get("score", 0)
    flags   = result.get("flags", [])
    n       = result.get("n_samples", 0)

    if verdict in [
        "NOT PROSTATE", "NOT HUMAN",
        "POOR", "NO_CANCER",
    ]:
        print(f"  {acc}: {verdict}")
        return

    if verdict == "EXCLUDE":
        print(
            f"  {acc}: {verdict} "
            f"— {result['reason']}"
        )
        return

    print(f"\n  {'='*58}")
    print(
        f"  {acc}  [{verdict}]  "
        f"score={score}  n={n}"
    )
    print(f"  {'='*58}")

    series  = result.get("series", {})
    title   = series.get(
        "!Series_title", ""
    )[:80]
    print(f"  Title  : {title}")

    summary = series.get(
        "!Series_summary", ""
    )[:200]
    print(f"  Summary: {summary}")

    design  = series.get(
        "!Series_overall_design", ""
    )[:200]
    print(f"  Design : {design}")

    print(f"  Flags  : {', '.join(flags)}")

    suppl   = series.get(
        "!Series_supplementary_file", ""
    )
    if suppl:
        for f in suppl.split(" "):
            if f.strip():
                print(
                    f"  Suppl  : "
                    f"{f.strip()[-60:]}"
                )

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 65)
    print("PRAD — PROSTATE ADENOCARCINOMA")
    print("DATASET DISCOVERY SCAN")
    print("OrganismCore Phase 0")
    print("Date: 2026-03-01")
    print("=" * 65)
    print(f"\nScanning {len(CANDIDATES)} "
          f"candidates...")
    print("Criteria:")
    print("  Human")
    print("  Prostate adenocarcinoma")
    print("  Normal/adjacent tissue present")
    print("  RNA-seq or microarray")
    print("  Adequate sample counts")
    print("  Gleason score preferred")
    print("  ERG fusion status preferred")
    print()

    results    = []
    excellent  = []
    strong     = []
    candidates = []
    errors     = []

    for i, (acc, note) in enumerate(
        CANDIDATES.items()
    ):
        sys.stdout.write(
            f"\r  Checking {i+1}/"
            f"{len(CANDIDATES)}: {acc}..."
        )
        sys.stdout.flush()

        series_url = (
            "https://www.ncbi.nlm.nih.gov/geo/"
            f"query/acc.cgi?acc={acc}"
            "&targ=self&form=text&view=quick"
        )
        sample_url = (
            "https://www.ncbi.nlm.nih.gov/geo/"
            f"query/acc.cgi?acc={acc}"
            "&targ=gsm&form=text&view=quick"
        )

        series_text = fetch(series_url)
        time.sleep(0.3)

        if "ERROR" in series_text:
            errors.append(acc)
            continue

        sample_text = fetch(sample_url)
        time.sleep(0.3)

        result = score_dataset(
            acc, series_text,
            sample_text, note
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

    if excellent:
        print(f"\n{'='*65}")
        print(
            f"EXCELLENT DATASETS "
            f"({len(excellent)})"
        )
        print(f"{'='*65}")
        for r in sorted(
            excellent,
            key=lambda x: x["score"],
            reverse=True,
        ):
            print_result(r)

    if strong:
        print(f"\n{'='*65}")
        print(f"STRONG DATASETS ({len(strong)})")
        print(f"{'='*65}")
        for r in sorted(
            strong,
            key=lambda x: x["score"],
            reverse=True,
        ):
            print_result(r)

    if candidates:
        print(f"\n{'='*65}")
        print(
            f"CANDIDATE DATASETS "
            f"({len(candidates)})"
        )
        print(f"{'='*65}")
        for r in sorted(
            candidates,
            key=lambda x: x["score"],
            reverse=True,
        ):
            print_result(r)

    # Summary table
    print(f"\n{'='*65}")
    print("SUMMARY TABLE")
    print(f"{'='*65}")
    print(
        f"  {'Accession':<14} {'Verdict':<14} "
        f"{'Score':>6} {'n':>6} "
        f"{'Cancer':>8} {'Normal':>8} "
        f"{'Grade':>7} {'ERG':>5}"
    )
    print(f"  {'-'*68}")

    show_verdicts = [
        "EXCELLENT", "STRONG", "CANDIDATE",
        "WEAK", "NO_NORMAL",
    ]
    for r in sorted(
        results,
        key=lambda x: x.get("score", 0),
        reverse=True,
    ):
        if r["verdict"] in show_verdicts:
            print(
                f"  {r['acc']:<14} "
                f"{r['verdict']:<14} "
                f"{r.get('score',0):>6} "
                f"{r.get('n_samples',0):>6} "
                f"{'✓' if r.get('has_cancer') else '✗':>8} "
                f"{'✓' if r.get('has_normal') else '✗':>8} "
                f"{'✓' if r.get('has_grade') else '✗':>7} "
                f"{'✓' if r.get('has_erg') else '✗':>5}"
            )

    if errors:
        print(
            f"\n  Fetch errors ({len(errors)}): "
            f"{', '.join(errors)}"
        )

    print(f"\n  Total scanned  : {len(CANDIDATES)}")
    print(f"  Excellent      : {len(excellent)}")
    print(f"  Strong         : {len(strong)}")
    print(f"  Candidate      : {len(candidates)}")
    print(f"  Errors         : {len(errors)}")

    # Recommendation
    print(f"\n{'='*65}")
    print("RECOMMENDATION")
    print(f"{'='*65}")

    top = excellent + strong + candidates
    top = sorted(
        top,
        key=lambda x: (
            x.get("score", 0) * 2
            + (3 if x.get("has_normal") else 0)
            + (2 if x.get("has_grade") else 0)
            + (1 if x.get("has_erg") else 0)
            + (1 if x.get(
                "n_samples", 0
            ) > 50 else 0)
        ),
        reverse=True,
    )

    if top:
        print(f"\n  PRIMARY RECOMMENDATION:")
        r = top[0]
        print(f"    Accession : {r['acc']}")
        print(f"    Verdict   : {r['verdict']}")
        print(f"    Score     : {r['score']}")
        print(f"    n samples : {r['n_samples']}")
        print(
            f"    Grade     : "
            f"{'YES' if r.get('has_grade') else 'NO'}"
        )
        print(
            f"    ERG       : "
            f"{'YES' if r.get('has_erg') else 'NO'}"
        )
        series = r.get("series", {})
        print(
            f"    Title     : "
            f"{series.get('!Series_title','')[:65]}"
        )

        if len(top) > 1:
            print(f"\n  BACKUP OPTIONS:")
            for r in top[1:5]:
                series = r.get("series", {})
                print(
                    f"    {r['acc']} "
                    f"[{r['verdict']} "
                    f"score={r['score']} "
                    f"n={r['n_samples']} "
                    f"grade={'Y' if r.get('has_grade') else 'N'} "
                    f"erg={'Y' if r.get('has_erg') else 'N'}] "
                    f"{series.get('!Series_title','')[:45]}"
                )

    print(f"\n  Next step:")
    print(f"    Manual review of top 5 results")
    print(f"    (lesson from PAAD: always read")
    print(f"    summaries before proceeding)")
    print(f"    Then structure check on winner.")
    print(f"    Then Phase 1 predictions locked.")
    print(
        f"\n=== PRAD DISCOVERY SCAN COMPLETE ==="
    )


if __name__ == "__main__":
    main()
