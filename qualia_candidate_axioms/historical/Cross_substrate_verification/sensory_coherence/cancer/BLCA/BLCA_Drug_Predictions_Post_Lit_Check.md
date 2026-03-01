# BLCA — DRUG PREDICTIONS ARTIFACT
## Consolidated Actionable Drug Hypotheses
## Date: 2026-03-01 | Author: Eric Robert Lawson | OrganismCore
## Status: PREDICTIONS LOCKED BEFORE LITERATURE CHECK

---

## HOW TO READ THIS DOCUMENT

```
Each prediction has:
  PREDICTION:  Exact falsifiable claim
  EVIDENCE:    Data supporting it
               (r values, p values, datasets)
  MECHANISM:   Why it should work
  STATUS:      Known / Novel / Confirmed
  TESTABLE BY: Exactly what experiment
               would confirm or refute it
  PRIORITY:    1 (highest) to 3 (lowest)
               based on clinical impact
               and experimental accessibility
```

---

## TIER 1 — NOVEL, UNTESTED, HIGH PRIORITY

---

### DRUG-BLCA-1
### Abemaciclib outperforms palbociclib in deep basal BLCA

```
PREDICTION:
  In basal BLCA cell lines and tumours,
  abemaciclib (CDK6 preference) will show
  greater growth inhibition than palbociclib
  (CDK4/6 balanced) at equivalent doses.
  The difference will be largest in
  TWIST1-high/GATA3-low (deep basal) cells.
  Palbociclib will show minimal effect
  in the deepest basal cells because
  CDK4 is not the active driver.

EVIDENCE:
  CDK6 r=+0.65*** with basal depth (GSE13507)
  CDK6 r=+0.56*** with basal depth (TCGA)
  CDK4 r=-0.06 ns  with basal depth (TCGA)
  CDK4 r=-0.06 ns  with basal depth (GSE)
  CDK6 predicts OS in basal BLCA p=0.032*
  CDK4 does not predict OS (ns)
  CCND1 r=-0.60*** in basal depth
  (CCND1 lost in deep basal — no CCND1-CDK4
   complex available for palbociclib to block)
  CDK6 is the ORPHAN driver in deep basal
  (paired with CCND3/CCNE, not CCND1)
  Two independent datasets, two platforms.

MECHANISM:
  In deep basal BLCA:
    CCND1 is lost (r=-0.60***)
    CDK4 is flat (r=-0.06 ns)
    CDK6 is elevated (r=+0.65***)
  CDK6 drives S-phase entry without CCND1
  by partnering non-canonically with CCND3
  or CCNE1.
  Palbociclib preferentially targets
  CDK4-CCND1 complex. This complex does
  not exist in deep basal BLCA.
  Abemaciclib inhibits CDK6 more potently
  AND has CDK4-independent activity.
  Therefore abemaciclib retains efficacy
  where palbociclib has no target.

STATUS:
  Novel. No published trial or paper
  tests abemaciclib vs palbociclib
  specifically in basal BLCA.
  CDK4/6i in BLCA is preclinical only
  (no Phase III results 2024).
  Literature (USMedicine): CDK4/6 pathway
  is a bladder cancer target — preclinical.
  The CDK6>CDK4 asymmetry and abemaciclib
  implication are not in any published paper.

TESTABLE BY:
  IMMEDIATE (no patients needed):
    Cell lines: T24, SCaBER, HT-1376
    (basal BLCA lines)
    Measure CDK6 and CDK4 protein by WB.
    Sort by TWIST1/GATA3 ratio.
    Deepest basal = high TWIST1/low GATA3.
    Run palbociclib vs abemaciclib
    dose-response (IC50).
    Prediction: abemaciclib IC50 << palbociclib
    IC50 in deepest basal lines.
    Measure CCND1 protein as confirmatory
    covariate (low CCND1 = abemaciclib benefit).

  VALIDATION:
    GSE13507/TCGA depth scores applied
    to CCLE BLCA cell lines.
    Correlate cell line CDK6/CDK4 ratio
    with published abemaciclib IC50 data.

PRIORITY: 1
  Most immediately testable.
  Existing approved drugs.
  Could redirect current CDK4/6i
  trial design for BLCA.
```

---

### DRUG-BLCA-2
### Erdafitinib + palbociclib combination
### for FGFR3-high/CCND1-high luminal BLCA

```
PREDICTION:
  In FGFR3-high luminal BLCA cell lines,
  erdafitinib + palbociclib will be
  synergistic (combination index < 1).
  Erdafitinib monotherapy will fail to
  fully suppress CCND1/CDK4 axis.
  Combination will arrest cells that
  escape erdafitinib monotherapy.

EVIDENCE:
  FGFR3 r=+0.78*** luminal depth (GSE)
  FGFR3 r=+0.59*** luminal depth (TCGA)
  CCND1 r=+0.70*** luminal depth (GSE)
  CCND1 r=+0.51*** luminal depth (TCGA)
  FGFR3 and CCND1 are the two strongest
  luminal FA genes in both datasets.
  r(FGFR3, CCND1) in luminal is strongly
  positive — they co-activate.
  FGFR3 → CCND1 is a known signalling axis:
  FGFR3 activates CCND1 transcription via
  MAPK/ERK and PI3K pathways.
  Blocking FGFR3 reduces CCND1 but
  does not eliminate CDK4/6 activity
  (CCND1 persists partially, RB is
  not fully dephosphorylated).
  CDK4/6i blocks the residual CCND1-CDK4
  activity — double blockade of the axis.
  Erdafitinib response rate ~40% in
  FGFR3-altered BLCA.
  60% non-responders need a second hit.
  CCND1/CDK4 bypass is the most
  mechanistically plausible resistance.

MECHANISM:
  FGFR3 → (via ERK/PI3K) → CCND1 ↑
  CCND1 + CDK4 → RB phosphorylation → S-phase
  Erdafitinib blocks step 1.
  Palbociclib blocks step 3.
  Together: full pathway suppression.
  Neither alone achieves complete
  RB hypophosphorylation in all cells.
  Together: RB remains hypophosphorylated
  → permanent G1 arrest.

STATUS:
  Novel combination. No published trial.
  Erdafitinib + CDK4/6i not described
  in bladder cancer literature.
  Mechanistic rationale is strong.
  Analogous combinations have shown
  synergy in breast cancer
  (CDK4/6i + RTK inhibitor combinations).

TESTABLE BY:
  IMMEDIATE:
    RT112 cell line (FGFR3-mutant luminal)
    SW780 cell line (FGFR3-amplified luminal)
    Erdafitinib alone: IC50 curve
    Palbociclib alone: IC50 curve
    Combination: Chou-Talalay method
    Measure: RB phosphorylation by WB
    Measure: CCND1 protein after erd alone
    Prediction: CCND1 partially persists
    after erdafitinib → palbociclib
    adds suppression → CI < 1 (synergy)

  PATIENT STRATIFICATION:
    FGFR3(+)/CCND1-high on IHC
    = candidates for combination trial
    FGFR3(+)/CCND1-low = erdafitinib alone
    sufficient

PRIORITY: 1
  Erdafitinib resistance is a real
  clinical problem NOW.
  60% of patients do not respond.
  This combination addresses the
  primary resistance mechanism.
  If confirmed in RT112: rationale for
  erdafitinib + ribociclib Phase I/II.
```

---

### DRUG-BLCA-3
### MCL1 inhibitor (BRD-810 / S63845)
### for deep basal BLCA

```
PREDICTION:
  Deep basal BLCA (TWIST1-high/GATA3-low)
  will be disproportionately sensitive to
  MCL1 inhibition compared to shallow
  basal or luminal BLCA.
  The deepest basal cells will show
  dual MCL1+BCL2 elevation and may
  require MCL1i + BCL2i (venetoclax)
  combination for maximal apoptosis.

EVIDENCE:
  MCL1 r=+0.51*** basal depth (GSE)
  MCL1 r=+0.40*** basal depth (TCGA)
  BCL2 r=+0.44*** basal depth (GSE)
  BCL2L1 r=-0.11 ns (BCL-XL flat)
  BAX r=-0.08 ns (flat)
  Both MCL1 AND BCL2 rise with basal depth.
  BCL2 was predicted to be flat —
  it is positive.
  Deepest basal = maximum anti-apoptotic
  protection via BOTH MCL1 and BCL2.
  Two independent datasets.
  MCL1 > BCL2 in both (stronger r).
  MCL1 is the primary target.

MECHANISM:
  As basal BLCA deepens (EMT/TWIST1-driven)
  cells encounter increasing apoptotic
  pressure (anoikis, immune surveillance).
  MCL1 and BCL2 are upregulated as
  survival adaptations.
  MCL1 is the dominant anti-apoptotic
  protein in most solid tumours.
  MCL1 inhibition releases BAX/BAK
  from MCL1 sequestration → MOMP →
  cytochrome c → apoptosis.
  In the deepest cells (maximum depth):
  BCL2 also elevated → BCL2 can rescue
  cells from MCL1 inhibition alone.
  Dual MCL1i + BCL2i (venetoclax) needed
  for the deepest basal subgroup.

STATUS:
  Novel. No MCL1 inhibitor trial for
  bladder cancer exists (2024).
  BRD-810 (Nature Cancer 2024) is a
  new highly selective MCL1 inhibitor
  advancing toward solid tumour trials.
  AZD5991, S63845 are MCL1 inhibitors
  in early clinical development.
  The framework provides the biomarker
  for patient selection:
  TWIST1-high + MCL1-high IHC
  = deep basal BLCA = MCL1i candidate.
  Without this biomarker, MCL1i would
  be tested in unselected BLCA and
  likely fail in the diluted population.

TESTABLE BY:
  IMMEDIATE:
    Basal BLCA cell lines: T24, HT-1376
    Sort by TWIST1 expression (depth proxy)
    Measure MCL1 and BCL2 protein by WB
    Run S63845 (MCL1i) dose-response
    Prediction: TWIST1-high/GATA3-low
    lines are more sensitive to S63845
    Run S63845 + venetoclax combination
    in deepest lines
    Prediction: synergy in depth-high lines
    not in depth-low lines

  BIOMARKER:
    MCL1 IHC H-score in BLCA TMA
    Correlate with TWIST1/GATA3 status
    Confirm co-elevation in deep basal

PRIORITY: 2
  No approved MCL1i yet in solid tumours.
  But BRD-810 is advancing.
  Framework provides patient selection
  before the drug enters trial —
  that is the optimal timing.
```

---

### DRUG-BLCA-4
### Erdafitinib + galunisertib (TGF-βRi)
### for FGFR3(+)/SMAD3(+) luminal BLCA
### (Track A, erdafitinib resistance prevention)

```
PREDICTION:
  FGFR3-altered luminal BLCA with
  high SMAD3 expression will respond
  LESS well to erdafitinib monotherapy
  than FGFR3-altered/SMAD3-low tumours.
  Erdafitinib + galunisertib will overcome
  this resistance in SMAD3-high cells.
  SMAD3-high status will predict
  erdafitinib non-response.

EVIDENCE:
  SMAD3 r=+0.60*** luminal depth (GSE)
  SMAD3 r=+0.47*** luminal depth (TCGA)
  Confirmed in both datasets, both platforms.
  SMAD3 is the third strongest luminal
  FA gene after FGFR3 and CCND1.
  TGFBR2 r=-0.27** in luminal depth
  (receptor FALLING while effector RISING).
  This is non-canonical SMAD3 activation:
  FGFR3 → SMAD3 directly (receptor-independent).
  SMAD3 predicts OS in luminal BLCA
  (GSE13507 individual gene p=0.034*
   SMAD3 high = worse OS).
  r(SMAD3, aneuploidy) = -0.27***
  SMAD3-high = CIN-low = Track A luminal.
  Track A is the erdafitinib-targetable
  subtype but SMAD3 provides a parallel
  survival signal.

MECHANISM:
  FGFR3 activates SMAD3 non-canonically
  (via MAPK or direct phosphorylation —
  described in chondrosarcoma/myeloma).
  SMAD3 activates transcription of
  survival genes (BCL-XL, survivin,
  TWIST family members in some contexts).
  When erdafitinib blocks FGFR3:
  Canonical outputs (CCND1, ERK) fall.
  But SMAD3 may remain partially active
  via alternative inputs (TGFB1 ligand
  r=+0.34*** in luminal depth is present)
  or via HRAS r=+0.39*** in luminal depth
  (HRAS can phosphorylate SMAD3).
  Residual SMAD3 activity = survival
  of erdafitinib-treated cells.
  Adding galunisertib (TGF-βR1i) removes
  any ligand-driven SMAD3 input.
  Combination: erdafitinib (FGFR3 block)
  + galunisertib (TGF-βR1 block) =
  dual SMAD3 deprivation.

STATUS:
  Novel. Erdafitinib + TGF-βRi
  not described in bladder cancer.
  Galunisertib has been tested in
  other solid tumours (hepatocellular,
  glioblastoma) with acceptable safety.
  The SMAD3-as-depth-driver finding
  is not in any published literature.
  This is the most unreported
  mechanistic finding from the analysis.

TESTABLE BY:
  IMMEDIATE:
    RT112 (FGFR3-mutant, luminal)
    Measure SMAD3 protein/activity (WB)
    after erdafitinib treatment.
    Prediction: SMAD3 activity persists
    after FGFR3 inhibition.
    Add galunisertib → SMAD3 suppressed.
    Measure apoptosis: erdafitinib alone
    vs erdafitinib + galunisertib.
    Prediction: combination > monotherapy.

  PATIENT STRATIFICATION:
    SMAD3 IHC on FGFR3+ luminal BLCA
    from patients treated with erdafitinib.
    Prediction: SMAD3-high patients have
    lower response rate and shorter PFS.
    If confirmed: SMAD3 IHC added to
    erdafitinib patient selection protocol.

PRIORITY: 1
  Erdafitinib resistance is an active
  clinical problem.
  SMAD3 high may be the molecular
  explanation for the 60% non-responders.
  This is the most clinically urgent
  prediction from the entire analysis.
```

---

## TIER 2 — PATIENT STRATIFICATION (existing drugs)

---

### DRUG-BLCA-5
### MLH1 IHC for pembrolizumab selection
### in luminal BLCA (not MSH2/MSH6)

```
PREDICTION:
  MLH1 IHC loss predicts pembrolizumab
  response in luminal BLCA more accurately
  than MSH2 or MSH6 IHC.

EVIDENCE:
  MSH2 r=-0.43*** luminal depth (GSE)
  MSH2 r=-0.40*** luminal depth (TCGA)
  MSH6 r=-0.52*** luminal depth (GSE)
  MSH6 r=-0.44*** luminal depth (TCGA)
  BUT: MSH2 and MSH6 RISE with CIN
  r(MSH2, aneuploidy) = +0.30***
  r(MSH6, aneuploidy) = +0.26***
  These are CIN-compensatory, not MSI.
  MLH1 r=-0.17*** with MSI sensor score
  MLH1 r=-0.11* with MSI MANTIS
  MLH1 is the direct MSI driver.
  MLH1 ↑=better OS in luminal (p=0.010**)
  (Low MLH1 = worse OS in luminal)

MECHANISM:
  MSH2/MSH6 fall with luminal depth
  but also rise with CIN.
  They are not reliable MSI markers
  in BLCA because they are confounded
  by the CIN signal.
  MLH1 is not confounded by CIN
  in this way.
  MLH1 loss (silencing/mutation)
  directly drives microsatellite
  instability → neoantigens →
  pembrolizumab response.
  The standard Lynch syndrome IHC panel
  tests MLH1/PMS2/MSH2/MSH6.
  In BLCA, focus should be on MLH1.

STATUS:
  Partially supported by literature.
  MLH1 is the canonical MSI-high driver.
  The specific finding that MSH2/MSH6
  are CIN-confounded in BLCA
  (not reliable MSI biomarkers) is novel.

TESTABLE BY:
  Retrospective IHC study:
  BLCA cohort with pembrolizumab
  treatment data.
  Compare MLH1 IHC vs MSH2 IHC vs
  MSH6 IHC as predictors of response.
  Prediction: MLH1 loss is a stronger
  predictor than MSH2/MSH6 loss.

PRIORITY: 2
  Pembrolizumab is already approved.
  This refines patient selection
  for existing therapy.
```

---

### DRUG-BLCA-6
### Platinum chemotherapy for
### luminal-unstable (Track B) preferentially

```
PREDICTION:
  Luminal-unstable BLCA (AURKA-high/
  CIN-high/SMAD3-low/FGFR3 wild-type)
  will show higher response rate to
  neoadjuvant cisplatin-based chemotherapy
  than luminal-papillary (FGFR3-high/
  SMAD3-high/CIN-low) tumours.
  Within luminal BLCA, FGA and aneuploidy
  score will be predictive of platinum
  response in a continuous manner.

EVIDENCE:
  Luminal FGA = 0.342 vs Basal = 0.260
  p=8.75e-06 ***
  Luminal > Basal CIN (confirmed TCGA).
  r(aneuploidy, luminal_depth) = -0.17*
  Deep luminal (Track A) is CIN-LOW.
  Track B (luminal-unstable) is CIN-HIGH.
  CIN-high tumours accumulate more DNA
  double strand breaks with platinum →
  more apoptosis.
  Literature: luminal-unstable subtype
  in Robertson 2017 has higher
  genomic instability.
  Clinical data (neoadjuvant platinum
  in TCGA Robertson analysis) shows
  luminal-unstable has variable but
  sometimes better platinum response.

CAVEAT (from literature check):
  CIN-platinum relationship is
  bidirectional — can cause resistance.
  Applies to Track B specifically
  not to all luminal BLCA.
  Track A (luminal-papillary) is
  CIN-low — do NOT treat with
  platinum preferentially.
  Erdafitinib first for Track A.

TESTABLE BY:
  Retrospective TCGA or BCON cohort:
  Subset luminal BLCA by AURKA/FGA
  (Track B proxy).
  Compare neoadjuvant platinum response
  rate in Track A vs Track B.
  Prediction: Track B response rate
  significantly higher.

PRIORITY: 2
  Important for treatment sequencing.
  Avoids giving wrong drug to Track A
  patients who have erdafitinib as
  better first option.
```

---

### DRUG-BLCA-7
### Abemaciclib + anti-PD1 for basal BLCA
### (NOT gemcitabine + CDK4/6i)

```
PREDICTION:
  Abemaciclib + pembrolizumab will show
  additive or synergistic activity in
  basal BLCA (immune-hot subtype).
  Abemaciclib + gemcitabine will be
  ANTAGONISTIC in basal BLCA.

EVIDENCE:
  CDK6 is the primary driver in basal ✓
  Abemaciclib suppresses CDK6 ✓
  Literature (Springer 2020):
  CDK4/6i + anti-PD1 = synergistic
  CDK4/6i + gemcitabine = ANTAGONISTIC
  (gemcitabine requires S-phase for
   efficacy; CDK4/6i blocks S-phase)
  Basal BLCA is immune-hot (CD274 high,
  CD8A positive) → pembrolizumab-eligible.
  Abemaciclib may reduce Treg activity
  (known CDK4/6i class effect) →
  enhances anti-tumour immunity.

STATUS:
  The CDK4/6i + ICI synergy and
  CDK4/6i + gem antagonism are
  in the literature.
  The specific combination in basal
  BLCA with abemaciclib is not tested.
  The framework adds:
  Use abemaciclib (not palbociclib)
  specifically for basal (CDK6-driven)
  BLCA in the combination.

TESTABLE BY:
  Syngeneic basal BLCA mouse model
  (MB49 or BBN963 basal-like model).
  Abemaciclib alone vs
  abemaciclib + anti-PD1 vs
  abemaciclib + gemcitabine.
  Prediction: ICI combination > mono,
  gemcitabine combination < mono.

PRIORITY: 2
  Clinically important warning:
  do not combine CDK4/6i with
  gemcitabine in BLCA trials.
```

---

## TIER 3 — LONGER HORIZON

---

### DRUG-BLCA-8
### FGFR1 inhibitor (pemigatinib)
### for FGFR1-high deep basal BLCA

```
PREDICTION:
  Deep basal BLCA tumours with high
  FGFR1 expression will respond to
  FGFR1/2/3 inhibitor pemigatinib
  (or infigratinib).

EVIDENCE:
  FGFR1 r=+0.50*** basal depth (TCGA)
  FGFR1 r=+0.56*** basal depth (GSE)
  FGFR3 r=-0.76*** in basal depth
  (deep basal has FGFR1 high, FGFR3 low)
  The isoform switch is confirmed ×2.

STATUS:
  FGFR1 inhibition not tested in BLCA.
  Pemigatinib approved for FGFR2-altered
  cholangiocarcinoma.
  Pan-FGFR inhibitors tested in BLCA
  only for FGFR3 alterations.
  FGFR1-high selection in basal BLCA
  is a novel enrichment strategy.

TESTABLE BY:
  FGFR1-high basal BLCA cell lines
  (select from CCLE by FGFR1 expression).
  Pemigatinib dose-response.
  Confirm FGFR1 r vs pemigatinib IC50.

PRIORITY: 3
  Requires FGFR1 mutation/amplification
  data to properly test.
  Expression-only is insufficient.
```

---

### DRUG-BLCA-9
### WNT5A pathway inhibition
### for deep basal BLCA (invasion suppression)

```
PREDICTION:
  WNT5A-high basal BLCA will show
  reduced invasion in vitro when
  treated with WNT5A pathway inhibitors
  (BOX5 peptide / anti-ROR2).
  WNT5A high = worse OS (p=0.026*)
  in basal BLCA (TCGA confirmed).

EVIDENCE:
  WNT5A predicts OS in basal BLCA
  p=0.026* ↑=worse (TCGA n=79 events)
  Literature (Cell 2022): CAFs drive
  basal BLCA stemness via WNT5A
  paracrine axis.
  WNT5A drives bladder cancer invasion
  via non-canonical Wnt (Frontiers 2020).

STATUS:
  WNT5A as OS predictor in basal BLCA
  is a framework-original finding.
  BOX5 (WNT5A antagonist) and
  anti-ROR2 (receptor) are preclinical.

TESTABLE BY:
  Invasion assay (Matrigel transwell)
  in TWIST1-high basal BLCA cell lines.
  Add WNT5A recombinant protein →
  confirm invasion increase.
  Add BOX5 → confirm invasion block.
  Correlate with WNT5A baseline expression.

PRIORITY: 3
  Longer horizon. BOX5 not in clinic.
  But WNT5A IHC as prognostic marker
  is testable now.
```

---

## SUMMARY TABLE

```
ID             Drug(s)                      Subtype              Novel?  Priority  Testable Now?
─────────────────────────────────────────────────────────────────────────────────────────────────
DRUG-BLCA-1    Abemaciclib > palbociclib    Deep basal           YES     1         YES (cell lines)
DRUG-BLCA-2    Erdafitinib + palbociclib    Luminal FGFR3/CCND1  YES     1         YES (RT112/SW780)
DRUG-BLCA-3    MCL1i (BRD-810/S63845)       Deep basal           YES     2         YES (T24/HT-1376)
DRUG-BLCA-4    Erdafitinib + galunisertib   FGFR3+/SMAD3+        YES     1         YES (RT112)
DRUG-BLCA-5    Pembrolizumab (MLH1 select)  MLH1-low luminal     PARTLY  2         Retro IHC study
DRUG-BLCA-6    Cisplatin (Track B select)   Luminal-unstable     PARTLY  2         Retro TCGA cohort
DRUG-BLCA-7    Abemaciclib + anti-PD1       Basal (not + gem)    PARTLY  2         Mouse model
DRUG-BLCA-8    Pemigatinib (FGFR1i)         FGFR1-high basal     YES     3         Cell lines
DRUG-BLCA-9    WNT5A inhibitor (BOX5)       Deep basal           YES     3         Invasion assay
─────────────────────────────────────────────────────────────────────────────────────────────────

PRIORITY 1 (start here):
  DRUG-BLCA-1: abemaciclib vs palbociclib in T24/SCaBER
  DRUG-BLCA-2: erdafitinib + palbociclib in RT112
  DRUG-BLCA-4: SMAD3 activity after erdafitinib in RT112

All three require only:
  2-3 cell lines (all commercially available)
  Western blot equipment
  Standard drug dose-response assay
  Approximately 6-8 weeks wet lab time
  No patients. No clinical trial.
  No funding beyond standard lab costs.
```

---

## BIOMARKER-TO-DRUG MAP

```
If patient IHC shows:              Consider:
──────────────────────────────────────────────────────────
GATA3+/KRT5-                       Luminal subtype workup
GATA3-/KRT5+                       Basal subtype workup

FGFR3+ AND SMAD3-low               Erdafitinib (Track A, good responder)
FGFR3+ AND SMAD3-high              Erdafitinib + galunisertib (DRUG-BLCA-4)
FGFR3+ AND CCND1-high              Erdafitinib + palbociclib (DRUG-BLCA-2)
FGFR3- AND AURKA-high/FGA-high     Cisplatin + AURKA inhibitor (Track B)
MLH1-low (any luminal)             MSI test → pembrolizumab (DRUG-BLCA-5)

TWIST1+ AND CDK6+ AND GATA3-       Deep basal panel (p=0.038* OS)
CDK6-high (basal)                  Abemaciclib > palbociclib (DRUG-BLCA-1)
MCL1-high AND TWIST1-high          MCL1 inhibitor candidate (DRUG-BLCA-3)
S100A8-high (any subtype)          Worst prognosis flag
CD274-high (basal)                 Pembrolizumab (immune-hot)
WNT5A-high (basal)                 WNT5A pathway (DRUG-BLCA-9, longer horizon)
```

---

## STATUS

```
document_type:    Drug predictions artifact
date_locked:      2026-03-01
author:           Eric Robert Lawson
framework:        OrganismCore

predictions:      9 drug hypotheses
                  3 Priority 1
                  4 Priority 2
                  2 Priority 3

novel_predictions: 6 fully novel
                   3 partially novel
                   (existing drugs,
                    novel patient selection)

literature_gap:   CDK4/6i in BLCA =
                  preclinical only.
                  No abemaciclib vs palbociclib
                  comparison exists for BLCA.
                  MCL1i = no BLCA trial exists.
                  SMAD3 as erdafitinib resistance =
                  not described anywhere.

most_urgent:      DRUG-BLCA-4
                  (SMAD3 as erdafitinib
                   resistance mechanism)
                  Erdafitinib non-response is
                  an active clinical problem.
                  60% of patients fail.
                  SMAD3-high may explain why.

status:           COMPLETE
                  Ready for lab handoff
```
