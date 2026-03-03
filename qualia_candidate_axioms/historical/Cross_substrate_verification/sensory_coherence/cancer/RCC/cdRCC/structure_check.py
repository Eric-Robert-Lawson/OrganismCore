"""
cdRCC — Collecting Duct Renal Cell Carcinoma
STRUCTURAL CHECK — Phase 0.5  (v2 — auto file discovery)

Changes from v1:
  - File names are discovered live from the GEO download
    page and FTP directory listing rather than hardcoded.
    The v1 file names returned 404 — actual names differ.
  - Falls back to individual GSM supplementary files if
    series-level matrix not found.
  - All other logic identical.

Author: Eric Robert Lawson
Framework: OrganismCore Principles-First
Date: 2026-03-03
"""

import os
import sys
import gzip
import re
import urllib.request
import urllib.error
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./cdRCC_false_attractor/"
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_FILE    = os.path.join(BASE_DIR,
                           "structural_check_log.txt")

os.makedirs(BASE_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

ACC = "GSE89122"
GEO_FTP_BASE = (
    "https://ftp.ncbi.nlm.nih.gov/geo/"
    "series/GSE89nnn/GSE89122/suppl/"
)
GEO_DOWNLOAD_PAGE = (
    "https://www.ncbi.nlm.nih.gov/geo/"
    "download/?acc=GSE89122"
)
GEO_SOFT_PAGE = (
    "https://www.ncbi.nlm.nih.gov/geo/query/"
    "acc.cgi?acc=GSE89122"
    "&targ=self&form=text&view=brief"
)
META_URL = (
    "https://www.ncbi.nlm.nih.gov/geo/query/"
    "acc.cgi?acc=GSE89122"
    "&targ=gsm&form=text&view=full"
)

# Known sample structure — confirmed from metadata
# in previous run (all 13/13 matched)
SAMPLE_MAP = {
    "GSM2359144": ("CDC1", "tumor"),
    "GSM2359145": ("CDC1", "normal"),
    "GSM2359146": ("CDC2", "tumor"),
    "GSM2359147": ("CDC2", "normal"),
    "GSM2359148": ("CDC3", "tumor"),
    "GSM2359149": ("CDC3", "normal"),
    "GSM2359150": ("CDC4", "tumor"),
    "GSM2359151": ("CDC4", "normal"),
    "GSM2359152": ("CDC5", "tumor"),
    "GSM2359153": ("CDC6", "tumor"),
    "GSM2359154": ("CDC6", "normal"),
    "GSM2359155": ("CDC7", "tumor"),
    "GSM2359156": ("CDC7", "normal"),
}

# ============================================================
# LOGGING
# ============================================================

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

# ============================================================
# FETCH UTILITY
# ============================================================

def fetch_text(url, timeout=30):
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
        return f"ERROR:{e}"

def download_file(url, local_path):
    def hook(count, block, total):
        if total > 0:
            pct = min(count * block / total * 100, 100)
            mb  = count * block / 1e6
            sys.stdout.write(
                f"\r    {mb:.2f} MB  {pct:.1f}%"
            )
            sys.stdout.flush()
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req) as resp, \
             open(local_path, "wb") as out:
            total = int(
                resp.headers.get("Content-Length", 0)
            )
            block = 65536
            count = 0
            while True:
                chunk = resp.read(block)
                if not chunk:
                    break
                out.write(chunk)
                count += 1
                hook(count, block, total)
        print()
        return True
    except Exception as e:
        print()
        log(f"    ERROR: {e}")
        return False

# ============================================================
# STEP 0: DISCOVER REAL FILE NAMES FROM GEO
# ============================================================

def discover_files():
    """
    Scrape the GEO download page and SOFT series text
    to find the actual supplementary file names for
    GSE89122. Returns dict of label → filename.
    """
    log("=" * 65)
    log("STEP 0 — FILE DISCOVERY")
    log(f"  Querying GEO for actual file names...")
    log("=" * 65)

    found_files = {}

    # ---- Method 1: SOFT series text ----
    # The SOFT text contains !Series_supplementary_file lines
    log("\n  [Method 1] Parsing SOFT series text...")
    soft_url = (
        "https://www.ncbi.nlm.nih.gov/geo/query/"
        f"acc.cgi?acc={ACC}"
        "&targ=self&form=text&view=full"
    )
    soft_text = fetch_text(soft_url)

    if "ERROR" not in soft_text[:20]:
        suppl_files = []
        for line in soft_text.split("\n"):
            if "!Series_supplementary_file" in line:
                val = line.split("=", 1)[1].strip()
                suppl_files.append(val)
                log(f"    Found: {val}")

        if suppl_files:
            for f in suppl_files:
                fname = f.split("/")[-1].strip()
                fl    = fname.lower()
                if "tpm" in fl:
                    found_files["tpm"] = fname
                elif "fpkm" in fl:
                    found_files["fpkm"] = fname
                elif "raw" in fl or "count" in fl:
                    found_files["raw"] = fname
                elif "annot" in fl or ".annot" in fl:
                    found_files["annot"] = fname
                else:
                    found_files[f"other_{len(found_files)}"] = fname
        else:
            log("    No supplementary_file lines found in SOFT")
    else:
        log(f"    SOFT fetch error: {soft_text[:80]}")

    # ---- Method 2: FTP directory listing ----
    # Try to list the FTP directory via HTTP
    log(f"\n  [Method 2] FTP directory listing...")
    ftp_dir = GEO_FTP_BASE
    dir_text = fetch_text(ftp_dir)

    if "ERROR" not in dir_text[:20]:
        # HTML directory listing — extract .gz filenames
        fnames = re.findall(
            r'href="([^"]+\.gz)"', dir_text
        )
        if not fnames:
            # Try plain text listing
            fnames = re.findall(
                r'(GSE\d+[^\s]+\.gz)', dir_text
            )
        log(f"    Found {len(fnames)} .gz files:")
        for fn in fnames:
            fn_clean = fn.split("/")[-1]
            log(f"      {fn_clean}")
            fl = fn_clean.lower()
            if "tpm" in fl and "tpm" not in found_files:
                found_files["tpm"] = fn_clean
            elif ("fpkm" in fl
                  and "fpkm" not in found_files):
                found_files["fpkm"] = fn_clean
            elif (("raw" in fl or "count" in fl)
                  and "raw" not in found_files):
                found_files["raw"] = fn_clean
            elif ("annot" in fl
                  and "annot" not in found_files):
                found_files["annot"] = fn_clean
    else:
        log(f"    FTP listing error: {dir_text[:80]}")

    # ---- Method 3: GEO download page (HTML) ----
    log(f"\n  [Method 3] GEO download page...")
    dl_page = fetch_text(GEO_DOWNLOAD_PAGE)
    if "ERROR" not in dl_page[:20]:
        # Look for filenames in href links
        fnames_html = re.findall(
            r'href="[^"]*/(GSE89122[^"]+\.gz)"',
            dl_page
        )
        if not fnames_html:
            fnames_html = re.findall(
                r'(GSE89122[^\s"<>]+\.(?:gz|tsv|txt))',
                dl_page
            )
        log(f"    Found {len(fnames_html)} files in page:")
        for fn in fnames_html:
            fn_clean = fn.split("/")[-1]
            log(f"      {fn_clean}")
            fl = fn_clean.lower()
            if "tpm" in fl and "tpm" not in found_files:
                found_files["tpm"] = fn_clean
            elif ("fpkm" in fl
                  and "fpkm" not in found_files):
                found_files["fpkm"] = fn_clean
            elif (("raw" in fl or "count" in fl)
                  and "raw" not in found_files):
                found_files["raw"] = fn_clean
            elif ("annot" in fl
                  and "annot" not in found_files):
                found_files["annot"] = fn_clean
    else:
        log(f"    Download page error: {dl_page[:80]}")

    # ---- Method 4: GSM-level supplementary files ----
    # If no series-level matrix found, each GSM may have
    # an individual count file
    if not found_files:
        log(f"\n  [Method 4] Checking GSM-level files...")
        sample_gsms = list(SAMPLE_MAP.keys())[:3]
        for gsm in sample_gsms:
            gsm_url = (
                "https://www.ncbi.nlm.nih.gov/geo/query/"
                f"acc.cgi?acc={gsm}"
                "&targ=self&form=text&view=full"
            )
            gsm_text = fetch_text(gsm_url)
            if "ERROR" not in gsm_text[:20]:
                for line in gsm_text.split("\n"):
                    if "!Sample_supplementary_file" in line:
                        val = line.split("=",1)[1].strip()
                        fname = val.split("/")[-1].strip()
                        log(f"    {gsm}: {fname}")
                        if gsm not in found_files:
                            found_files[gsm] = fname
                        break

    log(f"\n  DISCOVERED FILES:")
    if found_files:
        for k, v in found_files.items():
            log(f"    [{k}]  {v}")
    else:
        log("  WARNING: No files discovered automatically")
        log("  Manual download required")
        log(f"  Visit: {GEO_DOWNLOAD_PAGE}")

    return found_files

# ============================================================
# STEP 0b: DOWNLOAD DISCOVERED FILES
# ============================================================

def download_files(found_files):
    log("")
    log("=" * 65)
    log("STEP 0b — DOWNLOADING FILES")
    log("=" * 65)

    paths = {}

    priority_keys = ["tpm", "fpkm", "raw", "annot"]
    ordered = (
        [(k, found_files[k]) for k in priority_keys
         if k in found_files]
        + [(k, v) for k, v in found_files.items()
           if k not in priority_keys]
    )

    for key, fname in ordered:
        local = os.path.join(BASE_DIR, fname)

        if os.path.exists(local):
            sz = os.path.getsize(local) / 1e6
            if sz > 0.01:
                log(f"  [{key}] Found cached: {fname} "
                    f"({sz:.2f} MB)")
                paths[key] = local
                continue

        url = GEO_FTP_BASE + fname
        log(f"  [{key}] Downloading: {fname}")
        log(f"    URL: {url}")

        ok = download_file(url, local)
        if ok and os.path.getsize(local) > 100:
            sz = os.path.getsize(local) / 1e6
            log(f"    OK: {sz:.2f} MB")
            paths[key] = local
        else:
            # Try HTTPS GEO download URL as fallback
            alt_url = (
                "https://www.ncbi.nlm.nih.gov/geo/"
                f"download/?acc={ACC}&format=file"
                f"&file={urllib.parse.quote(fname)}"
                if hasattr(urllib, "parse")
                else url
            )
            log(f"    FTP failed — trying alt URL")
            import urllib.parse
            alt_url = (
                "https://www.ncbi.nlm.nih.gov/geo/"
                "download/?acc=GSE89122&format=file"
                f"&file={urllib.parse.quote(fname)}"
            )
            log(f"    Alt URL: {alt_url}")
            ok2 = download_file(alt_url, local)
            if ok2 and os.path.getsize(local) > 100:
                sz = os.path.getsize(local) / 1e6
                log(f"    OK (alt): {sz:.2f} MB")
                paths[key] = local
            else:
                log(f"    FAILED — skipping {key}")
                if os.path.exists(local):
                    os.remove(local)

    return paths

# ============================================================
# STEP 1: METADATA — already confirmed, just reload
# ============================================================

def load_confirmed_metadata():
    log("")
    log("=" * 65)
    log("STEP 1 — SAMPLE METADATA (confirmed in v1)")
    log("=" * 65)

    cache = os.path.join(BASE_DIR, "gsm_meta.txt")
    rows = []

    if os.path.exists(cache):
        log(f"  Using cached metadata: {cache}")
        with open(cache, encoding="utf-8") as f:
            text = f.read()

        samples = {}
        current_gsm = None
        current = {}
        for line in text.split("\n"):
            if line.startswith("^SAMPLE"):
                if current_gsm and current:
                    samples[current_gsm] = current
                current_gsm = line.split("=")[1].strip()
                current = {}
            elif line.startswith("!Sample_title"):
                current["title"] = \
                    line.split("=",1)[1].strip()
            elif line.startswith(
                    "!Sample_library_strategy"):
                current["lib"] = \
                    line.split("=",1)[1].strip()
            elif line.startswith(
                    "!Sample_supplementary_file"):
                val = line.split("=",1)[1].strip()
                current.setdefault(
                    "suppl", []
                ).append(val)
        if current_gsm and current:
            samples[current_gsm] = current

        for gsm, (patient, stype) in SAMPLE_MAP.items():
            info = samples.get(gsm, {})
            title = info.get("title", "")
            lib   = info.get("lib", "")
            suppl = info.get("suppl", [])
            rows.append({
                "gsm":     gsm,
                "patient": patient,
                "type":    stype,
                "title":   title,
                "lib":     lib,
                "suppl":   suppl,
            })
            log(
                f"  {gsm}  {patient:6s}  {stype:6s}  "
                f"lib={lib}"
            )
            for s in suppl:
                fname = s.split("/")[-1]
                log(f"    suppl: {fname}")
    else:
        log("  No cached metadata — building from SAMPLE_MAP")
        for gsm, (patient, stype) in SAMPLE_MAP.items():
            rows.append({
                "gsm": gsm, "patient": patient,
                "type": stype, "title": "",
                "lib": "RNA-Seq", "suppl": [],
            })

    meta = pd.DataFrame(rows)
    log(f"\n  Tumour:  {(meta['type']=='tumor').sum()}")
    log(f"  Normal:  {(meta['type']=='normal').sum()}")
    log(f"  Total:   {len(meta)}")

    # Extract GSM-level supplementary file names
    gsm_suppl = {}
    for _, row in meta.iterrows():
        if row["suppl"]:
            gsm_suppl[row["gsm"]] = [
                s.split("/")[-1]
                for s in row["suppl"]
            ]

    if gsm_suppl:
        log("\n  GSM-LEVEL SUPPLEMENTARY FILES:")
        for gsm, fnames in gsm_suppl.items():
            patient, stype = SAMPLE_MAP[gsm]
            for fn in fnames:
                log(f"    {gsm} ({patient} {stype}): "
                    f"{fn}")

    return meta, gsm_suppl

# ============================================================
# STEP 2: DOWNLOAD GSM-LEVEL FILES IF NEEDED
# ============================================================

def download_gsm_files(gsm_suppl):
    """
    If no series-level matrix was found,
    download individual per-sample count files
    and merge them into a single matrix.
    """
    log("")
    log("=" * 65)
    log("STEP 2 — GSM-LEVEL FILE DOWNLOAD")
    log("  Downloading individual sample count files")
    log("=" * 65)

    gsm_paths = {}
    gsm_prefix_map = {}

    for gsm, fnames in gsm_suppl.items():
        for fname in fnames:
            # Determine FTP prefix for this GSM
            # GSM2359144 → GSM2359nnn
            gsm_num = int(re.sub(r"\D", "", gsm))
            prefix  = str(gsm_num)[:-3] + "nnn"
            gsm_ftp = (
                "https://ftp.ncbi.nlm.nih.gov/geo/"
                f"samples/GSM{prefix}/{gsm}/suppl/"
            )

            local = os.path.join(BASE_DIR, fname)
            if os.path.exists(local):
                sz = os.path.getsize(local) / 1e6
                if sz > 0.001:
                    log(f"  {gsm}: cached {fname}")
                    gsm_paths[gsm] = local
                    continue

            url = gsm_ftp + fname
            log(f"  {gsm}: downloading {fname}")
            log(f"    URL: {url}")
            ok = download_file(url, local)
            if ok and os.path.exists(local):
                sz = os.path.getsize(local) / 1e6
                log(f"    OK: {sz:.4f} MB")
                gsm_paths[gsm] = local
            else:
                log(f"    FAILED")

    return gsm_paths

# ============================================================
# STEP 3: INSPECT MATRIX (series or per-GSM)
# ============================================================

def inspect_series_matrix(path, label, meta):
    log("")
    log("=" * 65)
    log(f"STEP 3 — MATRIX INSPECTION: {label}")
    log(f"  File: {os.path.basename(path)}")
    log("=" * 65)

    if not path or not os.path.exists(path):
        log("  FILE NOT AVAILABLE")
        return None

    sz = os.path.getsize(path) / 1e6
    log(f"  File size: {sz:.2f} MB")

    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt") as f:
                df = pd.read_csv(
                    f, sep="\t", index_col=0,
                    low_memory=False
                )
        else:
            df = pd.read_csv(
                path, sep="\t", index_col=0,
                low_memory=False
            )
    except Exception as e:
        log(f"  ERROR reading: {e}")
        # Try comma separator
        try:
            if path.endswith(".gz"):
                with gzip.open(path, "rt") as f:
                    df = pd.read_csv(
                        f, sep=",", index_col=0,
                        low_memory=False
                    )
            else:
                df = pd.read_csv(
                    path, sep=",", index_col=0,
                    low_memory=False
                )
            log("  Loaded with comma separator")
        except Exception as e2:
            log(f"  ERROR (comma sep): {e2}")
            return None

    log(f"\n  Shape: {df.shape[0]} rows × "
        f"{df.shape[1]} cols")
    log(f"  Index name: {df.index.name}")
    log(f"\n  First 8 row IDs:")
    for idx in list(df.index[:8]):
        log(f"    {idx}")

    log(f"\n  All column names:")
    for col in df.columns:
        log(f"    {col}")

    # Check column alignment with GSM IDs
    gsm_cols  = [c for c in df.columns
                 if c in SAMPLE_MAP]
    other_cols = [c for c in df.columns
                  if c not in SAMPLE_MAP]
    log(f"\n  GSM-matching columns: {len(gsm_cols)}")
    log(f"  Other columns:        {len(other_cols)}")
    if other_cols:
        log(f"  Other: {other_cols[:10]}")

    # Try to map columns to sample info
    if gsm_cols:
        log("\n  COLUMN → SAMPLE MAPPING:")
        for col in df.columns:
            if col in SAMPLE_MAP:
                p, t = SAMPLE_MAP[col]
                log(f"    {col}  {p:6s}  {t}")
            else:
                log(f"    {col}  [not in SAMPLE_MAP]")

    # Expression value inspection
    num_df = df.select_dtypes(include=[np.number])
    if num_df.empty:
        log("\n  No numeric columns — check separator")
        return df

    flat = num_df.values.flatten()
    flat = flat[~np.isnan(flat)]

    log(f"\n  VALUE STATISTICS:")
    log(f"    Min:     {flat.min():.4f}")
    log(f"    Max:     {flat.max():.4f}")
    log(f"    Mean:    {flat.mean():.4f}")
    log(f"    Median:  {np.median(flat):.4f}")
    log(f"    % zero:  "
        f"{(flat==0).sum()/len(flat)*100:.2f}%")
    log(f"    99th pct: {np.percentile(flat,99):.2f}")

    needs_log = flat.max() > 50
    log(f"\n  Scale: {'LINEAR — log2(x+1) needed' if needs_log else 'log-scale'}")

    # Gene ID type
    ids = [str(x) for x in list(df.index[:10])]
    is_entrez  = all(s.isdigit() for s in ids)
    is_ensembl = any(s.startswith("ENSG") for s in ids)
    id_type = (
        "ENTREZ"  if is_entrez  else
        "ENSEMBL" if is_ensembl else
        "SYMBOL"
    )
    log(f"  Gene ID type: {id_type}")
    log(f"  Sample IDs: {ids[:6]}")

    # Zero rows
    row_means = num_df.mean(axis=1)
    log(f"\n  Rows with mean=0:   "
        f"{(row_means==0).sum()}")
    log(f"  Rows with mean<0.5: "
        f"{(row_means<0.5).sum()}")
    log(f"  Rows with mean>1:   "
        f"{(row_means>1.0).sum()}")

    # Duplicates
    log(f"  Duplicate row IDs:  "
        f"{df.index.duplicated().sum()}")

    return df

# ============================================================
# STEP 4: MERGE PER-GSM FILES
# ============================================================

def merge_gsm_files(gsm_paths, meta):
    """
    Merge individually downloaded GSM count files
    into a single genes × samples matrix.
    """
    log("")
    log("=" * 65)
    log("STEP 4 — MERGING PER-GSM FILES")
    log("=" * 65)

    frames = {}
    for gsm, path in gsm_paths.items():
        if not os.path.exists(path):
            continue
        try:
            if path.endswith(".gz"):
                with gzip.open(path, "rt") as f:
                    df = pd.read_csv(
                        f, sep="\t",
                        header=None,
                        names=["gene", "count"],
                        index_col=0
                    )
            else:
                df = pd.read_csv(
                    path, sep="\t",
                    header=None,
                    names=["gene", "count"],
                    index_col=0
                )
            frames[gsm] = df["count"]
            p, t = SAMPLE_MAP.get(gsm, ("?","?"))
            log(f"  {gsm} ({p} {t}): "
                f"{len(df)} genes")
        except Exception as e:
            log(f"  {gsm}: ERROR — {e}")

    if not frames:
        log("  No per-GSM files loaded")
        return None

    merged = pd.DataFrame(frames)
    log(f"\n  Merged matrix: {merged.shape}")
    log(f"  Samples: {list(merged.columns)}")

    # Save
    out = os.path.join(BASE_DIR,
                       "GSE89122_merged_counts.tsv")
    merged.to_csv(out, sep="\t")
    log(f"  Saved: {out}")

    return merged

# ============================================================
# STRUCTURAL SUMMARY
# ============================================================

def structural_summary(meta, matrix_df,
                        matrix_label, found_files):
    log("")
    log("=" * 65)
    log("STRUCTURAL SUMMARY FOR SCRIPT 1")
    log("=" * 65)

    log(f"\n  SAMPLES (confirmed)")
    log(f"    Total:   {len(meta)}")
    log(f"    Tumour:  {(meta['type']=='tumor').sum()}")
    log(f"    Normal:  {(meta['type']=='normal').sum()}")
    log(f"    Paired patients: 6 (CDC1-4, CDC6, CDC7)")
    log(f"    Unpaired tumour: 1 (CDC5)")

    log(f"\n  EXPRESSION FILES FOUND:")
    if found_files:
        for k, v in found_files.items():
            log(f"    [{k}]  {v}")
    else:
        log("    None discovered automatically")

    if matrix_df is not None:
        num = matrix_df.select_dtypes(
            include=[np.number]
        )
        flat = num.values.flatten()
        flat = flat[~np.isnan(flat)]
        needs_log = flat.max() > 50
        ids = [str(x) for x in list(
            matrix_df.index[:5]
        )]
        is_entrez = all(s.isdigit() for s in ids)

        log(f"\n  MATRIX ({matrix_label})")
        log(f"    Shape:       {matrix_df.shape}")
        log(f"    Max value:   {flat.max():.2f}")
        log(f"    Log needed:  {needs_log}")
        log(f"    Gene ID:     "
            f"{'ENTREZ' if is_entrez else 'SYMBOL/OTHER'}")

        log(f"\n  SCRIPT 1 SETTINGS:")
        log(f"    matrix_file = '{matrix_label}'")
        log(f"    log_transform = {needs_log}")
        log(f"    gene_id_type = "
            f"{'ENTREZ — needs symbol map' if is_entrez else 'SYMBOL — direct use'}")
        log(f"    filter_mean_tpm = 1.0")
    else:
        log(f"\n  NO MATRIX LOADED")
        log(f"  Manual download required.")
        log(f"  Visit: {GEO_DOWNLOAD_PAGE}")
        log(f"  Download any .tsv.gz or .txt.gz file")
        log(f"  containing expression values and place")
        log(f"  in: {BASE_DIR}")

    log("")
    log("  PLATFORM: Illumina HiSeq 2000")
    log("  GENOME:   GRCh38.p13")
    log("  DATA:     RNA-seq")
    log("  DESIGN:   6 matched pairs + 1 tumour-only")

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("cdRCC — COLLECTING DUCT CARCINOMA")
    log("STRUCTURAL CHECK v2 — Phase 0.5")
    log("GSE89122 — Auto file discovery")
    log("Date: 2026-03-03")
    log("=" * 65)

    # Step 0 — Discover real file names
    found_files = discover_files()

    # Step 0b — Download whatever was found
    paths = {}
    if found_files:
        paths = download_files(found_files)

    # Step 1 — Metadata (already confirmed)
    meta, gsm_suppl = load_confirmed_metadata()

    # Step 2 — If no series matrix, try GSM files
    gsm_paths = {}
    if not any(k in paths
               for k in ["tpm","fpkm","raw"]):
        if gsm_suppl:
            gsm_paths = download_gsm_files(gsm_suppl)
        else:
            log("\n  No GSM-level supplementary files "
                "found either.")
            log("  Dataset may only provide SRA/FASTQ.")
            log("  A pre-processed matrix is needed.")

    # Step 3 — Inspect whatever matrix we have
    matrix_df    = None
    matrix_label = None

    for key in ["tpm", "fpkm", "raw"]:
        if key in paths and paths[key]:
            matrix_df = inspect_series_matrix(
                paths[key], key.upper(), meta
            )
            matrix_label = key
            if matrix_df is not None:
                break

    # Step 4 — Merge per-GSM if needed
    if matrix_df is None and gsm_paths:
        matrix_df = merge_gsm_files(gsm_paths, meta)
        matrix_label = "per-GSM merged"
        if matrix_df is not None:
            inspect_series_matrix(
                os.path.join(
                    BASE_DIR,
                    "GSE89122_merged_counts.tsv"
                ),
                "MERGED COUNTS",
                meta
            )

    # Summary
    structural_summary(
        meta, matrix_df, matrix_label, found_files
    )

    write_log()
    log(f"\nLog: {LOG_FILE}")
    log("\n[STRUCTURAL CHECK v2 COMPLETE]")


if __name__ == "__main__":
    main()
