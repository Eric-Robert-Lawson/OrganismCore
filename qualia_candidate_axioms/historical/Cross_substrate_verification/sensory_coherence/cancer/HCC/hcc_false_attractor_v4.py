"""
HEPATOCELLULAR CARCINOMA — FALSE ATTRACTOR ANALYSIS
SCRIPT 4
Dataset: TCGA-LIHC (continued)
Purpose: Mutation survival (HCC-P5),
         full Cox multivariate,
         SMARCA4/TWIST1 survival,
         checkpoint inhibitor hypothesis,
         GDC MAF download

Doc: 92d | Date: 2026-03-02

SCRIPT 4 TARGETS (locked 2026-03-02):

S4-1: GDC MAF download
      TCGA-LIHC somatic mutations
      MuTect2 caller, masked MAF
      Direct GDC API (no auth for
      open-access MAF files)

S4-2: CTNNB1 mutation survival (HCC-P5)
      Primary pending test since Script 1.
      CTNNB1 exon 3 mut vs wild-type OS.
      Prediction: mutant better OS.

S4-3: TP53 mutation survival
      TP53 mut vs wild-type OS.
      Prediction: mutant worse OS.

S4-4: CTNNB1 mutation vs depth
      Are CTNNB1-mutant HCCs shallower?
      Prediction: mutant = shallower
      metabolic depth score.

S4-5: All HCC driver mutation survival
      CTNNB1, TP53, ARID1A, AXIN1,
      NFE2L2, RB1, TSC1/2, ARID2,
      RNF43, HNF1A, TERT
      Comprehensive mutation OS table.

S4-6: Full Cox multivariate
      Depth + stage + grade + age
      + CTNNB1 mut + TP53 mut
      Using GDC clinical for proper
      stage encoding.

S4-7: SMARCA4 survival
      New top FA gene from Script 3.
      r=+0.52 in TCGA-LIHC.
      Prediction: SMARCA4-hi worse OS.

S4-8: TWIST1 survival
      New top FA gene from Script 3.
      r=+0.50 in TCGA-LIHC.
      Prediction: TWIST1-hi worse OS
      (EMT driver = deep attractor).

S4-9: Checkpoint inhibitor hypothesis
      CD274 (PD-L1) + PDCD1 (PD-1)
      vs depth score.
      Depth × CD274 interaction with OS.
      Prediction: deep + CD274-hi = worst OS
      AND = best checkpoint responders.

S4-10: Mutation × depth interaction
       CTNNB1-mut deep vs CTNNB1-mut shallow
       TP53-mut deep vs TP53-mut shallow
       Does depth stratify within mutation
       groups?

PREDICTIONS LOCKED 2026-03-02:
  S4-P1: CTNNB1-mutant better OS (HCC-P5)
  S4-P2: TP53-mutant worse OS
  S4-P3: CTNNB1-mutant shallower depth
  S4-P4: SMARCA4-hi worse OS
  S4-P5: TWIST1-hi worse OS
  S4-P6: CD274 rises with depth (immune
         exhaustion marker)
  S4-P7: Depth independent of stage/grade
         and mutation status in Cox

Author: Eric Robert Lawson
Framework: OrganismCore
"""

import os
import re
import gzip
import json
import time
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
RESULTS_DIR = os.path.join(BASE_DIR, "results_s4")
LOG_FILE    = os.path.join(RESULTS_DIR,
                           "analysis_log_s4.txt")
os.makedirs(TCGA_DIR,    exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Files from Script 3 (already present)
EXPR_FILE  = os.path.join(
    TCGA_DIR, "TCGA-LIHC.expr.tsv.gz"
)
SURV_FILE  = os.path.join(
    TCGA_DIR, "TCGA-LIHC.survival.tsv.gz"
)
PHENO_FILE = os.path.join(
    TCGA_DIR, "TCGA-LIHC.pheno.tsv.gz"
)

# New files for Script 4
MAF_FILE   = os.path.join(
    TCGA_DIR, "TCGA-LIHC.maf.gz"
)
CLIN_FILE  = os.path.join(
    TCGA_DIR, "TCGA-LIHC.clinical.tsv.gz"
)

# GDC API
GDC_BASE   = "https://api.gdc.cancer.gov"
GDC_FILES  = f"{GDC_BASE}/files"
GDC_DATA   = f"{GDC_BASE}/data"

# ============================================================
# GENES
# ============================================================

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

MUT_GENES_TRACK = [
    "CTNNB1","TP53","ARID1A","AXIN1",
    "NFE2L2","RB1","PIK3CA","PTEN",
    "TSC1","TSC2","ARID2","RNF43",
    "KMT2D","SETD2","HNF1A","TERT",
    "BAP1","CDKN2A","ALB","IDH1",
    "IDH2","SMARCA4","ELF3","MET",
    "KEAP1","ACVR2A","RPL22",
]

IMMUNE_GENES = [
    "CD274","PDCD1","CD8A","CD4",
    "FOXP3","CD68","LAG3","TIGIT",
    "HAVCR2","CTLA4","CD247",
    "GZMB","PRF1","IFNG",
]

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
    m1 = np.isfinite(t1) & np.isfinite(e1) & (t1>0)
    m0 = np.isfinite(t0) & np.isfinite(e0) & (t0>0)
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

def safe_km(kmf, t, e, label):
    t = np.asarray(t, dtype=float)
    e = np.asarray(e, dtype=float)
    v = np.isfinite(t) & np.isfinite(e) & (t > 0)
    if v.sum() < 5:
        return False
    kmf.fit(t[v], e[v], label=label)
    return True

# ============================================================
# S4-1: GDC MAF DOWNLOAD
# ============================================================

def download_gdc_maf():
    """
    Download TCGA-LIHC somatic MAF from GDC.
    Uses the GDC Files API to find the
    MuTect2 masked MAF file UUID, then
    downloads via the data endpoint.
    Open-access files require no token.
    """
    log("")
    log("=" * 65)
    log("S4-1: GDC MAF DOWNLOAD")
    log("=" * 65)

    if os.path.exists(MAF_FILE):
        sz = os.path.getsize(MAF_FILE)
        log(f"  Already present: {MAF_FILE} "
            f"({sz:,} bytes)")
        return True

    log("  Querying GDC Files API for "
        "TCGA-LIHC MAF...")

    # Query for TCGA-LIHC MuTect2 masked MAF
    query = {
        "filters": {
            "op": "and",
            "content": [
                {
                    "op": "=",
                    "content": {
                        "field":
                        "cases.project.project_id",
                        "value": "TCGA-LIHC",
                    },
                },
                {
                    "op": "=",
                    "content": {
                        "field": "data_type",
                        "value":
                        "Masked Somatic Mutation",
                    },
                },
                {
                    "op": "=",
                    "content": {
                        "field": "data_format",
                        "value": "MAF",
                    },
                },
                {
                    "op": "=",
                    "content": {
                        "field":
                        "analysis.workflow_type",
                        "value":
                        "MuTect2 Annotation",
                    },
                },
            ],
        },
        "fields": (
            "file_id,file_name,"
            "data_type,file_size,"
            "access"
        ),
        "size": "10",
    }

    try:
        r = requests.post(
            GDC_FILES,
            json=query,
            headers={
                "Content-Type":
                "application/json",
            },
            timeout=60,
        )
        log(f"  GDC Files query: HTTP {r.status_code}")

        if r.status_code != 200:
            log(f"  Query failed: {r.text[:200]}")
            return _download_maf_fallback()

        hits = r.json().get(
            "data", {}
        ).get("hits", [])
        log(f"  Files found: {len(hits)}")

        if not hits:
            log("  No MAF files found in GDC")
            return _download_maf_fallback()

        for h in hits:
            log(f"    {h.get('file_id','')} "
                f"{h.get('file_name','')} "
                f"{h.get('access','')} "
                f"{h.get('file_size',0):,} bytes")

        # Pick first open-access file
        file_id = None
        for h in hits:
            if h.get("access","") == "open":
                file_id = h["file_id"]
                log(f"  Selected: {file_id}")
                break
        if file_id is None:
            file_id = hits[0]["file_id"]
            log(f"  Using first: {file_id} "
                f"(may require token)")

        # Download
        dl_url = f"{GDC_DATA}/{file_id}"
        log(f"  Downloading: {dl_url}")
        r2 = requests.get(
            dl_url, stream=True, timeout=600,
            headers={
                "User-Agent":
                "OrganismCore/1.0",
            },
        )
        log(f"  Download HTTP: {r2.status_code}")

        if r2.status_code == 200:
            raw = b""
            for chunk in r2.iter_content(
                chunk_size=1024*1024
            ):
                raw += chunk
            # File may be a tar.gz containing
            # the MAF — handle both cases
            if raw[:2] == b"\x1f\x8b":
                # Already gzipped
                with open(MAF_FILE, "wb") as f:
                    f.write(raw)
            elif raw[:5] == b"PK\x03\x04":
                # ZIP archive — extract MAF
                import zipfile, io
                zf   = zipfile.ZipFile(
                    io.BytesIO(raw)
                )
                for name in zf.namelist():
                    if name.endswith(".maf") or \
                       name.endswith(".maf.gz"):
                        content = zf.read(name)
                        if not name.endswith(".gz"):
                            with gzip.open(
                                MAF_FILE, "wb"
                            ) as f:
                                f.write(content)
                        else:
                            with open(
                                MAF_FILE, "wb"
                            ) as f:
                                f.write(content)
                        break
            else:
                # Plain text MAF — gzip it
                with gzip.open(
                    MAF_FILE, "wb"
                ) as f:
                    f.write(raw)

            sz = os.path.getsize(MAF_FILE)
            log(f"  Saved: {MAF_FILE} "
                f"({sz:,} bytes)")
            return sz > 1000

        log(f"  Download failed: "
            f"{r2.status_code}")
        return _download_maf_fallback()

    except Exception as e:
        log(f"  GDC error: {e}")
        return _download_maf_fallback()


def _download_maf_fallback():
    """
    Fallback: try known GDC UUIDs for
    TCGA-LIHC MuTect2 masked MAF,
    then cBioPortal mutations TSV.
    """
    log("")
    log("  Trying MAF fallback sources...")

    # Known GDC file IDs for TCGA-LIHC
    # MuTect2 masked MAF (public as of 2024)
    KNOWN_IDS = [
        # TCGA-LIHC MuTect2 Annotation MAF
        "8f2dcc46-cdc0-4a07-ae53-b6c2f7b5ad9b",
        "1c8cfe5f-e52d-41ba-94da-f15ea1337c05",
        "c48e7ede-5aaa-40b5-a9fc-88fa30adde89",
    ]

    for uid in KNOWN_IDS:
        url = f"{GDC_DATA}/{uid}"
        log(f"  Trying UUID: {uid}")
        try:
            r = requests.get(
                url, stream=True,
                timeout=120,
                headers={
                    "User-Agent":
                    "OrganismCore/1.0"
                },
            )
            log(f"  HTTP {r.status_code}")
            if r.status_code == 200:
                raw = r.content
                if len(raw) > 10000:
                    with gzip.open(
                        MAF_FILE, "wb"
                    ) as f:
                        if raw[:2] == b"\x1f\x8b":
                            f.write(
                                gzip.decompress(raw)
                            )
                        else:
                            f.write(raw)
                    sz = os.path.getsize(MAF_FILE)
                    log(f"  Saved: {sz:,} bytes")
                    return True
        except Exception as e:
            log(f"  Error: {e}")

    # Final fallback: cBioPortal bulk mutation
    log("")
    log("  Trying cBioPortal bulk download...")
    cbio_url = (
        "https://www.cbioportal.org/api"
        "/molecular-profiles"
        "/lihc_tcga_mutations"
        "/mutations/fetch"
        "?projection=DETAILED"
    )
    try:
        # Get all sample IDs first
        r_s = requests.get(
            "https://www.cbioportal.org/api"
            "/studies/lihc_tcga/samples"
            "?pageSize=10000",
            timeout=60,
            headers={"Accept": "application/json"},
        )
        if r_s.status_code != 200:
            log(f"  Sample list HTTP "
                f"{r_s.status_code}")
            return False

        all_sids = [
            s["sampleId"]
            for s in r_s.json()
        ]
        log(f"  Samples: {len(all_sids)}")

        all_muts = []
        BATCH    = 300
        for i in range(
            0, len(all_sids), BATCH
        ):
            batch   = all_sids[i:i+BATCH]
            payload = {
                "sampleIds": batch,
                "hugoGeneSymbols":
                    MUT_GENES_TRACK,
            }
            r_m = requests.post(
                cbio_url,
                json=payload,
                headers={
                    "Accept":
                    "application/json",
                    "Content-Type":
                    "application/json",
                },
                timeout=120,
            )
            if r_m.status_code == 200:
                batch_muts = r_m.json()
                all_muts.extend(batch_muts)
                log(f"  Batch "
                    f"{i//BATCH+1}: "
                    f"n={len(batch_muts)}")
            time.sleep(0.3)

        log(f"  Total mutations: {len(all_muts)}")

        if len(all_muts) == 0:
            log("  cBioPortal returned 0 mutations")
            log("  Manual download required:")
            log("  https://portal.gdc.cancer.gov/")
            log("  Project: TCGA-LIHC")
            log("  File type: Masked Somatic Mutation")
            log(f"  Save to: {MAF_FILE}")
            return False

        # Write MAF-format TSV
        lines = [
            "Hugo_Symbol\t"
            "Tumor_Sample_Barcode\t"
            "Variant_Classification\t"
            "HGVSp_Short\t"
            "Chromosome\t"
            "Start_Position\t"
            "Reference_Allele\t"
            "Tumor_Seq_Allele2"
        ]
        for m in all_muts:
            gene = (
                m.get("gene", {})
                 .get("hugoGeneSymbol", "")
                if isinstance(m.get("gene"), dict)
                else m.get(
                    "hugoGeneSymbol",
                    m.get("gene", "")
                )
            )
            lines.append(
                "\t".join([
                    gene,
                    m.get("sampleId",""),
                    m.get("mutationType",
                          m.get(
                            "variantClassification",
                            ""
                          )),
                    m.get("proteinChange",
                          m.get("hgvsp","")),
                    str(m.get("chr",
                        m.get("chromosome",""))),
                    str(m.get("startPosition","")),
                    m.get("referenceAllele",""),
                    m.get("variantAllele",""),
                ])
            )

        with gzip.open(
            MAF_FILE, "wt", encoding="utf-8"
        ) as f:
            f.write("\n".join(lines))

        sz = os.path.getsize(MAF_FILE)
        log(f"  MAF saved: {sz:,} bytes "
            f"({len(all_muts)} mutations)")
        return True

    except Exception as e:
        log(f"  cBioPortal fallback error: {e}")
        return False

# ============================================================
# PARSE MAF
# ============================================================

def parse_maf(maf_file, sample_ids):
    log("")
    log("=" * 65)
    log("PARSE MAF / MUTATION FILE")
    log("=" * 65)

    n       = len(sample_ids)
    sid_idx = {
        s: i for i, s in enumerate(sample_ids)
    }
    gene_set = set(MUT_GENES_TRACK)

    mut_matrix = {
        g: np.zeros(n, dtype=int)
        for g in MUT_GENES_TRACK
    }

    if not os.path.exists(maf_file):
        log("  MAF file not found")
        return mut_matrix

    sz = os.path.getsize(maf_file)
    if sz < 200:
        log(f"  MAF file too small ({sz} bytes) "
            f"— empty or header only")
        return mut_matrix

    log(f"  File: {maf_file} ({sz:,} bytes)")

    opener = (
        gzip.open(maf_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if maf_file.endswith(".gz")
        else open(maf_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    hdr      = None
    gene_c   = None
    sample_c = None
    effect_c = None
    n_muts   = 0
    n_skipped = 0

    # Synonymous/benign effect keywords
    BENIGN = [
        "synonymous","silent",
        "3_prime_utr","5_prime_utr",
        "3'utr","5'utr",
        "intron","intergenic",
        "igr","rna","lincRNA",
    ]

    with opener as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            # Skip comment lines
            if line.startswith("#"):
                continue
            if not line.strip():
                continue

            parts = [
                p.strip().strip('"')
                for p in line.split("\t")
            ]

            if hdr is None:
                hdr = [
                    p.upper() for p in parts
                ]
                log(f"  Headers (first 10): "
                    f"{hdr[:10]}")
                for i, h in enumerate(hdr):
                    hl = h.lower()
                    if hl in [
                        "hugo_symbol",
                        "gene","gene_name",
                        "symbol",
                    ]:
                        gene_c = i
                    if any(x in hl for x in [
                        "tumor_sample_barcode",
                        "sample_id","tumor_sample",
                        "sampleid",
                    ]):
                        if sample_c is None:
                            sample_c = i
                    if any(x in hl for x in [
                        "variant_classification",
                        "consequence",
                        "one_consequence",
                        "effect",
                        "mutation_type",
                    ]):
                        if effect_c is None:
                            effect_c = i
                log(f"  gene_c={gene_c} "
                    f"sample_c={sample_c} "
                    f"effect_c={effect_c}")
                continue

            if gene_c is None or \
                    sample_c is None:
                continue
            if len(parts) <= max(
                gene_c, sample_c
            ):
                continue

            gene = parts[gene_c].strip()
            if gene not in gene_set:
                continue

            sid = parts[sample_c].strip()

            # Match sample ID
            idx = sid_idx.get(sid)
            if idx is None:
                # Try 15-char prefix
                for k, v in sid_idx.items():
                    if k[:15] == sid[:15]:
                        idx = v
                        break
            if idx is None:
                # Try 12-char case ID
                for k, v in sid_idx.items():
                    if k[:12] == sid[:12]:
                        idx = v
                        break
            if idx is None:
                n_skipped += 1
                continue

            # Check effect — skip benign
            keep = True
            if effect_c is not None \
                    and effect_c < len(parts):
                eff = parts[effect_c].lower()
                if any(b in eff for b in BENIGN):
                    keep = False

            if keep:
                mut_matrix[gene][idx] = 1
                n_muts += 1

    log(f"\n  Mutations parsed: {n_muts}")
    log(f"  Samples skipped: {n_skipped}")

    log(f"\n  Mutation frequencies (TCGA-LIHC):")
    log(f"  {'Gene':<14} {'n_mut':>6} "
        f"{'freq%':>8}")
    log(f"  {'-'*32}")
    for gene in MUT_GENES_TRACK:
        freq = mut_matrix[gene].sum()
        if freq > 0:
            pct = 100 * freq / n
            log(f"  {gene:<14} {freq:>6} "
                f"{pct:>8.1f}%")

    return mut_matrix

# ============================================================
# REUSE PARSERS FROM SCRIPT 3
# ============================================================

def load_expression_survival(
    expr_file, surv_file, pheno_file
):
    """
    Re-parse expression and survival
    from Script 3 files. Returns
    df (all samples), sample_ids,
    hcc_idx, os_time, os_event,
    stage, grade, age.
    """
    log("")
    log("=" * 65)
    log("LOADING EXPRESSION + SURVIVAL")
    log("(from Script 3 files)")
    log("=" * 65)

    # ── Expression ───────────────���────────────────────────
    opener = (
        gzip.open(expr_file, "rt",
                  encoding="utf-8",
                  errors="ignore")
        if expr_file.endswith(".gz")
        else open(expr_file, "r",
                  encoding="utf-8",
                  errors="ignore")
    )

    genes_wanted = set(
        METAB_SWITCH + PROG_FA + IMMUNE_GENES + [
            "SMARCA4","TWIST1","SMAD3",
            "GLUL","CTNNB1","GPC3",
            "TGFB1","FGFR1","CDK4",
            "VIM","CDH1","CDH2","FN1",
            "SNAI1","SNAI2","ZEB1","ZEB2",
        ]
    )

    sample_ids  = []
    gene_data   = {}
    header_done = False

    with opener as f:
        for line in f:
            line  = line.rstrip("\n")
            parts = line.split("\t")
            if not header_done:
                sample_ids  = [
                    p.strip() for p in parts[1:]
                ]
                header_done = True
                continue
            gene = parts[0].strip().strip('"')
            if gene not in genes_wanted:
                continue
            try:
                vals = [
                    float(p) if p.strip()
                    not in ["","NA","nan",
                             "NaN","NULL"]
                    else np.nan
                    for p in parts[1:]
                ]
            except ValueError:
                continue
            if gene not in gene_data:
                gene_data[gene] = vals
            else:
                ex = np.array(
                    gene_data[gene], dtype=float
                )
                nv = np.array(vals, dtype=float)
                if np.nanvar(nv) > np.nanvar(ex):
                    gene_data[gene] = vals

    n_s = len(sample_ids)
    df  = pd.DataFrame(
        {g: v[:n_s]
         for g, v in gene_data.items()},
        dtype=float,
    )
    log(f"  Expression: {df.shape}")

    # Sample type
    stype = np.array([
        s[13:15] if len(s) >= 15 else "??"
        for s in sample_ids
    ])
    tumour = (
        (stype == "01")
        | np.array([
            "-01" in s for s in sample_ids
        ])
    )
    normal = (
        (stype == "11")
        | np.array([
            "-11" in s for s in sample_ids
        ])
    )

    hcc_idx = np.where(tumour)[0]
    df_hcc  = df[tumour].reset_index(drop=True)
    log(f"  HCC: {tumour.sum()}  "
        f"Normal: {normal.sum()}")

    # ── Survival ──────────────────────────────────────────
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

    def match_sid(sid):
        idx = sid_idx.get(sid)
        if idx is not None:
            return idx
        for k, v in sid_idx.items():
            if k[:15] == sid[:15]:
                return v
        for k, v in sid_idx.items():
            if k[:12] == sid[:12]:
                return v
        return None

    def parse_tsv(fpath):
        if not os.path.exists(fpath):
            return
        opener_ = (
            gzip.open(fpath, "rt",
                      encoding="utf-8",
                      errors="ignore")
            if fpath.endswith(".gz")
            else open(fpath, "r",
                      encoding="utf-8",
                      errors="ignore")
        )
        hdr2 = None
        sc = tc = ec = stc = gc = ac = genc = None
        with opener_ as f:
            for line in f:
                line  = line.rstrip("\n")
                parts = [
                    p.strip().strip('"')
                    for p in line.split("\t")
                ]
                if hdr2 is None:
                    hdr2 = [
                        p.lower() for p in parts
                    ]
                    for i, h in enumerate(hdr2):
                        if h in [
                            "sample","sample_id",
                            "_sample_id","sampleid",
                            "submitter_id",
                            "case_submitter_id",
                        ]:
                            if sc is None:
                                sc = i
                        if h in [
                            "os.time","os_time",
                            "time","_time",
                        ]:
                            tc = i
                        if h in [
                            "os","os_status",
                            "vital_status",
                            "_vital_status",
                            "event","status",
                        ]:
                            ec = i
                        if any(x in h for x in [
                            "stage","ajcc_pathologic",
                            "tumor_stage",
                        ]):
                            if stc is None:
                                stc = i
                        if "grade" in h:
                            if gc is None:
                                gc = i
                        if any(x in h for x in [
                            "age_at","age_diag",
                            "age",
                        ]):
                            if ac is None:
                                ac = i
                        if h in [
                            "gender","sex"
                        ]:
                            if genc is None:
                                genc = i
                    continue
                if sc is None:
                    continue
                if sc >= len(parts):
                    continue
                sid = parts[sc].strip()
                idx = match_sid(sid)
                if idx is None:
                    continue
                if tc is not None \
                        and tc < len(parts):
                    try:
                        tv = float(parts[tc])
                        if tv > 200:
                            tv /= 30.44
                        if tv > 0:
                            os_time[idx] = tv
                    except (ValueError,
                            TypeError):
                        pass
                if ec is not None \
                        and ec < len(parts):
                    v = parts[ec].lower()
                    if v in [
                        "1","dead","deceased",
                        "died",
                    ]:
                        os_event[idx] = 1
                    elif v in [
                        "0","alive","living",
                        "censored",
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
                if stc is not None \
                        and stc < len(parts):
                    v = parts[stc].strip()
                    if v and not stage[idx]:
                        stage[idx] = v
                if gc is not None \
                        and gc < len(parts):
                    v = parts[gc].strip()
                    if v and not grade[idx]:
                        grade[idx] = v
                if ac is not None \
                        and ac < len(parts):
                    try:
                        if np.isnan(age[idx]):
                            age[idx] = float(
                                parts[ac]
                            )
                    except (ValueError,
                            TypeError):
                        pass
                if genc is not None \
                        and genc < len(parts):
                    if not gender[idx]:
                        gender[idx] = (
                            parts[genc].strip()
                        )

    parse_tsv(surv_file)
    parse_tsv(pheno_file)

    valid_os = (
        ~np.isnan(os_time[hcc_idx])
        & ~np.isnan(os_event[hcc_idx])
        & (os_time[hcc_idx] > 0)
    )
    log(f"  OS valid (HCC): {valid_os.sum()} "
        f"events="
        f"{int(os_event[hcc_idx][valid_os].sum())}")

    # Parse stage numeric
    stage_num = np.full(n, np.nan)
    for i, s in enumerate(stage):
        sl = s.lower()
        if re.search(
            r"stage\s*(i[^iv]|i$|1)", sl
        ):
            stage_num[i] = 1
        elif re.search(
            r"stage\s*(ii[^i]|ii$|2)", sl
        ):
            stage_num[i] = 2
        elif re.search(
            r"stage\s*(iii|3)", sl
        ):
            stage_num[i] = 3
        elif re.search(
            r"stage\s*(iv|4)", sl
        ):
            stage_num[i] = 4

    grade_num = np.full(n, np.nan)
    for i, g in enumerate(grade):
        gl = g.lower()
        if re.search(r"g1|grade\s*1|well", gl):
            grade_num[i] = 1
        elif re.search(
            r"g2|grade\s*2|moderate", gl
        ):
            grade_num[i] = 2
        elif re.search(r"g3|grade\s*3|poor", gl):
            grade_num[i] = 3
        elif re.search(r"g4|grade\s*4", gl):
            grade_num[i] = 4

    from collections import Counter
    log(f"  Stage (encoded): "
        f"{dict(Counter(stage_num[hcc_idx][~np.isnan(stage_num[hcc_idx])].astype(int)).most_common(5))}")
    log(f"  Grade (encoded): "
        f"{dict(Counter(grade_num[hcc_idx][~np.isnan(grade_num[hcc_idx])].astype(int)).most_common(5))}")

    return (
        df_hcc, sample_ids, hcc_idx,
        os_time, os_event,
        stage_num, grade_num, age, gender,
    )

# ============================================================
# BUILD DEPTH SCORES
# ============================================================

def build_depth(df, switch, fa, label):
    gc   = list(df.columns)
    sw   = [g for g in switch if g in gc]
    fa_  = [g for g in fa    if g in gc]
    log(f"  {label}:")
    log(f"    Switch ({len(sw)}): {sw}")
    log(f"    FA     ({len(fa_)}): {fa_}")

    n     = len(df)
    depth = np.zeros(n, dtype=float)
    nd    = 0
    if sw:
        depth += (
            1 - norm01(
                df[sw].mean(axis=1).values
            )
        )
        nd += 1
    if fa_:
        depth += norm01(
            df[fa_].mean(axis=1).values
        )
        nd += 1
    if nd > 0:
        depth /= nd

    log(f"    mean={np.nanmean(depth):.4f} "
        f"std={np.nanstd(depth):.4f} "
        f"range={np.nanmin(depth):.4f}–"
        f"{np.nanmax(depth):.4f}")
    return depth

# ============================================================
# S4-2/3: CTNNB1 + TP53 MUTATION SURVIVAL
# ============================================================

def mutation_survival_analysis(
    mut_matrix, os_time, os_event, hcc_idx,
    df_hcc, depth_metab
):
    log("")
    log("=" * 65)
    log("S4-2/3: MUTATION SURVIVAL ANALYSIS")
    log("S4-P1: CTNNB1-mut better OS (HCC-P5)")
    log("S4-P2: TP53-mut worse OS")
    log("=" * 65)

    t  = os_time[hcc_idx]
    e  = os_event[hcc_idx]
    gc = list(df_hcc.columns)

    results = {}

    log(f"\n  {'Gene':<12} {'n_mut':>6} "
        f"{'mut_OS':>10} {'wt_OS':>10}  "
        f"{'logrank':>14}  direction")
    log(f"  {'-'*68}")

    for gene in MUT_GENES_TRACK:
        gm = mut_matrix[gene][hcc_idx]
        n_mut = int(gm.sum())
        if n_mut < 5:
            continue

        mmask = gm == 1
        wmask = gm == 0

        vm = (
            mmask & np.isfinite(t)
            & np.isfinite(e) & (t > 0)
        )
        vw = (
            wmask & np.isfinite(t)
            & np.isfinite(e) & (t > 0)
        )
        m_m = (
            t[vm].mean()
            if vm.sum() > 0 else np.nan
        )
        m_w = (
            t[vw].mean()
            if vw.sum() > 0 else np.nan
        )
        p   = logrank_p(
            t[mmask], e[mmask],
            t[wmask], e[wmask],
        )
        direction = (
            "↑mut=better"
            if m_m > m_w else "↑mut=worse"
        )
        log(f"  {gene:<12} {n_mut:>6} "
            f"{m_m:>10.1f} {m_w:>10.1f}  "
            f"{fmt_p(p)}  {direction}")
        results[gene] = {
            "n_mut":    n_mut,
            "mmask":    mmask,
            "wmask":    wmask,
            "p":        p,
            "m_mut":    m_m,
            "m_wt":     m_w,
            "t":        t,
            "e":        e,
        }

    # Primary prediction checks
    log("")
    for gene, pred_dir, pred_label, p_id in [
        ("CTNNB1", "better",
         "S4-P1: CTNNB1-mut better OS", "P1"),
        ("TP53",   "worse",
         "S4-P2: TP53-mut worse OS",    "P2"),
    ]:
        if gene not in results:
            log(f"  {pred_label}")
            log(f"  STATUS: NOT TESTABLE "
                f"(n_mut<5 or no mut data)")
            continue
        res = results[gene]
        if pred_dir == "better":
            conf = (
                not np.isnan(res["m_mut"])
                and not np.isnan(res["m_wt"])
                and res["m_mut"] > res["m_wt"]
            )
        else:
            conf = (
                not np.isnan(res["m_mut"])
                and not np.isnan(res["m_wt"])
                and res["m_mut"] < res["m_wt"]
            )
        sig = (
            not np.isnan(res["p"])
            and res["p"] < 0.05
        )
        log(f"  {pred_label}")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf and sig else 'DIRECTIONALLY ✓' if conf else 'NOT CONFIRMED ✗'} "
            f"(dir={'✓' if conf else '✗'} "
            f"sig={'✓' if sig else '✗'} "
            f"{fmt_p(res['p'])})")

    # CTNNB1 expression vs mutation
    # (validates that mRNA ≠ pathway activity)
    if "CTNNB1" in gc and "CTNNB1" in results:
        ctnnb1_mut = (
            mut_matrix["CTNNB1"][hcc_idx]
        )
        rv, pv = safe_pearsonr(
            ctnnb1_mut.astype(float),
            df_hcc["CTNNB1"].values,
        )
        log(f"\n  r(CTNNB1_mut, CTNNB1_expr) = "
            f"{rv:+.4f}  {fmt_p(pv)}")

    # GLUL as Wnt proxy
    if "GLUL" in gc and "CTNNB1" in results:
        ctnnb1_mut = (
            mut_matrix["CTNNB1"][hcc_idx]
        )
        glul = df_hcc["GLUL"].values
        mmask = ctnnb1_mut == 1
        wmask = ctnnb1_mut == 0
        if mmask.sum() >= 5:
            m_m = glul[mmask].mean()
            m_w = glul[wmask].mean()
            _, p_g = safe_mwu(
                glul[mmask], glul[wmask]
            )
            rv_g, pv_g = safe_pearsonr(
                ctnnb1_mut.astype(float), glul
            )
            log(f"  GLUL (Wnt proxy) by "
                f"CTNNB1 mutation:")
            log(f"    CTNNB1-mut: {m_m:.4f}  "
                f"CTNNB1-WT: {m_w:.4f}")
            log(f"    MWU: {fmt_p(p_g)}")
            log(f"    r(mut, GLUL) = "
                f"{rv_g:+.4f}  {fmt_p(pv_g)}")
            log(f"    (r>+0.3 expected if "
                f"mutation drives Wnt activity)")

    return results

# ============================================================
# S4-4: CTNNB1 MUTATION vs DEPTH
# ============================================================

def ctnnb1_depth_analysis(
    mut_matrix, depth_metab, hcc_idx, df_hcc
):
    log("")
    log("=" * 65)
    log("S4-4: CTNNB1 MUTATION vs DEPTH")
    log("S4-P3: CTNNB1-mutant shallower")
    log("=" * 65)

    gc = list(df_hcc.columns)

    log(f"\n  Mutation vs depth (metabolic score):")
    log(f"  {'Gene':<14} {'n_mut':>6} "
        f"{'mut_depth':>12} {'wt_depth':>12}  p")
    log(f"  {'-'*58}")

    for gene in MUT_GENES_TRACK:
        gm = mut_matrix[gene][hcc_idx]
        if gm.sum() < 5:
            continue
        mmask = gm == 1
        wmask = gm == 0
        m_m   = depth_metab[mmask].mean()
        m_w   = depth_metab[wmask].mean()
        _, p  = safe_mwu(
            depth_metab[mmask],
            depth_metab[wmask],
        )
        d = (
            "↑shallower" if m_m < m_w
            else "↑deeper"
        )
        log(f"  {gene:<14} {gm.sum():>6} "
            f"{m_m:>12.4f} {m_w:>12.4f}  "
            f"{fmt_p(p)} {d}")

    # Primary prediction
    if "CTNNB1" in [
        g for g in MUT_GENES_TRACK
        if mut_matrix[g][hcc_idx].sum() >= 5
    ]:
        ctnnb1_mut = mut_matrix["CTNNB1"][hcc_idx]
        mmask = ctnnb1_mut == 1
        wmask = ctnnb1_mut == 0
        m_m   = depth_metab[mmask].mean()
        m_w   = depth_metab[wmask].mean()
        conf  = m_m < m_w
        log(f"\n  S4-P3: CTNNB1-mutant shallower")
        log(f"  mut_depth={m_m:.4f} "
            f"wt_depth={m_w:.4f}")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")

# ============================================================
# S4-5: SMARCA4 + TWIST1 SURVIVAL
# ============================================================

def new_fa_gene_survival(
    df_hcc, os_time, os_event,
    hcc_idx, depth_metab
):
    log("")
    log("=" * 65)
    log("S4-5/6: SMARCA4 + TWIST1 SURVIVAL")
    log("S4-P4: SMARCA4-hi worse OS")
    log("S4-P5: TWIST1-hi worse OS")
    log("=" * 65)

    t  = os_time[hcc_idx]
    e  = os_event[hcc_idx]
    gc = list(df_hcc.columns)

    results = {}

    new_genes = [
        "SMARCA4","TWIST1","CDK4",
        "TGFB1","FGFR1","DNMT3A",
        "SMAD3","VIM","ZEB1","ZEB2",
        "SNAI1","SNAI2",
    ]

    log(f"\n  {'Gene':<12} {'r_depth':>10}  "
        f"{'OS_p':>14}  "
        f"{'hi_OS':>8}  {'lo_OS':>8}  dir")
    log(f"  {'-'*70}")

    for gene in new_genes:
        if gene not in gc:
            continue
        gv = df_hcc[gene].values

        rv, pv = safe_pearsonr(
            depth_metab, gv
        )

        valid = (
            np.isfinite(gv)
            & np.isfinite(t)
            & np.isfinite(e)
            & (t > 0)
        )
        if valid.sum() < 10:
            continue

        med   = np.nanmedian(gv[valid])
        hi    = valid & (gv >= med)
        lo    = valid & (gv <  med)
        p_os  = logrank_p(
            t[hi], e[hi], t[lo], e[lo]
        )
        m_h   = t[hi].mean() if hi.sum()>0 else np.nan
        m_l   = t[lo].mean() if lo.sum()>0 else np.nan
        direction = (
            "↑=worse" if m_h < m_l
            else "↑=better"
        )
        log(f"  {gene:<12} {rv:>+10.4f}  "
            f"{fmt_p(p_os)}  "
            f"{m_h:>8.1f}  {m_l:>8.1f}  "
            f"{direction}")
        results[gene] = {
            "r_depth": rv,
            "p_os":    p_os,
            "m_hi":    m_h,
            "m_lo":    m_l,
            "hi":      hi,
            "lo":      lo,
            "t":       t,
            "e":       e,
        }

    for gene, pred_label, p_id in [
        ("SMARCA4", "S4-P4: SMARCA4-hi worse OS",
         "P4"),
        ("TWIST1",  "S4-P5: TWIST1-hi worse OS",
         "P5"),
    ]:
        if gene not in results:
            log(f"\n  {pred_label}")
            log(f"  STATUS: NOT TESTABLE "
                f"(gene not in matrix)")
            continue
        res  = results[gene]
        conf = (
            not np.isnan(res["m_hi"])
            and not np.isnan(res["m_lo"])
            and res["m_hi"] < res["m_lo"]
        )
        sig  = (
            not np.isnan(res["p_os"])
            and res["p_os"] < 0.05
        )
        log(f"\n  {pred_label}")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf and sig else 'DIRECTIONALLY ✓' if conf else 'NOT CONFIRMED ✗'} "
            f"(dir={'✓' if conf else '✗'} "
            f"sig={'✓' if sig else '✗'} "
            f"{fmt_p(res['p_os'])})")

    return results

# ============================================================
# S4-7: CHECKPOINT INHIBITOR HYPOTHESIS
# ============================================================

def checkpoint_inhibitor_analysis(
    df_hcc, depth_metab, os_time, os_event,
    hcc_idx
):
    log("")
    log("=" * 65)
    log("S4-7: CHECKPOINT INHIBITOR HYPOTHESIS")
    log("S4-P6: CD274 rises with depth")
    log("Immune exhaustion in deep HCC")
    log("=" * 65)

    t  = os_time[hcc_idx]
    e  = os_event[hcc_idx]
    gc = list(df_hcc.columns)

    # Correlations with depth
    log(f"\n  Immune checkpoint genes vs depth:")
    log(f"  {'Gene':<12} {'r_depth':>10}  "
        f"{'p_corr':>14}  interpretation")
    log(f"  {'-'*62}")

    checkpoint_genes = [
        "CD274","PDCD1","CTLA4","LAG3",
        "TIGIT","HAVCR2","CD8A","CD4",
        "FOXP3","GZMB","PRF1","IFNG",
        "CD68","CD247",
    ]

    corr_results = {}
    for gene in checkpoint_genes:
        if gene not in gc:
            continue
        rv, pv = safe_pearsonr(
            depth_metab, df_hcc[gene].values
        )
        if np.isnan(rv):
            continue
        interp = {
            "CD274":  "PD-L1 on tumour",
            "PDCD1":  "PD-1 on T cells",
            "CTLA4":  "CTLA-4 checkpoint",
            "LAG3":   "LAG-3 checkpoint",
            "TIGIT":  "TIGIT checkpoint",
            "HAVCR2": "TIM-3 checkpoint",
            "CD8A":   "cytotoxic T cells",
            "FOXP3":  "regulatory T cells",
            "GZMB":   "CTL effector",
            "PRF1":   "CTL effector",
            "IFNG":   "Th1/CTL cytokine",
            "CD68":   "macrophage",
        }.get(gene, "")
        log(f"  {gene:<12} {rv:>+10.4f}  "
            f"{fmt_p(pv)}  {interp}")
        corr_results[gene] = {
            "r": rv, "p": pv
        }

    # S4-P6 check
    if "CD274" in corr_results:
        rv_cd274 = corr_results["CD274"]["r"]
        conf = rv_cd274 > 0.10
        log(f"\n  S4-P6: CD274 rises with depth")
        log(f"  r(depth, CD274) = "
            f"{rv_cd274:+.4f}")
        log(f"  STATUS: "
            f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")

    # Deep + CD274-hi vs shallow + CD274-lo OS
    log(f"\n  Deep+CD274-hi vs Shallow+CD274-lo OS:")
    if "CD274" in gc:
        cd274 = df_hcc["CD274"].values
        med_d = np.median(depth_metab)
        med_c = np.nanmedian(cd274)
        valid = (
            np.isfinite(t) & np.isfinite(e)
            & (t > 0) & np.isfinite(cd274)
        )
        deep_hi = (
            valid
            & (depth_metab >= med_d)
            & (cd274 >= med_c)
        )
        shall_lo = (
            valid
            & (depth_metab < med_d)
            & (cd274 < med_c)
        )
        deep_lo = (
            valid
            & (depth_metab >= med_d)
            & (cd274 < med_c)
        )
        shall_hi = (
            valid
            & (depth_metab < med_d)
            & (cd274 >= med_c)
        )
        log(f"  Groups:")
        for label, mask in [
            ("Deep+CD274-hi",   deep_hi),
            ("Deep+CD274-lo",   deep_lo),
            ("Shallow+CD274-hi",shall_hi),
            ("Shallow+CD274-lo",shall_lo),
        ]:
            vm  = mask & valid
            m_t = (
                t[vm].mean()
                if vm.sum() > 0 else np.nan
            )
            n_e = (
                int(e[vm].sum())
                if vm.sum() > 0 else 0
            )
            log(f"    {label:<20} "
                f"n={vm.sum():>4} "
                f"OS={m_t:>6.1f}mo "
                f"ev={n_e}")

        p_deep_shall = logrank_p(
            t[deep_hi], e[deep_hi],
            t[shall_lo], e[shall_lo],
        )
        log(f"\n  Deep+CD274-hi vs "
            f"Shallow+CD274-lo:")
        log(f"  Logrank: {fmt_p(p_deep_shall)}")
        log(f"  Prediction: Deep+CD274-hi = "
            f"worst OS AND best checkpoint "
            f"responders")

    # Immune score = mean checkpoint gene expr
    immune_genes_avail = [
        g for g in [
            "CD8A","CD274","PDCD1",
            "LAG3","TIGIT","HAVCR2",
        ]
        if g in gc
    ]
    if len(immune_genes_avail) >= 3:
        immune_arr  = df_hcc[
            immune_genes_avail
        ].values
        immune_mean = np.nanmean(
            immune_arr, axis=1
        )
        rv_im, pv_im = safe_pearsonr(
            depth_metab, immune_mean
        )
        log(f"\n  Composite immune exhaustion score "
            f"vs depth:")
        log(f"  Genes: {immune_genes_avail}")
        log(f"  r(depth, immune_score) = "
            f"{rv_im:+.4f}  {fmt_p(pv_im)}")

    return corr_results

# ============================================================
# S4-6/8: FULL COX MULTIVARIATE
# ============================================================

def cox_multivariate_full(
    df_hcc, depth_metab, os_time, os_event,
    hcc_idx, stage_num, grade_num, age,
    mut_matrix
):
    log("")
    log("=" * 65)
    log("S4-6/8: FULL COX MULTIVARIATE")
    log("S4-P7: Depth independent of "
        "stage/grade/mutation")
    log("=" * 65)

    t     = os_time[hcc_idx]
    e     = os_event[hcc_idx]
    s_num = stage_num[hcc_idx]
    g_num = grade_num[hcc_idx]
    a_hcc = age[hcc_idx]

    ctnnb1_mut = mut_matrix["CTNNB1"][hcc_idx]
    tp53_mut   = mut_matrix["TP53"][hcc_idx]

    log(f"  Stage valid: "
        f"{(~np.isnan(s_num)).sum()}")
    log(f"  Grade valid: "
        f"{(~np.isnan(g_num)).sum()}")
    log(f"  Age valid:   "
        f"{(~np.isnan(a_hcc)).sum()}")
    log(f"  CTNNB1 mut:  "
        f"{ctnnb1_mut.sum()}")
    log(f"  TP53 mut:    "
        f"{tp53_mut.sum()}")

    def run_cox(df_model, label):
        log(f"\n  {label}:")
        try:
            df_c = df_model.copy().dropna()
            df_c = df_c[df_c["T"] > 0]
            if len(df_c) < 20:
                log(f"  Too few rows: {len(df_c)}")
                return None
            log(f"  n={len(df_c)}")
            # Standardise continuous vars
            for col in df_c.columns:
                if col in ["T","E"]:
                    continue
                sd = df_c[col].std()
                if sd > 0:
                    df_c[col] = (
                        (df_c[col]
                         - df_c[col].mean())
                        / sd
                    )
            cph = CoxPHFitter()
            cph.fit(df_c, "T", "E")
            smry = cph.summary[
                ["coef","exp(coef)","p"]
            ]
            log(smry.to_string())
            return cph
        except Exception as ex:
            log(f"  Error: {ex}")
            return None

    # Model 1: depth alone
    d1 = pd.DataFrame({
        "T": t, "E": e,
        "depth": depth_metab,
    })
    cph1 = run_cox(d1, "Model 1: depth alone")

    # Model 2: depth + age
    d2 = pd.DataFrame({
        "T": t, "E": e,
        "depth": depth_metab,
        "age":   a_hcc,
    })
    cph2 = run_cox(d2, "Model 2: depth + age")

    # Model 3: depth + stage (if available)
    s_valid = ~np.isnan(s_num)
    if s_valid.sum() >= 30:
        d3 = pd.DataFrame({
            "T":     t,
            "E":     e,
            "depth": depth_metab,
            "stage": s_num,
        })
        cph3 = run_cox(
            d3, "Model 3: depth + stage"
        )
    else:
        log(f"\n  Model 3 skipped: "
            f"only {s_valid.sum()} "
            f"samples with stage")

    # Model 4: depth + grade (if available)
    g_valid = ~np.isnan(g_num)
    if g_valid.sum() >= 30:
        d4 = pd.DataFrame({
            "T":     t,
            "E":     e,
            "depth": depth_metab,
            "grade": g_num,
        })
        cph4 = run_cox(
            d4, "Model 4: depth + grade"
        )
    else:
        log(f"\n  Model 4 skipped: "
            f"only {g_valid.sum()} "
            f"samples with grade")

    # Model 5: depth + mutations
    if ctnnb1_mut.sum() >= 5 \
            and tp53_mut.sum() >= 5:
        d5 = pd.DataFrame({
            "T":           t,
            "E":           e,
            "depth":       depth_metab,
            "CTNNB1_mut":  ctnnb1_mut.astype(float),
            "TP53_mut":    tp53_mut.astype(float),
        })
        cph5 = run_cox(
            d5,
            "Model 5: depth + CTNNB1 + TP53 mut",
        )
    else:
        log(f"\n  Model 5 skipped: "
            f"insufficient mutation data")

    # Model 6: full model
    if (s_valid.sum() >= 30
            and g_valid.sum() >= 30):
        d6 = pd.DataFrame({
            "T":     t,
            "E":     e,
            "depth": depth_metab,
            "stage": s_num,
            "grade": g_num,
            "age":   a_hcc,
        })
        cph6 = run_cox(
            d6,
            "Model 6: depth + stage + grade + age",
        )
        if cph6 is not None:
            p_depth = cph6.summary.loc[
                "depth", "p"
            ] if "depth" in cph6.summary.index \
               else np.nan
            conf = (
                not np.isnan(p_depth)
                and p_depth < 0.05
            )
            log(f"\n  S4-P7: depth independent "
                f"of stage/grade/age")
            log(f"  depth p={p_depth:.4f} "
                f"in full model")
            log(f"  STATUS: "
                f"{'CONFIRMED ✓' if conf else 'NOT CONFIRMED ✗'}")
    else:
        log(f"\n  Full model skipped: "
            f"insufficient stage/grade data")
        log(f"  Model 1 result:")
        if cph1 is not None:
            p_d = cph1.summary.loc[
                "depth", "p"
            ] if "depth" in \
                cph1.summary.index else np.nan
            log(f"  depth HR="
                f"{cph1.summary.loc['depth','exp(coef)']:.3f} "
                f"p={p_d:.6f}")

# ============================================================
# S4-9: MUTATION × DEPTH INTERACTION
# ============================================================

def mutation_depth_interaction(
    mut_matrix, depth_metab, os_time,
    os_event, hcc_idx
):
    log("")
    log("=" * 65)
    log("S4-9: MUTATION × DEPTH INTERACTION")
    log("Does depth stratify within mut groups?")
    log("=" * 65)

    t   = os_time[hcc_idx]
    e   = os_event[hcc_idx]
    med = np.median(depth_metab)

    for gene in ["CTNNB1","TP53","ARID1A",
                 "NFE2L2","RB1"]:
        gm = mut_matrix[gene][hcc_idx]
        if gm.sum() < 10:
            continue

        mmask = gm == 1
        wmask = gm == 0

        log(f"\n  {gene} (n_mut={mmask.sum()}):")

        for label, base_mask in [
            (f"{gene}-mutant",     mmask),
            (f"{gene}-wildtype",   wmask),
        ]:
            deep   = base_mask & (
                depth_metab >= med
            )
            shall  = base_mask & (
                depth_metab < med
            )
            valid_d = (
                deep & np.isfinite(t)
                & np.isfinite(e) & (t > 0)
            )
            valid_s = (
                shall & np.isfinite(t)
                & np.isfinite(e) & (t > 0)
            )
            m_d = (
                t[valid_d].mean()
                if valid_d.sum() > 0 else np.nan
            )
            m_s = (
                t[valid_s].mean()
                if valid_s.sum() > 0 else np.nan
            )
            p_int = logrank_p(
                t[shall], e[shall],
                t[deep],  e[deep],
            )
            log(f"    {label}:")
            log(f"      deep   n={deep.sum()} "
                f"OS={m_d:.1f}mo")
            log(f"      shallow n={shall.sum()} "
                f"OS={m_s:.1f}mo")
            log(f"      depth logrank: "
                f"{fmt_p(p_int)}")

# ============================================================
# GENERATE FIGURE
# ============================================================

def generate_figure(
    df_hcc, depth_metab,
    os_time, os_event, hcc_idx,
    mut_results, new_fa_results,
    checkpoint_results, mut_matrix,
):
    log("")
    log("--- Generating Script 4 figure ---")

    fig = plt.figure(figsize=(30, 26))
    fig.suptitle(
        "HCC — False Attractor Analysis Script 4\n"
        "TCGA-LIHC | Mutation Survival | "
        "SMARCA4/TWIST1 | Checkpoint | "
        "OrganismCore | Doc 92d | 2026-03-02",
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

    COLORS = [
        "#27ae60","#e74c3c",
        "#2980b9","#8e44ad","#e67e22",
    ]

    def km_panel(ax, groups, title):
        """groups = [(label, t, e, color)]"""
        for label, ti, ei, col in groups:
            ok = safe_km(kmf, ti, ei, label)
            if ok:
                kmf.plot_survival_function(
                    ax=ax, color=col,
                    ci_show=True, ci_alpha=0.10,
                )
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("Months", fontsize=8)
        ax.set_ylabel("Survival prob.",
                      fontsize=8)
        ax.legend(fontsize=6.5)
        ax.set_ylim(-0.05, 1.05)

    # ── A: CTNNB1 mutation KM ────��─────────────────────────
    ax_a = fig.add_subplot(gs_f[0, 0])
    if "CTNNB1" in mut_results:
        res = mut_results["CTNNB1"]
        p   = res["p"]
        km_panel(
            ax_a,
            [
                (f"CTNNB1-mut n={res['mmask'].sum()}",
                 t[res["mmask"]], e[res["mmask"]],
                 COLORS[0]),
                (f"CTNNB1-WT n={res['wmask'].sum()}",
                 t[res["wmask"]], e[res["wmask"]],
                 COLORS[1]),
            ],
            f"A — CTNNB1 mut OS (HCC-P5)\n"
            f"{fmt_p(p)}",
        )
    else:
        ax_a.set_title(
            "A — CTNNB1 mut OS\n"
            "(no mutation data)",
            fontsize=9,
        )

    # ── B: TP53 mutation KM ────────────────────────────────
    ax_b = fig.add_subplot(gs_f[0, 1])
    if "TP53" in mut_results:
        res = mut_results["TP53"]
        p   = res["p"]
        km_panel(
            ax_b,
            [
                (f"TP53-mut n={res['mmask'].sum()}",
                 t[res["mmask"]], e[res["mmask"]],
                 COLORS[1]),
                (f"TP53-WT n={res['wmask'].sum()}",
                 t[res["wmask"]], e[res["wmask"]],
                 COLORS[0]),
            ],
            f"B — TP53 mut OS\n{fmt_p(p)}",
        )
    else:
        ax_b.set_title(
            "B — TP53 mut OS\n"
            "(no mutation data)",
            fontsize=9,
        )

    # ── C: Depth KM (replication check) ───────────────────
    ax_c = fig.add_subplot(gs_f[0, 2])
    valid = (
        np.isfinite(t) & np.isfinite(e)
        & np.isfinite(depth_metab) & (t > 0)
    )
    if valid.sum() >= 10:
        med = np.median(depth_metab[valid])
        hi  = valid & (depth_metab >= med)
        lo  = valid & (depth_metab <  med)
        p   = logrank_p(
            t[hi], e[hi], t[lo], e[lo]
        )
        km_panel(
            ax_c,
            [
                (f"Deep n={hi.sum()}",
                 t[hi], e[hi], COLORS[1]),
                (f"Shallow n={lo.sum()}",
                 t[lo], e[lo], COLORS[0]),
            ],
            f"C — Metabolic depth OS\n{fmt_p(p)}",
        )

    # ── D: SMARCA4 KM ──────────────────────────────────────
    ax_d = fig.add_subplot(gs_f[1, 0])
    if "SMARCA4" in new_fa_results:
        res = new_fa_results["SMARCA4"]
        km_panel(
            ax_d,
            [
                (f"SMARCA4-hi "
                 f"n={res['hi'].sum()}",
                 t[res["hi"]], e[res["hi"]],
                 COLORS[1]),
                (f"SMARCA4-lo "
                 f"n={res['lo'].sum()}",
                 t[res["lo"]], e[res["lo"]],
                 COLORS[0]),
            ],
            f"D — SMARCA4 OS (new FA)\n"
            f"{fmt_p(res['p_os'])}",
        )
    else:
        ax_d.set_title(
            "D — SMARCA4 OS", fontsize=9
        )

    # ── E: TWIST1 KM ───────────────────────────────────────
    ax_e = fig.add_subplot(gs_f[1, 1])
    if "TWIST1" in new_fa_results:
        res = new_fa_results["TWIST1"]
        km_panel(
            ax_e,
            [
                (f"TWIST1-hi "
                 f"n={res['hi'].sum()}",
                 t[res["hi"]], e[res["hi"]],
                 COLORS[1]),
                (f"TWIST1-lo "
                 f"n={res['lo'].sum()}",
                 t[res["lo"]], e[res["lo"]],
                 COLORS[0]),
            ],
            f"E — TWIST1 OS (EMT FA)\n"
            f"{fmt_p(res['p_os'])}",
        )
    else:
        ax_e.set_title(
            "E — TWIST1 OS", fontsize=9
        )

    # ── F: Mutation frequency bar ──────────────────────────
    ax_f = fig.add_subplot(gs_f[1, 2])
    genes_bar = [
        g for g in MUT_GENES_TRACK
        if g in mut_results
    ]
    if genes_bar:
        freqs = [
            100 * mut_results[g]["mmask"].sum()
            / max(len(hcc_idx), 1)
            for g in genes_bar
        ]
        colors_bar = [
            COLORS[0] if g == "CTNNB1"
            else COLORS[1] if g == "TP53"
            else COLORS[2]
            for g in genes_bar
        ]
        y_pos = range(len(genes_bar))
        ax_f.barh(
            y_pos, freqs,
            color=colors_bar, alpha=0.8,
        )
        ax_f.set_yticks(y_pos)
        ax_f.set_yticklabels(
            genes_bar, fontsize=8
        )
        ax_f.set_xlabel(
            "Mutation frequency (%)", fontsize=8
        )
    ax_f.set_title(
        "F — Mutation frequencies",
        fontsize=9,
    )

    # ── G: Checkpoint genes vs depth scatter ───────────────
    ax_g = fig.add_subplot(gs_f[2, 0])
    plotted_g = False
    for gene, color in [
        ("CD274", COLORS[1]),
        ("PDCD1", COLORS[2]),
        ("CD8A",  COLORS[0]),
    ]:
        if gene not in gc:
            continue
        rv, _ = safe_pearsonr(
            depth_metab, df_hcc[gene].values
        )
        ax_g.scatter(
            depth_metab, df_hcc[gene].values,
            alpha=0.25, s=8, color=color,
            label=f"{gene} r={rv:+.2f}",
        )
        plotted_g = True
    if plotted_g:
        ax_g.set_xlabel(
            "Metabolic depth", fontsize=8
        )
        ax_g.legend(fontsize=7)
    ax_g.set_title(
        "G — Checkpoint genes vs depth\n"
        "(immune exhaustion pattern)",
        fontsize=9,
    )

    # ── H: CD274 KM (depth × CD274) ───────────────────────
    ax_h = fig.add_subplot(gs_f[2, 1])
    if "CD274" in gc:
        cd274   = df_hcc["CD274"].values
        med_d   = np.median(depth_metab)
        med_c   = np.nanmedian(cd274)
        valid_h = (
            np.isfinite(t) & np.isfinite(e)
            & (t > 0) & np.isfinite(cd274)
        )
        deep_hi  = valid_h & (
            depth_metab >= med_d
        ) & (cd274 >= med_c)
        shall_lo = valid_h & (
            depth_metab < med_d
        ) & (cd274 < med_c)
        km_panel(
            ax_h,
            [
                (f"Deep+CD274-hi n={deep_hi.sum()}",
                 t[deep_hi], e[deep_hi],
                 COLORS[1]),
                (f"Shall+CD274-lo n={shall_lo.sum()}",
                 t[shall_lo], e[shall_lo],
                 COLORS[0]),
            ],
            "H — Deep+CD274-hi vs Shall+CD274-lo\n"
            "(checkpoint inhibitor candidate)",
        )
    else:
        ax_h.set_title(
            "H — CD274 × depth", fontsize=9
        )

    # ── I: CTNNB1 mutation vs depth ───────────────────────
    ax_i = fig.add_subplot(gs_f[2, 2])
    ctnnb1_mut = mut_matrix["CTNNB1"][hcc_idx]
    if ctnnb1_mut.sum() >= 5:
        mmask = ctnnb1_mut == 1
        wmask = ctnnb1_mut == 0
        colors_i = np.where(
            mmask, COLORS[0], COLORS[1]
        )
        ax_i.scatter(
            np.arange(len(depth_metab)),
            depth_metab,
            c=colors_i, alpha=0.4, s=10,
        )
        for msk, lbl, col in [
            (mmask, "CTNNB1-mut", COLORS[0]),
            (wmask, "CTNNB1-WT",  COLORS[1]),
        ]:
            if msk.sum() > 0:
                m = depth_metab[msk].mean()
                ax_i.axhline(
                    m, color=col,
                    linestyle="--",
                    linewidth=1.5,
                    label=f"{lbl} mean={m:.3f}",
                )
        ax_i.set_title(
            "I — CTNNB1 mut vs depth\n"
            "(S4-P3: mut=shallower?)",
            fontsize=9,
        )
        ax_i.set_xlabel(
            "Sample index", fontsize=8
        )
        ax_i.set_ylabel(
            "Metabolic depth", fontsize=8
        )
        ax_i.legend(fontsize=7)
    else:
        ax_i.set_title(
            "I — CTNNB1 mut vs depth\n"
            "(no mutation data)",
            fontsize=9,
        )

    # ── J: All mutation OS summary bar ────────────────────
    ax_j = fig.add_subplot(gs_f[3, 0])
    if mut_results:
        genes_j = list(mut_results.keys())
        pvals_j = [
            -np.log10(
                mut_results[g]["p"]
            ) if not np.isnan(
                mut_results[g]["p"]
            ) else 0
            for g in genes_j
        ]
        colors_j = []
        for g in genes_j:
            res = mut_results[g]
            if (not np.isnan(res["m_mut"])
                    and not np.isnan(res["m_wt"])
                    and res["m_mut"] > res["m_wt"]):
                colors_j.append(COLORS[0])
            else:
                colors_j.append(COLORS[1])
        y_j = range(len(genes_j))
        ax_j.barh(
            y_j, pvals_j,
            color=colors_j, alpha=0.8,
        )
        ax_j.axvline(
            -np.log10(0.05),
            color="black",
            linestyle="--",
            linewidth=1,
            label="p=0.05",
        )
        ax_j.set_yticks(y_j)
        ax_j.set_yticklabels(
            genes_j, fontsize=7
        )
        ax_j.set_xlabel(
            "-log10(p) OS logrank", fontsize=8
        )
        ax_j.legend(fontsize=7)
    ax_j.set_title(
        "J — Mutation OS summary\n"
        "(green=better, red=worse)",
        fontsize=9,
    )

    # ── K: Depth histogram coloured by mutation ────────────
    ax_k = fig.add_subplot(gs_f[3, 1])
    ctnnb1_mut = mut_matrix["CTNNB1"][hcc_idx]
    tp53_mut   = mut_matrix["TP53"][hcc_idx]
    if ctnnb1_mut.sum() >= 5:
        ax_k.hist(
            depth_metab[ctnnb1_mut == 1],
            bins=20, alpha=0.6,
            color=COLORS[0],
            label=f"CTNNB1-mut "
                  f"n={int((ctnnb1_mut==1).sum())}",
        )
    if tp53_mut.sum() >= 5:
        ax_k.hist(
            depth_metab[tp53_mut == 1],
            bins=20, alpha=0.6,
            color=COLORS[1],
            label=f"TP53-mut "
                  f"n={int((tp53_mut==1).sum())}",
        )
    ax_k.hist(
        depth_metab[
            (ctnnb1_mut == 0) & (tp53_mut == 0)
        ],
        bins=20, alpha=0.4,
        color=COLORS[2],
        label=f"Neither "
              f"n={int(((ctnnb1_mut==0)&(tp53_mut==0)).sum())}",
    )
    ax_k.set_title(
        "K — Depth by mutation group\n"
        "(S4-P3: CTNNB1-mut shallower?)",
        fontsize=9,
    )
    ax_k.set_xlabel(
        "Metabolic depth", fontsize=8
    )
    ax_k.legend(fontsize=7)

    # ── L: Summary ─────────────────────────────────────────
    ax_l = fig.add_subplot(gs_f[3, 2])
    ax_l.axis("off")

    def pf(g, d):
        v = d.get(g, {}).get("p", np.nan)
        if isinstance(v, float) \
                and not np.isnan(v):
            return f"{v:.4f}"
        return "N/A"

    summary = (
        "L — SCRIPT 4 SUMMARY\n"
        "─────────────────────────────\n"
        "Dataset: TCGA-LIHC n=371\n\n"
        "PREDICTIONS:\n"
        f"  S4-P1: CTNNB1-mut better OS\n"
        f"         p={pf('CTNNB1',mut_results)}\n"
        f"  S4-P2: TP53-mut worse OS\n"
        f"         p={pf('TP53',mut_results)}\n"
        "  S4-P3: CTNNB1-mut shallower\n"
        f"  S4-P4: SMARCA4-hi worse OS\n"
        f"         p={pf('SMARCA4',new_fa_results)}\n"
        f"  S4-P5: TWIST1-hi worse OS\n"
        f"         p={pf('TWIST1',new_fa_results)}\n"
        "  S4-P6: CD274 rises with depth\n"
        "  S4-P7: depth indep stage/mut\n\n"
        "KEY:\n"
        "  CTNNB1 mut = HCC-P5 final test\n"
        "  SMARCA4 = new chromatin FA\n"
        "  TWIST1 = new EMT FA\n"
        "  CD274 = checkpoint target\n\n"
        "OrganismCore | Doc 92d | 2026-03-02"
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
        RESULTS_DIR, "hcc_tcga_s4.png"
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
    log("HEPATOCELLULAR CARCINOMA — SCRIPT 4")
    log("Dataset: TCGA-LIHC (continued)")
    log("Framework: OrganismCore")
    log("Doc: 92d | Date: 2026-03-02")
    log("=" * 65)
    log("")
    log("PREDICTIONS LOCKED 2026-03-02:")
    log("S4-P1: CTNNB1-mutant better OS (HCC-P5)")
    log("S4-P2: TP53-mutant worse OS")
    log("S4-P3: CTNNB1-mutant shallower depth")
    log("S4-P4: SMARCA4-hi worse OS")
    log("S4-P5: TWIST1-hi worse OS")
    log("S4-P6: CD274 rises with depth")
    log("S4-P7: Depth independent of "
        "stage/grade/mutation (Cox)")

    # ── Load expression + survival ────────────────────────
    (df_hcc, sample_ids, hcc_idx,
     os_time, os_event,
     stage_num, grade_num,
     age, gender) = load_expression_survival(
        EXPR_FILE, SURV_FILE, PHENO_FILE
    )

    # ── Download MAF ──────────────────────────────────────
    ok_maf = download_gdc_maf()
    if not ok_maf:
        log("")
        log("  MAF download failed.")
        log("  Mutation analyses will be skipped.")
        log("  Manual download:")
        log("  https://portal.gdc.cancer.gov/")
        log("  Project: TCGA-LIHC")
        log("  Data type: Masked Somatic Mutation")
        log(f"  Save to: {MAF_FILE}")

    # ── Parse MAF ─────────────────────────────────────────
    mut_matrix = parse_maf(MAF_FILE, sample_ids)

    # ── Build depth score ─────────────────────────────────
    log("")
    log("=" * 65)
    log("DEPTH SCORE — SCRIPT 4")
    log("=" * 65)

    gc = list(df_hcc.columns)
    metab_genes = [
        g for g in METAB_SWITCH if g in gc
    ]
    depth_metab = build_depth(
        df_hcc,
        METAB_SWITCH,
        PROG_FA,
        "Metabolic depth (V2)",
    )
    log(f"\n  Metabolic genes in matrix: "
        f"{metab_genes}")

    # ── S4-2/3: Mutation survival ─────────────────────────
    mut_results = mutation_survival_analysis(
        mut_matrix, os_time, os_event,
        hcc_idx, df_hcc, depth_metab,
    )

    # ── S4-4: CTNNB1 vs depth ────────────────────────────
    ctnnb1_depth_analysis(
        mut_matrix, depth_metab,
        hcc_idx, df_hcc,
    )

    # ── S4-5/6: SMARCA4, TWIST1 survival ─────────────────
    new_fa_results = new_fa_gene_survival(
        df_hcc, os_time, os_event,
        hcc_idx, depth_metab,
    )

    # ── S4-7: Checkpoint hypothesis ───────────────────────
    checkpoint_results = (
        checkpoint_inhibitor_analysis(
            df_hcc, depth_metab,
            os_time, os_event, hcc_idx,
        )
    )

    # ── S4-6/8: Full Cox ─────────────────────────────────
    cox_multivariate_full(
        df_hcc, depth_metab,
        os_time, os_event, hcc_idx,
        stage_num, grade_num, age,
        mut_matrix,
    )

    # ── S4-9: Mutation × depth interaction ────────────────
    mutation_depth_interaction(
        mut_matrix, depth_metab,
        os_time, os_event, hcc_idx,
    )

    # ── Generate figure ───────────────────────────────────
    generate_figure(
        df_hcc, depth_metab,
        os_time, os_event, hcc_idx,
        mut_results, new_fa_results,
        checkpoint_results, mut_matrix,
    )

    # ── Save scores ───────────────────────────────────────
    scores_df = pd.DataFrame({
        "sample_id": [
            sample_ids[i] for i in hcc_idx
        ],
        "depth_metabolic": depth_metab,
        "CTNNB1_mut": (
            mut_matrix["CTNNB1"][hcc_idx]
        ),
        "TP53_mut": (
            mut_matrix["TP53"][hcc_idx]
        ),
    })
    scores_df.to_csv(
        os.path.join(
            RESULTS_DIR, "depth_scores_s4.csv"
        ),
        index=False,
    )
    log(f"\n  Scores: "
        f"{RESULTS_DIR}/depth_scores_s4.csv")

    write_log()
    log(f"\n  Log:    {LOG_FILE}")
    log(f"  Output: {RESULTS_DIR}")
    log("\n=== SCRIPT 4 COMPLETE ===")
    log("\nPaste full output for Document 92d.")


if __name__ == "__main__":
    main()
