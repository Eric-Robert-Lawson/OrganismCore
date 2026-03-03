# RCC CROSS-TYPE ANALYSIS
## REASONING ARTIFACT — PRE-ANALYSIS PROTOCOL
## OrganismCore | 2026-03-03
### Author: Eric Robert Lawson

---

## METADATA

```
document_type:      Reasoning artifact
                    Pre-analysis protocol
                    Cross-cancer subtype work
covers:             ccRCC  (Validation #N, TCGA-KIRC
                            n=534 tumour / n=72 normal)
                    PRCC   (Validation #N, TCGA-KIRP
                            n=290 tumour)
                    chRCC  (Validation #N, TCGA-KICH
                            + GSE corpus)
                    cdRCC  (Validation #13, GSE89122
                            n=7 tumour / n=6 normal)
purpose:            Define locked predictions,
                    analytical protocol, and
                    output structure BEFORE any
                    cross-type script is written
                    or any cross-type comparison
                    is performed.
protocol_rule:      Predictions locked here.
                    Cannot be changed after script
                    runs.
                    Literature check follows analysis,
                    not before.
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-03
session_note:       The four individual analyses were
                    performed in three separate
                    sessions with no cross-type
                    context carry-over.
                    Convergences documented here
                    were observed AFTER the
                    individual analyses completed.
                    This cross-type analysis is
                    the first deliberate comparison.
```

---

## I. FOUNDATIONAL PRINCIPLE

```
The four individual analyses are the primary data.
They are not re-derived here.
They are not pooled here.
The depth scores for each type were computed
independently from type-specific normal references
and type-specific anchor genes.
They are not comparable at the raw expression level.

What is comparable:
  - Gene identity (same gene appears in depth
    correlators of multiple types)
  - Direction (same gene goes same direction
    in multiple types)
  - Rank (how high in the depth-correlated list
    does a gene appear across types)
  - Circuit topology (same gene-gene relationships
    appear in multiple types)
  - Drug target recurrence (same drug target
    identified independently in multiple types)
  - Contraindication recurrence (same drug
    contraindicated in multiple types)

What is NOT compared:
  - Raw fold change values across types
    (different platforms, different normals)
  - Absolute depth score values across types
    (axes are type-specific)
  - P-values directly (different n across types)

The analysis is a RANKED LIST COMPARISON
and a CIRCUIT TOPOLOGY COMPARISON.
It is not a pooled expression analysis.
```

---

## II. INPUT DATA — WHAT IS BROUGHT FORWARD

```
From each individual analysis, the following
are brought into the cross-type comparison:

FOR EACH TYPE:
  1. Top 20 positive depth correlators
     (genes that rise with attractor depth)
  2. Top 20 negative depth correlators
     (genes that fall — normal identity genes)
  3. Confirmed drug targets (with mechanism)
  4. Confirmed contraindications (with reason)
  5. False attractor identity description
     (what programme is gained)
  6. Normal identity description
     (what programme is lost)
  7. Epigenetic lock gene(s) confirmed
  8. Transition sequence (early/late phase genes
     if identified)
  9. Top inter-gene circuit (strongest r
     between any two depth-relevant genes)
  10. Switch gene (the gene most informative
      for the normal→attractor transition)

These ten items per type = 40 total inputs.
The cross-type analysis compares these 40 inputs
for structure, recurrence, and divergence.
```

---

## III. LOCKED PREDICTIONS
### (stated before any cross-type script runs)

---

### PREDICTION CLASS 1 — SHARED DEPTH GENES

```
X1: EZH2 will appear as a significant positive
    depth correlator in all four renal cancer
    types.
    Basis: Confirmed in ccRCC, PRCC, cdRCC
    individually. Predicted for chRCC based
    on the shared TCA disruption pattern.
    Falsification: EZH2 NOT depth-positive
    in chRCC would partially falsify X1.

X2: IL1RAP will appear as a significant positive
    depth correlator in at least three of the
    four types.
    Basis: Top attractor marker in cdRCC
    (r=+0.964). Best third gene in ccRCC panel
    (panel r=0.963). Not explicitly reported
    in PRCC or chRCC top lists.
    Predicted extension to at least three types.
    Falsification: IL1RAP depth-positive in
    fewer than three types.

X3: LOXL2 will appear as a positive depth
    correlator in at least two types beyond
    ccRCC (where it is the #1 metabolic
    axis correlate at r=+0.628).
    Basis: LOXL2 is an ECM crosslinker
    downstream of TCA collapse. ECM stiffening
    is a consequence of attractor deepening
    in any cancer that disrupts oxidative
    metabolism and shifts toward fibrotic
    remodelling. Predicted in PRCC (Type 2)
    and cdRCC.
    Falsification: LOXL2 not depth-positive
    in any other type.

X4: At least one SLC family transporter
    will be among the top negative depth
    correlators (normal identity losses)
    in all four types.
    Basis: SLC13A2 is the universal proximal
    tubule identity anchor in ccRCC (lost
    completely in Q4). SLC22A6 is the normal
    pole anchor in PRCC. SLC51B/SLC2A2 are
    chRCC normal identity genes. PRKAR2B
    (not SLC but transport-adjacent) in cdRCC.
    SLC transporters are the molecular
    definition of proximal tubule identity.
    Their loss should be universal.
    Falsification: A type where no SLC is
    in the top 20 normal identity losses.

X5: OGDHL will be among the top negative
    depth correlators (or confirmed suppressed)
    in at least three types.
    Basis: Confirmed suppressed in ccRCC
    (part of TCA collapse), PRCC (r=-0.527
    among metabolic losses), and cdRCC
    (r=-1.000 perfect depth ordering).
    Predicted also in chRCC given the shared
    TCA disruption pattern.
    Falsification: OGDHL not suppressed in
    two or more types.

X6: MKI67 (proliferation) will be UNCOUPLED
    from the top false attractor identity genes
    in all four types.
    Basis: The defining feature of an identity
    attractor (vs a proliferative oncogene)
    is that the attractor programme is not
    driven by proliferation — it is driven by
    identity. In cdRCC: MYC early but BHLHE40
    late (consolidation decoupled from
    proliferation). In PRCC: MET uncoupled
    from MKI67 (r=-0.069). In ccRCC: HIF
    programme partially decoupled from
    proliferative markers at Q4.
    Predicted: The top false attractor gene
    in each type will have r(gene, MKI67)
    closer to zero than r(gene, depth).
    Falsification: A type where the top
    attractor marker is strongly coupled to
    MKI67 (r > 0.5).
```

---

### PREDICTION CLASS 2 — SHARED CIRCUIT TOPOLOGY

```
X7: The TCA→αKG→EZH2 chromatin lock circuit
    will be quantitatively confirmed in all
    four types.
    Specifically: at least one TCA gene
    (OGDHL, SUCLG1, FH, or SDHA) will show
    negative correlation with EZH2 depth
    in each type.
    Basis: Confirmed in all three larger
    datasets (ccRCC: SUCLG1→EZH2 r=-0.300;
    PRCC: FH→EZH2 r=-0.293; cdRCC: EZH2
    confirmed up, OGDHL r=-1.000 down).
    Predicted for chRCC.
    Falsification: No TCA gene negatively
    correlated with EZH2 in one or more types.

X8: A polarity or cell architecture gene
    will be among the top depth correlators
    in at least three types.
    Basis: cdRCC found PAR→PCP polarity
    switch (PRKCI, PARD3, CELSR1, VANGL1).
    PRCC found TWIST1 as a stromal/EMT
    marker rising with depth. ccRCC found
    TGFBI (ECM adhesion/architecture) as
    the strongest circuit element (r=+0.766
    with RUNX1). chRCC has architecture-
    related genes in the Tier3 panel.
    Predicted: architecture/polarity loss
    or replacement is a universal feature
    of renal attractor deepening.
    Falsification: Only one or two types
    show architecture-related depth genes.

X9: The epigenetic lock will involve at least
    one of {EZH2, KDM1A, DNMT} in each type,
    and they will be mutually reinforcing
    (at least two co-elevated in the same type).
    Basis: ccRCC confirmed EZH2 + KDM1A
    (r=+0.390 depth). PRCC confirmed EZH2
    + KDM1A (r=+0.443 depth). cdRCC
    confirmed EZH2 (paired p=0.031).
    chRCC: Nrf2/KEAP1-AKR axis suggests
    a distinct epigenetic lock pathway.
    Predicted: co-elevation of chromatin
    modifiers in all types.
    Falsification: A type with only one
    chromatin modifier elevated.

X10: The false attractor identity in each type
     will be definable as a specific normal
     cell type from a different organ system.
     ccRCC:  HIF/VHL programme → hypoxic
             mesenchymal/endothelial-like
     PRCC:   Biliary ductal identity
             (KRT19/KRT7/ERBB2) → ICC-like
     chRCC:  Steroid-metabolising / adrenal
             cortical-like (CYP enzymes,
             AKR family, HSD17B)
     cdRCC:  Ductal secretory programme
             (PPARG/AGR2/IL1RAP) → aberrant
             collecting duct secretory cell
     Prediction: Each type's top 10 positive
     depth correlators will, when searched
     against normal tissue expression
     databases, show maximum expression in
     a specific non-renal tissue that defines
     the false identity.
     Falsification: A type whose depth
     correlators do not map to a coherent
     non-renal tissue identity.
```

---

### PREDICTION CLASS 3 — DRUG TARGET RECURRENCE

```
X11: Tazemetostat (EZH2 inhibitor) will be
     independently justified as a drug target
     in all four types from depth data alone.
     Basis: Justified in ccRCC (EZH2 depth+,
     BAP1→EZH2 mechanism), PRCC (EZH2 depth+,
     TCA coupling, PBAF synthetic lethality),
     cdRCC (EZH2 initiating lock, CEBPA
     mechanism, clinical trial NCT03874455).
     Predicted for chRCC.
     Falsification: chRCC depth analysis
     does not support EZH2 as a target.

X12: αKG supplementation will be independently
     justified as a combination partner for
     EZH2 inhibition in all four types.
     Basis: Justified in ccRCC (OGDHL/SUCLG1
     collapse → αKG depletion), PRCC (FH
     continuous sensor), cdRCC (OGDHL r=-1.000).
     Predicted for chRCC.
     Falsification: chRCC TCA is intact
     (OGDHL not suppressed) → αKG not needed.

X13: At least one checkpoint immunotherapy
     will be CONTRAINDICATED in the deepest
     attractor stratum of at least three types.
     Basis: ccRCC Q4: PD-L1 falls, MHC-I
     down, anti-PD-L1 contraindicated.
     PRCC Q4: TIM-3 falls, B2M down, anti-
     TIM-3 contraindicated. cdRCC: no explicit
     immune analysis in the four scripts
     completed.
     Predicted: the same immune evasion
     pattern (MHC-I down, checkpoint ligand
     down, T cells present but blind) will
     appear in deep chRCC.
     Falsification: A type where checkpoint
     markers RISE with attractor depth.

X14: The drug combinations that are predicted
     to work will require at least TWO
     simultaneous interventions in all deep
     (late-phase) tumours across all types.
     Basis: cdRCC three-circuit architecture
     (N16) — monotherapy insufficient.
     ccRCC four-wall model — all walls must
     be addressed. PRCC: depth-stratified
     combinations (EZH2i + αKG + identity
     disruptor). No type identified a single
     drug sufficient for deep attractor
     dissolution.
     Falsification: A type where a single
     drug addresses all depth-elevated
     circuits simultaneously.

X15: No existing single-agent standard of care
     for any RCC subtype will address the
     deepest attractor stratum of that
     subtype as currently deployed.
     Basis: ccRCC: belzutifan is depth-
     independent (not depth-targeted).
     PRCC: savolitinib 27% ORR (insufficient
     for deep tumours). cdRCC: no standard
     of care exists. chRCC: mTOR inhibitors
     are current SOC but not depth-stratified.
     Predicted: In every type, current SOC
     misses the deep attractor stratum because
     it was not designed around attractor depth.
     This is a structural prediction about
     the field, not about any specific drug.
     Falsification: A type where current
     SOC demonstrably targets the depth axis
     specifically.
```

---

### PREDICTION CLASS 4 — DIVERGENCE PREDICTIONS
### (where types are predicted to DIFFER)

```
X16: The false attractor identity programme
     will be SUBTYPE-SPECIFIC and non-overlapping
     at the gene level.
     ccRCC top false identity genes will NOT
     appear in the top false identity genes
     of the other three types.
     This is the prediction that distinguishes
     the shared mechanism (EZH2 lock) from
     the subtype-specific output (what fills
     the space after identity is erased).
     Falsification: >3 false attractor
     identity genes shared between any two
     types at the gene level.

X17: The normal identity loss programmes
     will be PARTIALLY shared (SLC transporters
     universal) but PARTIALLY divergent
     (the specific transporters, channels,
     and enzymes will differ by cell of origin).
     ccRCC: SLC13A2 (proximal tubule citrate/
             αKG import)
     PRCC:  SLC22A6 (OAT1, proximal tubule
             organic anion transport)
     chRCC: SLC51B/SLC2A2 (intercalated cell
             bile acid / glucose transport)
     cdRCC: AQP2/SCNN1/AVPR2 (collecting duct
             principal cell water/Na channels)
     Prediction: Each type loses the SLC/
     channel signature of its specific cell
     of origin. The specific genes will
     differ but will all be SLC/channel
     family members.
     Falsification: A type that loses a
     non-SLC/channel normal identity marker
     as its primary switch gene.

X18: The transition sequence (early phase vs
     late phase) will show MYC-related genes
     as early and consolidating TF programmes
     as late in at least two types.
     cdRCC confirmed: MYC early / BHLHE40 late.
     Predicted for PRCC: MET/proliferative
     early / ERBB2+KDM1A late.
     Predicted for ccRCC: MYC/proliferative
     early (not confirmed in scripts) /
     RUNX1+LOXL2 late.
     chRCC: unknown — this is the open
     prediction.
     Falsification: No type shows a two-phase
     early/late transition structure beyond
     cdRCC.

X19: The immune evasion mechanism will DIFFER
     between types in the specific downstream
     target but SHARE the upstream pattern
     (innate sensing active / adaptive
     presentation silenced).
     ccRCC deep: IFI16 active / B2M down
     PRCC deep: IFI16 active (inferred) /
                B2M/HLA-A down confirmed
     cdRCC: immune analysis incomplete
     chRCC: immune analysis — unknown
     Predicted common pattern: innate DNA
     sensing elevated (IFI16/cGAS/STING
     family) but MHC-I presentation down
     (B2M/HLA-A/TAP1 down) across at least
     three types.
     Falsification: Immune evasion pattern
     differs mechanistically between types
     (e.g., one type uses PD-L1 high, another
     uses B2M loss — these are different
     mechanisms).

X20: The depth score will have different
     DYNAMIC RANGE across types.
     cdRCC depth transitions are abrupt
     (n=7, binary-like — either early or late).
     ccRCC depth transitions are continuous
     (n=534, smooth quartile progression).
     PRCC depth transitions show Type 1/Type 2
     discontinuity superimposed on continuous
     depth within each type.
     chRCC depth transitions unknown.
     Prediction: Dynamic range reflects
     the underlying biology of each tumour
     type and its typical clinical presentation
     stage at diagnosis. This is not a
     testable quantitative prediction but a
     structural observation about why depth
     scores look different across types.
     This prediction is stated to prevent
     the error of assuming all types should
     have the same depth distribution.
```

---

## IV. ANALYTICAL PROTOCOL

```
STEP 1 — GENE OVERLAP ANALYSIS

  Input:
    Top 20 positive depth correlators
    per type (80 genes total, with
    possible overlaps).
    Top 20 negative depth correlators
    per type (80 genes total).

  Method:
    For each gene appearing in the depth
    correlator list of any type, count
    how many types it appears in.
    Classify as:
      Universal (4/4 types)
      Near-universal (3/4 types)
      Shared (2/4 types)
      Type-specific (1/4 types)

  Output:
    Universal positive depth gene list
    (pan-renal attractor genes — rising)
    Universal negative depth gene list
    (pan-renal identity loss genes — falling)
    Shared circuit candidates
    Type-specific signatures

  Threshold for significance:
    A gene appearing in 3/4 or 4/4 types
    in the same direction is a candidate
    pan-renal attractor gene.
    A gene appearing in 2/4 types is
    noted but not claimed as universal.


STEP 2 — DRUG TARGET RECURRENCE ANALYSIS

  Input:
    All confirmed drug targets per type
    (from locked drug target lists in
    individual analyses — not re-derived).
    All confirmed contraindications per type.

  Method:
    Matrix of drug × type.
    For each drug: how many types identify
    it as a target? How many as a
    contraindication?
    For drugs appearing in multiple types:
    is the mechanism the same or different?

  Output:
    Pan-renal drug targets (same drug,
    same mechanism, ≥3 types)
    Shared drug targets (≥2 types,
    may differ in mechanism)
    Type-specific drug targets
    Universal contraindications
    Conditional contraindications
    (contraindicated in deep stratum
    of ≥2 types)

  Critical distinction:
    A drug appearing as a target in 4/4
    types with the SAME mechanism is a
    pan-renal candidate for backbone
    therapy.
    A drug appearing as a target in 4/4
    types with DIFFERENT mechanisms
    is four independent validations of
    the drug class but NOT evidence for
    a shared mechanism.
    These must be distinguished.


STEP 3 — FALSE ATTRACTOR IDENTITY MAPPING

  Input:
    The false attractor identity programme
    for each type (positive depth genes
    that define WHAT the tumour has become,
    not just that it has deepened).

  Method:
    For each type's false attractor genes,
    query: what normal tissue or cell type
    expresses this programme?
    Source: Human Protein Atlas tissue
    expression profiles (used as reference,
    not re-downloaded — use known biology
    from individual analyses).

  Output:
    False identity map:
      ccRCC  → [mesenchymal/hypoxic/VHL-null]
      PRCC   → [biliary/ICC-like]
      chRCC  → [adrenocortical-like/steroid]
      cdRCC  → [aberrant ductal secretory]

    Overlap question: Do any two types
    converge on the same false identity?
    If yes: do they share drug targets for
    that identity programme?

  Note:
    If two types share a false identity
    programme, that is a novel finding.
    If they share a false identity AND
    independently arrived at the same drug
    target, that is a convergence of the
    strongest kind.


STEP 4 — NORMAL IDENTITY LOSS MAPPING

  Input:
    The normal identity loss genes for each
    type (negative depth correlators that
    define WHAT the tumour was before it
    became the false attractor).

  Method:
    Classify each type's switch genes and
    normal pole genes by:
      Cell of origin (nephron segment)
      Gene family (SLC, aquaporin, enzyme,
      TF, channel)

  Output:
    Normal identity map:
      ccRCC  → proximal tubule S1
               (SLC13A2, SLC22A6, CUBN)
      PRCC   → proximal tubule S2/S3
               (SLC22A6, FABP1, UMOD)
      chRCC  → intercalated cell
               (SLC51B, HSD17B14, FOXI1)
      cdRCC  → principal/intercalated cell
               (AQP2, SCNN1, AVPR2, TFCP2L1)

    Concordance test:
    Does the normal identity gene panel
    for each type match the expected cell
    of origin for that cancer type?
    This is a structural validation of
    the depth score methodology itself —
    if the depth score is real, the
    bottom of the normal identity axis
    should correspond to the known cell
    of origin for each cancer.


STEP 5 — CHROMATIN LOCK COMPARISON

  Input:
    All chromatin modifier genes confirmed
    as depth-positive in each type.
    All TCA genes confirmed as depth-negative
    in each type.

  Method:
    Build the TCA→αKG→chromatin circuit
    for each type using confirmed gene pairs.
    Compare circuit topology across types:
    same genes? same direction? same
    quantitative strength (correlation
    coefficient, within-type normalised)?

  Output:
    Shared TCA→αKG→chromatin circuit
    (universal renal attractor lock)
    or
    Type-specific circuits with analogous
    but different genes
    (convergent evolution of the same
    functional mechanism through different
    molecular actors)


STEP 6 — TRANSITION SEQUENCE ANALYSIS

  Input:
    Phase structure (early/late) where
    identified in individual analyses.
    cdRCC: MYC early / BHLHE40 late
           (r=-0.964 confirmed)
    PRCC:  proliferative early (MKI67-high)
           / identity-locked late (MKI67-low)
    ccRCC: depth quartiles Q1→Q4 (continuous)
           specific early/late TFs not yet
           formally confirmed in ccRCC scripts
    chRCC: not yet characterised

  Method:
    For each type where a transition
    sequence exists, characterise the
    early and late phase gene sets.
    Compare across types:
    Are the same TF families early and late?
    Is MYC consistently early?
    Is identity consolidation consistently late?

  Output:
    Cross-type transition model
    (if supported) or evidence against
    a universal transition sequence
    (if types differ fundamentally in
    how they deepen)


STEP 7 — IMMUNE ARCHITECTURE COMPARISON

  Input:
    Immune markers confirmed in each type
    with depth direction.
    ccRCC: B2M down, HLA-A down, IFI16 up,
           PD-L1 falls Q4, TIM-3 falls Q4
    PRCC:  B2M down (r=-0.222), HLA-A down
           (r=-0.237), TIM-3 down (r=-0.396),
           PD-L1 falls Q4, ARG1 up Q4
    cdRCC: immune analysis not fully
           completed in scripts 1-4
    chRCC: BTNL3 (immune) in Tier3 panel

  Method:
    Compare MHC-I pathway genes across types.
    Compare innate sensing genes across types.
    Compare checkpoint gene direction across types.

  Output:
    Universal immune evasion pattern
    (if innate sensing up / MHC-I down
    appears in ≥3 types):
      → supports MHC-I restoration as
        universal deep renal cancer immune
        strategy
    Type-specific immune evasion mechanisms:
      → supports subtype-specific immune
        combination strategies


STEP 8 — CLINICAL SYNTHESIS

  Input:
    All outputs from Steps 1-7.

  Method:
    Build a cross-cancer drug matrix:
      Rows: drug targets
      Columns: cancer types
      Cell: target (T), contraindicated (C),
            unknown (U), conditional (K)

    Identify the pan-renal backbone (drugs
    that are T in ≥3 types with same mechanism).

    Identify the subtype-specific arms
    (drugs that are T in only one type).

    Identify the universal contraindications
    (drugs that are C in ≥2 types in deep
    stratum).

    Formulate the basket trial design
    implication: what would a depth-
    stratified, pan-renal basket trial
    look like based on this analysis?

  Output:
    Cross-cancer drug matrix (table)
    Pan-renal backbone drug candidates
    Subtype-specific arms
    Universal contraindications
    Proposed basket trial stratification
    (by depth score + subtype)
    Not a clinical protocol — a hypothesis
    for protocol design
```

---

## V. OUTPUT STRUCTURE

```
The cross-type analysis script will produce
the following outputs in order:

  A. Gene overlap table
     (Universal / Near-universal / Shared /
     Type-specific for positive and negative
     depth correlators)

  B. False attractor identity map
     (one paragraph per type, then comparison)

  C. Normal identity loss map
     (nephron segment of origin confirmed
     or contradicted)

  D. TCA→αKG→chromatin circuit comparison
     (table: which TCA gene, which chromatin
     gene, what r, in which type)

  E. Drug target recurrence matrix
     (drug × type, with mechanism notation)

  F. Contraindication matrix
     (drug × type × depth stratum)

  G. Immune architecture comparison
     (table: immune gene, direction, type)

  H. Transition sequence comparison
     (where characterised)

  I. Cross-cancer drug matrix
     (final synthesis table)

  J. Basket trial design implication
     (hypothesis statement only —
     not a protocol)

  K. Open questions
     (what cannot be answered from the
     existing data and requires new data)

  L. Predictions confirmed or denied
     (scoring each X1-X20 against outputs)
```

---

## VI. WHAT THIS ANALYSIS CANNOT DO

```
The following are explicitly OUT OF SCOPE
for this analysis and must not be claimed
as outputs:

  1. Statistical testing across types
     The datasets have different n, different
     platforms, and different depth axes.
     No cross-type p-value is valid.
     All cross-type comparisons are
     descriptive and directional only.

  2. Pooled survival analysis
     OS data from TCGA-KIRC, TCGA-KIRP,
     TCGA-KICH, and GSE89122 are not
     comparable without harmonisation.
     No cross-type Kaplan-Meier is performed.

  3. Novel gene discovery
     This analysis does not search for new
     genes. It compares existing ranked
     lists. If a gene not in any individual
     analysis's top list is found to be
     interesting in a cross-type context,
     it is flagged as a hypothesis for
     future primary analysis, not claimed
     as a finding.

  4. Causal claims from correlation
     All circuits are correlation-based.
     Cross-type circuit comparisons are
     comparisons of correlational patterns.
     Causality requires experimental
     validation.

  5. Drug efficacy claims
     The drug matrix describes mechanistic
     rationale for drug targeting. It does
     not claim or imply clinical efficacy.
     All drug statements are hypotheses
     for experimental testing.

  6. Revision of individual type predictions
     The cross-type analysis is additive.
     It does not supersede, revise, or
     update the predictions locked in the
     individual type reasoning artifacts.
     If a cross-type finding appears to
     contradict an individual type finding,
     the contradiction is noted as an
     open question — the individual type
     prediction is not changed.
```

---

## VII. KNOWN STRUCTURAL ASYMMETRY — STATED BEFORE ANALYSIS

```
The four datasets are not equivalent in power:

  ccRCC:  n=534 tumour + 72 normal
          TCGA-KIRC — large, well-powered
          Most confident depth correlations
          Most confident drug targets

  PRCC:   n=290 tumour
          TCGA-KIRP — well-powered
          Two subtypes (T1/T2) introduce
          heterogeneity
          Second most confident

  chRCC:  n=~60-90 (TCGA-KICH is smaller)
          Moderately powered
          Oncocytoma comparison adds complexity

  cdRCC:  n=7 tumour + 6 normal
          GSE89122 — underpowered for many tests
          Most confident for paired comparisons
          Least confident for depth correlations

This asymmetry means:
  Findings confirmed in ccRCC and PRCC
  have the strongest support.
  Findings confirmed in ccRCC, PRCC, and
  chRCC are near-universal.
  Findings confirmed in all four including
  cdRCC carry a caveat for cdRCC (n=7).
  The cdRCC findings are confirmed as
  directionally consistent, not
  quantitatively equivalent.

This asymmetry is acknowledged in every
cross-type claim and factored into the
confidence statements for each prediction
X1-X20.
```

---

## VIII. NOVEL PREDICTION NOT IN ANY INDIVIDUAL ANALYSIS

```
The following predictions arise specifically
from the cross-type comparison context
and were not possible to state during any
individual analysis.
They are stated here for the first time
and are therefore locked as novel before
any cross-type script runs.

XN1: Pan-renal attractor signature exists.
  There is a set of 5-10 genes that are
  depth-positive in all four renal cancer
  types. This set, if it exists, is the
  molecular definition of "attractor depth"
  in the renal cancer context, independent
  of histological subtype.
  If XN1 is true, these genes could form
  a single IHC panel applicable to all
  renal cancer biopsies to determine
  attractor depth without subtype-specific
  assays.
  Testable: gene overlap analysis (Step 1).

XN2: The nephron segment of origin is
  recoverable from the negative depth
  correlators of each type, and the
  four types will map to four distinct
  nephron segments that match the
  known pathological cell of origin.
  This would validate the depth score
  methodology retroactively: if the score
  is measuring the normal→attractor
  transition correctly, the genes most
  sensitive to that transition (negative
  depth correlators) should be the genes
  most specific to the normal cell of
  origin.
  This is a structural validation of the
  entire framework across all four types
  simultaneously.
  Testable: normal identity loss mapping
  (Step 4).

XN3: The false attractor identities of
  the four types will not overlap at
  the gene level (X16) but WILL overlap
  at the pathway level.
  Specifically: all four false attractor
  identities involve secretory or transport
  programmes from other epithelial cell
  types. None involve a mesenchymal,
  neuronal, or haematopoietic identity.
  This would suggest that renal cancers
  specifically adopt false epithelial
  identities from adjacent epithelial
  lineages — consistent with the
  collecting duct origin of Müllerian,
  biliary, and secretory programmes all
  being epithelial-derived.
  Testable: false identity mapping (Step 3)
  + pathway classification of top false
  attractor genes.

XN4: The CEBPA-suppressed state (described
  as the false attractor definition in
  cdRCC) will have an analogous TF
  suppression mechanism in at least one
  other type.
  In cdRCC: EZH2 silences CEBPA, which
  allows the PPARG module to activate.
  The attractor IS the CEBPA-suppressed state.
  Predicted: ccRCC has an analogous TF
  (possibly CEBPA itself, or HNF4A, or
  another differentiation TF) whose
  EZH2-mediated silencing defines the
  attractor state.
  In PRCC: HNF4A falls with depth
  (published — proximal tubule identity TF).
  EZH2 silencing HNF4A in PRCC would be
  the PRCC equivalent of EZH2-CEBPA in cdRCC.
  Testable: correlation between EZH2 and
  the candidate suppressed TF in each type
  using existing depth-correlated gene data.

XN5: A two-gene clinical biomarker panel
  (one normal identity gene + one false
  attractor gene) will be derivable for
  each type, and the four panels together
  will form a cross-renal cancer depth
  staging system.
  This extends the PRCC GOT1/RUNX1
  Transition Index concept to all four types:
    ccRCC:  SLC13A2 / IL1RAP (proposed)
    PRCC:   SLC22A6 / ERBB2 (proposed)
            or GOT1 / RUNX1 (confirmed TI)
    chRCC:  SLC51B / [top false attractor]
            (to be identified)
    cdRCC:  PRKAR2B / IL1RAP (proposed)
            or ADPRM / IL1RAP
  If a two-gene panel exists for each type,
  and if they can be harmonised into a
  single cross-type staging framework,
  the clinical implication is a unified
  renal cancer depth staging system
  implementable by IHC in any pathology
  laboratory.
  Testable: Step 1 gene overlap analysis
  + cross-type transition index construction.
```

---

## IX. WHAT A CONFIRMATORY RESULT LOOKS LIKE

```
For the cross-type analysis to be
considered confirmatory (not just
exploratory), the following criteria
must be met:

  MINIMUM CONFIRMATION:
    X1 confirmed (EZH2 universal)
    X4 confirmed (SLC loss universal)
    X7 confirmed (TCA→EZH2 in all types)
    XN2 confirmed (nephron segment
         recoverable from negative panel)

  STRONG CONFIRMATION:
    Above plus:
    X2 confirmed (IL1RAP ≥3 types)
    X10 confirmed (false identities
         map to specific non-renal tissues)
    X13 confirmed (checkpoint
         contraindication ≥3 types)
    XN1 confirmed (pan-renal attractor
         signature exists)

  EXCEPTIONAL CONFIRMATION:
    All of the above plus:
    XN3 confirmed (all false identities
         are epithelial, not mesenchymal)
    XN4 confirmed (CEBPA-analogous TF
         suppression in ≥2 other types)
    XN5 confirmed (two-gene panels
         derivable for all four types)

  FALSIFICATION:
    X1 denied (EZH2 not universal) — this
    would suggest the TCA-chromatin lock
    is type-specific, not universal.
    This would be a significant finding
    even if unwelcome.

    X16 denied (false attractor genes
    overlap between types) — this would
    suggest the false identity programme
    is not subtype-specific, which would
    contradict the individual type findings.
    It would require re-examination of
    what the false attractor identity
    actually represents.

  The goal is not to confirm.
  The goal is to find what is true.
  Falsification of X1 would be a more
  important finding than confirmation
  of all 20 predictions, because it
  would require revision of the
  framework's most fundamental claim.
```

---

## X. PROTOCOL COMPLIANCE STATEMENT

```
This document was written before:
  - Any cross-type comparison script
    was written
  - Any cross-type gene overlap table
    was constructed
  - Any cross-type circuit comparison
    was made
  - Any cross-type drug matrix was built

The predictions X1-X20 and XN1-XN5 are
locked as of 2026-03-03.

They cannot be changed after the
cross-type script runs.

They can be confirmed, partially confirmed,
denied, or found to be untestable from
existing data.

All four outcomes are equally valid.

The analysis is designed to find structure
if structure exists, and to find its absence
if it does not.

The independence of the four individual
analyses (derived across three separate
sessions with no cross-type context)
is the primary strength of this work.
The cross-type analysis is the test of
whether that independence produced
convergent results because the biology
is real, or coincident results that
will not replicate in formal comparison.

Author:   Eric Robert Lawson
          OrganismCore
Date:     2026-03-03
Status:   LOCKED — READY FOR SCRIPT
```
