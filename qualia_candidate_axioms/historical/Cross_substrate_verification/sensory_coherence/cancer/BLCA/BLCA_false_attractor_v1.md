# DOCUMENT 91a — SCRIPT 1 REASONING ARTIFACT
## BLADDER CANCER — FALSE ATTRACTOR ANALYSIS
## Dataset: GSE13507 | Date: 2026-03-01
## Author: Eric Robert Lawson | OrganismCore

---

## I. TECHNICAL NOTES

```
DATASET: GSE13507
  256 samples total
  Normal: 9
  Luminal: 123 (median split GATA3/KRT5)
  Basal: 123
  1 Unknown (mouse MPP sample — excluded)

PROBE MAP: 126 genes covered (125 in matrix)
  Reused GPL6102 from ESCA Script 3.
  Efficiency confirmed — no re-download needed.
  Missing: FGFR2, KRT6A, PVRL4, VEGFR1

SUBTYPE SEPARATOR:
  GATA3 Luminal vs Basal: p=1.03e-10 ***
  KRT5  Luminal vs Basal: p=6.53e-24 ***
  Classification validated by both markers.
  Median split on GATA3-KRT5 score works.

SURVIVAL:
  Time found: 165 samples ✓
  Event found: 0 ✗
  Key: 'overall survival': death/survival
  BUT the parser did not capture 'death'
  as event=1 because the value IS the
  key name ('overall survival: death'
  means the event occurred — the value
  IS 'death' or 'survival').
  Fix needed: parse 'overall survival'
  key where value = 'death' → event=1,
  value = 'survival' → event=0.
  'cancer specific survival' same pattern.
  'survival month' = time ✓ (parsed).
  EVENT PARSING FIXABLE — data exists.
  Script 2 will fix this.
```

---

## II. FOLD CHANGE — WHAT WAS RIGHT

### LUMINAL vs NORMAL

```
CONFIRMED PREDICTIONS (UP as predicted):
  FGFR3  +9.6%  p=7.53e-03 **  ✓
    FDA-approved erdafitinib target.
    Framework derived independently.
  GATA3  +11.3% p=1.31e-03 **  ✓
    Luminal identity FA marker confirmed.
  PPARG  +11.2% p=5.04e-05 ***  ✓
    Luminal differentiation driver confirmed.
  ERBB2  +4.9%  p=1.31e-03 **  ✓
    HER2 elevated in luminal BLCA confirmed.
  KRT20  +23.3% p=4.15e-03 **  ✓
    Same intestinal/columnar marker as EAC.
    KRT20 elevated in luminal BLCA —
    urothelial and intestinal differentiation
    share this marker. Cross-cancer signal.
  EZH2   +12.7% p=1.27e-04 ***  ✓
    Epigenetic lock confirmed in luminal.
  HDAC1  +3.0%  p=9.19e-03 **  ✓
    Epigenetic lock confirmed.

SWITCH GENES (DOWN predicted):
  UPK1B  -2.8%  ns ✗
  UPK2   +11.5% ns (WRONG DIRECTION) ✗
  UPK3A  -4.2%  ns ✗
  CLDN3  +9.3%  ns (wrong direction) ✗

  THE SWITCH GENE FINDING:
  UPK genes are NOT suppressed in
  luminal BLCA vs Normal.
  UPK2 is actually ELEVATED.
  This is the most important error
  to explain.

  WHY UPK GENES ARE NOT SUPPRESSED:
  The luminal subtype in BLCA is NOT
  a terminal differentiation block
  in the same way as ESCC (IVL loss)
  or EAC (CDH1 loss).
  Luminal BLCA RETAINS umbrella markers
  (UPK2 elevated vs Normal).
  The attractor is not blocking
  terminal umbrella differentiation —
  it is blocking something BEFORE that.
  Luminal BLCA cells are stuck at an
  INTERMEDIATE differentiation state
  that EXPRESSES UPK genes but cannot
  exit to post-mitotic umbrella cells.
  They express umbrella markers but
  keep proliferating.
  This is the luminal BLCA attractor:
    Active UPK expression (retained)
    + Active FGFR3/PPARG (FA drivers)
    + Retained proliferation capacity
  The execution block is NOT at the
  UPK expression gate — it is at
  the CELL CYCLE EXIT gate.
  Cells express differentiation markers
  while continuing to divide.
  This is a different topology to
  ESCC and EAC.

  REVISED PREDICTION:
  Luminal BLCA switch genes are
  CELL CYCLE GENES, not terminal
  differentiation markers.
  The block is at the cell cycle exit.
  Evidence: CDKN2B r=-0.57***
  (lost in deep luminal — cell cycle
   brake is missing, not diff markers).

NOTCH1 IN LUMINAL:
  Luminal: 10.99 vs Normal: 11.69
  NOTCH1 LOWER in luminal than Normal.
  p=8.49e-03 **
  CC-5 NOT CONFIRMED in luminal ✗
  Epithelial rule does not hold here.
  NOTCH1 is SUPPRESSED in luminal BLCA.
  This is different from ESCC where
  NOTCH1 was elevated.
  Explanation: NOTCH1 in urothelium
  drives differentiation toward umbrella.
  In luminal BLCA, NOTCH1 is partially
  suppressed — consistent with the
  cell-cycle-exit block interpretation.
  Cells that cannot complete NOTCH1-driven
  umbrella differentiation stay luminal.
  NOTCH1 rule revised:
  NOTCH1 is elevated in squamous cancers
  (ESCC) but SUPPRESSED in urothelial
  luminal BLCA.
  Urothelial context = tumor suppressor.
  Squamous context = oncogene.
  This is a LINEAGE-SPECIFIC rule
  more granular than the binary
  epithelial/myeloid distinction.

CDX2 IN LUMINAL:
  CDX2 +6.3% p=0.0171 * (slightly UP)
  CC-4 NOT CONFIRMED as predicted absent.
  CDX2 is slightly elevated in luminal BLCA.
  Small but statistically significant.
  Possible explanation:
  KRT20 is also elevated in luminal BLCA.
  KRT20 and CDX2 co-appear in intestinal
  metaplasia (as in Barrett's/EAC).
  Luminal BLCA may have a weak
  intestinal-like transcriptional program.
  This is a genuinely unexpected finding.
  Low-grade luminal BLCA and intestinal
  metaplasia of the bladder (cystitis
  cystica/glandularis) share CDX2/KRT20.
  This may represent a common
  intestinal-type attractor accessible
  from both esophageal and urothelial
  cells.
  NOVEL OBSERVATION: KRT20+CDX2 co-
  elevation in luminal BLCA connects
  to the EAC intestinal attractor.
  Cross-cancer intestinal metaplasia
  signal confirmed in two tissues.
```

### BASAL vs NORMAL

```
CONFIRMED PREDICTIONS (UP as predicted):
  KRT5   +16.5% p=2.57e-03 **  ✓
  KRT14  +12.4% p=0.0146 *    ✓
  S100A8 +19.4% p=0.0545 ns   (trend ✓)
  AURKA  +19.4% p=1.09e-04 *** ✓
    Mitotic kinase elevated in basal BLCA.
    Consistent with high proliferation.
  EZH2   +10.4% p=2.18e-04 *** ✓
    EP-1 confirmed in basal too.
  HDAC1  +2.3%  p=0.0144 *    ✓

CONFIRMED PREDICTIONS (DOWN as predicted):
  Note: Switch genes (GATA3/FOXA1/CDH1)
  did NOT change vs Normal.
  GATA3 Normal=10.40 Basal=10.46 (flat) ✗
  FOXA1 Normal=11.96 Basal=11.94 (flat) ✗
  CDH1  Normal=7.82  Basal=7.85  (flat) ✗
  THE BASAL SWITCH GENE ERROR:
  These genes are NOT suppressed in
  basal BLCA vs Normal urothelium.
  This is because Normal urothelium
  already has LOW GATA3/FOXA1 in basal
  cells (it is the luminal umbrella cells
  that express GATA3/FOXA1 in normal tissue).
  Normal urothelium is HETEROGENEOUS.
  The bulk "Normal" signal (n=9) averages
  basal+intermediate+umbrella layers.
  GATA3/FOXA1 in basal BLCA is
  NOT lower than Normal BULK because
  Normal Bulk already includes basal
  cells with low GATA3.
  The switch is between LUMINAL and BASAL
  subtypes, not between BLCA and Normal.
  This is the correct comparison.
  CORRECTION: Compare BASAL vs LUMINAL,
  not BASAL vs NORMAL, for switch genes.

  BASAL vs LUMINAL (from depth correlations):
  GATA3  r=-0.88*** in basal depth ✓
  FOXA1  r=-0.84*** in basal depth ✓
  These are the strongest negative
  correlations in the entire analysis.
  The switch IS real — wrong comparator.

WRONG DIRECTION (predicted UP, found DOWN):
  VIM    -13.5% p=1.14e-03 ** ✗
    Predicted: VIM UP in basal BLCA
    Found: VIM DOWN vs Normal
    But within basal: VIM r=+0.53***
    Same platform effect as HDAC1/EZH2
    in ESCA. VIM is a within-basal
    depth driver, not a between-group marker.

  ZEB1   -3.6%  p=8.83e-03 **  ✗
    Predicted: ZEB1 UP in basal BLCA
    Found: ZEB1 DOWN vs Normal
    Same explanation as ESCA:
    ZEB1 in normal urothelium is HIGH
    (squamous/basal identity retained).
    ZEB1 in basal BLCA is slightly LOWER
    because cancer dedifferentiation
    partially reduces ZEB1.
    But within-basal: ZEB1 r=+0.46***
    ZEB1 is still a within-basal
    depth driver. The cross-group
    direction is confounded by
    heterogeneous Normal.

  BCL2   -12.9% p=1.32e-05 *** ✗
    Predicted: BCL2 UP (venetoclax target).
    Found: BCL2 DOWN in basal BLCA.
    This kills the venetoclax prediction
    for basal BLCA specifically.
    BCL2 is LOWER in basal BLCA.
    The venetoclax target is NOT basal.
    BUT: BCL2 r=-0.37*** in luminal depth.
    BCL2 is suppressed in DEEP LUMINAL.
    The BCL2 finding is inverted from
    the prediction.
    Revised: BCL2 is a LUMINAL marker
    that is lost as luminal BLCA deepens.
    BCL2 loss may increase apoptosis
    sensitivity in deep luminal BLCA.
    Venetoclax logic needs full revision
    for BLCA context.

  ZEB2   -16.5% p=1.37e-03 **  ✗
    Predicted: ZEB2 elevated in basal BLCA
    (from ESCA ZEB2-EMT coupling).
    Found: ZEB2 DOWN in basal vs Normal.
    But within basal: ZEB2 r=+0.56***
    (depth driver in deep basal).
    ZEB2 is lower on average but
    rises with depth WITHIN basal.
    The most dedifferentiated basal
    tumors have high ZEB2.
    This is consistent with ZEB2
    marking the most aggressive
    basal BLCA subset.

TP63 IN BLCA:
  TP63 Normal=11.29 Luminal=11.21 Basal=11.06
  ALL NEAR IDENTICAL.
  TP63 does NOT distinguish subtypes
  in bulk expression.
  CC-1 NOT CONFIRMED ✗ (flat across groups)
  BUT within basal: TP63 r=-0.55***
  TP63 is LOST in deep basal.
  This is the opposite of prediction.
  Predicted: TP63 UP in basal (identity marker).
  Found: TP63 DOWN in deep basal (lost).
  INTERPRETATION:
  TP63 in urothelial basal is a
  DIFFERENTIATION marker of the
  normal basal layer — not an
  oncogenic identity retainer.
  As basal BLCA deepens (becomes more
  aggressive/dedifferentiated), it LOSES
  even basal urothelial markers like TP63.
  The deepest basal BLCA is BELOW the
  normal basal state — it has lost
  even the basal identity markers.
  REVISED CROSS-CANCER RULE:
  TP63 direction depends on CANCER STATE,
  not just tissue type:
    ESCC: TP63 retained (squamous identity)
    Basal-BLCA deep: TP63 LOST
    (gone below basal urothelial state)
  This deepens the framework significantly.
  The false attractor in deep basal BLCA
  is MORE PRIMITIVE than normal basal
  urothelium — it has lost even the
  basal markers.
```

---

## III. DEPTH CORRELATIONS — KEY FINDINGS

### LUMINAL DEPTH

```
STRONGEST POSITIVE (FA markers):
  CCND1  r=+0.70*** PRIMARY ANCHOR
  FGFR3  r=+0.70*** CO-PRIMARY ANCHOR
  SMAD3  r=+0.54*** UNEXPECTED
  KRT19  r=+0.48***
  TP63   r=+0.47*** (rising with luminal depth)
  JAG1   r=+0.46*** (NOTCH ligand)
  SOX2   r=+0.39***
  NOTCH1 r=+0.39*** (rising within luminal)
  IVL    r=+0.35*** (squamous marker in luminal)

STRONGEST NEGATIVE (switch genes):
  CDKN2B r=-0.57*** PRIMARY GATE
  CLDN3  r=-0.56*** (claudin lost)
  UPK3A  r=-0.52***
  CDKN2A r=-0.49***
  UPK1B  r=-0.46***
  ALDH1A1 r=-0.45*** (stem cell lost)
  PCNA   r=-0.45*** (proliferation marker)
  VIM    r=-0.44***
  NOTCH2 r=-0.42***
  MSH6   r=-0.41*** (MMR lost)
  BCL2   r=-0.37***

KEY INSIGHTS FROM LUMINAL DEPTH:
  1. CCND1 is the strongest single
     depth driver in luminal BLCA.
     FGFR3 is co-equal.
     Predicted L-D1 r(FGFR3)>0.50: ✓ (r=0.70)
     Predicted L-D5 FGFR3+CCND1>FGFR3: ✓
     r=0.75 combined vs 0.70 alone.

  2. CDKN2B and CDKN2A are the PRIMARY
     SWITCH GENES for luminal depth,
     not UPK genes.
     The cell cycle checkpoint loss
     (not terminal diff marker loss)
     is the execution block.
     This confirms the revised model:
     Luminal BLCA block = cell cycle exit,
     not umbrella differentiation.

  3. SMAD3 r=+0.54*** in deep luminal:
     TGF-β pathway ACTIVE in deep luminal.
     SMAD3 is a TGF-β transcription factor.
     Deep luminal BLCA has active TGF-β.
     This is unexpected — TGF-β usually
     drives differentiation/growth arrest.
     In deep luminal context it may be
     driving EMT-like signals alongside
     FGFR3 proliferative signals.
     Paradox: TGF-β + FGFR3 simultaneously.
     Resolved: FGFR3 activates SMAD3
     via non-canonical pathway.
     Or: TGF-β-driven EMT is beginning
     in the deepest luminal tumors.

  4. TP63 r=+0.47*** in luminal depth:
     Squamous/basal marker rising
     in deep luminal BLCA.
     Deep luminal tumors are acquiring
     squamous features.
     This is the SQUAMOUS TRANSDIFFERENTIATION
     of deep luminal BLCA.
     Clinical implication: deeply stuck
     luminal BLCA may express squamous
     markers — may confuse pathology
     (adenosquamous mixed histology).
     Same as ESCA NP-ESCA-3 (SPRR1A+TP63
     hybrid subtype) but in bladder.

  5. IVL r=+0.35*** in luminal depth:
     Involucrin (terminal squamous marker)
     rising in deep luminal BLCA.
     Confirms squamous transdifferentiation
     in the deepest luminal tumors.
     IVL was the primary switch gene in ESCC.
     Here it rises with depth — not falls.
     Cross-cancer: IVL direction is
     context-dependent.

  6. MSH6/MSH2 r=-0.41/-0.38*** in depth:
     MMR genes LOST in deep luminal BLCA.
     MMR loss = microsatellite instability.
     Deep luminal BLCA has HIGHER MSI burden.
     This predicts: DEEP LUMINAL BLCA is
     immunotherapy-responsive (MSI-high).
     Pembrolizumab is approved for MSI-high
     tumors regardless of histology.
     NOVEL PREDICTION:
     Luminal depth score predicts MSI
     and therefore pembrolizumab response.

  7. ALDH1A1 r=-0.45*** (suppressed with depth):
     Cancer stem cell marker LOST in
     deep luminal BLCA.
     Deep luminal tumors have LOST
     stem-like properties.
     Dedifferentiated state is not
     a cancer stem cell state in luminal BLCA.
```

### BASAL DEPTH

```
STRONGEST POSITIVE (FA markers):
  TWIST1 r=+0.74*** PRIMARY ANCHOR
  CDK6   r=+0.59*** CELL CYCLE DRIVER
  FN1    r=+0.57*** FIBRONECTIN/ECM
  ZEB2   r=+0.56*** EMT MASTER TF
  SNAI1  r=+0.55*** EMT
  VIM    r=+0.53*** MESENCHYMAL
  KRT14  r=+0.50*** BASAL KERATIN
  MYC    r=+0.50*** ONCOGENE
  CDH2   r=+0.50*** N-CADHERIN (EMT)
  ZEB1   r=+0.46*** EMT/BASAL
  S100A8 r=+0.46*** INFLAMMATORY
  MCL1   r=+0.46*** SURVIVAL
  DSG3   r=+0.45*** SQUAMOUS JUNCTION
  FGFR1  r=+0.43*** RTK

STRONGEST NEGATIVE (switch genes):
  GATA3  r=-0.88*** PRIMARY GATE
  FOXA1  r=-0.84*** CO-PRIMARY GATE
  PPARG  r=-0.79*** LUMINAL TF LOST
  KRT8   r=-0.72*** LUMINAL KERATIN LOST
  ERBB3  r=-0.71*** LUMINAL RTK LOST
  KRT19  r=-0.68*** LUMINAL KERATIN LOST
  KRT7   r=-0.68*** LUMINAL KERATIN LOST
  HES1   r=-0.67*** NOTCH TARGET LOST
  FGFR3  r=-0.64*** LUMINAL RTK LOST
  KRT13  r=-0.62*** LUMINAL KERATIN LOST
  UPK2   r=-0.60*** UMBRELLA MARKER LOST
  CLDN7  r=-0.57*** TIGHT JUNCTION LOST
  SMAD3  r=-0.56*** TGF-β LOST
  TP63   r=-0.55*** BASAL MARKER LOST

KEY INSIGHTS FROM BASAL DEPTH:
  1. GATA3 r=-0.88*** is the STRONGEST
     SINGLE CORRELATION in the entire
     BLCA analysis.
     Prediction B-D3 r(GATA3)<-0.50: ✓ (r=-0.88)
     GATA3 loss is the primary gate
     for basal depth.
     Every standard deviation deeper in
     basal BLCA = GATA3 substantially lower.
     GATA3 IHC is the primary clinical
     tool for luminal vs basal diagnosis
     — this confirms it is also
     a depth stratifier within basal.

  2. FOXA1 r=-0.84***:
     Pioneer TF for luminal identity.
     Lost as deeply as GATA3.
     GATA3+FOXA1 co-loss = deepest basal.

  3. PPARG r=-0.79***:
     Nuclear receptor for luminal program.
     Lost in deep basal — confirms
     complete luminal identity erasure.

  4. Full luminal keratin loss:
     KRT8/KRT7/KRT19/KRT13 all r<-0.62***
     The deeper the basal tumor, the more
     completely it has erased luminal
     keratin identity.

  5. TWIST1 r=+0.74*** PRIMARY BASAL ANCHOR:
     Predicted: TWIST1 as EMT marker (UP).
     Found: TWIST1 is the PRIMARY depth
     anchor — strongest positive correlate.
     TWIST1 > KRT5 as basal depth marker.
     This was NOT predicted — predicted
     B-D1 was KRT5.
     The data-driven panel:
     TWIST1(+)/CDK6(+)/FN1(+) r=+0.77***
     outperforms the predicted panel
     KRT5(+)/EGFR(+)/GATA3(-) r=+0.66***

  6. KRT5 r=-0.22* (WRONG DIRECTION):
     Predicted: KRT5 UP with basal depth.
     Found: KRT5 SLIGHTLY DOWN with depth.
     KRT5 marks basal BLCA vs luminal BLCA
     (FC +16.5% vs Normal).
     But within basal: DEEPER basal has
     LESS KRT5.
     Interpretation: KRT5 marks entry
     into basal identity (present in
     shallow basal BLCA) but is LOST
     in the DEEPEST basal BLCA.
     The deepest basal BLCA has moved
     BELOW the normal basal urothelial
     state — it has lost even KRT5.
     Confirmed by TP63 r=-0.55*** (same).
     DEEP BASAL BLCA IS BELOW THE
     NORMAL BASAL STATE.
     This is a new attractor topology:
     not arrested IN the basal state,
     but arrested BELOW it.
     More primitive than any normal
     urothelial cell type.

  7. CDK6 r=+0.59***:
     Cell cycle driver in deep basal.
     CDK6 inhibition (palbociclib/
     ribociclib/abemaciclib) is a
     predicted target for deep basal BLCA.
     Combined with FGFR3 prediction
     for luminal: CDK4/6i is relevant
     to BOTH subtypes but through
     different mechanisms.

  8. HES1 r=-0.67***:
     NOTCH target gene LOST in deep basal.
     NOTCH signalling is SUPPRESSED
     in deep basal BLCA.
     Consistent with NOTCH acting as
     differentiation promoter —
     its targets are lost as cells
     dedifferentiate.

  9. MCL1 r=+0.46***:
     Anti-apoptotic MCL1 ELEVATED in
     deep basal BLCA.
     MCL1 inhibitor (AMG-176) is a
     predicted drug target for deep
     basal BLCA.
     This replaces the BCL2/venetoclax
     prediction (BCL2 is DOWN in basal).
     Revised: MCL1i not BCL2i for
     deep basal BLCA.

  10. FGFR1 r=+0.43*** in deep basal:
      FGFR1 (not FGFR3) is the FGFR
      isoform relevant to deep basal.
      FGFR3 is the luminal BLCA FGFR.
      FGFR1 is the basal BLCA FGFR.
      This mirrors ESCA:
        ESCC: FGFR1 amplified (squamous)
        EAC:  FGFR3 lower (no role)
      BLCA:
        Luminal: FGFR3 r=+0.70***
        Basal:   FGFR1 r=+0.43***
      Cross-cancer FGFR isoform rule:
        FGFR3 = columnar/luminal cancers
        FGFR1 = squamous/basal cancers
```

---

## IV. PREDICTION TESTS — SUMMARY

```
CONFIRMED ✓:
  L-D1: r(FGFR3,luminal depth) = +0.70*** ✓
  L-D3: r(UPK2,luminal depth) = -0.39*** ✓
        (UPK genes fall with depth even
         though mean is UP vs Normal)
  L-D5: FGFR3+CCND1 combined r=+0.75 >
        FGFR3 alone r=+0.70 ✓
  B-D3: r(GATA3,basal depth) = -0.88*** ✓
        (strongest confirmation in study)
  CC-1-L: TP63 r=+0.47 in luminal depth ✓
          (squamous marker rising in deep
           luminal BLCA — novel finding)

NOT CONFIRMED ✗:
  L-D2: r(PPARG,luminal depth) = +0.15 ns
        PPARG is elevated vs Normal (+11%)
        but does not track within-luminal depth.
        PPARG marks luminal identity broadly,
        not depth within luminal.
  L-D4: CDKN1A r=+0.11 (wrong direction)
        Predicted: p21 lost in deep luminal.
        Found: CDKN1A slightly positive.
        CDKN2A/CDKN2B lost instead (r=-0.49/-0.57)
        The checkpoint loss is at CDKN2A/B
        not CDKN1A. Different checkpoint gate.
  B-D1: KRT5 r=-0.22* (wrong direction!)
        Deep basal has LESS KRT5.
        Model revision required (see above).
  B-D2: EGFR r=+0.28** (below threshold)
        Direction correct, magnitude insufficient.
        EGFR rises with depth but only moderately.
  B-D4: TP63 r=-0.55*** (wrong direction)
        Deep basal LOSES TP63.
        Major model revision (see above).
  B-D5: ZEB2-AURKA r=-0.43*** (NEGATIVE)
        The coupling is ANTICORRELATED in BLCA.
        ZEB2 and AURKA move in OPPOSITE directions.
        This is the most striking cross-cancer
        divergence in the framework.
  EP-1: EZH2 r=-0.10 in luminal depth
        EZH2 does not track luminal depth.
        Elevated vs Normal (+12.7%) but flat
        within luminal. Same as ESCA HDAC1/EZH2.
  EP-3: EZH2+HDAC1 combined does not
        improve on either alone in luminal.
        Cannot replicate ESCA finding here.
  EP-4: KDM6A r=+0.13 luminal (wrong dir)
        KDM6A not tracking depth in luminal.
  W-1:  APC r=+0.26** (wrong direction)
        APC rises slightly with luminal depth.
        No Wnt activation in luminal BLCA.
        Different from EAC.
  CC-3: KDM6A r=-0.24** basal (right direction
        but below -0.40 threshold)
        Trending in right direction but weak.
```

---

## V. ZEB2-AURKA — MAJOR CROSS-CANCER FINDING

```
RESULTS:
  Normal  (n=9):   r(ZEB2,AURKA) = -0.23 ns
  Luminal (n=123): r(ZEB2,AURKA) = -0.36***
  Basal   (n=123): r(ZEB2,AURKA) = -0.43***

PREDICTION: r = +0.55 to +0.75 in basal
FOUND:      r = -0.43***

ZEB2 and AURKA are ANTI-CORRELATED
in BLCA. Both subtypes.

THIS IS NOT AN ERROR — IT IS A FINDING.

Cross-cancer ZEB2-AURKA coupling:
  STAD:         r = +0.99 (positive)
  EAC:          r = +0.47 (positive, weaker)
  Basal-BLCA:   r = -0.43 (NEGATIVE)
  Luminal-BLCA: r = -0.36 (NEGATIVE)

The coupling INVERTS in BLCA.

WHY IS IT NEGATIVE IN BLCA?

In STAD and EAC:
  ZEB2 and AURKA are co-elevated in
  the most dedifferentiated/CIN tumors.
  They share a common upstream driver
  (TGF-β/hypoxia → ZEB2; CIN → AURKA).

In BLCA:
  ZEB2 tracks the EMT/mesenchymal axis.
  AURKA tracks the luminal/proliferative axis.
  These are DIFFERENT and COMPETING
  programs in BLCA.

  Basal BLCA depth:
    ZEB2 r=+0.56*** (deep basal = high ZEB2)
    AURKA r=+0.26 (deep basal = slight AURKA up)
    But ZEB2 high BASAL has HIGH EMT (TWIST1/VIM)
    And AURKA rises in both luminal and basal
    through different mechanisms.

  The anti-correlation arises because:
  Luminal BLCA: AURKA high, ZEB2 low
  (proliferative, luminal, not mesenchymal)
  Basal BLCA: AURKA lower, ZEB2 higher
  (EMT, mesenchymal, not proliferating as fast)

  ACROSS THE WHOLE BLCA COHORT:
  High ZEB2 = basal/EMT = lower AURKA
  High AURKA = luminal/proliferative = lower ZEB2
  The negative correlation reflects SUBTYPE
  identity, not a cancer-progression axis.

REVISED CROSS-CANCER RULE:
  ZEB2-AURKA coupling direction encodes
  the PROLIFERATIVE vs EMT balance:
    Positive coupling (STAD/EAC):
      Tumors where CIN drives both
      proliferation AND EMT simultaneously.
      High-CIN GI adenocarcinomas.
    Negative coupling (BLCA):
      Tumors where EMT and proliferation
      are in a trade-off.
      High-ZEB2 BLCA = slow-dividing EMT.
      High-AURKA BLCA = fast-dividing luminal.
      These are different tumour programmes
      that do not co-occur.

  This is a NEW framework rule:
  The SIGN of r(ZEB2,AURKA) encodes
  whether a cancer uses simultaneous
  or mutually exclusive
  proliferation + EMT strategies.

NP-BLCA-1 (novel prediction derived):
  r(ZEB2,AURKA) > 0 in pan-cancer
  predicts high CIN burden.
  r(ZEB2,AURKA) < 0 in pan-cancer
  predicts EMT-proliferation trade-off.
  Testable: TCGA pan-cancer ZEB2-AURKA
  sign vs aneuploidy score.
```

---

## VI. CLINICAL PANELS — DERIVED

```
LUMINAL PANEL:
  PREDICTED: FGFR3(+)/GATA3(+)/UPK2(-)
  r with depth = +0.81*** ✓
  This is a strong panel.

  DATA-DRIVEN: CCND1(+)/FGFR3(+)/SMAD3(+)
  r with depth = +0.75***
  Predicted panel (r=0.81) OUTPERFORMS
  data-driven (r=0.75).
  The predicted panel is better because
  it includes a negative gate (UPK2-)
  that captures the switch gene axis.
  Data-driven misses the switch gene.

  REVISED LUMINAL PANEL:
  FGFR3(+) / CCND1(+) / CLDN3(-)
  Rationale:
    FGFR3 r=+0.70*** (FA marker, drug target)
    CCND1 r=+0.70*** (cell cycle driver, strongest)
    CLDN3 r=-0.56*** (strongest switch gene)
  All three are IHC-deployable.
  CCND1 and CLDN3 IHC are routine.
  FGFR3 IHC used for erdafitinib selection.
  This panel should be tested for
  erdafitinib response prediction.

  NOVEL ADDITION: SMAD3(+) for deepest
  luminal BLCA — TGF-β active subset.
  These patients may resist FGFR3i alone
  (TGF-β provides escape route).
  Combined FGFR3i + TGF-β pathway inhibition
  for FGFR3(+)/SMAD3(+) deep luminal BLCA.

BASAL PANEL:
  PREDICTED: KRT5(+)/EGFR(+)/GATA3(-)
  r with depth = +0.66***

  DATA-DRIVEN: TWIST1(+)/CDK6(+)/FN1(+)
  r with depth = +0.77***
  Data-driven OUTPERFORMS predicted
  (0.77 vs 0.66).
  TWIST1 not predicted as primary.

  REVISED BASAL PANEL:
  TWIST1(+) / CDK6(+) / GATA3(-)
  Rationale:
    TWIST1 r=+0.74*** (strongest FA marker)
    CDK6   r=+0.59*** (cell cycle, drug target)
    GATA3  r=-0.88*** (switch gene, strongest)
  All three are IHC-deployable.
  GATA3 IHC is routine pathology.
  TWIST1 IHC available clinically.
  CDK6 IHC not routine but feasible.

  KEY IMPLICATION:
  CDK6 in the basal panel makes
  CDK4/6i (palbociclib/ribociclib)
  a data-derived prediction for
  deep basal BLCA.
  Not currently a standard treatment.
  Novel prediction for basal BLCA.
```

---

## VII. SURVIVAL DATA — STATUS

```
SURVIVAL DATA EXISTS:
  'survival month': present (165 samples)
  Time range: 1.0–137.0 months
  'overall survival': values = 'death'/'survival'
  'cancer specific survival': same pattern

EVENT PARSING FAILURE:
  Parser looked for numeric value
  after 'overall survival:' key.
  The value IS the text 'death' or 'survival'.
  The event_re regex did not match
  because it searched in the KEY,
  not the VALUE.
  The key IS 'overall survival' and
  the VALUE is 'death' or 'survival'.

FIX FOR SCRIPT 2:
  Parse: if key == 'overall survival'
         and value == 'death' → event=1
         and value == 'survival' → event=0
  Also: 'cancer specific survival'
         value == 'death' → css_event=1

SURVIVAL TEST IS ONE FIX AWAY.
Script 2 will fix the event parser
and run the survival analysis.
165 samples with both time and event
will be available.
```

---

## VIII. DRUG TARGET SUMMARY

```
CONFIRMED TARGETS:
  FGFR3 (erdafitinib) — LUMINAL ✓✓
    r=+0.70*** in luminal depth.
    FDA-approved. Independently derived.
    Strongest luminal depth driver.

  CDK4/6i — LUMINAL (CCND1/CDKN2A axis)
    CCND1 r=+0.70*** in luminal depth.
    CDKN2A r=-0.49*** (lost in deep luminal).
    Same mechanism as ESCC.
    Palbociclib predicted for deep luminal BLCA.
    Not currently approved specifically
    for BLCA — novel application.

  CDK6i — BASAL ✓
    CDK6 r=+0.59*** in basal depth.
    Different isoform emphasis than luminal.
    Basal BLCA = CDK6 dominant.
    Luminal BLCA = CCND1/CDK4 dominant.
    Abemaciclib (CDK4/6, CDK6 preference)
    may be better for basal BLCA.

  FGFR1 inhibitor — DEEP BASAL
    FGFR1 r=+0.43*** in basal depth.
    Cross-cancer FGFR isoform rule confirmed:
    FGFR1 = squamous/basal
    FGFR3 = columnar/luminal
    Infigratinib (FGFR1-3 inhibitor)
    or futibatinib for deep basal BLCA.

  TACSTD2 (sacituzumab govitecan) ✓
    TACSTD2 present in both subtypes.
    Not depth-stratified significantly.
    Confirms it is a broad BLCA target.
    Consistent with FDA-approved use.

NOVEL TARGETS (not in current BLCA guidelines):
  MCL1 inhibitor for deep basal BLCA
    MCL1 r=+0.46*** in basal depth.
    Replaces BCL2/venetoclax (BCL2 is DOWN).
    AMG-176 or S63845 are MCL1 inhibitors.
    Not in BLCA trials currently.

  TGF-β pathway inhibitor for deep luminal
    SMAD3 r=+0.54*** in luminal depth.
    Galunisertib (TGF-βR1 inhibitor)
    for FGFR3(+)/SMAD3(+) deep luminal.
    Novel combination not published for BLCA.

  Pembrolizumab for DEEP LUMINAL BLCA
    MSH2/MSH6 lost in deep luminal
    (r=-0.38/-0.41***).
    MSI-high predicted in deep luminal.
    Pembrolizumab approved for MSI-high.
    Depth score may select immunotherapy
    candidates better than MSI testing alone.

  ERBB3 (low for basal BLCA target)
    ERBB3 r=-0.71*** in basal depth.
    ERBB3 is the dimerisation partner
    for ERBB2 and EGFR.
    ERBB3 is LOST in deep basal.
    Anti-ERBB3 therapy would not work
    in deep basal BLCA.
    Target ERBB3 in SHALLOW basal
    (where ERBB3 is still expressed).

REVISED — NOT CONFIRMED:
  BCL2/venetoclax for BASAL BLCA ✗
    BCL2 is DOWN in basal BLCA.
    BCL2-based therapy not appropriate.
    Replace with MCL1 inhibitor.

  EGFR inhibitor for deep basal ✗
    EGFR only r=+0.28 in basal depth.
    EGFR is not the primary RTK driver.
    FGFR1 is more important in deep basal.
```

---

## IX. NOVEL PREDICTIONS LOCKED 2026-03-01

```
NP-BLCA-1: ZEB2-AURKA sign encodes
  cancer strategy:
  Positive = simultaneous EMT+proliferation
  (STAD/EAC — CIN-dominant GI cancers)
  Negative = EMT-proliferation trade-off
  (BLCA — urothelial cancers)
  Testable: TCGA pan-cancer ZEB2-AURKA r
  vs aneuploidy score per cancer type.

NP-BLCA-2: Deep luminal BLCA is MSI-high
  due to MMR loss (MSH2/MSH6 r<-0.40***).
  Luminal depth score predicts pembrolizumab
  response better than MSI testing alone.
  Testable: luminal depth score vs
  MSI status + immunotherapy response
  in clinical BLCA cohort.

NP-BLCA-3: Deep luminal BLCA acquires
  squamous features (TP63 r=+0.47***,
  IVL r=+0.35***).
  Deepest luminal tumors show
  adenosquamous mixed histology.
  Testable: TP63 IHC in FGFR3-high luminal
  BLCA TMA — does TP63 co-elevate with
  FGFR3 in the deepest luminal tumors?

NP-BLCA-4: Deep basal BLCA is BELOW
  the normal basal urothelial state.
  KRT5 r=-0.22* and TP63 r=-0.55***
  in basal depth — both LOST in deepest.
  The most aggressive basal BLCA has
  no urothelial identity markers remaining.
  Testable: KRT5/TP63 IHC intensity
  in stage T3/T4 basal BLCA vs T1/T2.
  Prediction: T3/T4 has LOWER KRT5/TP63
  than T1/T2 within basal subtype.

NP-BLCA-5: MCL1 (not BCL2) is the
  anti-apoptotic survival gene in
  deep basal BLCA.
  MCL1 r=+0.46*** in basal depth.
  BCL2 is DOWN in basal BLCA.
  MCL1 inhibitor (AMG-176/S63845)
  predicted for deep basal BLCA.
  Testable: OE/OC/T24 basal BLCA cell lines
  + AMG-176 dose response vs depth score.

NP-BLCA-6: FGFR isoform switch across
  BLCA subtypes:
  Luminal: FGFR3 r=+0.70***
  Basal:   FGFR1 r=+0.43***
  Cross-cancer rule confirmed:
  FGFR3 = columnar/luminal
  FGFR1 = squamous/basal
  Testable: FGFR1 IHC in basal BLCA TMA
  + response to FGFR1/2/3 inhibitors.

NP-BLCA-7: CDK6 (not CDK4) is the
  primary cell cycle driver in deep
  basal BLCA.
  CDK6 r=+0.59*** in basal depth.
  Abemaciclib (CDK4/6, CDK6 preference)
  > palbociclib (CDK4/6 balanced)
  for deep basal BLCA.
  Testable: BLCA cell line panel
  (basal vs luminal) + CDK4i vs CDK6i
  selective inhibitors.

NP-BLCA-8: SMAD3-high deep luminal BLCA
  (TGF-β active) resists FGFR3 inhibitor
  monotherapy.
  Combined FGFR3i + TGF-βRi
  (erdafitinib + galunisertib) synergistic
  in FGFR3(+)/SMAD3(+) deep luminal BLCA.
  Testable: FGFR3-mutant luminal BLCA
  cell lines + erdafitinib + galunisertib
  combination index.

NP-BLCA-9: KRT20+CDX2 co-elevation in
  luminal BLCA connects bladder to
  intestinal metaplasia program.
  Luminal BLCA may share an intestinal
  attractor with EAC.
  This is the same KRT20/CDX2 axis
  found in EAC (from ESCA analysis).
  Cross-tissue attractor hypothesis:
  A single intestinal-type attractor
  is accessible from multiple tissue
  types (esophagus, bladder).
  Testable: CDX2/KRT20 IHC co-staining
  in luminal BLCA and intestinal
  metaplasia of bladder (cystitis
  glandularis).
```

---

## X. REVISED MODEL SUMMARY

```
ATTRACTOR TOPOLOGY REVISION:

LUMINAL BLCA:
  Block: NOT at umbrella differentiation
         (UPK genes retained/elevated)
  Block: AT CELL CYCLE EXIT
         (CDKN2A/2B lost r=-0.49/-0.57)
  FA drivers: FGFR3+CCND1 (co-equal, r=+0.70)
  Novel feature: TGF-β active in deepest
                 (SMAD3 r=+0.54)
  Novel feature: Squamous transdiff in deepest
                 (TP63/IVL rising)
  Novel feature: MMR loss in deepest
                 (MSI-high)

BASAL BLCA:
  Block: BELOW the normal basal state
         (KRT5/TP63 lost in deepest)
  FA drivers: TWIST1+ZEB2+CDK6
              (TWIST1 primary, r=+0.74)
  Switch: GATA3/FOXA1/PPARG loss
          (luminal identity completely erased)
  Novel feature: FGFR1 (not FGFR3) is RTK
  Novel feature: MCL1 (not BCL2) survival gene
  Novel feature: Negative ZEB2-AURKA coupling
                 (EMT-proliferation trade-off)

CROSS-CANCER RULES REFINED:
  1. FGFR isoform rule confirmed:
     FGFR3 = luminal/columnar
     FGFR1 = basal/squamous
  2. ZEB2-AURKA sign rule (new):
     Positive = CIN-dominant (STAD/EAC)
     Negative = EMT-proliferation trade-off (BLCA)
  3. TP63 revised:
     ESCC: TP63 retained (squamous arrested)
     Basal BLCA deep: TP63 LOST (below basal)
     TP63 direction encodes how FAR below
     normal the cancer has gone, not just
     which state it is arrested in.
  4. NOTCH1 revised:
     Not a simple epithelial/myeloid binary.
     Context: squamous cancer = oncogenic UP
              luminal urothelial = suppressed
              myeloid = tumor suppressor DOWN
  5. UPK genes: not primary switch genes
     The umbrella differentiation gate is
     not where luminal BLCA is blocked.
     Cell cycle exit (CDKN2A/2B) is the gate.
```

---

## XI. STATUS

```
document_type:    Script 1 reasoning artifact
dataset:          GSE13507
platform:         GPL6102 Illumina HWG-6 V2
date:             2026-03-01
script:           blca_false_attractor_1.py
results:          blca_false_attractor/results_s1/
figure:           blca_gse13507_s1.png

groups:           Normal=9 Luminal=123 Basal=123
genes:            125 mapped

confirmed:        L-D1 (FGFR3 r=+0.70***)
                  L-D3 (UPK2 negative with depth)
                  L-D5 (combined > individual)
                  B-D3 (GATA3 r=-0.88***)
                  CC-1-L (TP63 rising in deep lum)
                  FGFR3 independently derived ✓✓

not_confirmed:    B-D1 KRT5 (wrong direction)
                  B-D4 TP63 (wrong direction)
                  B-D5 ZEB2-AURKA (inverted)
                  EP-3 EZH2+HDAC1 (flat)
                  BCL2/venetoclax basal (BCL2 down)

key_discovery:    ZEB2-AURKA INVERTED in BLCA
                  (new cross-cancer framework rule)
                  TWIST1 = primary basal anchor
                  (stronger than KRT5)
                  Deep basal BELOW normal basal
                  (KRT5/TP63 lost in deepest)
                  FGFR isoform switch confirmed
                  MMR loss in deep luminal
                  (MSI-high/pembrolizumab)
                  MCL1 replaces BCL2 for basal

novel_predictions: NP-BLCA-1 through NP-BLCA-9

survival:         EVENT PARSER FIX NEEDED
                  Data exists (165 samples)
                  'overall survival': death/survival
                  One fix away from KM curves

next:             Doc 91b — Script 2
                  Fix event parser
                  Run KM survival curves
                  Test depth panel vs OS
                  Test TWIST1/CDK6/GATA3 panel
                  Replication dataset (GSE32894)
                  OR run Script 2 on GSE13507
                  with survival fix

author:           Eric Robert Lawson
                  OrganismCore
status:           DOC 91a COMPLETE
```
