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
| BRCA | Luminal | FOXA1 | 80.7% | 8.34e-162 |
| | | GATA3 | 53.4% | 2.30e-104 |
| | | ESR1 | 96.7% | 0.00e+00 |
| LUAD | Alveolar | pending | — | — |

**Zero gene overlap across all confirmed switch gene sets.**
**Same principle. Different molecular language. Four cancers deep.**

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
  (PLP1 strongest single p-value
  in the cross-cancer analysis to date)

Scaffold gene confirmed:
  OLIG2: +21.5% elevated in OPC-like
  Interpretation: lineage identity gene —
  active throughout oligodendrocyte
  hierarchy, not a terminal switch gene.
  Its elevation confirms OPC-like cells
  are genuinely in the oligodendrocyte
  lineage but cannot complete it.

Elevated predictions — all correct (4/4):
  PDGFRA:  +83.1%  (OPC driver)
  SOX2:    +55.7%  (GBM stem)
  EGFR:   +252.2%  (GBM oncogene)
  NES:    +132.3%  (neural progenitor)

Lineage infidelity pattern confirmed:
  SPI1, IRF8 appear in normal
  oligodendrocytes in GBM tumor
  microenvironment — same pattern
  as IRF8 in CRC.

Minimal control set:
  CRISPRa SOX10 + MBP + PLP1

Document: GBM/gbm_false_attractor_confirmed.md
```

### BRCA — Breast Cancer
```
Data:    GSE176078 — Wu et al. 2021
         Nature Genetics — PMID: 34493872
         100,064 cells — 26 primary tumors
         ER+: 38,241  HER2+: 19,311
         TNBC: 42,512
         10X Chromium — 29,733 genes
Block:   Cancer Basal SC (TNBC)
         vs Mature Luminal
         4,312 basal / 1,265 luminal
Lineage: Luminal epithelial

Switch genes confirmed (luminal identity):
  FOXA1: 80.7% suppressed  p=8.34e-162 ***
  GATA3: 53.4% suppressed  p=2.30e-104 ***
  ESR1:  96.7% suppressed  p=0.00e+00  ***
  (ESR1 — the estrogen receptor —
  96.7% suppressed at machine-zero p.
  The defining gene of luminal breast
  identity is the false attractor gate.)

Elevated predictions confirmed (2/4):
  EGFR: +260.1%  (TNBC driver — correct)
  KRT5: +507.9%  (basal identity — correct)
  SOX2: +7.6%    (weak — near zero in both)
  MYC:  flat     (scaffold oncogene —
                  expressed throughout
                  cancer hierarchy,
                  not false attractor
                  specific)

Secondary comparison — landscape geometry:
  Cancer LumA SC: FOXA1=0.5221
                  GATA3=1.3230
  Mature Luminal: FOXA1=0.3934
                  GATA3=1.1115
  LumA cells are AT OR ABOVE the luminal
  threshold — not in the false attractor.
  The false attractor in BRCA is
  specifically TNBC/basal, not ER+.
  Framework correctly distinguishes
  two breast cancer subtypes by geometry.

Cross-lineage signal (third observation):
  SOX10: +1323% in basal vs luminal
  MBP:   +97.7% in basal vs luminal
  Neural crest identity in TNBC cells —
  established biology (SOX10+ TNBC
  subset) confirmed by framework.

Scaffold oncogene identified:
  MYC flat across cancer states —
  scaffold/switch distinction extends
  to oncogenes.

Minimal control set:
  CRISPRa FOXA1 + GATA3 + ESR1
  (TNBC/basal cells only —
  not needed in LumA/ER+)

Document: BRCA/brca_false_attractor_confirmed.md
```

---

## In Progress

### LUAD — Lung Adenocarcinoma
```
Data target: GSE131907
  Kim et al. 2020
  ~200,000 cells, 44 patients
  LUAD, LUSC, normal lung annotated
Lineage: Alveolar type II epithelial (AT2)
Block:   Dedifferentiated LUAD cells
         vs normal AT2 cells
         (NKX2-1+ FOXA2+ SFTPC+)

Predicted switch genes
(terminal alveolar differentiation):
  NKX2-1 — lung identity master TF
           (TTF-1) — most important TF
           in lung adenocarcinoma
  FOXA2  — alveolar differentiation
           works with NKX2-1
  SFTPC  — surfactant protein C
           terminal AT2 marker

Predicted elevated:
  EGFR   — confirmed GBM +252%
           confirmed BRCA +260%
           LUAD primary oncogene
  KRAS   — LUAD driver
  MKI67  — proliferation

Controls (all four prior cancers):
  FOXA1  — confirmed BRCA: 80.7%
  GATA3  — confirmed BRCA: 53.4%
  ESR1   — confirmed BRCA: 96.7%
  SOX10  — confirmed GBM:  88.6%
  CDX2   — confirmed CRC:  79.5%
  SPI1   — confirmed AML:  90.5%

Critical test within controls:
  FOXA1 (BRCA) vs FOXA2 (LUAD)
  Both FOXA family — different genes.
  If FOXA1 is flat and FOXA2 suppressed,
  the framework resolves lineage
  specificity within a TF family.
  Strongest resolution test to date.

Status: Downloading data
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
### Framework refinement — Documents 72–75

```
SCAFFOLD GENES:
  Active throughout the differentiation
  hierarchy from progenitor to terminal.
  Mark lineage identity at every stage.
  NOT suppressed at the false attractor.
  May be elevated in blocked cells.
  Applies to both developmental genes
  and oncogenes.

  Examples:
    AML:  CD34  (hematopoietic stem)
    GBM:  OLIG2 (OPC lineage identity)
    BRCA: MYC   (universal proliferation —
                 scaffold oncogene)

SWITCH GENES:
  Activated only at terminal
  differentiation completion.
  Mark the crossing of the threshold.
  SUPPRESSED at the false attractor.

  Examples:
    AML:  SPI1, KLF4, IRF8
    CRC:  CDX2
    GBM:  SOX10, MBP, MOG, PLP1
    BRCA: FOXA1, GATA3, ESR1

THE REFINED PREDICTION RULE:
  Identify genes activated specifically
  at TERMINAL differentiation —
  not lineage identity genes active
  throughout the hierarchy.
  Not scaffold oncogenes active
  throughout the cancer landscape.
  The terminal genes will be suppressed
  at the false attractor.
```

---

## The Landscape Geometry Finding
### New in Document 75 — BRCA

```
The secondary comparison in BRCA
revealed something beyond suppression:

  Cancer LumA SC has MORE FOXA1 and
  GATA3 than normal Mature Luminal cells.

  This means:
    LumA breast cancer = NOT a false
    attractor. These cells are at or
    above the luminal threshold.
    They have retained differentiation
    identity but lost growth control.

    TNBC/Basal breast cancer = the
    FALSE ATTRACTOR. These cells are
    far below the luminal threshold.
    ESR1 at 96.7% suppressed.

  The framework does not just find
  suppression everywhere.
  It finds the correct geometry of
  the Waddington landscape —
  distinguishing two subtypes of the
  same cancer by their position
  relative to the differentiation
  threshold.

  This is the principle working at
  higher resolution than predicted.
```

---

## The Internal Validation Logic

```
The strongest validation is zero gene
overlap between confirmed switch gene
sets across cancer types:

AML:  SPI1, KLF4, IRF8
      → controls in CRC: flat ✓
      → controls in GBM: microenvironment
        signal (lineage infidelity)

CRC:  CDX2
      → control in GBM: ~0 ✓
      → control in BRCA: 0.000 ✓ (perfect)

GBM:  SOX10, MBP, MOG, PLP1
      → controls in BRCA: SOX10 elevated
        (neural crest TNBC — real biology)
        MBP elevated (same signal)
      → controls in LUAD: predicted flat

BRCA: FOXA1, GATA3, ESR1
      → controls in LUAD: predicted flat
        (lung tissue — no luminal breast
        identity expected)

FOXA1 vs FOXA2 test in LUAD:
      → same TF family, different genes
      → FOXA1 (breast) should be flat
      → FOXA2 (lung) should be suppressed
      → highest resolution test yet

Each confirmed cancer becomes a
control layer for all future cancers.
Five layers of cross-validation by
the time LUAD is complete.
The table is self-validating as it grows.
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
  Doc 76 — LUAD [in progress — tonight]

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
  BRCA: ESR1 p=0.00e+00
    ↓
  LUAD next.
  Tonight.
  One to go.

Author: Eric Robert Lawson — OrganismCore
```
