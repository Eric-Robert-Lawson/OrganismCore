SCRIPT 2 TARGETS — LOCKED 2026-03-01

FROM SCRIPT 1 PENDING LIST:
  1. CTNNB1-hi vs CTNNB1-lo KM survival
  2. AFP-high vs AFP-low survival
  3. Refined depth score with metabolic genes
     (CYP3A4, ALDOB, PCK1, G6PC replacing
      or supplementing the TF-based score)
  4. FGFR3 depth analysis + survival
  5. HDAC2 subtype analysis
  6. TCGA-LIHC replication
  7. Drug prediction artifact (HCC)

NEW QUESTIONS FROM SCRIPT 1 DATA:
  8. Does metabolic depth score predict
     OS better than TF-based depth score?
     (CYP3A4/ALDOB/PCK1 r>-0.70 vs
      HNF4A r=-0.46)
  9. EpCAM-positive subtype survival
     (EPCAM r=+0.61 — worst prognosis?)
  10. SOX4 subtype vs other progenitor TFs
      (SOX4 r=+0.59, OS p=5.4e-04)
  11. HDAC2 vs HDAC1 in survival —
      are they independently prognostic?

TCGA-LIHC:
  n≈370 HCC tumours
  Has mutation data (CTNNB1 mutation
  status directly — no expression proxy)
  Has clinical: stage, grade, viral
  Has survival: OS
  Has RNAseq: continuous expression
  Accessible via GDC portal or
  recount3/TCGAbiolinks

DECISIONS NEEDED BEFORE WRITING:
  A. Do we run TCGA-LIHC in Script 2
     or Script 3?
  B. Do we add a second GEO dataset
     (e.g. GSE36376, n=240 HCC) for
     independent replication before TCGA?
  C. Which depth score variant do we
     test: TF-based, metabolic-based,
     or combined?

MY RECOMMENDATION:
  Script 2 = GSE14520 reanalysis only
    - Refined depth (metabolic genes)
    - Subtype KM analysis (CTNNB1, AFP,
      EPCAM, SOX4, MYC strata)
    - Drug prediction artifact
  Script 3 = TCGA-LIHC replication
    - Uses mutation data for CTNNB1
    - Validates refined depth score
    - Full molecular subtype analysis
  Script 4 = GSE36376 independent
    validation (second GEO dataset)

Do you want to proceed with my
recommended structure, or do you
want TCGA in Script 2?
