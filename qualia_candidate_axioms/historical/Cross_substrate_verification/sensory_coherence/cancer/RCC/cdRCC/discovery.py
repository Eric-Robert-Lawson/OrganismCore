"""
cdRCC — Collecting Duct Renal Cell Carcinoma
Dataset Discovery Script
Phase 0 of OrganismCore Cancer Analysis Protocol

Scans GEO accessions for:
  - Human collecting duct carcinoma (CDC / cdRCC)
  - Normal kidney tissue — matched preferred
  - RNA-seq preferred; microarray scored lower
  - Adequate sample counts (n>=5 tumor, n>=3 normal)
  - Matched / within-patient paired normals preferred
  - Fresh-frozen preferred; FFPE penalised
  - Internal normal cohort preferred; external reference penalised
  - Platform batch consistency preferred

Also queries GEO full-text search to discover
any accessions not in the seed candidate list.

PRE-DATA PREDICTIONS LOCKED (before any data seen):
  Axis 1 (PC1): normal-to-attractor transition
  Axis 2 (PC2): principal cell identity
               (AQP2 / SCNN1 / AVPR2 programme expected)
  NOT expected on PC2: SLC51B / HSD17B14 / SULT2B1
               (those are intercalated cell — chRCC)
  Depth structure: predicted present
  Tier3 attractor programme: predicted present
  Two-subgroup structure: predicted recoverable
               (GSE83479 found CDC1 / CDC2 by clustering)

Author: Eric Robert Lawson
Framework: OrganismCore
Date: 2026-03-03
Protocol: Phase 0 — Dataset Discovery
"""

import urllib.request
import urllib.parse
import sys
import time
import re

# ============================================================
# CANDIDATE ACCESSIONS
# Four categories:
#   A: CDC / cdRCC tumour vs normal — known
#   B: CDC with comparator cancer types
#   C: CDC vs urothelial (differential diagnosis datasets)
#   D: Additional / search-discovered accessions
# ============================================================

CANDIDATES = {

    # ---- CATEGORY A: CDC tumour vs normal — known ----
    "GSE89122":  "CDC RNA-seq 7 tumour 6 matched normal — Illumina HiSeq 2000",
    "GSE19982":  "CDC microarray 5 tumour 5 normal — Affymetrix U133A",

    # ---- CATEGORY B: CDC with comparator cancer types ----
    "GSE153965": "CDC microarray 6 tumour + 5 ccRCC + 4 normal — Affymetrix HTA2 FFPE",
    "GSE83479":  "CDC microarray 17 tumour + 10 UTUC + 9 ext normal — Illumina HT12",

    # ---- CATEGORY C: CDC vs urothelial / multi-kidney ----
    "GSE15641":  "Normal kidney reference used by GSE83479 — multi-platform",
    "GSE11024":  "Kidney tumour subtypes including CDC — microarray",
    "GSE53757":  "ccRCC tumour vs normal — large cohort for cross-comparison",
    "GSE36895":  "ccRCC tumour vs normal — Affymetrix",

    # ---- CATEGORY D: Candidate search-discovered ----
    # Populated by GEO search below — see main()
    # Manual additions from literature:
    "GSE78993":  "Kidney cancer subtypes panel — CDC possible",
    "GSE72556":  "Renal tumour subtypes — CDC possible",
    "GSE16441":  "Kidney tumour subtypes microarray — CDC possible",
    "GSE31903":  "Kidney RCC subtypes — CDC possible",
    "GSE40435":  "ccRCC and non-ccRCC subtypes",
}

# ============================================================
# SCORING KEYWORDS
# ============================================================

REQUIRED_KEYWORDS = [
    "collecting duct",
    "bellini",
    "cdc",
    "cdcrcc",
    "cd-rcc",
    "collecting duct carcinoma",
    "renal collecting duct",
    "tubular and collecting duct",
]

CANCER_KEYWORDS = [
    "tumor", "tumour", "carcinoma",
    "cancer", "malignant", "neoplasm",
    "adenocarcinoma",
]

NORMAL_KEYWORDS = [
    "normal", "adjacent", "non-tumor",
    "non-tumour", "non-neoplastic",
    "healthy kidney", "normal kidney",
    "paired normal",
]

RNASEQ_KEYWORDS = [
    "rna-seq", "rnaseq", "rna seq",
    "illumina hiseq", "illumina nextseq",
    "high-throughput sequencing",
    "mrna sequencing", "transcriptome sequencing",
    "paired-end", "single-end sequencing",
]

ARRAY_KEYWORDS = [
    "microarray", "affymetrix", "illumina beadchip",
    "agilent", "array", "expression profiling by array",
]

FFPE_KEYWORDS = [
    "ffpe", "formalin-fixed", "paraffin-embedded",
    "formalin fixed",
]

PAIRED_KEYWORDS = [
    "matched", "paired", "same patient",
    "adjacent normal", "matched normal",
    "within-patient",
]

EXTERNAL_NORMAL_KEYWORDS = [
    "external reference", "reference dataset",
    "from gse", "gse15641",
]

EXCLUDE_KEYWORDS = [
    "mouse", "mus musculus", "murine",
    "rat ", "rattus",
    "prostate", "breast", "lung",
    "colon", "colorectal", "bladder only",
    "in vitro only", "cell line only",
]

# ============================================================
# SCORING WEIGHTS
# ============================================================

SCORE_RNASEQ          = +30   # RNA-seq preferred
SCORE_ARRAY           = +10   # microarray accepted but lower
SCORE_FFPE_PENALTY    = -15   # FFPE degrades RNA quality
SCORE_MATCHED_NORMAL  = +25   # within-patient pairing
SCORE_NORMAL_PRESENT  = +15   # any normal tissue
SCORE_EXT_NORMAL_PEN  = -10   # external reference normals
SCORE_PER_TUMOR       =  +2   # per tumour sample (capped)
SCORE_PER_NORMAL      =  +2   # per normal sample (capped)
SCORE_MIN_TUMOR_5     = +10   # >= 5 tumour bonus
SCORE_MIN_NORMAL_3    = +10   # >= 3 normal bonus
SCORE_CDC_ONLY        = +10   # CDC-only dataset (no contaminant subtypes)
SCORE_COMPARATOR      =  +5   # has comparator subtype (useful for PC2)

MIN_TUMOR  = 3   # hard minimum tumour samples
MIN_NORMAL = 2   # hard minimum normal samples

# ============================================================
# GEO URLS
# ============================================================

GEO_SOFT_BASE  = "https://ftp.ncbi.nlm.nih.gov/geo/series/"
GEO_QUERY_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# ============================================================
# FETCH
# ============================================================

def fetch(url, timeout=25):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(
            req, timeout=timeout
        ) as r:
            raw = r.read()
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError:
                return raw.decode("latin-1")
    except Exception as e:
        return f"ERROR: {e}"

# ============================================================
# GEO SOFT URL BUILDER
# ============================================================

def soft_url(acc):
    """
    Build the SOFT family file URL for a GEO series.
    GSE89122 → geo/series/GSE89nnn/GSE89122/soft/
    """
    prefix = acc[:len(acc) - 3] + "nnn"
    return (
        f"{GEO_SOFT_BASE}{prefix}/{acc}/soft/"
        f"{acc}_family.soft.gz"
    )

def miniml_url(acc):
    """
    MINiML format — smaller than SOFT, faster to parse.
    """
    prefix = acc[:len(acc) - 3] + "nnn"
    return (
        f"{GEO_SOFT_BASE}{prefix}/{acc}/miniml/"
        f"{acc}_family.xml.tgz"
    )

def soft_text_url(acc):
    """
    SOFT text (uncompressed) — available for some series.
    """
    prefix = acc[:len(acc) - 3] + "nnn"
    return (
        f"https://www.ncbi.nlm.nih.gov/geo/query/"
        f"acc.cgi?acc={acc}&targ=self&form=text&view=full"
    )

# ============================================================
# PARSE SERIES METADATA
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
            "!Series_type",
        ]:
            if line.startswith(key):
                existing = data.get(key, "")
                addition = line.split("=", 1)[1].strip()
                data[key] = (existing + " " + addition).strip()
    return data

# ============================================================
# PARSE SAMPLE ANNOTATIONS
# ============================================================

def parse_samples(text):
    samples, current = [], {}
    for line in text.split("\n"):
        if line.startswith("^SAMPLE"):
            if current:
                samples.append(current)
            current = {"gsm": line.split("=")[1].strip()}
        elif line.startswith("!Sample_title"):
            current["title"] = line.split("=", 1)[1].strip()
        elif line.startswith("!Sample_source_name_ch1"):
            current["source"] = line.split("=", 1)[1].strip()
        elif line.startswith("!Sample_characteristics_ch1"):
            val = line.split("=", 1)[1].strip()
            if ":" in val:
                k, v = val.split(":", 1)
                current[
                    k.strip().lower().replace(" ", "_")
                ] = v.strip()
        elif line.startswith("!Sample_library_strategy"):
            current["library_strategy"] = \
                line.split("=", 1)[1].strip()
        elif line.startswith("!Sample_instrument_model"):
            current["instrument"] = \
                line.split("=", 1)[1].strip()
    if current:
        samples.append(current)
    return samples

# ============================================================
# COUNT TUMOUR / NORMAL SAMPLES
# ============================================================

def count_sample_types(samples, series_combined):
    n_tumor  = 0
    n_normal = 0
    matched_pairs = 0

    for s in samples:
        fields = " ".join(str(v) for v in s.values()).lower()

        is_tumor  = any(kw in fields for kw in CANCER_KEYWORDS)
        is_normal = any(kw in fields for kw in NORMAL_KEYWORDS)

        # Collecting duct specific — count CDC tumours
        is_cdc = any(kw in fields for kw in REQUIRED_KEYWORDS)

        if is_cdc and is_tumor:
            n_tumor += 1
        elif is_normal and not is_tumor:
            n_normal += 1

        if any(kw in fields for kw in PAIRED_KEYWORDS):
            matched_pairs += 1

    # Fallback: if CDC keywords missing from samples
    # but series mentions it, use total sample heuristic
    if n_tumor == 0 and any(
        kw in series_combined for kw in REQUIRED_KEYWORDS
    ):
        for s in samples:
            fields = " ".join(
                str(v) for v in s.values()
            ).lower()
            is_normal = any(
                kw in fields for kw in NORMAL_KEYWORDS
            )
            if not is_normal:
                n_tumor += 1
            else:
                n_normal += 1

    return n_tumor, n_normal, matched_pairs

# ============================================================
# DETECT PLATFORM
# ============================================================

def detect_platform(combined):
    if any(kw in combined for kw in RNASEQ_KEYWORDS):
        return "RNA-seq"
    if any(kw in combined for kw in ARRAY_KEYWORDS):
        return "Array"
    return "Unknown"

# ============================================================
# SCORE DATASET
# ============================================================

def score_dataset(acc, series_text, sample_text, note):
    if "ERROR" in series_text[:50]:
        return {
            "acc":      acc,
            "note":     note,
            "verdict":  "FETCH_ERROR",
            "reason":   series_text[:80],
            "score":    -99,
            "details":  {},
        }

    series   = parse_series(series_text)
    samples  = parse_samples(sample_text)
    full_ser = " ".join(series.values()).lower()
    full_sam = sample_text.lower()
    combined = full_ser + " " + full_sam

    details = {}

    # ---- Hard excludes ----
    for kw in EXCLUDE_KEYWORDS:
        if kw in combined:
            # Only exclude if CDC keyword also absent
            if not any(
                kw2 in combined for kw2 in REQUIRED_KEYWORDS
            ):
                return {
                    "acc":     acc,
                    "note":    note,
                    "verdict": "EXCLUDE",
                    "reason":  f"excluded keyword: '{kw}', no CDC keyword found",
                    "score":   -1,
                    "details": {},
                }

    # ---- Human check ----
    organism = series.get("!Series_organism", "").lower()
    if organism and "homo sapiens" not in organism:
        return {
            "acc":     acc,
            "note":    note,
            "verdict": "NOT HUMAN",
            "reason":  f"organism: {organism}",
            "score":   0,
            "details": {},
        }

    # ---- CDC relevance check ----
    has_cdc = any(kw in combined for kw in REQUIRED_KEYWORDS)
    if not has_cdc:
        # May still be useful as comparator/normal reference
        has_kidney = "kidney" in combined or "renal" in combined
        if not has_kidney:
            return {
                "acc":     acc,
                "note":    note,
                "verdict": "NOT RELEVANT",
                "reason":  "no CDC keyword, no kidney keyword",
                "score":   0,
                "details": {},
            }
        details["role"] = "COMPARATOR_ONLY"
    else:
        details["role"] = "CDC_PRIMARY"

    # ---- Platform ----
    platform = detect_platform(combined)
    details["platform"] = platform

    score = 0
    reasons = []

    if platform == "RNA-seq":
        score += SCORE_RNASEQ
        reasons.append(f"+{SCORE_RNASEQ} RNA-seq")
    elif platform == "Array":
        score += SCORE_ARRAY
        reasons.append(f"+{SCORE_ARRAY} Array")
    else:
        reasons.append("+0 platform unknown")

    # ---- FFPE penalty ----
    is_ffpe = any(kw in combined for kw in FFPE_KEYWORDS)
    details["ffpe"] = is_ffpe
    if is_ffpe:
        score += SCORE_FFPE_PENALTY
        reasons.append(f"{SCORE_FFPE_PENALTY} FFPE")

    # ---- Normal tissue ----
    has_normal = any(kw in combined for kw in NORMAL_KEYWORDS)
    details["has_normal"] = has_normal
    if has_normal:
        score += SCORE_NORMAL_PRESENT
        reasons.append(f"+{SCORE_NORMAL_PRESENT} normal present")

    # ---- Matched / paired normals ----
    is_matched = any(kw in combined for kw in PAIRED_KEYWORDS)
    details["matched"] = is_matched
    if is_matched:
        score += SCORE_MATCHED_NORMAL
        reasons.append(f"+{SCORE_MATCHED_NORMAL} matched normals")

    # ---- External normal penalty ----
    is_ext_normal = any(
        kw in combined for kw in EXTERNAL_NORMAL_KEYWORDS
    )
    details["external_normal"] = is_ext_normal
    if is_ext_normal and not is_matched:
        score += SCORE_EXT_NORMAL_PEN
        reasons.append(f"{SCORE_EXT_NORMAL_PEN} external normals")

    # ---- Sample counts ----
    n_tumor, n_normal, n_matched = count_sample_types(
        samples, combined
    )
    details["n_tumor"]   = n_tumor
    details["n_normal"]  = n_normal
    details["n_matched"] = n_matched
    details["n_samples"] = len(samples)

    # Hard minimum check
    if details["role"] == "CDC_PRIMARY":
        if n_tumor < MIN_TUMOR:
            # Don't hard-fail — sample parsing may have missed
            # Record warning but continue scoring
            reasons.append(
                f"WARN: n_tumor={n_tumor} < {MIN_TUMOR}"
            )
        if n_normal < MIN_NORMAL and not has_normal:
            reasons.append(
                f"WARN: n_normal={n_normal} < {MIN_NORMAL}"
            )

    # Per-sample scores (capped at 20 each)
    tumor_pts  = min(n_tumor  * SCORE_PER_TUMOR,  20)
    normal_pts = min(n_normal * SCORE_PER_NORMAL, 20)
    score += tumor_pts + normal_pts
    reasons.append(f"+{tumor_pts} ({n_tumor} tumour samples)")
    reasons.append(f"+{normal_pts} ({n_normal} normal samples)")

    # Bonus for crossing minimum thresholds
    if n_tumor >= 5:
        score += SCORE_MIN_TUMOR_5
        reasons.append(f"+{SCORE_MIN_TUMOR_5} n_tumor>=5 bonus")
    if n_normal >= 3:
        score += SCORE_MIN_NORMAL_3
        reasons.append(f"+{SCORE_MIN_NORMAL_3} n_normal>=3 bonus")

    # ---- CDC-only vs multi-subtype ----
    # Multi-subtype datasets have comparator value but are not
    # pure CDC — slight bonus for having a comparator
    series_type_text = series.get("!Series_overall_design", "")
    has_comparator = any(
        kw in series_type_text.lower()
        for kw in ["ccrcc", "ccRCC", "urothelial", "utuc",
                   "papillary", "chromophobe", "rcc"]
    )
    if has_comparator:
        score += SCORE_COMPARATOR
        reasons.append(f"+{SCORE_COMPARATOR} comparator subtype present")
    elif details["role"] == "CDC_PRIMARY":
        score += SCORE_CDC_ONLY
        reasons.append(f"+{SCORE_CDC_ONLY} CDC-only dataset")

    # ---- Final verdict ----
    if details["role"] == "COMPARATOR_ONLY":
        verdict = "COMPARATOR"
    elif score >= 60:
        verdict = "PASS"
    elif score >= 35:
        verdict = "MARGINAL"
    elif score >= 10:
        verdict = "WEAK"
    else:
        verdict = "FAIL"

    details["reasons"] = reasons
    details["title"]   = series.get("!Series_title", "")[:80]
    details["summary"] = series.get("!Series_summary", "")[:120]

    return {
        "acc":     acc,
        "note":    note,
        "verdict": verdict,
        "score":   score,
        "details": details,
    }

# ============================================================
# GEO FULL-TEXT SEARCH
# Discovers accessions not in the seed list
# ============================================================

def search_geo_cdc(max_results=40):
    """
    Query NCBI eutils for GEO series matching
    collecting duct carcinoma.
    Returns list of GSE accession strings.
    """
    query = urllib.parse.quote(
        'collecting duct carcinoma[Title/Abstract] '
        'AND "expression profiling"[DataSet Type] '
        'AND "Homo sapiens"[Organism]'
    )
    url = (
        f"{GEO_QUERY_BASE}esearch.fcgi?"
        f"db=gds&term={query}"
        f"&retmax={max_results}&retmode=text"
    )
    text = fetch(url)
    if "ERROR" in text:
        print(f"  GEO search error: {text[:80]}")
        return []

    ids = re.findall(r"<Id>(\d+)</Id>", text)
    accs = []
    for gds_id in ids[:max_results]:
        # Convert GDS ID to GSE accession via esummary
        sum_url = (
            f"{GEO_QUERY_BASE}esummary.fcgi?"
            f"db=gds&id={gds_id}&retmode=text"
        )
        summary = fetch(sum_url)
        # Extract GSE accession from summary
        gse_match = re.search(r"GSE\d+", summary)
        if gse_match:
            gse = gse_match.group(0)
            if gse not in CANDIDATES:
                accs.append(gse)
        time.sleep(0.35)   # NCBI rate limit
    return accs

# ============================================================
# PRINT RESULT
# ============================================================

def print_result(result):
    acc     = result["acc"]
    verdict = result["verdict"]
    score   = result.get("score", 0)
    note    = result.get("note", "")
    details = result.get("details", {})

    # Verdict colour codes (terminal)
    colour = {
        "PASS":        "\033[92m",   # green
        "MARGINAL":    "\033[93m",   # yellow
        "WEAK":        "\033[33m",   # orange
        "COMPARATOR":  "\033[96m",   # cyan
        "FAIL":        "\033[91m",   # red
        "EXCLUDE":     "\033[90m",   # grey
        "NOT HUMAN":   "\033[90m",
        "NOT RELEVANT":"\033[90m",
        "FETCH_ERROR": "\033[91m",
    }.get(verdict, "")
    reset = "\033[0m"

    print(f"\n{'='*60}")
    print(f"  {colour}{verdict}{reset}  [{score:+d}]  {acc}")
    print(f"  {note}")

    if details.get("title"):
        print(f"  Title:    {details['title']}")
    if details.get("summary"):
        print(f"  Summary:  {details['summary']}")

    plat    = details.get("platform", "?")
    ffpe    = "FFPE" if details.get("ffpe") else "fresh/unknown"
    matched = "MATCHED" if details.get("matched") else "unmatched"
    ext_n   = "EXT-NORM" if details.get("external_normal") else ""
    n_t     = details.get("n_tumor",  "?")
    n_n     = details.get("n_normal", "?")
    n_s     = details.get("n_samples","?")
    role    = details.get("role", "")

    print(
        f"  Platform: {plat}  |  {ffpe}  |  {matched}  "
        f"{ext_n}"
    )
    print(
        f"  Samples:  {n_s} total  "
        f"[tumour={n_t}, normal={n_n}]  "
        f"role={role}"
    )

    if details.get("reasons"):
        print("  Scoring:")
        for r in details["reasons"]:
            print(f"    {r}")

    if result.get("reason"):
        print(f"  Reason:  {result['reason']}")

# ============================================================
# PRINT FINAL RANKED SUMMARY
# ============================================================

def print_summary(results):
    print("\n")
    print("=" * 60)
    print("  RANKED SUMMARY — cdRCC DATASET DISCOVERY")
    print("=" * 60)

    passed     = [r for r in results if r["verdict"] == "PASS"]
    marginal   = [r for r in results if r["verdict"] == "MARGINAL"]
    comparator = [r for r in results if r["verdict"] == "COMPARATOR"]
    weak       = [r for r in results if r["verdict"] == "WEAK"]
    failed     = [r for r in results
                  if r["verdict"] not in
                  ("PASS","MARGINAL","COMPARATOR","WEAK")]

    for label, group in [
        ("PASS",       passed),
        ("MARGINAL",   marginal),
        ("COMPARATOR", comparator),
        ("WEAK",       weak),
        ("OTHER",      failed),
    ]:
        if not group:
            continue
        sorted_g = sorted(
            group, key=lambda x: x.get("score", 0), reverse=True
        )
        print(f"\n  --- {label} ---")
        for r in sorted_g:
            d = r.get("details", {})
            print(
                f"    {r['acc']:12s}  score={r['score']:+4d}  "
                f"T={d.get('n_tumor','?'):>3}  "
                f"N={d.get('n_normal','?'):>3}  "
                f"{d.get('platform','?'):8s}  "
                f"{'MATCHED' if d.get('matched') else '       '}  "
                f"{'FFPE' if d.get('ffpe') else '    '}  "
                f"{r['note'][:50]}"
            )

    print(f"\n  Total evaluated: {len(results)}")
    print(f"  PASS:       {len(passed)}")
    print(f"  MARGINAL:   {len(marginal)}")
    print(f"  COMPARATOR: {len(comparator)}")
    print(f"  WEAK:       {len(weak)}")
    print(f"  Other:      {len(failed)}")

    # Recommendation
    print("\n  RECOMMENDATION:")
    if passed:
        best = sorted(
            passed, key=lambda x: x["score"], reverse=True
        )[0]
        print(f"    PRIMARY:    {best['acc']}  (score={best['score']:+d})")
        if len(passed) > 1:
            second = sorted(
                passed, key=lambda x: x["score"], reverse=True
            )[1]
            print(
                f"    SECONDARY:  {second['acc']}  "
                f"(score={second['score']:+d})"
            )
    elif marginal:
        best = sorted(
            marginal, key=lambda x: x["score"], reverse=True
        )[0]
        print(
            f"    BEST MARGINAL: {best['acc']}  "
            f"(score={best['score']:+d})"
        )
        print(
            "    WARNING: No PASS-grade dataset found."
            " Proceed with caution."
        )
    else:
        print(
            "    NO SUITABLE DATASET FOUND."
            " Manual review required."
        )

    if comparator:
        print("    COMPARATORS available for PC2 cross-validation:")
        for r in comparator:
            print(f"      {r['acc']}  {r['note'][:60]}")

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  cdRCC — COLLECTING DUCT CARCINOMA")
    print("  OrganismCore Dataset Discovery — Phase 0")
    print("  Date: 2026-03-03")
    print("=" * 60)

    # Step 1 — GEO full-text search for undiscovered accessions
    print("\n[1] Querying GEO for additional cdRCC datasets...")
    discovered = search_geo_cdc(max_results=40)
    if discovered:
        print(f"  Discovered {len(discovered)} additional accessions:")
        for acc in discovered:
            print(f"    {acc}")
            CANDIDATES[acc] = "GEO search discovery — CDC query"
    else:
        print("  No additional accessions discovered (or search error)")

    # Step 2 — Score all candidates
    print(f"\n[2] Scoring {len(CANDIDATES)} candidate datasets...")
    results = []

    for acc, note in CANDIDATES.items():
        print(f"\n  Fetching {acc}...", end=" ", flush=True)

        # Fetch series metadata (SOFT text format)
        series_url = soft_text_url(acc)
        series_text = fetch(series_url)
        time.sleep(0.4)   # NCBI rate limit

        if "ERROR" in str(series_text)[:30]:
            print("FETCH ERROR")
            results.append({
                "acc":     acc,
                "note":    note,
                "verdict": "FETCH_ERROR",
                "score":   -99,
                "details": {},
                "reason":  series_text[:80],
            })
            continue

        print(f"OK ({len(series_text)} chars)")

        result = score_dataset(acc, series_text, series_text, note)
        results.append(result)
        print_result(result)

        time.sleep(0.4)

    # Step 3 — Ranked summary and recommendation
    print_summary(results)

    # Step 4 — Write results to file
    out_path = "./cdRCC_discovery_results.txt"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            # Redirect stdout to file for full log
            import io
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()

            print_summary(results)
            for r in sorted(
                results,
                key=lambda x: x.get("score", -99),
                reverse=True,
            ):
                print_result(r)

            sys.stdout = old_stdout
            f.write(buffer.getvalue())

        print(f"\n  Results written to: {out_path}")
    except Exception as e:
        print(f"\n  Could not write results file: {e}")

    print("\n[PHASE 0 COMPLETE]")
    print("Review output above and select dataset before Phase 1.")
    print("Do NOT load biology or form predictions until")
    print("dataset is selected and downloaded.")


if __name__ == "__main__":
    main()
