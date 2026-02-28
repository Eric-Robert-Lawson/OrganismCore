# OrganismCore — Cancer False Attractor Analysis

## Structure

Each cancer type has its own folder.
Each folder contains:
  - The analysis script
  - The raw annotation file
  - The expression cache (generated on first run)
  - The results CSV
  - The figure PNG
  - The analysis log
  - The reasoning artifact (Document N)

---

## The Cross-Cancer Table — COMPLETE (Session 1)

| Cancer | Lineage | Switch Genes | Suppression | p-value |
|--------|---------|--------------|-------------|---------|
| AML | Myeloid | SPI1 | 90.5% | 0.00e+00 |
| | | KLF4 | 94.7% | 0.00e+00 |
| | | IRF8 | 69.5% | 0.00e+00 |
| CRC | Epithelial/Colonocyte | CDX2 | 79.5% | 3.89e-154 |
| GBM | Oligodendrocyte | SOX10 | 88.6% | 5.50e-188 |
| | | MBP | 89.6% | 1.97e-143 |
| | | MOG | 56.9% | 2.97e-91 |
| | | PLP1 | 83.4% | 1.27e-280 |
| BRCA | Luminal Epithelial | FOXA1 | 80.7% | 8.34e-162 |
| | | GATA3 | 53.4% | 2.30e-104 |
| | | ESR1 | 96.7% | 0.00e+00 |
| LUAD | Alveolar/AT2 | FOXA2 | 57.2% | 1.10e-132 |
| | | SFTPC | 95.7% | 0.00e+00 |
| | | SFTPB | 72.7% | 0.00e+00 |
| | | SFTPA1 | 91.4% | 0.00e+00 |

**Zero gene overlap across all five confirmed switch gene sets.**
**15 switch genes confirmed. 583,249 cells analyzed.**
**Same principle. Different molecular language. Five cancers deep.**

---

## Completed

### AML — Acute Myeloid Leukemia
```
Data:    Zenodo:10013368 (VanGalen-Oetjen)
         van Galen et al. 2019, Cell
         74,583 cells — 10,130 malignant
Block:   GMP-like/Prog-like vs CD14+ monocytes
Lineage: Myeloid

Switch genes confirmed:
  SPI1:  90.5% suppressed  p=0.00e+00 ***
  KLF4:  94.7% suppressed  p=0.00e+00 ***
  IRF8:  69.5% suppressed  p=0.00e+00 ***

Controls: 4/4 as predicted
Scaffold gene distinction first observed:
  CD34 present throughout hierarchy —
  not suppressed at block (correct)

Therapeutic target:
  CRISPRa SPI1 + KLF4 + IRF8

Document: AML/aml_false_attractor_confirmed.md (Doc 72)
```

### CRC — Colorectal Cancer
```
Data:    Zenodo:14602110
         192,166 cells — 477 gene panel
Block:   Epithelial 2 (MKI67+ TOP2A+)
         vs Epithelial 1 (KRT8+ MUC13+)
Lineage: Colonocyte/Epithelial

Switch genes confirmed:
  CDX2:  79.5% suppressed  p=3.89e-154 ***

Unexpected finding:
  IRF8: +211% elevated — lineage infidelity
  First observation of cross-lineage
  expression pattern.

Therapeutic target:
  CRISPRa CDX2 + CRISPRi IRF8

Document: CRC/crc_false_attractor_confirmed.md (Doc 73)
```

### GBM — Glioblastoma
```
Data:    GSE131928 — Neftel et al. 2019, Cell
         7,930 cells — 28 IDH-wt patients
Block:   OPC-like vs Normal oligodendrocytes
         1,334 cells each
Lineage: Oligodendrocyte/Neural

Switch genes confirmed:
  SOX10: 88.6% suppressed  p=5.50e-188 ***
  MBP:   89.6% suppressed  p=1.97e-143 ***
  MOG:   56.9% suppressed  p=2.97e-91  ***
  PLP1:  83.4% suppressed  p=1.27e-280 ***

Scaffold gene confirmed:
  OLIG2: +21.5% elevated — lineage identity
  gene, not terminal switch gene.

Elevated 4/4: PDGFRA EGFR SOX2 NES

Therapeutic target:
  CRISPRa SOX10 + MBP + PLP1

Document: GBM/gbm_false_attractor_confirmed.md (Doc 74)
```

### BRCA — Breast Cancer
```
Data:    GSE176078 — Wu et al. 2021
         Nature Genetics
         100,064 cells — 26 primary tumors
Block:   Cancer Basal SC (TNBC)
         vs Mature Luminal
Lineage: Luminal Epithelial

Switch genes confirmed:
  FOXA1: 80.7% suppressed  p=8.34e-162 ***
  GATA3: 53.4% suppressed  p=2.30e-104 ***
  ESR1:  96.7% suppressed  p=0.00e+00  ***

Landscape geometry observed:
  LumA cancer is NOT a false attractor —
  FOXA1/GATA3 at or above normal luminal.
  False attractor is specifically TNBC.

Cross-lineage: SOX10 +1323% in TNBC
Scaffold oncogene: MYC flat throughout

Therapeutic target:
  CRISPRa FOXA1 + GATA3 + ESR1
  (TNBC only)

Document: BRCA/brca_false_attractor_confirmed.md (Doc 75)
```

### LUAD — Lung Adenocarcinoma
```
Data:    GSE131907 — Kim et al. 2020
         Nature Communications
         208,506 cells — 44 patients
Block:   Malignant cells vs AT2
         24,784 malignant / 2,020 AT2
Lineage: Alveolar Type II / AT2

Switch genes confirmed:
  FOXA2:  57.2% suppressed  p=1.10e-132 ***
  SFTPC:  95.7% suppressed  p=0.00e+00  ***
  SFTPB:  72.7% suppressed  p=0.00e+00  ***
  SFTPA1: 91.4% suppressed  p=0.00e+00  ***

NKX2-1: 19.3% partial — scaffold gene.
  Lung lineage identity gene retained
  in malignant cells (correct biology).

FOXA resolution test:
  FOXA2 (lung gate): 57.2% suppressed
  FOXA1 (breast gate): +115% elevated
  Malignant LUAD closes the lung pioneer
  TF and opens the breast pioneer TF.
  Cross-lineage TF substitution within
  the same protein family.

Elevated 4/4: EGFR SOX2 KRT5 MYC
  SOX2: +2827% — near-zero in AT2,
  massively elevated in malignant LUAD.

Therapeutic target:
  CRISPRa FOXA2 + SFTPC
  + CRISPRi FOXA1

Document: LUAD/luad_false_attractor_confirmed.md (Doc 76)
```

---

## Upcoming Validations — Full Map

The method works for any cancer type
with a public scRNA-seq dataset that
contains both malignant cells and
a normal differentiated endpoint.
Requirements:
  1. Public scRNA-seq (GEO or similar)
  2. Cell type annotations present
  3. Normal cells in the same dataset
     OR normal tissue co-profiled
  4. Known terminal differentiation
     markers for the lineage

The following cancers all satisfy
these requirements. Data exists.
Predictions are derivable from
known differentiation biology.
This is the full map.

---

### Session 2 — Hematopoietic Cancers
#### CML — Chronic Myeloid Leukemia
```
Lineage:  Myeloid (granulocyte)
Block:    CML Primitive stem cells
          vs committed myeloid (My)
          cells — conservative
          comparison (CD34+ enriched,
          mature neutrophils excluded
          by sort protocol — true
          signal larger than reported)
Confirmed switch genes:
  CEBPA  — granulocyte master TF       90.3%  p=0.00e+00
  CEBPE  — late granulocyte maturation 99.1%  p=1.14e-161
  ELANE  — neutrophil elastase         97.7%  p=4.30e-205
  CAMP   — terminal neutrophil peptide 88.6%  p=0.0112
Cross-cancer myeloid confirmation:
  SPI1   — confirmed AML + CML         70.9%  p=0.00e+00
  IRF8   — confirmed AML + CML         93.7%  p=3.18e-30
  KLF4   — AML-specific (not CML)      11.8%  ns
             informative divergence
Depth gradient confirmed:
  Primitive → MPP2 → MPP1 → My/Ly → My
  Monotonic increase all switch genes
  Waddington geometry directly observed
New finding:
  CML stem cells are quiescent
  (MKI67 suppressed 92.9% in Primitive)
  False attractor is non-cycling —
  explains imatinib persistence failure
  Switch gene reactivation reaches
  quiescent cells — BCR-ABL inhibition
  does not
  CSF3R suppressed 62.8% — self-
  maintaining attractor mechanism
Data:     GSE236233 (Warfvinge 2024
          eLife — 9 patients, 20,395
          cells, 33,538 genes)
Status:   CONFIRMED
Doc:      78
```

#### ALL — Acute Lymphoblastic Leukemia
```
Lineage:  B-lymphocyte or T-lymphocyte
Block:    B-ALL blasts vs mature B cells
          T-ALL blasts vs mature T cells
Predicted switch genes (B-ALL):
  PAX5   — B cell identity master TF
  EBF1   — early B cell factor
  PRDM1  — terminal plasma cell
Predicted switch genes (T-ALL):
  BCL11B — T cell identity TF
  GATA3  — T cell maturation
           (also BRCA control — watch
           for cross-lineage)
Data:    GSE132509 or GSE138398
Doc: 78
```

#### CLL — Chronic Lymphocytic Leukemia
```
Lineage:  B-lymphocyte (mature)
Block:    CLL cells vs normal
          mature B cells
Predicted switch genes:
  PRDM1  — plasma cell terminal TF
  IRF4   — plasma cell completion
  XBP1   — unfolded protein response
           (plasma cell secretory)
Data:    GSE111014 or GSE130120
Doc: 79
```

#### Multiple Myeloma
```
Lineage:  Plasma cell
Block:    Myeloma cells vs normal
          plasma cells
Predicted switch genes:
  PRDM1  — plasma cell master TF
  IRF4   — plasma cell identity
  XBP1   — secretory completion
Data:    GSE193531 or
         MMRF CoMMpass Study
Note:    Plasma cell is already the
         terminal state — myeloma may
         represent a WITHIN-terminal
         false attractor.
         Interesting edge case.
Doc: 80
```

#### MDS — Myelodysplastic Syndrome
```
Lineage:  Multi-lineage (erythroid,
          myeloid, megakaryocyte)
Block:    MDS progenitors vs normal
          differentiated cells
Predicted switch genes:
  GATA1  — erythroid/megakaryocyte TF
  KLF1   — erythroid terminal TF
  HBB    — hemoglobin beta (terminal)
Data:    GSE140559 or GSE145491
Note:    Multi-lineage block means
         multiple switch gene sets
         may be suppressable
         simultaneously.
Doc: 81
```

---

### Session 3 — Solid Tumor Epithelial

#### PAAD — Pancreatic Adenocarcinoma
```
Lineage:  Acinar or ductal epithelial
Block:    PDAC cells vs normal
          pancreatic ductal cells
          OR acinar cells
Predicted switch genes:
  PTF1A  — pancreatic acinar TF
  RBPJL  — acinar terminal TF
  PRSS1  — trypsinogen (acinar terminal)
  SPT1   — acinar secretory marker
Data:    GSE155698 (Moncada)
         or PDAC atlas (Chan-Seng-Yue
         et al. 2020 Nature Genetics)
Note:    Pancreatic cancer has the
         worst prognosis of all cancers
         tested so far. The therapeutic
         implications here are the most
         urgent.
Doc: 82
```

#### PRAD — Prostate Adenocarcinoma
```
Lineage:  Luminal secretory epithelial
Block:    Prostate cancer cells vs
          normal luminal prostate
Predicted switch genes:
  NKX3-1 — prostate identity master TF
  AR     — androgen receptor
           (confirmed present in BRCA
           dataset — watch for
           cross-cancer signal)
  KLK3   — PSA / terminal secretory
Data:    GSE176031 or GSE141370
Note:    AR is to prostate what ESR1
         is to breast. Both nuclear
         hormone receptors. Both
         terminal identity genes.
         Predicting >90% suppression
         in CRPC (castration-resistant
         prostate cancer).
Doc: 83
```

#### STAD — Stomach Adenocarcinoma
```
Lineage:  Gastric epithelial (chief
          cells or pit cells)
Block:    Gastric cancer cells vs
          normal gastric epithelium
Predicted switch genes:
  MIST1  — chief cell terminal TF
  PGC    — pepsinogen C (chief terminal)
  GKN1   — gastrokine (pit terminal)
  TFF1   — trefoil factor (pit marker)
Data:    GSE134520 (Kumar et al.)
         or STAD Human Cell Atlas
Doc: 84
```

#### ESCA — Esophageal Cancer
```
Lineage:  Squamous or Barrett's
          adenocarcinoma
Block:    ESCC cells vs normal
          esophageal squamous
          OR Barrett's vs normal
Predicted switch genes (squamous):
  TP63   — squamous identity TF
  KRT14  — basal squamous marker
  IVL    — involucrin (terminal)
Data:    GSE160269 or GSE188476
Note:    TP63 was in the LUAD
         extraction — watch for
         cross-cancer signal.
Doc: 85
```

#### BLCA — Bladder Cancer
```
Lineage:  Urothelial epithelial
Block:    Bladder cancer cells vs
          normal urothelium
Predicted switch genes:
  FOXA1  — confirmed BRCA 80.7%
           ALSO a urothelial TF
           (bladder and breast share
           FOXA1 as a gate —
           cross-cancer test of
           whether same gene can be
           a switch gene in two
           different cancers)
  GATA3  — confirmed BRCA 53.4%
           also expressed in
           urothelium
  UPK1B  — uroplakin (terminal
           urothelial marker)
Data:    GSE222315 or GSE135337
Note:    FOXA1 and GATA3 may be
         confirmed BOTH in BRCA and
         BLCA — two cancers, same
         switch genes, different
         because the urothelium and
         luminal breast share a
         developmental origin.
         This would be a framework
         refinement: switch genes can
         overlap if lineages share
         developmental history.
Doc: 86
```

#### HCC — Hepatocellular Carcinoma
```
Lineage:  Hepatocyte
Block:    HCC cells vs normal
          hepatocytes
Predicted switch genes:
  HNF4A  — hepatocyte master TF
           (was in CRC panel but
           absent from dataset —
           now test in correct tissue)
  ALB    — albumin (terminal marker)
  APOB   — apolipoprotein B
           (terminal secretory)
  CYP3A4 — cytochrome P450
           (terminal metabolic)
Data:    GSE149614 (Ma et al.)
         or GSE151530 (Zhang et al.)
Note:    HNF4A was predicted in CRC
         but missing from the panel.
         This is the first chance to
         test it in its primary tissue.
Doc: 87
```

#### ICC — Intrahepatic
#### Cholangiocarcinoma
```
Lineage:  Cholangiocyte (bile duct)
Block:    ICC cells vs normal
          cholangiocytes
Predicted switch genes:
  SOX17  — cholangiocyte identity TF
  HNF1B  — biliary specification
  KRT19  — cholangiocyte marker
Data:    GSE138709 or
         combined liver atlas
Doc: 88
```

#### RCC — Renal Cell Carcinoma
```
Lineage:  Proximal tubule epithelial
Block:    ccRCC cells vs normal
          proximal tubule cells
Predicted switch genes:
  HNF1A  — renal tubule TF
  CUBN   — cubilin (proximal tubule
           terminal marker)
  SLC34A1 — phosphate transporter
            (proximal tubule terminal)
Data:    GSE171306 or GSE207493
Note:    ccRCC is driven by VHL loss
         and HIF activation. The false
         attractor is a hypoxia-locked
         dedifferentiated state.
Doc: 89
```

#### OV — Ovarian Cancer
```
Lineage:  Fallopian tube epithelial
          (STIC origin) or
          ovarian surface epithelial
Block:    HGSOC cells vs normal
          fallopian tube epithelium
Predicted switch genes:
  PAX8   — Müllerian epithelial TF
  WT1    — ovarian surface marker
  OVGP1  — oviductal glycoprotein
           (fallopian terminal)
Data:    GSE154600 or
         TCGA + scRNA-seq atlas
Doc: 90
```

#### UCEC — Endometrial Cancer
```
Lineage:  Endometrial epithelial
Block:    Endometrial cancer vs
          normal endometrium
Predicted switch genes:
  FOXA2  — confirmed LUAD
           ALSO expressed in
           endometrium —
           second test of FOXA2
           in a different tissue
  PGR    — progesterone receptor
           (endometrial terminal)
  HAND2  — endometrial stromal TF
Data:    GSE213216 or TCGA UCEC
         + scRNA atlas
Note:    FOXA2 overlap with LUAD
         would be second confirmation
         of FOXA2 as a switch gene
         in a different tissue context.
Doc: 91
```

---

### Session 4 — Rare and Aggressive

#### PDAC Subtypes
```
Classical vs Basal-like PDAC
Two false attractors within one cancer.
Same approach as BRCA LumA vs TNBC.
Doc: 92
```

#### Uveal Melanoma
```
Lineage:  Melanocyte/neural crest
Block:    Uveal melanoma vs normal
          uveal melanocytes
Predicted switch genes:
  MITF   — melanocyte master TF
  DCT    — dopachrome tautomerase
           (terminal melanin synthesis)
  TYRP1  — tyrosinase-related protein
Data:    GSE139829
Note:    MITF is the melanocyte
         equivalent of FOXA1 in breast.
         One master TF defining
         terminal melanocyte identity.
Doc: 93
```

#### Cutaneous Melanoma
```
Same logic as uveal but different
microenvironment and mutation spectrum.
MITF, DCT, TYRP1 as switch genes.
BRAF V600E drives the false attractor.
Data: GSE215120 or GSE72056
Doc: 94
```

#### Mesothelioma
```
Lineage:  Mesothelial cell
Block:    Mesothelioma vs normal
          mesothelium
Predicted switch genes:
  WT1    — mesothelial identity TF
  MSLN   — mesothelin (terminal)
  CALB2  — calretinin (terminal marker)
Data:    GSE195615
Doc: 95
```

#### Thyroid Cancer — PTC/FTC
```
Lineage:  Thyroid follicular cell
Block:    Thyroid cancer vs normal
          follicular cells
Predicted switch genes:
  NKX2-1 — confirmed LUAD partial
           ALSO the thyroid identity TF
           (TTF-1 is NKX2-1 —
           used in both lung and thyroid)
           Second test of NKX2-1 in
           its primary thyroid context
  PAX8   — thyroid specification TF
  TG     — thyroglobulin (terminal)
  TSHR   — TSH receptor (terminal)
Data:    GSE184362 or GSE213647
Note:    NKX2-1 was partial in LUAD
         (scaffold). In thyroid it may
         be a switch gene — its primary
         tissue. This would refine the
         scaffold/switch distinction:
         NKX2-1 is scaffold in lung
         but switch in thyroid.
Doc: 96
```

#### Neuroblastoma
```
Lineage:  Sympathetic neuron /
          chromaffin cell
Block:    Neuroblastoma cells vs
          normal sympathetic neurons
Predicted switch genes:
  PHOX2B — sympathetic neuron TF
  DBH    — dopamine beta-hydroxylase
           (terminal chromaffin)
  TH     — tyrosine hydroxylase
Data:    GSE137804 or GSE137804
Doc: 97
```

#### Medulloblastoma
```
Lineage:  Cerebellar granule neuron
Block:    MB cells vs normal
          granule neuron precursors
Predicted switch genes:
  ATOH1  — granule neuron TF
           (was in CRC panel, absent)
           Now test in correct tissue
  NEUROD1 — neuronal differentiation
  RBFOX3  — mature neuron marker
Data:    GSE119926 or GSE155446
Note:    ATOH1 was predicted in CRC
         but missing from panel.
         First test in its actual
         tissue of function.
Doc: 98
```

---

### Session 5 — Liquid Tumors and
### Rare Hematopoietic

#### DLBCL — Diffuse Large B Cell Lymphoma
```
Lineage:  Germinal center B cell
          → plasma cell
Block:    DLBCL cells vs normal GC
          B cells or plasma cells
Predicted switch genes:
  PRDM1  — plasma cell TF
  IRF4   — plasma cell identity
  BLIMP1 — terminal B cell
Data:    GSE181063 or GSE132509
Doc: 99
```

#### Follicular Lymphoma
```
Lineage:  Follicular B cell
Block:    FL cells vs normal
          follicular B cells
Predicted switch genes:
  BCL6   — germinal center master TF
           (loss of BCL6 is required
           for terminal B cell
           differentiation — this
           may INVERT the prediction:
           BCL6 ELEVATED in FL because
           it PREVENTS terminal
           differentiation)
  PRDM1  — downstream of BCL6
Data:    GSE181063
Note:    BCL6 is a repressor of
         terminal B cell
         differentiation. FL may be
         the first case where the
         false attractor is maintained
         by ACTIVE expression of a TF
         that represses the switch genes,
         rather than by suppression of
         the switch genes directly.
         Framework stress test.
Doc: 100
```

#### T Cell Lymphoma
```
Lineage:  T cell (various subtypes)
Block:    PTCL cells vs normal
          mature T cells
Predicted switch genes:
  TBX21  — Th1 identity TF
  GATA3  — Th2 identity TF
           (confirmed BRCA, ALL —
           third cancer test)
  RORC   — Th17 terminal TF
Data:    GSE188053
Doc: 101
```

#### Mast Cell Disease / MCL
```
Lineage:  Mast cell
Block:    Mastocytosis vs normal
          mast cells
Predicted switch genes:
  MITF   — mast cell identity TF
           (also melanocyte — second
           tissue test)
  TPSAB1 — tryptase (terminal)
Data:    GSE141560
Doc: 102
```

---

### Session 6 — Brain Tumors

#### LGG — Low Grade Glioma (IDH-mutant)
```
Lineage:  Oligodendrocyte or astrocyte
Block:    IDH-mutant glioma vs
          normal oligodendrocyte
          (same switch genes as GBM?)
Predicted switch genes:
  SOX10  — confirmed GBM 88.6%
  MBP    — confirmed GBM 89.6%
  PLP1   — confirmed GBM 83.4%
Data:    GSE131928 (Neftel — same
         dataset, IDH-mutant subset)
Note:    Direct comparison with GBM.
         IDH-mutant glioma is less
         aggressive than IDH-wt GBM.
         Does it show less switch gene
         suppression? This would be
         the first test of whether
         suppression magnitude
         correlates with clinical
         aggressiveness.
Doc: 103
```

#### Ependymoma
```
Lineage:  Ependymal cell
Block:    Ependymoma vs normal
          ependymal cells
Predicted switch genes:
  FOXJ1  — ependymal/ciliated TF
  CFAP126 — ciliogenesis (terminal)
Data:    GSE141383
Doc: 104
```

#### Oligodendroglioma
```
Lineage:  Oligodendrocyte (IDH+1p19q)
Block:    Oligodendroglioma cells vs
          normal oligodendrocytes
Same switch genes as GBM predicted.
Third test of SOX10/MBP/PLP1 axis.
Data:    GSE131928 subset
Doc: 105
```

---

### Session 7 — Cross-Tissue Validation

#### Matched Primary and Metastasis
```
Use LUAD dataset (GSE131907) which
contains primary tumor, brain
metastasis, and pleural effusion
from the same patients.

Question: Do metastatic cells show
MORE or LESS switch gene suppression
than primary tumor cells?

Prediction: Metastatic cells are
MORE suppressed — deeper in the
false attractor. The metastatic
state requires losing even more
differentiation identity.

This tests whether the false attractor
depth correlates with metastatic
potential.
Doc: 106
```

#### Chemotherapy-Resistant Subpopulations
```
Multiple datasets contain matched
pre- and post-treatment samples.

Question: Do resistant cells show
MORE switch gene suppression than
sensitive cells?

Prediction: Yes. Drug resistance
selects for deeper false attractor
states — cells that are more
dedifferentiated and therefore
more insensitive to
differentiation-based signals.

This would provide a mechanism
for acquired resistance:
resistance = deeper false attractor.

Data: GSE161533 (BRCA chemo)
      GSE150949 (LUAD EGFR inhibitor)
Doc: 107
```

#### Pediatric vs Adult Same Cancer
```
Compare pediatric GBM vs adult GBM
(already in Neftel dataset —
pediatric samples included).

Question: Same switch gene suppression
in pediatric GBM?

This tests whether the false attractor
is age-invariant.
Doc: 108
```

---

### Session 8 — Synthetic Lethal Tests

#### AML with DNMT3A mutation
```
Subset the AML dataset by mutation
status (DNMT3A, FLT3, NPM1).
Do different mutation backgrounds
show different depths of switch gene
suppression?

This connects mutation → epigenetic
state → false attractor depth.
Doc: 109
```

#### BRCA1/2 mutant vs sporadic BRCA
```
GSE176078 has BRCA1/2 mutation status.
Compare FOXA1/GATA3/ESR1 suppression
in BRCA1-mutant TNBC vs sporadic TNBC.

Prediction: BRCA1-mutant shows deeper
suppression — the germline mutation
predisposes to a deeper false attractor.
Doc: 110
```

---

### The Full Validation Map — Summary

```
Session 1 (complete):
  AML, CRC, GBM, BRCA, LUAD
  5 cancers — 15 switch genes confirmed
  Docs 72-76

Session 2 — Hematopoietic:
  CML, ALL, CLL, Myeloma, MDS
  5 cancers — Docs 77-81

Session 3 — Solid Epithelial:
  PAAD, PRAD, STAD, ESCA, BLCA,
  HCC, ICC, RCC, OV, UCEC
  10 cancers — Docs 82-91

Session 4 — Rare and Aggressive:
  PDAC subtypes, Uveal Melanoma,
  Cutaneous Melanoma, Mesothelioma,
  Thyroid, Neuroblastoma,
  Medulloblastoma
  7 cancers — Docs 92-98

Session 5 — Liquid Tumors:
  DLBCL, Follicular Lymphoma,
  T Cell Lymphoma, Mast Cell Disease
  4 cancers — Docs 99-102

Session 6 — Brain Tumors:
  LGG, Ependymoma, Oligodendroglioma
  3 cancers — Docs 103-105

Session 7 — Cross-Tissue:
  Metastasis vs Primary
  Resistant vs Sensitive
  Pediatric vs Adult
  3 analyses — Docs 106-108

Session 8 — Synthetic Lethal:
  Mutation-stratified AML
  BRCA1/2 vs sporadic BRCA
  2 analyses — Docs 109-110

TOTAL: 39 cancer types / analyses
       Docs 72-110
       All from public data
       All derivable from the
       same principle
       All runnable with the
       same method
```

---

### Critical Tests Embedded in the Map

```
SAME SWITCH GENE IN TWO CANCERS:
  FOXA1: confirmed BRCA — test in BLCA
  FOXA2: confirmed LUAD — test in UCEC
  NKX2-1: partial LUAD — test in thyroid
  PRDM1: predicted ALL/CLL/MM/DLBCL
  GATA3: confirmed BRCA — test in T-ALL
  MITF: predicted melanoma AND mast cell

  If the same gene is confirmed as a
  switch gene in two independent cancers
  from different tissues — that is the
  deepest possible validation.
  The framework is finding the gene
  because the biology demands it,
  not because of chance.

AGGRESSIVENESS GRADIENT:
  LGG (IDH-mutant) vs GBM (IDH-wt)
  Both gliomas. Same switch genes.
  Does suppression depth correlate
  with survival?
  First test of false attractor depth
  as a clinical biomarker.

THE FOLLICULAR LYMPHOMA INVERSION:
  BCL6 ELEVATED in FL predicts a
  case where the false attractor is
  maintained by active repression
  rather than passive suppression.
  Framework stress test.
  If it holds, the principle generalizes
  to repressor-driven blocks.

RESISTANCE = DEEPER ATTRACTOR:
  If chemo-resistant cells show more
  switch gene suppression than sensitive
  cells — that is a mechanistic
  explanation for drug resistance
  and a prediction for how to
  overcome it.
```

---

## The Principle

```
Cancer is a false attractor in the
Waddington epigenetic landscape.
The malignant cells are stuck below
the differentiation threshold —
a ceiling imposed by suppression of
the lineage-specific terminal
differentiation genes (switch genes).

The switch genes are identifiable by
their expression profile: suppressed
in the malignant block population
relative to the normal differentiated
endpoint.

The minimal therapeutic set for
reversion is the switch genes —
not the scaffold genes that mark
lineage identity throughout the
hierarchy, and not the scaffold
oncogenes expressed throughout
the cancer landscape.

The gates are different for each
cancer type because the lineages
are different. The lock is the same.

This is computable.
For any cancer.
From public data.
From one principle.
```

---

## The Scaffold/Switch Distinction

```
SCAFFOLD GENES:
  Mark lineage identity throughout.
  NOT suppressed at the false attractor.
  Examples: CD34 (AML), OLIG2 (GBM),
            MYC (BRCA), NKX2-1 (LUAD)

SWITCH GENES:
  Activated only at terminal completion.
  SUPPRESSED at the false attractor.
  Examples: SPI1/KLF4/IRF8 (AML),
            CDX2 (CRC),
            SOX10/MBP/MOG/PLP1 (GBM),
            FOXA1/GATA3/ESR1 (BRCA),
            FOXA2/SFTPC/SFTPB/SFTPA1 (LUAD)

PLASTICITY MARKERS:
  Confirmed switch genes from prior
  cancers that appear in the false
  attractor of a different lineage.
  Not controls — reporters of
  cross-lineage transcriptional
  plasticity in the false attractor.
  Examples: IRF8 in CRC, SOX10 in BRCA,
            FOXA1/GATA3 in LUAD
```

---

## Framework

```
OrganismCore — False Attractor Framework
First derived: from a theory of tinnitus
First confirmed: February 28, 2026

Document chain:
  Doc 70 — genomic eigenfunction principle
  Doc 71 — Waddington saddle point derived
  Doc 72 — AML confirmed
  Doc 73 — CRC confirmed
  Doc 74 — GBM confirmed
  Doc 75 — BRCA confirmed
  Doc 76 — LUAD confirmed
  Doc 77 — CML [Session 2]
  ...
  Doc 110 — final analysis

Session 1 result:
  AML:  SPI1 p=0, KLF4 p=0, IRF8 p=0
  CRC:  CDX2 p=3.89e-154
  GBM:  PLP1 p=1.27e-280
  BRCA: ESR1 p=0.00e+00
  LUAD: SFTPC p=0.00e+00
        SFTPB p=0.00e+00
        SFTPA1 p=0.00e+00

  Five cancers. One session.
  583,249 cells. Zero gene overlap.
  One principle.

  39 more analyses mapped.
  All from public data.
  All from the same method.
  All from the same principle
  derived from a theory of tinnitus.

  The table is not closed.
  It is just getting started.

Author: Eric Robert Lawson — OrganismCore
```
