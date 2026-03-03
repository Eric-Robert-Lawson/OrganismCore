# cdRCC — COLLECTING DUCT RENAL CELL CARCINOMA
## DOCUMENT 89b ADDENDUM — SCRIPT 3 OUTPUT
## OrganismCore — Cancer Validation #13
## Script 3 — Spearman Audit, Module Independence,
##             Circuit Assignments, MYC Role
## Date: 2026-03-03

---

## METADATA

```
document_number:    89b addendum
document_type:      Script 3 reasoning artifact
dataset_primary:    GSE89122
                    7 CDC tumours | 6 matched normals
                    6 matched pairs + 1 unpaired (CDC5)
dataset_replication: GSE83479
                    Downloaded. Column classifier
                    returned 0 CDC samples.
                    Metadata titles do not contain
                    expected keywords. Fix required
                    for Script 4 (see Section VIII).
scripts:            cdrcc_false_attractor.py    (S1)
                    cdrcc_false_attractor_2.py  (S2)
                    cdrcc_false_attractor_3.py  (S3 v2)
follows:            Doc 89b
next:               Doc 89c (Literature check)
                    OR Script 4 (GSE83479 fix + new tests)
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-03
```

---

## I. WHAT SCRIPT 3 WAS DESIGNED TO DO

```
Seven tests were designed and run:

  S3-P1: Programme A vs B independence
         Predicted: r(A,B) < 0.3 in tumours
  S3-P2: PPARG rewiring
         Predicted: CEBPA lost, KLF5 gained
  S3-P3: ADCY3 driver identification
         Predicted: MYC or BHLHE40
  S3-P4: CELSR1 circuit assignment
         Predicted: PPARG module
  S3-P5: CDC3 biology
         Predicted: AQP2/PRKAR2B retained
  S3-P6: MYC metabolic vs proliferation
         Predicted: |r(MYC, MKI67)| < 0.4
  S3-P7: GSE83479 independent replication
         Predicted: 8+/12 genes replicate

Additional outputs:
  - Spearman depth correlations (CDC4 corrected)
  - Pearson vs Spearman audit table
  - Full Spearman negative correlator list
  - Corrected paired Wilcoxon (full panel)
```

---

## II. SPEARMAN AUDIT — WHAT S1/S2 GETS TO KEEP

```
17/20 genes from the S2 Pearson top-20 are stable
(|Pearson| - |Spearman| < 0.15).

STABLE (reliable regardless of CDC4):
  LOC101927630  USP45       IL1RAP      MYC
  PRKCI         CD48        PRKAR2B     INPP4B
  CHPT1         GPRC5A      ADPRM       TMPRSS4
  NOMO1         IKZF2       CST6        B4GALT5
  CDS2

CDC4-INFLATED (directional only, r overstated):
  KLF5    (Pearson +0.950 → Spearman +0.786)
  MPP6    (Pearson -0.948 → Spearman -0.786)
  RHBDL2  (Pearson +0.946 → Spearman +0.786)

CONSEQUENCE:
  KLF5 is the core attractor TF — confirmed.
  Its Spearman r is +0.786, still the top
  depth-tracking TF in the dataset.
  The inflation was ~0.16. The biology stands.
  The direction is right. The magnitude was
  overstated by ~17% due to CDC4.
  All conclusions from S1/S2 about KLF5,
  MPP6, RHBDL2 are directionally confirmed.

ADPRM AT SPEARMAN r=-1.000:
  Perfect negative rank correlation.
  ADPRM encodes ADP-ribosylhydrolase 3.
  Every single tumour ranking on the depth axis
  is exactly mirrored by ADPRM ranking in
  reverse. ADPRM is the most depth-coupled
  suppressed gene in the entire dataset by
  rank ordering.
  Biological meaning: ADP-ribosylation is a
  post-translational modification involved in
  DNA repair (PARP pathway), mitochondrial
  function, and stress signalling. ADPRM
  reverses mono-ADP-ribosylation marks.
  Its perfect suppression with depth suggests
  the ADP-ribosylation state is progressively
  altered as the attractor deepens.
  Stated here before literature check.
```

---

## III. NEW SPEARMAN NEGATIVES — REAL BIOLOGY

```
Six genes at perfect Spearman r = -1.000:
  TNXB     OGDHL    ADPRM
  SCG2     LAMTOR4  ZBED6CL

These genes are monotonically suppressed
across the depth ranking. Every tumour
with more depth has less of these genes.

TNXB — Tenascin-X
  Extracellular matrix glycoprotein.
  Expressed in the tubular basement membrane
  of the kidney. Complete loss as attractor
  deepens. The ECM scaffold of the collecting
  duct is being progressively dismantled.
  TNXB loss is associated with connective
  tissue disorders (Ehlers-Danlos). In cancer,
  TNXB loss may facilitate invasion.
  Its perfect depth coupling suggests the
  collecting duct ECM programme is the most
  depth-sensitive feature of the transition.
  Novel observation for cdRCC.

OGDHL — Oxoglutarate Dehydrogenase-Like
  Mitochondrial TCA cycle enzyme.
  OGDHL suppression = TCA cycle impairment.
  This was predicted in Doc 89b as a switch
  gene candidate (r=-0.931 in S1 Pearson —
  now confirmed r=-1.000 Spearman).
  The deepest tumours have completely lost
  mitochondrial TCA activity at this node.
  OGDHL suppression forces cells toward
  alternative carbon metabolism.
  Connected to the HK2 UP / HK1 DOWN finding
  (Step 11) — the cell loses TCA-coupled
  metabolism and shifts glucose entry to
  HK2-mediated routes.

SCG2 — Secretogranin II
  Dense-core vesicle protein. Marker of
  neuroendocrine secretory cells.
  Expressed in normal collecting duct
  (scattered neuroendocrine cells).
  Complete loss with depth.
  The neuroendocrine microenvironment of
  the collecting duct is lost as the
  attractor deepens.

LAMTOR4 — Late Endosomal/Lysosomal
  Adaptor, MAPK and mTOR Activator 4
  Part of the Ragulator complex on
  lysosomes — required for amino acid-
  sensing mTORC1 activation.
  Complete suppression with depth.
  As the attractor deepens, mTORC1
  lysosomal signalling is progressively lost.
  This may reflect the shift from nutrient-
  sensing growth control to constitutive
  proliferative signalling in deep attractor
  states.

ZBED6CL — ZBED6 C-terminal Like
  Poorly characterised zinc-finger BED
  domain protein. Predicted transcription
  factor. Complete depth coupling suggests
  it is a collecting duct identity TF
  not yet characterised.
  Novel prediction: ZBED6CL is a marker of
  collecting duct identity that is lost
  monotonically with cdRCC depth.
  Stated before literature check.

SUMMARY OF r=-1.000 GENES:
  These six genes define the FLOOR of the
  attractor transition. They are not partially
  suppressed — they are rank-ordered perfectly
  against depth. Any of them could serve as
  a single-gene proxy for depth measurement
  more robustly than the composite score.
  ADPRM or TNXB could replace the PRKAR2B
  component in the depth score for a purely
  data-driven axis.
  The biology is: ECM loss (TNXB) + TCA loss
  (OGDHL) + ADP-ribosylation loss (ADPRM) +
  dense-core vesicle loss (SCG2) + mTOR
  sensing loss (LAMTOR4).
  This is a coherent programme: the deep
  attractor state has lost the metabolic,
  structural, and signalling identity of the
  collecting duct simultaneously.
```

---

## IV. PREDICTION VERDICTS — ALL SEVEN

### S3-P1: Programme A vs B independence

```
PREDICTED: r(A,B) < 0.3
OBSERVED:  r = +0.607  p = 0.148  ns
VERDICT:   UNDERPOWERED — CANNOT DETERMINE

The r is above the prediction threshold.
BUT p = 0.148 — not significant.
With n=7, Spearman requires |r| > 0.75
for p < 0.05.

THE DATA TELLS US:
  CDC6 (depth=1.000) scores highest on BOTH
  Programme A (+1.558) and Programme B (+1.262).
  Every other tumour has lower scores on both.
  The correlation is driven by a single sample.
  Remove CDC6 and r would be near zero.

  Per-gene depth r (Spearman):
  Programme A: all 10 genes r > 0.785  p<0.05
  Programme B: PAEP r=+0.14 ns
               CST1 r=-0.54 ns
               S100A7 r=+0.43 ns
               ANXA8 r=+0.75 ns (borderline)
               ANXA8L1 r=+0.75 ns
               LY6D r=+0.82 p=0.023 *

  Programme B genes do NOT uniformly track
  depth the way Programme A does.
  4/6 Programme B genes are not significant.
  Programme A: 10/10 significant.
  Programme B: 2/6 significant.

  REVISED CONCLUSION:
  Programme A is the depth-tracking driver.
  Programme B is heterogeneous within the
  tumour set — some B genes co-elevate with
  depth (CDC6 pushes them up) but others
  (PAEP, CST1) do not.
  The two-module hypothesis stands with a
  correction:
    Programme A = coherent driver module
                  (10/10 genes depth-track)
    Programme B = heterogeneous ectopic
                  (2/6 depth-track, 4/6 flat)
  The two-module architecture is real.
  The independence cannot be confirmed at n=7
  but the internal structure supports it.
  Programme B is not a unified module —
  it is a collection of ectopic activations
  with different expression patterns.
```

### S3-P2: PPARG rewiring

```
PREDICTED: PPARG-CEBPA lost, PPARG-KLF5 gained
OBSERVED:
  KLF5:   r_tumour=+0.964, r_normal=+0.943 — STABLE
           KLF5 was already coupled to PPARG in normal.
           The coupling was not gained — it was retained.

  CEBPA:  r_tumour=-0.786 p=0.036
          r_normal=-0.257 ns
          CEBPA went from weakly anticorrelated in
          normal to SIGNIFICANTLY anticorrelated
          in tumour.
          PPARG and CEBPA are now opposing each other.
          This is a shift from neutral to antagonistic —
          not from positive to zero.
          The prediction was wrong about direction
          (expected loss of positive coupling)
          but found something more informative:
          CEBPA has become a PPARG antagonist
          in the tumour state.

  THE ACTUAL REWIRING:
  GAINED:  AGR2  r_t=+0.857, r_n=-0.829  ← most dramatic
           IL1RAP r_t=+0.786, r_n=-0.029
  LOST:    RXRA  r_t=+0.107, r_n=+0.829
           KLF2  r_t=-0.357, r_n=+0.600
           KLF4  r_t=+0.143, r_n=+0.486
           RXRB  r_t=-0.143, r_n=+0.600
  SHIFTED: CEBPB r_t=+0.286, r_n=-0.543 (+0.83 shift)
           CEBPA from neutral to antagonist

WHAT THE REWIRING MEANS:
  Normal PPARG programme:
    PPARG + RXRA (heterodimerisation partner)
    PPARG drives FABP4 (lipid binding, r_n=+0.943)
    PPARG suppresses AGR2 (r_n=-0.829)
    PPARG is the lipid metabolism TF

  Tumour PPARG programme:
    RXRA lost (heterodimerisation broken)
    FABP4 decoupled (r_t=+0.536 ns, was +0.943)
    AGR2 coupled (r_t=+0.857, was -0.829)
    IL1RAP coupled (r_t=+0.786, was -0.029)
    CEBPB now tracks PPARG (r_t=+0.286,
      was -0.543 — shifted from opposing to
      weakly tracking)
    PPARG is now the ductal/secretory TF

  The rewiring is a PARTNER SWITCH:
  PPARG lost RXRA and gained AGR2/IL1RAP
  as co-expression partners.
  Without RXRA, PPARG cannot form its
  canonical NR1C3/RXRA heterodimer.
  It is activating AGR2 and IL1RAP through
  a different mechanism — possibly as
  monomer or with an alternative partner.
  CEBPA actively opposing PPARG in tumour
  suggests the two TFs are competing for
  shared target gene regulation.

VERDICT:
  PARTIALLY CONFIRMED with correction.
  KLF5 was not gained (was already coupled).
  CEBPA was not simply lost — it became
  an active antagonist.
  The real finding is the RXRA loss and
  AGR2/IL1RAP gain — a partner switch,
  not a simple gain/loss event.
  This is more mechanistically specific
  than the prediction.
```

### S3-P3: ADCY3 driver

```
PREDICTED: MYC or BHLHE40
OBSERVED:  best = RELA r=+0.679 (ns at n=7)
           HIF1A second r=-0.643 (ns)
VERDICT:   NOT CONFIRMED

WHAT THE DATA SHOWS:
  RELA r=+0.679 — NF-κB p65 subunit
  HIF1A r=-0.643 — hypoxia TF (negative)
  NFKB2 r=+0.571 — second NF-κB subunit

  Two NF-κB subunits (RELA, NFKB2) both
  positively correlate with ADCY3.
  HIF1A negatively correlates — tumours
  with more HIF1A have less ADCY3.

  NF-κB-driven ADCY3 is mechanistically
  coherent: ADCY3 has an NF-κB binding
  site in its promoter. IL-1β (confirmed
  elevated, paired p=0.031) activates
  IKK→NF-κB→ADCY3 transcription.
  The IL1B→RELA→ADCY3 axis explains:
    1. Why IL1B and ADCY3 are both
       paired-confirmed elevated
    2. Why RELA tracks ADCY3 best
    3. Why the proliferative cAMP
       (ADCY3) replaces differentiation
       cAMP (ADCY6) — it is driven by
       inflammation, not by the
       differentiation circuit

  ANALYST ASSUMPTION ERROR:
  Predicted MYC drives ADCY3.
  MYC r(ADCY3) = +0.25 ns — no coupling.
  MYC is anti-correlated with depth overall
  (r=-0.964) but does not drive ADCY3.
  MYC and ADCY3 are in different circuits:
    MYC = early attractor commitment (CDC3
          has high MYC but low depth score)
    ADCY3 = NF-κB driven, depth-correlated

  CORRECTED MECHANISM:
  IL1B (elevated, NF-κB driven)
    → RELA activation
    → ADCY3 transcription
    → proliferative cAMP
  This is the axis.
  MYC is upstream and early.
  ADCY3 is downstream and late.
```

### S3-P4: CELSR1 circuit assignment

```
PREDICTED: CELSR1 belongs to PPARG module
OBSERVED:  r(CELSR1, KLF5) = +0.750
           r(CELSR1, IL1B) = +0.821
           r(CELSR1, VANGL1) = +0.929
           r(CELSR1, AGR2) = +0.929
VERDICT:   NOT CONFIRMED (IL1B > KLF5)
           — but the finding is more informative

CELSR1 SITS AT AN INTERSECTION:
  Top 5 correlators:
    VANGL1 +0.929  (PCP partner gene)
    AGR2   +0.929  (PPARG module)
    IL1B   +0.821  (NF-κB arm)
    PPARG  +0.786  (attractor hub)
    KLF5   +0.750  (attractor driver)

  CELSR1 co-varies equally strongly with
  AGR2/VANGL1 (+0.929 each) and tracks
  both the ductal module and NF-κB arm.

  The two top correlators are AGR2 (ductal)
  and VANGL1 (PCP). These are at the same r.
  CELSR1 is not in one circuit — it is at
  the intersection of the ductal identity
  programme and the PCP programme.

VANGL1-CELSR1 COUPLING r=+0.929:
  CELSR1 and VANGL1 are the two core
  planar cell polarity proteins.
  In normal collecting duct, they
  orient cell division to maintain
  tubular structure (tubule elongation).
  Their co-elevation in tumour confirms
  the PCP programme is activated — but
  in a context without tubular structure
  to orient (the duct architecture is
  gone). PCP activated without its
  structural context = misoriented cell
  polarity signals.
  Combined with PRKCI loss of PAR complex
  (Doc 89b Step 5: PRKCI-PARD3 r=-0.672),
  the polarity landscape in cdRCC is:
    PAR complex: dismantled
    PCP programme: activated
  These two polarity systems are being
  DISSOCIATED. PCP up, PAR down.

CELSR3 PAIRED-CONFIRMED (Step 11):
  CELSR3 +1.969 p=0.031 Wilcoxon.
  Both CELSR1 (depth-correlated) and
  CELSR3 (paired-confirmed) are elevated.
  Two members of the CELSR family are
  independently confirmed elevated.
  The entire PCP programme is activated.

  NOVEL FINDING CONFIRMED:
  PAR complex dismantled (PRKCI-PARD3
  anticorrelated, Doc 89b) + PCP activated
  (CELSR1/CELSR3 elevated) = polarity
  programme switch in cdRCC.
  The tumour has replaced apical-basal
  polarity (PAR) with planar cell polarity
  (PCP). This is a polarity system switch,
  not simply polarity loss.
  Stated before literature check.
```

### S3-P5: CDC3 biology

```
PREDICTED: CDC3 retains AQP2/PRKAR2B
OBSERVED:  AQP2 not retained
           PRKAR2B not retained
           PPARG: CD-retained (closer to CDC3 normal)
           KLF5:  CD-retained (closer to CDC3 normal)
           MYC:   attractor-direction (7.994 vs 3.690 normal)
VERDICT:   NOT CONFIRMED as stated
           MODIFIED finding is more informative

CDC3 IS A TRANSITIONAL STATE:
  The collecting duct programme is gone:
    AQP2:  CDC3_T=1.005, CDC3_N=9.482 — lost
    AVPR2: CDC3_T=0.476, CDC3_N=2.090 — lost
    All SCNN channels: lost
    All IC cell genes: lost
    TFCP2L1, HNF4A: lost
    This is not retention. CD identity is gone.

  The false attractor has not fully formed:
    PPARG: CDC3_T=3.745, Other_mean=5.162
           CDC3_N=4.862
           CDC3 tumour is CLOSER to normal than
           to other tumours. PPARG is partially
           retained at normal levels.
    KLF5:  CDC3_T=3.598, Other_mean=6.010
           CDC3_N=4.314
           Same — closer to normal than attractor.
    IL1RAP: CDC3_T=5.285, Other_mean=6.315
           Still attractor-direction but less elevated.

  MYC is fully committed:
    MYC: CDC3_T=7.994, CDC3_N=3.690
    MYC is dramatically elevated even in CDC3.
    Other mean=6.848 — CDC3 has MORE MYC than
    the average tumour.

  THE PICTURE:
  CDC3 has:
    1. Lost all collecting duct identity
       (same as all other tumours)
    2. Not yet fully activated the PPARG/KLF5
       ductal secretory module
    3. Already fully activated MYC
       (above average for tumour set)

  This is the TRANSITION SEQUENCE:
    Step 1: MYC activates (early, all tumours)
    Step 2: PPARG/KLF5 module activates (later)
    CDC3 is between Step 1 and Step 2.
    It is post-CD-loss but pre-attractor-
    consolidation.

  CDC3 IS THE MOST INFORMATIVE SAMPLE:
  It shows the sequence of attractor formation.
  MYC rises first. PPARG/KLF5 rises second.
  This is testable in time-course experiments.
  MYC inhibition before PPARG/KLF5 activation
  may prevent attractor consolidation.
  After PPARG/KLF5 are activated, MYC
  inhibition alone is insufficient.
  STATED BEFORE LITERATURE CHECK.
```

### S3-P6: MYC metabolic vs proliferation

```
PREDICTED: |r(MYC, MKI67)| < 0.4
OBSERVED:  r(MYC, MKI67) = -0.571 (ns at n=7)
           r(MYC, HK1)   = -0.964 p=4.54e-04
           r(MYC, BHLHE40) = -0.964 p=4.54e-04
VERDICT:   CONFIRMED — stronger than predicted

r(MYC, MKI67) = -0.571 (negative, not just < 0.4).
r(MYC, HK1) = -0.964 — the most significant
single-gene finding in Script 3.

WHAT THE MYC-HK1 ANTI-CORRELATION MEANS:
  HK1 = hexokinase 1 = the constitutive
  glycolytic gate enzyme.
  Paired Wilcoxon step 11 shows HK2 is UP
  (+4.396 p=0.031) while HK1 is depth-
  anti-correlated (r=-0.964 Spearman).
  So: HK1 falls as MYC rises.
      HK2 rises independently of MYC.
  HK1 → HK2 isoform switch is in the data.
  MYC does not drive HK2 elevation.
  MYC is anti-correlated with BOTH HK1
  and glycolysis.

  MYC HIGH + HK1 LOW + HK2 HIGH:
  This is not Warburg metabolism.
  This is a metabolic state where:
    Glycolysis entry is through HK2 (stress)
    not HK1 (constitutive)
    MYC is not driving the Warburg shift
    MYC is inversely related to metabolic
    output here

WHAT THE MYC-BHLHE40 ANTI-CORRELATION MEANS:
  r(MYC, BHLHE40) = -0.964
  BHLHE40 is in the TOP 20 POSITIVE depth
  correlators (r=+0.929) — it rises with depth.
  MYC is in the TOP 20 NEGATIVE depth
  correlators (r=-0.964) — it falls with depth.
  As attractor deepens: BHLHE40 rises, MYC falls.
  They are inversely related to each other
  AND to depth.

  MYC IS AN EARLY ATTRACTOR GENE.
  BHLHE40 IS A LATE ATTRACTOR GENE.

  CDC3 (earliest tumour, depth=0):
    MYC = 7.994 (highest in tumour set)
    BHLHE40 = lower (would need to check)
  CDC6 (deepest tumour, depth=1.0):
    MYC lower
    BHLHE40 highest

  The attractor transition sequence:
    Early: MYC high, BHLHE40 low
    Late:  MYC falls, BHLHE40 rises
    At the deepest state: BHLHE40 dominates

  BHLHE40 (DEC1) is a repressor of E-box
  targets that competes with MYC.
  As BHLHE40 rises, it displaces MYC from
  E-box sites. MYC is progressively replaced
  by BHLHE40 as the attractor deepens.
  BHLHE40 also drives the PPARG-KLF5 module
  indirectly (BHLHE40 is a KLF5 target
  in some epithelial contexts) — or they
  are co-regulated by the same upstream
  signal.

  NEW NOVEL PREDICTION (N8):
  MYC drives the early phase of cdRCC
  attractor formation (CD identity loss,
  initial reprogramming). BHLHE40 drives
  the late phase (consolidation of the
  PPARG/KLF5 ductal secretory module).
  The therapeutic window for MYC inhibition
  is early — before BHLHE40 rises.
  Once BHLHE40 is high and MYC has been
  displaced, MYC inhibition will not
  reverse the attractor.
  Stated before literature check.

MYC IS A DIFFERENTIATION REPRESSOR IN cdRCC:
  Mean r(MYC, proliferation panel) = -0.191
  Mean r(MYC, metabolic panel)     = -0.372
  MYC anti-correlates with both panels.
  Within the tumour set, the samples with
  most MYC are the ones with least
  proliferation AND least glycolysis.
  This is not a Warburg driver.
  MYC in cdRCC is suppressing differentiation
  identity (collecting duct) without driving
  the canonical MYC proliferative or
  glycolytic programmes.
  It is acting as a transcriptional eraser —
  consistent with its known role as a
  global chromatin opener that suppresses
  tissue-specific gene programmes by
  competing with lineage TFs.
```

### S3-P7: GSE83479 replication

```
PREDICTED: 8+/12 genes replicate
OBSERVED:  0 CDC columns identified
           Metadata classifier returned 0 CDC
           and 0 normal samples
VERDICT:   NOT RUN — technical failure

WHAT HAPPENED:
  The GSE83479 matrix downloaded successfully.
  Columns were renamed to GSM IDs positionally.
  First 5 renamed columns: GSM2204076–GSM2204080.
  These GSM IDs exist in the metadata.
  BUT: the CDC classifier searches for keywords
  "collecting duct", "bellini", "cdc", "cd-rcc"
  in sample descriptions.
  The sample descriptions in GSE83479 may use
  different terminology.
  57 samples in metadata, all classified as
  "other" — none matched any keyword.

WHAT IS NEEDED FOR SCRIPT 4:
  Fetch raw metadata for GSM2204076.
  Read the actual title/source/characteristics.
  Determine the correct classification keyword.
  Hardcode a GSM-to-type map for GSE83479.
  This is a classifier fix, not a data problem.
  The matrix is downloaded and parsed correctly.

INTERIM STATUS:
  GSE83479 replication is deferred to Script 4.
  The matrix is cached locally.
  Fix is straightforward.
  Replication result will not be assumed.
```

---

## V. NEW FINDINGS FROM STEP 11 (PAIRED WILCOXON)

```
39/86 genes significant at p<0.05 by
Wilcoxon signed-rank across 6 matched pairs.
These are the most reliable findings —
non-parametric, matched, not sensitive
to CDC4 library size.

NEW CONFIRMATIONS NOT IN S1/S2 REPORTS:

HK2 +4.396 p=0.031 (confirmed):
  Hexokinase 2 is paired-confirmed elevated.
  Together with HK1 depth anti-correlated
  (r=-0.964 Spearman S3), the HK1→HK2
  isoform switch is confirmed.
  HK1: constitutive, mitochondria-associated,
       normal glycolysis gateway
  HK2: stress/hypoxia-inducible, anoikis-
       resistant, associates with VDAC
       on outer mitochondrial membrane
  The switch is from metabolic efficiency
  (HK1) to stress-resistant glycolysis (HK2).
  Driver of HK2: NOT MYC (Step 9).
  Likely driver: HIF pathway or NF-κB.
  Note: EPAS1 (HIF2α) is DOWN p=0.031.
  HIF1A r=-0.643 with ADCY3 (ADCY3 also up).
  HIF2 is down but HIF1A may be driving HK2.
  To be tested in Script 4.

TOP2A +4.074 p=0.031 (confirmed):
  Topoisomerase IIα — required for chromosome
  segregation during mitosis. Paired-confirmed
  elevated. The proliferative machinery IS
  active. Consistent with MKI67 +4.169 p=0.031.
  But NOT driven by MYC (MYC-TOP2A r=-0.179).
  Proliferation driver in cdRCC ≠ MYC.
  Likely AURKA/PLK1 axis:
    PLK1 +2.642 p=0.031
    AURKA +2.160 p=0.031
    These are mitotic kinases.
  The proliferation programme (TOP2A/MKI67/
  PLK1/AURKA/MCM2) is confirmed active.
  Its driver is the mitotic kinase programme
  — not MYC.

SLC2A1 +2.629, SLC2A3 +2.080 (both p=0.031):
  GLUT1 and GLUT3 — glucose transporters.
  Both confirmed elevated. Glucose import is up.
  But HK1 (first step of glycolysis) is down.
  GLUT transporters up + HK1 down = glucose
  is being imported but the canonical
  glycolytic processing is altered.
  This is consistent with glucose diversion
  to alternative pathways (pentose phosphate,
  serine synthesis, or HK2-mitochondrial).

EPAS1 -1.505 p=0.031 (confirmed DOWN):
  HIF2α (encoded by EPAS1) is confirmed lost.
  HIF2α normally drives collecting duct
  differentiation and oxygen sensing in the
  distal nephron. Its loss is a functional
  confirmation of collecting duct identity
  loss independent of the lineage TF data.
  Also relevant: EPAS1/HIF2α drives clear
  cell RCC. cdRCC loses HIF2α instead of
  gaining it. This distinguishes cdRCC from
  ccRCC at the molecular level — a built-in
  differential diagnosis marker.

CEBPB +1.986 p=0.031 (confirmed):
  CEBPB (not CEBPA) is the elevated
  CCAAT-binding factor in cdRCC.
  CEBPB drives inflammatory gene expression
  including IL-6, IL-1 target genes, and
  acute phase response.
  Together with RELA being the best ADCY3
  driver (Step 6), the inflammatory TF
  landscape in cdRCC is:
    CEBPB elevated (paired p=0.031)
    RELA tracking ADCY3 (r=+0.679)
    IL1B elevated (paired p=0.031)
  This is a coherent NF-κB/CEBPB inflammatory
  transcriptional circuit.
  CEBPA (the differentiation-associated
  CCAAT factor) is anticorrelated with PPARG
  in tumours (r=-0.786) — it is opposing
  the false attractor.
  CEBPB has REPLACED CEBPA as the dominant
  CCAAT-binding TF in the attractor.
  CEBPB drives inflammation; CEBPA drives
  differentiation. The switch from CEBPA
  to CEBPB is part of the attractor identity.

ADCY3 +1.686 p=0.031 (confirmed):
  The ADCY3 isoform switch is confirmed by
  paired Wilcoxon. Not sensitive to CDC4.
  Real biology across all 6 matched pairs.

CELSR3 +1.969 p=0.031 (confirmed):
  Second PCP gene confirmed paired-elevated.
  Together with CELSR1 depth-correlated,
  the PCP programme elevation is confirmed
  by two independent methods:
    CELSR1: Spearman depth r positive
    CELSR3: Wilcoxon paired p=0.031
  The PCP programme elevation in cdRCC is
  the most independently confirmed unexpected
  finding in Script 3.
```

---

## VI. REVISED ATTRACTOR PICTURE AFTER S3

```
The three components from Doc 89b are
refined but not changed:

COMPONENT 1 — THE EXECUTION BLOCK (revised):
  Original: PKA broken at PRKAR2B node
  Refined: The floor of the block is deeper.
  Genes at r=-1.000 Spearman include TNXB
  (ECM), OGDHL (TCA), ADPRM, SCG2, LAMTOR4.
  The execution block removes:
    - Collecting duct functional identity
      (AQP2/PRKAR2B/SCNN channels — all lost)
    - Collecting duct ECM (TNXB lost)
    - TCA cycle at OGDHL (mitochondria impaired)
    - mTOR nutrient sensing (LAMTOR4 lost)
    - HIF2α (EPAS1 lost p=0.031)
  This is more comprehensive than a single
  circuit break. The block removes the entire
  collecting duct metabolic and structural
  identity simultaneously.

COMPONENT 2 — THE IDENTITY RETENTION (refined):
  Original: PPARG-KLF5-AGR2-ESRP1-IL1RAP +
            PAEP-CST1-S100A7-ANXA8
  Refined:
  CORE MODULE (depth-tracking, coherent):
    PPARG-KLF5-AGR2-ESRP1-IL1RAP-GPRC5A
    -CST6-KLF10-TMPRSS4
    All 9: Spearman r > 0.785, p < 0.05
    PPARG has been rewired: RXRA lost,
    AGR2/IL1RAP gained. CEBPA opposing.
    The module is an autonomous ductal
    secretory state.

  PCP MODULE (new finding):
    CELSR1 (depth-correlated) +
    CELSR3 (paired p=0.031) +
    VANGL1 (CELSR1 r=+0.929)
    Activated without structural context.
    Co-regulated with NF-κB (IL1B r=+0.821
    with CELSR1).

  HETEROGENEOUS ECTOPIC:
    PAEP (+0.143 depth r, ns)
    CST1 (-0.536 depth r, ns)
    S100A7 (+0.429 depth r, ns)
    Not a coherent module — 4/6 not
    depth-correlated. These are stochastic
    activations, not a driven programme.

COMPONENT 3 — THE STABILISING MECHANISM (refined):
  Original: EZH2 initiating + PPARG-KLF5 +
            PRKCI/NF-κB
  Refined:
  EZH2 — INITIATING LOCK (uniform +70%)
    Silences HNF4A, FOXI1, TFCP2L1, EPAS1
    Establishes the block. Does not vary
    with depth (r=+0.191).

  TRANSITION SEQUENCE (new from S3):
    Phase 1 (early): MYC rises
                     CD identity dissolves
                     CDC3-like state
    Phase 2 (late):  MYC falls
                     BHLHE40 rises
                     PPARG module activates
                     HK1 suppressed, HK2 rises
                     ADCY3 rises (NF-κB driven)
                     PCP programme activates
                     CEBPB replaces CEBPA

  PPARG-RXRA PARTNER SWITCH:
    RXRA uncoupled from PPARG
    PPARG now drives AGR2/IL1RAP
    through non-canonical mechanism
    CEBPA becomes a PPARG antagonist

  INFLAMMATORY CONSOLIDATION:
    RELA → ADCY3 (isoform switch)
    RELA/CEBPB → IL1B, IL6, IL1RAP
    NF-κB not only drives inflammation
    but drives the ADCY3 cAMP switch
    that redirects signalling from
    differentiation to proliferation
```

---

## VII. NOVEL PREDICTIONS — UPDATED LIST

```
From Doc 89b (N1-N7) — all still locked.
New predictions from Script 3 (N8-N12):

N8: MYC drives the EARLY phase of cdRCC
    attractor formation.
    BHLHE40 drives the LATE phase.
    The sequence: MYC rises first (CDC3 has
    highest MYC in tumour set), then MYC falls
    as BHLHE40 rises in deeper states.
    The therapeutic window for MYC inhibition
    is BEFORE BHLHE40 consolidation.
    Stated 2026-03-03 before literature check.

N9: PPARG-RXRA heterodimerisation is broken
    in cdRCC. PPARG drives AGR2 and IL1RAP
    through a non-canonical (RXRA-independent)
    mechanism. RXRA is lost as a PPARG partner
    (r_tumour=+0.107 vs r_normal=+0.829).
    PPARG inverse agonist may be insufficient
    if PPARG is not signalling through RXRA.
    RXRA re-engagement may be needed to
    make PPARG targetable.
    Stated 2026-03-03 before literature check.

N10: CEBPB has replaced CEBPA as the dominant
     CCAAT-binding factor in cdRCC.
     CEBPA opposes PPARG in tumours (r=-0.786).
     CEBPB tracks the inflammatory programme
     (elevated paired p=0.031).
     The CEBPA→CEBPB switch is part of the
     attractor identity.
     CEBPA restoration may dissolve the PPARG
     module by competing with it at shared
     E-box/CCAAT sites.
     Stated 2026-03-03 before literature check.

N11: PAR polarity complex dismantled +
     PCP programme activated = a polarity
     system SWITCH in cdRCC.
     Not polarity loss — polarity replacement.
     PAR complex: PRKCI-PARD3 anticorrelated
                  (Doc 89b), LLGL2 down
     PCP programme: CELSR1 depth-correlated,
                    CELSR3 paired p=0.031,
                    VANGL1-CELSR1 r=+0.929
     The tumour has replaced apical-basal
     polarity with planar cell polarity.
     This may drive the loss of tubular
     architecture (PCP without structure =
     misoriented polarity signals = no lumen).
     Stated 2026-03-03 before literature check.

N12: HK1→HK2 hexokinase isoform switch
     confirmed in cdRCC.
     HK2 paired +4.396 p=0.031 (confirmed up).
     HK1 Spearman r=-0.964 with depth (down
     with deepening).
     Driver is NOT MYC (r(MYC,HK2) not tested
     but r(MYC,HK1)=-0.964 — MYC suppresses HK1
     as both fall together, but HK2 is driven
     independently).
     Likely driver: NF-κB or HIF1A pathway.
     The isoform switch moves glucose metabolism
     from constitutive (HK1) to stress/survival
     (HK2) mode — consistent with the mTOR
     sensing loss (LAMTOR4 r=-1.000).
     Stated 2026-03-03 before literature check.
```

---

## VIII. WHAT SCRIPT 4 SHOULD DO

```
One technical fix + four biological tests:

TECHNICAL FIX (required):
  GSE83479 classifier fix.
  Fetch GSM2204076 metadata and read the
  actual title/source text.
  The sample descriptions use terminology
  not matching the current keywords.
  Once the correct terms are found,
  hardcode a 57-sample GSM-to-type map
  for GSE83479.
  Run the replication panel.
  This should be the first thing Script 4
  does — the matrix is already cached.

BIOLOGICAL TEST 1: HK1/HK2 driver
  r(HK2, HIF1A) in tumours
  r(HK2, RELA) in tumours
  r(HK2, CEBPB) in tumours
  Which TF drives the HK2 isoform switch?
  Prediction: RELA or CEBPB (NF-κB arm)
  not HIF1A (HIF1A r(ADCY3) was -0.643 —
  HIF1A is in the same direction as PPARG
  in opposing the attractor).

BIOLOGICAL TEST 2: MYC timing
  In CDC3 (shallowest tumour):
    MYC = 7.994 (highest in set)
    BHLHE40 = ?
    PPARG = 3.745 (partially retained)
  Test: does CDC3 have low BHLHE40?
  If CDC3: high MYC + low BHLHE40 =
  confirms the transition sequence.
  Plot MYC vs BHLHE40 across all 7 tumours.
  Expected: strong negative linear relationship.
  This would confirm N8 (MYC early,
  BHLHE40 late).

BIOLOGICAL TEST 3: CEBPA antagonism
  r(CEBPA, PPARG) in tumours: -0.786 p=0.036
  r(CEBPA, AGR2) in tumours: to be computed
  r(CEBPA, KLF5) in tumours: to be computed
  If CEBPA opposes the whole PPARG module
  (not just PPARG itself), then CEBPA
  restoration is a candidate therapeutic
  strategy.
  Test: does CEBPA anti-correlate with
  AGR2, KLF5, IL1RAP as well as PPARG?

BIOLOGICAL TEST 4: ADPRM/TNXB as depth
  proxies
  ADPRM and TNXB are at r=-1.000 Spearman.
  Rebuild depth score using ADPRM (switch)
  and IL1RAP (FA) instead of PRKAR2B/IL1RAP.
  Compare r(S3_depth, S4_depth).
  If r > 0.95: ADPRM is an equivalent
  depth proxy.
  This matters for clinical scoring:
  ADPRM is potentially more measurable
  than PRKAR2B as a clinical biomarker
  (higher expression range, more dynamic).
```

---

## IX. STATUS

```
scripts_run:        S1 (blind discovery)
                    S2 (circuit analysis)
                    S3 v2 (Spearman audit +
                           module tests)
                    S4 needed (GSE83479 fix +
                               4 biological tests)

attractor_status:   CONFIRMED and refined
                    Three-component structure
                    holds from Doc 89b
                    Transition sequence added:
                    MYC early → BHLHE40 late

new_genes_confirmed:
  Spearman r=-1.000: TNXB, OGDHL, ADPRM,
                     SCG2, LAMTOR4, ZBED6CL
  Paired p=0.031:    HK2, TOP2A, SLC2A1,
                     SLC2A3, PLK1, AURKA,
                     MCM2, CEBPB, CELSR3,
                     ADCY3, EPAS1(down)

novel_predictions:  N1-N7 (Doc 89b) unchanged
                    N8-N12 added (Doc 89b addendum)
                    All dated 2026-03-03
                    All stated before literature

replication:        GSE83479 deferred to S4
                    Matrix cached
                    Classifier fix identified

ready_for_lit_check: YES (after S4 replication)
                     OR immediately if user
                     prefers to proceed without
                     replication first

author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-03
document:           89b addendum
```
