"""
HEPATOCELLULAR CARCINOMA — FALSE ATTRACTOR ANALYSIS
SCRIPT 3
Dataset: TCGA-LIHC
         Downloaded via recount3 / GDC portal
         RNAseq (STAR counts → TPM)
         n≈370 HCC tumours + adjacent normal
         Has: mutation calls, copy number,
              clinical, molecular subtypes,
              immune deconvolution proxy

Doc: 92c | Date: 2026-03-02

SCRIPT 3 TARGETS (locked 2026-03-02):

S3-1: Download TCGA-LIHC data
      Expression: GDC portal or recount3
      Clinical:   GDC clinical XML or
                  TCGAbiolinks-style TSV
      Mutations:  MAF file (MC3 calls)

S3-2: HCC_DEPTH_V2 validation
      Metabolic score from Script 2
      replicated in independent cohort.
      Prediction: metab score predicts
      OS at p<0.01 in TCGA-LIHC.

S3-3: CTNNB1 mutation survival (HCC-P5)
      CTNNB1 exon 3 mutation vs wild-type.
      Prediction: CTNNB1-mutant better OS.
      This is the primary pending test
      from Scripts 1+2.

S3-4: TP53 mutation survival
      TP53 mutant vs wild-type OS.
      Prediction: TP53 mutation worse OS.

S3-5: CTNNB1 mutation vs depth score
      Are CTNNB1-mutant HCCs shallower?
      Prediction: mutant = shallower.

S3-6: Molecular subtype vs depth
      TCGA iCluster subtypes:
        C1: proliferative (poor prognosis)
        C2: metabolic (better prognosis)
        C3: unannotated
      Prediction: C1 deepest, C2 shallowest.

S3-7: Immune infiltration vs depth
      Proxy markers from RNAseq:
        CD8A, CD4, FOXP3, CD68, ARG1
      Prediction: deeper = lower CD8A
      (immune exclusion in false attractor).

S3-8: Depth × mutation interaction
      Do CTNNB1-mutant deep tumours
      have different prognosis from
      CTNNB1-mutant shallow tumours?

S3-9: Cross-cohort comparison
      GSE14520 vs TCGA-LIHC depth
      distributions and survival.

PREDICTIONS LOCKED 2026-03-02:
  S3-P1: Metabolic score predicts TCGA-LIHC
         OS at p<0.01 (replication)
  S3-P2: CTNNB1-mutant better OS than WT
         (HCC-P5 direct test)
  S3-P3: TP53-mutant worse OS than WT
  S3-P4: CTNNB1-mutant HCCs shallower
         (depth < median)
  S3-P5: iCluster C1 deepest, C2 shallowest
  S3-P6: CD8A falls with depth in TCGA-LIHC
  S3-P7: Depth predicts OS in TCGA-LIHC
         independently of stage and grade

Author: Eric Robert Lawson
Framework: OrganismCore
"""

import os
import re
import gzip
import tarfile
import requests
import numpy as np
import pandas as pd
from scipy import stats
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
from lifelines import CoxPHFitter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR    = "./hcc_false_attractor/"
TCGA_DIR    = os.path.join(BASE_DIR, "tcga_lihc/")
RESULTS_DIR = os.path.join(BASE_DIR, "results_s3")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log_s3.txt")
os.makedirs(TCGA_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ============================================================
# TCGA-LIHC DATA SOURCES
#
# Strategy: try three sources in order
#   1. recount3 pre-processed TSV (easiest)
#   2. Xena UCSC browser TSV (no auth)
#   3. GDC portal (requires token for some)
#
# Xena source (no authentication required):
#   Expression: STAR TPM log2(TPM+0.001)
#   Clinical:   phenotype TSV
#   Mutations:  TCGA MC3 somatic MAF
# ============================================================

XENA_BASE = (
    "https://tcga-xena-hub.s3.us-east-1"
    ".amazonaws.com/download/"
)

# Expression matrix (log2 TPM)
EXPR_URL = (
    XENA_BASE
    + "TCGA-LIHC.htseq_fpkm-uq.tsv.gz"
)
EXPR_FILE = os.path.join(
    TCGA_DIR, "TCGA-LIHC.expr.tsv.gz"
)

# Phenotype / clinical
PHENO_URL = (
    XENA_BASE
    + "TCGA-LIHC.GDC_phenotype.tsv.gz"
)
PHENO_FILE = os.path.join(
    TCGA_DIR, "TCGA-LIHC.pheno.tsv.gz"
)

# Survival
SURV_URL = (
    XENA_BASE
    + "TCGA-LIHC.survival.tsv.gz"
)
SURV_FILE = os.path.join(
    TCGA_DIR, "TCGA-LIHC.survival.tsv.gz"
)

# Somatic mutations (MC3)
MUT_URL = (
    XENA_BASE
    + "TCGA-LIHC.mutect2_snv.tsv.gz"
)
MUT_FILE = os.path.join(
    TCGA_DIR, "TCGA-LIHC.mutations.tsv.gz"
)

# Alternative: UCSC Xena public hub
XENA_PUBLIC = (
    "https://tcga.xenahubs.net/download/"
    "TCGA.LIHC.sampleMap/"
)

# ============================================================
# GENES — same 152-gene target list approach
# but now from RNAseq we have full genome
# so we use gene symbols directly
# ============================================================

# HCC_DEPTH_V2 — from Script 2 findings
METAB_SWITCH = [
    "CYP3A4","ALDOB","PCK1","G6PC",
    "CYP2C9","TTR","IGF1","ARG1",
    "APOE","RXRA","PPARA","FGF21",
    "FABP1","ALB","APOB","HNF4A",
]
PROG_FA = [
    "SOX4","PROM1","AFP","EPCAM",
    "CDC20","BIRC5","TOP2A","MKI67",
    "CCNB1","KRT19","EZH2","HDAC2",
]

# Full gene list for analysis
GENES_OF_INTEREST = sorted(set(
    METAB_SWITCH + PROG_FA + [
        "CTNNB1","MYC","MYCN",
        "TP53","ARID1A","AXIN1","AXIN2",
        "RB1","CDKN2A","KEAP1","NFE2L2",
        "PIK3CA","PTEN","TSC1","TSC2",
        "HNF1A","HNF1B","FOXA1","FOXA2",
        "GPC3","GLUL","LGR5","DKK1","DKK4",
        "TBX3","WNT5A","FZD3","RNF43",
        "CCND1","CDK4","CDK6","CCNE1",
        "E2F1","E2F3","AURKA","PLK1",
        "BCL2","MCL1","BAX","BIRC5",
        "MDM2","CDKN1A","CDKN2A",
        "FGFR1","FGFR2","FGFR3","FGFR4",
        "FGF19","KLB","EGFR","ERBB2",
        "MET","KDR","VEGFA","VEGFC",
        "IGF1R","IGF2","IGF2R","INSR",
        "TERT","TGFB1","TGFBR2",
        "SMAD2","SMAD3","SMAD4",
        "SNAI1","SNAI2","TWIST1",
        "ZEB1","ZEB2","CDH1","CDH2",
        "VIM","FN1","CD44","CD90",
        "EED","SUZ12","HDAC1","HDAC3",
        "KDM6A","KDM5C","KDM4A",
        "DNMT3A","DNMT3B","ARID2",
        "SMARCA4","KMT2A","KMT2D",
        "CD274","PDCD1","CD8A","FOXP3",
        "CD4","CD68","TNF","NFKB1",
        "STAT3","JAK1","JAK2","IL6","IL6R",
        "S100A8","S100A9","S100A4",
        "FASN","SCD","ACLY","ACACA",
        "HMGCR","SQLE","LDLR","PPARG",
        "CYP3A4","CYP2C9","CYP7A1",
        "PCK1","G6PC","ALDOB","ARG1",
        "INSR","GCK","ACSL4",
        "KRT7","KRT14","KRT5","TP63",
        "SOX2","SOX9","CD133",
        "MTOR","PIK3CA","AKT1",
        "MLH1","MSH2","MSH6",
        "AURKA","ZEB2","KRT19",
        "HDAC2","DNMT3A","ACLY",
        "PCNA","MCM2","CDC20",
        "CCNB1","CDK4","E2F3",
        "SOX4","SOX9","PROM1",
    ]
))

# ============================================================
# LOGGING
# ============================================================

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

def write_log():
    with open(LOG_FILE, "w") as f:
        f.write("\n".join(log_lines))

def fmt_p(p):
    if p is None or (
        isinstance(p, float) and np.isnan(p)
    ):
        return "p=N/A     "
    if p < 0.001:  return f"p={p:.2e} ***"
    elif p < 0.01: return f"p={p:.2e}  **"
    elif p < 0.05: return f"p={p:.4f}   *"
    else:          return f"p={p:.4f}  ns"

def safe_pearsonr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 5:
        return np.nan, np.nan
    return stats.pearsonr(x, y)

def safe_mwu(a, b, alt="two-sided"):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    return stats.mannwhitneyu(
        a, b, alternative=alt
    )

def norm01(arr):
    arr = np.asarray(arr, dtype=float)
    mn  = np.nanmin(arr)
    mx  = np.nanmax(arr)
    if mx > mn:
        return (arr - mn) / (mx - mn)
    return np.full_like(arr, 0.5)

def logrank_p(t1, e1, t0, e0):
    t1 = np.asarray(t1, dtype=float)
    e1 = np.asarray(e1, dtype=float)
    t0 = np.asarray(t0, dtype=float)
    e0 = np.asarray(e0, dtype=float)
    m1 = np.isfinite(t1) & np.isfinite(e1) & (t1 > 0)
    m0 = np.isfinite(t0) & np.isfinite(e0) & (t0 > 0)
    if m1.sum() < 5 or m0.sum() < 5:
        return np.nan
    try:
        res = logrank_test(
            t1[m1], t0[m0],
            e1[m1], e0[m0],
        )
        return res.p_value
    except Exception:
        return np.nan

# ============================================================
# DOWNLOAD
# ============================================================

def download(url, dest, label=""):
    if os.path.exists(dest):
        sz = os.path.getsize(dest)
        log(f"  Already present: {dest} "
            f"({sz:,} bytes)")
        return True
    log(f"  Downloading {label}...")
    log(f"  URL: {url}")
    try:
        r = requests.get(
            url, timeout=600, stream=True,
            headers={
                "User-Agent":
                "Mozilla/5.0 OrganismCore/1.0"
            },
        )
        if r.status_code == 200:
            with open(dest, "wb") as f:
                for chunk in r.iter_content(
                    chunk_size=1024*1024
                ):
                    f.write(chunk)
            sz = os.path.getsize(dest)
            log(f"  Saved: {dest} ({sz:,} bytes)")
            return True
        log(f"  HTTP {r.status_code} for {url}")
        return False
    except Exception as e:
        log(f"  Error: {e}")
        return False

def try_download_multi(url_list, dest, label):
    """Try multiple URLs for same file."""
    if os.path.exists(dest):
        sz = os.path.getsize(dest)
        log(f"  Already present: {dest} "
            f"({sz:,} bytes)")
        return True
    for url in url_list:
        ok = download(url, dest, label)
        if ok and os.path.getsize(dest) > 1000:
            return True
        if os.path.exists(dest):
            os.remove(dest)
    return False

# ============================================================
# PARSE EXPRESSION MATRIX
# Xena format: rows=genes, cols=samples
# First col = Ensembl ID or gene symbol
# ============================================================

def parse_expression(expr_file):
    log("")
    log("=" * 65)
    log("PARSE EXPRESSION MATRIX")
    log(f"  File: {expr_file}")
    log("=" * 65)

    opener = (
        gzip.open(expr_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if expr_file.endswith(".gz")
        else open(expr_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    sample_ids  = []
    gene_data   = {}
    header_done = False
    n_rows      = 0
    genes_wanted = set(GENES_OF_INTEREST)

    with opener as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue

            parts = line.split("\t")

            if not header_done:
                # Header: first col = gene id label
                sample_ids = [
                    p.strip()
                    for p in parts[1:]
                ]
                header_done = True
                log(f"  Samples: {len(sample_ids)}")
                log(f"  IDs[0:3]: "
                    f"{sample_ids[:3]}")
                continue

            gene_raw = parts[0].strip()

            # Handle Ensembl IDs (ENSG00000...)
            # Xena often uses Ensembl; strip version
            gene = gene_raw.split(".")[0]

            # Try direct symbol match first
            if gene not in genes_wanted:
                # Try stripping quotes
                gene_clean = gene.strip('"')
                if gene_clean in genes_wanted:
                    gene = gene_clean
                else:
                    continue

            try:
                vals = [
                    float(p) if p not in [
                        "","NA","nan","NaN","NULL"
                    ]
                    else np.nan
                    for p in parts[1:]
                ]
            except ValueError:
                continue

            if gene not in gene_data:
                gene_data[gene] = vals
            else:
                # Keep highest variance probe
                existing = np.array(
                    gene_data[gene], dtype=float
                )
                new_v    = np.array(vals, dtype=float)
                if (np.nanvar(new_v)
                        > np.nanvar(existing)):
                    gene_data[gene] = vals

            n_rows += 1

    log(f"  Rows read: {n_rows}")
    log(f"  Genes matched: {len(gene_data)}")

    if len(gene_data) == 0:
        log("  WARNING: No genes matched by symbol.")
        log("  File may use Ensembl IDs.")
        log("  Will attempt Ensembl→symbol mapping.")
        return None, sample_ids, True

    n_s = len(sample_ids)
    df  = pd.DataFrame(
        {g: v[:n_s] for g, v in gene_data.items()},
        dtype=float,
    )
    log(f"  Matrix shape: {df.shape}")

    return df, sample_ids, False

# ============================================================
# PARSE EXPRESSION WITH ENSEMBL IDs
# If gene symbols not found, re-read and
# map Ensembl → symbol using a minimal
# lookup from the file itself (gene names
# are sometimes in a separate column)
# ============================================================

def parse_expression_ensembl(expr_file):
    """
    Fallback parser for Ensembl ID format.
    Reads all rows, builds Ensembl→gene map
    from the data file if gene name column
    exists, otherwise uses a hardcoded
    Ensembl ID map for our target genes.
    """
    log("")
    log("  Trying Ensembl ID parsing...")

    # Minimal Ensembl ID map for target genes
    # These are GRCh38 stable IDs
    ENSEMBL_MAP = {
        "ENSG00000148795": "CYP3A4",
        "ENSG00000166571": "ALDOB",
        "ENSG00000126544": "PCK1",
        "ENSG00000131482": "G6PC",
        "ENSG00000138109": "CYP2C9",
        "ENSG00000118271": "TTR",
        "ENSG00000017427": "IGF1",
        "ENSG00000118520": "ARG1",
        "ENSG00000130203": "APOE",
        "ENSG00000186350": "RXRA",
        "ENSG00000186951": "PPARA",
        "ENSG00000105550": "FGF21",
        "ENSG00000164093": "FABP1",
        "ENSG00000163631": "ALB",
        "ENSG00000084674": "APOB",
        "ENSG00000101076": "HNF4A",
        "ENSG00000124664": "SOX4",  # Note: verify
        "ENSG00000007350": "PROM1",
        "ENSG00000081051": "AFP",
        "ENSG00000119888": "EPCAM",
        "ENSG00000094880": "CDC20",
        "ENSG00000177084": "BIRC5",
        "ENSG00000131747": "TOP2A",
        "ENSG00000148773": "MKI67",
        "ENSG00000134057": "CCNB1",
        "ENSG00000171223": "KRT19",
        "ENSG00000106462": "EZH2",
        "ENSG00000068024": "HDAC2",
        "ENSG00000168036": "CTNNB1",
        "ENSG00000136997": "MYC",
        "ENSG00000141510": "TP53",
        "ENSG00000117713": "ARID1A",
        "ENSG00000103126": "AXIN1",
        "ENSG00000168646": "AXIN2",
        "ENSG00000057663": "RNF43",
        "ENSG00000105851": "PIK3CA",
        "ENSG00000171862": "PTEN",
        "ENSG00000135679": "MDM2",
        "ENSG00000105329": "TGFB1",
        "ENSG00000166033": "HTRA1",
        "ENSG00000138395": "CDK15",
        "ENSG00000077721": "ARID2",
        "ENSG00000073910": "FRY",
        "ENSG00000116062": "MSH6",
        "ENSG00000115414": "FN1",
        "ENSG00000092820": "EZR",
        "ENSG00000116791": "CRYZ",
        "ENSG00000171823": "FBXL11",
        "ENSG00000139618": "BRCA2",
        "ENSG00000012048": "BRCA1",
        "ENSG00000141736": "ERBB2",
        "ENSG00000146648": "EGFR",
        "ENSG00000110803": "FGFR4",
        "ENSG00000077782": "FGFR1",
        "ENSG00000066468": "FGFR2",
        "ENSG00000068078": "FGFR3",
        "ENSG00000157404": "KIT",
        "ENSG00000128052": "KDR",
        "ENSG00000112715": "VEGFA",
        "ENSG00000150291": "VEGFC",
        "ENSG00000122025": "FLT3",
        "ENSG00000105976": "MET",
        "ENSG00000067048": "DDX3Y",
        "ENSG00000102144": "PGK1",
        "ENSG00000162188": "GPC3",
        "ENSG00000168685": "IL7R",
        "ENSG00000168484": "SFTPB",
        "ENSG00000196139": "AKR1C3",
        "ENSG00000187486": "LDHA",
        "ENSG00000111640": "GAPDH",
        "ENSG00000159111": "MYDGF",
        "ENSG00000116815": "CD44",
        "ENSG00000133110": "POSTN",
        "ENSG00000164692": "COL1A2",
        "ENSG00000115461": "IGFBP5",
        "ENSG00000135046": "ANXA1",
        "ENSG00000148400": "NOTCH1",
        "ENSG00000162736": "NCSTN",
        "ENSG00000115884": "SDC1",
        "ENSG00000065361": "ATP7B",
        "ENSG00000107404": "DVL1",
        "ENSG00000082438": "COBLL1",
        "ENSG00000169562": "GLS2",
        "ENSG00000180370": "PAK2",
        "ENSG00000100030": "MAPK1",
        "ENSG00000145050": "MANF",
        "ENSG00000197905": "GLUL",
        "ENSG00000183044": "ABAT",
        "ENSG00000100764": "PCSK1",
        "ENSG00000107159": "CA9",
        "ENSG00000136244": "IL6",
        "ENSG00000160712": "IL6R",
        "ENSG00000115415": "STAT1",
        "ENSG00000168610": "STAT3",
        "ENSG00000177885": "GRB2",
        "ENSG00000170458": "CD14",
        "ENSG00000010610": "CD4",
        "ENSG00000153563": "CD8A",
        "ENSG00000019582": "CD68",
        "ENSG00000049249": "TNFRSF9",
        "ENSG00000188389": "PDCD1",
        "ENSG00000120217": "CD274",
        "ENSG00000049768": "FOXP3",
        "ENSG00000117560": "FASLG",
        "ENSG00000100644": "HIF1A",
        "ENSG00000087245": "MMP2",
        "ENSG00000145113": "MMP14",
        "ENSG00000179091": "CYB5A",
        "ENSG00000007047": "MARK4",
        "ENSG00000111679": "PTPN6",
        "ENSG00000143631": "FGB",
        "ENSG00000132693": "CRP",
        "ENSG00000163359": "COL6A3",
        "ENSG00000168002": "GINS2",
        "ENSG00000135679": "MDM2",
        "ENSG00000085741": "WNT11",
        "ENSG00000108379": "WNT3",
        "ENSG00000112599": "SMAD2",
        "ENSG00000166949": "SMAD3",
        "ENSG00000141646": "SMAD4",
        "ENSG00000122691": "TWIST1",
        "ENSG00000148516": "ZEB1",
        "ENSG00000169554": "ZEB2",
        "ENSG00000039068": "CDH1",
        "ENSG00000170558": "CDH2",
        "ENSG00000026025": "VIM",
        "ENSG00000067955": "CBFB",
        "ENSG00000073282": "TP63",
        "ENSG00000037474": "NSUN2",
        "ENSG00000101213": "PTPRT",
        "ENSG00000099985": "OSM",
        "ENSG00000135547": "HDAC1",
        "ENSG00000023287": "RB1CC1",
        "ENSG00000147889": "CDKN2A",
        "ENSG00000124762": "CDKN1A",
        "ENSG00000105173": "CCNE1",
        "ENSG00000134308": "YWHAQ",
        "ENSG00000163514": "IL17RC",
        "ENSG00000005893": "LAMP2",
        "ENSG00000075426": "FOXA2",
        "ENSG00000129514": "FOXA1",
        "ENSG00000130294": "KIF1A",
        "ENSG00000181195": "PENK",
        "ENSG00000148737": "TCF7L2",
        "ENSG00000177606": "JUN",
        "ENSG00000125868": "DUSP5",
        "ENSG00000185917": "SFRP1",
        "ENSG00000007372": "PAX6",
        "ENSG00000118513": "MYB",
        "ENSG00000105939": "ZC3H12A",
        "ENSG00000116704": "SLC2A2",
        "ENSG00000010292": "NCAPD2",
        "ENSG00000099860": "GADD45B",
        "ENSG00000174307": "PHLDA1",
        "ENSG00000062485": "CS",
        "ENSG00000145692": "BHMT",
        "ENSG00000148180": "GSN",
        "ENSG00000108309": "RUNDC1",
        "ENSG00000140443": "IGF1R",
        "ENSG00000167244": "IGF2",
        "ENSG00000197081": "IGF2R",
        "ENSG00000171105": "INSR",
        "ENSG00000079689": "SCNN1A",
        "ENSG00000197380": "DYRK4",
        "ENSG00000171560": "FGA",
        "ENSG00000198518": "AMBP",
        "ENSG00000117601": "SERPINC1",
        "ENSG00000117601": "SERPINC1",
        "ENSG00000172201": "ID4",
        "ENSG00000196188": "CLDN5",
        "ENSG00000164754": "RAD54B",
        "ENSG00000173599": "PC",
        "ENSG00000106631": "MYL7",
        "ENSG00000141504": "DHCR7",
        "ENSG00000064932": "SBNO2",
        "ENSG00000138795": "LEF1",
        "ENSG00000057657": "PRDM1",
        "ENSG00000135148": "TRADD",
        "ENSG00000078808": "SFN",
        "ENSG00000013810": "TACC3",
        "ENSG00000152217": "SETBP1",
        "ENSG00000100867": "DHRS2",
        "ENSG00000108849": "PTTG2",
        "ENSG00000198670": "HBA1",
        "ENSG00000163737": "CXCL1",
        "ENSG00000109046": "WSB1",
        "ENSG00000095139": "ARCN1",
        "ENSG00000065534": "MYLK",
        "ENSG00000106541": "AGR2",
        "ENSG00000196188": "CLDN5",
        "ENSG00000073849": "ST6GAL1",
        "ENSG00000159111": "MYDGF",
        "ENSG00000074181": "NOTCH3",
        "ENSG00000138131": "LOXL4",
        "ENSG00000105048": "TNNT1",
        "ENSG00000108256": "COLGALT1",
        "ENSG00000160285": "LMAN2",
        "ENSG00000139793": "MBNL2",
        "ENSG00000107954": "NEURL1",
        "ENSG00000054965": "FAM168A",
        "ENSG00000130958": "TULP3",
        "ENSG00000136826": "KLF4",
        "ENSG00000124216": "SNAI1",
        "ENSG00000019549": "SNAI2",
        "ENSG00000139083": "ETV4",
        "ENSG00000184956": "PROM2",
        "ENSG00000171766": "GATM",
        "ENSG00000147648": "ECHDC3",
        "ENSG00000058866": "PHGDH",
        "ENSG00000163811": "WDR12",
        "ENSG00000148153": "NHLRC3",
        "ENSG00000172115": "CYCS",
        "ENSG00000197442": "MAP3K5",
        "ENSG00000007372": "PAX6",
        "ENSG00000197291": "STXBP6",
        "ENSG00000159399": "HK2",
        "ENSG00000159111": "MYDGF",
        "ENSG00000197142": "ACSL5",
        "ENSG00000118137": "APOA1",
        "ENSG00000130176": "CNN1",
        "ENSG00000145022": "ANPEP",
        "ENSG00000171084": "FAM3C",
        "ENSG00000154719": "MRPS36",
        "ENSG00000162873": "KLHDC8A",
        "ENSG00000197122": "SRC",
        "ENSG00000152582": "SPTA1",
        "ENSG00000064835": "POU2F1",
        "ENSG00000177606": "JUN",
        "ENSG00000107104": "KANK1",
        "ENSG00000196188": "CLDN5",
        "ENSG00000213741": "RPS29",
        "ENSG00000204287": "HLA-DRA",
        "ENSG00000204592": "HLA-E",
        "ENSG00000204525": "HLA-C",
        "ENSG00000223960": "SCARNA8",
        "ENSG00000160285": "LMAN2",
        "ENSG00000118058": "KMT2A",
        "ENSG00000167548": "KMT2D",
        "ENSG00000089902": "RCOR1",
        "ENSG00000007312": "CD79B",
        "ENSG00000185479": "KRT8",
        "ENSG00000171345": "KRT19",
        "ENSG00000205336": "ADGRB1",
        "ENSG00000150093": "ITGB1",
        "ENSG00000132170": "PPARG",
        "ENSG00000092978": "ACAT2",
        "ENSG00000086827": "ZW10",
        "ENSG00000071655": "MBD3",
        "ENSG00000205837": "MBD2",
        "ENSG00000144381": "HSPD1",
        "ENSG00000173166": "RAPH1",
        "ENSG00000143153": "ATP1B1",
        "ENSG00000148926": "ADM",
        "ENSG00000159111": "MYDGF",
        "ENSG00000180817": "PPA1",
        "ENSG00000138162": "TAOK2",
        "ENSG00000053900": "ANAMORSIN",
        "ENSG00000163931": "TKT",
        "ENSG00000004468": "CD38",
        "ENSG00000143727": "ATP1A1",
        "ENSG00000113580": "NR3C1",
        "ENSG00000117318": "ID3",
        "ENSG00000172216": "CEBPB",
        "ENSG00000156234": "CXCL13",
        "ENSG00000108690": "CXCL9",
        "ENSG00000125538": "IL1B",
        "ENSG00000163235": "TGFB2",
        "ENSG00000049768": "FOXP3",
        "ENSG00000188290": "HES4",
        "ENSG00000120738": "EGR1",
        "ENSG00000150764": "DIXDC1",
        "ENSG00000172794": "RAB7B",
        "ENSG00000106799": "TGFBR1",
        "ENSG00000163513": "TGFBR2",
        "ENSG00000072818": "ACVR1",
        "ENSG00000151090": "THRB",
        "ENSG00000117601": "SERPINC1",
        "ENSG00000133048": "CHI3L1",
        "ENSG00000105810": "CDK6",
        "ENSG00000135446": "CDK4",
        "ENSG00000123374": "CDK2",
        "ENSG00000164885": "CDKN3",
        "ENSG00000110092": "CCND1",
        "ENSG00000112576": "CCND2",
        "ENSG00000112742": "TTK",
        "ENSG00000007171": "NOS2",
        "ENSG00000111046": "MYF6",
        "ENSG00000196730": "DAPK1",
        "ENSG00000108963": "DPP9",
        "ENSG00000183287": "CCBE1",
        "ENSG00000130203": "APOE",
        "ENSG00000107562": "CXCL12",
        "ENSG00000198670": "HBA1",
        "ENSG00000091482": "TNFSF9",
        "ENSG00000091879": "ANGPT2",
        "ENSG00000117461": "PIK3R3",
        "ENSG00000108384": "RAD51",
        "ENSG00000166033": "HTRA1",
        "ENSG00000177606": "JUN",
        "ENSG00000099860": "GADD45B",
        "ENSG00000162924": "REG3A",
        "ENSG00000102243": "HSPB8",
        "ENSG00000189013": "KIF26A",
        "ENSG00000154236": "LSAMP",
        "ENSG00000110713": "NME1",
        "ENSG00000186462": "NAA11",
        "ENSG00000168036": "CTNNB1",
        "ENSG00000081059": "TCF7",
        "ENSG00000148737": "TCF7L2",
        "ENSG00000154370": "TCF7L1",
        "ENSG00000071127": "DVL1",
        "ENSG00000172349": "IL16",
        "ENSG00000049249": "TNFRSF9",
        "ENSG00000078487": "ZZEF1",
        "ENSG00000113522": "RAD51C",
        "ENSG00000156675": "RAB11FIP1",
        "ENSG00000143401": "ANP32A",
        "ENSG00000100867": "DHRS2",
        "ENSG00000197442": "MAP3K5",
        "ENSG00000204983": "PRSS1",
        "ENSG00000073614": "KDM5A",
        "ENSG00000196591": "HDAC2",
        "ENSG00000130055": "GDPD5",
        "ENSG00000138175": "ARL3",
        "ENSG00000175061": "COX5B",
        "ENSG00000168282": "MGMT",
        "ENSG00000064655": "EYA2",
        "ENSG00000075651": "PLD1",
        "ENSG00000065413": "ANKRD44",
        "ENSG00000188501": "LRRC15",
        "ENSG00000133116": "KL",
        "ENSG00000144218": "AFF3",
        "ENSG00000157322": "CLEC18A",
        "ENSG00000243468": "LINC01116",
        "ENSG00000105610": "KLF5",
        "ENSG00000143878": "RHOB",
        "ENSG00000168496": "FEN1",
        "ENSG00000163913": "CDC25A",
        "ENSG00000178229": "ZNF826P",
        "ENSG00000143376": "SNX15",
        "ENSG00000089063": "SLC8A1",
        "ENSG00000197892": "KIF13B",
        "ENSG00000164327": "RICTOR",
        "ENSG00000085063": "CD59",
        "ENSG00000134262": "AP4B1",
        "ENSG00000011465": "DCN",
        "ENSG00000084234": "APLP2",
        "ENSG00000130528": "PTPN13",
        "ENSG00000131408": "VDR",
        "ENSG00000012061": "ERCC1",
        "ENSG00000197442": "MAP3K5",
        "ENSG00000076321": "KLHL20",
        "ENSG00000144401": "USE1",
        "ENSG00000148180": "GSN",
        "ENSG00000170759": "KIF5B",
        "ENSG00000148600": "CDHR1",
        "ENSG00000019505": "SYT9",
        "ENSG00000163517": "FLVCR1",
        "ENSG00000186439": "TRDN",
        "ENSG00000124571": "XPO5",
        "ENSG00000183878": "UTY",
        "ENSG00000099337": "KCNB1",
        "ENSG00000158528": "PPP1R9A",
        "ENSG00000100767": "PAPLN",
        "ENSG00000055208": "TAB2",
        "ENSG00000117122": "MFAP2",
        "ENSG00000117601": "SERPINC1",
        "ENSG00000101017": "CD40",
        "ENSG00000138615": "CILK1",
        "ENSG00000113013": "HSPA9",
        "ENSG00000159111": "MYDGF",
        "ENSG00000089116": "RCAN2",
        "ENSG00000162104": "ADCY9",
        "ENSG00000197442": "MAP3K5",
        "ENSG00000117461": "PIK3R3",
        "ENSG00000151291": "TOM1L2",
        "ENSG00000164530": "PI3",
        "ENSG00000110104": "CCDC86",
        "ENSG00000196557": "CACNA1H",
        "ENSG00000160285": "LMAN2",
        "ENSG00000128050": "PAICS",
        "ENSG00000108984": "MAP2K6",
        "ENSG00000162188": "GPC3",
        "ENSG00000106682": "WNT5A",
        "ENSG00000108375": "RNF43",
        "ENSG00000185920": "PTCH1",
        "ENSG00000124664": "SOX4",
        "ENSG00000091831": "ESR1",
        "ENSG00000141738": "GRB7",
        "ENSG00000196714": "CELF2",
        "ENSG00000113140": "SPARC",
        "ENSG00000138081": "FBXO11",
        "ENSG00000138083": "FBXO43",
        "ENSG00000196776": "CD47",
        "ENSG00000159111": "MYDGF",
        "ENSG00000196652": "ZBTB17",
        "ENSG00000137309": "HMGA1",
        "ENSG00000149485": "FADS1",
        "ENSG00000168484": "SFTPB",
        "ENSG00000101109": "STK4",
        "ENSG00000117601": "SERPINC1",
        "ENSG00000176396": "EID3",
        "ENSG00000168291": "PDHB",
        "ENSG00000204568": "MICB",
        "ENSG00000163348": "PYGO2",
        "ENSG00000113649": "BCAM",
        "ENSG00000168002": "GINS2",
        "ENSG00000182220": "ATP6AP2",
        "ENSG00000164815": "ORC5",
        "ENSG00000135390": "ATP5F1E",
        "ENSG00000166033": "HTRA1",
        "ENSG00000143217": "CLDN7",
        "ENSG00000095832": "SLC7A1",
        "ENSG00000100092": "SH3BP1",
        "ENSG00000114126": "TFDP2",
        "ENSG00000130558": "OLFM1",
        "ENSG00000131981": "LGALS3",
        "ENSG00000158286": "RNF13",
        "ENSG00000082212": "ME2",
        "ENSG00000138336": "TET1",
        "ENSG00000168769": "TET2",
        "ENSG00000187605": "TET3",
        "ENSG00000117318": "ID3",
        "ENSG00000162772": "ATF3",
        "ENSG00000149150": "SLC43A1",
        "ENSG00000004455": "AK2",
        "ENSG00000184445": "KNTC1",
        "ENSG00000183576": "SETD1A",
        "ENSG00000181555": "SETD2",
        "ENSG00000197780": "TAF13",
        "ENSG00000166033": "HTRA1",
        "ENSG00000184156": "KCNQ3",
        "ENSG00000197442": "MAP3K5",
        "ENSG00000083635": "NRXN3",
        "ENSG00000116285": "ERRFI1",
        "ENSG00000067704": "IARS2",
        "ENSG00000080839": "RBL1",
        "ENSG00000166033": "HTRA1",
        "ENSG00000103647": "CAND1",
        "ENSG00000117601": "SERPINC1",
        "ENSG00000160285": "LMAN2",
        "ENSG00000150961": "SEC24D",
        "ENSG00000180803": "SPRY3",
        "ENSG00000197442": "MAP3K5",
        "ENSG00000204843": "DCTN1",
        "ENSG00000145687": "SSBP2",
        "ENSG00000141956": "PRDM15",
        "ENSG00000159111": "MYDGF",
        "ENSG00000140451": "PIF1",
        "ENSG00000160285": "LMAN2",
        "ENSG00000073756": "PTGS2",
        "ENSG00000138207": "RBP4",
        "ENSG00000100031": "GGH",
        "ENSG00000169684": "CHRNA5",
        "ENSG00000188229": "TUBB4A",
        "ENSG00000109610": "SOD3",
        "ENSG00000111640": "GAPDH",
        "ENSG00000153774": "CFDP1",
        "ENSG00000164132": "ATG5",
        "ENSG00000163904": "SENP2",
        "ENSG00000159111": "MYDGF",
        "ENSG00000164867": "NOS3",
        "ENSG00000159111": "MYDGF",
        "ENSG00000197442": "MAP3K5",
        "ENSG00000117601": "SERPINC1",
        "ENSG00000102003": "SYP",
        "ENSG00000104131": "EIF3J",
        "ENSG00000165794": "SRSF11",
        "ENSG00000173992": "CDA",
        "ENSG00000135148": "TRADD",
        "ENSG00000164306": "PRIMPOL",
        "ENSG00000107551": "ADORA1",
        "ENSG00000189367": "RAVER2",
        "ENSG00000196188": "CLDN5",
        "ENSG00000143248": "HSD17B6",
        "ENSG00000081138": "CDH6",
        "ENSG00000123358": "NR4A1",
        "ENSG00000159111": "MYDGF",
        "ENSG00000134873": "CLDN10",
        "ENSG00000008226": "DLEC1",
        "ENSG00000197442": "MAP3K5",
        "ENSG00000063046": "EIF4B",
        "ENSG00000125834": "STX4",
    }

    opener = (
        gzip.open(expr_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if expr_file.endswith(".gz")
        else open(expr_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    sample_ids  = []
    gene_data   = {}
    header_done = False
    n_matched   = 0
    n_rows      = 0

    with opener as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if not header_done:
                sample_ids = [
                    p.strip() for p in parts[1:]
                ]
                header_done = True
                continue

            ensembl_raw = parts[0].strip()
            ensembl     = ensembl_raw.split(".")[0]
            gene        = ENSEMBL_MAP.get(ensembl)

            n_rows += 1
            if gene is None:
                continue
            if gene not in set(GENES_OF_INTEREST):
                continue

            try:
                vals = [
                    float(p) if p not in [
                        "","NA","nan","NaN","NULL"
                    ]
                    else np.nan
                    for p in parts[1:]
                ]
            except ValueError:
                continue

            if gene not in gene_data:
                gene_data[gene] = vals
                n_matched += 1
            else:
                existing = np.array(
                    gene_data[gene], dtype=float
                )
                new_v    = np.array(vals, dtype=float)
                if (np.nanvar(new_v)
                        > np.nanvar(existing)):
                    gene_data[gene] = vals

    log(f"  Total rows: {n_rows}")
    log(f"  Genes matched (Ensembl): {n_matched}")

    if len(gene_data) == 0:
        log("  FATAL: No genes matched by "
            "Ensembl ID either.")
        log("  First 5 gene IDs in file:")
        # Re-scan first few lines to diagnose
        opener2 = (
            gzip.open(expr_file, "rt",
                      encoding="utf-8",
                      errors="ignore")
            if expr_file.endswith(".gz")
            else open(expr_file, "r",
                      encoding="utf-8",
                      errors="ignore")
        )
        skip = True
        count = 0
        with opener2 as f:
            for line in f:
                if skip:
                    skip = False
                    continue
                log(f"    {line.split(chr(9))[0]}")
                count += 1
                if count >= 5:
                    break
        return None, sample_ids

    n_s = len(sample_ids)
    df  = pd.DataFrame(
        {g: v[:n_s] for g, v in gene_data.items()},
        dtype=float,
    )
    log(f"  Matrix: {df.shape}")
    return df, sample_ids

# ============================================================
# PARSE CLINICAL / SURVIVAL
# ============================================================

def parse_survival_robust(
    surv_file, pheno_file, sample_ids
):
    """
    Multi-format survival parser.
    Tries surv_file first, then pheno_file.
    Handles Xena, GDC, and combined formats.
    """
    log("")
    log("=" * 65)
    log("PARSE SURVIVAL + CLINICAL (robust)")
    log("=" * 65)

    n         = len(sample_ids)
    sid_idx   = {
        s: i for i, s in enumerate(sample_ids)
    }
    os_time   = np.full(n, np.nan)
    os_event  = np.full(n, np.nan)
    stage     = np.array([""] * n)
    grade     = np.array([""] * n)
    age       = np.full(n, np.nan)
    gender    = np.array([""] * n)
    etiology  = np.array([""] * n)
    sample_type = np.array([""] * n)

    def match_sample(sid):
        """
        Try multiple matching strategies
        for TCGA barcodes.
        """
        # Exact match
        idx = sid_idx.get(sid)
        if idx is not None:
            return idx
        # 15-char prefix match
        # TCGA-XX-XXXX-01A → TCGA-XX-XXXX-01
        sid15 = sid[:15]
        for k, v in sid_idx.items():
            if k[:15] == sid15:
                return v
        # 12-char case ID match
        # TCGA-XX-XXXX (case, not sample)
        # match any sample from that case
        sid12 = sid[:12]
        for k, v in sid_idx.items():
            if k[:12] == sid12:
                return v
        return None

    def parse_file(fpath):
        """
        Parse one TSV/CSV file for
        survival and clinical data.
        Returns n_matched.
        """
        if not os.path.exists(fpath):
            log(f"  File not found: {fpath}")
            return 0

        sz = os.path.getsize(fpath)
        log(f"  Parsing: {fpath} ({sz:,} bytes)")

        opener = (
            gzip.open(fpath, "rt",
                      encoding="utf-8",
                      errors="ignore")
            if fpath.endswith(".gz")
            else open(fpath, "r",
                      encoding="utf-8",
                      errors="ignore")
        )

        hdr      = None
        n_parsed = 0

        # Column index holders
        col = {
            "sample":   None,
            "os_t":     None,
            "os_e":     None,
            "days_to_death":        None,
            "days_to_last_follow":  None,
            "vital_status":         None,
            "stage":    None,
            "grade":    None,
            "age":      None,
            "gender":   None,
            "etiol":    None,
            "stype":    None,
        }

        with opener as f:
            for line in f:
                line  = line.rstrip("\n")
                if not line.strip():
                    continue
                # Support tab or comma
                sep = (
                    "\t" if "\t" in line
                    else ","
                )
                parts = [
                    p.strip().strip('"')
                    for p in line.split(sep)
                ]

                # ── Header ──────────────────────
                if hdr is None:
                    hdr = [
                        p.lower() for p in parts
                    ]
                    log(f"  Headers: {hdr[:12]}")
                    for i, h in enumerate(hdr):
                        # Sample ID
                        if h in [
                            "sample","sample_id",
                            "_sample_id","sampleid",
                            "submitter_id",
                            "case_submitter_id",
                            "bcr_patient_barcode",
                        ]:
                            if col["sample"] is None:
                                col["sample"] = i

                        # OS time (days or months)
                        if h in [
                            "os.time","os_time",
                            "days_to_last_follow_up",
                            "days_to_last_followup",
                            "time","_time",
                            "days_to_last_follow",
                        ]:
                            col["os_t"] = i
                        if h in [
                            "days_to_death",
                            "days_to_patient_death",
                        ]:
                            col["days_to_death"] = i
                        if "last_follow" in h \
                                and "days" in h:
                            if col["days_to_last_follow"] \
                                    is None:
                                col["days_to_last_follow"] = i

                        # OS event
                        if h in [
                            "os","os_status",
                            "vital_status",
                            "_vital_status",
                            "event","status",
                        ]:
                            col["os_e"] = i

                        # Stage
                        if any(x in h for x in [
                            "stage","ajcc_pathologic_t",
                            "tumor_stage",
                            "clinical_stage",
                        ]):
                            if col["stage"] is None:
                                col["stage"] = i

                        # Grade
                        if any(x in h for x in [
                            "grade","neoplasm_grade",
                            "tumor_grade",
                            "histologic_grade",
                        ]):
                            if col["grade"] is None:
                                col["grade"] = i

                        # Age
                        if any(x in h for x in [
                            "age_at_initial",
                            "age_at_diagnosis",
                            "age_at_index",
                            "age",
                        ]):
                            if col["age"] is None:
                                col["age"] = i

                        # Gender
                        if h in [
                            "gender","sex",
                            "patient_gender",
                        ]:
                            if col["gender"] is None:
                                col["gender"] = i

                        # Etiology
                        if any(x in h for x in [
                            "alcohol","hbv","hcv",
                            "viral","etiology",
                            "primary_diagnosis",
                            "hepatitis",
                        ]):
                            if col["etiol"] is None:
                                col["etiol"] = i

                        # Sample type
                        if "sample_type" in h:
                            col["stype"] = i

                    log(f"  Col map: "
                        f"sample={col['sample']} "
                        f"os_t={col['os_t']} "
                        f"os_e={col['os_e']} "
                        f"stage={col['stage']} "
                        f"grade={col['grade']}")
                    continue

                # ── Data row ────────────────────
                if col["sample"] is None:
                    continue
                sc = col["sample"]
                if sc >= len(parts):
                    continue

                sid = parts[sc].strip()
                idx = match_sample(sid)
                if idx is None:
                    continue

                # OS time
                # Strategy: use os_t if present,
                # else derive from days_to_death
                # and days_to_last_follow
                if col["os_t"] is not None:
                    c = col["os_t"]
                    if c < len(parts):
                        try:
                            t_raw = float(parts[c])
                            # Detect if days (>100)
                            # or months (<24 typical)
                            if t_raw > 200:
                                t_raw /= 30.44
                            if t_raw > 0:
                                os_time[idx] = t_raw
                        except (ValueError,
                                TypeError):
                            pass

                # Derive time from days
                if np.isnan(os_time[idx]):
                    dtd = np.nan
                    dtf = np.nan
                    if col["days_to_death"] \
                            is not None:
                        c = col["days_to_death"]
                        if c < len(parts):
                            try:
                                dtd = float(
                                    parts[c]
                                )
                            except (ValueError,
                                    TypeError):
                                pass
                    if col["days_to_last_follow"] \
                            is not None:
                        c = col["days_to_last_follow"]
                        if c < len(parts):
                            try:
                                dtf = float(
                                    parts[c]
                                )
                            except (ValueError,
                                    TypeError):
                                pass
                    # Use max of death/follow
                    if np.isfinite(dtd) and dtd > 0:
                        os_time[idx] = dtd / 30.44
                    elif (np.isfinite(dtf)
                            and dtf > 0):
                        os_time[idx] = dtf / 30.44

                # OS event
                if col["os_e"] is not None:
                    c = col["os_e"]
                    if c < len(parts):
                        v = parts[c].strip().lower()
                        if v in [
                            "1","dead","deceased",
                            "died","true",
                        ]:
                            os_event[idx] = 1
                        elif v in [
                            "0","alive","living",
                            "censored","false",
                            "not reported",
                        ]:
                            os_event[idx] = 0
                        else:
                            try:
                                os_event[idx] = (
                                    float(v)
                                )
                            except (ValueError,
                                    TypeError):
                                pass

                # Stage
                if col["stage"] is not None:
                    c = col["stage"]
                    if (c < len(parts)
                            and not stage[idx]):
                        v = parts[c].strip()
                        if v and v.lower() not in [
                            "na","not reported",
                            "unknown","","--",
                        ]:
                            stage[idx] = v

                # Grade
                if col["grade"] is not None:
                    c = col["grade"]
                    if (c < len(parts)
                            and not grade[idx]):
                        v = parts[c].strip()
                        if v and v.lower() not in [
                            "na","not reported",
                            "unknown","","--",
                        ]:
                            grade[idx] = v

                # Age
                if col["age"] is not None:
                    c = col["age"]
                    if (c < len(parts)
                            and np.isnan(age[idx])):
                        try:
                            age[idx] = float(
                                parts[c]
                            )
                        except (ValueError,
                                TypeError):
                            pass

                # Gender
                if col["gender"] is not None:
                    c = col["gender"]
                    if (c < len(parts)
                            and not gender[idx]):
                        gender[idx] = (
                            parts[c].strip()
                        )

                # Etiology
                if col["etiol"] is not None:
                    c = col["etiol"]
                    if (c < len(parts)
                            and not etiology[idx]):
                        etiology[idx] = (
                            parts[c].strip()
                        )

                # Sample type
                if col["stype"] is not None:
                    c = col["stype"]
                    if (c < len(parts)
                            and not sample_type[idx]):
                        sample_type[idx] = (
                            parts[c].strip()
                        )

                n_parsed += 1

        log(f"  Rows matched: {n_parsed}")
        return n_parsed

    # Parse both files
    n1 = parse_file(surv_file)
    n2 = parse_file(pheno_file)

    valid_os = (
        ~np.isnan(os_time)
        & ~np.isnan(os_event)
        & (os_time > 0)
    )
    log(f"\n  OS valid total: {valid_os.sum()}")
    log(f"  OS events: "
        f"{int(os_event[valid_os].sum())}")

    # If OS time still missing, try to
    # reconstruct from event + any time column
    # in the parsed data
    os_missing = valid_os.sum() == 0
    if os_missing:
        log("")
        log("  WARNING: OS time still 0 after "
            "parsing both files.")
        log("  Possible causes:")
        log("  1. Survival file not downloaded")
        log("  2. Sample ID format mismatch")
        log("  3. Column header not matched")
        log("")
        log("  Attempting ID format diagnosis:")
        log(f"  Matrix sample IDs format: "
            f"{sample_ids[:3]}")
        log("")
        log("  Expected survival file formats:")
        log("  Xena: col 'sample' = "
            "TCGA-FV-A495-01")
        log("  GDC:  col 'case_submitter_id' = "
            "TCGA-FV-A495")
        log("  Note: GDC uses 12-char case ID,")
        log("  matrix uses 15-char sample ID.")
        log("  The match_sample() function")
        log("  handles both via prefix matching.")

    from collections import Counter
    log(f"\n  Stage: "
        f"{dict(Counter([s for s in stage if s]).most_common(8))}")
    log(f"  Grade: "
        f"{dict(Counter([g for g in grade if g]).most_common(6))}")
    log(f"  Gender: "
        f"{dict(Counter([g for g in gender if g]).most_common(4))}")
    age_v = age[~np.isnan(age)]
    if len(age_v) > 0:
        log(f"  Age: mean={age_v.mean():.1f} "
            f"range={age_v.min():.0f}–"
            f"{age_v.max():.0f}")

    return {
        "os_time":      os_time,
        "os_event":     os_event,
        "stage":        stage,
        "grade":        grade,
        "age":          age,
        "gender":       gender,
        "etiology":     etiology,
        "sample_type":  sample_type,
    }


# ============================================================
# STANDALONE DOWNLOAD HELPER
# Run this independently to fetch the
# three missing files using working
# 2026 public URLs
# ============================================================

def download_tcga_lihc_clinical(tcga_dir):
    """
    Fetch TCGA-LIHC survival, clinical,
    and mutation data from sources that
    do not require authentication.

    Priority order:
      1. NCI GDC API (no auth for public)
      2. cBioPortal public API
      3. LinkedOmics (mirrored data)
      4. Manual instruction
    """
    log("")
    log("=" * 65)
    log("ALTERNATIVE DOWNLOAD — TCGA-LIHC")
    log("=" * 65)

    import json

    surv_file  = os.path.join(
        tcga_dir, "TCGA-LIHC.survival.tsv.gz"
    )
    pheno_file = os.path.join(
        tcga_dir, "TCGA-LIHC.pheno.tsv.gz"
    )
    mut_file   = os.path.join(
        tcga_dir, "TCGA-LIHC.mutations.tsv.gz"
    )

    # ── 1. cBioPortal API (no auth) ──────────────────────
    # cBioPortal hosts TCGA-LIHC clinical data
    # publicly via REST API
    CBIO_BASE = "https://www.cbioportal.org/api"
    STUDY_ID  = "lihc_tcga"

    # Clinical data (includes OS)
    cbio_clinical_url = (
        f"{CBIO_BASE}/studies/{STUDY_ID}"
        f"/clinical-data?clinicalDataType=SAMPLE"
        f"&pageSize=10000"
    )

    # Patient clinical (OS time + event)
    cbio_patient_url  = (
        f"{CBIO_BASE}/studies/{STUDY_ID}"
        f"/clinical-data?clinicalDataType=PATIENT"
        f"&pageSize=10000"
    )

    log("  Trying cBioPortal API...")

    for label, url, outfile in [
        ("patient clinical",
         cbio_patient_url,
         pheno_file),
    ]:
        if os.path.exists(outfile):
            log(f"  Already present: {outfile}")
            continue
        try:
            r = requests.get(
                url, timeout=60,
                headers={
                    "Accept": "application/json",
                    "User-Agent":
                    "OrganismCore/1.0",
                },
            )
            if r.status_code == 200:
                data = r.json()
                log(f"  cBioPortal {label}: "
                    f"n={len(data)} records")

                # Convert JSON to TSV
                if not data:
                    continue
                keys = set()
                for row in data:
                    keys.update(row.keys())
                keys = sorted(keys)

                lines = ["\t".join(keys)]
                for row in data:
                    lines.append(
                        "\t".join(
                            str(row.get(k, ""))
                            for k in keys
                        )
                    )
                content = "\n".join(lines)

                with gzip.open(
                    outfile, "wt",
                    encoding="utf-8",
                ) as f:
                    f.write(content)
                sz = os.path.getsize(outfile)
                log(f"  Saved: {outfile} "
                    f"({sz:,} bytes)")
            else:
                log(f"  HTTP {r.status_code} "
                    f"for cBioPortal {label}")
        except Exception as e:
            log(f"  cBioPortal error: {e}")

    # ── 2. cBioPortal clinical attributes ────────────────
    # Specifically request OS_MONTHS, OS_STATUS,
    # STAGE, GRADE for TCGA-LIHC
    cbio_attrs = [
        "OS_MONTHS","OS_STATUS",
        "AJCC_PATHOLOGIC_TUMOR_STAGE",
        "GRADE","AGE","SEX",
        "DAYS_TO_LAST_FOLLOWUP",
    ]

    # Build a separate survival TSV
    # from cBioPortal patient data
    if not os.path.exists(surv_file):
        log("")
        log("  Building survival TSV from "
            "cBioPortal patient data...")
        try:
            url_p = (
                f"{CBIO_BASE}/studies/{STUDY_ID}"
                f"/clinical-data"
                f"?clinicalDataType=PATIENT"
                f"&pageSize=10000"
            )
            r = requests.get(
                url_p, timeout=60,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "OrganismCore",
                },
            )
            if r.status_code == 200:
                data = r.json()
                # Pivot: patientId → {attr: val}
                patient_data = {}
                for row in data:
                    pid  = row.get(
                        "patientId", ""
                    )
                    attr = row.get(
                        "clinicalAttributeId", ""
                    )
                    val  = row.get("value", "")
                    if pid not in patient_data:
                        patient_data[pid] = {}
                    patient_data[pid][attr] = val

                log(f"  Patients: "
                    f"{len(patient_data)}")

                # Get sample list to build
                # patient→sample mapping
                url_s = (
                    f"{CBIO_BASE}/studies/"
                    f"{STUDY_ID}/samples"
                    f"?pageSize=10000"
                )
                r2 = requests.get(
                    url_s, timeout=60,
                    headers={
                        "Accept":
                        "application/json",
                        "User-Agent":
                        "OrganismCore",
                    },
                )
                sample_map = {}
                if r2.status_code == 200:
                    samples = r2.json()
                    for s in samples:
                        sid = s.get(
                            "sampleId", ""
                        )
                        pid = s.get(
                            "patientId", ""
                        )
                        sample_map[sid] = pid
                    log(f"  Samples: "
                        f"{len(sample_map)}")

                # Write survival TSV:
                # sample, OS, OS.time
                lines = ["sample\tOS\tOS.time"]
                for sid, pid in (
                    sample_map.items()
                ):
                    pd_  = patient_data.get(
                        pid, {}
                    )
                    os_s = pd_.get(
                        "OS_STATUS", ""
                    )
                    os_t = pd_.get(
                        "OS_MONTHS", ""
                    )
                    # Map status
                    if "DECEASED" in os_s.upper():
                        ev = "1"
                    elif "LIVING" in os_s.upper():
                        ev = "0"
                    else:
                        ev = os_s
                    lines.append(
                        f"{sid}\t{ev}\t{os_t}"
                    )

                content = "\n".join(lines)
                with gzip.open(
                    surv_file, "wt",
                    encoding="utf-8",
                ) as f:
                    f.write(content)
                sz = os.path.getsize(surv_file)
                log(f"  Saved survival: "
                    f"{surv_file} ({sz:,} bytes)")

                # Also write full phenotype
                if not os.path.exists(pheno_file):
                    attrs_all = set()
                    for pd_ in patient_data.values():
                        attrs_all.update(pd_.keys())
                    attrs_all = sorted(attrs_all)
                    hdr_cols = (
                        ["sample","patientId"]
                        + attrs_all
                    )
                    lines2   = [
                        "\t".join(hdr_cols)
                    ]
                    for sid, pid in (
                        sample_map.items()
                    ):
                        pd_ = patient_data.get(
                            pid, {}
                        )
                        row = (
                            [sid, pid]
                            + [
                                pd_.get(a, "")
                                for a in attrs_all
                            ]
                        )
                        lines2.append(
                            "\t".join(row)
                        )
                    content2 = "\n".join(lines2)
                    with gzip.open(
                        pheno_file, "wt",
                        encoding="utf-8",
                    ) as f:
                        f.write(content2)
                    sz2 = os.path.getsize(
                        pheno_file
                    )
                    log(f"  Saved pheno: "
                        f"{pheno_file} "
                        f"({sz2:,} bytes)")

        except Exception as e:
            log(f"  cBioPortal patient error: {e}")

    # ── 3. Mutations from cBioPortal ─────────────────────
    if not os.path.exists(mut_file):
        log("")
        log("  Fetching mutations from "
            "cBioPortal...")
        try:
            # Get mutations for key HCC genes
            genes_req = [
                "CTNNB1","TP53","ARID1A",
                "AXIN1","NFE2L2","RB1",
                "PIK3CA","PTEN","TSC1",
                "TSC2","ARID2","RNF43",
                "KMT2D","SETD2","HNF1A",
                "TERT","BAP1","CDKN2A",
                "ALB","IDH1",
            ]
            url_m = (
                f"{CBIO_BASE}/molecular-profiles"
                f"/{STUDY_ID}_mutations"
                f"/mutations/fetch"
                f"?projection=DETAILED"
            )
            payload = {
                "entrezGeneIds": [],
                "hugoGeneSymbols": genes_req,
            }
            # Get all samples first
            url_s = (
                f"{CBIO_BASE}/studies/"
                f"{STUDY_ID}/samples"
                f"?pageSize=10000"
            )
            r_s = requests.get(
                url_s, timeout=60,
                headers={
                    "Accept":
                    "application/json",
                },
            )
            if r_s.status_code == 200:
                all_samples = [
                    s["sampleId"]
                    for s in r_s.json()
                ]
                payload["sampleIds"] = (
                    all_samples
                )

            r_m = requests.post(
                url_m, json=payload,
                timeout=120,
                headers={
                    "Accept":
                    "application/json",
                    "Content-Type":
                    "application/json",
                },
            )
            if r_m.status_code == 200:
                muts = r_m.json()
                log(f"  Mutations fetched: "
                    f"n={len(muts)}")

                # Write as TSV
                lines_m = [
                    "Hugo_Symbol\t"
                    "Tumor_Sample_Barcode\t"
                    "Variant_Classification\t"
                    "HGVSp_Short\t"
                    "Chromosome\t"
                    "Start_Position\t"
                    "Reference_Allele\t"
                    "Tumor_Seq_Allele2"
                ]
                for m in muts:
                    gene  = m.get(
                        "gene", {}
                    ).get(
                        "hugoGeneSymbol", ""
                    )
                    sid   = m.get(
                        "sampleId", ""
                    )
                    vclass = m.get(
                        "mutationType", ""
                    )
                    pchng  = m.get(
                        "proteinChange", ""
                    )
                    chrom  = m.get("chr", "")
                    start  = str(
                        m.get("startPosition","")
                    )
                    ref    = m.get(
                        "referenceAllele", ""
                    )
                    alt    = m.get(
                        "variantAllele", ""
                    )
                    lines_m.append(
                        f"{gene}\t{sid}\t"
                        f"{vclass}\t{pchng}\t"
                        f"{chrom}\t{start}\t"
                        f"{ref}\t{alt}"
                    )

                content_m = "\n".join(lines_m)
                with gzip.open(
                    mut_file, "wt",
                    encoding="utf-8",
                ) as f:
                    f.write(content_m)
                sz = os.path.getsize(mut_file)
                log(f"  Saved mutations: "
                    f"{mut_file} ({sz:,} bytes)")
            else:
                log(f"  Mutation HTTP "
                    f"{r_m.status_code}")
        except Exception as e:
            log(f"  Mutation error: {e}")

    # ── 4. Status check ──────────────────────────────────
    log("")
    log("  File status after download:")
    for label, fpath in [
        ("Survival",  surv_file),
        ("Phenotype", pheno_file),
        ("Mutations", mut_file),
    ]:
        if os.path.exists(fpath):
            sz = os.path.getsize(fpath)
            log(f"  {label}: ✓ ({sz:,} bytes)")
        else:
            log(f"  {label}: ✗ NOT FOUND")

    return (
        os.path.exists(surv_file),
        os.path.exists(pheno_file),
        os.path.exists(mut_file),
    )

# ============================================================
# PARSE MUTATIONS
# ============================================================

def parse_mutations(mut_file, sample_ids):
    log("")
    log("=" * 65)
    log("PARSE MUTATIONS")
    log("=" * 65)

    n       = len(sample_ids)
    sid_idx = {s: i for i, s in enumerate(sample_ids)}

    genes_track = [
        "CTNNB1","TP53","ARID1A","AXIN1",
        "RB1","NFE2L2","KEAP1","PIK3CA",
        "PTEN","ALB","RPS6KA3","CDKN2A",
        "TSC1","TSC2","ARID2","BAP1",
        "MET","FGF19","CCND1","CDK4",
        "ELF3","SMARCA4","IDH1","IDH2",
        "KMT2A","KMT2D","SETD2","NOTCH1",
        "HNF1A","RNF43","TERT",
    ]
    gene_set = set(genes_track)

    # mut_matrix[gene][sample_idx] = 1 if mutated
    mut_matrix = {
        g: np.zeros(n, dtype=int)
        for g in genes_track
    }

    if not os.path.exists(mut_file):
        log("  Mutation file not found")
        return mut_matrix

    opener = (
        gzip.open(mut_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if mut_file.endswith(".gz")
        else open(mut_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    hdr       = None
    gene_c    = None
    sample_c  = None
    effect_c  = None
    n_muts    = 0

    with opener as f:
        for line in f:
            line  = line.rstrip("\n")
            if line.startswith("#"):
                continue
            parts = [
                p.strip().strip('"')
                for p in line.split("\t")
            ]
            if hdr is None:
                hdr = [
                    p.upper() for p in parts
                ]
                log(f"  Mutation headers "
                    f"(first 8): {hdr[:8]}")
                for i, h in enumerate(hdr):
                    hl = h.lower()
                    if hl in [
                        "hugo_symbol","gene",
                        "gene_name","symbol",
                    ]:
                        gene_c = i
                    if any(x in hl for x in [
                        "tumor_sample",
                        "sample_id",
                        "sample",
                    ]):
                        if sample_c is None:
                            sample_c = i
                    if any(x in hl for x in [
                        "consequence",
                        "variant_class",
                        "mutation_type",
                        "effect",
                        "one_consequence",
                    ]):
                        if effect_c is None:
                            effect_c = i
                log(f"  gene_c={gene_c} "
                    f"sample_c={sample_c} "
                    f"effect_c={effect_c}")
                continue

            if gene_c is None or sample_c is None:
                continue
            if len(parts) <= max(
                gene_c, sample_c
            ):
                continue

            gene = parts[gene_c].strip()
            if gene not in gene_set:
                continue

            sid = parts[sample_c].strip()
            idx = sid_idx.get(sid)
            if idx is None:
                # Try barcode match
                for k, v in sid_idx.items():
                    if k[:15] == sid[:15]:
                        idx = v
                        break
            if idx is None:
                continue

            # Filter to damaging mutations
            keep = True
            if effect_c is not None:
                eff = parts[effect_c].lower()
                benign = [
                    "synonymous","silent",
                    "3_prime_utr","5_prime_utr",
                    "intron","intronic",
                ]
                if any(b in eff for b in benign):
                    keep = False

            if keep:
                mut_matrix[gene][idx] = 1
                n_muts += 1

    log(f"\n  Total mutations parsed: {n_muts}")
    log(f"\n  Mutation frequencies:")
    for gene in genes_track:
        freq = mut_matrix[gene].sum()
        if freq > 0:
            pct = 100 * freq / n
            log(f"  {gene:<12} {freq:>4} "
                f"({pct:.1f}%)")

    return mut_matrix

# ============================================================
# BUILD DEPTH SCORES
# ============================================================

def build_depth(df, switch, fa, label):
    gc  = list(df.columns)
    sw  = [g for g in switch if g in gc]
    fa_ = [g for g in fa    if g in gc]
    log(f"  {label}:")
    log(f"    Switch: {sw}")
    log(f"    FA:     {fa_}")

    n     = len(df)
    depth = np.zeros(n, dtype=float)
    nd    = 0
    if sw:
        depth += (
            1 - norm01(df[sw].mean(axis=1).values)
        )
        nd += 1
    if fa_:
        depth += norm01(
            df[fa_].mean(axis=1).values
        )
        nd += 1
    if nd > 0:
        depth /= nd

    log(f"    n={n} mean={np.nanmean(depth):.4f} "
        f"std={np.nanstd(depth):.4f} "
        f"min={np.nanmin(depth):.4f} "
        f"max={np.nanmax(depth):.4f}")
    return depth

# ============================================================
# S3-2: METABOLIC SCORE REPLICATION
# ============================================================

def metabolic_score_replication(
    df_hcc, os_time, os_event, hcc_idx
):
    log("")
    log("=" * 65)
    log("S3-2: METABOLIC SCORE REPLICATION")
    log("S3-P1: Metab score OS p<0.01")
    log("=" * 65)

    t  = os_time[hcc_idx]
    e  = os_event[hcc_idx]
    gc = list(df_hcc.columns)

    metab_genes = [
        g for g in METAB_SWITCH if g in gc
    ]
    log(f"  Metabolic genes available: "
        f"{metab_genes}")

    if len(metab_genes) < 3:
        log("  FATAL: Too few metabolic genes")
        return np.zeros(len(df_hcc))

    metab_arr   = df_hcc[metab_genes].values
    metab_mean  = np.nanmean(metab_arr, axis=1)
    metab_score = 1 - norm01(metab_mean)

    valid = (
        ~np.isnan(t) & ~np.isnan(e)
        & ~np.isnan(metab_score) & (t > 0)
    )
    log(f"  n_valid OS: {valid.sum()}")

    if valid.sum() < 10:
        log("  Insufficient data")
        return metab_score

    med = np.median(metab_score[valid])
    hi  = metab_score[valid] >= med
    lo  = ~hi

    p = logrank_p(
        t[valid][hi], e[valid][hi],
        t[valid][lo], e[valid][lo],
    )

    mh = t[valid][hi].mean()
    ml = t[valid][lo].mean()
    log(f"  Metabolic score OS: {fmt_p(p)}")
    log(f"  Deep={mh:.1f}mo  Shallow={ml:.1f}mo")

    conf = not np.isnan(p) and p < 0.01
    log(f"\n  S3-P1: Metab score OS p<0.01")
    log(f"  STATUS: "
        f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")

    # Correlations with individual genes
    log(f"\n  Metab gene correlations "
        f"(within TCGA HCC):")
    for gene in metab_genes:
        rv, pv = safe_pearsonr(
            metab_score, df_hcc[gene].values
        )
        log(f"  {gene:<10} r={rv:>+.4f}  "
            f"{fmt_p(pv)}")

    # Tertile
    dc_v = metab_score[valid]
    t33, t67 = np.percentile(dc_v, [33, 67])
    t1  = dc_v <= t33
    t2  = (dc_v > t33) & (dc_v <= t67)
    t3  = dc_v > t67
    log(f"\n  Tertile OS (metabolic score):")
    for tlabel, tmask in [
        ("T1 shallow", t1),
        ("T2 mid",     t2),
        ("T3 deep",    t3),
    ]:
        tv = t[valid][tmask]
        ev = e[valid][tmask]
        vm = np.isfinite(tv) & np.isfinite(ev)
        m  = tv[vm].mean() if vm.sum() > 0 else np.nan
        log(f"  {tlabel}: n={tmask.sum()} "
            f"OS mean={m:.1f}mo")

    p13 = logrank_p(
        t[valid][t3], e[valid][t3],
        t[valid][t1], e[valid][t1],
    )
    log(f"  T3 vs T1: {fmt_p(p13)}")

    return metab_score

# ============================================================
# S3-3: CTNNB1 MUTATION SURVIVAL (HCC-P5)
# ============================================================

def ctnnb1_mutation_survival(
    mut_matrix, os_time, os_event,
    hcc_idx, df_hcc
):
    log("")
    log("=" * 65)
    log("S3-3: CTNNB1 MUTATION SURVIVAL")
    log("HCC-P5 DIRECT TEST")
    log("S3-P2: CTNNB1-mutant better OS")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    gc  = list(df_hcc.columns)

    ctnnb1_mut = mut_matrix["CTNNB1"][hcc_idx]
    n_mut      = ctnnb1_mut.sum()
    n_wt       = (ctnnb1_mut == 0).sum()

    log(f"  CTNNB1 mutant: n={n_mut}")
    log(f"  CTNNB1 WT:     n={n_wt}")

    if n_mut < 5 or n_wt < 5:
        log("  Insufficient mutant samples")
        return {}

    mut_mask = ctnnb1_mut == 1
    wt_mask  = ctnnb1_mut == 0

    valid_mut = (
        mut_mask
        & ~np.isnan(t) & ~np.isnan(e) & (t > 0)
    )
    valid_wt  = (
        wt_mask
        & ~np.isnan(t) & ~np.isnan(e) & (t > 0)
    )

    m_mut = t[valid_mut].mean() if valid_mut.sum() > 0 else np.nan
    m_wt  = t[valid_wt].mean()  if valid_wt.sum() > 0  else np.nan

    p = logrank_p(
        t[mut_mask], e[mut_mask],
        t[wt_mask],  e[wt_mask],
    )

    direction = (
        "mut=better" if m_mut > m_wt
        else "mut=worse"
    )

    log(f"\n  CTNNB1 mut OS: {fmt_p(p)}")
    log(f"  Mutant: {m_mut:.1f}mo "
        f"WT: {m_wt:.1f}mo  ({direction})")

    conf = (
        not np.isnan(p)
        and not np.isnan(m_mut)
        and not np.isnan(m_wt)
        and m_mut > m_wt
    )
    log(f"\n  S3-P2 CTNNB1-mutant better OS")
    log(f"  STATUS: "
        f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")

    # CTNNB1 mutation vs expression
    if "CTNNB1" in gc:
        rv, pv = safe_pearsonr(
            ctnnb1_mut.astype(float),
            df_hcc["CTNNB1"].values,
        )
        log(f"\n  r(CTNNB1_mut, CTNNB1_expr) = "
            f"{rv:+.4f}  {fmt_p(pv)}")
        log(f"  (validates mutation-expression")
        log(f"   decoupling hypothesis from S2)")

    # CTNNB1 mutation vs GLUL
    if "GLUL" in gc:
        rv_g, pv_g = safe_pearsonr(
            ctnnb1_mut.astype(float),
            df_hcc["GLUL"].values,
        )
        log(f"  r(CTNNB1_mut, GLUL_expr) = "
            f"{rv_g:+.4f}  {fmt_p(pv_g)}")
        log(f"  (GLUL=Wnt target; expect r>+0.3)")

    # CTNNB1 mutation vs depth
    return {
        "mut_mask":   mut_mask,
        "wt_mask":    wt_mask,
        "p":          p,
        "m_mut":      m_mut,
        "m_wt":       m_wt,
        "t":          t,
        "e":          e,
        "confirmed":  conf,
    }

# ============================================================
# S3-4: TP53 MUTATION SURVIVAL
# ============================================================

def tp53_mutation_survival(
    mut_matrix, os_time, os_event, hcc_idx
):
    log("")
    log("=" * 65)
    log("S3-4: TP53 MUTATION SURVIVAL")
    log("S3-P3: TP53-mutant worse OS")
    log("=" * 65)

    t        = os_time[hcc_idx]
    e        = os_event[hcc_idx]
    tp53_mut = mut_matrix["TP53"][hcc_idx]
    n_mut    = tp53_mut.sum()
    n_wt     = (tp53_mut == 0).sum()

    log(f"  TP53 mutant: n={n_mut}")
    log(f"  TP53 WT:     n={n_wt}")

    if n_mut < 5 or n_wt < 5:
        log("  Insufficient samples")
        return {}

    mut_mask = tp53_mut == 1
    wt_mask  = tp53_mut == 0

    valid_m = (
        mut_mask & ~np.isnan(t)
        & ~np.isnan(e) & (t > 0)
    )
    valid_w = (
        wt_mask & ~np.isnan(t)
        & ~np.isnan(e) & (t > 0)
    )

    m_mut = t[valid_m].mean() if valid_m.sum() > 0 else np.nan
    m_wt  = t[valid_w].mean() if valid_w.sum() > 0 else np.nan

    p = logrank_p(
        t[mut_mask], e[mut_mask],
        t[wt_mask],  e[wt_mask],
    )

    direction = (
        "mut=worse" if m_mut < m_wt
        else "mut=better"
    )
    log(f"  TP53 mut OS: {fmt_p(p)}")
    log(f"  Mutant: {m_mut:.1f}mo "
        f"WT: {m_wt:.1f}mo  ({direction})")

    conf = (
        not np.isnan(p)
        and not np.isnan(m_mut)
        and not np.isnan(m_wt)
        and m_mut < m_wt
    )
    log(f"\n  S3-P3: TP53-mutant worse OS")
    log(f"  STATUS: "
        f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")

    # Also test other key mutations
    log(f"\n  All mutation OS tests:")
    log(f"  {'Gene':<12} {'n_mut':>6} "
        f"{'mut_OS':>10} {'WT_OS':>10}  p-value")
    log(f"  {'-'*55}")

    results = {}
    for gene in [
        "CTNNB1","TP53","ARID1A","AXIN1",
        "NFE2L2","RB1","PIK3CA","PTEN",
        "TSC1","TSC2","ARID2","RNF43",
        "KMT2D","SETD2","HNF1A","TERT",
    ]:
        gm = mut_matrix[gene][hcc_idx]
        if gm.sum() < 5:
            continue
        mmask = gm == 1
        wmask = gm == 0
        vm = (
            mmask & ~np.isnan(t)
            & ~np.isnan(e) & (t > 0)
        )
        vw = (
            wmask & ~np.isnan(t)
            & ~np.isnan(e) & (t > 0)
        )
        mm = (
            t[vm].mean() if vm.sum() > 0
            else np.nan
        )
        mw = (
            t[vw].mean() if vw.sum() > 0
            else np.nan
        )
        gp = logrank_p(
            t[mmask], e[mmask],
            t[wmask], e[wmask],
        )
        d  = (
            "↑mut=worse"
            if mm < mw else "↑mut=better"
        )
        log(f"  {gene:<12} {gm.sum():>6} "
            f"{mm:>10.1f} {mw:>10.1f}  "
            f"{fmt_p(gp)} {d}")
        results[gene] = {
            "p": gp, "m_mut": mm, "m_wt": mw,
            "mut_mask": mmask, "wt_mask": wmask,
            "t": t, "e": e,
        }

    return results

# ============================================================
# S3-5: CTNNB1 MUTATION vs DEPTH
# ============================================================

def ctnnb1_depth_analysis(
    mut_matrix, depth_metab,
    depth_v2, df_hcc, hcc_idx
):
    log("")
    log("=" * 65)
    log("S3-5: CTNNB1 MUTATION vs DEPTH")
    log("S3-P4: CTNNB1-mutant shallower")
    log("=" * 65)

    ctnnb1_mut = mut_matrix["CTNNB1"][hcc_idx]
    tp53_mut   = mut_matrix["TP53"][hcc_idx]
    mut_mask   = ctnnb1_mut == 1
    wt_mask    = ctnnb1_mut == 0
    tp53_mask  = tp53_mut == 1

    for score_label, score in [
        ("metab_score",  depth_metab),
        ("depth_v2",     depth_v2),
    ]:
        m_mut = score[mut_mask].mean() if mut_mask.sum() > 0 else np.nan
        m_wt  = score[wt_mask].mean()  if wt_mask.sum() > 0  else np.nan
        _, p  = safe_mwu(
            score[mut_mask],
            score[wt_mask],
        )
        direction = (
            "mut=shallower"
            if m_mut < m_wt else "mut=deeper"
        )
        log(f"  {score_label}:")
        log(f"    CTNNB1-mut: mean={m_mut:.4f}")
        log(f"    CTNNB1-WT:  mean={m_wt:.4f}")
        log(f"    MWU: {fmt_p(p)} ({direction})")

    # Prediction check on metab score
    m_mut_m = depth_metab[mut_mask].mean() if mut_mask.sum() > 0 else np.nan
    m_wt_m  = depth_metab[wt_mask].mean()  if wt_mask.sum() > 0  else np.nan
    conf = (
        not np.isnan(m_mut_m)
        and not np.isnan(m_wt_m)
        and m_mut_m < m_wt_m
    )
    log(f"\n  S3-P4: CTNNB1-mutant shallower")
    log(f"  STATUS: "
        f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")

    # TP53 vs depth
    if tp53_mask.sum() >= 5:
        m_tp53   = depth_metab[tp53_mask].mean()
        m_nontp53 = depth_metab[~tp53_mask].mean()
        _, p_tp53 = safe_mwu(
            depth_metab[tp53_mask],
            depth_metab[~tp53_mask],
        )
        log(f"\n  TP53 vs depth (metab):")
        log(f"    TP53-mut:  mean={m_tp53:.4f}")
        log(f"    TP53-WT:   mean={m_nontp53:.4f}")
        log(f"    MWU: {fmt_p(p_tp53)}")
        log(f"    (Expect TP53-mut deeper)")

    # Multiple mutation depth analysis
    log(f"\n  Mutation vs depth summary:")
    log(f"  {'Gene':<12} {'n_mut':>6} "
        f"{'mut_depth':>12} {'wt_depth':>12}  p")
    log(f"  {'-'*55}")

    for gene in [
        "CTNNB1","TP53","ARID1A","AXIN1",
        "NFE2L2","RB1","PIK3CA","PTEN",
        "ARID2","RNF43","HNF1A","TERT",
    ]:
        gm = mut_matrix[gene][hcc_idx]
        if gm.sum() < 5:
            continue
        mmask = gm == 1
        wmask = gm == 0
        mm    = depth_metab[mmask].mean()
        mw    = depth_metab[wmask].mean()
        _, gp = safe_mwu(
            depth_metab[mmask],
            depth_metab[wmask],
        )
        d = (
            "↑mut=shallow" if mm < mw
            else "↑mut=deep"
        )
        log(f"  {gene:<12} {gm.sum():>6} "
            f"{mm:>12.4f} {mw:>12.4f}  "
            f"{fmt_p(gp)} {d}")

# ============================================================
# S3-6: IMMUNE INFILTRATION vs DEPTH
# ============================================================

def immune_depth_analysis(df_hcc, depth_metab):
    log("")
    log("=" * 65)
    log("S3-6/S3-7: IMMUNE INFILTRATION vs DEPTH")
    log("S3-P6: CD8A falls with depth")
    log("=" * 65)

    gc = list(df_hcc.columns)

    immune_genes = [
        "CD8A","CD4","FOXP3","CD68",
        "ARG1","CD274","PDCD1",
        "IL6","IL6R","STAT3","TNF",
        "NFKB1","CD44","CD274",
    ]

    log(f"\n  {'Gene':<10} {'r_depth':>10}  "
        f"p-value       interpretation")
    log(f"  {'-'*60}")

    results = {}
    for gene in immune_genes:
        if gene not in gc:
            continue
        rv, pv = safe_pearsonr(
            depth_metab, df_hcc[gene].values
        )
        if np.isnan(rv):
            continue
        interp = ""
        if gene == "CD8A":
            interp = (
                "✓ excludes CTL"
                if rv < -0.10
                else "✗ not excluded"
            )
        elif gene == "FOXP3":
            interp = (
                "deeper=more Treg"
                if rv > 0.10 else ""
            )
        elif gene == "ARG1":
            interp = (
                "ARG1=hepatocyte/MDSC"
            )
        elif gene == "CD274":
            interp = (
                "PD-L1 pattern"
            )
        log(f"  {gene:<10} {rv:>+10.4f}  "
            f"{fmt_p(pv)}  {interp}")
        results[gene] = {"r": rv, "p": pv}

    if "CD8A" in results:
        rv_cd8 = results["CD8A"]["r"]
        conf   = rv_cd8 < -0.10
        log(f"\n  S3-P6: CD8A falls with depth")
        log(f"  r(depth, CD8A) = {rv_cd8:+.4f}")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")

    return results

# ============================================================
# S3-7: COX MULTIVARIATE — DEPTH + STAGE + GRADE
# ============================================================

def cox_multivariate(
    df_hcc, depth_metab,
    os_time, os_event, hcc_idx,
    stage, grade, age, mut_matrix
):
    log("")
    log("=" * 65)
    log("S3-7: COX MULTIVARIATE REGRESSION")
    log("S3-P7: Depth independent of stage/grade")
    log("=" * 65)

    t = os_time[hcc_idx]
    e = os_event[hcc_idx]

    # Encode stage numerically
    stage_num = np.full(len(hcc_idx), np.nan)
    for i, s in enumerate(stage[hcc_idx]):
        sl = s.lower()
        if "stage i" in sl and "ii" not in sl:
            stage_num[i] = 1
        elif "stage ii" in sl and "iii" not in sl:
            stage_num[i] = 2
        elif "stage iii" in sl:
            stage_num[i] = 3
        elif "stage iv" in sl:
            stage_num[i] = 4

    # Encode grade
    grade_num = np.full(len(hcc_idx), np.nan)
    for i, g in enumerate(grade[hcc_idx]):
        gl = g.lower()
        if "g1" in gl or "grade 1" in gl \
                or "well" in gl:
            grade_num[i] = 1
        elif "g2" in gl or "grade 2" in gl \
                or "moderate" in gl:
            grade_num[i] = 2
        elif "g3" in gl or "grade 3" in gl \
                or "poor" in gl:
            grade_num[i] = 3
        elif "g4" in gl or "grade 4" in gl:
            grade_num[i] = 4

    ctnnb1_mut = mut_matrix["CTNNB1"][hcc_idx]
    tp53_mut   = mut_matrix["TP53"][hcc_idx]
    age_hcc    = age[hcc_idx]

    log(f"  Stage numeric: "
        f"{np.unique(stage_num[~np.isnan(stage_num)], return_counts=True)}")
    log(f"  Grade numeric: "
        f"{np.unique(grade_num[~np.isnan(grade_num)], return_counts=True)}")

    # Build Cox dataframe
    cox_df = pd.DataFrame({
        "T":           t,
        "E":           e,
        "depth_metab": depth_metab,
        "stage":       stage_num,
        "grade":       grade_num,
        "age":         age_hcc,
        "CTNNB1_mut":  ctnnb1_mut.astype(float),
        "TP53_mut":    tp53_mut.astype(float),
    })

    cox_df = cox_df.dropna(subset=["T","E"])
    cox_df = cox_df[cox_df["T"] > 0]
    log(f"  n_valid for Cox: {len(cox_df)}")

    # Model 1: depth alone
    log(f"\n  Model 1: depth alone")
    try:
        cph1 = CoxPHFitter()
        d1   = cox_df[["T","E","depth_metab"]].copy()
        d1   = d1.dropna()
        for col in ["depth_metab"]:
            mu = d1[col].mean()
            sd = d1[col].std()
            if sd > 0:
                d1[col] = (d1[col] - mu) / sd
        cph1.fit(d1, "T", "E")
        log(cph1.summary[
            ["coef","exp(coef)","p"]
        ].to_string())
    except Exception as ex:
        log(f"  Error: {ex}")

    # Model 2: depth + stage + grade
    log(f"\n  Model 2: depth + stage + grade")
    try:
        d2 = cox_df[[
            "T","E","depth_metab",
            "stage","grade",
        ]].copy().dropna()
        for col in ["depth_metab","stage","grade"]:
            mu = d2[col].mean()
            sd = d2[col].std()
            if sd > 0:
                d2[col] = (d2[col] - mu) / sd
        cph2 = CoxPHFitter()
        cph2.fit(d2, "T", "E")
        log(cph2.summary[
            ["coef","exp(coef)","p"]
        ].to_string())
        p_depth = cph2.summary.loc[
            "depth_metab", "p"
        ]
        conf = not np.isnan(p_depth) and p_depth < 0.05
        log(f"\n  S3-P7: depth independent of stage/grade")
        log(f"  depth p={p_depth:.4f} in multivariate")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")
    except Exception as ex:
        log(f"  Error: {ex}")

    # Model 3: full model
    log(f"\n  Model 3: depth + stage + grade "
        f"+ mutations + age")
    try:
        d3 = cox_df.copy().dropna()
        for col in [
            "depth_metab","stage","grade","age"
        ]:
            if col in d3.columns:
                mu = d3[col].mean()
                sd = d3[col].std()
                if sd > 0:
                    d3[col] = (d3[col] - mu) / sd
        cph3 = CoxPHFitter()
        cph3.fit(d3, "T", "E")
        log(cph3.summary[
            ["coef","exp(coef)","p"]
        ].to_string())
    except Exception as ex:
        log(f"  Error: {ex}")

# ============================================================
# GENERATE FIGURE
# ============================================================

# ── Replace the generate_figure function ──────────────────
# Add this safe_km helper just above generate_figure,
# then replace every raw kmf.fit() call in the figure
# with safe_km().

def safe_km_fit(kmf, t, e, label):
    """
    Filter NaN/inf/<=0 before passing to
    KaplanMeierFitter.fit(). Returns False
    if too few valid points remain.
    """
    t = np.asarray(t, dtype=float)
    e = np.asarray(e, dtype=float)
    valid = np.isfinite(t) & np.isfinite(e) & (t > 0)
    if valid.sum() < 5:
        return False
    kmf.fit(t[valid], e[valid], label=label)
    return True


def generate_figure(
    df_hcc, depth_metab, depth_v2,
    os_time, os_event, hcc_idx,
    ctnnb1_res, tp53_res, immune_res,
    mut_matrix,
):
    log("")
    log("--- Generating Script 3 figure ---")

    fig = plt.figure(figsize=(30, 26))
    fig.suptitle(
        "HCC — False Attractor Analysis Script 3\n"
        "TCGA-LIHC | Mutations | Metabolic Depth | "
        "OrganismCore | Doc 92c | 2026-03-02",
        fontsize=10, fontweight="bold", y=0.99,
    )
    gs_f = gridspec.GridSpec(
        4, 3, figure=fig,
        hspace=0.60, wspace=0.42,
    )

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    kmf = KaplanMeierFitter()
    gc  = list(df_hcc.columns)

    # ── A: Metabolic score KM ──────────────────────────────
    ax_a = fig.add_subplot(gs_f[0, 0])
    valid = (
        np.isfinite(t) & np.isfinite(e)
        & np.isfinite(depth_metab) & (t > 0)
    )
    if valid.sum() >= 10:
        med = np.median(depth_metab[valid])
        hi  = depth_metab[valid] >= med
        lo  = ~hi
        p   = logrank_p(
            t[valid][hi], e[valid][hi],
            t[valid][lo], e[valid][lo],
        )
        safe_km_fit(
            kmf,
            t[valid][hi], e[valid][hi],
            label=f"Deep n={hi.sum()}",
        )
        kmf.plot_survival_function(
            ax=ax_a, color="#e74c3c",
            ci_show=True, ci_alpha=0.1,
        )
        safe_km_fit(
            kmf,
            t[valid][lo], e[valid][lo],
            label=f"Shallow n={lo.sum()}",
        )
        kmf.plot_survival_function(
            ax=ax_a, color="#27ae60",
            ci_show=True, ci_alpha=0.1,
        )
        ax_a.set_title(
            f"A — Metabolic score OS "
            f"(TCGA-LIHC)\n{fmt_p(p)}",
            fontsize=9,
        )
    else:
        ax_a.set_title(
            "A — Metabolic score OS "
            "(insufficient valid data)",
            fontsize=9,
        )
    ax_a.set_xlabel("Months", fontsize=8)
    ax_a.legend(fontsize=7)

    # ── B: CTNNB1 mutation KM ──────────────────────────────
    ax_b = fig.add_subplot(gs_f[0, 1])
    if ctnnb1_res and "mut_mask" in ctnnb1_res:
        mm = ctnnb1_res["mut_mask"]
        wm = ctnnb1_res["wt_mask"]
        p  = ctnnb1_res["p"]
        ok1 = safe_km_fit(
            kmf, t[mm], e[mm],
            label=f"CTNNB1-mut n={mm.sum()}",
        )
        if ok1:
            kmf.plot_survival_function(
                ax=ax_b, color="#27ae60",
                ci_show=True, ci_alpha=0.1,
            )
        ok2 = safe_km_fit(
            kmf, t[wm], e[wm],
            label=f"CTNNB1-WT n={wm.sum()}",
        )
        if ok2:
            kmf.plot_survival_function(
                ax=ax_b, color="#e74c3c",
                ci_show=True, ci_alpha=0.1,
            )
        ax_b.set_title(
            f"B — CTNNB1 mut vs WT OS "
            f"(HCC-P5)\n{fmt_p(p)}",
            fontsize=9,
        )
    else:
        ax_b.set_title(
            "B — CTNNB1 mutation OS "
            "(no mutation data)",
            fontsize=9,
        )
    ax_b.set_xlabel("Months", fontsize=8)
    ax_b.legend(fontsize=7)

    # ── C: TP53 mutation KM ────────────────────────────────
    ax_c = fig.add_subplot(gs_f[0, 2])
    if "TP53" in tp53_res:
        res = tp53_res["TP53"]
        mm  = res["mut_mask"]
        wm  = res["wt_mask"]
        p   = res["p"]
        ok1 = safe_km_fit(
            kmf, t[mm], e[mm],
            label=f"TP53-mut n={mm.sum()}",
        )
        if ok1:
            kmf.plot_survival_function(
                ax=ax_c, color="#e74c3c",
                ci_show=True, ci_alpha=0.1,
            )
        ok2 = safe_km_fit(
            kmf, t[wm], e[wm],
            label=f"TP53-WT n={wm.sum()}",
        )
        if ok2:
            kmf.plot_survival_function(
                ax=ax_c, color="#27ae60",
                ci_show=True, ci_alpha=0.1,
            )
        ax_c.set_title(
            f"C — TP53 mut vs WT OS\n{fmt_p(p)}",
            fontsize=9,
        )
    else:
        ax_c.set_title(
            "C — TP53 mutation OS "
            "(no mutation data)",
            fontsize=9,
        )
    ax_c.set_xlabel("Months", fontsize=8)
    ax_c.legend(fontsize=7)

    # ── D: CTNNB1 mut vs depth scatter ────────────────────
    ax_d = fig.add_subplot(gs_f[1, 0])
    ctnnb1_mut = mut_matrix["CTNNB1"][hcc_idx]
    mut_m  = ctnnb1_mut == 1
    wt_m   = ctnnb1_mut == 0
    colors = np.where(mut_m, "#27ae60", "#e74c3c")
    ax_d.scatter(
        np.arange(len(depth_metab)),
        depth_metab,
        c=colors, alpha=0.4, s=12,
    )
    m_mut_d = (
        depth_metab[mut_m].mean()
        if mut_m.sum() > 0 else np.nan
    )
    m_wt_d = (
        depth_metab[wt_m].mean()
        if wt_m.sum() > 0 else np.nan
    )
    if np.isfinite(m_mut_d):
        ax_d.axhline(
            m_mut_d, color="#27ae60",
            linestyle="--", linewidth=1.5,
            label=f"CTNNB1-mut mean={m_mut_d:.3f}",
        )
    if np.isfinite(m_wt_d):
        ax_d.axhline(
            m_wt_d, color="#e74c3c",
            linestyle="--", linewidth=1.5,
            label=f"CTNNB1-WT mean={m_wt_d:.3f}",
        )
    ax_d.set_title(
        "D — CTNNB1 mut vs metabolic depth\n"
        "(S3-P4: mut=shallower?)",
        fontsize=9,
    )
    ax_d.set_xlabel("Sample index", fontsize=8)
    ax_d.set_ylabel("Metabolic depth", fontsize=8)
    ax_d.legend(fontsize=7)

    # ── E: CYP3A4 & AFP vs depth ──────────────────────────
    ax_e = fig.add_subplot(gs_f[1, 1])
    plotted_e = False
    if "CYP3A4" in gc:
        rv, _ = safe_pearsonr(
            depth_metab,
            df_hcc["CYP3A4"].values,
        )
        ax_e.scatter(
            depth_metab,
            df_hcc["CYP3A4"].values,
            alpha=0.3, s=10, color="#2980b9",
            label=f"CYP3A4 r={rv:+.2f}",
        )
        ax_e.set_ylabel(
            "CYP3A4", fontsize=8,
            color="#2980b9",
        )
        plotted_e = True
    if "AFP" in gc:
        rv2, _ = safe_pearsonr(
            depth_metab,
            df_hcc["AFP"].values,
        )
        if plotted_e:
            ax_e2 = ax_e.twinx()
            ax_e2.scatter(
                depth_metab,
                df_hcc["AFP"].values,
                alpha=0.3, s=10,
                color="#e74c3c",
                label=f"AFP r={rv2:+.2f}",
            )
            ax_e2.set_ylabel(
                "AFP", fontsize=8,
                color="#e74c3c",
            )
            lines1, lbl1 = (
                ax_e.get_legend_handles_labels()
            )
            lines2, lbl2 = (
                ax_e2.get_legend_handles_labels()
            )
            ax_e.legend(
                lines1 + lines2,
                lbl1 + lbl2,
                fontsize=7,
            )
        else:
            ax_e.scatter(
                depth_metab,
                df_hcc["AFP"].values,
                alpha=0.3, s=10,
                color="#e74c3c",
                label=f"AFP r={rv2:+.2f}",
            )
            ax_e.legend(fontsize=7)
    ax_e.set_title(
        "E — CYP3A4 & AFP vs depth",
        fontsize=9,
    )
    ax_e.set_xlabel("Depth", fontsize=8)

    # ── F: Immune genes vs depth ──────────────────────────
    ax_f = fig.add_subplot(gs_f[1, 2])
    for gene, color in [
        ("CD8A",  "#2980b9"),
        ("FOXP3", "#e74c3c"),
        ("CD274", "#8e44ad"),
    ]:
        if gene not in gc:
            continue
        rv, _ = safe_pearsonr(
            depth_metab,
            df_hcc[gene].values,
        )
        ax_f.scatter(
            depth_metab,
            df_hcc[gene].values,
            alpha=0.25, s=8,
            color=color,
            label=f"{gene} r={rv:+.2f}",
        )
    ax_f.set_title(
        "F — Immune genes vs depth\n"
        "(S3-P6: CD8A falls?)",
        fontsize=9,
    )
    ax_f.set_xlabel("Metabolic depth", fontsize=8)
    ax_f.legend(fontsize=7)

    # ── G: SOX4 KM (replication) ──────────────────────────
    ax_g = fig.add_subplot(gs_f[2, 0])
    if "SOX4" in gc:
        sox4_v = df_hcc["SOX4"].values
        # Filter NaN from gene values AND t/e
        valid_s4 = (
            np.isfinite(sox4_v)
            & np.isfinite(t)
            & np.isfinite(e)
            & (t > 0)
        )
        if valid_s4.sum() >= 10:
            med_s  = np.nanmedian(sox4_v[valid_s4])
            s_hi   = valid_s4 & (sox4_v >= med_s)
            s_lo   = valid_s4 & (sox4_v <  med_s)
            p_s4   = logrank_p(
                t[s_hi], e[s_hi],
                t[s_lo], e[s_lo],
            )
            ok1 = safe_km_fit(
                kmf, t[s_hi], e[s_hi],
                label=f"SOX4-hi n={s_hi.sum()}",
            )
            if ok1:
                kmf.plot_survival_function(
                    ax=ax_g, color="#e74c3c",
                    ci_show=True, ci_alpha=0.1,
                )
            ok2 = safe_km_fit(
                kmf, t[s_lo], e[s_lo],
                label=f"SOX4-lo n={s_lo.sum()}",
            )
            if ok2:
                kmf.plot_survival_function(
                    ax=ax_g, color="#27ae60",
                    ci_show=True, ci_alpha=0.1,
                )
            ax_g.set_title(
                f"G — SOX4 OS (TCGA replication)\n"
                f"{fmt_p(p_s4)}",
                fontsize=9,
            )
        else:
            ax_g.set_title(
                "G — SOX4 OS (insufficient data)",
                fontsize=9,
            )
    else:
        ax_g.set_title(
            "G — SOX4 not in matrix", fontsize=9
        )
    ax_g.set_xlabel("Months", fontsize=8)
    ax_g.legend(fontsize=7)

    # ── H: SMAD3 KM ───────────────────────────────────────
    ax_h = fig.add_subplot(gs_f[2, 1])
    if "SMAD3" in gc:
        sm3_v  = df_hcc["SMAD3"].values
        valid_sm = (
            np.isfinite(sm3_v)
            & np.isfinite(t)
            & np.isfinite(e)
            & (t > 0)
        )
        if valid_sm.sum() >= 10:
            med_sm = np.nanmedian(sm3_v[valid_sm])
            sm_hi  = valid_sm & (sm3_v >= med_sm)
            sm_lo  = valid_sm & (sm3_v <  med_sm)
            p_sm3  = logrank_p(
                t[sm_hi], e[sm_hi],
                t[sm_lo], e[sm_lo],
            )
            ok1 = safe_km_fit(
                kmf, t[sm_hi], e[sm_hi],
                label=f"SMAD3-hi n={sm_hi.sum()}",
            )
            if ok1:
                kmf.plot_survival_function(
                    ax=ax_h, color="#e74c3c",
                    ci_show=True, ci_alpha=0.1,
                )
            ok2 = safe_km_fit(
                kmf, t[sm_lo], e[sm_lo],
                label=f"SMAD3-lo n={sm_lo.sum()}",
            )
            if ok2:
                kmf.plot_survival_function(
                    ax=ax_h, color="#27ae60",
                    ci_show=True, ci_alpha=0.1,
                )
            ax_h.set_title(
                f"H — SMAD3 OS "
                f"(cross-cancer rep)\n"
                f"{fmt_p(p_sm3)}",
                fontsize=9,
            )
        else:
            ax_h.set_title(
                "H — SMAD3 OS "
                "(insufficient data)",
                fontsize=9,
            )
    else:
        ax_h.set_title(
            "H — SMAD3 not in matrix", fontsize=9
        )
    ax_h.set_xlabel("Months", fontsize=8)
    ax_h.legend(fontsize=7)

    # ── I: Mutation frequency bar ──────────────────────────
    ax_i = fig.add_subplot(gs_f[2, 2])
    genes_bar = [
        g for g in [
            "CTNNB1","TP53","ARID1A","AXIN1",
            "NFE2L2","RB1","PIK3CA","PTEN",
            "TSC1","ARID2","RNF43","TERT",
        ]
        if mut_matrix[g][hcc_idx].sum() > 0
    ]
    if genes_bar:
        freqs = [
            100 * mut_matrix[g][hcc_idx].sum()
            / max(len(hcc_idx), 1)
            for g in genes_bar
        ]
        colors_bar = [
            "#27ae60" if g == "CTNNB1"
            else "#e74c3c" if g == "TP53"
            else "#2980b9"
            for g in genes_bar
        ]
        y_pos = range(len(genes_bar))
        ax_i.barh(
            y_pos, freqs,
            color=colors_bar, alpha=0.8,
        )
        ax_i.set_yticks(y_pos)
        ax_i.set_yticklabels(
            genes_bar, fontsize=8
        )
        ax_i.set_xlabel(
            "Mutation frequency (%)", fontsize=8
        )
    ax_i.set_title(
        "I — TCGA-LIHC mutation frequencies",
        fontsize=9,
    )

    # ── J: Depth distribution histogram ───────────────────
    ax_j = fig.add_subplot(gs_f[3, 0])
    dm_finite = depth_metab[np.isfinite(depth_metab)]
    if len(dm_finite) > 0:
        ax_j.hist(
            dm_finite, bins=25,
            alpha=0.7, color="#2980b9",
            label=(
                f"TCGA-LIHC n={len(dm_finite)}\n"
                f"mean={dm_finite.mean():.3f}"
            ),
        )
        ax_j.axvline(
            dm_finite.mean(),
            color="#2980b9",
            linestyle="--", linewidth=2,
        )
    ax_j.set_title(
        "J — Metabolic depth distribution\n"
        "(TCGA-LIHC HCC)",
        fontsize=9,
    )
    ax_j.set_xlabel("Metabolic depth", fontsize=8)
    ax_j.legend(fontsize=7)

    # ── K: GLUL by CTNNB1 mutation ────────────────────────
    ax_k = fig.add_subplot(gs_f[3, 1])
    if "GLUL" in gc:
        ctnnb1_mut_k = mut_matrix["CTNNB1"][hcc_idx]
        glul_v = df_hcc["GLUL"].values
        valid_glul = np.isfinite(glul_v)
        m_m  = (ctnnb1_mut_k == 1) & valid_glul
        m_w  = (ctnnb1_mut_k == 0) & valid_glul
        if m_m.sum() >= 3:
            ax_k.hist(
                glul_v[m_m], bins=20,
                alpha=0.6, color="#27ae60",
                label=f"CTNNB1-mut n={m_m.sum()}",
            )
        if m_w.sum() >= 3:
            ax_k.hist(
                glul_v[m_w], bins=20,
                alpha=0.6, color="#e74c3c",
                label=f"CTNNB1-WT n={m_w.sum()}",
            )
        rv_gl, pv_gl = safe_pearsonr(
            ctnnb1_mut_k.astype(float),
            glul_v,
        )
        ax_k.set_title(
            f"K — GLUL by CTNNB1 mut\n"
            f"r={rv_gl:+.3f} {fmt_p(pv_gl)}",
            fontsize=9,
        )
        ax_k.set_xlabel(
            "GLUL expression", fontsize=8
        )
        ax_k.legend(fontsize=7)
    else:
        ax_k.set_title(
            "K — GLUL not in matrix", fontsize=9
        )

    # ── L: Summary ─────────────────────────────────────────
    ax_l = fig.add_subplot(gs_f[3, 2])
    ax_l.axis("off")

    p_ctnnb1_str = "N/A"
    p_tp53_str   = "N/A"
    if ctnnb1_res and "p" in ctnnb1_res:
        v = ctnnb1_res["p"]
        if not np.isnan(v):
            p_ctnnb1_str = f"{v:.4f}"
    if "TP53" in tp53_res:
        v = tp53_res["TP53"]["p"]
        if not np.isnan(v):
            p_tp53_str = f"{v:.4f}"

    summary = (
        "L — SCRIPT 3 SUMMARY\n"
        "─────────────────────────────\n"
        "Dataset: TCGA-LIHC\n\n"
        "PREDICTIONS:\n"
        "  S3-P1: metab score OS p<0.01\n"
        "  S3-P2: CTNNB1-mut better OS\n"
        f"         p={p_ctnnb1_str}\n"
        "  S3-P3: TP53-mut worse OS\n"
        f"         p={p_tp53_str}\n"
        "  S3-P4: CTNNB1-mut shallower\n"
        "  S3-P5: C1 deepest iCluster\n"
        "  S3-P6: CD8A falls with depth\n"
        "  S3-P7: depth indep stage/grade\n\n"
        "KEY REPLICATIONS:\n"
        "  Metabolic score OS\n"
        "  SMAD3 cross-cancer (3rd)\n"
        "  SOX4 OS replication\n"
        "  EZH2+HDAC glandular lock\n\n"
        "OrganismCore | Doc 92c | 2026-03-02"
    )
    ax_l.text(
        0.03, 0.97, summary,
        transform=ax_l.transAxes,
        fontsize=7.5,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(
            boxstyle="round",
            facecolor="#f8f8f8",
            edgecolor="#cccccc",
        ),
    )

    out = os.path.join(
        RESULTS_DIR, "hcc_tcga_lihc_s3.png"
    )
    plt.savefig(
        out, dpi=150, bbox_inches="tight"
    )
    log(f"\n  Figure saved: {out}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 65)
    log("HEPATOCELLULAR CARCINOMA — SCRIPT 3")
    log("Dataset: TCGA-LIHC")
    log("Framework: OrganismCore")
    log("Doc: 92c | Date: 2026-03-02")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED 2026-03-02:")
    log("S3-P1: Metab score OS p<0.01 (TCGA)")
    log("S3-P2: CTNNB1-mutant better OS (HCC-P5)")
    log("S3-P3: TP53-mutant worse OS")
    log("S3-P4: CTNNB1-mutant shallower depth")
    log("S3-P5: iCluster C1 deepest")
    log("S3-P6: CD8A falls with depth")
    log("S3-P7: Depth indep of stage/grade (Cox)")

    # ── Download ──────────────────────────────────────────
    log("")
    log("=" * 65)
    log("STEP 0: DATA ACQUISITION")
    log("=" * 65)

    # Expression — try multiple Xena URLs
    expr_urls = [
        XENA_BASE + "TCGA-LIHC.htseq_fpkm-uq.tsv.gz",
        XENA_BASE + "TCGA-LIHC.htseq_fpkm.tsv.gz",
        XENA_BASE + "TCGA-LIHC.star_fpkm-uq.tsv.gz",
        ("https://tcga.xenahubs.net/download/"
         "TCGA.LIHC.sampleMap/"
         "HiSeqV2_PANCAN.gz"),
        ("https://tcga.xenahubs.net/download/"
         "TCGA.LIHC.sampleMap/HiSeqV2.gz"),
    ]
    ok_expr = try_download_multi(
        expr_urls, EXPR_FILE, "TCGA-LIHC expression"
    )

    # Survival
    surv_urls = [
        XENA_BASE + "TCGA-LIHC.survival.tsv.gz",
        ("https://tcga.xenahubs.net/download/"
         "TCGA.LIHC.sampleMap/"
         "TCGA.LIHC.sampleMap_survival.txt.gz"),
    ]
    ok_surv = try_download_multi(
        surv_urls, SURV_FILE, "TCGA-LIHC survival"
    )

    # Phenotype
    pheno_urls = [
        XENA_BASE + "TCGA-LIHC.GDC_phenotype.tsv.gz",
        ("https://tcga.xenahubs.net/download/"
         "TCGA.LIHC.sampleMap/"
         "TCGA.LIHC_clinicalMatrix.gz"),
    ]
    ok_pheno = try_download_multi(
        pheno_urls, PHENO_FILE, "TCGA-LIHC phenotype"
    )

    # Mutations
    mut_urls = [
        XENA_BASE + "TCGA-LIHC.mutect2_snv.tsv.gz",
        ("https://tcga.xenahubs.net/download/"
         "TCGA.LIHC.sampleMap/"
         "mutation_curated_wustl.gz"),
    ]
    ok_mut = try_download_multi(
        mut_urls, MUT_FILE, "TCGA-LIHC mutations"
    )

    if not ok_expr:
        log("FATAL: Expression download failed")
        log("Manual download instructions:")
        log("  1. Go to https://xenabrowser.net/datapages/")
        log("  2. Search TCGA-LIHC")
        log("  3. Download: HTSeq - FPKM-UQ")
        log(f"  4. Save to: {EXPR_FILE}")
        write_log()
        return

    # ── Parse expression ──────────────────────────────────
    df_raw, sample_ids, needs_ensembl = (
        parse_expression(EXPR_FILE)
    )

    if needs_ensembl or df_raw is None:
        log("  Switching to Ensembl ID parser...")
        df_raw, sample_ids = parse_expression_ensembl(
            EXPR_FILE
        )

    if df_raw is None or len(df_raw) == 0:
        log("FATAL: Expression matrix empty")
        log("Check file format and gene IDs")
        write_log()
        return

    log(f"\n  Expression matrix: {df_raw.shape}")
    log(f"  Samples: {len(sample_ids)}")
    log(f"  Genes: {list(df_raw.columns)[:10]}...")

    # ── Identify tumour vs normal samples ─────────────────
    # TCGA barcodes:
    # TCGA-XX-XXXX-01 = primary tumour
    # TCGA-XX-XXXX-11 = adjacent normal
    # Sample type code is chars 13-15
    sample_type_code = np.array([
        s[13:15] if len(s) >= 15 else "??"
        for s in sample_ids
    ])
    tumour_mask = sample_type_code == "01"
    normal_mask = sample_type_code == "11"

    log(f"\n  Sample type codes:")
    from collections import Counter
    sc = Counter(sample_type_code)
    for k, v in sorted(
        sc.items(), key=lambda x: -x[1]
    ):
        log(f"    {k}: {v}")

    log(f"  Tumour (01): {tumour_mask.sum()}")
    log(f"  Normal (11): {normal_mask.sum()}")

    if tumour_mask.sum() < 10:
        log("  WARNING: Few tumour samples — "
            "checking alternative coding")
        # Some Xena files use full barcode or
        # different slice positions
        tumour_mask = np.array([
            (
                "-01" in s
                or s.endswith("01A")
                or s.endswith("01B")
            )
            for s in sample_ids
        ])
        normal_mask = np.array([
            (
                "-11" in s
                or s.endswith("11A")
            )
            for s in sample_ids
        ])
        log(f"  Tumour (retry): {tumour_mask.sum()}")
        log(f"  Normal (retry): {normal_mask.sum()}")

    if tumour_mask.sum() < 10:
        log("  Treating all samples as tumour")
        tumour_mask = np.ones(
            len(sample_ids), dtype=bool
        )
        normal_mask = np.zeros(
            len(sample_ids), dtype=bool
        )

    hcc_idx = np.where(tumour_mask)[0]

    df_hcc = df_raw[tumour_mask].reset_index(
        drop=True
    )
    df_nor = df_raw[normal_mask].reset_index(
        drop=True
    )

    log(f"\n  HCC samples: {len(df_hcc)}")
    log(f"  Normal samples: {len(df_nor)}")
    log(f"  Genes in matrix: {df_hcc.shape[1]}")

    # ── Parse survival + clinical ─────────────────────────
    clin = parse_survival_robust(
        SURV_FILE, PHENO_FILE, sample_ids
    )

    os_time  = clin["os_time"]
    os_event = clin["os_event"]
    stage    = clin["stage"]
    grade    = clin["grade"]
    age      = clin["age"]

    valid_os = (
        ~np.isnan(os_time[hcc_idx])
        & ~np.isnan(os_event[hcc_idx])
        & (os_time[hcc_idx] > 0)
    )
    log(f"\n  OS valid (HCC): {valid_os.sum()}")
    log(f"  OS events: "
        f"{int(os_event[hcc_idx][valid_os].sum())}")

    if valid_os.sum() < 20:
        log("  WARNING: Few OS events — "
            "survival analysis will be limited")

    # ── Parse mutations ───────────────────────────────────
    mut_matrix = parse_mutations(
        MUT_FILE, sample_ids
    )

    # ── Build depth scores ────────────────────────────────
    log("")
    log("=" * 65)
    log("DEPTH SCORES — TCGA-LIHC")
    log("=" * 65)

    depth_metab = build_depth(
        df_hcc,
        METAB_SWITCH,
        PROG_FA,
        "HCC_DEPTH_V2 (metabolic)",
    )

    # Pure metabolic score (switch genes only)
    gc = list(df_hcc.columns)
    metab_genes_avail = [
        g for g in METAB_SWITCH if g in gc
    ]
    if len(metab_genes_avail) >= 3:
        metab_arr   = df_hcc[metab_genes_avail].values
        metab_mean  = np.nanmean(metab_arr, axis=1)
        depth_pure_metab = 1 - norm01(metab_mean)
    else:
        depth_pure_metab = depth_metab.copy()

    log(f"\n  Pure metabolic score:")
    log(f"    Genes: {metab_genes_avail}")
    log(f"    mean={np.nanmean(depth_pure_metab):.4f} "
        f"std={np.nanstd(depth_pure_metab):.4f}")

    # ── Normal vs HCC comparison ──────────────────────────
    if len(df_nor) >= 5:
        log("")
        log("=" * 65)
        log("NORMAL vs HCC — TCGA-LIHC")
        log("(replication of Script 1 findings)")
        log("=" * 65)

        priority_genes = [
            "AFP","HNF4A","FOXA1","FOXA2",
            "ALB","CYP3A4","ALDOB","PCK1",
            "G6PC","TTR","EZH2","HDAC2",
            "SOX4","EPCAM","GPC3","MYC",
            "CTNNB1","TOP2A","MKI67","AURKA",
        ]
        log(f"  {'Gene':<12} {'Normal':>10} "
            f"{'HCC':>10} {'FC%':>8}  p-value")
        log(f"  {'-'*58}")

        for gene in priority_genes:
            if gene not in gc:
                continue
            n_v = df_nor[gene].dropna().values
            h_v = df_hcc[gene].dropna().values
            if len(n_v) < 3 or len(h_v) < 3:
                continue
            nm  = n_v.mean()
            hm  = h_v.mean()
            fc  = (
                100*(hm - nm)/abs(nm)
                if nm != 0 else np.nan
            )
            _, p = safe_mwu(h_v, n_v)
            log(f"  {gene:<12} {nm:>10.4f} "
                f"{hm:>10.4f} {fc:>+8.1f}%  "
                f"{fmt_p(p)}")

    # ── Depth correlations ──���─────────────────────────────
    log("")
    log("=" * 65)
    log("DEPTH CORRELATIONS — TCGA-LIHC HCC")
    log("(Cross-cohort replication of Script 1)")
    log("=" * 65)

    corrs = []
    for gene in sorted(gc):
        rv, pv = safe_pearsonr(
            depth_pure_metab,
            df_hcc[gene].values,
        )
        if not np.isnan(rv):
            corrs.append((gene, rv, pv))

    corrs.sort(key=lambda x: x[1], reverse=True)

    log(f"\n  TOP 15 POSITIVE (FA genes):")
    for g, r, p in corrs[:15]:
        log(f"  {g:<12} r={r:>+.4f}  {fmt_p(p)}")

    log(f"\n  TOP 15 NEGATIVE (switch genes):")
    for g, r, p in corrs[-15:][::-1]:
        log(f"  {g:<12} r={r:>+.4f}  {fmt_p(p)}")

    log(f"\n  KEY PREDICTION REPLICATIONS:")
    key_genes = {
        "HNF4A":  ("<", -0.30, "switch"),
        "CYP3A4": ("<", -0.50, "switch"),
        "ALDOB":  ("<", -0.50, "switch"),
        "AFP":    (">", +0.40, "FA"),
        "EZH2":   (">", +0.40, "FA/epigenetic"),
        "HDAC2":  (">", +0.40, "FA/epigenetic"),
        "SOX4":   (">", +0.40, "FA/progenitor"),
        "EPCAM":  (">", +0.30, "FA/progenitor"),
        "TOP2A":  (">", +0.40, "FA/cell-cycle"),
        "MKI67":  (">", +0.40, "FA/cell-cycle"),
        "CD8A":   ("<", -0.10, "immune"),
        "SMAD3":  (">", +0.10, "TGF-B"),
        "GLUL":   (">", +0.10, "Wnt"),
    }
    log(f"  {'Gene':<12} {'Role':<15} "
        f"{'r':>8}  p-value    Pred  Result")
    log(f"  {'-'*68}")
    for gene, (direction, thr, role) in (
        key_genes.items()
    ):
        if gene not in gc:
            log(f"  {gene:<12} NOT IN MATRIX")
            continue
        rv, pv = safe_pearsonr(
            depth_pure_metab,
            df_hcc[gene].values,
        )
        if np.isnan(rv):
            continue
        ok = (
            rv > thr if direction == ">"
            else rv < thr
        )
        sym     = "✓" if ok else "✗"
        thr_str = (
            f"{'>' if direction=='>' else '<'}"
            f"{thr:+.2f}"
        )
        log(f"  {gene:<12} {role:<15} "
            f"{rv:>+8.4f}  {fmt_p(pv)}  "
            f"{thr_str:>7}  {sym}")

    # ── S3-2: Metabolic score replication ─────────────────
    metabolic_score_replication(
        df_hcc, os_time, os_event, hcc_idx
    )

    # ── S3-3: CTNNB1 mutation survival ────────────────────
    ctnnb1_res = ctnnb1_mutation_survival(
        mut_matrix, os_time, os_event,
        hcc_idx, df_hcc,
    )

    # ── S3-4: TP53 + all mutation survival ────────────────
    tp53_res = tp53_mutation_survival(
        mut_matrix, os_time, os_event, hcc_idx
    )

    # ── S3-5: CTNNB1 mutation vs depth ───────────────────
    ctnnb1_depth_analysis(
        mut_matrix, depth_pure_metab,
        depth_metab, df_hcc, hcc_idx,
    )

    # ── S3-6: Immune vs depth ────────────────────────────
    immune_res = immune_depth_analysis(
        df_hcc, depth_pure_metab
    )

    # ── S3-7: Cox multivariate ───────────────────────────
    cox_multivariate(
        df_hcc, depth_pure_metab,
        os_time, os_event, hcc_idx,
        stage, grade, age, mut_matrix,
    )

    # ── Cross-cohort survival comparison ─────────────────
    log("")
    log("=" * 65)
    log("CROSS-COHORT DEPTH COMPARISON")
    log("GSE14520 (Script 1) vs TCGA-LIHC (Script 3)")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    valid = (
        ~np.isnan(t) & ~np.isnan(e)
        & ~np.isnan(depth_pure_metab) & (t > 0)
    )

    if valid.sum() >= 10:
        med = np.median(depth_pure_metab[valid])
        hi  = depth_pure_metab[valid] >= med
        lo  = ~hi
        p   = logrank_p(
            t[valid][hi], e[valid][hi],
            t[valid][lo], e[valid][lo],
        )
        mh  = t[valid][hi].mean()
        ml  = t[valid][lo].mean()
        log(f"  TCGA-LIHC metabolic score OS: "
            f"{fmt_p(p)}")
        log(f"  Deep={mh:.1f}mo  Shallow={ml:.1f}mo")
        log(f"  GSE14520 Script 1 OS: p=3.80e-04 ***")
        log(f"  GSE14520 Script 2 metab OS: "
            f"p=1.78e-05 ***")
        log(f"  Replication: "
            f"{'✓' if not np.isnan(p) and p < 0.05 else '✗'}")

    # ── SMAD3 cross-cancer replication ───────────────────
    log("")
    log("=" * 65)
    log("SMAD3 CROSS-CANCER REPLICATION")
    log("Confirmed: BLCA (Script 91)")
    log("Confirmed: HCC GSE14520 (Script 1)")
    log("Test: HCC TCGA-LIHC (Script 3)")
    log("=" * 65)

    if "SMAD3" in gc:
        sm3   = df_hcc["SMAD3"].values
        med_s = np.nanmedian(sm3)
        s_hi  = sm3 >= med_s
        s_lo  = ~s_hi
        p_sm3 = logrank_p(
            t[s_hi], e[s_hi],
            t[s_lo], e[s_lo],
        )
        v_h = (
            ~np.isnan(t[s_hi])
            & ~np.isnan(e[s_hi])
            & (t[s_hi] > 0)
        )
        v_l = (
            ~np.isnan(t[s_lo])
            & ~np.isnan(e[s_lo])
            & (t[s_lo] > 0)
        )
        m_h = (
            t[s_hi][v_h].mean()
            if v_h.sum() > 0 else np.nan
        )
        m_l = (
            t[s_lo][v_l].mean()
            if v_l.sum() > 0 else np.nan
        )
        log(f"  SMAD3 OS: {fmt_p(p_sm3)}")
        log(f"  SMAD3-hi={m_h:.1f}mo "
            f"SMAD3-lo={m_l:.1f}mo")
        rep = (
            not np.isnan(p_sm3)
            and p_sm3 < 0.05
            and m_h < m_l
        )
        log(f"  Cross-cancer SMAD3 OS: "
            f"BLCA ✓ | GSE14520-HCC ✓ | "
            f"TCGA-HCC "
            f"{'✓' if rep else '✗'}")

    # ── SOX4 replication ─────────────────────────────────
    log("")
    log("=" * 65)
    log("SOX4 OS REPLICATION")
    log("GSE14520 p=3.30e-04 ***")
    log("Test: TCGA-LIHC")
    log("=" * 65)

    if "SOX4" in gc:
        sox4_v  = df_hcc["SOX4"].values
        med_s4  = np.nanmedian(sox4_v)
        s4_hi   = sox4_v >= med_s4
        s4_lo   = ~s4_hi
        p_sox4  = logrank_p(
            t[s4_hi], e[s4_hi],
            t[s4_lo], e[s4_lo],
        )
        v_h4 = (
            ~np.isnan(t[s4_hi])
            & ~np.isnan(e[s4_hi])
            & (t[s4_hi] > 0)
        )
        v_l4 = (
            ~np.isnan(t[s4_lo])
            & ~np.isnan(e[s4_lo])
            & (t[s4_lo] > 0)
        )
        m_h4 = (
            t[s4_hi][v_h4].mean()
            if v_h4.sum() > 0 else np.nan
        )
        m_l4 = (
            t[s4_lo][v_l4].mean()
            if v_l4.sum() > 0 else np.nan
        )
        rep_sox4 = (
            not np.isnan(p_sox4)
            and p_sox4 < 0.05
            and m_h4 < m_l4
        )
        log(f"  SOX4 OS TCGA: {fmt_p(p_sox4)}")
        log(f"  SOX4-hi={m_h4:.1f}mo "
            f"SOX4-lo={m_l4:.1f}mo")
        log(f"  Replication: "
            f"{'✓ CONFIRMED' if rep_sox4 else '✗ NOT CONFIRMED'}")

    # ── Generate figure ───────────────────────────────────
    generate_figure(
        df_hcc, depth_pure_metab, depth_metab,
        os_time, os_event, hcc_idx,
        ctnnb1_res, tp53_res, immune_res,
        mut_matrix,
    )

    # ── Save scores ───────────────────────────────────────
    scores_df = pd.DataFrame({
        "sample_id": [
            sample_ids[i] for i in hcc_idx
        ],
        "depth_v2_metabolic": depth_metab,
        "depth_pure_metab":   depth_pure_metab,
    })
    scores_df.to_csv(
        os.path.join(
            RESULTS_DIR, "depth_scores_s3.csv"
        ),
        index=False,
    )
    log(f"\n  Scores saved: "
        f"{RESULTS_DIR}/depth_scores_s3.csv")

    write_log()
    log(f"\n  Log:    {LOG_FILE}")
    log(f"  Output: {RESULTS_DIR}")
    log("\n=== SCRIPT 3 COMPLETE ===")
    log("\nPaste full output for Document 92c.")


if __name__ == "__main__":
    main()
