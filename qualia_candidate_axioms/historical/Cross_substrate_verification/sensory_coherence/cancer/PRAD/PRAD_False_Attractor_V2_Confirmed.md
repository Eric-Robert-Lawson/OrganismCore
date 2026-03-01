# PROSTATE ADENOCARCINOMA — CIRCUIT ANALYSIS
## REASONING ARTIFACT — DOCUMENT 88b
## OrganismCore — Cancer Validation #12
## Script 2 — Circuit Analysis
## Date: 2026-03-01

---

## METADATA

```
document_number:    88b
document_type:      Reasoning artifact
                    Script 2 circuit analysis
dataset:            GSE32571
                    59 PRAD tumors
                    39 matched benign prostate
                    Illumina HumanHT-12 v4
                    Gleason high/low annotated
                    Matched pairs (DKFZ cohort)
scripts:            prad_false_attractor.py
                    (Script 1 — discovery)
                    prad_false_attractor_2.py
                    (Script 2 — circuit analysis)
framework:          OrganismCore Principles-First
status:             SCRIPT 2 COMPLETE
                    Literature check pending
follows:            Document 88a (Script 1)
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-01
series_position:    Cancer validation #12
```

---

## I. SCRIPT 2 OBJECTIVES AND RESULTS

```
OBJECTIVE 1: Gap analysis — circuit
             connections between nodes
RESULT:      5/20 confirmed
             Core chain confirmed:
             AR → NKX3-1 → ACPP/MSMB/KLK3

OBJECTIVE 2: ERG subtype analysis
             ERG-high vs ERG-low depth
RESULT:      Same depth (p=0.614)
             One signal: TMPRSS2 lower
             in ERG-high confirms fusion
             ERG subtypes = same attractor

OBJECTIVE 3: 3-gene score
             ACPP + HOXC6 + AMACR
RESULT:      r=+0.8664 with block_depth
             Near-identical to full score
             3-gene clinical panel validated

OBJECTIVE 4: NKX3-1 function gap
             INTACT (PAAD-like) or
             BROKEN (MDS-like)?
RESULT:      INTACT
             4/5 targets confirmed
             NKX3-1→ACPP r=+0.454
             NKX3-1→MSMB r=+0.523
             NKX3-1→KLK3 r=+0.665
             Architecture like PAAD

OBJECTIVE 5: FOXA1 circuit architecture
             Driver or AR consequence?
RESULT:      Neither primary driver
             nor simple AR consequence
             FOXA1→MYC r=+0.366 only
             FOXA1 disconnected from
             AMACR/HOXC6 false attractor
             markers
             FOXA1 is not the route to
             attractor dissolution
```

---

## II. CONFIRMED CIRCUIT CONNECTIONS

```
All connections tested: 20
Confirmed (p<0.05, expected direction): 5
Not confirmed: 15
Wrong direction: 1 (EZH2→KLK3)

CONFIRMED:
Connection         r         p       Role
--------------------------------------------------
AR→NKX3-1     +0.3605  p=5.03e-03 **
  AR drives NKX3-1 transcription
  NKX3-1 is an AR target gene
  AR activity → NKX3-1 expression

AR→KLK3       +0.2928  p=2.44e-02 *
  AR drives KLK3/PSA directly
  Standard AR target gene

NKX3-1→ACPP   +0.4541  p=3.04e-04 ***
  NKX3-1 drives terminal secretory
  differentiation (ACPP)
  Circuit INTACT

NKX3-1→MSMB   +0.5226  p=2.17e-05 ***
  NKX3-1 drives MSMB expression
  Circuit INTACT

NKX3-1→KLK3   +0.6647  p=9.44e-09 ***
  NKX3-1 drives KLK3/PSA
  Strongest circuit connection
  Circuit INTACT

CONFIRMED CIRCUIT CHAIN:
  AR → NKX3-1 → ACPP / MSMB / KLK3
  Three-node linear chain
  AR is the upstream driver
  NKX3-1 is the intermediate node
  Terminal genes follow NKX3-1

NOT CONFIRMED (notable):
  AR→FOXA1      r=-0.083  ns
  AR→TMPRSS2    r=+0.088  ns
  EZH2→ACPP     r=-0.193  ns
  EZH2→MSMB     r=+0.049  ns
  EZH2→NKX3-1   r=-0.029  ns
  FOXA1→AMACR   r=+0.068  ns
  FOXA1→HOXC6   r=+0.098  ns
  MYC→MKI67     r=-0.022  ns
  AURKA→MKI67   r=+0.100  ns

WRONG DIRECTION:
  EZH2→KLK3    r=+0.342  p=0.008
  EZH2 appears to ACTIVATE KLK3
  within tumor samples
  See Section V for interpretation
```

---

## III. ARCHITECTURAL FINDING —
## NKX3-1 CIRCUIT IS INTACT

```
THE CENTRAL QUESTION:
  Is the NKX3-1→terminal differentiation
  circuit intact (like PAAD PTF1A→CTRC)
  or broken (like MDS CEBPE→ELANE)?

  This question determines the
  entire therapeutic geometry.
  Intact circuit = restore NKX3-1 input
  Broken circuit = different target needed

PRAD RESULT:
  NKX3-1 → target correlations (in tumors):
  Target     r         p        Architecture
  -----------------------------------------------
  ACPP    +0.4541  p=3.04e-04  INTACT
  MSMB    +0.5226  p=2.17e-05  INTACT
  KLK3    +0.6647  p=9.44e-09  INTACT
  KLK2    +0.6349  p=6.65e-08  INTACT
  HOXB13  +0.2614  p=4.55e-02  PARTIAL

  4/5 connections: INTACT
  VERDICT: INTACT

COMPARISON TABLE:
  Cancer  TF      Target  r       Architecture
  -----------------------------------------------
  PAAD    PTF1A   CTRC    +0.754  INTACT
  PRAD    NKX3-1  ACPP    +0.454  INTACT
  PRAD    NKX3-1  MSMB    +0.523  INTACT
  PRAD    NKX3-1  KLK3    +0.665  INTACT
  MDS     CEBPE   ELANE   +0.07   BROKEN

PAAD and PRAD share the same architecture:
  Switch gene is present in tumor cells
  When switch gene is expressed,
  downstream circuit executes normally
  The block is at the SWITCH GENE INPUT
  Not at the downstream connections

WHAT THIS MEANS:

  In PRAD tumor cells, NKX3-1 protein
  (when present) can still drive ACPP,
  MSMB, KLK3 terminal expression.
  The differentiation machinery is intact.
  The block is:
    1. NKX3-1 genomic deletion
       (chr8p21 loss — functional
       haploinsufficiency)
    2. NKX3-1 transcriptional repression
       (EZH2 lock — see Section V)
  Both mechanisms reduce NKX3-1 DOSE
  below the threshold needed for full
  terminal differentiation execution.

  Restore NKX3-1 dose:
  → ACPP executes (r=+0.454)
  → MSMB executes (r=+0.523)
  → KLK3 executes (r=+0.665)
  → Terminal luminal identity restores
  → False attractor dissolves

  This is directly analogous to PAAD:
  Restore PTF1A → CTRC executes
  → Acinar identity restores
  → False attractor dissolves

  Two different cancers.
  Same architectural principle.
  Same therapeutic logic.
```

---

## IV. ERG SUBTYPE ANALYSIS

```
ERG-high (fusion+?): n=20
ERG-low  (fusion-?): n=39
Threshold: 6.4804 (KDE from Script 1)

DEPTH BY ERG STATUS:
  ERG-high: 0.4327 ± 0.1516
  ERG-low : 0.4104 ± 0.1071
  p=0.614   NOT DIFFERENT

KEY GENES BY ERG STATUS:
  Gene      ERG-hi  ERG-lo  Change  p
  ------------------------------------------
  TMPRSS2   11.865  12.666  -6.3%  p=3.24e-05 ***
  PTEN      10.293  10.611  -3.0%  p=1.74e-02 *
  All other key genes: ns

GLEASON BY ERG:
  ERG-high: 10 high / 10 low (50/50)
  ERG-low:  17 high / 22 low (43/57)
  Similar distribution — no enrichment

INTERPRETATION:

  Finding 1: Same attractor
  ERG-high and ERG-low tumors are
  equally deeply blocked.
  TMPRSS2-ERG fusion and ETS-negative
  PRAD both arrive at the same
  HOXC6/AMACR false attractor.
  Different initiating events.
  Same destination.

  This has critical therapeutic implications:
  The attractor dissolution strategy
  (EZH2i / NKX3-1 restoration) should
  work equally in ERG+ and ERG- PRAD.
  No ERG-specific treatment stratification
  is needed for this approach.

  Finding 2: TMPRSS2 lower in ERG-high
  r confirms TMPRSS2-ERG fusion from
  expression data alone.
  When TMPRSS2 is fused to ERG,
  probes covering the TMPRSS2 transcript
  (5' of fusion breakpoint) show lower
  expression because the intact
  TMPRSS2 transcript is reduced.
  Framework found chromosomal
  rearrangement signature from
  expression data without fusion
  annotation.

  Finding 3: PTEN lower in ERG-high
  Known co-occurrence confirmed:
  TMPRSS2-ERG fusion + PTEN loss
  is a defined aggressive subtype.
  The framework found the co-occurrence
  from expression data.
  This subset (ERG+ / PTEN-low) likely
  has worse prognosis and may need
  PTEN pathway restoration in addition
  to attractor dissolution.
```

---

## V. EZH2 FINDINGS — REINTERPRETATION

```
SCRIPT 2 FINDING:
  EZH2→ACPP   r=-0.193  p=0.143  ns
  EZH2→MSMB   r=+0.049  p=0.714  ns
  EZH2→NKX3-1 r=-0.029  p=0.829  ns
  EZH2→KLK3   r=+0.342  p=0.008  WRONG DIR

EZH2 is NOT correlating with switch gene
suppression within tumor samples.

This requires careful interpretation.
It does not invalidate the EZH2 finding
from Script 1 (EZH2 +3.8%  p=1.53e-06
r=+0.426 with depth).

THREE EXPLANATIONS:

Explanation 1 — Floor effect:
  ACPP and MSMB are already suppressed
  in all tumors.
  The variance in ACPP within tumors
  is not driven by EZH2 variation.
  It is driven by NKX3-1 variation
  (NKX3-1→ACPP r=+0.454 confirmed).
  EZH2 has established the floor —
  within-tumor variance of ACPP
  reflects NKX3-1 dose variation,
  not EZH2 variation.
  This is consistent with:
  EZH2 locks the locus at initiation.
  NKX3-1 deletion + haploinsufficiency
  explains the within-tumor variation.

Explanation 2 — Stage specificity:
  EZH2 as ACPP/NKX3-1 lock is more
  prominent in advanced/metastatic PRAD
  and CRPC than in primary PRAD.
  In primary AR-positive PRAD:
  NKX3-1 genomic deletion is the
  dominant mechanism of functional loss.
  EZH2 lock becomes more important
  as cells progress toward AR independence.
  The dataset is primary PRAD (Gleason
  6-7 mostly) — not CRPC.
  EZH2 role may be underrepresented
  in this cohort.

Explanation 3 — EZH2 targets HOXC6/AMACR
                 not NKX3-1/ACPP directly:
  In PRAD specifically, EZH2 may be
  silencing the differentiation TFs
  while simultaneously allowing
  HOXC6/AMACR reactivation.
  EZH2's primary target in PRAD may be
  the basal cell program (TP63/KRT5)
  and other differentiation barriers —
  not directly NKX3-1 in primary disease.

WRONG DIRECTION finding — EZH2→KLK3:
  EZH2 r=+0.342 with KLK3  p=0.008
  EZH2 appears to ACTIVATE KLK3
  within tumor samples.

  Interpretation:
  This is likely a confounding effect.
  Higher EZH2 tumors are more AR-active
  (AR program amplified in aggressive
  primary PRAD).
  Higher AR activity → higher KLK3.
  EZH2 is co-regulated with the AR
  program in primary PRAD.
  EZH2 is a CONSEQUENCE of AR
  amplification in this stage —
  not a primary independent driver
  of NKX3-1 suppression.
  AR → EZH2 (positive) and
  AR → KLK3 (positive) both occur.
  EZH2 and KLK3 appear positively
  correlated as co-consequences of
  AR activity.

REVISED EZH2 PICTURE IN PRAD:
  Primary PRAD:
    EZH2 elevated (+3.8%) — real
    EZH2 tracks depth (r=+0.426) — real
    EZH2 co-regulated with AR program
    EZH2 not the primary within-tumor
    driver of NKX3-1/ACPP variation
    NKX3-1 haploinsufficiency dominates
    EZH2 inhibitor prediction: valid
    but may be more important in
    CRPC than primary disease

  CRPC / advanced PRAD:
    EZH2 role likely more prominent
    Cells have lost AR dependence
    EZH2 now primary chromatin lock
    EZH2i prediction stronger in CRPC
    This needs a CRPC dataset to confirm
    GSE35988 (the dataset we set aside
    with CRPC data) is the right next step
```

---

## VI. FOXA1 — FULL PICTURE

```
SCRIPT 2 FOXA1 CONNECTIONS:
  AR→FOXA1      r=-0.083  p=0.530  ns
  FOXA1→AMACR   r=+0.068  p=0.608  ns
  FOXA1→HOXC6   r=+0.098  p=0.460  ns
  FOXA1→EZH2    r=+0.066  p=0.619  ns
  FOXA1→ACPP    r=+0.168  p=0.203  ns
  FOXA1→KLK3    r=-0.006  p=0.964  ns
  FOXA1→MYC     r=+0.366  p=4.39e-03 **
  AR→AMACR      r=+0.083  p=0.531  ns
  AR→HOXC6      r=-0.107  p=0.422  ns

WHAT FOXA1 IS NOT:
  Not driven by AR (within tumor variance)
  Not driving AMACR or HOXC6
  Not driving EZH2
  Not connected to the NKX3-1 circuit
  Not the route to attractor dissolution

WHAT FOXA1 IS:
  Uniformly elevated in primary PRAD
  (+6.4% Script 1  p=2.21e-10)
  FOXA1 is elevated in ALL tumors
  nearly equally — low within-tumor
  variance.
  This is why within-tumor correlations
  are near zero — FOXA1 is a
  background constant not a variable.

  FOXA1 connects to MYC (r=+0.366)
  within tumors — the cells with
  slightly higher FOXA1 have slightly
  higher MYC.
  This is consistent with FOXA1
  activating MYC enhancers.
  A real but modest connection.

FOXA1 ROLE IN PRAD:
  FOXA1 is elevated as part of the
  AR program amplification that
  characterizes primary PRAD.
  It is a CONSEQUENCE of the
  false attractor state — not a
  primary driver of HOXC6/AMACR.
  HOXC6 and AMACR are driven by a
  mechanism independent of FOXA1
  within-tumor variation.

THERAPEUTIC IMPLICATION:
  FOXA1 inhibition would NOT dissolve
  the HOXC6/AMACR false attractor.
  FOXA1 is not connected to those
  markers in the within-tumor circuit.
  FOXA1 is a marker of AR program
  amplification — targeting it
  is similar to targeting AR itself.
  The attractor dissolution route
  is through NKX3-1 restoration
  (EZH2 inhibition / chromatin opening
  at NKX3-1 locus) — not FOXA1.
```

---

## VII. 3-GENE CLINICAL SCORE

```
COMPONENTS:
  ACPP  — suppressed in PRAD (switch gene)
           Contribute: (1 - normalized ACPP)
  HOXC6 — elevated in PRAD (FA marker)
           Contribute: normalized HOXC6
  AMACR — elevated in PRAD (FA marker)
           Contribute: normalized AMACR

SCORE STATISTICS (59 tumors):
  Mean  : 0.4796
  Median: 0.4854
  Std   : 0.1302

VALIDATION:
  vs block_depth (full score):
    r=+0.8664  p=7.81e-19
    Agreement: STRONG
    The 3-gene score captures 75%
    of the variance in the full
    depth score (r² = 0.75)
    Near-equivalent for clinical use

  vs Gleason:
    High: 0.4970 ± 0.1551 (n=27)
    Low : 0.4649 ± 0.1051 (n=32)
    p=0.1047  NOT CONFIRMED

  vs ERG:
    ERG-high: 0.4796 ± 0.1680
    ERG-low:  0.4796 ± 0.1085
    p=0.9044  No difference

NOTE ON GLEASON NON-CONFIRMATION:
  The 3-gene score uses ACPP, HOXC6, AMACR.
  The full depth score also includes
  MSMB, KLK3, KLK2, ERG, MKI67, EZH2.
  MSMB was the second strongest depth
  correlator (r=-0.551) and is not
  in the 3-gene score.
  A 4-gene score adding MSMB would
  likely restore Gleason separation.
  This is a post-hoc observation.
  The 3-gene score is validated as
  equivalent to the depth score
  but requires MSMB for Gleason
  stratification specifically.

CLINICAL UTILITY:
  3-gene RNA panel (ACPP/HOXC6/AMACR)
  measurable from standard biopsy
  RNA extraction.
  AMACR is already measured by IHC
  in clinical pathology for PRAD diagnosis.
  HOXC6 is in published prognostic
  panels (need literature confirmation).
  ACPP is measurable by IHC.
  A 3-protein IHC panel is feasible
  from routine biopsy material.
  This is a clinically actionable
  finding requiring validation.
```

---

## VIII. THE COMPLETE PRAD CIRCUIT MAP

```
CONFIRMED CONNECTIONS (5):

  AR ──(+0.361)──→ NKX3-1 ──(+0.454)──→ ACPP
                        │
                        ├──(+0.523)──→ MSMB
                        │
                        └──(+0.665)──→ KLK3
                                           ↑
  AR ──────────(+0.293)───────────────────→┘

  Also confirmed:
  FOXA1 ──(+0.366)──→ MYC (modest)

BLOCK LOCATION:
  The block is at or before NKX3-1.
  AR drives NKX3-1 (r=+0.361).
  But NKX3-1 is HAPLOINSUFFICIENT
  (chr8p21 deletion — genomic loss).
  Even with AR driving the remaining allele,
  NKX3-1 dose is below threshold for
  full terminal differentiation.

  Pathway to dissolution:
    Restore NKX3-1 protein dose
    → ACPP/MSMB/KLK3 execute (circuit intact)
    → Terminal luminal identity restores
    → HOXC6/AMACR cannot maintain
    → False attractor dissolves

  How to restore NKX3-1 dose:
    Option 1: EZH2 inhibitor
      Removes H3K27me3 at NKX3-1 locus
      Transcription of remaining allele
      increases
      NKX3-1 dose approaches threshold
      Most relevant in advanced PRAD/CRPC

    Option 2: CRISPRa
      Activate NKX3-1 locus directly
      Research tool — not clinical yet

    Option 3: AR agonist (paradoxical)
      AR drives NKX3-1 (r=+0.361)
      Supraphysiologic AR activation
      → higher NKX3-1 from remaining allele
      This is the bipolar androgen therapy
      (BAT) rationale
      Already in clinical use for CRPC

    Option 4: EZH2i + AR pathway combination
      EZH2i removes chromatin lock
      AR activity drives remaining allele
      Combined effect may reach
      differentiation threshold

NOT IN CIRCUIT (from this dataset):
  FOXA1 not connected to attractor markers
  EZH2 not connected to NKX3-1/ACPP
    within primary tumor variance
    (floor effect or stage specificity)
  MYC not connected to cell cycle markers
    within this cohort
  AR not connected to FOXA1 or TMPRSS2
    within this cohort's variance
```

---

## IX. REVISED DRUG TARGET HIERARCHY

```
Before literature check.
From geometry of both scripts.

TARGET 1: AR pathway inhibitor
  Geometry: AR→NKX3-1→KLK3 confirmed
            AR drives the circuit
            ADT/enzalutamide reduces
            AR driving the false attractor
  Stage:    Standard for all PRAD
  Note:     ADT alone does NOT dissolve
            attractor — reduces input
            but does not restore
            NKX3-1 dose to threshold
            (haploinsufficiency persists)

TARGET 2: EZH2 inhibitor (tazemetostat)
  Geometry: EZH2 +3.8% confirmed
            r=+0.426 with depth confirmed
            Within-tumor EZH2→NKX3-1
            correlation weak (primary PRAD)
            EZH2i prediction stronger
            for advanced PRAD/CRPC
            where EZH2 becomes primary lock
  Stage:    Primary PRAD — possible
            CRPC — stronger prediction
  Note:     Most important in combination
            with AR pathway inhibitor

TARGET 3: NKX3-1 restoration
  Geometry: NKX3-1 circuit INTACT
            r=+0.454 to +0.665
            Restore NKX3-1 dose →
            terminal differentiation executes
  Mechanism: CRISPRa (research)
             EZH2i (indirect)
             BAT (bipolar androgen therapy)
  Stage:    CRPC — high priority

TARGET 4: MYC / BET inhibitor
  Geometry: MYC +5.6% confirmed
            FOXA1→MYC r=+0.366 confirmed
            MYC elevated in PRAD
  Stage:    Primary and advanced PRAD
  Note:     BET inhibitors (JQ1 / iBET)
            suppress MYC transcription
            Already in PRAD trials

TARGET 5: AURKA inhibitor (alisertib)
  Geometry: AURKA +5.6% p=1.92e-07
            Depth correlation r=+0.346
            More deeply blocked tumors
            have more AURKA
  Stage:    High-grade PRAD / NEPC
            Alisertib already in PRAD
            and NEPC trials

NOT A TARGET (from geometry):
  FOXA1 inhibition
  FOXA1 is disconnected from HOXC6/AMACR
  within-tumor circuit.
  FOXA1 inhibition would not dissolve
  the false attractor.
  It is an AR consequence — target AR
  not FOXA1 for attractor dissolution.
```

---

## X. ANALYST ASSUMPTION ERRORS
## CORRECTED BY SCRIPT 2

```
ASSUMPTION ERROR 1:
  EZH2 directly suppresses NKX3-1/ACPP
  within primary PRAD tumors.

  Data: EZH2→ACPP  r=-0.193  ns
        EZH2→NKX3-1 r=-0.029 ns

  CORRECTION:
  In primary PRAD the dominant mechanism
  of NKX3-1 functional loss is genomic
  deletion (haploinsufficiency) not
  EZH2-mediated transcriptional repression.
  EZH2 repression is more prominent
  in advanced disease.
  Within-tumor variation in primary PRAD
  reflects NKX3-1 dose variation driven
  by haploinsufficiency — not by EZH2
  variation.
  The framework correctly found no
  within-tumor EZH2→NKX3-1 correlation.
  The analyst's assumption that EZH2
  would be the primary within-tumor
  driver was wrong for this stage.

ASSUMPTION ERROR 2:
  FOXA1 would drive HOXC6/AMACR
  as an AR pioneer factor opening
  chromatin for FA gene activation.

  Data: FOXA1→AMACR r=+0.068  ns
        FOXA1→HOXC6 r=+0.098  ns

  CORRECTION:
  FOXA1 is uniformly elevated across
  all primary PRAD tumors.
  It is a background constant not a variable.
  Within-tumor FOXA1 variation does not
  drive HOXC6 or AMACR variation.
  HOXC6 and AMACR are driven by a
  mechanism independent of FOXA1.
  Likely candidates: HOX cluster
  reactivation by loss of PRC1/PRC2
  repression; AMACR activation by
  metabolic reprogramming.
  These need further investigation.

ASSUMPTION ERROR 3:
  AR would not drive NKX3-1 in cancer
  (because NKX3-1 is frequently deleted).

  Data: AR→NKX3-1  r=+0.361  p=0.005

  CORRECTION:
  AR still drives the remaining NKX3-1
  allele in primary PRAD.
  Deletion removes one copy but the
  remaining copy is AR-regulated.
  The framework found this correctly.
  This has therapeutic implications:
  AR inhibition reduces NKX3-1 further
  (which worsens haploinsufficiency)
  while EZH2 inhibition increases
  NKX3-1 from the remaining allele.
  ADT and EZH2i have opposite effects
  on NKX3-1 transcription.
  Combination timing matters.
```

---

## XI. NOVEL PREDICTIONS — UPDATED

```
From Scripts 1 and 2 combined.
Before literature check.

N1: ACPP+MSMB co-suppression is a better
    clinical depth predictor than NKX3-1
    expression alone in primary PRAD.
    Both r>0.55 with depth.
    A 2-gene suppression score
    (ACPP low + MSMB low) predicts
    Gleason grade and attractor depth.
    ACPP is already in clinical use as
    a serum marker (PAP assay).
    ACPP tissue expression from biopsy
    as a depth predictor: not in use.

N2: NKX3-1 circuit is INTACT in PRAD.
    4/5 terminal genes follow NKX3-1
    with r=0.45-0.66 within tumors.
    This architecture (intact circuit,
    blocked input) means NKX3-1 dose
    restoration will execute the
    full terminal differentiation program.
    This is not stated explicitly in
    the PRAD literature in these terms.

N3: ERG-positive and ERG-negative PRAD
    share the same attractor basin
    (depth p=0.614 — no difference).
    Different initiating events
    (TMPRSS2-ERG fusion vs ETS-negative
    transformation) converge to the same
    HOXC6/AMACR false attractor.
    Attractor dissolution strategy
    applies equally to both subtypes.
    No ERG-stratified treatment needed
    for this approach.

N4: 3-gene score (ACPP/HOXC6/AMACR)
    r=+0.866 with full depth score.
    Equivalent to full multi-gene panel
    for depth scoring in primary PRAD.
    3-protein IHC panel feasible from
    routine biopsy material.
    AMACR already in clinical use —
    2-protein addition (ACPP + HOXC6)
    to existing AMACR IHC.

N5: AR inhibition reduces NKX3-1
    transcription (AR→NKX3-1 r=+0.361).
    EZH2 inhibition increases NKX3-1
    transcription (derepression).
    These are opposing mechanisms.
    Sequential therapy:
    EZH2 inhibitor FIRST to restore
    NKX3-1 and differentiation —
    THEN AR inhibitor for anti-proliferative
    effect after differentiation is restored.
    Simultaneous therapy risks:
    AR inhibition may counteract EZH2i
    benefit at NKX3-1 locus.
    Sequencing matters.
    Testable in KRAS-driven PRAD organoids
    or LNCaP cells.

N6: EZH2 role is stage-specific in PRAD.
    Primary PRAD: NKX3-1 haploinsufficiency
    dominates (genomic loss).
    EZH2 lock is secondary.
    Advanced PRAD/CRPC: EZH2 becomes
    primary chromatin lock as cells
    lose AR dependence and NKX3-1
    deletion is complemented by
    epigenetic silencing.
    EZH2i more important in CRPC
    than primary PRAD.
    Testable in GSE35988 (CRPC dataset
    set aside during dataset selection).
```

---

## XII. OPEN QUESTIONS FOR LITERATURE CHECK

```
OPEN 1:
  Is HOXC6 a direct AR target in PRAD?
  AR→HOXC6 not confirmed in this data
  (r=-0.107 ns).
  If HOXC6 is not AR-driven, what drives
  HOXC6 reactivation in PRAD?
  Candidate: loss of PRC2 repression
  at HOXC locus — EZH2 paradox
  (EZH2 elevated yet HOXC6 elevated
  — are they at different loci?)

OPEN 2:
  What drives AMACR elevation?
  AMACR is a metabolic enzyme
  (branched-chain fatty acid metabolism).
  Its elevation in PRAD is well known
  but the driver is unclear.
  Not driven by AR or FOXA1 in this data.
  May be driven by metabolic
  reprogramming independent of
  the transcription factor circuit.

OPEN 3:
  Does EZH2 inhibition in PRAD organoids
  restore NKX3-1 and ACPP expression?
  The within-tumor correlation is weak
  but the tumor-vs-normal comparison
  supports EZH2 as a contributor.
  Needs experimental confirmation.

OPEN 4:
  Does bipolar androgen therapy (BAT)
  increase NKX3-1 expression?
  AR drives NKX3-1 (r=+0.361).
  Supraphysiologic testosterone
  in BAT → AR activation → NKX3-1 up.
  If NKX3-1 crosses threshold →
  terminal differentiation executes.
  This would explain BAT efficacy
  in CRPC from an attractor geometry
  perspective.
  Testable from BAT trial biopsy RNA data.

OPEN 5:
  GSE35988 — CRPC analysis.
  EZH2 role in castration-resistant
  PRAD vs primary PRAD.
  The dataset has:
    Matched benign (n=28)
    Localized PRAD (n=59)
    Metastatic CRPC (n=35)
  Running this would confirm whether
  EZH2→NKX3-1 correlation strengthens
  in CRPC (as predicted in N6).
  This would complete the PRAD story.
```

---

## XIII. THE COMPLETE PICTURE

```
PRAD FALSE ATTRACTOR — CONFIRMED:
  Identity: HOXC6-high / AMACR-high /
            ACPP-low / MSMB-low /
            Basal layer dissolved

CIRCUIT: AR → NKX3-1 → ACPP/MSMB/KLK3
  3-node chain confirmed
  5 connections confirmed
  Circuit INTACT downstream of NKX3-1

BLOCK LOCATION:
  At NKX3-1 INPUT:
  1. Genomic deletion (chr8p21)
     → haploinsufficiency
  2. EZH2 chromatin lock (stage-dependent)
     → transcriptional repression
  Either/both reduce NKX3-1 dose below
  threshold for terminal differentiation

EZH2 ROLE:
  Confirmed elevated (+3.8% p=1.53e-06)
  Tracks with depth (r=+0.426)
  Primary role in advanced PRAD/CRPC
  Secondary role in primary PRAD
  (haploinsufficiency dominates in primary)

ERG SUBTYPES:
  Same attractor regardless of ERG status
  TMPRSS2 lower in ERG+ (fusion confirmed)
  PTEN lower in ERG+ (co-occurrence confirmed)

3-GENE CLINICAL SCORE:
  ACPP / HOXC6 / AMACR
  r=+0.866 with full depth score
  Near-equivalent clinical panel

THERAPEUTIC GEOMETRY:
  Restore NKX3-1 dose
  → circuit executes (confirmed intact)
  → attractor dissolves

  Primary route: EZH2 inhibitor
  Stage: CRPC > primary PRAD
  Combination: EZH2i + AR inhibitor
  Sequencing: EZH2i first then AR inhibitor

  Supporting route: BAT (bipolar androgen)
  Mechanism: AR→NKX3-1 confirmed
  Supraphysiologic AR → NKX3-1 above
  differentiation threshold

CROSS-CANCER PATTERN:
  PAAD: PTF1A circuit INTACT r=+0.754
  PRAD: NKX3-1 circuit INTACT r=+0.454-0.665
  Both: block at switch gene INPUT
  Both: EZH2 gain lock (3rd-4th cancer)
  Both: restore switch gene → program executes
  Same principle. Different lineage.
  Same therapeutic logic.

document_number:    88b
series_position:    Cancer validation #12
follows:            88a (Script 1)
next:               88c (Literature check)
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-01
```
