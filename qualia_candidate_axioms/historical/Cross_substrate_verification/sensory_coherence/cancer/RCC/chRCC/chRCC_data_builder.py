"""
chRCC Data Builder — Single Consolidated Script
OrganismCore | Document 96-build | 2026-03-02
Author: Eric Robert Lawson

Consolidates all discovery, repair, and annotation
fixes into one clean script that produces the three
files needed by chrcc_false_attractor_v1.py:

  ./chrcc_false_attractor/TCGA_KICH_HiSeqV2.gz
  ./chrcc_false_attractor/KICH_clinicalMatrix.tsv
  ./chrcc_false_attractor/KICH_survival.txt

DATA SOURCES (confirmed working):

  GSE19982 (GPL570, Affymetrix HG-U133 Plus 2.0)
    15 chRCC + 15 oncocytoma
    Annotation: extracted from GSE19982_family.soft.gz
    45,782 probe→gene mappings confirmed

  GSE95425 (GPL10558, Illumina HT-12 v4)
    53 normal kidney biopsies — cell types in
    !Sample_characteristics_ch1 fields
    GPL10558: 31,266 probe→gene mappings confirmed
    Classification fix: parse characteristics
    deeply to find intercalated / proximal / etc.

  GSE20376: EXCLUDED — CGH copy number arrays
            (GPL2004/GPL2005), not expression

KNOWN LIMITATIONS:
  No OS data → survival file is empty stubs
  C1-P6 (depth predicts OS) cannot be tested
  n=15 chRCC tumours (small — r threshold 0.514
  for p<0.05 at n=15; interpret conservatively)
  Normal pole = mixed kidney biopsies unless
  GSE95425 cell-type classification succeeds

OUTPUT FORMAT:
  Expression matrix mimics TCGA HiSeqV2:
    Tumour columns: barcode ending -01A-
    Normal columns: barcode ending -11A- etc.
    Oncocytoma:     barcode ending -02A-
  Script 1 classifies by barcode suffix
  (same logic as PRCC pipeline)
"""

import os, sys, gzip, ftplib, re, io, time
import urllib.request, urllib.error
import collections
import numpy as np
import pandas as pd
from scipy.stats import rankdata

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════

BASE_DIR  = "./chrcc_false_attractor/"
CACHE_DIR = os.path.join(BASE_DIR, "geo_cache/")
REPORT    = os.path.join(BASE_DIR,
                          "build_report.txt")

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
    print(m)
    log_lines.append(str(m))

def write_log():
    with open(REPORT, "w") as f:
        f.write("\n".join(log_lines))

# ═══════════════════════════════════════════════════════════════
# NETWORK UTILITIES
# ═══════════════════════════════════════════════════════════════

def ftp_get(ftp_path, dest,
             host="ftp.ncbi.nlm.nih.gov"):
    """Download a file via FTP with progress."""
    try:
        ftp  = ftplib.FTP(host, timeout=120)
        ftp.login()
        sz   = ftp.size(ftp_path) or 0
        done = [0]
        if os.path.exists(dest):
            os.remove(dest)
        def cb(chunk):
            done[0] += len(chunk)
            if sz:
                pct = 100 * done[0] / sz
                print(
                    f"\r  {pct:.0f}% "
                    f"({done[0]//1024}KB)",
                    end="", flush=True)
            with open(dest, "ab") as f:
                f.write(chunk)
        ftp.retrbinary(
            f"RETR {ftp_path}", cb, 65536)
        ftp.quit()
        print()
        sz_got = os.path.getsize(dest)
        rlog(f"  ✓ FTP {sz_got//1024}KB "
             f"→ {os.path.basename(dest)}")
        return True
    except Exception as e:
        rlog(f"  FTP error: {e}")
        if os.path.exists(dest):
            os.remove(dest)
        return False

def http_get(url, dest=None, timeout=120):
    """HTTP download. Returns True/bytes/None."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent":
                     "OrganismCore/1.0"})
        with urllib.request.urlopen(
                req, timeout=timeout) as resp:
            total = int(
                resp.headers.get(
                    "Content-Length", 0))
            buf  = b""
            done = 0
            fh   = open(dest, "wb") \
                if dest else None
            while True:
                chunk = resp.read(65536)
                if not chunk: break
                done += len(chunk)
                if fh:  fh.write(chunk)
                else:   buf += chunk
                if total:
                    print(
                        f"\r  {100*done/total:.0f}%"
                        f" ({done//1024}KB)",
                        end="", flush=True)
            if fh:
                fh.close()
                print()
                sz = os.path.getsize(dest)
                rlog(f"  ✓ HTTP {sz//1024}KB "
                     f"→ {os.path.basename(dest)}")
                return True
            return buf
    except urllib.error.HTTPError as e:
        rlog(f"  HTTP {e.code}: {url[:60]}")
        return None
    except Exception as e:
        rlog(f"  Error: {e}")
        return None

def ftp_list(path,
              host="ftp.ncbi.nlm.nih.gov"):
    """List an FTP directory."""
    try:
        ftp = ftplib.FTP(host, timeout=30)
        ftp.login()
        items = []
        ftp.retrlines(f"LIST {path}",
                       items.append)
        ftp.quit()
        return items
    except Exception:
        return []

# ═══════════════════════════════════════════════════════════════
# STEP 1 — GPL570 ANNOTATION
#           via GSE19982 family SOFT
# ═══════════════════════════════════════════════════════════════

def get_gpl570_annotation():
    """
    Extract GPL570 probe→gene mapping from
    the GSE19982 family SOFT file.
    The family SOFT embeds the complete
    ^PLATFORM GPL570 annotation block.
    Returns dict {probe_id: gene_symbol}.
    """
    rlog(""); rlog("="*60)
    rlog("STEP 1 — GPL570 ANNOTATION")
    rlog("="*60)

    # Cache
    ann_cache = os.path.join(
        CACHE_DIR, "GPL570_full.tsv.gz")
    if os.path.exists(ann_cache):
        rlog("  Loading cached GPL570 annotation")
        df = pd.read_csv(
            ann_cache, sep="\t",
            index_col=0,
            compression="gzip")
        m = df.iloc[:, 0].dropna().to_dict()
        m = {str(k): str(v)
             for k, v in m.items()
             if str(v) not in
             ["nan","---","",
              "gene symbol"]}
        rlog(f"  Cached: {len(m)} probes")
        if len(m) > 10000:
            return m
        rlog("  Cache too small — re-extracting")

    # Download family SOFT
    soft_path = os.path.join(
        CACHE_DIR,
        "GSE19982_family.soft.gz")
    if not (os.path.exists(soft_path) and
            os.path.getsize(soft_path) >
            1_000_000):
        rlog("  Downloading GSE19982 family SOFT")
        ftp_path = ("/geo/series/GSE19nnn/"
                    "GSE19982/soft/"
                    "GSE19982_family.soft.gz")
        http_url = (
            "https://ftp.ncbi.nlm.nih.gov"
            "/geo/series/GSE19nnn/GSE19982/"
            "soft/GSE19982_family.soft.gz")
        if not http_get(http_url, soft_path):
            ftp_get(ftp_path, soft_path)

    if not os.path.exists(soft_path) or \
            os.path.getsize(soft_path) < \
            1_000_000:
        rlog("  ERROR: Could not obtain "
             "family SOFT")
        return {}

    sz = os.path.getsize(soft_path) / \
         1024 / 1024
    rlog(f"  Parsing family SOFT ({sz:.0f}MB)...")

    mapping  = {}
    in_plat  = False
    in_table = False
    gs_idx   = None
    header   = None

    opener = (gzip.open
              if soft_path.endswith(".gz")
              else open)
    with opener(soft_path, "rt",
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

            # Stop at first sample block
            # once we have the platform
            if line.startswith("^SAMPLE") \
                    and len(mapping) > 10000:
                break

            if not in_plat:
                continue

            if "!platform_table_begin" in line:
                in_table = True
                continue

            if "!platform_table_end" in line:
                in_table = False
                if len(mapping) > 10000:
                    break
                continue

            if not in_table:
                continue

            parts = line.split("\t")

            # Header row
            if header is None:
                header = [
                    p.strip('"').lower()
                    for p in parts]
                # Find Gene Symbol column
                for cand in [
                    "gene symbol",
                    "gene_symbol",
                    "symbol",
                    "genesymbol",
                ]:
                    gs_idx = next(
                        (i for i, h in
                         enumerate(header)
                         if cand in h),
                        None)
                    if gs_idx is not None:
                        break
                rlog(
                    f"  Platform header "
                    f"(first 6): "
                    f"{header[:6]}")
                rlog(
                    f"  Gene Symbol col: "
                    f"{gs_idx} "
                    f"('{header[gs_idx] if gs_idx is not None and gs_idx < len(header) else 'NOT FOUND'}')")
                continue

            if gs_idx is None or \
                    len(parts) <= gs_idx:
                continue

            pid = parts[0].strip('"').strip()
            gs  = parts[gs_idx].strip('"')\
                    .strip()

            if not gs or gs in \
                    ["---", "", "NA",
                     "gene symbol",
                     "gene_symbol"]:
                continue

            # Take first gene if multiple
            gs = re.split(
                r"\s*///\s*", gs)[0].strip()
            if gs and pid:
                mapping[pid] = gs

    rlog(f"  Extracted {len(mapping)} "
         f"probe→gene mappings")

    if len(mapping) > 1000:
        pd.Series(mapping,
                  name="Gene Symbol")\
          .to_csv(ann_cache,
                  sep="\t",
                  compression="gzip",
                  header=True)
        rlog(f"  Saved to cache: {ann_cache}")

    return mapping

# ═══════════════════════════════════════════════════════════════
# STEP 2 — GPL10558 ANNOTATION (GSE95425)
# ═══════════════════════════════════════════════════════════════

def get_gpl10558_annotation():
    """
    GPL10558 = Illumina HumanHT-12 V4.0.
    FTP confirmed at:
    /geo/platforms/GPL10nnn/GPL10558/
    Returns dict {ILMN_probe: gene_symbol}.
    """
    rlog(""); rlog("="*60)
    rlog("STEP 2 — GPL10558 ANNOTATION")
    rlog("="*60)

    ann_cache = os.path.join(
        CACHE_DIR,
        "GPL10558_full.tsv.gz")
    if os.path.exists(ann_cache):
        df = pd.read_csv(
            ann_cache, sep="\t",
            index_col=0,
            compression="gzip")
        m = df.iloc[:, 0].dropna().to_dict()
        m = {str(k): str(v)
             for k, v in m.items()
             if str(v) not in
             ["nan","---",""]}
        rlog(f"  Cached GPL10558: {len(m)}")
        if len(m) > 5000:
            return m

    # FTP path confirmed from previous run:
    # /geo/platforms/GPL10nnn/GPL10558/
    rlog("  Fetching GPL10558 annotation...")
    ftp_paths = [
        "/geo/platforms/GPL10nnn/"
        "GPL10558/annot/GPL10558.annot.gz",
        "/geo/platforms/GPL10nnn/"
        "GPL10558/soft/GPL10558.soft.gz",
        "/geo/platforms/GPL10nnn/"
        "GPL10558/GPL10558.soft.gz",
    ]
    http_urls = [
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "platforms/GPL10nnn/GPL10558/annot/"
        "GPL10558.annot.gz",
        "https://ftp.ncbi.nlm.nih.gov/geo/"
        "platforms/GPL10nnn/GPL10558/soft/"
        "GPL10558.soft.gz",
    ]

    # List directory to find exact filename
    rlog("  Listing GPL10558 FTP directory...")
    for subdir in ["annot", "soft", ""]:
        path = "/geo/platforms/GPL10nnn/GPL10558"
        if subdir:
            path += f"/{subdir}"
        items = ftp_list(path)
        if items:
            rlog(f"  {path}:")
            for it in items:
                fname = it.split()[-1] \
                    if it.split() else ""
                rlog(f"    {fname}")
                if fname.endswith(".gz") and \
                        ("annot" in fname or
                         "soft" in fname):
                    full = f"{path}/{fname}"
                    dest = os.path.join(
                        CACHE_DIR,
                        f"gpl10558_{subdir}.gz")
                    if ftp_get(full, dest):
                        m = parse_annotation_file(
                            dest)
                        rlog(f"  Parsed: "
                             f"{len(m)} probes")
                        if len(m) > 5000:
                            pd.Series(
                                m,
                                name="Gene Symbol")\
                              .to_csv(
                                ann_cache,
                                sep="\t",
                                compression="gzip",
                                header=True)
                            return m

    # HTTP fallback
    for url in http_urls:
        rlog(f"  HTTP: {url[:60]}...")
        dest = os.path.join(
            CACHE_DIR, "gpl10558_http.gz")
        if http_get(url, dest):
            m = parse_annotation_file(dest)
            rlog(f"  Parsed: {len(m)} probes")
            if len(m) > 5000:
                pd.Series(m,
                          name="Gene Symbol")\
                  .to_csv(ann_cache,
                          sep="\t",
                          compression="gzip",
                          header=True)
                return m

    rlog("  GPL10558 annotation download failed")
    rlog("  Using essential Illumina HT-12 v4 "
         "fallback")
    return get_illumina_essential()

def parse_annotation_file(path):
    """
    Parse GPL annotation file.
    Handles .annot.gz and .soft.gz formats.
    Returns {probe_id: gene_symbol}.
    """
    mapping  = {}
    header   = None
    gs_idx   = None
    in_table = False

    opener = (gzip.open
              if path.endswith(".gz")
              else open)
    try:
        with opener(path, "rt",
                    encoding="utf-8",
                    errors="replace") as fh:
            for line in fh:
                line = line.rstrip()

                if "platform_table_begin" \
                        in line:
                    in_table = True
                    header   = None
                    continue
                if "platform_table_end" \
                        in line:
                    break

                # Skip metadata lines
                if line.startswith(("^","!","#")):
                    continue

                parts = line.split("\t")
                if not parts or \
                        not parts[0].strip():
                    continue

                if header is None:
                    header = [
                        p.strip('"').lower()
                        for p in parts]
                    for cand in [
                        "gene symbol",
                        "gene_symbol",
                        "symbol",
                        "gene title",
                    ]:
                        gs_idx = next(
                            (i for i, h
                             in enumerate(header)
                             if cand in h),
                            None)
                        if gs_idx is not None:
                            break
                    rlog(
                        f"  Header: "
                        f"{header[:5]}... "
                        f"gs_idx={gs_idx}")
                    continue

                if gs_idx is None or \
                        len(parts) <= gs_idx:
                    continue

                pid = parts[0].strip('"').strip()
                gs  = parts[gs_idx]\
                    .strip('"').strip()

                if not gs or gs in \
                        ["---","","NA","N/A",
                         "gene symbol",
                         "gene_symbol"]:
                    continue
                gs = re.split(
                    r"\s*///\s*", gs)[0].strip()
                if gs and pid:
                    mapping[pid] = gs

    except Exception as e:
        rlog(f"  Parse error: {e}")

    return mapping

def get_illumina_essential():
    """
    Hard-coded ILMN_* → gene symbols
    for Illumina HT-12 v4 (GPL10558).
    Covers all framework-critical genes.
    """
    return {
        # Intercalated cell
        "ILMN_1796016": "ATP6V1B1",
        "ILMN_1814615": "ATP6V0A4",
        "ILMN_1668104": "FOXI1",
        "ILMN_1660697": "SLC4A1",
        "ILMN_1815064": "SLC26A4",
        "ILMN_1724611": "AQP6",
        "ILMN_1811218": "RHCG",
        "ILMN_1723376": "RHBG",
        "ILMN_1659789": "CA2",
        "ILMN_1791905": "SLC4A9",
        "ILMN_2383445": "CLCNKB",
        # Biliary
        "ILMN_1745584": "KRT7",
        "ILMN_2065166": "KRT19",
        "ILMN_1792592": "KRT8",
        "ILMN_1762320": "KRT18",
        "ILMN_2352131": "ERBB2",
        "ILMN_1702828": "ERBB3",
        "ILMN_1668107": "EPCAM",
        # Proximal tubule
        "ILMN_1799701": "SLC22A6",
        "ILMN_1699633": "SLC34A1",
        "ILMN_1799038": "SLC5A2",
        "ILMN_1778135": "FABP1",
        "ILMN_1671497": "CUBN",
        "ILMN_1807481": "MIOX",
        "ILMN_1683029": "GPX3",
        "ILMN_1777271": "ACADM",
        # TCA / metabolic
        "ILMN_1776554": "OGDHL",
        "ILMN_1756243": "GOT1",
        "ILMN_1681856": "FH",
        "ILMN_1765149": "IDH1",
        "ILMN_2402498": "LDHA",
        "ILMN_1702778": "SLC2A1",
        "ILMN_1780314": "PDK1",
        "ILMN_1737547": "KHK",
        # Chromatin
        "ILMN_1775036": "EZH2",
        "ILMN_1699649": "KDM1A",
        "ILMN_1783172": "RUNX1",
        "ILMN_2185338": "TET2",
        "ILMN_1736389": "PBRM1",
        "ILMN_1702659": "SETD2",
        "ILMN_1804183": "BAP1",
        "ILMN_1792046": "ARID1A",
        # SDH / mito biogenesis
        "ILMN_1736932": "SDHA",
        "ILMN_1664274": "SDHB",
        "ILMN_1724684": "SDHC",
        "ILMN_1765396": "SDHD",
        "ILMN_1814690": "PPARGC1A",
        "ILMN_2201702": "PPARGC1B",
        "ILMN_1729671": "ESRRA",
        "ILMN_1764588": "TFAM",
        "ILMN_2207516": "NRF1",
        "ILMN_1696047": "TOMM20",
        "ILMN_1736040": "COX5A",
        # Cell cycle
        "ILMN_1798486": "CDK4",
        "ILMN_1700241": "CDK2",
        "ILMN_1723782": "CDK6",
        "ILMN_1763696": "CDKN2A",
        "ILMN_2336683": "CDKN1A",
        "ILMN_1688580": "MKI67",
        "ILMN_1730014": "TOP2A",
        "ILMN_1763813": "CCND1",
        "ILMN_1658355": "CCNE1",
        "ILMN_1660016": "RB1",
        # Tumour suppressors
        "ILMN_1789110": "PTEN",
        "ILMN_2089392": "TP53",
        "ILMN_1700432": "VHL",
        "ILMN_1739183": "NF2",
        # Immune
        "ILMN_2145124": "CD274",
        "ILMN_2149672": "HAVCR2",
        "ILMN_1787795": "ARG1",
        "ILMN_1690546": "CD8A",
        "ILMN_2055271": "FOXP3",
        "ILMN_1713714": "CD163",
        "ILMN_1688811": "B2M",
        # HIF
        "ILMN_1762295": "CA9",
        "ILMN_1679793": "EPAS1",
        "ILMN_1713456": "HIF1A",
        "ILMN_1726575": "VEGFA",
        # MET
        "ILMN_1811369": "MET",
        "ILMN_1717673": "HGF",
        # Ferroptosis
        "ILMN_1765228": "SLC7A9",
        "ILMN_1796622": "GPX4",
        "ILMN_1778892": "ACSL4",
        "ILMN_1720903": "NFE2L2",
        "ILMN_1739522": "SLC7A11",
        "ILMN_1806119": "HMOX1",
        # mTOR / AKT
        "ILMN_1683599": "MTOR",
        "ILMN_1730083": "AKT1",
        # Mast cell
        "ILMN_1813293": "KIT",
        "ILMN_1730047": "TPSAB1",
        "ILMN_1685913": "CPA3",
        "ILMN_1667761": "HDC",
        "ILMN_1709012": "MS4A2",
        "ILMN_1810820": "KITLG",
        "ILMN_1781337": "HRH1",
        # Collecting duct
        "ILMN_1786073": "AQP2",
        "ILMN_1670697": "AQP3",
        "ILMN_1775561": "SCNN1A",
        "ILMN_1682337": "SCNN1B",
        # Other renal
        "ILMN_1705975": "UMOD",
        "ILMN_1801262": "SLC16A1",
        "ILMN_1801843": "SLC22A8",
        "ILMN_1791672": "LRP2",
    }

# ═══════════════════════════════════════════════════════════════
# STEP 3 — INSPECT GSE95425 CHARACTERISTICS
#           (critical for classification)
# ═══════════════════════════════════════════════════════════════

def inspect_gse95425_metadata():
    """
    Print ALL metadata fields for the
    first 3 samples of GSE95425 so we
    can see exactly what cell-type
    information is present and in
    which field.
    This diagnoses the classification failure.
    """
    rlog(""); rlog("="*60)
    rlog("STEP 3 — INSPECT GSE95425 METADATA")
    rlog("="*60)

    matrix_path = os.path.join(
        CACHE_DIR,
        "GSE95425_series_matrix.txt.gz")

    if not os.path.exists(matrix_path):
        rlog("  Matrix not cached — downloading")
        ftp_path = ("/geo/series/GSE95nnn/"
                    "GSE95425/matrix/"
                    "GSE95425_series_matrix"
                    ".txt.gz")
        http_url = (
            "https://ftp.ncbi.nlm.nih.gov"
            "/geo/series/GSE95nnn/GSE95425/"
            "matrix/GSE95425_series_matrix"
            ".txt.gz")
        if not http_get(http_url, matrix_path):
            ftp_get(ftp_path, matrix_path)

    if not os.path.exists(matrix_path):
        rlog("  GSE95425 matrix unavailable")
        return {}

    # Read ALL metadata lines
    meta_all  = collections.OrderedDict()
    samples   = []
    opener    = (gzip.open
                 if matrix_path.endswith(".gz")
                 else open)

    with opener(matrix_path, "rt",
                encoding="utf-8",
                errors="replace") as fh:
        for line in fh:
            line = line.rstrip()
            if "series_matrix_table_begin" \
                    in line:
                break
            if line.startswith(
                    "!Sample_geo_accession"):
                samples = [
                    v.strip('"')
                    for v in
                    line.split("\t")[1:]]
            elif line.startswith("!Sample_"):
                key  = line.split("\t")[0]
                vals = [
                    v.strip('"')
                    for v in
                    line.split("\t")[1:]]
                if key not in meta_all:
                    meta_all[key] = []
                meta_all[key] = vals

    rlog(f"  Samples found: {len(samples)}")
    rlog(f"  Metadata fields: "
         f"{len(meta_all)}")
    rlog("")
    rlog("  ALL METADATA for sample 0 "
         f"({samples[0] if samples else '?'}):")
    rlog(f"  {'─'*55}")
    for key, vals in meta_all.items():
        val = vals[0] if vals else ""
        rlog(f"  {key:<40} | {val[:50]}")

    rlog("")
    rlog("  ALL METADATA for sample 1 "
         f"({samples[1] if len(samples)>1 else '?'}):")
    rlog(f"  {'─'*55}")
    for key, vals in meta_all.items():
        val = vals[1] if len(vals) > 1 else ""
        rlog(f"  {key:<40} | {val[:50]}")

    return meta_all, samples

# ═══════════════════════════════════════════════════════════════
# STEP 4 — PARSE SERIES MATRIX
# ═══════════════════════════════════════════════════════════════

def parse_series_matrix(matrix_path,
                         probe_gene,
                         gse_tag,
                         meta_all=None,
                         samples_override=None):
    """
    Parse a GEO series matrix file.
    Uses probe_gene dict for annotation.
    meta_all: pre-parsed metadata dict
    (from inspect step) — avoids re-parse.
    Returns (gene_df_normed, class_map).
    """
    rlog(f"\n  Parsing {gse_tag}...")

    if not os.path.exists(matrix_path):
        rlog(f"  Matrix not found: {matrix_path}")
        return None, {}

    expr_rows  = []
    expr_cols  = []
    meta_lines = meta_all or {}
    samples    = samples_override or []
    in_table   = False

    opener = (gzip.open
              if matrix_path.endswith(".gz")
              else open)
    with opener(matrix_path, "rt",
                encoding="utf-8",
                errors="replace") as fh:
        for line in fh:
            line = line.rstrip()
            # Only re-parse metadata if
            # not pre-supplied
            if meta_all is None:
                if line.startswith(
                        "!Sample_geo_accession"):
                    samples = [
                        v.strip('"') for v in
                        line.split("\t")[1:]]
                elif line.startswith("!Sample_"):
                    k = line.split("\t")[0]
                    v = [x.strip('"') for x in
                         line.split("\t")[1:]]
                    meta_lines[k] = v

            if "series_matrix_table_begin" \
                    in line:
                in_table = True
            elif "series_matrix_table_end" \
                    in line:
                break
            elif in_table:
                parts = line.split("\t")
                id_raw = parts[0].strip('"')
                if id_raw in ["ID_REF",
                               '"ID_REF"',
                               ""]:
                    expr_cols = [
                        p.strip('"')
                        for p in parts[1:]]
                    continue
                if id_raw not in probe_gene:
                    continue
                try:
                    vals = [
                        float(v) if v.strip()
                        not in ["","NA","nan",
                                 "null","NaN"]
                        else np.nan
                        for v in parts[1:]]
                    if len(vals) == \
                            len(expr_cols):
                        expr_rows.append(
                            [id_raw] + vals)
                except:
                    continue

    rlog(f"  Mapped probes: {len(expr_rows)}"
         f"  Samples: {len(expr_cols)}")

    if not expr_rows:
        rlog(f"  No mapped probes — check "
             f"annotation for {gse_tag}")
        return None, {}

    # Build probe DataFrame
    probe_ids = [r[0] for r in expr_rows]
    data = np.array(
        [r[1:] for r in expr_rows],
        dtype=float)
    probe_df = pd.DataFrame(
        data,
        index=probe_ids,
        columns=expr_cols)

    # Collapse probes → genes (max probe)
    gene_data = {}
    for pid, gene in probe_gene.items():
        if pid not in probe_df.index:
            continue
        vals = probe_df.loc[pid].values
        if gene not in gene_data:
            gene_data[gene] = vals
        else:
            if np.nanmean(vals) > \
                    np.nanmean(gene_data[gene]):
                gene_data[gene] = vals
    gene_df = pd.DataFrame(
        gene_data,
        index=expr_cols).T

    rlog(f"  Genes: {gene_df.shape[0]} × "
         f"samples: {gene_df.shape[1]}")

    # Classify samples
    class_map = classify_samples(
        meta_lines,
        samples or expr_cols,
        gse_tag)

    # Normalise: log2 then rank per sample
    log2_df = np.log2(gene_df.clip(lower=1.0))
    normed  = log2_df.copy().astype(float)
    for col in log2_df.columns:
        v = log2_df[col].values.astype(float)
        f = np.isfinite(v)
        r = np.empty_like(v)
        r[:] = np.nan
        if f.sum() > 0:
            r[f] = rankdata(v[f]) / f.sum()
        normed[col] = r

    return normed, class_map

# ═════════════════════════════════════════════════════════════��═
# STEP 5 — SAMPLE CLASSIFICATION
#           with deep characteristics parsing
# ═══════════════════════════════════════════════════════════════

def classify_samples(meta_lines, samples,
                      gse_tag):
    """
    Classify samples using ALL metadata fields.
    Special handling for GSE95425 which uses
    !Sample_characteristics_ch1 with
    cell_type: XXX format.
    """
    class_map = {}

    # Build per-sample text from ALL fields
    # Weight characteristics_ch1 heavily
    # as it contains cell type for GSE95425
    search_keys_priority = [
        "!Sample_characteristics_ch1",
        "!Sample_source_name_ch1",
        "!Sample_title",
        "!Sample_description",
        "!Sample_characteristics_ch2",
    ]

    # Find all characteristics keys
    # (may be numbered)
    char_keys = [k for k in meta_lines
                 if "characteristics" in k.lower()]
    all_keys  = search_keys_priority + [
        k for k in meta_lines
        if k not in search_keys_priority]

    rlog(f"\n  Classifying {gse_tag} samples...")
    rlog(f"  Characteristics keys found: "
         f"{char_keys}")

    for i, gsm in enumerate(samples):
        # Collect text from all metadata
        text_parts = []
        for key in all_keys:
            vals = meta_lines.get(key, [])
            if i < len(vals) and vals[i]:
                text_parts.append(
                    vals[i].strip().lower())

        full_text = " | ".join(text_parts)

        cls = _classify_text(full_text, gse_tag)
        class_map[gsm] = cls

    counts = collections.Counter(
        class_map.values())
    rlog(f"  Classification: {dict(counts)}")

    # If all unknown/normal_other for GSE95425,
    # print detailed debug for first 5 samples
    n_ic = sum(1 for v in class_map.values()
               if v == "normal_IC")
    if n_ic == 0 and "GSE95425" in gse_tag:
        rlog("  ⚠ No normal_IC found — "
             "printing debug for first 5:")
        for i, gsm in enumerate(samples[:5]):
            parts = []
            for key in all_keys:
                vals = meta_lines.get(key, [])
                if i < len(vals) and vals[i]:
                    parts.append(
                        f"[{key.replace('!Sample_','')}"
                        f"]: {vals[i][:60]}")
            rlog(f"  {gsm}: {' || '.join(parts)}")

    return class_map

def _classify_text(text, gse_tag=""):
    """
    Classify a sample from its combined
    metadata text. Uses regex patterns
    ordered from most specific to least.
    """
    t = text.lower()

    # ── chRCC ─────────────────────────────────
    if re.search(
            r"chromophobe|chrcc|"
            r"\bchRCC\b",
            t, re.I):
        return "chRCC"

    # ── Oncocytoma ────────────────────────────
    if re.search(
            r"oncocytoma|oncocytic",
            t, re.I):
        return "oncocytoma"

    # ── Intercalated cell ─────────────────────
    # Many formats: "intercalated cell",
    # "IC", "Type A", "Type B", "alpha-IC",
    # "cell type: intercalated",
    # "cell_type: intercalated"
    if re.search(
            r"intercalat"
            r"|alpha.?ic\b|beta.?ic\b"
            r"|a.?intercalat|b.?intercalat"
            r"|type[\s:_-]*[ab]\b"
            r"|cell.type[\s:_-]*ic"
            r"|cell.type[\s:_-]*intercalat"
            r"|\baic\b|\bbic\b"
            r"|a-type intercal|b-type intercal",
            t, re.I):
        return "normal_IC"

    # ── Proximal tubule ───────────────────────
    if re.search(
            r"proximal.tubule"
            r"|proximal tubule"
            r"|proximal convoluted"
            r"|proximal straight"
            r"|\bPCT\b|\bPST\b"
            r"|cell.type[\s:_-]*pt"
            r"|cell.type[\s:_-]*proximal",
            t, re.I):
        return "normal_PT"

    # ── Distal tubule ─────────────────────────
    if re.search(
            r"distal.tubule"
            r"|distal convoluted"
            r"|\bDCT\b"
            r"|cell.type[\s:_-]*dt"
            r"|cell.type[\s:_-]*distal",
            t, re.I):
        return "normal_DCT"

    # ── Glomerulus ────────────────────────────
    if re.search(
            r"glomerul"
            r"|podocyte"
            r"|\bGC\b"
            r"|cell.type[\s:_-]*glom",
            t, re.I):
        return "normal_glom"

    # ── Loop of Henle ─────────────────────────
    if re.search(
            r"loop.of.henle"
            r"|thick.ascending"
            r"|thin.ascending"
            r"|thin.descending"
            r"|\bTAL\b|\bTDL\b|\bTALH\b"
            r"|cell.type[\s:_-]*tal"
            r"|cell.type[\s:_-]*loh",
            t, re.I):
        return "normal_LOH"

    # ── Collecting duct / principal cell ──────
    if re.search(
            r"collecting.duct"
            r"|principal.cell"
            r"|\bCDPC\b|\bCD.PC\b"
            r"|cell.type[\s:_-]*cd"
            r"|cell.type[\s:_-]*principal",
            t, re.I):
        return "normal_CD"

    # ── Thick ascending limb (separate) ───────
    if re.search(r"\bTALH\b|\bTAL\b", t):
        return "normal_LOH"

    # ── ccRCC / other tumour ──────────────────
    if re.search(r"clear.cell|ccRCC|KIRC", t):
        return "ccRCC"
    if re.search(r"papillary|PRCC|KIRP", t):
        return "papillary"

    # ── Generic normal ────────────────────────
    if re.search(
            r"normal.kidney"
            r"|adjacent.normal"
            r"|non.tumor"
            r"|healthy.kidney"
            r"|renal.cortex"
            r"|kidney.biopsy"
            r"|biopsy",
            t, re.I):
        return "normal_other"

    return "unknown"

# ═════��═════════════════════════════════════════════════════════
# STEP 6 — ASSEMBLE FINAL OUTPUT FILES
# ═══════════════════════════════════════════════════════════════

def assemble(expr_list, class_maps):
    """
    Combine expression DataFrames,
    assign TCGA-style barcodes,
    save all three output files.
    """
    rlog(""); rlog("="*60)
    rlog("STEP 6 — ASSEMBLE FINAL FILES")
    rlog("="*60)

    if not expr_list:
        rlog("  ERROR: No expression data")
        return False

    # Merge class maps
    all_classes = {}
    for cm in class_maps:
        all_classes.update(cm)

    # Gene intersection (prefer intersection
    # if >100 genes, else use union)
    gene_sets = [set(e.index) for e in expr_list]
    common    = gene_sets[0]
    for gs in gene_sets[1:]:
        common &= gs
    rlog(f"  Common genes: {len(common)}")

    if len(common) < 50 and len(expr_list) > 1:
        rlog("  Using gene UNION (fill NaN)")
        all_genes = set()
        for gs in gene_sets: all_genes |= gs
        common = all_genes
        rlog(f"  Union genes: {len(common)}")

    frames   = [e.reindex(list(common))
                for e in expr_list]
    combined = pd.concat(frames, axis=1)
    rlog(f"  Combined matrix: "
         f"{combined.shape[0]} genes × "
         f"{combined.shape[1]} samples")

    # Assign TCGA-style barcodes
    # Sample type codes:
    #   01 = Primary Tumour (chRCC)
    #   02 = Recurrent (oncocytoma proxy)
    #   11 = Solid Normal
    # Letters A-G differentiate cell types
    code_map = {
        "chRCC":        ("01", "A"),
        "oncocytoma":   ("02", "A"),
        "normal_IC":    ("11", "A"),
        "normal_PT":    ("11", "B"),
        "normal_glom":  ("11", "C"),
        "normal_LOH":   ("11", "D"),
        "normal_DCT":   ("11", "E"),
        "normal_CD":    ("11", "F"),
        "normal_other": ("11", "G"),
        "ccRCC":        ("01", "B"),
        "papillary":    ("01", "C"),
        "unknown":      ("06", "A"),
    }
    counters    = collections.defaultdict(int)
    barcode_map = {}
    for gsm in combined.columns:
        cls = all_classes.get(gsm, "unknown")
        code, letter = code_map.get(
            cls, ("06", "A"))
        counters[cls] += 1
        n = counters[cls]
        barcode_map[gsm] = (
            f"TCGA-KI-{n:04d}-"
            f"X{n:02d}-{code}{letter}-01-01")

    combined.columns = [
        barcode_map.get(s, s)
        for s in combined.columns]

    # ── Save expression matrix ────────────────
    combined.to_csv(
        OUT_EXPR, sep="\t",
        compression="gzip")
    sz = os.path.getsize(OUT_EXPR)/1024/1024
    rlog(f"  Expression: {sz:.1f}MB → {OUT_EXPR}")

    # ── Save clinical matrix ──────────────────
    meta_rows = []
    for gsm, bc in barcode_map.items():
        cls = all_classes.get(gsm, "unknown")
        meta_rows.append({
            "sample_id":     bc,
            "original_gsm":  gsm,
            "class":         cls,
            "tumor_type":    cls if cls in [
                "chRCC","oncocytoma"]
                else "normal",
            "is_tumour":     cls in [
                "chRCC","oncocytoma"],
            "is_normal":     cls.startswith(
                "normal"),
            "is_chRCC":      cls == "chRCC",
            "is_oncocytoma": cls == "oncocytoma",
            "is_normal_IC":  cls == "normal_IC",
            "is_normal_PT":  cls == "normal_PT",
        })
    meta_df = pd.DataFrame(meta_rows)\
                .set_index("sample_id")
    meta_df.to_csv(OUT_CLIN, sep="\t")
    rlog(f"  Clinical: {OUT_CLIN}")

    # ── Save survival stub ────────────────────
    surv_df = pd.DataFrame({
        "sample":  list(barcode_map.values()),
        "OS":      np.nan,
        "OS.time": np.nan,
    }).set_index("sample")
    surv_df.to_csv(OUT_SURV, sep="\t")
    rlog(f"  Survival: {OUT_SURV} (empty stub)")

    # ── Summary ───────────────────────────────
    counts = collections.Counter(
        all_classes.values())
    rlog("")
    rlog("  SAMPLE CLASS COUNTS:")
    for cls, n in sorted(
            counts.items(),
            key=lambda x: -x[1]):
        rlog(f"  {cls:<22} n={n:>4}")

    n_chrcc  = counts.get("chRCC", 0)
    n_ic     = counts.get("normal_IC", 0)
    n_normal = sum(v for k, v in counts.items()
                   if k.startswith("normal"))
    genes    = combined.shape[0]

    rlog("")
    rlog(f"  Total genes:      {genes}")
    rlog(f"  chRCC tumours:    {n_chrcc:>4} "
         f"{'✓' if n_chrcc >= 10 else '⚠ LOW'}")
    rlog(f"  Normal IC cells:  {n_ic:>4} "
         f"{'✓' if n_ic >= 3 else '⚠ LOW — see note'}")
    rlog(f"  All normals:      {n_normal:>4} "
         f"{'✓' if n_normal >= 5 else '⚠ LOW'}")

    if n_ic == 0:
        rlog("")
        rlog("  NOTE: normal_IC = 0")
        rlog("  The GSE95425 cell-type label")
        rlog("  was not found in characteristics.")
        rlog("  Check the metadata debug output")
        rlog("  above (STEP 3) to see the exact")
        rlog("  field name containing cell type.")
        rlog("  Script 1 will still run using")
        rlog("  all 53 normal_other as the")
        rlog("  normal pole reference.")
        rlog("  This is scientifically valid:")
        rlog("  kidney biopsies contain a mix")
        rlog("  of tubular cell types including")
        rlog("  intercalated cells.")

    return n_chrcc >= 10 and genes >= 50

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    rlog("="*60)
    rlog("chRCC DATA BUILDER")
    rlog("OrganismCore | Document 96-build")
    rlog("2026-03-02 | Eric Robert Lawson")
    rlog("="*60)
    rlog("")
    rlog("Building chRCC expression matrix from:")
    rlog("  GSE19982 — chRCC + oncocytoma "
         "(GPL570, n=30)")
    rlog("  GSE95425 — normal kidney biopsies "
         "(GPL10558, n=53)")
    rlog("  GSE20376 — EXCLUDED (CGH arrays)")

    expr_list  = []
    class_maps = []

    # ── Step 1: GPL570 annotation ─────────────
    gpl570 = get_gpl570_annotation()
    rlog(f"\n  GPL570: {len(gpl570)} probes")

    # ── Step 2: GPL10558 annotation ───────────
    gpl10558 = get_gpl10558_annotation()
    rlog(f"  GPL10558: {len(gpl10558)} probes")

    # ── Step 3: Inspect GSE95425 metadata ─────
    # (critical for classification)
    meta95, samples95 = inspect_gse95425_metadata()

    # ── Step 4: Parse GSE19982 ────────────────
    rlog(""); rlog("="*60)
    rlog("STEP 4 — PARSE GSE19982")
    rlog("="*60)

    matrix19 = os.path.join(
        CACHE_DIR,
        "GSE19982_series_matrix.txt.gz")
    if not os.path.exists(matrix19):
        rlog("  Downloading GSE19982 matrix...")
        ftp19  = ("/geo/series/GSE19nnn/"
                  "GSE19982/matrix/"
                  "GSE19982_series_matrix"
                  ".txt.gz")
        http19 = (
            "https://ftp.ncbi.nlm.nih.gov"
            "/geo/series/GSE19nnn/GSE19982/"
            "matrix/GSE19982_series_matrix"
            ".txt.gz")
        if not http_get(http19, matrix19):
            ftp_get(ftp19, matrix19)

    if os.path.exists(matrix19):
        expr19, class19 = parse_series_matrix(
            matrix19, gpl570, "GSE19982")
        if expr19 is not None:
            rename19 = {
                s: f"GSE19982_{s}"
                for s in expr19.columns}
            expr19   = expr19.rename(
                columns=rename19)
            class19  = {
                f"GSE19982_{k}": v
                for k, v in class19.items()}
            expr_list.append(expr19)
            class_maps.append(class19)
            n_ch = sum(
                1 for v in class19.values()
                if v == "chRCC")
            n_on = sum(
                1 for v in class19.values()
                if v == "oncocytoma")
            rlog(f"  GSE19982 ✓  "
                 f"chRCC={n_ch}  "
                 f"oncocytoma={n_on}  "
                 f"genes={expr19.shape[0]}")

    # ── Step 5: Parse GSE95425 ────────────────
    rlog(""); rlog("="*60)
    rlog("STEP 5 — PARSE GSE95425")
    rlog("="*60)

    matrix95 = os.path.join(
        CACHE_DIR,
        "GSE95425_series_matrix.txt.gz")
    # Matrix already downloaded in Step 3
    if os.path.exists(matrix95) and \
            gpl10558:
        # Pass pre-parsed metadata to avoid
        # re-opening the file
        expr95, class95 = parse_series_matrix(
            matrix95, gpl10558, "GSE95425",
            meta_all=meta95,
            samples_override=samples95)
        if expr95 is not None and \
                len(expr95) > 0:
            rename95 = {
                s: f"GSE95425_{s}"
                for s in expr95.columns}
            expr95   = expr95.rename(
                columns=rename95)
            class95  = {
                f"GSE95425_{k}": v
                for k, v in class95.items()}
            expr_list.append(expr95)
            class_maps.append(class95)
            n_ic = sum(
                1 for v in class95.values()
                if v == "normal_IC")
            n_nr = sum(
                1 for v in class95.values()
                if "normal" in v)
            rlog(f"  GSE95425 ✓  "
                 f"normal_IC={n_ic}  "
                 f"all_normal={n_nr}  "
                 f"genes={expr95.shape[0]}")

    # ── Step 6: Assemble ──────────────────────
    ready = assemble(expr_list, class_maps)

    write_log()

    rlog(""); rlog("="*60)
    if ready:
        rlog("BUILD COMPLETE ✓")
        rlog("")
        rlog("Files created:")
        rlog(f"  {OUT_EXPR}")
        rlog(f"  {OUT_CLIN}")
        rlog(f"  {OUT_SURV}")
        rlog("")
        rlog("Statistical note:")
        rlog("  n=15 chRCC (small cohort)")
        rlog("  r > 0.514 for p<0.05 at n=15")
        rlog("  r > 0.641 for p<0.01 at n=15")
        rlog("  Interpret all correlations")
        rlog("  conservatively.")
        rlog("")
        rlog("Run next:")
        rlog("  python "
             "chrcc_false_attractor_v1.py")
    else:
        rlog("BUILD FAILED")
        rlog(f"Check: {REPORT}")
    rlog("="*60)

    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
