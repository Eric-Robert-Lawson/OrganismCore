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

## The Cross-Cancer Table

| Cancer | Lineage | Switch Genes | Suppression | p-value |
|--------|---------|--------------|-------------|---------|
| AML | Myeloid | SPI1 | 90.5% | 0.00e+00 |
| | | KLF4 | 94.7% | 0.00e+00 |
| | | IRF8 | 69.5% | 0.00e+00 |
| CRC | Epithelial | CDX2 | 79.5% | 3.89e-154 |
| GBM | Oligodendrocyte | SOX10 | 88.6% | 5.50e-188 |
| | | MBP | 89.6% | 1.97e-143 |
| | | MOG | 56.9% | 2.97e-91 |
| | | PLP1 | 83.4% | 1.27e-280 |
| BRCA | Luminal | pending | — | — |
| LUAD | Alveolar | pending | — | — |

**Zero gene overlap across all confirmed switch gene sets.**
**Same principle. Different molecular language. Three cancers deep.**

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
  MYC   ↑ (oncogene — correct)
  CD34  ↑ (stem marker — correct)
  GATA1 ~ (wrong lineage — correct)
  MPO   ↑ (GMP marker — correct)

Scaffold gene distinction first observed:
  CD34 present throughout hierarchy —
  not suppressed at block (correct)

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
  Interpretation: lineage infidelity —
  dedifferentiated epithelial cells
  express partial myeloid character.
  First observation of this pattern.

Revised therapeutic target:
  CRISPRa CDX2 + CRISPRi IRF8

Note: 477-gene panel only.
  HNF4A, KLF5, ATOH1, MYC, YY1
  not present in panel.
  CDX2 confirmed from available genes.

Document: CRC/crc_false_attractor_confirmed.md
```

### GBM — Glioblastoma
```
Data:    GSE131928 — Neftel et al. 2019, Cell
         PMID: 31327527
         Smart-seq2: GSM3828672
         23,686 genes x 7,930 cells
         28 IDH-wildtype GBM patients
         Full transcriptome TPM
Block:   OPC-like (PDGFRA+ SOX2+ EGFR+ NES+)
         vs Normal oligodendrocytes
         (MBP+ MOG+ PLP1+ SOX10+)
         1,334 cells each (top 20% scoring)
Lineage: Oligodendrocyte/Neural

Switch genes confirmed (terminal myelination):
  SOX10: 88.6% suppressed  p=5.50e-188 ***
  MBP:   89.6% suppressed  p=1.97e-143 ***
  MOG:   56.9% suppressed  p=2.97e-91  ***
  PLP1:  83.4% suppressed  p=1.27e-280 ***
  (PLP1 is the strongest single p-value
  in the cross-cancer analysis to date)

Scaffold gene confirmed:
  OLIG2: +21.5% elevated in OPC-like
  Interpretation: OLIG2 is a lineage
  identity gene active throughout the
  oligodendrocyte hierarchy — not a
  terminal switch gene. Its elevation
  confirms OPC-like cells are genuinely
  in the oligodendrocyte lineage but
  cannot complete it.

Elevated predictions — all correct (4/4):
  PDGFRA:  +83.1%  (OPC driver)
  SOX2:    +55.7%  (GBM stem)
  EGFR:   +252.2%  (GBM oncogene)
  NES:    +132.3%  (neural progenitor)

Lineage infidelity pattern confirmed:
  SPI1, IRF8 appear in normal
  oligodendrocytes in GBM tumor
  microenvironment — same pattern
  as IRF8 in CRC. Myeloid TFs
  report on microenvironmental immune
  state, not cell lineage identity.

Minimal control set:
  CRISPRa SOX10 + MBP + PLP1

Document: GBM/gbm_false_attractor_confirmed.md
```

---

## In Progress

### BRCA — Breast Cancer
```
Lineage: Luminal epithelial
Block:   Basal/stem-like or TNBC
         dedifferentiated cells
         vs mature luminal cells
         (ER+ PR+ FOXA1+ GATA3+)

Predicted switch genes
(terminal luminal differentiation):
  FOXA1  — luminal pioneer TF
  GATA3  — luminal identity master TF
  ESR1   — estrogen receptor
           (luminal completion gene)

Predicted elevated (false attractor
drivers):
  SOX2   — stem/dedifferentiation
           (confirmed elevated in GBM)
  MYC    — proliferation driver
  EGFR   — confirmed elevated in GBM

Controls (confirmed switch genes from
prior cancers — myelination genes now
primary controls for solid tumors):
  SOX10  — confirmed GBM: 88.6%
  MBP    — confirmed GBM: 89.6%
  PLP1   — confirmed GBM: 83.4%
  CDX2   — confirmed CRC: 79.5%

Data target: GSE176078
  Wu et al. 2021
  ~100,000 cells, well annotated,
  includes normal breast epithelium
  and multiple tumor subtypes

Status: Queued
```

---

## Queued

### LUAD — Lung Adenocarcinoma
```
Lineage: Alveolar type II epithelial
Predicted switch genes:
  NKX2-1 — lung identity master TF
  FOXA2  — alveolar differentiation
Controls will include:
  FOXA1, GATA3   (confirmed BRCA)
  SOX10, MBP     (confirmed GBM)
  CDX2           (confirmed CRC)
  SPI1, KLF4     (confirmed AML)
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
the lineage-specific terminal
differentiation genes (switch genes).

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

---

## The Scaffold/Switch Distinction
### Framework refinement — Document 74

```
SCAFFOLD GENES:
  Active throughout the differentiation
  hierarchy from progenitor to terminal.
  Mark lineage identity at every stage.
  NOT suppressed at the false attractor.
  May be elevated in blocked cells.

  Examples:
    AML:  CD34 (hematopoietic stem marker)
    GBM:  OLIG2, OLIG1 (OPC lineage)

SWITCH GENES:
  Activated only at terminal
  differentiation completion.
  Mark the crossing of the
  differentiation threshold.
  SUPPRESSED at the false attractor.

  Examples:
    AML:  SPI1, KLF4, IRF8
          (monocyte terminal markers)
    CRC:  CDX2
          (colonocyte identity gate)
    GBM:  SOX10, MBP, MOG, PLP1
          (myelination completion)

THE REFINED PREDICTION RULE:
  For any cancer type, identify the
  genes activated specifically at
  TERMINAL differentiation completion
  — not the genes marking lineage
  identity throughout the hierarchy.
  Those terminal genes will be
  suppressed at the false attractor.
```

---

## The Internal Validation Logic

```
The strongest validation is zero gene
overlap between confirmed switch gene
sets across cancer types:

AML:  SPI1, KLF4, IRF8
      myeloid terminal TFs
      → used as controls in CRC ✓
      → appeared in GBM microenvironment
        (lineage infidelity signal)

CRC:  CDX2
      colonocyte master TF
      → absent from brain (CDX2 ~ 0)
      → will be control in BRCA ✓

GBM:  SOX10, MBP, MOG, PLP1
      myelination completion genes
      → absent from breast/lung tissue
      → primary controls for BRCA/LUAD

BRCA: FOXA1, GATA3, ESR1 [predicted]
      → will become controls for LUAD

Each confirmed cancer becomes a
control layer for all future cancers.
The table is self-validating as it
grows. The more rows confirmed, the
harder it is to dismiss as coincidence.
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
  Doc 75 — BRCA [in progress]
  Doc 76 — LUAD [queued]

The chain:
  Why does experience feel like
  anything at all?
    ↓ coherence
    ↓ eigenfunction spaces
    ↓ false attractors
    ↓ tinnitus
    ↓ cancer
  AML:  SPI1 p=0, KLF4 p=0, IRF8 p=0
  CRC:  CDX2 p=3.89e-154
  GBM:  PLP1 p=1.27e-280
    ↓
  BRCA next.

Author: Eric Robert Lawson — OrganismCore
```
