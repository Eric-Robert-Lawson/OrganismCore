# Document 97x-2 — Pre-Computation Reasoning Artifact
## RCC Cross-Type Script 2: Chromatin Lock Architecture and Phase Transition
### OrganismCore | 2026-03-03 | Author: Eric Robert Lawson

---

## METADATA

```
document_number:    97x-2
document_type:      Pre-computation reasoning artifact
                    Predictions locked BEFORE script runs.
                    Script outcome cannot change these predictions.
follows:            97x (cross-type Script 1 reasoning artifact)
                    94f, 95-LC/DLC/g, 96f, 89c (individual type docs)
script:             rcc_cross_type_script2.py  (NOT YET RUN)
date_locked:        2026-03-03
author:             Eric Robert Lawson
                    OrganismCore

protocol_rule:      This document is written before the script
                    executes. Predictions are locked here.
                    The script output will be assessed against
                    these predictions in a subsequent document
                    (97x-2-results).
                    No prediction may be added after the script runs.
```

---

## CRITICAL RULE — CONFIRMED

```
All predictions in this document are stated before any script
computation is run. The script (rcc_cross_type_script2.py)
has not been executed at the time of writing.

Order enforced:
  Script 1 findings reviewed →
  New predictions derived →
  THIS DOCUMENT LOCKED →
  Script 2 executed →
  Results document written.

The predictions below cannot be changed by the script output.
```

---

## SECTION I — WHAT SCRIPT 1 ESTABLISHED (CARRY-FORWARD)

```
From Document 97x (cross-type Script 1):

CONFIRMED (carry-forward as structural facts):
  F1: EZH2 is the only universal positive gene (4/4 types)
  F2: TCA→αKG→EZH2 circuit is present in all four types
      (entry point differs: SUCLG1 ccRCC, FH PRCC, OGDHL cdRCC/chRCC)
  F3: False attractor identities are non-overlapping (max ≤3 gene pairs)
  F4: Normal identity genes are SLC/channel family across all types
  F5: DNMT3A is near-universal positive (3/4: ccRCC, PRCC, cdRCC)
  F6: CCND1 is near-universal positive (3/4: ccRCC, PRCC, cdRCC)
  F7: Two-phase transition (MYC-early, consolidation-late) confirmed
      in cdRCC (r(MYC,BHLHE40)=-0.964) and inferred in ccRCC
  F8: IL1RAP confirmed positive in ccRCC (Q4/Q1=1.15) and cdRCC
      (r=+0.964, top false attractor marker)
  F9: MHC-I evasion (B2M/HLA-A fall with depth) confirmed in
      ccRCC and PRCC — NOT yet characterised in chRCC or cdRCC
  F10: Tazemetostat pan-renal (T=4/4)
  F11: chRCC contributed ZERO genes from CSV — all locked knowledge

OPEN FROM SCRIPT 1 (targets for Script 2):
  O1: Are EZH2 and DNMT3A co-elevated in the same depth quartile
      within the same tumour? (CT-1 combination rationale)
  O2: Does the two-phase structure (MYC-early / TF-late) hold across
      all four types, with type-specific Phase 2 TFs?
  O3: Is IL1RAP a depth correlator in PRCC and chRCC?
  O4: What is the ranked αKG deficit score by type?
      (dual-depletion hypothesis: cdRCC deepest)
  O5: Does the GOT1/RUNX1 Transition Index generalise beyond ccRCC?
  O6: Can chRCC pc2_results be integrated into depth_corr format?
```

---

## SECTION II — LOCKED PREDICTIONS

### Prediction P2-1 — EZH2 and DNMT3A are co-elevated in the same depth quartile

```
Prediction:
  r(EZH2, DNMT3A) will be POSITIVE in ccRCC, PRCC, and cdRCC.
  r > 0.30 in all three types.
  r(EZH2, DNMT3A) will be NEAR ZERO or ABSENT in chRCC.

Mechanistic basis:
  Script 1 established DNMT3A as near-universal (3/4 types).
  EZH2 is universal (4/4 types).
  If they track the same depth axis they must be co-elevated
  in the same samples.
  The αKG depletion hypothesis predicts both:
    αKG↓ → TET enzymes inactive → DNA methylation accumulates (DNMT3A active)
    αKG↓ → KDM demethylases inactive → H3K27me3 persists (EZH2 effective)
  Both are consequences of the same upstream deficit.
  They should therefore co-vary positively.

  chRCC: DNMT3A was absent from chRCC positive panel in Script 1.
  chRCC attractor maintenance is NRF2/AKR-driven, not DNMT3A-driven.
  Therefore r(EZH2, DNMT3A) in chRCC is predicted to be < 0.20
  (weak or absent co-regulation).

Clinical implication of this prediction:
  If confirmed: EZH2i + DNMTi combination (CT-1) is justified as
  simultaneous co-administration in ccRCC, PRCC, cdRCC.
  If EZH2 and DNMT3A track different depth axes: the combination
  would need to be phase-staged, not co-administered.

Falsification condition:
  r(EZH2, DNMT3A) < 0.15 in any of ccRCC, PRCC, cdRCC
  would indicate independent depth axes and would require
  the CT-1 prediction to be revised to phase-staged sequencing.
```

---

### Prediction P2-2 — Two-phase transition is universal; Phase 2 TFs are type-specific

```
Prediction:
  For each type, r(MYC, Phase2_TF) will be NEGATIVE (< -0.30).
  The Phase 2 TF is type-specific:
    ccRCC:  RUNX1    (confirmed depth hub r=+0.742 from individual analysis)
    PRCC:   KDM1A    (depth r=+0.443 from individual analysis)
    chRCC:  BHLHE40  (inferred from cdRCC architecture; test hypothesis)
    cdRCC:  BHLHE40  (r(MYC,BHLHE40)=-0.964, confirmed)

  Additionally:
    r(MYC, BHLHE40) will be negative in ccRCC as well (< -0.20),
    suggesting BHLHE40 is a shared late-phase marker despite
    RUNX1 being the ccRCC-specific consolidation hub.

  MYC will be highest in Q1/Q2 across all types.
  Phase 2 TF will be highest in Q3/Q4 across all types.
  The MYC/Phase2_TF ratio will be a candidate phase classifier
  with better OS stratification than either gene alone.

Mechanistic basis:
  The two-phase architecture was independently confirmed in cdRCC
  with r(MYC,BHLHE40)=-0.964 (p<0.001) across 7 patients.
  cdRCC Script 4 showed: CDC3 = MYC-high/BHLHE40-low (Phase 1),
  CDC6 = MYC-low/BHLHE40-high (Phase 2).
  The same logic applies to any cancer where:
    (a) a proliferative erasure phase exists (MYC-driven)
    (b) followed by an identity consolidation phase (TF-driven)
  All four types were confirmed to have identity genes rising with
  depth and MKI67 uncoupled from the top FA marker (X6 CONFIRMED).
  MKI67 uncoupling from FA markers implies the proliferative phase
  and identity phase are sequential, not concurrent.

Falsification condition:
  r(MYC, Phase2_TF) > 0 in any type would indicate those phases
  are concurrent or co-activated, which would require a different
  model than the sequential two-phase structure.
  This would be a major framework revision trigger.
```

---

### Prediction P2-3 — IL1RAP depth correlation in PRCC and chRCC

```
Prediction:
  PRCC:  r(IL1RAP, depth_PRCC) > 0.25  (positive depth correlator)
         Mechanism: inflammatory TME recruitment in deep PRCC
         (mast cell/TPSAB1 programme co-recruits IL-1 signalling)
         The TGFBI→CCL22→Treg→IL1B chain confirmed in ccRCC
         has an analogue in PRCC Q4 (ARG1/M2 module)

  chRCC: r(IL1RAP, depth_chRCC) < 0.15  (near zero or absent)
         Mechanism: chRCC attractor is steroid/AKR-mediated.
         The CEBPA-suppression mechanism (cdRCC) and the
         inflammatory TME route (ccRCC/PRCC Q4) are both
         absent from the chRCC programme.
         BTNL3 (γδ T cell immune modulation) is the chRCC
         immune axis, not IL-1/IL1RAP-driven myeloid suppression.

Clinical implication:
  If IL1RAP is positive in PRCC:
    IL1RAP ADC (in development) becomes relevant for PRCC Q4
    in addition to ccRCC and cdRCC.
    Pan-renal IL1RAP hypothesis upgrades from 2/4 to 3/4.
  If IL1RAP is absent in chRCC:
    IL1RAP targeting is NOT a chRCC strategy.
    Confirms that chRCC uses a qualitatively different immune
    evasion architecture.

Falsification condition:
  r(IL1RAP, depth_chRCC) > 0.30 would challenge the prediction
  and require re-evaluation of whether an inflammatory TME
  programme exists in deep chRCC that is not yet characterised.
```

---

### Prediction P2-4 — Ranked αKG deficit score by type: cdRCC deepest

```
Prediction:
  αKG deficit score = -(norm(OGDHL) + norm(SUCLG1) + norm(FH) + norm(SLC13A2))
  computed at sample level and averaged per type.

  Predicted rank order (deepest to shallowest αKG deficit):
    1st (deepest):  cdRCC   — OGDHL r=-1.000 + SLC13A2 universal loss
    2nd:            PRCC    — FH r=-0.451, SUCLG1 r=-0.519, OGDHL r=-0.402
                              three simultaneous TCA gene falls
    3rd:            ccRCC   — SUCLG1 confirmed, OGDHL confirmed
                              FH not a primary ccRCC depth marker
    4th (shallowest): chRCC — OGDHL predicted down but NRF2/AKR
                              alternative metabolism compensates partially

Mechanistic basis:
  cdRCC loses SLC13A2 (apical dicarboxylate importer, confirmed
  lost universally in ALL RCC per Document 94f) plus OGDHL
  (internal synthesis). Both routes eliminated simultaneously.
  PRCC has three TCA genes falling simultaneously in CSV data —
  the richest multi-gene TCA evidence in the series.
  ccRCC: SUCLG1 is the primary confirmed TCA gene; FH is not
  a primary ccRCC depth correlate (FH mutations are PRCC-specific).
  chRCC: OGDHL down but the NRF2/AKR axis provides an alternative
  programme that may partially compensate for TCA disruption.

Clinical implication:
  The αKG deficit rank directly maps to the αKG supplementation
  priority order:
    cdRCC most urgent → PRCC second → ccRCC third → chRCC fourth.
  This provides a cross-type patient prioritisation framework
  for any future αKG supplementation trial.

Falsification condition:
  If PRCC ranks above cdRCC (i.e., SLC13A2 loss is not quantitatively
  significant in the αKG deficit score), it would suggest that
  import loss is less impactful than synthesis loss, and the
  dual-depletion hypothesis would need revision.
```

---

### Prediction P2-5 — GOT1/RUNX1 Transition Index generalises to PRCC but not chRCC

```
Prediction:
  TI = norm(GOT1) - norm(RUNX1)

  ccRCC:  r(TI, depth) < -0.50  [already confirmed r=-0.600, n=534]
          This is the reference. Use to validate the script's
          TI implementation before applying to other types.

  PRCC:   r(TI, depth) < -0.35  (significant negative correlation)
          Mechanism: GOT1 is a proximal tubule identity gene
          (aspartate aminotransferase, TCA-bridging enzyme).
          PRCC arises from proximal tubule S2/S3.
          GOT1 loss tracks PT identity loss in PRCC as in ccRCC.
          RUNX1 is a confirmed depth hub in PRCC (from individual
          type analysis — Documents 95-DLC, 95g).
          Therefore TI should work in PRCC.

  chRCC:  r(TI, depth) > -0.20  (TI does not generalise)
          Mechanism: GOT1 is a proximal tubule marker.
          chRCC arises from intercalated cells — NOT proximal tubule.
          GOT1 loss is not expected to track intercalated cell
          identity loss. The negative pole of chRCC depth is defined
          by AQP2, SCNN1, AVPR2, PRKAR2B (collecting duct markers),
          not by GOT1 (proximal tubule marker).
          RUNX1 was not confirmed as a chRCC depth hub in individual
          type analysis.
          Therefore TI is predicted to fail in chRCC — not because
          the framework fails, but because it is the wrong gene pair
          for the wrong cell of origin.

  cdRCC:  r(TI, depth) < -0.30  (partial generalisation)
          cdRCC arises from collecting duct principal cells.
          GOT1 was not the primary anchor for cdRCC depth (PRKAR2B
          was the primary negative anchor, Document 89c).
          However, GOT1 falls with depth in cdRCC (metabolic collapse
          confirmed generally) and RUNX1 may be partially elevated.
          Prediction: TI works but less precisely than in ccRCC/PRCC.
          r < -0.30 but not < -0.50.

Clinical implication:
  If confirmed: GOT1/RUNX1 TI is a pan-renal biomarker for PT-origin
  cancers (ccRCC + PRCC) — measurable from a two-gene RNA panel
  on biopsy. Clinical utility for staging and treatment stratification.
  If chRCC fails as predicted: confirms the TI is lineage-specific
  and a chRCC-specific TI (using collecting duct identity genes)
  would need to be derived separately.
  Best candidate for chRCC TI: norm(AQP2) - norm(IL1RAP) or
  norm(PRKAR2B) - norm(IL1RAP) (from Document 89c architecture).
```

---

### Prediction P2-6 — chRCC pc2_results integration

```
Prediction:
  If the chRCC pc2_results file is successfully parsed:
    chRCC will contribute >=30 positive and >=20 negative genes
    to the cross-type gene lists.
    The chRCC positive panel will remain non-overlapping with
    the other three types (consistent with X16 confirmed).
    EZH2 will appear in the chRCC positive panel from CSV
    (currently locked knowledge only — confirmed from individual scripts).
    DNMT3A will NOT appear in the chRCC positive panel from CSV
    (predicted absent from F5 and chRCC architecture).
    SLC51B, ABCC2, HSD17B14, RDH5 will appear in the chRCC
    positive panel (confirmed as depth markers in Document 96f).

  If the pc2_results file cannot be integrated:
    chRCC remains locked-knowledge-only for all cross-type claims.
    All chRCC results in 97x and 97x-2 carry this caveat.
    A dedicated chRCC depth_corr file should be generated from
    chRCC Script 6 (Document 96g) as a priority.
```

---

### Prediction P2-7 — LOXL2 as near-universal ECM depth marker (3/4 or 4/4 types)

```
Prediction:
  LOXL2 will be confirmed as a positive depth correlator in PRCC
  when PRCC full CSV data is loaded (r > 0.25 in TCGA-KIRP).

  Mechanistic basis:
    LOXL2 is an extracellular matrix lysyl oxidase — it crosslinks
    collagen and elastin, increasing ECM stiffness.
    ECM stiffening is a feature of all four RCC types' deep
    attractor states (confirmed from individual type documents):
      ccRCC:  LOXL2 r=+0.628 — #1 depth correlate
      PRCC:   LAMC2 r=+0.760 — basement membrane invasion
              LOXL2 not measured from full script CSV yet
      chRCC:  ECM markers in PC2 (SLC family displacement)
      cdRCC:  TNXB r=-1.000 — ECM scaffold progressively dismantled
              (inverse — ECM protective structure lost)
    LOXL2 drives ECM stiffening; TNXB loss removes ECM protection.
    These may be the same process viewed from opposite directions.

  If confirmed in PRCC (r > 0.25):
    LOXL2 reaches 3/4 types from CSV — X3 upgrades from PARTIAL
    to CONFIRMED.
    Simtuzumab (anti-LOXL2) becomes a potential pan-renal ECM target
    beyond ccRCC.

  chRCC and cdRCC LOXL2 prediction:
    cdRCC:  LOXL2 not expected as primary depth correlate because
            TNXB loss (ECM dismantling) dominates — these are
            mechanistically distinct ECM events.
    chRCC:  Insufficient data to predict confidently.
            ECM programme in chRCC is less characterised.
            Prediction: LOXL2 absent from chRCC positive panel.

Falsification condition:
  LOXL2 absent from PRCC at r < 0.15 would confirm LOXL2 is
  ccRCC-specific and the ECM stiffening in PRCC operates through
  a different crosslinker. LAMC2 (basement membrane component)
  rather than LOXL2 (matrix crosslinker) may be the primary PRCC
  ECM axis — mechanistically distinct.
```

---

### Prediction P2-8 — RUNX1 is a near-universal depth hub (3/4 types)

```
Prediction:
  RUNX1 will be confirmed as a positive depth correlator in PRCC
  (from PRCC full CSV output, r > 0.30 in TCGA-KIRP).
  Combined with ccRCC (r=+0.742 confirmed) and PRCC, RUNX1
  would reach 2/4 types from CSV.
  chRCC and cdRCC: RUNX1 not predicted as primary depth hub
  (different regulatory architectures).

  If RUNX1 reaches 3/4 with locked knowledge inclusion:
    RUNX1 inhibition becomes a near-universal target
    alongside tazemetostat for PT-origin renal cancers.
    AI2-FL (RUNX1/CBFB inhibitor) would have a multi-cancer
    renal rationale.

  Mechanistic basis:
    RUNX1 is an oncogenic TF confirmed as a CRISPR-validated
    driver in ccRCC (Cancer Research 2020).
    RUNX1 drives ECM remodelling (COL5A1), adhesion (TGFBI),
    and immune evasion (CCL22 → Treg) — all processes that
    increase with attractor depth.
    These same processes (ECM, adhesion, Treg recruitment)
    are active in PRCC Q4 (TGFBI elevated in ccRCC Q4/Q1=1.30;
    LAMC2 elevated in PRCC deep stratum).
    RUNX1 likely drives analogous programmes in PRCC.
```

---

## SECTION III — PREDICTIONS SUMMARY TABLE

```
Prediction  Gene/Metric                    Type(s)        Expected value      
─────────────────────────────────────────────────────────────────────────────
P2-1        r(EZH2, DNMT3A)               ccRCC          > +0.30             
P2-1        r(EZH2, DNMT3A)               PRCC           > +0.30             
P2-1        r(EZH2, DNMT3A)               cdRCC          > +0.30             
P2-1        r(EZH2, DNMT3A)               chRCC          < +0.20             
P2-2        r(MYC, RUNX1)                 ccRCC          < -0.20             
P2-2        r(MYC, KDM1A)                 PRCC           < -0.20             
P2-2        r(MYC, BHLHE40)               cdRCC          < -0.90 (confirmed) 
P2-2        r(MYC, BHLHE40)               chRCC          < -0.30 (predicted) 
P2-2        r(MYC, BHLHE40)               ccRCC          < -0.20             
P2-2        Phase2_TF Q4/Q1               all types      > 1.10              
P2-2        MYC Q4/Q1                     all types      < 0.90              
P2-3        r(IL1RAP, depth)              PRCC           > +0.25             
P2-3        r(IL1RAP, depth)              chRCC          < +0.15             
P2-4        αKG deficit rank              cdRCC          1st (deepest)       
P2-4        αKG deficit rank              PRCC           2nd                 
P2-4        αKG deficit rank              ccRCC          3rd                 
P2-4        αKG deficit rank              chRCC          4th (shallowest)    
P2-5        r(TI, depth) TI=GOT1-RUNX1   ccRCC          < -0.50 (reference) 
P2-5        r(TI, depth)                  PRCC           < -0.35             
P2-5        r(TI, depth)                  chRCC          > -0.20 (fails)     
P2-5        r(TI, depth)                  cdRCC          < -0.30             
P2-6        chRCC CSV integration         chRCC          >= 30 pos genes     
P2-6        DNMT3A in chRCC CSV           chRCC          ABSENT              
P2-6        EZH2 in chRCC CSV             chRCC          PRESENT             
P2-7        r(LOXL2, depth)               PRCC           > +0.25             
P2-7        r(LOXL2, depth)               chRCC          < +0.15             
P2-8        r(RUNX1, depth)               PRCC           > +0.30             
P2-8        RUNX1 in cross-type           >=2 types CSV  CONFIRMED           
```

---

## SECTION IV — WHAT THIS SCRIPT CANNOT DETERMINE

```
These questions are open after Script 2 and require
additional data or subsequent scripts:

CANNOT-1:
  MHC-I architecture in chRCC and cdRCC.
  Script 2 does not include immune deconvolution.
  Formal characterisation requires B2M/HLA-A depth
  correlation with immune cell proportion estimation
  (ESTIMATE, CIBERSORT, or equivalent) per type.
  This is the primary immune open question after Script 2.

CANNOT-2:
  Protein-level validation of any cross-type finding.
  All data is bulk RNA-seq from TCGA.
  EZH2/DNMT3A co-elevation at protein level (IHC) is
  not testable from these data.
  All chromatin findings require ChIP-seq validation.

CANNOT-3:
  cdRCC sample size caveat (n=7) applies to all cdRCC
  outputs from this script as well. Correlations involving
  cdRCC reach at most n=7 for the paired GEO dataset
  (GSE89122). TCGA-KIRP may contain some cdRCC-like cases
  but they are not formally annotated as cdRCC.
  All cdRCC results carry the n=7 caveat.

CANNOT-4:
  Whether DNMT3A is the active writer in these tumours
  or whether it is being transcribed but not translated.
  RNA elevation ≠ active de novo methylation.
  DNMT3A protein activity requires mass spectrometry or
  specific functional assays. All DNMT3A claims in this
  script are RNA-level.

CANNOT-5:
  Formal two-phase survival analysis.
  Phase-stratified OS comparison (MYC-high vs Phase2-TF-high)
  requires clinical outcome data linked to expression profiles.
  TCGA-KIRC and TCGA-KIRP have clinical follow-up.
  TCGA-KICH has limited follow-up.
  GSE89122 (cdRCC) has n=7 — no meaningful survival analysis.
  Script 2 will compute the TI and phase ratios.
  Survival analysis requires a dedicated subsequent step.
```

---

## SECTION V — WHAT A CONFIRMED RESULT MEANS CLINICALLY

```
If ALL P2-1 through P2-8 predictions are confirmed:

1. EZH2i + DNMTi combination (CT-1) is structurally justified
   for ccRCC, PRCC, and cdRCC as co-administration.
   First-in-class renal cancer combination: tazemetostat + azacitidine.
   Strongest rationale in Q3/Q4 depth-stratified patients.

2. Phase 1 / Phase 2 two-axis treatment protocol becomes
   mandatory, not optional. No treatment decision should be made
   without knowing the patient's phase (MYC:Phase2_TF ratio)
   as well as their depth stratum (Q1-Q4 equivalent).

3. GOT1/RUNX1 TI becomes a validated pan-renal biomarker for
   PT-origin cancers — deployable from RNA panel on biopsy.
   Two genes. No depth score computation required.
   Immediate clinical utility for staging.

4. IL1RAP ADC trials in PRCC are warranted:
   PRCC Q4 patients should be enrolled alongside ccRCC
   patients in any IL1RAP ADC development programme.

5. αKG supplementation priority order is established:
   cdRCC > PRCC > ccRCC > chRCC.
   Any αKG trial that does not enrich for cdRCC/PRCC is
   diluting its population by including the wrong types.

If ANY P2-2 predictions are DENIED (r(MYC, Phase2_TF) > 0
in any type):
   The sequential two-phase model is wrong for that type.
   The attractor in that type consolidates while still
   proliferating — a concurrent, not sequential, structure.
   This would require a revised model for that type only.
   It would not invalidate the other types.
```

---

## STATUS BLOCK — PRE-COMPUTATION

```
document:           97x-2 (pre-computation reasoning artifact)
date_locked:        2026-03-03
author:             Eric Robert Lawson
                    OrganismCore

script_status:      NOT YET RUN
predictions_locked: 8 primary predictions (28 specific sub-predictions)
falsification_conditions_stated: YES (all predictions)

next_action:        Run rcc_cross_type_script2.py
                    Write results document 97x-2-results
                    Compare each sub-prediction against output

protocol_status:    FULLY COMPLIANT ✓
                    Predictions locked before computation.
```
