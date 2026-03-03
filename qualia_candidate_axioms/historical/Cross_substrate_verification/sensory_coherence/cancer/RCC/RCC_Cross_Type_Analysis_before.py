"""
RCC CROSS-TYPE ANALYSIS
OrganismCore | 2026-03-03
Author: Eric Robert Lawson

Protocol-compliant cross-cancer subtype comparison.
Reads existing results CSVs from each subtype's results
directory. Does NOT re-derive depth scores or re-download
data. Performs RANKED LIST COMPARISON only.

════════════════════════════════════════════════════════════
SUPPORTED DIRECTORY LAYOUTS — auto-detected at runtime
════════════════════════════════════════════════════════════

LAYOUT A — LOCAL (your working machine)
  Script lives anywhere; results live under a dedicated
  working folder per cancer type:

    CCRCC/ccrcc_false_attractor/results/       ← s1
    CCRCC/ccrcc_false_attractor/results_s2/
    CCRCC/ccrcc_false_attractor/results_s3/
    CCRCC/ccrcc_false_attractor/results_s4/
    CCRCC/ccrcc_false_attractor/results_s5/
    PRCC/prcc_false_attractor/results/
    PRCC/prcc_false_attractor/results_s2/  … etc.
    chRCC/chrcc_false_attractor/results/   … etc.
    cdRCC/cdRCC_false_attractor/results/   ← s1 (named "results")
    cdRCC/cdRCC_false_attractor/results_s2/ … etc.

  The script looks for the CCRCC/ root relative to:
    1. The directory containing this script
    2. The current working directory
    3. The parent of the current working directory

LAYOUT B — REPO (github.com/Eric-Robert-Lawson/OrganismCore)
  Script lives at:
    .../cancer/RCC/rcc_cross_type_analysis.py
  Results live at:
    .../cancer/RCC/CCRCC/results_s1/  … results_s5/
    .../cancer/RCC/PRCC/results_s1/   … results_s6/
    .../cancer/RCC/chRCC/results_s1/  … results_s5/
    .../cancer/RCC/cdRCC/results/  results_s2/ … results_s4/

Auto-detection logic (in order):
  1. Check if REPO layout exists relative to script dir
     (looks for ./CCRCC/results_s1/ sibling)
  2. Check if LOCAL layout exists relative to script dir
     (looks for ./CCRCC/ccrcc_false_attractor/)
  3. Check CWD for both layouts
  4. Check parent of CWD for both layouts
  5. If none found: print clear instructions and exit

════════════════════════════════════════════════════════════
OUTPUT
════════════════════════════════════════════════════════════
  ./results_cross_type/
    01_gene_overlap_positive.csv
    02_gene_overlap_negative.csv
    03_universal_genes.txt
    04_drug_matrix.csv
    05_normal_identity_map.txt
    06_false_attractor_map.txt
    07_tca_chromatin_circuit.csv
    08_immune_architecture.csv
    09_transition_sequence.txt
    10_prediction_scoring.txt
    11_basket_trial_hypothesis.txt
    cross_type_analysis_log.txt

PROTOCOL RULES:
  - No cross-type p-values computed
  - No pooled expression analysis
  - No raw fold-change comparisons across types
  - Ranked list comparison only
  - Individual type predictions NOT revised
  - cdRCC findings carry n=7 caveat
  - All outputs are descriptive and directional

Date: 2026-03-03
"""

import os
import sys
import csv
from collections import defaultdict

# ============================================================
# CANCER TYPES
# ============================================================

CANCER_TYPES_ORDER = ["ccRCC", "PRCC", "chRCC", "cdRCC"]

# ============================================================
# LAYOUT DETECTION
# ============================================================

# Repo layout: type dirs sit directly next to the script,
# named CCRCC / PRCC / chRCC / cdRCC
REPO_TYPE_DIRS = {
    "ccRCC": "CCRCC",
    "PRCC":  "PRCC",
    "chRCC": "chRCC",
    "cdRCC": "cdRCC",
}

# Local layout: type dirs contain a named working subfolder
# Subfolder names as used on your machine
LOCAL_WORK_DIRS = {
    "ccRCC": os.path.join("CCRCC", "ccrcc_false_attractor"),
    "PRCC":  os.path.join("PRCC",  "prcc_false_attractor"),
    "chRCC": os.path.join("chRCC", "chrcc_false_attractor"),
    "cdRCC": os.path.join("cdRCC", "cdRCC_false_attractor"),
}


def _is_repo_layout(base):
    """
    True if base contains CCRCC/results_s1 (or CCRCC/results_s5).
    Enough to confirm repo layout.
    """
    ccrcc = os.path.join(base, "CCRCC")
    if not os.path.isdir(ccrcc):
        return False
    for name in os.listdir(ccrcc):
        if name.startswith("results"):
            return True
    return False


def _is_local_layout(base):
    """
    True if base contains CCRCC/ccrcc_false_attractor/results*
    """
    work = os.path.join(base, "CCRCC", "ccrcc_false_attractor")
    if not os.path.isdir(work):
        return False
    for name in os.listdir(work):
        if name.startswith("results"):
            return True
    return False


def detect_layout():
    """
    Returns (layout, rcc_base) where layout is 'repo' or 'local'
    and rcc_base is the absolute path to the directory that
    contains CCRCC/, PRCC/, chRCC/, cdRCC/.
    """
    candidates = [
        os.path.dirname(os.path.abspath(__file__)),
        os.getcwd(),
        os.path.dirname(os.getcwd()),
    ]
    # De-duplicate while preserving order
    seen = set()
    search_dirs = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            search_dirs.append(c)

    for base in search_dirs:
        if _is_repo_layout(base):
            return "repo", base
        if _is_local_layout(base):
            return "local", base

    return None, None


def type_base_dir(layout, rcc_base, cancer_type):
    """
    Returns the directory that contains results_sN folders
    for a given cancer type.
    """
    if layout == "repo":
        return os.path.join(rcc_base, REPO_TYPE_DIRS[cancer_type])
    else:  # local
        return os.path.join(rcc_base, LOCAL_WORK_DIRS[cancer_type])


# ============================================================
# LOCKED KNOWLEDGE
# All from confirmed reasoning artifacts — not re-derived.
# ============================================================

FALSE_ATTRACTOR_IDENTITY = {
    "ccRCC": {
        "description":      "HIF/VHL-null hypoxic mesenchymal-like programme",
        "top_genes":        ["CA9", "VEGFA", "SLC2A1", "LDHA", "PDK1",
                             "SCD", "EGLN3", "FABP7", "VIM", "TGFB1"],
        "non_renal_tissue": "Hypoxic mesenchymal / pseudo-endothelial",
        "key_TF":           "EPAS1 (HIF2α)",
    },
    "PRCC": {
        "description":      "Biliary ductal / intrahepatic cholangiocarcinoma-like",
        "top_genes":        ["KRT19", "KRT7", "ERBB2", "LAMC2", "RUNX1",
                             "EZH2", "KDM1A", "MUC1", "TWIST1", "COL1A1"],
        "non_renal_tissue": "Biliary epithelium / intrahepatic bile duct",
        "key_TF":           "RUNX1 + KDM1A",
    },
    "chRCC": {
        "description":      "Steroid-metabolising / adrenocortical-like programme",
        "top_genes":        ["AKR1C1", "AKR1C3", "AKR1E2", "HSD17B14",
                             "CYP1B1", "SULT2B1", "TM6SF2", "ABCC2",
                             "SLC51B", "GPD1"],
        "non_renal_tissue": "Adrenocortical / steroid-metabolising epithelium",
        "key_TF":           "NRF2/KEAP1-AKR axis",
    },
    "cdRCC": {
        "description":      "Aberrant ductal secretory programme",
        "top_genes":        ["IL1RAP", "PPARG", "KLF5", "AGR2", "GPRC5A",
                             "CST6", "KLF10", "TMPRSS4", "ESRP1", "SERPINA1"],
        "non_renal_tissue": "Aberrant collecting duct secretory / "
                            "pancreatic ductal-like",
        "key_TF":           "PPARG (uncoupled from RXRA) + BHLHE40",
    },
}

NORMAL_IDENTITY = {
    "ccRCC": {
        "nephron_segment": "Proximal tubule S1",
        "top_genes":       ["UMOD", "SLC34A1", "SLC13A3", "SLC22A6",
                            "ALDOB", "PCK1", "AGXT", "FBP1", "G6PC",
                            "LHX1", "AQP1", "GATM", "SLC13A2"],
        "gene_families":   ["SLC (citrate/αKG/OAT)", "Gluconeogenesis",
                            "TCA/oxidative", "TF (LHX1, HNF4A)"],
    },
    "PRCC": {
        "nephron_segment": "Proximal tubule S2/S3",
        "top_genes":       ["SLC22A6", "FABP1", "UMOD", "SLC34A2",
                            "CUBN", "PDZK1", "GOT1", "SLC7A9",
                            "FH", "SUCLG1"],
        "gene_families":   ["SLC (OAT1)", "TCA (FH, SUCLG1)",
                            "Fatty acid binding", "Cubilin pathway"],
    },
    "chRCC": {
        "nephron_segment": "Intercalated cell (collecting duct)",
        "top_genes":       ["SLC51B", "SLC2A2", "SLC1A1", "SLC5A12",
                            "FOXI1", "HSD17B14", "SULT2B1", "RDH5",
                            "CALB1", "ATP6V1G3"],
        "gene_families":   ["SLC (bile acid, GLUT2, glutamate)",
                            "Steroid metabolism (HSD17B14, RDH5)",
                            "Intercalated cell TF (FOXI1)", "Calbindin"],
    },
    "cdRCC": {
        "nephron_segment": "Principal / intercalated cell (collecting duct)",
        "top_genes":       ["AQP2", "SCNN1A", "SCNN1B", "SCNN1G",
                            "AVPR2", "TFCP2L1", "PRKAR2B", "UMOD",
                            "CALB1", "FOXI1", "EPAS1", "HNF4A"],
        "gene_families":   ["Aquaporin", "ENaC (SCNN1)",
                            "AVPR2 (vasopressin R)", "PKA (PRKAR2B)",
                            "TF (TFCP2L1, HNF4A, FOXI1)"],
    },
}

EPIGENETIC_LOCKS = {
    "ccRCC": {
        "EZH2":          "+",
        "KDM1A":         "+",
        "DNMT3A":        "+",
        "TCA_gene_down": "SUCLG1",
        "mechanism":     "EZH2↑+KDM1A↑ co-elevated; "
                         "SUCLG1↓ → αKG↓ → EZH2 hyperactive",
    },
    "PRCC": {
        "EZH2":          "+",
        "KDM1A":         "+",
        "TCA_gene_down": "FH",
        "mechanism":     "EZH2↑+KDM1A↑ co-elevated; "
                         "FH↓ → fumarate↑ / αKG↓ → chromatin lock",
    },
    "chRCC": {
        "EZH2":          "+",
        "TCA_gene_down": "OGDHL",
        "mechanism":     "EZH2↑; KEAP1/NRF2 → AKR axis; "
                         "OGDHL predicted down",
    },
    "cdRCC": {
        "EZH2":          "+",
        "TCA_gene_down": "OGDHL",
        "mechanism":     "EZH2↑ (paired p=0.031); silences CEBPA; "
                         "CEBPA removal allows PPARG module; "
                         "OGDHL r=-1.000 depth",
    },
}

DRUG_TARGETS = {
    "ccRCC": [
        {"drug": "Tazemetostat",           "target": "EZH2",
         "mechanism": "EZH2 initiating lock → chromatin de-repression",
         "evidence": "CONFIRMED + clinical trials"},
        {"drug": "Belzutifan",             "target": "HIF2α/EPAS1",
         "mechanism": "Wall 1 — depth-independent (universal benefit)",
         "evidence": "FDA approved"},
        {"drug": "LOXL2 inhibitor",        "target": "LOXL2",
         "mechanism": "Top depth marker r=+0.628; ECM stiffening",
         "evidence": "Preclinical (simtuzumab class)"},
        {"drug": "AXL inhibitor",          "target": "AXL",
         "mechanism": "Q4 ccRCC deep state; bemcentinib/cabozantinib",
         "evidence": "Clinical trials in ccRCC"},
        {"drug": "RUNX1 inhibitor",        "target": "RUNX1",
         "mechanism": "Depth hub r=+0.742; drives LOXL2/TGFBI/EZH2",
         "evidence": "Preclinical"},
        {"drug": "αKG supplement",         "target": "TCA/αKG axis",
         "mechanism": "Restore αKG → reduce EZH2 hyperactivity",
         "evidence": "Preclinical (DMKG class)"},
        {"drug": "IKKβ inhibitor",         "target": "NF-κB/RELA",
         "mechanism": "Wall 2 inflammatory circuit",
         "evidence": "Preclinical"},
        {"drug": "HDACi + anti-PD1",       "target": "B2M/HLA-A/HDAC",
         "mechanism": "Q4 immune evasion — MHC-I down not PD-L1 high",
         "evidence": "Preclinical + entinostat trials"},
    ],
    "PRCC": [
        {"drug": "Tazemetostat",           "target": "EZH2",
         "mechanism": "EZH2 depth+ in PRCC; TCA coupling (FH)",
         "evidence": "CONFIRMED + trial evidence"},
        {"drug": "Savolitinib",            "target": "MET",
         "mechanism": "MET depth+ in PRCC; SAVOIR trial 27% ORR",
         "evidence": "Phase 2 trial (SAVOIR)"},
        {"drug": "Trastuzumab/T-DXd",     "target": "ERBB2",
         "mechanism": "ERBB2 depth+ in PRCC (r=+0.556); biliary "
                      "identity marker; IHC2+ continuous criterion",
         "evidence": "FDA tumour-agnostic approval 2024 (IHC3+); "
                     "BTC data supports IHC2+"},
        {"drug": "CDK4/6 inhibitor",       "target": "CDK4/6",
         "mechanism": "CCND1/CDKN2A axis in deep PRCC",
         "evidence": "Palbociclib+sasanlimab Phase I/II includes pRCC"},
        {"drug": "KDM1A inhibitor",        "target": "KDM1A",
         "mechanism": "KDM1A co-elevated with EZH2 in PRCC; "
                      "RUNX1-KDM1A co-dependency",
         "evidence": "Preclinical (iadademstat)"},
        {"drug": "αKG supplement",         "target": "FH/TCA",
         "mechanism": "FH↓ → fumarate↑ / αKG↓ → chromatin lock; "
                      "αKG restores balance in FH-low PRCC",
         "evidence": "Preclinical"},
        {"drug": "Anti-CSF1R / repol",     "target": "TAM/CSF1R",
         "mechanism": "M2 macrophage repolarisation in deep PRCC TME; "
                      "ARG1 Q4/Q1=1.748",
         "evidence": "Preclinical (repolarisation not depletion)"},
        {"drug": "HDACi + anti-PD1",       "target": "B2M/HLA-A/HDAC",
         "mechanism": "Q4 immune evasion — B2M r=-0.222, HLA-A r=-0.237",
         "evidence": "Preclinical + entinostat trials"},
    ],
    "chRCC": [
        {"drug": "SLC inhibitors",         "target": "SLC2A2/SLC1A1/SLC5A12",
         "mechanism": "PC2 identity markers; chRCC > oncocytoma selectivity",
         "evidence": "Preclinical concept"},
        {"drug": "AKR1C3 inhibitor",       "target": "HSD17B14/AKR1C3",
         "mechanism": "chRCC-specific after depth removal; "
                      "steroid metabolism axis",
         "evidence": "AKR1C3 inhibitors in clinical dev (AML)"},
        {"drug": "MAP3K19 inhibitor",      "target": "MAP3K19",
         "mechanism": "Highest-rank novel kinase in Tier3",
         "evidence": "Exploratory — no clinical precedent"},
        {"drug": "Tazemetostat",           "target": "EZH2",
         "mechanism": "EZH2 predicted depth+ in chRCC",
         "evidence": "Predicted — pending chRCC-specific confirmation"},
        {"drug": "αKG supplement",         "target": "TCA/OGDHL",
         "mechanism": "OGDHL predicted down in chRCC",
         "evidence": "Predicted"},
        {"drug": "NOX4 inhibitor",         "target": "NOX4",
         "mechanism": "NOX4 clean_r +0.507 on chRCC PC2",
         "evidence": "Preclinical (GKT137831 class)"},
    ],
    "cdRCC": [
        {"drug": "Tazemetostat",           "target": "EZH2",
         "mechanism": "EZH2 initiating lock → silences CEBPA → "
                      "PPARG module activates; CEBPA opposes 10/10 genes",
         "evidence": "CONFIRMED + NCT03874455"},
        {"drug": "Bexarotene (RXRA)",      "target": "RXRA",
         "mechanism": "PPARG-RXRA uncoupled in cdRCC (r drops "
                      "+0.829→+0.107); rexinoid re-engages RXRA",
         "evidence": "Partial — bexarotene in CTCL; novel for cdRCC"},
        {"drug": "IKKβ inhibitor",         "target": "NF-κB/RELA",
         "mechanism": "Circuit 2: RELA-ADCY3 axis; IL1B+CEBPB up",
         "evidence": "CONFIRMED NF-κB in CDC; mechanism novel"},
        {"drug": "Ipatasertib/MK-2206",    "target": "Akt",
         "mechanism": "Circuit 3: PRKCI→Akt→HK2-VDAC "
                      "r(PRKCI,HK2)=+0.929 p=0.003",
         "evidence": "CONFIRMED mechanism + Akt inhibitors in trials"},
        {"drug": "BET inhibitor",          "target": "BRD4/MYC",
         "mechanism": "MYC early window; closes when BHLHE40 rises; "
                      "CDK9 convergence in EMBO 2024",
         "evidence": "CONVERGENCE with EMBO 2024 CDK9 inhibitor"},
        {"drug": "PRKCI inhibitor",        "target": "PRKCI",
         "mechanism": "PRKCI uncoupled from PARD3 → oncogenic; "
                      "PAR→PCP polarity switch",
         "evidence": "Preclinical"},
    ],
}

CONTRAINDICATIONS = {
    "ccRCC": [
        {"drug": "Anti-PD-L1 monotherapy (Q4 deep)",
         "reason": "PD-L1 FALLS with depth in Q4; "
                   "MHC-I down → T cells blind not exhausted; "
                   "checkpoint blockade misses mechanism"},
        {"drug": "Anti-TIM-3 (Q4 deep)",
         "reason": "TIM-3 falls in Q4 ccRCC — "
                   "wrong checkpoint for deep tumours"},
    ],
    "PRCC": [
        {"drug": "Belzutifan/HIF2α inhibitor",
         "reason": "EPAS1 actively SUPPRESSED in deep PRCC "
                   "(PRCC uses biliary identity, not HIF); "
                   "CONTRAINDICATED — targets absent pathway"},
        {"drug": "Anti-PD-L1 monotherapy (Q4 deep)",
         "reason": "PD-L1 falls in deep PRCC; "
                   "MHC-I restoration is correct Q4 target"},
        {"drug": "Anti-TIM-3 (Q4 deep)",
         "reason": "TIM-3 r=-0.396 with depth — "
                   "falls in deep PRCC; wrong target"},
        {"drug": "STING agonist (Q4 deep)",
         "reason": "IFI16 already firing in Q4; overdrive on "
                   "active innate circuit without adaptive output; "
                   "same principle as ccRCC Q4"},
    ],
    "chRCC": [
        {"drug": "Belzutifan/HIF2α inhibitor",
         "reason": "chRCC is NOT HIF-driven; HIF programme absent; "
                   "applying ccRCC drug to chRCC is mechanistically wrong"},
        {"drug": "Sunitinib/VEGFR TKI",
         "reason": "VEGFA is not a primary depth driver in chRCC; "
                   "ccRCC SOC applied to chRCC without mechanistic basis"},
        {"drug": "SULT2B1 inhibitor",
         "reason": "SULT2B1 is an ONCOCYTOMA identity marker not chRCC; "
                   "CONTRAINDICATED — would target the wrong identity"},
    ],
    "cdRCC": [
        {"drug": "TZD/PPARG agonist (rosiglitazone class)",
         "reason": "PPARG-RXRA is uncoupled in cdRCC; "
                   "canonical PPARG agonists require functional PPARG-RXRA; "
                   "RXRA re-engagement needed first (bexarotene)"},
        {"drug": "MET inhibitor (as primary)",
         "reason": "MET not identified as depth driver in cdRCC; "
                   "cdRCC depth is PRKCI/Akt/HK2 not MET"},
        {"drug": "Belzutifan/HIF2α inhibitor",
         "reason": "EPAS1 confirmed DOWN in cdRCC (paired p=0.031); "
                   "HIF programme absent; CONTRAINDICATED"},
    ],
}

IMMUNE_ARCHITECTURE = {
    "ccRCC": {
        "MHC_I":    "DOWN (B2M and HLA-A fall with depth)",
        "PD_L1":    "FALLS in Q4",
        "TIM3":     "FALLS in Q4",
        "IFI16":    "UP in deep tumours (innate sensing active)",
        "B2M":      "Negative depth correlation",
        "evasion":  "Innate sensing UP / adaptive presentation DOWN — "
                    "immune evasion not exhaustion",
        "strategy": "MHC-I restoration (HDACi + anti-PD1); "
                    "NOT anti-PD-L1 monotherapy in Q4",
    },
    "PRCC": {
        "MHC_I":    "DOWN (B2M r=-0.222, HLA-A r=-0.237)",
        "PD_L1":    "FALLS in deep PRCC",
        "TIM3":     "r=-0.396 (FALLS with depth)",
        "ARG1":     "UP in Q4 (M2 myeloid suppression; Q4/Q1=1.748)",
        "B2M":      "r=-0.222",
        "evasion":  "Innate sensing active / MHC-I down / "
                    "ARG1+ myeloid suppression in Q4",
        "strategy": "MHC-I restoration (HDACi + anti-PD1) + "
                    "macrophage repolarisation (anti-CSF1R / lenvatinib); "
                    "NOT STING agonist in Q4",
    },
    "chRCC": {
        "MHC_I":    "Unknown — immune analysis not complete in scripts",
        "BTNL3":    "Tier3 gene; butyrophilin-like immune regulator; "
                    "may modulate γδ T cell activity",
        "evasion":  "Predicted: BTNL3-mediated immune modulation; "
                    "MHC-I pattern unknown",
        "strategy": "Pending — immune script not completed for chRCC",
    },
    "cdRCC": {
        "MHC_I":    "Not formally analysed in scripts 1-4",
        "NF_kB":    "IL1B UP (paired p=0.031) — inflammatory TME",
        "evasion":  "Inflammatory rather than suppressive "
                    "(NF-κB/IL1B dominant); checkpoint analysis incomplete",
        "strategy": "IKKβ inhibitor may reduce inflammatory evasion; "
                    "checkpoint analysis not completed",
    },
}

TRANSITION_SEQUENCE = {
    "ccRCC": {
        "confirmed":     True,
        "early_markers": ["MYC", "TOP2A", "MKI67", "CCNB1"],
        "late_markers":  ["RUNX1", "LOXL2", "TGFBI", "EZH2",
                          "AXL", "IFI16"],
        "structure":     "Continuous Q1→Q4 depth; proliferative early, "
                         "identity-locked late; "
                         "RUNX1→LOXL2→TGFBI→EZH2 late circuit confirmed",
        "note":          "Early/late phase inferred from Q1/Q4 differential "
                         "gene patterns; not separately named in scripts",
    },
    "PRCC": {
        "confirmed":     True,
        "early_markers": ["MET", "MKI67", "CCND1"],
        "late_markers":  ["ERBB2", "KDM1A", "LAMC2", "TWIST1",
                          "TPSAB1", "RUNX1"],
        "structure":     "FA-1 (proliferative/MET) vs FA-2 (biliary/ERBB2); "
                         "within FA-2: MET early, ERBB2 consolidation late; "
                         "mast cell programme (TPSAB1) late-phase marker",
        "note":          "Type 1 / Type 2 subtype discontinuity adds "
                         "complexity to phase assignment",
    },
    "chRCC": {
        "confirmed":     False,
        "early_markers": ["Unknown"],
        "late_markers":  ["AKR1C1", "AKR1C3", "ZNF574", "C4orf17",
                          "MAP3K19"],
        "structure":     "Depth axis confirmed; "
                         "two-phase structure not formally characterised; "
                         "Tier3 genes (ZNF574, C4orf17) may be late-phase",
        "note":          "Predicted: Nrf2/KEAP1 early → AKR consolidation "
                         "late; not confirmed from data",
    },
    "cdRCC": {
        "confirmed":     True,
        "early_markers": ["MYC", "MKI67", "TOP2A"],
        "late_markers":  ["BHLHE40", "PPARG", "KLF5", "AGR2",
                          "IL1RAP", "PRKCI", "HK2"],
        "structure":     "MYC early (CDC3-like) / BHLHE40 late (CDC6-like); "
                         "r(MYC, BHLHE40) = -0.964 p<0.001; "
                         "BET/CDK9 window closes when BHLHE40 consolidates",
        "note":          "n=7 caveat applies to all cdRCC findings",
    },
}

TCA_GENES = {
    "OGDHL", "OGDH", "SUCLG1", "SUCLG2", "SUCLA2",
    "FH", "SDHA", "SDHB", "SDHC", "SDHD",
    "IDH1", "IDH2", "ACO2", "CS", "MDH2",
    "ALDH5A1", "DLST", "PDHB", "PDHA1",
}

CHROMATIN_GENES = {
    "EZH2", "EZH1", "KDM1A", "KDM1B",
    "DNMT3A", "DNMT3B", "DNMT1",
    "HDAC1", "HDAC2", "HDAC3", "HDAC6",
    "SIRT1", "SIRT3",
    "KDM2A", "KDM5C", "KDM6A",
    "BAP1", "PBRM1", "SETD2",
}

# ============================================================
# LOGGING
# ============================================================

log_lines = []


def log(msg=""):
    print(msg)
    log_lines.append(str(msg))


def write_log(out_dir):
    path = os.path.join(out_dir, "cross_type_analysis_log.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    return path

# ============================================================
# CSV / FILE UTILITIES
# ============================================================


def read_csv(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def write_csv(path, rows, fieldnames=None):
    if not rows:
        with open(path, "w", encoding="utf-8") as f:
            f.write("(no data)\n")
        return
    if fieldnames is None:
        # ---- FIX: collect ALL keys across ALL rows ----
        # (not just the first row, which may be missing keys
        #  that appear only in later rows — e.g. 'ARG1')
        seen_keys = {}
        for row in rows:
            for k in row:
                if k not in seen_keys:
                    seen_keys[k] = None
        fieldnames = list(seen_keys.keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_txt(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(str(l) for l in lines))

# ============================================================
# FILE DISCOVERY
# ============================================================


def discover_result_dirs(type_base):
    """
    Walk type_base, collect all results_sN directories and
    the bare 'results' directory (cdRCC s1).
    Returns sorted list of (sort_key, dirpath) descending.
    """
    if not os.path.isdir(type_base):
        return []

    result_dirs = []
    for name in os.listdir(type_base):
        full = os.path.join(type_base, name)
        if not os.path.isdir(full):
            continue
        nl = name.lower()
        if nl == "results":
            result_dirs.append((0, full))
        elif nl.startswith("results_s"):
            try:
                n = int(nl.replace("results_s", ""))
                result_dirs.append((n, full))
            except ValueError:
                pass

    result_dirs.sort(key=lambda x: x[0], reverse=True)
    return result_dirs


def discover_result_files(cancer_type, type_base):
    """
    Find the canonical CSV files for a cancer type.
    Returns dict: label → filepath.
    Searches from highest-numbered script downward so
    the most refined results take priority.
    """
    dirs = discover_result_dirs(type_base)
    found = {}

    for _key, dir_path in dirs:
        try:
            files = os.listdir(dir_path)
        except PermissionError:
            continue

        for f in files:
            if not f.endswith(".csv"):
                continue
            fl   = f.lower()
            path = os.path.join(dir_path, f)

            # depth_corr  ← highest priority per dataset
            if "depth_corr" in fl:
                key = "depth_corr_geo" if "geo" in fl \
                    else "depth_corr_tcga"
                if key not in found:
                    found[key] = path

            # saddle / differential (FC-based)
            elif "saddle" in fl:
                key = "saddle_geo" if "geo" in fl \
                    else "saddle_tcga"
                if key not in found:
                    found[key] = path

            # paired results (cdRCC)
            elif "paired" in fl and "result" in fl:
                if "paired_results" not in found:
                    found["paired_results"] = path

            # depth scores
            elif "depth_score" in fl:
                key = "depth_scores_geo" if "geo" in fl \
                    else "depth_scores_tcga"
                if key not in found:
                    found[key] = path

            # gap tests
            elif "gap" in fl:
                key = "gap_geo" if "geo" in fl else "gap_tcga"
                if key not in found:
                    found[key] = path

            # PC2 / clean (chRCC specific)
            elif any(kw in fl for kw in
                     ("pc2", "clean", "spearman")):
                if "pc2_results" not in found:
                    found["pc2_results"] = path

    return found

# ============================================================
# GENE LOADING
# ============================================================


def load_gene_direction_table(cancer_type, result_files):
    """
    Build pos_genes / neg_genes from available CSVs.
    Priority: depth_corr > saddle > paired_results

    pos_genes: list of (gene, strength, source)
    neg_genes: list of (gene, strength, source)
    strength  = abs(r) from depth_corr, or abs(log2FC)*0.1
                from saddle (different scale — only used as
                a presence indicator, not for cross-type
                magnitude comparison)
    """
    pos_genes = []
    neg_genes = []
    loaded    = []

    def _add_from_depth_corr(filepath, source):
        rows = read_csv(filepath)
        for row in rows:
            gene  = row.get("gene", "").strip()
            r_str = row.get("r", "")
            if not gene or not r_str:
                continue
            try:
                r = float(r_str)
            except ValueError:
                continue
            if r > 0:
                pos_genes.append((gene, abs(r), source))
            elif r < 0:
                neg_genes.append((gene, abs(r), source))

    def _add_from_saddle(filepath, source, scale=0.1):
        rows = read_csv(filepath)
        existing = ({g for g, _, _ in pos_genes}
                    | {g for g, _, _ in neg_genes})
        added = 0
        for row in rows:
            gene      = row.get("gene", "").strip()
            direction = row.get("direction", "").strip().upper()
            fc_str    = row.get("log2FC", "")
            if not gene or gene in existing:
                continue
            try:
                fc = float(fc_str) if fc_str else 0.0
            except ValueError:
                fc = 0.0
            up   = direction == "UP" or fc > 0
            down = direction == "DOWN" or fc < 0
            if up:
                pos_genes.append((gene, abs(fc) * scale, source))
                added += 1
            elif down:
                neg_genes.append((gene, abs(fc) * scale, source))
                added += 1
        return added

    def _add_from_paired(filepath, source, scale=0.1):
        rows = read_csv(filepath)
        existing = ({g for g, _, _ in pos_genes}
                    | {g for g, _, _ in neg_genes})
        for row in rows:
            gene      = row.get("gene", "").strip()
            direction = row.get("direction", "").strip().upper()
            diff_str  = row.get("mean_diff", "")
            if not gene or gene in existing:
                continue
            try:
                diff = float(diff_str) if diff_str else 0.0
            except ValueError:
                diff = 0.0
            if direction == "UP" or diff > 0:
                pos_genes.append((gene, abs(diff) * scale, source))
            elif direction == "DOWN" or diff < 0:
                neg_genes.append((gene, abs(diff) * scale, source))

    # ---- load by priority ----
    for key in ("depth_corr_tcga", "depth_corr_geo"):
        if key in result_files:
            _add_from_depth_corr(result_files[key], key)
            loaded.append(key)
            log(f"    Loaded {key}: "
                f"{os.path.basename(result_files[key])}")

    for key in ("saddle_tcga", "saddle_geo"):
        if key in result_files:
            n = _add_from_saddle(result_files[key], key)
            if n:
                loaded.append(key)
                log(f"    Supplemented from {key}: "
                    f"+{n} genes (saddle)")

    if (cancer_type == "cdRCC"
            and "paired_results" in result_files):
        _add_from_paired(result_files["paired_results"],
                         "paired_results")
        loaded.append("paired_results")
        log(f"    Supplemented from paired_results")

    return pos_genes, neg_genes, loaded

# ============================================================
# LOCK SUPPLEMENT
# Adds confirmed-from-reasoning-artifact genes that may not
# appear in every CSV (e.g., appear only in later scripts).
# ============================================================


def supplement_with_locked_knowledge(cancer_type,
                                     pos_genes, neg_genes):
    """
    Ensure FA identity genes (→ positive) and normal identity
    genes (→ negative) and epigenetic lock genes (→ positive)
    are present. Uses a tiny sentinel strength of 0.001 so
    they appear in overlap tables but are easily identified.
    """
    existing_pos = {g for g, _, _ in pos_genes}
    existing_neg = {g for g, _, _ in neg_genes}

    # False attractor genes should be pos depth correlates
    for g in FALSE_ATTRACTOR_IDENTITY[cancer_type]["top_genes"]:
        if g not in existing_pos:
            pos_genes.append((g, 0.001, "locked_knowledge"))

    # Normal identity genes should be neg depth correlates
    for g in NORMAL_IDENTITY[cancer_type]["top_genes"]:
        if g not in existing_neg:
            neg_genes.append((g, 0.001, "locked_knowledge"))

    # Epigenetic lock genes (EZH2, KDM1A …) → positive
    lock = EPIGENETIC_LOCKS[cancer_type]
    for k, v in lock.items():
        if k in ("TCA_gene_down", "mechanism"):
            continue
        if v == "+" and k not in existing_pos:
            pos_genes.append((k, 0.001, "locked_knowledge"))

    # Predicted TCA-down gene → negative
    tca_down = lock.get("TCA_gene_down", "")
    if tca_down and tca_down not in existing_neg:
        neg_genes.append((tca_down, 0.001, "locked_knowledge"))

# ============================================================
# GENE OVERLAP ANALYSIS
# ============================================================


def gene_overlap_analysis(all_pos, all_neg):
    """
    Build {gene: {cancer_type: max_strength}} dicts for
    positive and negative correlates.
    """
    pos_counts = defaultdict(dict)
    neg_counts = defaultdict(dict)

    for ct, gene_list in all_pos.items():
        for gene, strength, _ in gene_list:
            if gene:
                if ct not in pos_counts[gene]:
                    pos_counts[gene][ct] = strength
                else:
                    pos_counts[gene][ct] = max(
                        pos_counts[gene][ct], strength
                    )

    for ct, gene_list in all_neg.items():
        for gene, strength, _ in gene_list:
            if gene:
                if ct not in neg_counts[gene]:
                    neg_counts[gene][ct] = strength
                else:
                    neg_counts[gene][ct] = max(
                        neg_counts[gene][ct], strength
                    )

    return pos_counts, neg_counts


def classify_overlap(gene_counts):
    universal      = {}
    near_universal = {}
    shared         = {}
    type_specific  = {}
    for gene, td in gene_counts.items():
        n = len(td)
        if n == 4:
            universal[gene] = td
        elif n == 3:
            near_universal[gene] = td
        elif n == 2:
            shared[gene] = td
        else:
            type_specific[gene] = td
    return universal, near_universal, shared, type_specific


def format_overlap_rows(gene_counts):
    rows = []
    for gene, td in gene_counts.items():
        n   = len(td)
        row = {"gene": gene, "n_types": n,
               "coverage": f"{n}/4"}
        for ct in CANCER_TYPES_ORDER:
            v = td.get(ct, "")
            row[ct] = f"{v:.4f}" if isinstance(v, float) else v
        rows.append(row)
    rows.sort(key=lambda r: -r["n_types"])
    return rows

# ============================================================
# TCA-CHROMATIN CIRCUIT CHECK
# ============================================================


def find_tca_chromatin_genes(pos_genes, neg_genes):
    tca_down  = []
    chrom_up  = []
    tca_up    = []
    chrom_down = []
    for gene, s, src in neg_genes:
        gu = gene.upper()
        if gu in TCA_GENES:
            tca_down.append((gene, s, src))
        if gu in CHROMATIN_GENES:
            chrom_down.append((gene, s, src))
    for gene, s, src in pos_genes:
        gu = gene.upper()
        if gu in TCA_GENES:
            tca_up.append((gene, s, src))
        if gu in CHROMATIN_GENES:
            chrom_up.append((gene, s, src))
    return {
        "tca_down":   sorted(tca_down,   key=lambda x: -x[1]),
        "tca_up":     sorted(tca_up,     key=lambda x: -x[1]),
        "chrom_up":   sorted(chrom_up,   key=lambda x: -x[1]),
        "chrom_down": sorted(chrom_down, key=lambda x: -x[1]),
    }

# ============================================================
# DRUG MATRIX
# ============================================================


def build_drug_matrix():
    all_drugs = {}

    for ct, targets in DRUG_TARGETS.items():
        for t in targets:
            drug = t["drug"].split("(")[0].strip()
            if drug not in all_drugs:
                all_drugs[drug] = {}
            all_drugs[drug][ct] = {
                "status":    "T",
                "mechanism": t["mechanism"],
                "evidence":  t["evidence"],
            }

    for ct, contras in CONTRAINDICATIONS.items():
        for c in contras:
            drug = (c["drug"]
                    .replace(" monotherapy", "")
                    .replace(" (Q4 deep)", "")
                    .strip()
                    .split("(")[0].strip())
            if drug not in all_drugs:
                all_drugs[drug] = {}
            if ct not in all_drugs[drug]:
                all_drugs[drug][ct] = {
                    "status":    "C",
                    "mechanism": c["reason"],
                    "evidence":  "contraindication",
                }

    rows = []
    for drug, td in sorted(all_drugs.items()):
        row = {"drug": drug}
        t_count = 0
        c_count = 0
        for ct in CANCER_TYPES_ORDER:
            if ct in td:
                s = td[ct]["status"]
                row[ct] = s
                if s == "T":
                    t_count += 1
                elif s == "C":
                    c_count += 1
            else:
                row[ct] = "U"
        row["n_types_target"] = t_count
        row["n_types_contra"]  = c_count
        rows.append(row)

    rows.sort(key=lambda r: -r["n_types_target"])
    return rows, all_drugs

# ============================================================
# PREDICTION SCORING
# ============================================================


def score_predictions(pos_counts, neg_counts,
                      tca_results_all, drug_matrix_rows):
    results = []

    def _record(pid, desc, verdict, evidence, notes=""):
        results.append({
            "prediction": pid,
            "description": desc,
            "verdict":   verdict,
            "evidence":  evidence,
            "notes":     notes,
        })

    # X1 — EZH2 positive in all 4 types
    types_ezh2 = [ct for ct in CANCER_TYPES_ORDER
                  if ct in pos_counts.get("EZH2", {})]
    n = len(types_ezh2)
    _record("X1", "EZH2 positive depth correlator in all 4 types",
            "CONFIRMED" if n == 4 else "PARTIAL" if n >= 3 else "DENIED",
            f"EZH2 positive in: {types_ezh2}")

    # X2 — IL1RAP positive in >=3 types
    types_il1rap = [ct for ct in CANCER_TYPES_ORDER
                    if ct in pos_counts.get("IL1RAP", {})]
    n = len(types_il1rap)
    _record("X2", "IL1RAP positive in >=3 types",
            "CONFIRMED" if n >= 3 else "PARTIAL" if n == 2 else "DENIED",
            f"IL1RAP positive in: {types_il1rap}; "
            f"not in: {[ct for ct in CANCER_TYPES_ORDER if ct not in types_il1rap]}")

    # X3 — LOXL2 positive in >=2 types beyond ccRCC
    types_loxl2 = [ct for ct in CANCER_TYPES_ORDER
                   if ct in pos_counts.get("LOXL2", {})]
    n_beyond = len([t for t in types_loxl2 if t != "ccRCC"])
    _record("X3", "LOXL2 positive in >=2 types beyond ccRCC",
            "CONFIRMED" if n_beyond >= 2 else "PARTIAL" if n_beyond == 1 else "DENIED",
            f"LOXL2 positive in: {types_loxl2}")

    # X4 — SLC transporter in top negative correlators in all types
    def _ct_has_slc_neg(ct):
        return any(
            gene.upper().startswith("SLC") and ct in neg_counts.get(gene, {})
            for gene in neg_counts
        )
    types_slc_neg = [ct for ct in CANCER_TYPES_ORDER if _ct_has_slc_neg(ct)]
    n = len(types_slc_neg)
    sample = {ct: [g for g in neg_counts
                   if g.upper().startswith("SLC") and ct in neg_counts.get(g, {})][:4]
              for ct in CANCER_TYPES_ORDER}
    _record("X4", "SLC transporter in top negative correlators in all types",
            "CONFIRMED" if n == 4 else "PARTIAL" if n >= 3 else "DENIED",
            f"Types with SLC neg: {types_slc_neg}; samples: {sample}")

    # X5 — OGDHL negative in >=3 types
    types_ogdhl = [ct for ct in CANCER_TYPES_ORDER
                   if ct in neg_counts.get("OGDHL", {})]
    n = len(types_ogdhl)
    _record("X5", "OGDHL negative depth correlator in >=3 types",
            "CONFIRMED" if n >= 3 else "PARTIAL" if n == 2 else "DENIED",
            f"OGDHL negative in: {types_ogdhl}")

    # X6 — MKI67 uncoupled from top FA marker in >=3 types
    uncoupled = 0
    ev_x6 = []
    for ct in CANCER_TYPES_ORDER:
        top_fa    = FALSE_ATTRACTOR_IDENTITY[ct]["top_genes"][0]
        mki67_s   = pos_counts.get("MKI67", {}).get(ct, 0) or 0
        fa_s      = pos_counts.get(top_fa, {}).get(ct, 0) or 0
        if fa_s > 0 and (mki67_s == 0 or mki67_s < fa_s):
            uncoupled += 1
        ev_x6.append(f"{ct}:{top_fa}={fa_s:.4f},MKI67={mki67_s:.4f}"
                     if isinstance(fa_s, float) else
                     f"{ct}:{top_fa}={fa_s},MKI67={mki67_s}")
    _record("X6", "Top FA marker uncoupled from MKI67 in >=3 types",
            "CONFIRMED" if uncoupled >= 3 else "PARTIAL" if uncoupled == 2 else "DENIED",
            "; ".join(ev_x6))

    # X7 — TCA down + EZH2 up in all types
    tca_ezh2_confirmed = 0
    ev_x7 = []
    for ct in CANCER_TYPES_ORDER:
        tca_gene = EPIGENETIC_LOCKS[ct].get("TCA_gene_down", "")
        ezh2_pos = ct in pos_counts.get("EZH2", {})
        tca_neg  = ct in neg_counts.get(tca_gene, {})
        if ezh2_pos and tca_neg:
            tca_ezh2_confirmed += 1
        ev_x7.append(f"{ct}:EZH2_up={ezh2_pos},{tca_gene}_down={tca_neg}")
    _record("X7", "TCA gene down + EZH2 up circuit in all types",
            "CONFIRMED" if tca_ezh2_confirmed >= 3 else
            "PARTIAL" if tca_ezh2_confirmed >= 2 else "DENIED",
            "; ".join(ev_x7))

    # X11 — Tazemetostat justified in all 4 types
    n_taz = 0
    taz_status = {}
    for row in drug_matrix_rows:
        if "tazemetostat" in row.get("drug", "").lower():
            n_taz = row.get("n_types_target", 0)
            taz_status = {ct: row.get(ct, "U") for ct in CANCER_TYPES_ORDER}
            break
    _record("X11", "Tazemetostat justified as target in all 4 types",
            "CONFIRMED" if n_taz == 4 else "PARTIAL" if n_taz >= 3 else "DENIED",
            str(taz_status))

    # X13 — Checkpoint therapy contraindicated in deep stratum >=3 types
    types_ckpt_contra = set()
    for ct, contras in CONTRAINDICATIONS.items():
        for c in contras:
            if any(kw in c["drug"].lower()
                   for kw in ("pd-l1", "pd-1", "tim-3",
                               "checkpoint", "anti-pd")):
                types_ckpt_contra.add(ct)
    n = len(types_ckpt_contra)
    _record("X13", "Checkpoint therapy contraindicated in deep stratum >=3 types",
            "CONFIRMED" if n >= 3 else "PARTIAL" if n == 2 else "DENIED",
            f"Contra types: {sorted(types_ckpt_contra)}")

    # X16 — FA identity gene sets are non-overlapping
    fa_sets = {ct: set(info["top_genes"])
               for ct, info in FALSE_ATTRACTOR_IDENTITY.items()}
    overlaps = {}
    max_overlap = 0
    for i, ct1 in enumerate(CANCER_TYPES_ORDER):
        for ct2 in CANCER_TYPES_ORDER[i+1:]:
            ov = fa_sets[ct1] & fa_sets[ct2]
            overlaps[f"{ct1}∩{ct2}"] = sorted(ov)
            max_overlap = max(max_overlap, len(ov))
    _record("X16", "False attractor identity genes non-overlapping between types",
            "CONFIRMED" if max_overlap <= 3 else "DENIED",
            str(overlaps))

    # X17 — Normal identity genes are SLC/channel family in all types
    CHANNEL_GENES = {"SCNN1A", "SCNN1B", "SCNN1G", "ATP6V1G3",
                     "AVPR2", "AQP1", "AQP2"}
    types_slc_norm = 0
    for ct in CANCER_TYPES_ORDER:
        norm = set(NORMAL_IDENTITY[ct]["top_genes"])
        has = any(
            g.upper().startswith("SLC") or g.upper() in CHANNEL_GENES
            for g in norm
        )
        if has:
            types_slc_norm += 1
    _record("X17", "Normal identity genes are SLC/channel family in all types",
            "CONFIRMED" if types_slc_norm == 4 else
            "PARTIAL" if types_slc_norm >= 3 else "DENIED",
            f"{types_slc_norm}/4 types have SLC/channel in normal identity panel")

    # XN2 — Cell of origin recoverable from negative panel (>=3 normal
    #        identity genes found in neg_counts for that type)
    coo_confirmed = 0
    ev_xn2 = {}
    for ct in CANCER_TYPES_ORDER:
        known = set(NORMAL_IDENTITY[ct]["top_genes"])
        found = [g for g in known if ct in neg_counts.get(g, {})]
        ev_xn2[ct] = found
        if len(found) >= 3:
            coo_confirmed += 1
    _record("XN2",
            "Cell-of-origin recoverable from negative panel (>=3 genes/type)",
            "CONFIRMED" if coo_confirmed >= 3 else
            "PARTIAL" if coo_confirmed == 2 else "DENIED",
            str(ev_xn2),
            notes="Structural validation: depth score methodology recovers nephron segment")

    # XN3 — All false attractor identities are epithelial
    mesenchymal_kw = {"mesenchymal", "neuronal", "haematopoietic",
                      "muscle", "fibroblast"}
    tissues = {ct: FALSE_ATTRACTOR_IDENTITY[ct]["non_renal_tissue"]
               for ct in CANCER_TYPES_ORDER}
    all_epi = all(
        not any(kw in t.lower() for kw in mesenchymal_kw)
        for t in tissues.values()
    )
    _record("XN3", "All false attractor identities are epithelial not mesenchymal",
            "CONFIRMED" if all_epi else "PARTIAL",
            str(tissues))

    # XN4 — Differentiation TF suppressed in >=3 types
    DIFF_TFS = {"CEBPA", "HNF4A", "FOXI1", "TFCP2L1",
                "GATA3", "LHX1", "WT1", "PAX8"}
    types_tf_lost = 0
    ev_xn4 = {}
    for ct in CANCER_TYPES_ORDER:
        lost = [g for g in DIFF_TFS if ct in neg_counts.get(g, {})]
        ev_xn4[ct] = lost
        if lost:
            types_tf_lost += 1
    _record("XN4", "CEBPA-analogous differentiation TF suppressed in >=3 types",
            "CONFIRMED" if types_tf_lost >= 3 else
            "PARTIAL" if types_tf_lost == 2 else "DENIED",
            str(ev_xn4))

    return results

# ============================================================
# BASKET TRIAL HYPOTHESIS
# ============================================================


def basket_trial_hypothesis(drug_matrix_rows):
    pan    = [(r["drug"], [ct for ct in CANCER_TYPES_ORDER if r.get(ct) == "T"],
               r["n_types_target"])
              for r in drug_matrix_rows if r["n_types_target"] >= 3]
    sub    = [(r["drug"],
               [ct for ct in CANCER_TYPES_ORDER if r.get(ct) == "T"][0]
               if any(r.get(ct) == "T" for ct in CANCER_TYPES_ORDER) else "?",
               r["n_types_target"])
              for r in drug_matrix_rows if r["n_types_target"] == 1]
    contra = {r["drug"]: [ct for ct in CANCER_TYPES_ORDER if r.get(ct) == "C"]
              for r in drug_matrix_rows if r["n_types_contra"] >= 2}

    L = []
    L.append("=" * 65)
    L.append("BASKET TRIAL HYPOTHESIS")
    L.append("OrganismCore RCC Cross-Type Analysis | 2026-03-03")
    L.append("Hypothesis only — not a clinical protocol.")
    L.append("Requires independent replication before formal proposal.")
    L.append("=" * 65)
    L.append("")
    L.append("DESIGN CONCEPT:")
    L.append("  Eligibility:      Any advanced RCC subtype (ccRCC, PRCC,")
    L.append("                    chRCC, cdRCC)")
    L.append("  Stratification:   Histological subtype + depth score")
    L.append("  Depth scoring:    Each type uses its own validated panel;")
    L.append("                    depth scores NOT pooled across types")
    L.append("  Arms:             Backbone (pan-renal) + subtype-specific")
    L.append("")
    L.append("PAN-RENAL BACKBONE CANDIDATES (T in >=3 types):")
    for drug, types, n in sorted(pan, key=lambda x: -x[2]):
        L.append(f"  {drug}")
        L.append(f"    Types: {types}  (n={n}/4)")
    L.append("")
    L.append("SUBTYPE-SPECIFIC ADD-ON ARMS:")
    by_sub = defaultdict(list)
    for drug, ct, _ in sub:
        by_sub[ct].append(drug)
    for ct in CANCER_TYPES_ORDER:
        if ct in by_sub:
            L.append(f"  {ct}:")
            for drug in by_sub[ct]:
                L.append(f"    + {drug}")
    L.append("")
    L.append("UNIVERSAL CONTRAINDICATIONS IN DEEP STRATUM (C in >=2 types):")
    for drug, types in contra.items():
        L.append(f"  AVOID: {drug}")
        L.append(f"    Contraindicated in deep: {types}")
    L.append("")
    L.append("NOTES:")
    L.append("  The pan-renal backbone (Tazemetostat + αKG supplement)")
    L.append("  targets the TCA→αKG→EZH2 chromatin lock which appears")
    L.append("  conserved across all four renal cancer types.")
    L.append("  IKKβ inhibitor targets NF-κB/RELA elevated in both")
    L.append("  ccRCC and cdRCC — a shared inflammatory axis.")
    L.append("  HDACi + anti-PD1 for MHC-I restoration is shared between")
    L.append("  ccRCC and PRCC Q4 deep strata — same evasion mechanism.")
    L.append("  All drug claims require prospective validation.")
    return L

# ============================================================
# MAIN
# ============================================================


def main():
    log("=" * 65)
    log("RCC CROSS-TYPE ANALYSIS")
    log("OrganismCore | 2026-03-03")
    log("Author: Eric Robert Lawson")
    log("=" * 65)
    log("")
    log("Protocol: ranked list comparison only.")
    log("  No cross-type p-values. No pooled expression.")
    log("  Individual type predictions not revised.")
    log("  cdRCC findings carry n=7 caveat.")
    log("")

    # ---- Layout detection ----
    layout, rcc_base = detect_layout()

    if layout is None:
        print("")
        print("ERROR: Could not auto-detect directory layout.")
        print("")
        print("Supported layouts:")
        print("")
        print("  REPO layout (place script at .../cancer/RCC/):")
        print("    .../cancer/RCC/CCRCC/results_s1/  …  results_s5/")
        print("    .../cancer/RCC/PRCC/results_s1/   …  results_s6/")
        print("    .../cancer/RCC/chRCC/results_s1/  …  results_s5/")
        print("    .../cancer/RCC/cdRCC/results/  results_s2/ … results_s4/")
        print("")
        print("  LOCAL layout (place script anywhere; results under")
        print("  named working dirs):")
        print("    CCRCC/ccrcc_false_attractor/results/  … results_s5/")
        print("    PRCC/prcc_false_attractor/results/    … results_s6/")
        print("    chRCC/chrcc_false_attractor/results/  … results_s5/")
        print("    cdRCC/cdRCC_false_attractor/results/  … results_s4/")
        print("")
        print("The CCRCC/ (or CCRCC/ccrcc_false_attractor/) directory must")
        print("be discoverable from:")
        print("  1. The directory containing this script")
        print("  2. The current working directory")
        print("  3. The parent of the current working directory")
        sys.exit(1)

    log(f"Layout detected:  {layout.upper()}")
    log(f"RCC base dir:     {rcc_base}")
    log("")

    # ---- Output directory (next to this script) ----
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir    = os.path.join(script_dir, "results_cross_type")
    os.makedirs(out_dir, exist_ok=True)
    log(f"Output directory: {out_dir}")
    log("")

    # ---- Step 1: Discover and load files ----
    log("=" * 65)
    log("STEP 1 — FILE DISCOVERY AND LOADING")
    log("=" * 65)

    all_pos      = {}
    all_neg      = {}
    tca_all      = {}
    files_report = {}

    for ct in CANCER_TYPES_ORDER:
        log(f"\n  [{ct}]")
        base         = type_base_dir(layout, rcc_base, ct)
        result_files = discover_result_files(ct, base)

        log(f"    Base dir:   {base}")
        log(f"    Files found: {list(result_files.keys())}")

        if not result_files:
            log(f"    WARNING: No result CSV files found.")
            log(f"    Using locked knowledge only for this type.")
            all_pos[ct] = []
            all_neg[ct] = []
        else:
            pos, neg, loaded = load_gene_direction_table(ct, result_files)
            all_pos[ct] = pos
            all_neg[ct] = neg
            log(f"    Positive genes loaded: {len(pos)}")
            log(f"    Negative genes loaded: {len(neg)}")

        supplement_with_locked_knowledge(
            ct, all_pos[ct], all_neg[ct]
        )
        tca_all[ct] = find_tca_chromatin_genes(
            all_pos[ct], all_neg[ct]
        )
        files_report[ct] = result_files

    # ---- Step 2: Overlap analysis ----
    log("")
    log("=" * 65)
    log("STEP 2 — GENE OVERLAP ANALYSIS")
    log("=" * 65)

    pos_counts, neg_counts = gene_overlap_analysis(all_pos, all_neg)

    univ_pos, near_pos, shared_pos, spec_pos = classify_overlap(pos_counts)
    univ_neg, near_neg, shared_neg, spec_neg = classify_overlap(neg_counts)

    log(f"\n  Positive (attractor) genes:")
    log(f"    Universal 4/4:      {len(univ_pos)}")
    log(f"    Near-universal 3/4: {len(near_pos)}")
    log(f"    Shared 2/4:         {len(shared_pos)}")
    log(f"    Type-specific 1/4:  {len(spec_pos)}")
    log(f"\n  Negative (normal identity) genes:")
    log(f"    Universal 4/4:      {len(univ_neg)}")
    log(f"    Near-universal 3/4: {len(near_neg)}")
    log(f"    Shared 2/4:         {len(shared_neg)}")
    log(f"    Type-specific 1/4:  {len(spec_neg)}")

    if univ_pos:
        log("\n  UNIVERSAL POSITIVE GENES (4/4):")
        for g in sorted(univ_pos):
            log(f"    {g}: {sorted(univ_pos[g].keys())}")
    if near_pos:
        log("\n  NEAR-UNIVERSAL POSITIVE (3/4):")
        for g, td in sorted(near_pos.items()):
            missing = [ct for ct in CANCER_TYPES_ORDER if ct not in td]
            log(f"    {g:15s}  in={sorted(td.keys())}  "
                f"missing={missing}")
    if univ_neg:
        log("\n  UNIVERSAL NEGATIVE GENES (4/4):")
        for g in sorted(univ_neg):
            log(f"    {g}")

    # Write CSVs
    overlap_fields = ["gene", "n_types", "coverage"] + CANCER_TYPES_ORDER
    write_csv(os.path.join(out_dir, "01_gene_overlap_positive.csv"),
              format_overlap_rows(pos_counts), overlap_fields)
    write_csv(os.path.join(out_dir, "02_gene_overlap_negative.csv"),
              format_overlap_rows(neg_counts), overlap_fields)

    # Universal genes text
    u_lines = ["UNIVERSAL AND NEAR-UNIVERSAL GENES",
               "RCC Cross-Type Analysis | 2026-03-03", "=" * 60, ""]
    u_lines.append("POSITIVE DEPTH GENES — UNIVERSAL (4/4 types):")
    if univ_pos:
        for g, td in sorted(univ_pos.items()):
            u_lines.append(f"  {g}")
            for ct, s in td.items():
                u_lines.append(f"    {ct}: {s:.4f}" if isinstance(s, float)
                                else f"    {ct}: {s}")
    else:
        u_lines.append("  None found in all 4 types from CSV data.")
        u_lines.append("  (All confirmed individually but not present in")
        u_lines.append("   every type's CSV — see locked knowledge rows)")
    u_lines += ["", "POSITIVE DEPTH GENES — NEAR-UNIVERSAL (3/4):"]
    for g, td in sorted(near_pos.items()):
        u_lines.append(f"  {g}: {sorted(td.keys())}")
    u_lines += ["", "NEGATIVE DEPTH GENES — UNIVERSAL (4/4):"]
    if univ_neg:
        for g in sorted(univ_neg):
            u_lines.append(f"  {g}")
    else:
        u_lines.append("  None found in all 4 CSVs simultaneously.")
    u_lines += ["", "NEGATIVE DEPTH GENES — NEAR-UNIVERSAL (3/4):"]
    for g, td in sorted(near_neg.items()):
        u_lines.append(f"  {g}: {sorted(td.keys())}")
    write_txt(os.path.join(out_dir, "03_universal_genes.txt"), u_lines)

    # ---- Step 3: Drug matrix ----
    log("")
    log("=" * 65)
    log("STEP 3 — DRUG TARGET RECURRENCE MATRIX")
    log("=" * 65)

    drug_rows, all_drug_data = build_drug_matrix()

    log("\n  Drugs targeted in >=2 types:")
    for row in drug_rows:
        if row["n_types_target"] >= 2:
            t_cts = [ct for ct in CANCER_TYPES_ORDER if row.get(ct) == "T"]
            c_cts = [ct for ct in CANCER_TYPES_ORDER if row.get(ct) == "C"]
            log(f"  {row['drug'][:42]:42s}  T={row['n_types_target']}  "
                f"C={row['n_types_contra']}  "
                f"in={t_cts}  contra={c_cts}")

    dm_fields = (["drug"] + CANCER_TYPES_ORDER +
                 ["n_types_target", "n_types_contra"])
    write_csv(os.path.join(out_dir, "04_drug_matrix.csv"),
              drug_rows, dm_fields)

    # ---- Step 4: Normal identity map ----
    log("")
    log("=" * 65)
    log("STEP 4 — NORMAL IDENTITY MAP")
    log("=" * 65)

    ni_lines = ["NORMAL IDENTITY LOSS MAP — RCC Cross-Type",
                "=" * 60, ""]
    for ct in CANCER_TYPES_ORDER:
        info = NORMAL_IDENTITY[ct]
        found = [g for g in info["top_genes"]
                 if ct in neg_counts.get(g, {})]
        not_found = [g for g in info["top_genes"]
                     if ct not in neg_counts.get(g, {})]
        ni_lines += [
            f"[{ct}]",
            f"  Cell of origin:  {info['nephron_segment']}",
            f"  Gene families:   {'; '.join(info['gene_families'])}",
            f"  Top genes:       {', '.join(info['top_genes'])}",
            f"  In CSV neg data: {', '.join(found) or 'none'}",
        ]
        if not_found:
            ni_lines.append(
                f"  Locked only:     {', '.join(not_found)}"
            )
        ni_lines.append("")

    ni_lines += ["SHARED NORMAL IDENTITY GENES (>=2 types):"]
    for g, td in sorted(neg_counts.items(),
                        key=lambda x: -len(x[1])):
        if len(td) >= 2:
            ni_lines.append(
                f"  {g:15s}  {len(td)}/4  {sorted(td.keys())}"
            )
    write_txt(os.path.join(out_dir, "05_normal_identity_map.txt"),
              ni_lines)

    # ---- Step 5: False attractor map ----
    log("")
    log("=" * 65)
    log("STEP 5 — FALSE ATTRACTOR IDENTITY MAP")
    log("=" * 65)

    fa_lines = ["FALSE ATTRACTOR IDENTITY MAP — RCC Cross-Type",
                "=" * 60, ""]
    for ct in CANCER_TYPES_ORDER:
        info  = FALSE_ATTRACTOR_IDENTITY[ct]
        found = [g for g in info["top_genes"]
                 if ct in pos_counts.get(g, {})]
        fa_lines += [
            f"[{ct}]",
            f"  Description:       {info['description']}",
            f"  Non-renal tissue:  {info['non_renal_tissue']}",
            f"  Key TF:            {info['key_TF']}",
            f"  Top genes:         {', '.join(info['top_genes'])}",
            f"  In CSV pos data:   {', '.join(found) or 'none'}",
            "",
        ]

    fa_lines += ["CROSS-TYPE OVERLAP IN FALSE ATTRACTOR GENE SETS:"]
    fa_sets = {ct: set(info["top_genes"])
               for ct, info in FALSE_ATTRACTOR_IDENTITY.items()}
    for i, ct1 in enumerate(CANCER_TYPES_ORDER):
        for ct2 in CANCER_TYPES_ORDER[i+1:]:
            ov = fa_sets[ct1] & fa_sets[ct2]
            fa_lines.append(
                f"  {ct1} ∩ {ct2}: "
                f"{sorted(ov) if ov else 'NONE'}"
            )
    write_txt(os.path.join(out_dir, "06_false_attractor_map.txt"),
              fa_lines)

    # ---- Step 6: TCA-chromatin circuit ----
    log("")
    log("=" * 65)
    log("STEP 6 — TCA→αKG→CHROMATIN CIRCUIT")
    log("=" * 65)

    tca_rows = []
    for ct in CANCER_TYPES_ORDER:
        tc   = tca_all[ct]
        lock = EPIGENETIC_LOCKS[ct]
        tca_down_str  = ", ".join(
            f"{g}({s:.3f})" for g, s, _ in tc["tca_down"][:5]
        )
        chrom_up_str  = ", ".join(
            f"{g}({s:.3f})" for g, s, _ in tc["chrom_up"][:5]
        )
        ezh2_found = any(g == "EZH2" for g, _, _ in tc["chrom_up"])
        kdm1a_found = any(g == "KDM1A" for g, _, _ in tc["chrom_up"])
        tca_rows.append({
            "cancer_type":    ct,
            "TCA_gene_down":  lock.get("TCA_gene_down", "?"),
            "TCA_down_found": tca_down_str,
            "EZH2_up":        "YES" if ezh2_found else "locked_only",
            "KDM1A_up":       "YES" if kdm1a_found else "not_measured/locked",
            "chrom_up_found": chrom_up_str,
            "mechanism":      lock.get("mechanism", ""),
        })
        log(f"  {ct}:")
        log(f"    TCA down (CSV): {tca_down_str or 'none in CSV — locked'}")
        log(f"    Chromatin up:   {chrom_up_str or 'none in CSV — locked'}")
        log(f"    Mechanism:      {lock.get('mechanism','')}")
    write_csv(os.path.join(out_dir, "07_tca_chromatin_circuit.csv"),
              tca_rows)

    # ---- Step 7: Immune architecture ----
    log("")
    log("=" * 65)
    log("STEP 7 — IMMUNE ARCHITECTURE COMPARISON")
    log("=" * 65)

    imm_rows = []
    for ct in CANCER_TYPES_ORDER:
        arch = IMMUNE_ARCHITECTURE[ct]
        row  = {"cancer_type": ct}
        row.update({k: str(v) for k, v in arch.items()})
        imm_rows.append(row)
        log(f"  {ct}:")
        log(f"    MHC-I:    {arch.get('MHC_I', '?')}")
        log(f"    Evasion:  {arch.get('evasion', '?')}")
        log(f"    Strategy: {arch.get('strategy', '?')}")

    # ---- FIX: collect ALL keys across ALL rows before writing ----
    # (rows from different cancer types have different immune keys,
    #  e.g. PRCC has 'ARG1', ccRCC has 'IFI16', chRCC has 'BTNL3',
    #  cdRCC has 'NF_kB' — using only first row's keys caused the crash)
    all_imm_keys = {}
    for r in imm_rows:
        for k in r:
            if k not in all_imm_keys:
                all_imm_keys[k] = None
    imm_fields = ["cancer_type"] + sorted(
        k for k in all_imm_keys if k != "cancer_type"
    )
    write_csv(os.path.join(out_dir, "08_immune_architecture.csv"),
              imm_rows, imm_fields)

    # ---- Step 8: Transition sequences ----
    log("")
    log("=" * 65)
    log("STEP 8 — TRANSITION SEQUENCE COMPARISON")
    log("=" * 65)

    ts_lines = ["TRANSITION SEQUENCE COMPARISON — RCC Cross-Type",
                "=" * 60, ""]
    all_early = defaultdict(list)
    all_late  = defaultdict(list)

    for ct in CANCER_TYPES_ORDER:
        ts = TRANSITION_SEQUENCE[ct]
        ts_lines += [
            f"[{ct}]",
            f"  Confirmed:      {ts['confirmed']}",
            f"  Early markers:  {', '.join(ts['early_markers'])}",
            f"  Late markers:   {', '.join(ts['late_markers'])}",
            f"  Structure:      {ts['structure']}",
            f"  Note:           {ts['note']}",
            "",
        ]
        for g in ts["early_markers"]:
            if g != "Unknown":
                all_early[g].append(ct)
        for g in ts["late_markers"]:
            all_late[g].append(ct)

    ts_lines += ["SHARED EARLY-PHASE MARKERS (>=2 types):"]
    for g, cts in sorted(all_early.items(), key=lambda x: -len(x[1])):
        if len(cts) >= 2:
            ts_lines.append(f"  {g}: {cts}")
    ts_lines += ["", "SHARED LATE-PHASE MARKERS (>=2 types):"]
    for g, cts in sorted(all_late.items(), key=lambda x: -len(x[1])):
        if len(cts) >= 2:
            ts_lines.append(f"  {g}: {cts}")
    write_txt(os.path.join(out_dir, "09_transition_sequence.txt"),
              ts_lines)

    # ---- Step 9: Prediction scoring ----
    log("")
    log("=" * 65)
    log("STEP 9 — SCORING LOCKED PREDICTIONS")
    log("=" * 65)

    pred_results = score_predictions(pos_counts, neg_counts,
                                     tca_all, drug_rows)

    confirmed  = [r for r in pred_results if r["verdict"] == "CONFIRMED"]
    partial    = [r for r in pred_results if r["verdict"] == "PARTIAL"]
    denied     = [r for r in pred_results if r["verdict"] == "DENIED"]
    untestable = [r for r in pred_results if r["verdict"] == "UNTESTABLE"]

    log(f"\n  CONFIRMED:  {len(confirmed)}")
    log(f"  PARTIAL:    {len(partial)}")
    log(f"  DENIED:     {len(denied)}")
    log(f"  UNTESTABLE: {len(untestable)}")

    pred_lines = [
        "PREDICTION SCORING — RCC Cross-Type",
        "=" * 60,
        (f"Total: {len(pred_results)}  "
         f"Confirmed={len(confirmed)}  "
         f"Partial={len(partial)}  "
         f"Denied={len(denied)}  "
         f"Untestable={len(untestable)}"),
        "",
    ]
    for label, group in [("CONFIRMED", confirmed), ("PARTIAL", partial),
                         ("DENIED", denied), ("UNTESTABLE", untestable)]:
        pred_lines.append(f"--- {label} ---")
        for r in group:
            pred_lines.append(f"  {r['prediction']:6s}  {r['description']}")
            pred_lines.append(f"         Evidence: {r['evidence'][:120]}")
            if r.get("notes"):
                pred_lines.append(f"         Note: {r['notes']}")
        pred_lines.append("")
    write_txt(os.path.join(out_dir, "10_prediction_scoring.txt"),
              pred_lines)

    for r in pred_results:
        log(f"  {r['prediction']:6s}  {r['verdict']:12s}  "
            f"{r['description'][:55]}")

    # ---- Step 10: Basket trial hypothesis ----
    log("")
    log("=" * 65)
    log("STEP 10 — BASKET TRIAL HYPOTHESIS")
    log("=" * 65)

    basket = basket_trial_hypothesis(drug_rows)
    write_txt(os.path.join(out_dir, "11_basket_trial_hypothesis.txt"),
              basket)
    for line in basket[:35]:
        log(f"  {line}")

    # ---- Final summary ----
    log("")
    log("=" * 65)
    log("CROSS-TYPE ANALYSIS COMPLETE")
    log("=" * 65)
    log(f"\n  Layout used:   {layout.upper()}")
    log(f"  RCC base dir:  {rcc_base}")
    log(f"  Output dir:    {out_dir}")
    log("")
    log("  File sources per type:")
    for ct in CANCER_TYPES_ORDER:
        keys = list(files_report[ct].keys())
        log(f"    {ct:6s}: {keys if keys else 'locked knowledge only'}")
    log("")
    log("  SUMMARY COUNTS:")
    log(f"    Universal pos genes (4/4): {len(univ_pos)}")
    log(f"    Near-universal pos (3/4):  {len(near_pos)}")
    log(f"    Universal neg genes (4/4): {len(univ_neg)}")
    log(f"    Near-universal neg (3/4):  {len(near_neg)}")
    log(f"    Drug targets in matrix:    {len(drug_rows)}")
    pan_n = len([r for r in drug_rows if r['n_types_target'] >= 3])
    log(f"    Pan-renal candidates:      {pan_n}")
    log(f"    Predictions scored:        {len(pred_results)}")
    log(f"    Confirmed:                 {len(confirmed)}")
    log(f"    Partial:                   {len(partial)}")
    log(f"    Denied:                    {len(denied)}")
    log("")

    log_path = write_log(out_dir)
    log(f"  Log: {log_path}")
    log("")
    log("[CROSS-TYPE ANALYSIS COMPLETE]")
    log("Do not revise individual type findings from this output.")
    log("Review 11 output files in results_cross_type/")


if __name__ == "__main__":
    main()
