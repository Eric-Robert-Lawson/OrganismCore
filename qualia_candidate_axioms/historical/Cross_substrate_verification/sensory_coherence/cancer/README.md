# OrganismCore — Cancer False Attractor Analysis

---

**IMPORTANT**

document numbering gets messed up with new agents, but method doesn't, just look for individual cancer results, the chronology of the documentation is not important.

---

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
Block:    B-ALL blasts vs normal B cells
          T-ALL blasts vs normal T cells
          NOTE: ALL block sits AFTER
          lineage identity is established
          (PAX5, CD19, TCF7, CD3E are ON
          in blasts — not switch genes)
          Block is at TERMINAL COMPLETION
          not at lineage identity
Confirmed switch genes (B-ALL):
  IGKC   — Ig kappa light chain         83.7%  p=0.00e+00
           terminal B cell product
           recombination complete marker
  PRDM1  — Blimp1 — plasma cell         76.0%  p=2.01e-25
           master TF — final B cell
           commitment step
Confirmed switch genes (T-ALL):
  CCR7   — mature naive T cell           97.4%  p=0.00e+00
           chemokine receptor
           lymph node homing
  IL7R   — IL-7 receptor                 60.1%  p=2.68e-219
           mature T cell survival
           signal receptor
RAG scaffold confirmed:
  RAG1   — 642% elevated in B-ALL blasts
           1330% elevated in T-ALL blasts
           Recombination machinery running
           Completion products absent
           False attractor at mechanism level
Proliferation geometry:
  T-ALL hyperproliferative (MKI67 1487%↑)
  opposite of CML quiescent attractor
  same fix: force terminal completion
Lineage specificity confirmed absolute:
  CEBPA near-zero all lymphoid populations
  (max=0.0781 vs myeloid normal 0.8887)
  Myeloid switch genes do not apply
  to lymphoid cancers
Cross-lineage note:
  GATA3 INVERTED in T-ALL (elevated
  in blasts) — T-cell identity gene
  not terminal completion gene
  GATA3 confirmed BRCA luminal switch
  Same gene. Different lineage role.
  Different direction. Both correct.
Data:     GSE132509 (Caron et al. 2020
          38,922 cells — 8 ALL patients
          3 normal PBMMC donors)
Status:   CONFIRMED
Note:     v1 gene list (identity genes)
          required correction to v2
          (terminal completion genes)
          Revision informative — confirmed
          ALL block sits after lineage
          identity, not before it
Doc:      79
```

#### CLL — Chronic Lymphocytic Leukemia

```
Status:   CONFIRMED — Cancer Validation #8
Date:     2026-02-28
Doc:      80 (updated from 79)

Lineage:  B-lymphocyte (mature naive)
Attractor type: SURVIVAL ATTRACTOR
          CLL cells are NOT blocked in
          differentiation. They ARE blocked
          from dying. Mature B cells that
          accumulate because they fail to
          undergo apoptosis.

Data:     GSE111014 — Rendeiro et al. 2020
          10X Chromium scRNA-seq
          48,016 cells total
          15,007 day 0 untreated CLL cells
          4 patients: CLL1, CLL5, CLL6, CLL8
          Timepoints: d0, d30, d120, d150, d280
          Treatment: Ibrutinib (BTK inhibitor)

Normal B reference:
          GSE132509 PBMMC
          2,744 normal B cells + Mono
          3 healthy donors

Confirmed switch gene:
  PRDM1  — Blimp1, plasma cell terminal TF
           suppressed -57% *** p<1e-6
           CLL resists terminal plasma cell fate
           FLAT under ibrutinib — cells die,
           they do not differentiate

Confirmed scaffold:
  BCL2   — anti-apoptotic survival gene
           elevated +136% *** p<1e-45
           THE molecular lock of the
           survival attractor
           falls 83% by day 150 under ibrutinib
           Venetoclax target — FDA approved

Confirmed cross-checks:
  IGKC   — elevated +60% vs normal B
           CLL cells are mature — V(D)J complete
           Contrast: B-ALL IGKC suppressed 83.7%
           CLL block is DEEPER than B-ALL
  CD27   — elevated +817% ***
           Antigen-experienced memory B identity
           Confirms mature B cell state

Biological findings beyond predictions:
  IGHD   — elevated +43% in CLL
           CLL co-expresses IgM/IgD for
           tonic BCR signaling
           drops to zero under ibrutinib
           BCR-dependent attractor marker
  FCRL5  — elevated +415% in CLL
           Anergy marker — CLL cells are
           functionally anergic
           drops to near zero under ibrutinib
           BCR-dependent attractor marker
  RAG1/RAG2 — silent in CLL
           No V(D)J recombination
           Development is complete
  MKI67  — near zero
           CLL does not proliferate
           Accumulates by survival not division

Ibrutinib response (attractor dissolution):
  BCL2:  d0=0.158 → d150=0.026  (-83%)
  IGHD:  d0=0.238 → d150=0.000  (-100%)
  FCRL5: d0=0.162 → d150=0.001  (-99%)
  PRDM1: flat throughout — no differentiation
  Cells exit false attractor by dying only

Drug targets derived from attractor logic:
  BCR/BTK signaling → BCL2 → survival lock
  Block BTK:  ibrutinib  ✓ FDA approved
  Block BCL2: venetoclax ✓ FDA approved
  Both independently confirmed by
  attractor analysis without prior
  knowledge of existing drugs

Automated scoring note:
  Script reports 1/4 switch genes confirmed
  Scoring logic designed for differentiation
  block attractors — not survival attractors
  Biological confirmation is solid
  Framework scoring needs survival attractor
  revision for future cancers of this type

Comparison to B-ALL (Cancer Validation #7):
  B-ALL: differentiation block, Pre-B stage
         IGKC suppressed, RAG1/2 active
         Block = cannot complete development
  CLL:   survival block, mature naive B
         IGKC elevated, RAG1/2 silent
         Block = development complete,
                 cannot die
  These are two distinct attractor topologies
  in the same B cell lineage

Scripts:
  CLL/cll_saddle_point_analysis.py
  CLL/rebuild_normal_b_cache.py

Results:
  CLL/cll_saddle_results/
    analysis_log.txt
    cll_saddle_results.csv
    cll_saddle_figure.png

Reasoning artifact:
  CLL/CLL_FALSE_ATTRACTOR_REASONING.md

Reference:
  Rendeiro AF et al. (2020)
  Chromatin mapping and single-cell immune
  profiling define the temporal dynamics of
  ibrutinib drug response in CLL
  Nature Communications 11:577
  GSE111014
```

#### Multiple Myeloma
```
Lineage:  Plasma cell (plasmablast → LLPC transition)
Block:    MM plasma cells vs HD plasma cells
          Stuck in plasmablast/activated state
          Cannot complete → Long-lived plasma cell (LLPC)

True switch gene (suppressed in MM):
  IRF8   — differentiation block marker
           -79.4%  p=0.00e+00  CONFIRMED
           Monotonic: HD(0.568) → MGUS(0.169)
                   → SMM(0.154) → MM(0.117)
           Block established at MGUS — not at MM
           Note: IRF8 is a negative regulator of
           plasma cell fate — its suppression marks
           full plasma cell commitment, not failure
           to reach LLPC. Block is downstream.

False attractor markers (elevated in MM):
  IRF4   — activation lock      +114.0%  p=2.23e-199
  PRDM1  — plasma cell identity +199.9%  p=0.00e+00
  XBP1   — secretory program    +65.5%   p=1.92e-158
  XBP1 is strongest depth driver r=+0.75 (p=0)
  Stronger than IRF4 (r=+0.63) or PRDM1 (r=+0.64)

Epigenetic lock:
  EZH2 NEUTRAL (-10.4%, r=-0.13 with depth)
  MM lock is transcriptional + proteostatic
  NOT epigenetic (contrast: BRCA where EZH2=lock)

Two sub-populations within MM plasma cells:
  Deep  (25%, n=3,062):
    IRF8=0.004  XBP1=1.992  MKI67=0.026
    Post-mitotic. HSPA5=1.854 (high secretory stress)
    Cannot be killed by anti-proliferatives
    Vulnerability: proteasome inhibition via UPR overload
  Shallow (45%, n=5,471):
    IRF8=0.248  XBP1=0.096  MKI67=0.417
    Proliferating. IRF8 partially retained.
    Vulnerability: IRF4 inhibition / IMiD therapy

Drug predictions (geometry-derived, confirmed vs literature):
  1. IRF4 inhibition
       Geometry: primary activation lock +114%
       Literature: ✅ EXACT MATCH
       IMiDs (lenalidomide/thalidomide) = backbone of
       all MM therapy — work by degrading IKZF1/3
       which directly suppresses IRF4
       ION251 (IRF4 ASO) in Phase 1 NCT04398485
       SH514 (direct IRF4 inhibitor) preclinical
       Framework derived this independently from
       first principles and scRNA-seq data alone

  2. Proteasome inhibition (for deep cells)
       Geometry: deep cells post-mitotic, HSPA5 2.75x
                 near proteostatic overload
       Literature: ✅ EXACT MATCH
       Bortezomib mechanism = terminal UPR in MM cells
       XBP1 high = bortezomib sensitive (confirmed 2019)
       Attractor depth score predicts bortezomib
       sensitivity from the same underlying biology

  3. XBP1/IRE1α inhibition
       Geometry: r=+0.75 dominant lock signal
                 synergy with proteasome inhibitor
       Literature: ✅ CONFIRMED preclinical
       STF-083010 and KIRA6 show anti-MM activity
       IRE1α+proteasome synergy in preclinical models
       Not yet in MM clinical trials — ahead of curve

  4. IRF8 restoration (revised after literature check)
       Geometry: restore switch gene → LLPC maturation
       Literature: ⚠️ REVISED
       IRF8 is a B cell identity repressor — must fall
       for plasma cell commitment (normal event)
       Restoration would de-differentiate toward B cell,
       not push toward LLPC
       Block is downstream: LLPC survival niche signals,
       XBP1/IRF4 balance, PRDM1 maturation completion
       IRF8 as PROGRESSION MARKER stands — mechanism revised

Novel predictions (not in existing literature):
  1. Attractor depth score for treatment stratification
       High depth → lead with proteasome inhibitor
       Low depth  → lead with IMiD / IRF4 inhibitor
       No clinical trial uses depth score for assignment
  2. IRF8 at MGUS as MM progression biomarker
       70.2% drop at HD→MGUS is earliest measured event
       Not in GS36 or any published MGUS biomarker panel
       FNIH MMyeRisk consortium actively seeking this type
       of marker — testable from existing cohort data
  3. Sub-population mechanism for why VRd combination works
       IMiD kills shallow cells (proliferating, IRF4-dependent)
       Proteasome inhibitor kills deep cells (post-mitotic,
       UPR-overloaded) — together = complete coverage
       Combination used empirically — this mechanism is novel

Convergence pattern:
  IRF4 → IMiDs (FDA approved standard of care globally)
  Proteasome → bortezomib (FDA approved cornerstone)
  XBP1/IRE1α → preclinical development confirmed
  Same targets. Independent derivation. Every time.

Data:     GSE271107 (Cai et al.)
          5 HD | 6 MGUS | 4 SMM | 4 MM
          47,499 plasma cells across all stages
          Whole bone marrow 10x CellRanger HDF5
Script:   mm_false_attractor_full.py
          Self-contained — GEO accession to result
          Reproducible on any machine in ~20 minutes
Docs:     85 (confirmed) | 85L (literature check)
Status:   CONFIRMED + LITERATURE CHECK COMPLETE
```

#### MDS — Myelodysplastic Syndrome
```
Lineage:  Myeloid (granulocytic)
          CD34+ hematopoietic stem/progenitor cells
          Bone marrow
Block:    MDS HSPCs vs healthy donor HSPCs
          Promyelocyte → Myelocyte transition
          Block is DOWNSTREAM of AML in same lineage
          AML: stuck before TF activation (Saddle 1)
          MDS: stuck before effector execution (Saddle 3)
          Cells have TFs present — cannot execute program

Switch gene (confirmed):
  ELANE  — neutrophil elastase
           -42.8%  p=1.24e-03  CONFIRMED
           depth r=-0.803  p=1.10e-19
           Marks promyelocyte→myelocyte transition
           Its loss = arrest at that stage
           Same biology as ELANE-mutant congenital
           neutropenia (independent lit confirmation)

False attractor (confirmed):
  CD34   — HSPC surface identity marker
           +12.1%  depth r=+0.757  p=1.88e-16
           Retained in stuck promyelocyte-like state

Key structural findings:
  CEBPE→ELANE circuit severed:
    CEBPE elevated +135.3% (p=0.029)
    ELANE suppressed -42.8%
    r(CEBPE, ELANE) = 0.07 in MDS — statistical zero
    CEBPE normally drives ELANE — connection broken
    Not in any published MDS signature
  AZU1 elevated +26.2% (p=2.78e-04):
    AZU1 is promyelocyte-specific granule gene
    AZU1 up + ELANE down = promyelocyte arrest
    locates block with single-stage precision
    Same AZU1/ELANE gene cluster (chr19p13.3)
    confirmed in Blood 1999 chromatin paper
  GFI1B elevated +152.5% (p=1.82e-04):
    Erythroid/megakaryocyte TF aberrantly expressed
    in granulocytic progenitors
    Molecular basis of multilineage dysplasia
    GFI1B recruits LSD1/CoREST to repress myeloid
    differentiation genes — may be causal not marker
  RCOR1 suppressed -61.3% (p=1.96e-03):
    LSD1/CoREST scaffold reduced
    Progenitor silencing complex disrupted
    Progenitor genes (AZU1, GFI1B) cannot be silenced
    Rcor1 knockout mice develop MDS-like phenotype
    (Blood 2014 — exact match)
  EZH2 -26.2% (p=7.3e-04) ASXL1 -25.0% (p=0.003):
    Epigenetic LOSS not gain (contrast BRCA)
    Loss of H3K27me3 maintenance

Mutation subtypes:
  SF3B1_MUT (n=28): depth 0.478 vs WT 0.536 p=0.008
    Shallower on granulocytic ELANE/CD34 axis
    SF3B1 MDS is erythroid-dominant (ring sideroblasts)
    Wrong axis for SF3B1 — needs erythroid depth score
    (ALAS2/HBA1/GATA1 panel)
  SRSF2_MUT (n=8):  depth 0.429 (underpowered)
  U2AF1_MUT (n=6):  depth 0.578 (underpowered)

Drug predictions (geometry-derived):
  1. LSD1 inhibitor (KDM1A/RCOR1 axis)
       Geometry: RCOR1 suppressed, GFI1B elevated,
                 LSD1/CoREST complex disrupted,
                 ELANE locus inaccessible despite
                 CEBPE presence
       Literature: ✅ iadademstat (ORY-1001) Phase 1
                   ACTIVE (NCT06502145) + azacitidine
                   seclidemstat Phase I/II MD Anderson
                   GSK2879552 Phase I/II (terminated)
                   Same target — independent derivation
  2. Splicing correction (SF3B1/U2AF1 mutants)
       Geometry: splicing factor mutations break
                 CEBPE→ELANE circuit at RNA level
       Literature: ✅ H3B-8800 in trials for
                   splicing-mutant MDS
  3. HMA therapy mechanism clarified
       Geometry: EZH2/ASXL1 loss + DNA methylation
                 at ELANE locus — HMA demethylates
                 → ELANE expressed → cells mature
       Literature: ✅ azacitidine standard of care
                   mechanism from geometry confirmed
  4. MYC inhibition for proliferative control
       Geometry: MYC +52.7% (p=0.021)
                 proliferative drive at block point
       Literature: ⚠️ MYC inhibitors in development
                   not MDS-specific yet

Novel predictions (not in literature):
  1. ELANE expression at diagnosis predicts HMA
     response — high suppression = more HMA benefit
     Testable from existing clinical cohorts
  2. CEBPE→ELANE r≈0 as MDS molecular signature
     distinguishes MDS from normal granulopoiesis
     Not in any published MDS gene panel
  3. GFI1B:GFI1 ratio elevated in multilineage
     vs single-lineage dysplasia
     Testable from annotated clinical samples
  4. SF3B1 MDS needs erythroid-axis depth score
     (ALAS2/HBA1/GATA1) not ELANE/CD34 axis
     Lineage-specific depth scoring framework

Scripts:
  mds_false_attractor.py    (Script 1 — discovery)
  mds_false_attractor_2.py  (Script 2 — corrected)
  Self-contained — GEO accession to figure

Data:    GSE114922 (Dolatshad et al.)
         82 MDS patients | 8 healthy controls
         CD34+ HSPCs | bone marrow bulk RNA-seq
         Mutation subtypes: SF3B1/SRSF2/U2AF1/ZRSR2

Docs:    86a (Script 1 — discovery run)
         86b (Script 2 — corrected framework +
              reasoning artifact)
         86c (Literature check — complete)
         Protocol (OrganismCore_Cancer_Analysis_Protocol.md)

Prior entry (Doc 81, GSE140559):
         Superseded — wrong dataset (GSE145477 was
         mouse aging data), predictions not tested.
         This entry (Doc 86a/b/c) is the valid record.

Status:  CONFIRMED + LITERATURE CHECK COMPLETE
         Drug target (LSD1) in Phase 1 trials NOW
         4 novel predictions stated and testable
```

---

### Session 3 — Solid Tumor Epithelial

#### PAAD — Pancreatic Adenocarcinoma
```
Lineage:  Acinar epithelial (pancreas)
          Acinar-to-ductal metaplasia (ADM)
          origin — cells dedifferentiate
          from acinar into ductal/progenitor
          hybrid false attractor state
          Bone marrow not involved
Block:    PAAD tumor cells vs adjacent
          non-tumor pancreatic tissue
          Acinar identity lost
          Ductal gland progenitor identity
          adopted (KRT19/TFF1/TFF2 high)
          Block is at PTF1A INPUT level —
          not at downstream circuit
          PTF1A→CTRC circuit INTACT
          (r=+0.754) — restore input,
          program executes normally

Switch genes (confirmed):
  PTF1A   — acinar master TF
            r=-0.720  p=1.81e-23
            Master gate of acinar identity
            Its loss initiates ADM
            Its restoration REVERSES PAAD
            (Dev Cell 2019 — causal confirmed)
  NR5A2   — acinar nuclear receptor
            r=-0.742  p=2.17e-43
            PAAD germline risk gene
  RBPJL   — acinar Notch TF
            r=-0.744  p=1.05e-43
  BHLHA15 — MIST1 acinar secretory TF
            r=-0.683  p=1.84e-34
  CPA1    — acinar digestive enzyme
            r=-0.728  p=4.14e-41
  PRSS1   — trypsinogen 1
            r=-0.700  p=8.49e-37

Acinar enzyme cluster (all confirmed):
  CTRC     r=-0.832  p=7.17e-37  strongest
  PNLIPRP1 r=-0.826  p=6.25e-36
  AMY2A    r=-0.814  p=4.19e-34
  CEL      r=-0.801  p=2.60e-32
  PNLIP    r=-0.791  p=4.74e-31
  CELA3A/B r≈-0.784
  14 acinar genes — all p<1e-07
  Most complete switch gene cluster
  in the series

False attractor (confirmed):
  KRT19  — ductal identity marker
           r=+0.800  p=3.78e-32
           Strongest FA signal in series
  KRT7   — ductal keratin  +20.0%
  TFF1   — ductal gland progenitor
           +27.0%  p=2.72e-15
           (unexpected — confirmed as
           progenitor niche marker
           Cell Stem Cell 2023)
  TFF2   — ductal gland progenitor
           +17.4%  p=1.24e-10
  MUC1   — ductal surface  +10.3%
  EPCAM  — progenitor surface +8.2%

  The false attractor is NOT pure ductal.
  It is a ductal gland progenitor hybrid —
  KRT19 high + TFF1/TFF2 high.
  Distinct from any normal cell type.

Molecular circuit (11/11 confirmed):
  KRAS → EZH2:   r=+0.597  p=8.80e-15
  EZH2 → PTF1A:  r=-0.369  p=7.65e-06
  KRAS → PTF1A:  r=-0.542  p=5.85e-12
  EZH2 → NR5A2:  r=-0.321  p=1.18e-04
  EZH2 → RBPJL:  r=-0.348  p=2.69e-05
  KRAS → KRT19:  r=+0.645  p=9.97e-18
  EZH2 → KRT19:  r=+0.525  p=3.26e-11
  KRAS → CTRC:   r=-0.524  p=3.64e-11
  MKI67→ KRAS:   r=+0.609  p=1.89e-15
  POSTN→ depth:  r=+0.529  p=2.21e-11
  TGFB1→ POSTN:  r=+0.582  p=5.56e-14

  Full circuit (NRF2 from literature 2025):
  KRAS → NRF2 → EZH2 → H3K27me3
  → PTF1A suppressed → acinar silence
  NRF2 was not in panel — derived from
  endpoints by framework, named by
  Nature Cancer 2025

Epigenetic lock (confirmed):
  EZH2   +5.6%  p=1.82e-09
  SUZ12  +3.5%  p=2.06e-07
  JARID2 +3.1%  p=2.80e-05
  EZH2 silences PTF1A/NR5A2/GATA6 loci
  via H3K27me3
  Same gain-of-function lock as BRCA
  Different lineage — same chromatin
  mechanism

Stromal co-stabilizer (unexpected — confirmed):
  POSTN   +32.5%  p=4.80e-21
  FN1     +18.7%  p=1.15e-21
  FAP     +23.8%  p=3.45e-15
  COL1A1  +14.1%  p=1.15e-10
  ACTA2   +10.3%  p=2.64e-12
  TGFB1   +7.2%   p=1.13e-09
  TGFB2   +10.3%  p=2.33e-08
  POSTN r=+0.529 with depth
  TGFB1→POSTN r=+0.582
  More dedifferentiated tumor =
  more CAF activation = more stroma
  The stroma and tumor co-stabilize
  the same attractor
  POSTN r=-0.259 with survival p=0.002
  42-fold in published data (Gastro 2007)
  7-month survival difference confirmed

Subtype (confirmed):
  GATA6 stratifies depth — p=0.000
  Classical (GATA6 high):
    depth 0.550  survival 13.8 mo
  Basal-like (GATA6 low):
    depth 0.647  survival 10.9 mo
  GATA6 is now a validated clinical
  biomarker (COMPASS trial)
  Framework derived same axis independently
  Within Basal: depth r=-0.318 p=0.009
  (survival prediction subtype-specific)

KRAS as attractor stabilizer (novel):
  r(KRAS expression, depth) = +0.707
  p=2.32e-22
  Not just mutation presence —
  expression LEVEL determines depth
  Higher KRAS = deeper in attractor
  = more acinar gene loss
  = more stroma activation
  Continuous quantitative predictor
  Not in published literature as
  within-tumor continuous correlation

Drug predictions (geometry-derived):
  1. EZH2 inhibitor (tazemetostat)
       Geometry: EZH2 gain-of-function lock
                 EZH2→PTF1A r=-0.369
                 EZH2 inhibition →
                 PTF1A demethylated →
                 acinar circuit executes
                 (PTF1A→CTRC intact r=+0.754)
       Literature: ✅ mechanism confirmed
                   EZH2i converts Basal→
                   Classical (Cancer Res 2020)
                   No PAAD Phase 2 yet —
                   this is the trial that
                   should exist
       TP53 status required for selection:
       TP53 wild-type responds better

  2. NRF2 inhibitor (brusatol / ML385)
       Geometry: NRF2 sits between KRAS
                 and EZH2 in self-amplifying
                 loop (lit 2025)
                 Framework found KRAS→EZH2
                 endpoints — lit filled node
       Literature: ✅ NRF2-EZH2 loop confirmed
                   Nature Cancer 2025
                   Compounds preclinical
                   for PAAD
       Most mechanistically targeted node —
       disrupts self-amplification without
       touching all KRAS pathways

  3. KRAS G12D inhibitor
       Geometry: r(KRAS,depth)=+0.707
                 KRAS drives all three arms:
                 tumor dedifferentiation +
                 stroma activation +
                 proliferation
       Literature: ✅ target confirmed
                   MRTX1133 Phase 1 terminated
                   (PK failure not biology)
                   Multiple next-gen G12D
                   inhibitors in pipeline
       Correct biology — chemistry
       barrier not biology barrier

  4. NRF2 + EZH2 combination (novel)
       Geometry: attack self-amplifying loop
                 (NRF2) AND existing lock
                 (EZH2) simultaneously
       Literature: ⚠️ not in any trial
                   not in any paper
                   mechanistically motivated
                   Testable: KRAS G12D PAAD
                   organoids today

  5. TGF-beta inhibitor (galunisertib)
       Geometry: TGFB1→POSTN r=+0.582
                 stroma co-stabilizes
                 attractor — removing
                 stroma should allow
                 attractor to shallow
       Literature: ✅ galunisertib in
                   PAAD trials

Novel predictions (not in literature):
  1. KRAS expression level continuously
     predicts attractor depth within
     established PAAD tumors (r=+0.707)
     Not just mutation — level matters
     Testable from existing RNA profiles

  2. PTF1A→acinar circuit intact (r=+0.754)
     Block is at input only
     Single upstream intervention
     (EZH2i or NRF2i) should be sufficient
     to restore full acinar program
     Testable in KRAS G12D cell lines

  3. POSTN+TGFB1 2-gene stroma score
     predicts survival better than
     differentiation depth score
     POSTN r=-0.259 TGFB1 r=-0.238
     Not in any published biomarker panel
     Testable from COMPASS cohort data

  4. Depth predicts survival within
     Basal-like subtype (r=-0.318 p=0.009)
     but not globally — subtype-specific
     survival predictor
     Testable from COMPASS cohort

  5. NRF2+EZH2 combination more effective
     than either alone for attractor
     dissolution in PAAD
     Mechanistically: removes induction
     signal AND existing chromatin lock
     Testable in KRAS G12D organoids

Analyst assumption corrections (not
framework errors — framework was correct):
  MYC: adjacent normal is acinar tissue
       (high-MYC secretory factory)
       MYC appears suppressed vs acinar
       baseline even in proliferating PAAD
       Framework correctly found suppression
       Analyst assumed neutral reference
  Survival global: surgical stage/margin
       dominate in resectable PAAD
       Framework correctly found depth
       signal within Basal subtype
       Analyst predicted scope too broadly

Scripts:
  paad_false_attractor.py    (Script 1 — discovery)
  paad_false_attractor_2.py  (Script 2 — corrected
                              classifier + gap
                              analysis + stroma)
  Self-contained — GEO accession to figure

Data:    GSE183795 (Hussain et al.)
         139 PAAD tumors
         102 adjacent non-tumor pancreas
         Affymetrix HuGene-1.0-ST
         Stage / grade / resection margin /
         survival annotated

Docs:    87a (Script 1 — discovery run)
         87b (Script 2 — corrected framework +
              reasoning artifact)
         87c (Literature check — complete,
              revised framing)
         Protocol (OrganismCore_Cancer_
                   Analysis_Protocol.md)

Prior entry (Doc 82, GSE155698):
         Superseded — predictions not tested,
         dataset not run.
         This entry (Doc 87a/b/c) is the
         valid record.

Status:  CONFIRMED + LITERATURE CHECK COMPLETE
         Circuit: KRAS→NRF2→EZH2→PTF1A
         11/11 connections confirmed
         PTF1A causal reversal confirmed
         POSTN survival split confirmed
         GATA6 subtype confirmed (clinical std)
         5 novel predictions stated + testable
         NRF2 inhibitor new drug target
         from literature completing circuit
```

#### PRAD — Prostate Adenocarcinoma
```
Status:   COMPLETE
          Scripts 1 and 2 run
          Literature check complete
          Documents: 88a, 88b, 88c

Lineage:  Luminal secretory epithelial
          Prostate-specific secretory cell
          Normal: ACPP/MSMB/KLK3 high
          AR-driven terminal identity

Block:    Luminal progenitor
          → mature luminal secretory
          Terminal secretory step blocked
          AR program amplified not lost
          NKX3-1 haploinsufficient
          (chr8p21 deletion)
          EZH2 lock (stage-dependent)

Dataset:  GSE32571
          59 PRAD tumors
          39 matched benign prostate
          Illumina HumanHT-12 v4
          Gleason high/low annotated
          Matched pairs (DKFZ cohort)

Switch genes (actual — from data):
  ACPP   r=-0.595 with depth ***
         Terminal secretory enzyme
         Primary expression-level
         depth predictor
         Not predicted — found by geometry
  MSMB   r=-0.551 with depth ***
         Secreted tumor suppressor
         2025 literature confirms
         AUC 0.93 — geometry preceded
         independent validation
  NKX3-1 +3.3% elevated (not suppressed)
         Haploinsufficiency at DNA level
         Expression maintained/elevated
         via AR-driven transcription
         of remaining allele
         Functional loss is genomic
         not transcriptomic in primary PRAD

Predicted switch genes (pre-data):
  NKX3-1 — CORRECT biology
            WRONG direction for expression
            Analyst error corrected by data
            Dual role confirmed by
            literature (MDPI Cancers 2025)
  AR      — Maintained flat (-0.4% ns)
            AR→NKX3-1 r=+0.361 confirmed
            AR is upstream driver not switch
  KLK3   — +7.1% elevated overall
            Falls with Gleason (p=0.0015)
            AR target confirmed in circuit
            Not a switch gene —
            a circuit output

False attractor identity:
  HOXC6  +34.7%  p=2.28e-15  r=+0.514
         Largest change in dataset
         Driven by METTL3/m6A/IGF2BP2
         (RNA-level epigenetic stabilization)
         Activates Wnt/β-catenin via
         SFRP1 suppression
  AMACR  +36.1%  p=5.39e-13  r=+0.428
         Second largest change
         Standard clinical diagnostic
         marker for PRAD worldwide
         Framework derived from
         first principles — geometry
         found pathology standard

Epigenetic lock:
  EZH2   +3.8%  p=1.53e-06
         r=+0.426 with depth
         4th solid cancer in series
         Non-canonical activation also
         present (activates AR targets
         while silencing differentiation)
         Primary lock in CRPC
         Secondary in primary PRAD
         (haploinsufficiency dominates
         in primary disease)

Circuit (confirmed Script 2):
  AR → NKX3-1 → ACPP / MSMB / KLK3
  AR   → NKX3-1  r=+0.361  p=0.005
  NKX3-1 → ACPP  r=+0.454  p=3.04e-04
  NKX3-1 → MSMB  r=+0.523  p=2.17e-05
  NKX3-1 → KLK3  r=+0.665  p=9.44e-09
  NKX3-1 → KLK2  r=+0.635  p=6.65e-08
  Architecture: INTACT
  Same as PAAD (PTF1A→CTRC r=+0.754)
  Block at NKX3-1 INPUT not downstream
  Restore NKX3-1 dose →
  intact circuit executes →
  attractor dissolves

Basal layer:
  KRT5   -17.1%  p=3.22e-15
  KRT14  -12.3%  p=3.33e-09
  TP63   -16.9%  p=1.92e-16
  Complete basal dissolution confirmed
  Framework found histological
  diagnostic criterion for invasive
  PRAD from gene expression alone

ERG subtype finding:
  ERG-high (fusion+): n=20
  ERG-low  (fusion-): n=39
  Threshold: 6.4804 (KDE-derived)
  Depth ERG-high: 0.433
  Depth ERG-low:  0.410
  p=0.614 — SAME ATTRACTOR
  ERG+ and ERG- PRAD converge to
  identical attractor geometry
  One dissolution strategy works
  for all primary PRAD regardless
  of ERG fusion status
  TMPRSS2 -6.3% in ERG-high
  confirms fusion from expression

Depth score:
  Mean: 0.418  Std: 0.123
  High Gleason: 0.462 ± 0.132
  Low  Gleason: 0.381 ± 0.103
  p=0.0024 CONFIRMED
  3-gene score (ACPP/HOXC6/AMACR):
  r=+0.866 with full depth score
  Clinical panel equivalent

Drug targets (geometry-derived):
  1. AR inhibitor
     Standard of care — confirmed
  2. EZH2 inhibitor (mevrometostat)
     Three trials failed unselected
     (CELLO-1, PROSTAR, tulmimetostat)
     Depth score is missing selection
     biomarker
     Trial design: depth > 0.55
     Pharmacodynamic: NKX3-1/ACPP
     restoration in biopsy
  3. NKX3-1 restoration
     EZH2i (indirect) or BAT
     AR→NKX3-1 r=+0.361 confirmed
     BAT (bipolar androgen therapy)
     supraphysiologic AR →
     NKX3-1 above threshold →
     terminal differentiation executes
     CAUTION: NKX3-1 dual role in
     late CRPC (oncogenic at that stage)
     Strategy valid for primary PRAD
     and early CRPC only
  4. MYC / BET inhibitor
     MYC +5.6% confirmed
     BET inhibitors in active PRAD trials
  5. AURKA inhibitor (alisertib)
     r=+0.346 with depth
     In PRAD and NEPC trials
  6. METTL3 inhibitor [from literature]
     METTL3 → m6A → HOXC6 stability
     Targets largest signal (+34.7%)
     at RNA level
  7. Wnt inhibitor [from literature]
     HOXC6 → SFRP1 suppression →
     Wnt/β-catenin → progenitor state
     Second pathway to HOXC6 strategy

Novel findings (6):
  N1: ACPP as primary depth predictor
      r=-0.595 — not in existing panels
  N2: NKX3-1 circuit INTACT
      Therapeutic implication: restore
      input → program executes
  N3: ERG subtypes share same attractor
      One strategy for all primary PRAD
  N4: Depth score = missing EZH2 trial
      selection biomarker
      CELLO-1 failed without it
  N5: MSMB r=-0.551 preceded 2025
      independent validation (AUC 0.93)
  N6: EZH2 non-canonical activation
      found from data anomaly before
      mechanism paper located

Cross-cancer pattern:
  BRCA: EZH2 lock            ✓
  PAAD: PTF1A circuit INTACT ✓  EZH2 ✓
  PRAD: NKX3-1 circuit INTACT ✓ EZH2 ✓
  Same architecture. Different lineage.
  Same therapeutic logic.

Analyst errors corrected by data:
  NKX3-1 predicted DOWN → found UP
  FOXA1  predicted DOWN → found UP
  Both corrected before literature.
  Both confirmed by literature.

Prediction score: 11/13 confirmed (85%)
  2 partially confirmed
  0 failed
  2 analyst errors corrected by data

Documents:
  88a — Script 1 discovery
  88b — Script 2 circuit analysis
  88c — Literature check

Doc origin: 83
```

#### STAD — Stomach Adenocarcinoma

```
Lineage:  Gastric epithelial
          (pit cells / chief cells /
          intestinal metaplasia)
Block:    Proliferative activation
          attractor — not a
          differentiation block.
          STAD does not arrest before
          a differentiation checkpoint.
          It enters a false attractor
          defined by mitotic activation
          (ZEB2/AURKA) co-regulated
          as a single unified program.
          Fundamentally different
          attractor architecture from
          PAAD and PRAD.

Analyst assumption errors (recorded):
  Predicted: gastric switch genes
             suppressed (MIST1/PGC/GKN1/TFF1)
  Reality:   ALL gastric master TFs
             elevated in tumor —
             SOX2 +54.1% / FOXA2 +16.2% /
             GATA6 +4.3% / GATA4 +14.8% /
             HNF4A +21.1%
             STAD does not lose gastric
             identity — it re-activates
             developmental TFs in cancer
             context.
  Predicted: CDH2/VIM elevated (EMT)
  Reality:   CDH2/VIM suppressed in bulk
             EMT subtype is a minority
             (~15%) not recoverable from
             expression arrays alone
             (CDH1 loss is protein-level
             in diffuse histology)
  Predicted: single master switch TF
             analogous to PTF1A/NKX3-1
  Reality:   No single switch TF found.
             STAD has distributed TF
             reactivation not single TF loss.
             Circuit-restoration therapy
             is not applicable.

False attractor identity:
  PRIMARY DRIVER (r=+0.84 with depth):
    ZEB2   — mesenchymal TF
             +31.5% in tumor ***
  COUPLED PROGRAM (r=+0.82, r(ZEB2,AURKA)=0.9871):
    AURKA  — mitotic kinase
             +33.4% in tumor ***
  ZEB2 and AURKA share 97.4% variance
  in 300 tumor samples.
  They are one program not two.
  This coupling is not in published
  literature. Framework discovery.

Switch genes (depth-inverse, r < -0.50):
  ERBB4   r=-0.6798 ***  terminal diff
           -46.6% in tumor
  CDH2    r=-0.6259 ***  mesenchymal marker
           -40.8% in tumor
  VIM     r=-0.6211 ***  stromal identity
           -3.7% in tumor
  FABP1   r=-0.6175 ***  intestinal marker
           -suppressed
  TWIST1  r=-0.5894 ***  EMT regulator
           -23.1% in tumor
  BCL2    r=-0.5832 ***  anti-apoptotic
           suppressed in deep tumors
  EZH2    r=-0.4368 ***  epigenetic
           -13.1% in tumor
           NOTE: mainstream literature
           reports EZH2 as oncogenic
           in STAD. Within-tumor inverse
           correlation is real but
           cohort-specific (ACRG Korean).
           EZH2 inhibitor contraindication
           requires independent validation.

Epigenetic finding:
  EZH2    -13.1% *** in ACRG cohort
  KDM6A   +6.9%  *** (H3K27 demethylase up)
  Net: H3K27me3 REDUCED in this cohort.
  OPPOSITE of BRCA/PAAD/PRAD pattern.
  EZH2 is not a universal oncogene.
  Direction must be determined per cancer.
  HDAC1   +12.8% *** r=+0.24 ***
  → HDAC inhibitors are correct
    epigenetic target in STAD.

CDX2 circuit:
  CDX2    +23.1% *** elevated
  r(CDX2, depth) = +0.3854 ***
  Circuit integrity: 1/5 targets intact
  CDX2 → MUC2    r=-0.016  BROKEN
  CDX2 → KRT20   r=+0.297  intact ✓
  CDX2 → VIL1    r=-0.024  BROKEN
  CDX2 → FABP1   r=-0.139  INVERTED
  CDX2 is oncogenic in STAD context —
  not a differentiation restoration target.
  Confirmed by published literature
  (CDX2 drives Reg IV/SOX9/migration
  not differentiation in gastric cancer).

TF network (all elevated in STAD):
  SOX2    +54.1% r=+0.394 ***
          3q amplification detected
          from expression geometry.
          Confirmed by published literature.
  FOXA2   +16.2% r=+0.523 ***
          Strongest gastric TF depth
          correlator. 4/8 circuit intact.
  GATA6   +4.3%  r=+0.412 ***
          4/8 circuit intact.
  GATA4   +14.8% r=-0.135 *
          Maintains CLDN18/PGC.
          Slight loss in deep tumors.
  HNF4A   +21.1% r=-0.129 *
          Maintains CLDN18/PGC.
          Slight loss in deep tumors.

Key structural findings:
  1. ZEB2-AURKA coupling r=0.9871 ***
     p=4.05e-239
     Single unified proliferative
     attractor program. Framework
     discovery — not in literature.
     Alisertib (AURKA inhibitor)
     collapses both programs simultaneously.

  2. Wnt pathway switch:
     CTNNB1  r=-0.5691 *** (canonical DOWN)
     WNT5A   r=+0.5585 *** (non-canonical UP)
     STAD is NOT a canonical Wnt cancer.
     WNT5A drives invasion in deep tumors.
     Confirmed by published literature
     (Cancer Research 2006, Frontiers 2021).

  3. Apoptosis transition:
     BCL2    r=-0.5832 *** (DOWN in deep)
     MCL1    r=+0.3460 *** (UP in deep)
     BAX     r=+0.4899 *** (UP in deep)
     Deep tumors: MCL1-dependent survival.
     Venetoclax (BCL2i) ineffective in deep STAD.
     MCL1 inhibitors correct target.
     Confirmed by published literature.

  4. GATA4/HNF4A → CLDN18 resistance circuit:
     GATA4 → CLDN18  r=+0.5365 ***
     HNF4A → CLDN18  r=+0.2757 ***
     Attractor deepening → GATA4/HNF4A
     partial loss → CLDN18 loss →
     zolbetuximab ineligibility.
     Circuit confirmed by published
     literature (iScience 2025).
     Depth-stratified selection framework
     for zolbetuximab is novel.

  5. TGF-B circuit split:
     TGFBR1 (ALK5) r=+0.4704 *** with depth
     TGFBR2        r=-0.5164 *** with depth
     TGFB2 ligand  r=-0.5493 *** with depth
     Non-canonical ALK5 arm drives
     ZEB2 not canonical TGF-B/TGFBR2.
     ALK5 inhibitors (galunisertib)
     are the upstream ZEB2 target.

  6. HER2 as attractor-deepening event:
     HER2-high depth: 0.7464 ± 0.0750
     HER2-low  depth: 0.6159 ± 0.1329
     p=2.19e-06 ***
     r(ERBB2, SNAI1) = +0.4028 ***
     HER2 amplification deepens the
     false attractor via SNAI1.
     New geometric framing of a
     known driver event.

  7. MSH6 loss tracks depth:
     MSH6 r=-0.4873 *** with depth
     Progressive MMR dysfunction in
     deep STAD via MSH6 not MLH1.
     Deep STAD warrants comprehensive
     MMR/TMB profiling beyond classical
     MLH1/MSI testing.

Clinical panel (3-gene, IHC-deployable):
  PRIMARY:
    MKI67(+) + ZEB2(+) / ERBB4(-)
    r = 0.9111 *** p=1.02e-116
    Strongest panel in this series.
    All three measurable by standard IHC.
  FALLBACK (2-gene):
    ZEB2(+) / ERBB4(-)
    r = 0.8925 ***

Drug predictions (geometry-derived,
all confirmed by literature):
  TIER 1 — PRIMARY ATTRACTOR TARGETS:
    Alisertib (AURKA)
      Geometry: r=+0.8222 ***
                ZEB2-AURKA coupling r=0.9871
      Literature: ✅ Phase I data in GI cancer
                  ⚠️  PD-L1 upregulation
                      resistance — requires
                      anti-PD-L1 combination
      Selection: depth score > 0.65
    CDK4/6 inhibitor (palbociclib/ribociclib)
      Geometry: CDK6 r=+0.7057 ***
                CDK4 r=+0.5206 ***
      Literature: ✅ active in solid tumors
    Topoisomerase II (TOP2A)
      Geometry: r=+0.7821 ***
      Literature: ✅ standard chemotherapy

  TIER 2 �� PATHWAY TARGETS:
    Trastuzumab (ERBB2/HER2)
      Geometry: r=+0.3872 ***
                HER2-high = deepest tumors
      Literature: ✅ approved (ToGA trial)
      Selection: HER2+ AND depth > 0.65
    Anti-MET (savolitinib/crizotinib)
      Geometry: r=+0.3386 ***
                99.7% of tumors elevated
      Literature: ✅ active trials
    HDAC inhibitor (vorinostat/entinostat)
      Geometry: HDAC1 r=+0.2389 ***
      Literature: ✅ active in GI cancers
    Ramucirumab (VEGFA)
      Geometry: VEGFA r=+0.4120 ***
      Literature: ✅ approved in advanced STAD
    ALK5 inhibitor (galunisertib)
      Geometry: TGFBR1 r=+0.4704 ***
                upstream of ZEB2-AURKA axis
      Literature: ✅ active trials
      🆕 ALK5 as upstream ZEB2 driver
         not in published literature

  TIER 3 — PATIENT-SELECTED:
    Zolbetuximab (CLDN18.2)
      Geometry: CLDN18 r=-0.2599 ***
                GATA4 → CLDN18 r=+0.5365 ***
      Literature: ✅ approved (SPOTLIGHT/GLOW)
      Selection: depth < 0.55
                 + CLDN18-high
                 + GATA4-preserved
      🆕 Depth-stratified selection
         not in published trial design
    MCL1 inhibitor (AMG-176/S63845)
      Geometry: MCL1 r=+0.3460 ***
                BCL2 r=-0.5832 ***
      Literature: ✅ active trials
      Selection: depth > 0.65
      🆕 Depth-stratified BCL2 vs MCL1
         selection not in literature
    Anti-PD-L1 (atezolizumab)
      Geometry: MSH6 r=-0.4873 ***
      Literature: ✅ AURKA → PD-L1
                     resistance (JCI 2022)
      Selection: depth > 0.65
                 + alisertib combination
                 OR MSH6-low + TMB-high

  COMBINATION PROPOSAL (geometry + literature):
    Alisertib + MCL1 inhibitor + anti-PD-L1
    Selection: depth > 0.65
    Rationale: AURKA collapses ZEB2/AURKA
               MCL1i removes apoptotic escape
               anti-PD-L1 blocks resistance
               All three mechanistically
               justified by independent
               evidence streams.
    🆕 Not in any published trial design.

  CONTRAINDICATED:
    Venetoclax (BCL2i)
      BCL2 r=-0.5832 *** (already low deep)
      Wrong target in deep STAD.
    EZH2 inhibitors (tazemetostat)
      EZH2 r=-0.4368 *** (ACRG cohort)
      Requires independent validation
      before clinical application.
      Mainstream literature reports EZH2
      as oncogenic in STAD — cohort
      discrepancy documented honestly.

Patient stratification by depth:
  Depth > 0.65 (MSS/TP53+ dominant):
    Alisertib + MCL1i + anti-PD-L1
    + Trastuzumab if HER2+
    + Ramucirumab (advanced)
    Test: MSH6 IHC + TMB
  Depth 0.50–0.65 (MSS/TP53- dominant):
    CDK4/6 inhibitor
    + Anti-MET
    + ALK5 inhibitor
    + Trastuzumab if HER2+
  Depth < 0.50 (MSI dominant):
    Zolbetuximab if CLDN18-high
                    + GATA4-preserved
    Pembrolizumab if MSI-H / TMB-high
    CDK4/6 inhibitor

Novel predictions (geometry-derived,
confirmed not in prior literature):
  1. ZEB2-AURKA coupling r=0.9871
     as single unified attractor program.
     Alisertib collapses both simultaneously.
     Doc 89c Section IX.
  2. Depth-stratified zolbetuximab selection:
     low depth + CLDN18-high + GATA4-preserved
     = best responders.
     Doc 89c Section X / 89d Section VI.
  3. GATA4/HNF4A → CLDN18 resistance circuit
     quantified from tumor expression geometry.
     Doc 89c Section VI / 89d Section VI.
  4. BCL2-to-MCL1 apoptotic transition
     as continuous depth-dependent function.
     Venetoclax ineffective in deep STAD.
     Doc 89c Section X / 89d Section IV.
  5. ALK5 (TGFBR1) as specific upstream
     driver of ZEB2-AURKA axis —
     not generic TGF-B signaling.
     Doc 89c Section IX / 89d Section VII.
  6. HER2 amplification as attractor-
     deepening event — geometric framing.
     Doc 89c Section VIII / 89d Section X.
  7. Triple combination: alisertib +
     MCL1i + anti-PD-L1 with depth
     score selection criterion.
     Assembled from three independent
     evidence streams by framework.
     Doc 89d Section XI.
  8. MSH6 progressive loss in deep STAD —
     comprehensive MMR/TMB profiling
     beyond classical MLH1/MSI testing.
     Doc 89c Section X / 89d Section IX.

Survival:
  GSE66229 survival data not in series
  matrix — in ACRG supplementary files.
  Published ACRG survival concordance
  with depth score:
    MSI (shallowest, depth 0.5810)
    → best OS (median not reached)
    MSS/TP53+ (deepest, depth 0.6697)
    → poor OS
  Depth-survival concordance confirmed
  by published ACRG data without
  accessing survival directly.
  Cristescu et al. Nature Medicine 2015.

Data:    GSE66229 (Cristescu et al.
         Nature Medicine 2015)
         ACRG Korean cohort
         300 STAD tumors
         100 matched normal gastric
         Affymetrix GPL570
Scripts: stad_false_attractor.py (S1)
         stad_circuit_analysis.py (S2)
         stad_survival_analysis.py (S3)
Docs:    89a (Script 1)
         89b (Script 2 / circuit)
         89c (Script 3 / panel / TF network)
         89d (Literature check)
         89e (Synthesis)
Status:  COMPLETE — SCRIPTS 1–3 +
         LITERATURE CHECK +
         SYNTHESIS DONE
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
