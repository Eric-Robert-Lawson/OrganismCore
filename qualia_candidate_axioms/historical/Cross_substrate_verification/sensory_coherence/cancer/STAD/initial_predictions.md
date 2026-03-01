# STOMACH ADENOCARCINOMA — PREDICTIONS LOCKED
## PRE-DATA RECORD
## OrganismCore — Cancer Validation #13
## Date: 2026-03-01

---

## METADATA

```
document_number:    pre-STAD
document_type:      Predictions locked before data
cancer:             Stomach Adenocarcinoma (STAD)
dataset:            GSE66229
                    300 gastric cancer samples
                    Affymetrix array
                    Tumor + normal pairs
                    Korean cohort
                    Survival data available
framework:          OrganismCore Principles-First
status:             PREDICTIONS LOCKED
                    Script 1 not yet run
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-01
series_position:    Cancer validation #13
follows:            PRAD (88a/88b/88c)
```

---

## I. LINEAGE

```
Cell of origin:
  Gastric glandular epithelium
  Multiple differentiated cell types:
    Pit/foveolar cells
      (MUC5AC/TFF1 — surface mucus)
    Parietal cells
      (ATP4A/ATP4B — HCl secretion)
    Chief cells
      (PGC/CTRB — pepsinogen)
    Enteroendocrine cells
      (CHGA/SYP — hormones)
    Stem cells
      (OLFM4/LGR5 — isthmus zone)

  Normal gastric identity genes:
    CLDN18  — most stomach-specific
               tight junction protein
               known — the most specific
               single gene for gastric
               identity in the body
    MUC5AC  — surface mucous cell mucin
    TFF1    — trefoil factor 1
               foveolar pit cell marker
    GKN1    — gastrokine 1
               stomach-specific secreted
               protein
    GKN2    — gastrokine 2
    OLFM4   — gastric stem cell marker
    ATP4A   — parietal cell H+/K+ ATPase
    PGC     — pepsinogen C (chief cell)

Molecular subtypes (TCGA 2014):
  EBV-positive  (~9%)
  MSI-high      (~22%)
  Genomically stable (GS)  (~20%)
    — enriched for diffuse type
    — CDH1 loss dominant
  Chromosomally unstable (CIN) (~50%)
    — enriched for intestinal type
    — TP53 mutations dominant
    — HER2 amplification here

Lauren histological subtypes:
  Intestinal type:
    Gland-forming
    Preceded by intestinal metaplasia
    CDX2/KRT20/MUC2 program active
    Precursor → H. pylori → atrophy →
    intestinal metaplasia → dysplasia →
    carcinoma
  Diffuse type:
    No glands
    Signet ring cells
    CDH1 loss (E-cadherin)
    Poorly cohesive
    Worse prognosis
    GS subtype
```

---

## II. PREDICTIONS LOCKED

### Switch Genes (predicted suppressed in STAD)

```
CLDN18   Claudin-18
  Most stomach-specific gene known.
  CLDN18.2 isoform restricted to
  gastric mucosa in normal tissue.
  Its loss = loss of gastric identity.
  Currently targeted by zolbetuximab
  in clinical trials — geometry should
  find this independently.
  Predict: strongly suppressed in STAD
  r(CLDN18, depth) < 0 predicted

MUC5AC   Gastric surface mucin
  Pit/foveolar cell identity marker.
  Normal stomach surface is coated
  with MUC5AC mucus.
  Lost in gastric cancer.
  Replaced by intestinal mucins (MUC2).
  Predict: suppressed in STAD

TFF1     Trefoil factor 1
  Foveolar pit cell marker.
  Gastric-specific.
  TFF1 knockout mice develop
  gastric cancer spontaneously —
  the only known gene whose deletion
  alone causes gastric cancer in mice.
  Predict: strongly suppressed in STAD

GKN1     Gastrokine 1
  Stomach-specific secreted protein.
  Tumor suppressor function.
  Virtually absent outside stomach.
  Predict: suppressed in STAD

CDH1     E-cadherin
  Master epithelial identity gene.
  Germline CDH1 mutations cause
  hereditary diffuse gastric cancer.
  Somatic loss frequent in diffuse type.
  Predict: suppressed — especially
  in diffuse / GS subtype

OLFM4    Gastric stem cell marker
  Marks the isthmus stem cell zone
  in normal gastric glands.
  Predict: suppressed — stem cell
  program silenced in cancer
```

### False Attractor (predicted elevated in STAD)

```
CDX2     Caudal-type homeobox 2
  Master transcription factor for
  intestinal identity.
  Found in intestinal metaplasia —
  the precursor lesion to intestinal-
  type gastric cancer.
  Its presence marks the cell's
  adoption of an intestinal progenitor
  false attractor state.
  Predict: elevated in STAD
  especially intestinal type

MUC2     Intestinal goblet cell mucin
  Marks intestinal identity.
  Found in goblet cells of intestinal
  metaplasia and intestinal-type STAD.
  Replaces MUC5AC in the false
  attractor state.
  Predict: elevated

KRT20    Intestinal epithelial keratin
  Marker of intestinal differentiation.
  Expressed in normal colon / small
  intestine — not normal stomach.
  Its presence in gastric tissue
  marks intestinal transdifferentiation.
  Predict: elevated

CDH2     N-cadherin
  EMT marker — cadherin switch.
  CDH1 (E-cadherin) down +
  CDH2 (N-cadherin) up =
  classic EMT signature.
  Predict: elevated in diffuse type
  and high-grade STAD

VIM      Vimentin
  Mesenchymal marker / EMT.
  Predict: elevated

TWIST1   EMT transcription factor
  Predict: elevated

ZEB1     EMT transcription factor
  Predict: elevated

SNAI1    Snail — EMT TF
  Predict: elevated
```

### Epigenetic Lock

```
EZH2     Enhancer of zeste homolog 2
  5th solid cancer prediction.
  Series so far:
    BRCA: EZH2 elevated ✓
    PAAD: EZH2 elevated ✓  r>0 ✓
    PRAD: EZH2 elevated ✓  r>0 ✓
  STAD:   EZH2 elevated predicted
          r(EZH2, depth) > 0 predicted
  Same gain-of-function chromatin lock.
  Different lineage. Same mechanism.
  EZH2 inhibitor predicted as drug target.

SUZ12    PRC2 component
  Predict: elevated with EZH2

BMI1     PRC1 component
  Predict: elevated
```

### Scaffold

```
MYC      Amplified in CIN subtype (~30%)
  Predict: elevated in STAD overall
  Especially CIN molecular subtype

ERBB2    HER2
  Amplified in ~20% STAD
  Trastuzumab is standard of care
  for HER2-positive STAD
  Geometry should find HER2 elevated
  — and find it as a drug target —
  independently from prior knowledge
  This is a key framework validation:
  the geometry must find the one
  approved targeted therapy for STAD
  (other than chemotherapy) from
  first principles

EGFR     Amplified in subset
  Predict: elevated

CCND1    Cyclin D1
  Cell cycle — predict elevated
  in CIN subtype

FGFR2    Amplified in ~10% STAD
  Predict: elevated in subset

MET      Amplified in subset (~4%)
  Predict: elevated
```

### Specific Predictions

```
PREDICTION 1:
  CLDN18 strongly suppressed
  It is the most stomach-specific gene.
  Its loss should be the clearest
  signal in the dataset.
  Predict: largest or near-largest
  suppression in STAD vs normal.

PREDICTION 2:
  TFF1 suppressed
  TFF1 knockout → spontaneous gastric
  cancer in mice.
  The framework should find this.

PREDICTION 3:
  CDX2 elevated in STAD
  The intestinal metaplasia → carcinoma
  sequence means CDX2 should be
  elevated in the intestinal-type
  tumors that dominate this dataset.

PREDICTION 4:
  EZH2 elevated with r(EZH2, depth) > 0
  5th cancer in series.
  Same lock. Different lineage.

PREDICTION 5:
  ERBB2/HER2 elevated
  Framework finds approved drug
  target independently.
  If the geometry finds ERBB2 elevated
  and r(ERBB2, depth) > 0, this
  confirms the framework can derive
  the existing standard of care
  from first principles — exactly
  as AMACR confirmed the diagnostic
  standard in PRAD.

PREDICTION 6:
  MUC5AC → MUC2 switch
  Normal stomach: MUC5AC high, MUC2 low
  STAD:           MUC5AC low,  MUC2 high
  A mucin identity switch from
  gastric to intestinal.
  Predict: MUC5AC suppressed,
           MUC2 elevated.

PREDICTION 7:
  Depth correlates with aggressive
  molecular subtype.
  Predict: GS and MSI-high deeper
  than EBV and CIN.
  OR: depth correlates with Lauren
  diffuse > intestinal.

PREDICTION 8:
  The false attractor in STAD is a
  INTESTINAL PROGENITOR state.
  Not a generic dedifferentiated state.
  Specifically: a CDX2-driven intestinal
  metaplasia-like state.
  The geometry should show:
  CDX2/KRT20/MUC2 up together
  CLDN18/MUC5AC/TFF1 down together
  This is a LINEAGE SWITCH not just
  loss of identity.
  Gastric → intestinal progenitor.
```

---

## III. COMPLEXITY NOTE

```
STAD is the most complex cancer
in the series so far.

Reasons:
  1. Multiple cell types in normal
     gastric mucosa (pit / parietal /
     chief / enteroendocrine / stem).
     The normal expression signature
     contains multiple programs.

  2. Multiple molecular subtypes
     (EBV / MSI / GS / CIN) with
     different biology and drivers.
     The bulk tumor signal will be
     a mixture.

  3. Two histological types
     (intestinal vs diffuse) with
     fundamentally different biology:
     Intestinal → CDX2/MUC2 attractor
     Diffuse → CDH1 loss / EMT attractor

  4. H. pylori infection drives
     intestinal metaplasia which
     is itself an intermediate state
     between normal and cancer.
     The false attractor may already
     exist in the metaplasia.

  5. Geographic variation:
     GSE66229 is Korean cohort.
     Korean STAD has higher proportion
     of EBV-positive and MSI-high
     than Western cohorts.

WHAT THIS MEANS FOR SCRIPT 1:
  The bulk signal should still show:
    CLDN18/MUC5AC/TFF1/GKN1 DOWN
    EZH2/MYC/CDX2 UP
  But the depth score will need
  to handle subtype heterogeneity.
  The ERG-like subtype split
  (two attractors vs one) is possible.
  Script 1 must test for this.
```

---

## IV. CROSS-CANCER PREDICTIONS

```
From the series pattern so far:

EZH2 gain lock:
  BRCA ✓  PAAD ✓  PRAD ✓
  STAD: PREDICTED ✓

Intact circuit architecture:
  PAAD: PTF1A→CTRC INTACT
  PRAD: NKX3-1→ACPP INTACT
  STAD: TFF1→MUC5AC or
        CDX2→MUC2 INTACT?
  Predict: INTACT
  The terminal differentiation
  circuit should still run when
  the switch gene is present.

Clinical diagnostic marker derivation:
  PAAD: framework found CTRC
  PRAD: framework found AMACR
  STAD: framework should find
        a clinical diagnostic marker
        from first principles.
  Candidate: CLDN18
             Already a drug target
             (zolbetuximab)
             Geometry should find it
             as the strongest
             switch gene signal.

Drug target derivation:
  In every prior cancer the framework
  found the existing standard of care
  from geometry.
  BRCA: hormone receptor / HER2
  PAAD: KRAS (indirectly)
  PRAD: AR inhibitor / EZH2i
  STAD: ERBB2/HER2 (trastuzumab)
        CLDN18.2 (zolbetuximab)
  Both should emerge from data.
```

---

## V. PREDICTIONS SUMMARY

```
SWITCH GENES (locked):
  CLDN18  — strongest suppression predicted
  MUC5AC  — gastric mucin switch
  TFF1    — foveolar marker
  GKN1    — stomach-specific
  CDH1    — epithelial identity

FALSE ATTRACTOR (locked):
  CDX2    — intestinal master TF
  MUC2    — intestinal mucin
  KRT20   — intestinal keratin
  VIM     — EMT
  CDH2    — N-cadherin

EPIGENETIC LOCK (locked):
  EZH2    — 5th cancer in series
             r(EZH2, depth) > 0

SCAFFOLD (locked):
  MYC     — elevated
  ERBB2   — elevated (HER2)
  FGFR2   — elevated subset

IDENTITY SWITCH (locked):
  MUC5AC → MUC2
  Gastric mucin → intestinal mucin
  Most specific identity switch
  prediction in any cancer so far.

DRUG TARGETS (locked):
  1. ERBB2/HER2 inhibitor
     (trastuzumab — must find this)
  2. CLDN18.2 inhibitor
     (zolbetuximab — must find this)
  3. EZH2 inhibitor
  4. CDX2 pathway
  5. Anti-EMT

document_number:    pre-STAD
series_position:    Cancer validation #13
status:             PREDICTIONS LOCKED
                    Awaiting Script 1
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-01
```
