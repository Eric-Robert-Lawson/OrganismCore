"""
chRCC Data Builder v2
OrganismCore | Document 96-build-v2 | 2026-03-02
Author: Eric Robert Lawson

PATCH from v1:
  GSE95425 metadata is anatomical zone only:
    "sampling depth: cortex"
    "sampling depth: cortex/medulla"
    "sampling depth: medulla"
  These are NOT cell-type labels.
  
  Reclassification:
    cortex       → normal_cortex
                   (PT-enriched, glomeruli)
    cortex/medulla→ normal_corticomedullary
    medulla      → normal_medulla
                   (collecting duct-enriched,
                    loop of Henle, IC cells)

  Biological rationale:
    Intercalated cells reside in the collecting
    duct = medullary zone.
    Medullary samples are the closest available
    proxy for the intercalated cell normal pole.
    Cortex samples are the proximal tubule proxy.
    This is bulk tissue, not purified cells —
    all samples remain in the normal pole set.

  Script 1 impact:
    normal_medulla samples will anchor the
    intercalated cell pole more specifically.
    normal_cortex samples anchor the proximal
    tubule / glomerular pole.
    The depth score remains valid — ALL 53
    normal samples anchor the normal pole
    against 15 chRCC tumours.

  SCIENTIFIC NOTE ON GSE95425:
    The paper (Lindgren et al. 2017, Nat Commun)
    describes multi-region sampling of the same
    kidney at different cortex/medulla depths
    to study intratumour heterogeneity in RCC.
    The NORMAL samples are the adjacent normal
    tissue controls from the same patients.
    n=53 normal samples from 6 patients (R099,
    R116, R127, R134, R164, + 1 more).
    These are all-normal-tissue controls —
    appropriate as the normal pole reference.

NO OTHER CHANGES from v1.
All file paths, gene sets, and output format
are identical. Script 1 runs unchanged.
"""

import os, sys, gzip, ftplib, re
import urllib.request, urllib.error
import collections
import numpy as np
import pandas as pd
from scipy.stats import rankdata

BASE_DIR  = "./chrcc_false_attractor/"
CACHE_DIR = os.path.join(BASE_DIR, "geo_cache/")
REPORT    = os.path.join(BASE_DIR,
                          "build_v2_report.txt")
OUT_EXPR  = os.path.join(BASE_DIR,
                          "TCGA_KICH_HiSeqV2.gz")
OUT_CLIN  = os.path.join(BASE_DIR,
                          "KICH_clinicalMatrix.tsv")
OUT_SURV  = os.path.join(BASE_DIR,
                          "KICH_survival.txt")

os.makedirs(BASE_DIR,  exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

log_lines = []
def rlog(m=""):
    print(m); log_lines.append(str(m))
def write_log():
    open(REPORT,"w").write("\n".join(log_lines))

# ═══════════════════════════════════════════════════════════════
# NETWORK
# ══════════════════════════════════════════════════════════════���

def ftp_get(ftp_path, dest,
             host="ftp.ncbi.nlm.nih.gov"):
    try:
        ftp  = ftplib.FTP(host, timeout=120)
        ftp.login()
        sz   = ftp.size(ftp_path) or 0
        done = [0]
        if os.path.exists(dest): os.remove(dest)
        def cb(chunk):
            done[0] += len(chunk)
            if sz:
                print(f"\r  {100*done[0]/sz:.0f}%"
                      f" ({done[0]//1024}KB)",
                      end="", flush=True)
            open(dest, "ab").write(chunk)
        ftp.retrbinary(f"RETR {ftp_path}",
                        cb, 65536)
        ftp.quit(); print()
        rlog(f"  ✓ FTP {os.path.getsize(dest)//1024}"
             f"KB → {os.path.basename(dest)}")
        return True
    except Exception as e:
        rlog(f"  FTP error: {e}")
        if os.path.exists(dest): os.remove(dest)
        return False

def http_get(url, dest=None, timeout=120):
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent":
                          "OrganismCore/1.0"})
        with urllib.request.urlopen(
                req, timeout=timeout) as resp:
            total = int(resp.headers.get(
                "Content-Length", 0))
            buf  = b""; done = 0
            fh   = open(dest, "wb") if dest \
                else None
            while True:
                chunk = resp.read(65536)
                if not chunk: break
                done += len(chunk)
                if fh:  fh.write(chunk)
                else:   buf += chunk
                if total:
                    print(f"\r  {100*done/total:.0f}%"
                          f" ({done//1024}KB)",
                          end="", flush=True)
            if fh:
                fh.close(); print()
                rlog(f"  ✓ HTTP "
                     f"{os.path.getsize(dest)//1024}"
                     f"KB → "
                     f"{os.path.basename(dest)}")
                return True
            return buf
    except urllib.error.HTTPError as e:
        rlog(f"  HTTP {e.code}: {url[:60]}")
        return None
    except Exception as e:
        rlog(f"  Error: {e}"); return None

def ftp_list(path,
              host="ftp.ncbi.nlm.nih.gov"):
    try:
        ftp = ftplib.FTP(host, timeout=30)
        ftp.login()
        items = []
        ftp.retrlines(f"LIST {path}",
                       items.append)
        ftp.quit(); return items
    except: return []

# ═══════════════════════════════════════════════════════════════
# ANNOTATION LOADING (cached from v1)
# ═══════════════════════════════════════════════════════════════

def load_cached_annotation(cache_path,
                             min_entries=1000):
    """Load annotation from cache TSV.gz."""
    if not os.path.exists(cache_path):
        return {}
    df = pd.read_csv(cache_path, sep="\t",
                     index_col=0,
                     compression="gzip")
    m  = df.iloc[:, 0].dropna().to_dict()
    m  = {str(k): str(v) for k, v in m.items()
          if str(v) not in
          ["nan", "---", "", "gene symbol"]}
    return m if len(m) >= min_entries else {}

def get_gpl570():
    """Load GPL570 — use cache from v1."""
    rlog(""); rlog("="*60)
    rlog("GPL570 ANNOTATION")
    rlog("="*60)
    cache = os.path.join(
        CACHE_DIR, "GPL570_full.tsv.gz")
    m = load_cached_annotation(cache,
                                min_entries=10000)
    if m:
        rlog(f"  Loaded from cache: {len(m)} probes")
        return m

    # Re-extract from family SOFT if cache missing
    rlog("  Cache missing — re-extracting "
         "from GSE19982 family SOFT")
    soft = os.path.join(
        CACHE_DIR,
        "GSE19982_family.soft.gz")
    if not (os.path.exists(soft) and
            os.path.getsize(soft) > 1_000_000):
        rlog("  Downloading family SOFT...")
        http_get(
            "https://ftp.ncbi.nlm.nih.gov"
            "/geo/series/GSE19nnn/GSE19982"
            "/soft/GSE19982_family.soft.gz",
            soft)

    if not os.path.exists(soft):
        rlog("  ERROR: Cannot get GPL570")
        return {}

    mapping  = {}
    in_plat  = False
    in_table = False
    gs_idx   = None
    header   = None
    opener   = (gzip.open
                if soft.endswith(".gz") else open)
    with opener(soft, "rt",
                encoding="utf-8",
                errors="replace") as fh:
        for line in fh:
            line = line.rstrip()
            if line.startswith("^PLATFORM"):
                in_plat  = True
                in_table = False
                header   = None
                gs_idx   = None
                continue
            if line.startswith("^SAMPLE") \
                    and len(mapping) > 10000:
                break
            if not in_plat: continue
            if "!platform_table_begin" in line:
                in_table = True; continue
            if "!platform_table_end" in line:
                in_table = False
                if len(mapping) > 10000: break
                continue
            if not in_table: continue
            parts = line.split("\t")
            if header is None:
                header = [p.strip('"').lower()
                           for p in parts]
                gs_idx = next(
                    (i for i, h in
                     enumerate(header)
                     if "gene symbol" in h
                     or h == "symbol"),
                    None)
                continue
            if gs_idx is None or \
                    len(parts) <= gs_idx:
                continue
            pid = parts[0].strip('"').strip()
            gs  = parts[gs_idx].strip('"').strip()
            if not gs or gs in \
                    ["---","","gene symbol"]:
                continue
            gs = re.split(r"\s*///\s*",
                           gs)[0].strip()
            if gs and pid:
                mapping[pid] = gs

    rlog(f"  Extracted: {len(mapping)} probes")
    if len(mapping) > 1000:
        pd.Series(mapping, name="Gene Symbol")\
          .to_csv(cache, sep="\t",
                  compression="gzip",
                  header=True)
    return mapping

def get_gpl10558():
    """Load GPL10558 — use cache from v1."""
    rlog(""); rlog("="*60)
    rlog("GPL10558 ANNOTATION")
    rlog("="*60)
    cache = os.path.join(
        CACHE_DIR, "GPL10558_full.tsv.gz")
    m = load_cached_annotation(cache,
                                min_entries=5000)
    if m:
        rlog(f"  Loaded from cache: {len(m)} probes")
        return m

    # Re-download from FTP if cache missing
    rlog("  Cache missing — fetching GPL10558")
    ftp_path = ("/geo/platforms/GPL10nnn/"
                "GPL10558/annot/"
                "GPL10558.annot.gz")
    dest = os.path.join(
        CACHE_DIR, "gpl10558_annot.gz")
    if ftp_get(ftp_path, dest):
        m = parse_annot_file(dest)
        if len(m) > 5000:
            pd.Series(m, name="Gene Symbol")\
              .to_csv(cache, sep="\t",
                      compression="gzip",
                      header=True)
            return m

    rlog("  ERROR: Cannot get GPL10558")
    return {}

def parse_annot_file(path):
    """Generic GPL annotation parser."""
    mapping  = {}
    header   = None
    gs_idx   = None
    opener   = (gzip.open
                if path.endswith(".gz") else open)
    try:
        with opener(path, "rt",
                    encoding="utf-8",
                    errors="replace") as fh:
            for line in fh:
                line = line.rstrip()
                if line.startswith(
                        ("^","!","#")): continue
                parts = line.split("\t")
                if not parts or not parts[0]:
                    continue
                if header is None:
                    header = [p.strip('"').lower()
                               for p in parts]
                    for cand in [
                        "gene symbol",
                        "gene_symbol","symbol"]:
                        gs_idx = next(
                            (i for i, h in
                             enumerate(header)
                             if cand in h),
                            None)
                        if gs_idx: break
                    continue
                if gs_idx is None or \
                        len(parts) <= gs_idx:
                    continue
                pid = parts[0].strip('"').strip()
                gs  = parts[gs_idx]\
                    .strip('"').strip()
                if not gs or gs in \
                        ["---","","NA"]:
                    continue
                gs = re.split(r"\s*///\s*",
                               gs)[0].strip()
                if gs and pid:
                    mapping[pid] = gs
    except Exception as e:
        rlog(f"  Parse error: {e}")
    return mapping

# ═══════════════════════════════════════════════════════════════
# CLASSIFICATION — v2 with anatomy zones
# ═══════════════════════════════════════════════════════════════

def classify_sample(text, gse_tag=""):
    """
    Classify one sample from its full
    metadata text.

    GSE95425-specific:
      "sampling depth: cortex"      → normal_cortex
      "sampling depth: medulla"     → normal_medulla
      "sampling depth: cortex/medulla"
                                    → normal_corticomedullary

    Anatomical rationale:
      medulla     = collecting duct zone
                    = intercalated cell-enriched
                    = the best available proxy
                    for the chRCC normal pole
      cortex      = proximal tubule + glomeruli
                    = important contrast
      cortex/medulla = mixed zone

    For Script 1:
      All three are classified as "normal"
      (barcode suffix -11) so all 53 contribute
      to the normal pole in the depth score.
      The sub-type labels (A/B/C) allow
      post-hoc analysis of which zone best
      captures intercalated cell identity.
    """
    t = text.lower()

    # ── Tumour types ──────────────────────────
    if re.search(r"chromophobe|chrcc", t):
        return "chRCC"
    if re.search(r"oncocytoma", t):
        return "oncocytoma"
    if re.search(r"clear.cell|ccRCC|KIRC", t):
        return "ccRCC"
    if re.search(r"papillary|PRCC|KIRP", t):
        return "papillary"

    # ── GSE95425 anatomy zones ────────────────
    # Check for "sampling depth" field first
    # (unique to GSE95425)
    depth_match = re.search(
        r"sampling depth\s*:\s*"
        r"(cortex/medulla|cortex|medulla)",
        t, re.I)
    if depth_match:
        zone = depth_match.group(1).lower()\
                          .strip()
        if zone == "cortex":
            return "normal_cortex"
        elif zone == "medulla":
            return "normal_medulla"
        elif zone in ["cortex/medulla",
                       "corticomedullary"]:
            return "normal_corticomedullary"

    # ── Generic cell-type labels ──────────────
    if re.search(
            r"intercalat"
            r"|alpha.?ic|beta.?ic"
            r"|type[\s:_-]*[ab]\b"
            r"|\baic\b|\bbic\b",
            t, re.I):
        return "normal_IC"
    if re.search(
            r"proximal.tubule|\bPCT\b|\bPST\b",
            t, re.I):
        return "normal_PT"
    if re.search(
            r"distal.tubule|\bDCT\b", t, re.I):
        return "normal_DCT"
    if re.search(
            r"glomerul|podocyte", t, re.I):
        return "normal_glom"
    if re.search(
            r"loop.of.henle|\bTAL\b", t, re.I):
        return "normal_LOH"
    if re.search(
            r"collecting.duct|principal.cell",
            t, re.I):
        return "normal_CD"

    # ── Generic normal ────────────────────────
    if re.search(
            r"normal.kidney|adjacent.normal"
            r"|non.tumor|healthy.kidney"
            r"|kidney.biopsy|biopsy"
            r"|renal.cortex|renal.medulla",
            t, re.I):
        return "normal_other"

    return "unknown"

def classify_all_samples(meta_lines,
                           samples,
                           gse_tag):
    """Classify all samples in a dataset."""
    # Keys to search, in priority order
    priority_keys = [
        "!Sample_characteristics_ch1",
        "!Sample_source_name_ch1",
        "!Sample_title",
        "!Sample_description",
        "!Sample_characteristics_ch2",
    ]
    all_keys = priority_keys + [
        k for k in meta_lines
        if k not in priority_keys]

    class_map = {}
    for i, gsm in enumerate(samples):
        parts = []
        for key in all_keys:
            vals = meta_lines.get(key, [])
            if i < len(vals) and vals[i]:
                parts.append(
                    vals[i].strip().lower())
        full_text = " | ".join(parts)
        class_map[gsm] = classify_sample(
            full_text, gse_tag)

    counts = collections.Counter(
        class_map.values())
    rlog(f"  Classification: {dict(counts)}")
    return class_map

# ═══════════════════════════════════════════════════════════════
# SERIES MATRIX PARSER
# ═══════════════════════════════════════════════════════════════

def parse_matrix(matrix_path, probe_gene,
                  gse_tag):
    """
    Parse GEO series matrix, map probes to
    genes, classify samples.
    Returns (gene_df_normed, class_map).
    """
    rlog(f"\n  Parsing {gse_tag}...")

    if not os.path.exists(matrix_path):
        rlog(f"  Missing: {matrix_path}")
        return None, {}

    meta_lines = collections.OrderedDict()
    samples    = []
    expr_rows  = []
    expr_cols  = []
    in_table   = False

    opener = (gzip.open
              if matrix_path.endswith(".gz")
              else open)
    with opener(matrix_path, "rt",
                encoding="utf-8",
                errors="replace") as fh:
        for line in fh:
            line = line.rstrip()
            if line.startswith(
                    "!Sample_geo_accession"):
                samples = [v.strip('"') for v
                            in line.split("\t")[1:]]
            elif line.startswith("!Sample_"):
                k = line.split("\t")[0]
                v = [x.strip('"') for x in
                     line.split("\t")[1:]]
                meta_lines[k] = v
            elif "series_matrix_table_begin" \
                    in line:
                in_table = True
            elif "series_matrix_table_end" \
                    in line:
                break
            elif in_table:
                parts = line.split("\t")
                pid   = parts[0].strip('"')
                if pid in ["ID_REF",
                            '"ID_REF"', ""]:
                    expr_cols = [
                        p.strip('"')
                        for p in parts[1:]]
                    continue
                if pid not in probe_gene:
                    continue
                try:
                    vals = [
                        float(v) if v.strip()
                        not in ["","NA","nan",
                                 "null","NaN"]
                        else np.nan
                        for v in parts[1:]]
                    if len(vals) == len(expr_cols):
                        expr_rows.append(
                            [pid]+vals)
                except: continue

    rlog(f"  Mapped probes: {len(expr_rows)}  "
         f"Samples: {len(expr_cols)}")

    if not expr_rows:
        rlog("  No mapped probes found")
        return None, {}

    # Build gene-level DataFrame (max probe)
    probe_ids = [r[0] for r in expr_rows]
    data = np.array(
        [r[1:] for r in expr_rows], dtype=float)
    probe_df = pd.DataFrame(
        data, index=probe_ids, columns=expr_cols)

    gene_data = {}
    for pid, gene in probe_gene.items():
        if pid not in probe_df.index: continue
        v = probe_df.loc[pid].values
        if gene not in gene_data:
            gene_data[gene] = v
        elif np.nanmean(v) > \
                np.nanmean(gene_data[gene]):
            gene_data[gene] = v

    gene_df = pd.DataFrame(
        gene_data, index=expr_cols).T
    rlog(f"  Genes: {gene_df.shape[0]} × "
         f"samples: {gene_df.shape[1]}")

    # Classify
    use_samples = samples if samples \
        else list(expr_cols)
    class_map = classify_all_samples(
        meta_lines, use_samples, gse_tag)

    # Normalise: log2 then rank-per-sample
    log2_df = np.log2(gene_df.clip(lower=1.0))
    normed  = log2_df.copy().astype(float)
    for col in log2_df.columns:
        v = log2_df[col].values.astype(float)
        f = np.isfinite(v)
        r = np.empty_like(v); r[:] = np.nan
        if f.sum() > 0:
            r[f] = rankdata(v[f]) / f.sum()
        normed[col] = r

    return normed, class_map

# ═══��═══════════════════════════════════════════════════════════
# ASSEMBLE OUTPUT
# ═══════════════════════════════════════════════════════════════

def assemble(expr_list, class_maps):
    """Combine, barcode, and save."""
    rlog(""); rlog("="*60)
    rlog("ASSEMBLE FINAL FILES")
    rlog("="*60)

    if not expr_list:
        rlog("  ERROR: No expression data")
        return False

    all_classes = {}
    for cm in class_maps:
        all_classes.update(cm)

    # Gene intersection
    gene_sets = [set(e.index) for e in expr_list]
    common    = gene_sets[0]
    for gs in gene_sets[1:]: common &= gs
    rlog(f"  Common genes: {len(common)}")
    if len(common) < 50:
        all_genes = set()
        for gs in gene_sets: all_genes |= gs
        common = all_genes
        rlog(f"  Using union: {len(common)}")

    frames   = [e.reindex(list(common))
                for e in expr_list]
    combined = pd.concat(frames, axis=1)
    rlog(f"  Matrix: {combined.shape[0]} × "
         f"{combined.shape[1]}")

    # TCGA-style barcodes
    # Tumour code = 01 (chRCC), 02 (oncocytoma)
    # Normal code = 11 (all normal subtypes)
    # Letter distinguishes normal subtype
    code_map = {
        "chRCC":                  ("01","A"),
        "oncocytoma":             ("02","A"),
        "normal_IC":              ("11","A"),
        "normal_PT":              ("11","B"),
        "normal_glom":            ("11","C"),
        "normal_LOH":             ("11","D"),
        "normal_DCT":             ("11","E"),
        "normal_CD":              ("11","F"),
        "normal_cortex":          ("11","G"),
        "normal_medulla":         ("11","H"),
        "normal_corticomedullary":("11","I"),
        "normal_other":           ("11","J"),
        "ccRCC":                  ("01","B"),
        "papillary":              ("01","C"),
        "unknown":                ("06","A"),
    }
    counters    = collections.defaultdict(int)
    barcode_map = {}
    for gsm in combined.columns:
        cls  = all_classes.get(gsm, "unknown")
        code, letter = code_map.get(
            cls, ("06","A"))
        counters[cls] += 1
        n = counters[cls]
        barcode_map[gsm] = (
            f"TCGA-KI-{n:04d}-"
            f"X{n:02d}-{code}{letter}-01-01")

    combined.columns = [
        barcode_map.get(s, s)
        for s in combined.columns]

    # Save expression
    combined.to_csv(OUT_EXPR, sep="\t",
                    compression="gzip")
    sz = os.path.getsize(OUT_EXPR)/1024/1024
    rlog(f"  Expression: {sz:.1f}MB → {OUT_EXPR}")

    # Save clinical
    rows = []
    for gsm, bc in barcode_map.items():
        cls = all_classes.get(gsm, "unknown")
        rows.append({
            "sample_id":       bc,
            "original_gsm":    gsm,
            "class":           cls,
            "is_tumour":       cls in [
                "chRCC","oncocytoma"],
            "is_normal":       cls.startswith(
                "normal"),
            "is_chRCC":        cls=="chRCC",
            "is_oncocytoma":   cls=="oncocytoma",
            "is_normal_IC":    cls=="normal_IC",
            "is_normal_medulla":
                cls=="normal_medulla",
            "is_normal_cortex":
                cls=="normal_cortex",
        })
    meta_df = pd.DataFrame(rows)\
                .set_index("sample_id")
    meta_df.to_csv(OUT_CLIN, sep="\t")
    rlog(f"  Clinical: {OUT_CLIN}")

    # Save survival stub
    pd.DataFrame({
        "sample":  list(barcode_map.values()),
        "OS":      np.nan,
        "OS.time": np.nan,
    }).set_index("sample").to_csv(
        OUT_SURV, sep="\t")
    rlog(f"  Survival: {OUT_SURV} (empty stub)")

    # Summary
    counts = collections.Counter(
        all_classes.values())
    rlog("")
    rlog("  SAMPLE COUNTS:")
    for cls, n in sorted(counts.items(),
                          key=lambda x:-x[1]):
        rlog(f"  {cls:<28} n={n:>3}")

    n_ch   = counts.get("chRCC", 0)
    n_norm = sum(v for k, v in counts.items()
                 if k.startswith("normal"))
    n_med  = counts.get("normal_medulla", 0)
    n_ctx  = counts.get("normal_cortex", 0)
    n_ctxm = counts.get(
        "normal_corticomedullary", 0)
    genes  = combined.shape[0]

    rlog("")
    rlog(f"  Genes:                  {genes}")
    rlog(f"  chRCC tumours:    {n_ch:>4}  "
         f"{'✓' if n_ch>=10 else '⚠'}")
    rlog(f"  Normal (all):     {n_norm:>4}  "
         f"{'✓' if n_norm>=5 else '⚠'}")
    rlog(f"    cortex:         {n_ctx:>4}")
    rlog(f"    medulla:        {n_med:>4}  "
         f"← IC-enriched zone")
    rlog(f"    cortex/medulla: {n_ctxm:>4}")
    rlog("")
    rlog("  SCIENTIFIC NOTE:")
    rlog("  normal_medulla samples (code -11H-)")
    rlog("  are used as the intercalated cell")
    rlog("  proxy in Script 1.")
    rlog("  Script 1 identifies -11- samples")
    rlog("  as normal regardless of letter.")
    rlog("  All 53 normals contribute to the")
    rlog("  normal pole anchor.")

    return n_ch >= 10 and genes >= 50

# ═══════════════════════════════════════════════════════════════
# ENSURE MATRICES ARE DOWNLOADED
# ═══════════════════════════════════════════════════════════════

def ensure_matrix(gse, cache_name,
                   ftp_path, http_url):
    path = os.path.join(CACHE_DIR, cache_name)
    if os.path.exists(path) and \
            os.path.getsize(path) > 100_000:
        rlog(f"  {gse}: cached ✓")
        return path
    rlog(f"  {gse}: downloading...")
    if http_get(http_url, path):
        return path
    if ftp_get(ftp_path, path):
        return path
    rlog(f"  {gse}: download failed")
    return None

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    rlog("="*60)
    rlog("chRCC DATA BUILDER v2")
    rlog("OrganismCore | Document 96-build-v2")
    rlog("2026-03-02 | Eric Robert Lawson")
    rlog("="*60)
    rlog("")
    rlog("PATCH: GSE95425 reclassified by")
    rlog("anatomical zone (cortex/medulla)")
    rlog("rather than cell type (none present)")

    # Annotations (use cache from v1)
    gpl570   = get_gpl570()
    gpl10558 = get_gpl10558()

    if not gpl570:
        rlog("FATAL: GPL570 annotation missing")
        write_log(); return 1
    if not gpl10558:
        rlog("FATAL: GPL10558 annotation missing")
        write_log(); return 1

    rlog(f"\n  GPL570:   {len(gpl570)} probes")
    rlog(f"  GPL10558: {len(gpl10558)} probes")

    expr_list  = []
    class_maps = []

    # ── GSE19982 (chRCC + oncocytoma) ─────────
    rlog(""); rlog("="*60)
    rlog("GSE19982 — chRCC + oncocytoma")
    rlog("="*60)
    m19 = ensure_matrix(
        "GSE19982",
        "GSE19982_series_matrix.txt.gz",
        "/geo/series/GSE19nnn/GSE19982/matrix/"
        "GSE19982_series_matrix.txt.gz",
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "series/GSE19nnn/GSE19982/matrix/"
        "GSE19982_series_matrix.txt.gz")
    if m19:
        expr19, cls19 = parse_matrix(
            m19, gpl570, "GSE19982")
        if expr19 is not None:
            rename = {s: f"GSE19982_{s}"
                      for s in expr19.columns}
            expr19 = expr19.rename(columns=rename)
            cls19  = {f"GSE19982_{k}": v
                      for k, v in cls19.items()}
            expr_list.append(expr19)
            class_maps.append(cls19)
            n_ch = sum(1 for v in cls19.values()
                       if v=="chRCC")
            n_on = sum(1 for v in cls19.values()
                       if v=="oncocytoma")
            rlog(f"  ✓ chRCC={n_ch}  "
                 f"oncocytoma={n_on}  "
                 f"genes={expr19.shape[0]}")

    # ── GSE95425 (normal kidney anatomy) ──────
    rlog(""); rlog("="*60)
    rlog("GSE95425 — normal kidney biopsies")
    rlog("(anatomy zone classification)")
    rlog("="*60)
    m95 = ensure_matrix(
        "GSE95425",
        "GSE95425_series_matrix.txt.gz",
        "/geo/series/GSE95nnn/GSE95425/matrix/"
        "GSE95425_series_matrix.txt.gz",
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "series/GSE95nnn/GSE95425/matrix/"
        "GSE95425_series_matrix.txt.gz")
    if m95:
        expr95, cls95 = parse_matrix(
            m95, gpl10558, "GSE95425")
        if expr95 is not None and \
                len(expr95) > 0:
            rename = {s: f"GSE95425_{s}"
                      for s in expr95.columns}
            expr95 = expr95.rename(columns=rename)
            cls95  = {f"GSE95425_{k}": v
                      for k, v in cls95.items()}
            expr_list.append(expr95)
            class_maps.append(cls95)
            n_m = sum(1 for v in cls95.values()
                      if v=="normal_medulla")
            n_c = sum(1 for v in cls95.values()
                      if v=="normal_cortex")
            n_cm = sum(1 for v in cls95.values()
                       if v==
                       "normal_corticomedullary")
            rlog(f"  ✓ medulla={n_m}  "
                 f"cortex={n_c}  "
                 f"cortex/medulla={n_cm}  "
                 f"genes={expr95.shape[0]}")

    # ── Assemble ──────────────────────────────
    ready = assemble(expr_list, class_maps)

    write_log()

    rlog(""); rlog("="*60)
    if ready:
        rlog("BUILD v2 COMPLETE ✓")
        rlog("")
        rlog("Files ready for Script 1:")
        rlog(f"  {OUT_EXPR}")
        rlog(f"  {OUT_CLIN}")
        rlog(f"  {OUT_SURV}")
        rlog("")
        rlog("STATISTICAL NOTE:")
        rlog("  n=15 chRCC vs n=53 normal")
        rlog("  r > 0.514 for p<0.05 at n=15")
        rlog("  n_tumour is the binding constraint")
        rlog("  All depth correlations use")
        rlog("  tumour samples only (n=15)")
        rlog("  Normal samples anchor the pole")
        rlog("  but do not inflate n for r")
        rlog("")
        rlog("NORMAL POLE INTERPRETATION:")
        rlog("  normal_medulla (-11H-) samples")
        rlog("  are the collecting duct proxy")
        rlog("  — most relevant to chRCC origin")
        rlog("  normal_cortex (-11G-) samples")
        rlog("  are the proximal tubule proxy")
        rlog("  — relevant for cross-cancer")
        rlog("  comparison vs PRCC/ccRCC")
        rlog("")
        rlog("Run: python "
             "chrcc_false_attractor_v1.py")
    else:
        rlog("BUILD v2 FAILED")
        rlog(f"Report: {REPORT}")
    rlog("="*60)

    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
