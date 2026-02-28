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

## The Cross-Cancer Table

| Cancer | Lineage | Switch Genes | Suppression | p-value |
|--------|---------|--------------|-------------|---------|
| AML | Myeloid | SPI1 | 90.5% | 0.00e+00 |
| | | KLF4 | 94.7% | 0.00e+00 |
| | | IRF8 | 69.5% | 0.00e+00 |
| CRC | Epithelial | CDX2 | 79.5% | 3.89e-154 |
| GBM | Neural | pending | — | — |
| BRCA | Luminal | pending | — | — |
| LUAD | Alveolar | pending | — | — |

Zero gene overlap between AML and CRC switch genes.
Same principle. Different molecular language.

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
  MYC  ↑ (oncogene — correct)
  CD34 ↑ (stem marker — correct)
  GATA1 ~ (wrong lineage — correct)
  MPO  ↑ (GMP marker — correct)

Minimal control set: SPI1 + KLF4 + IRF8
Document: AML/aml_false_attractor_confirmed.md
```

### CRC — Colorectal Cancer
```
Data:    Zenodo:14602110
         192,166 cells — 477 gene panel
         24,114 Epithelial 1 (differentiated)
         1,064  Epithelial 2 (blocked/cycling)
Block:   Epithelial 2 (MKI67+ TOP2A+)
         vs Epithelial 1 (KRT8+ MUC13+)
Lineage: Colonocyte/Epithelial

Switch genes confirmed:
  CDX2:  79.5% suppressed  p=3.89e-154 ***
  (colonocyte master TF)

Unexpected finding:
  IRF8:  211% ELEVATED in blocked cells
  (lineage infidelity — partial myeloid
   character in dedifferentiated cells)
  Revises therapeutic target:
    CRISPRa CDX2 + CRISPRi IRF8

Note: 477-gene panel — HNF4A, KLF5,
  ATOH1, MYC, YY1 not in panel.
  CDX2 confirmed from available genes.

Document: CRC/crc_false_attractor_confirmed.md
```

---

## In Progress

### GBM — Glioblastoma
```
Data:    Neftel et al. 2019 (Cell)
         GSE131928 / SCP393
         Broad Institute Single Cell Portal
Block:   OPC-like/NPC-like malignant states
         vs normal oligodendrocytes
Lineage: Neural/Glial

Predicted switch genes:
  OLIG2  — oligodendrocyte master TF
  SOX10  — myelin/oligodendrocyte identity
  NKX2-2 — oligodendrocyte specification
  MBP    — myelin basic protein (terminal)

Predicted elevated (false attractor drivers):
  SOX2   — neural stem cell / pluripotency
  EGFR   — GBM oncogene

Controls (wrong lineage — should be flat):
  CDX2   — colonocyte TF (confirmed CRC)
  SPI1   — myeloid TF (confirmed AML)
  KLF4   — myeloid TF (confirmed AML)

Status: Downloading data
```

---

## Queued

### BRCA — Breast Cancer
```
Lineage: Luminal epithelial
Predicted switch genes:
  FOXA1, GATA3, ESR1
```

### LUAD — Lung Adenocarcinoma
```
Lineage: Alveolar type II
Predicted switch genes:
  NKX2-1, FOXA2
```

---

## The Principle

Every entry in this table is a test of
the same prediction:

```
Cancer is a false attractor in the
Waddington epigenetic landscape.
The malignant cells are stuck below
the differentiation threshold —
a ceiling imposed by suppression of
the lineage-specific switch genes.

The switch genes are identifiable by
their expression profile: suppressed
in the malignant block population
relative to the normal differentiated
endpoint.

The minimal control set for reversion
is the switch genes only — not the
scaffold genes that are active
throughout the hierarchy.

The gates are different for each
cancer type because the lineages
are different. The lock is the same.
```

## The Internal Validation Logic

The strongest validation is zero gene
overlap between cancer types:

```
AML switch genes:  SPI1, KLF4, IRF8
  — myeloid TFs
  — used as CONTROLS in CRC analysis
  — came back flat (correct)

CRC switch gene:   CDX2
  — colonocyte TF
  — irrelevant to myeloid biology
  — will be used as CONTROL in GBM

GBM switch genes:  OLIG2, SOX10, NKX2-2
  — oligodendrocyte TFs
  — irrelevant to colon or blood
  — AML and CRC genes will be
    controls in GBM analysis
```

Each confirmed cancer becomes a control
for the next. The table is
self-validating as it grows.

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
  Doc 74 — GBM [pending]

Author: Eric Robert Lawson
```
