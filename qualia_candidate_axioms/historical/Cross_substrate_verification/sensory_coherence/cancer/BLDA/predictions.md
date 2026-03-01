Locked.

---

## BLCA — Pre-Analysis Prediction Block
### All predictions locked before any data
### Date: 2026-03-01 | Doc 91a prep

```
BIOLOGICAL FRAMEWORK:

Normal urothelium hierarchy:
  Basal (KRT5/KRT14/TP63)
    ↓
  Intermediate (KRT7/KRT19/CDH1)
    ↓
  Luminal/Umbrella (GATA3/FOXA1/
    UPK1B/UPK2/UPK3A)

Two attractor states in BLCA:
  BASAL-BLCA: stuck at basal state
    Cannot commit to luminal identity
    KRT5/KRT14/TP63/EGFR high
    GATA3/FOXA1/UPKs low
    More aggressive, worse prognosis
    Squamous features common

  LUMINAL-BLCA: stuck at intermediate
    Cannot complete umbrella terminal
    differentiation
    GATA3/FOXA1/FGFR3/ERBB2/CDH1 high
    KRT5/TP63 low
    Less aggressive, better prognosis
    FGFR3 mutations common
```

---

## SWITCH GENE PREDICTIONS

```
LUMINAL-BLCA switch genes
(DOWN = execution block):
  UPK1B  — uroplakin 1B
           terminal umbrella marker
           PREDICTED: DOWN in luminal BLCA
           vs normal urothelium
           The IVL equivalent for bladder.
  UPK2   — uroplakin 2
           PREDICTED: DOWN in luminal BLCA
  UPK3A  — uroplakin 3A
           PREDICTED: DOWN in luminal BLCA
  CLDN3  — claudin 3
           tight junction — terminal diff
           PREDICTED: DOWN in deep luminal

BASAL-BLCA switch genes
(DOWN = execution block):
  GATA3  — luminal identity TF
           PREDICTED: DOWN in basal BLCA
           Cannot commit to luminal fate
  FOXA1  — luminal pioneer TF
           PREDICTED: DOWN in basal BLCA
  CDH1   — epithelial junction
           PREDICTED: DOWN in basal BLCA
           Same as EAC — loss of cohesion

NOTE ON TP63:
  TP63 appeared in LUAD extraction.
  In ESCA: TP63 elevated in ESCC
  (squamous identity retained).
  In BLCA basal: TP63 predicted UP
  (basal identity retained —
   cannot exit basal state).
  Cross-cancer test:
  TP63 direction = always UP in
  the subtype that retains squamous/
  basal identity.
  PREDICTION: TP63 UP in basal-BLCA,
  DOWN or flat in luminal-BLCA.
  This will confirm the cross-cancer
  rule established in ESCA/LUAD.
```

---

## FALSE ATTRACTOR GENE PREDICTIONS

```
LUMINAL-BLCA FA genes
(UP = attractor markers):
  FGFR3  — PREDICTED: UP ***
           Most common luminal oncogene.
           FGFR3 mutation/overexpression
           in ~75% luminal BLCA.
           Framework should derive
           erdafitinib independently.
           If confirmed = validation. ✓
  ERBB2  — PREDICTED: UP
           HER2 amplification in luminal.
           Not as common as FGFR3 but
           present in luminal subtype.
  CCND1  — PREDICTED: UP
           Cyclin D1 — FGFR3 downstream.
           Cell cycle driver in luminal.
  CDH1   — PREDICTED: UP in luminal
           (switch gene in basal —
            directionally opposite
            across subtypes)
  GATA3  — PREDICTED: UP in luminal
           (switch gene when lost
            in basal — FA marker
            in luminal context)
  FOXA1  — PREDICTED: UP in luminal
  PPARG  — PREDICTED: UP in luminal
           Nuclear receptor — luminal
           differentiation driver.
           PPARG pathway active in
           luminal BLCA.

BASAL-BLCA FA genes
(UP = attractor markers):
  KRT5   — PREDICTED: UP ***
           Primary basal keratin.
           Should be strongest signal.
  KRT14  — PREDICTED: UP ***
           Basal keratin pair with KRT5.
  EGFR   — PREDICTED: UP
           Basal BLCA oncogene.
           Same as ESCC — squamous/basal
           cancers tend to overexpress EGFR.
  MYC    — PREDICTED: UP
           Common across basal cancers.
  CD44   — PREDICTED: UP
           Basal/stem cell marker.
           Cancer stem cell identity
           in basal BLCA.
  S100A8 — PREDICTED: UP
           Inflammatory/basal marker.
  VIM    — PREDICTED: UP
           Mesenchymal — basal BLCA
           has EMT features.
  ZEB1   — PREDICTED: UP in basal
           REVISED FROM ESCA LESSON:
           ZEB1 in squamous/basal context
           = identity retainer.
           Basal BLCA retains ZEB1.
           BUT — ESCA taught us ZEB1
           near detection floor in
           some platforms. Flag for
           platform effect.
```

---

## DEPTH DRIVER PREDICTIONS

```
LUMINAL DEPTH DRIVERS:
  L-D1: FGFR3 r > +0.50 with
        luminal depth
  L-D2: PPARG r > +0.40 with
        luminal depth
  L-D3: UPK genes NEGATIVE with
        luminal depth
        (deeper = more blocked =
         less uroplakin expression)
  L-D4: CDKN1A (p21) r < -0.40
        with luminal depth
        (same as ESCC — p21 loss
         in deeply stuck cells)
  L-D5: Combined FGFR3+CCND1 score
        outperforms FGFR3 alone

BASAL DEPTH DRIVERS:
  B-D1: KRT5 r > +0.60 with
        basal depth
  B-D2: EGFR r > +0.40 with
        basal depth
  B-D3: GATA3 r < -0.50 with
        basal depth
        (deeper basal = less GATA3)
  B-D4: TP63 r > +0.50 with
        basal depth
        Cross-cancer TP63 test.
  B-D5: ZEB2-AURKA coupling present
        in basal BLCA
        r > 0.50 (between STAD 0.99
        and EAC 0.47 — basal BLCA
        has moderate-high CIN)
```

---

## EPIGENETIC PREDICTIONS

```
From ESCA learning:

EP-1: EZH2 elevated in deep BLCA
      (both subtypes)
      EZH2 is a pan-cancer depth
      driver. Confirmed in EAC.
      Predict same in BLCA.

EP-2: HDAC1 elevated in deep BLCA
      (luminal subtype specifically)
      HDAC1 co-elevated with EZH2
      in deeply stuck luminal BLCA.

EP-3: Combined EZH2+HDAC1 outperforms
      either alone in BLCA
      (replication of ESCA S2-4)

EP-4: KDM6A (UTX) DOWN in deep BLCA
      KDM6A is the most commonly
      mutated epigenetic gene in BLCA
      (~25% mutation rate, highest
       of any cancer type).
      KDM6A demethylates H3K27me3
      (opposes EZH2).
      PREDICTED: KDM6A r < -0.40
      with depth in BLCA.
      This would explain why EZH2
      locks the attractor in BLCA —
      KDM6A is lost so H3K27me3
      cannot be removed.
      KDM6A loss + EZH2 up =
      irreversible epigenetic lock.

EP-5: DNMT3A elevated in deep basal
      DNA methylation adds to
      epigenetic lock in basal BLCA.
```

---

## WNT PATHWAY PREDICTIONS

```
From ESCA learning (APC paradox):

W-1: APC mRNA suppressed in deep
     luminal BLCA (same as EAC)
W-2: CTNNB1 mRNA low but pathway
     active (same APC-loss paradox)
W-3: AXIN2 trending positive in
     deep luminal BLCA (Wnt feedback)
     Same as EAC finding.
W-4: TCF7L2 flat or down despite
     AXIN2 up — split Wnt signal.

NOTE: APC mutations are RARE in BLCA
(unlike colorectal cancer).
APC loss in BLCA likely allelic
loss (5q deletion) not mutation.
Same mechanism as EAC.
```

---

## DRUG TARGET PREDICTIONS
### All stated before data

```
LUMINAL-BLCA DRUG TARGETS:
  1. Erdafitinib (FGFR3 inhibitor)
     FDA-APPROVED for FGFR3-altered BLCA.
     FRAMEWORK PREDICTION: FGFR3 UP
     in luminal attractor.
     If confirmed = independent
     derivation of approved drug. ✓✓
     Expected result.

  2. Trastuzumab/pertuzumab (HER2)
     ERBB2 amplification in luminal.
     Parallel event (as in EAC) or
     depth-correlated?
     PREDICTION: ERBB2 partially
     depth-correlated in luminal BLCA
     (unlike EAC where r=+0.08).
     Luminal BLCA has higher ERBB2
     dependence than EAC.

  3. Palbociclib (CDK4/6i)
     CCND1 elevated in luminal.
     CDKN2A lost in deep luminal.
     CDK4/6 inhibitor may work
     in luminal BLCA same as ESCC.
     PREDICTION: CCND1 r > +0.40
     and CDKN2A r < -0.40 in
     luminal depth.

  4. EZH2i + HDACi (novel)
     Replication of ESCA novel
     combination.
     PREDICTION: Combined score
     r > 0.55 in luminal depth.
     If confirmed = second cancer
     where this combination is
     geometrically derived.
     Strengthens the EAC finding.

BASAL-BLCA DRUG TARGETS:
  1. EGFR inhibitor
     EGFR UP in basal BLCA.
     Same as ESCC (squamous/basal).
     Cetuximab or erlotinib.
     Less evidence than in ESCC
     but geometry predicts it.

  2. Sacituzumab govitecan
     (anti-TROP2/TACSTD2)
     FDA-approved for BLCA.
     TROP2 is expressed in basal BLCA.
     PREDICTION: TACSTD2 elevated
     in basal vs luminal BLCA.
     If confirmed = second approved
     drug derived independently.

  3. Enfortumab vedotin
     (anti-Nectin4/PVRL4)
     FDA-approved for BLCA.
     PVRL4 expressed in urothelial.
     PREDICTION: PVRL4 elevated in
     luminal BLCA (luminal identity
     marker).
     Test both subtypes.

  4. Pembrolizumab (anti-PD1)
     CD274 (PD-L1) elevated in
     basal BLCA (immune-excluded
     basal subtype).
     PREDICTION: CD274 r > +0.30
     with basal depth.

  5. Venetoclax (BCL2i)
     From ESCA ZEB2-BCL2 finding:
     ZEB2-high cancers have elevated
     BCL2.
     If ZEB2-BCL2 coupling confirmed
     in basal BLCA, venetoclax
     becomes a predicted target.
     NOVEL — not in current BLCA
     guidelines.
```

---

## CROSS-CANCER TESTS IN BLCA

```
These are direct tests of rules
derived from prior cancers:

CC-1: TP63 UP in basal-BLCA
      (LUAD + ESCA rule: TP63 marks
       squamous/basal identity retention)

CC-2: ZEB2-AURKA r between 0.47 (EAC)
      and 0.99 (STAD) in basal-BLCA
      (CIN-graded coupling hypothesis)
      Basal BLCA has moderate-high CIN.
      Prediction: r = 0.55–0.75.

CC-3: KDM6A DOWN in deep BLCA
      Most mutated epigenetic gene
      in BLCA. Framework should
      detect this from expression
      even without mutation data.

CC-4: CDX2 circuit test
      CDX2 is NOT a BLCA gene.
      Bladder is urothelial not
      intestinal lineage.
      CDX2 should be ABSENT or flat.
      If CDX2 is elevated in any
      BLCA subtype → unexpected finding
      requiring explanation.

CC-5: NOTCH1 direction test
      In ESCC: oncogenic (UP).
      In myeloid: tumor suppressor (DOWN).
      In BLCA: predicted UP
      (epithelial cancer context —
       same rule as ESCC).
      BLCA NOTCH1 direction will
      confirm or challenge the
      epithelial vs myeloid rule.
```

---

## CLINICAL PANEL PREDICTION
### Stated before data

```
LUMINAL PANEL (predicted):
  FGFR3(+) / GATA3(+) / UPK2(-)
  Rationale:
    FGFR3 = depth driver (FA marker)
    GATA3 = luminal identity (FA marker)
    UPK2  = terminal diff gate
            (switch gene — lost in
             deeply stuck luminal)
  All three are IHC-deployable.
  GATA3 and UPK2 already used
  clinically to confirm urothelial
  origin.
  FGFR3 IHC used to guide
  erdafitinib selection.
  This panel is clinically deployable
  immediately if depth prediction
  holds.

BASAL PANEL (predicted):
  KRT5(+) / EGFR(+) / GATA3(-)
  Rationale:
    KRT5 = basal identity (FA marker)
    EGFR = basal oncogene (FA marker)
    GATA3 = luminal TF
             (switch gene — lost in
              deeply stuck basal)
  All three are standard IHC.
  KRT5 already used to classify
  basal BLCA in pathology.
  Panel adds EGFR and GATA3 to
  quantify depth within basal subtype.

CROSS-SUBTYPE SEPARATOR:
  GATA3 alone separates luminal
  from basal in BLCA.
  KRT5 alone also separates.
  The question is whether depth
  WITHIN each subtype can be
  captured.
```

---

## DATASET SELECTION

```
RECOMMENDED PRIMARY DATASET:
  GSE13507
  165 BLCA + 10 normal urothelium
  Platform: GPL6102 Illumina HWG-6 V2
  SAME PLATFORM AS GSE13898 (ESCA S3)
  Probe map already built. ✓
  Survival data: YES (OS available)
  Both subtypes present.
  This solves the survival problem
  from ESCA immediately.

BACKUP / VALIDATION:
  GSE32894
  224 BLCA samples
  Survival data available
  Larger cohort for panel validation

  TCGA-BLCA
  408 samples + mutation + CNV
  Tests CC-2 (ZEB2-AURKA + CIN)
  Tests NP-ESCA-10 cross-cancer
  Tests NOTCH1 mutation + depth

RECOMMENDATION:
  Script 1: GSE13507
  Same GPL6102 platform — reuse
  probe map from ESCA Script 3.
  Immediate efficiency gain.
  Survival data present — no
  deferral needed.
```

---

## WHAT SUCCESS LOOKS LIKE

```
MINIMUM CONFIRMATION BAR:
  FGFR3 UP in luminal BLCA **
  KRT5 UP in basal BLCA **
  GATA3 DOWN in basal BLCA **
  UPK genes DOWN in luminal BLCA *
  KDM6A DOWN in deep BLCA *
  TP63 UP in basal, flat in luminal
  Survival panel significant in
  at least one subtype

NOVEL IF CONFIRMED:
  EZH2+HDAC1 combined in BLCA
  (second cancer validation)
  ZEB2-BCL2 in basal BLCA
  (venetoclax target)
  KDM6A loss explaining EZH2 lock
  ZEB2-AURKA CIN gradient confirmed
  Barrett's-equivalent in BLCA
  (which state is the fork point?)
```

---

Ready to write Script 1 (Doc 91a). Say the word.
