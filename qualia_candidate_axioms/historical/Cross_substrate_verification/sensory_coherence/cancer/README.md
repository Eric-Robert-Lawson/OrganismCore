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

## Completed

### AML — Acute Myeloid Leukemia
Data: Zenodo:10013368 (VanGalen-Oetjen)
      van Galen et al. 2019, Cell
      74,583 cells — 10,130 malignant

Result:
  SPI1:  90.5% suppressed at block, p=0.00e+00 ***
  KLF4:  94.7% suppressed at block, p=0.00e+00 ***
  IRF8:  69.5% suppressed at block, p=0.00e+00 ***
  Controls: 4/4 as predicted

Switch genes (minimal control set):
  SPI1 + KLF4 + IRF8

## In Progress

### CRC — Colorectal Cancer
Data: Zenodo:14602110
Predicted switch genes:
  CDX2, HNF4A, KLF5, ATOH1
Predicted controls (elevated):
  MYC, YY1, CTNNB1
Status: Running

## Queued

### GBM — Glioblastoma
### BRCA — Breast Cancer
### LUAD — Lung Adenocarcinoma

## The Principle

Every entry in this table is a test of
the same prediction:

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

Framework: OrganismCore — Document 72
First confirmed: February 28, 2026
