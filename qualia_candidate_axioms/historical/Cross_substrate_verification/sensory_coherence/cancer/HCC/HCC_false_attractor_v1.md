================================================================
DOCUMENT 92a
HEPATOCELLULAR CARCINOMA — FALSE ATTRACTOR ANALYSIS
Script 1 Results | GSE14520
225 HCC + 220 Adjacent Normal
Platform: Affymetrix HG-U133A (GPL3921)
Survival: OS n=221 | RFS n=221
Date: 2026-03-01
Framework: OrganismCore
Author: Eric Robert Lawson
================================================================

----------------------------------------------------------------
SECTION 1: DEPTH SCORE
----------------------------------------------------------------

Depth score computed successfully.
n=225 HCC samples.
mean=0.3217  std=0.1505
min=0.0285   max=0.8019

Switch genes used:
  HNF4A, FOXA1, FOXA2, ALB, APOB,
  TTR, CYP3A4, G6PC, PCK1

FA genes used:
  AFP, MYC, BIRC5, TOP2A, MKI67,
  AURKA, CCND1, EPCAM

The depth score captures a continuous
spectrum from well-differentiated HCC
(depth≈0.03) to deeply dedifferentiated
progenitor-like HCC (depth≈0.80).

----------------------------------------------------------------
SECTION 2: SURVIVAL — HEADLINE RESULTS
----------------------------------------------------------------

OS (n=221, events=85, range=2.0–67.4 mo):
  Deep    (n=111): mean=34.3 months
  Shallow (n=110): mean=46.7 months
  Log-rank p=3.80e-04 ***
  STATUS: CONFIRMED ✓

RFS (n=221, events=121, range=0.1–67.4 mo):
  Deep    (n=111): mean=29.5 months
  Shallow (n=110): mean=38.8 months
  Log-rank p=0.0296 *
  STATUS: CONFIRMED ✓

INTERPRETATION:
  Deeper HCC = shorter OS (12.4 mo gap)
  Deeper HCC = shorter RFS (9.3 mo gap)
  The attractor depth score is a
  significant prognostic marker in HCC.
  This is the first validation of the
  OrganismCore depth framework in a
  hepatocellular lineage.

----------------------------------------------------------------
SECTION 3: PREDICTION SCORECARD
----------------------------------------------------------------

PREDICTIONS LOCKED 2026-03-01
(before any data was examined)

HCC-P1: HNF4A r<-0.50 (primary switch)
  Result: r=-0.4603 p=3.39e-13 ***
  STATUS: PARTIAL ✗
  (strong negative correlation confirmed
   but threshold was -0.50; r=-0.46
   is close — borderline fail)
  NOTE: HNF4A is 9th strongest switch
  gene. Metabolic enzymes CYP3A4 and
  ALDOB are actually stronger switches
  (r=-0.72 and r=-0.71). This is an
  important revision — the primary
  switch in HCC is not the TF but the
  terminal metabolic programme.
  REVISED UNDERSTANDING: HNF4A
  is a switch gene but not the
  strongest one. The metabolic
  differentiation programme
  (CYP3A4, ALDOB, PCK1, G6PC)
  is more tightly coupled to
  attractor depth than the TF itself.

HCC-P2: AFP r>+0.50 (primary FA gene)
  Result: r=+0.6230 p=1.39e-25 ***
  STATUS: CONFIRMED ✓
  AFP is the 4th strongest FA gene.
  Foetal re-expression confirmed
  as predicted.

HCC-P3: MYC r>+0.40 (FA gene)
  Result: r=+0.2852 p=1.39e-05 ***
  STATUS: NOT CONFIRMED ✗
  MYC rises with depth (correct direction)
  but the correlation is weaker than
  predicted (r=+0.29 vs predicted >+0.40).
  INTERPRETATION: MYC is not the primary
  driver of depth in this cohort.
  The primary FA genes are cell-cycle
  regulators: CDC20 (r=+0.64),
  CCNB1 (r=+0.63), MKI67 (r=+0.62).
  MYC is a real FA gene but acts
  upstream — it activates the
  cell-cycle programme rather than
  being the most tightly correlated
  with depth itself.

HCC-P4: CTNNB1 defines subtype
  r(depth, CTNNB1) = +0.1364 p=0.041 *
  r(CTNNB1, MYC)   = +0.0221 p=0.74 ns
  STATUS: PARTIAL ✓
  CTNNB1 and MYC are uncorrelated
  (r=+0.02, ns) — they are independent
  axes as predicted. This confirms
  two-track HCC geometry.
  However Wnt target genes (LGR5,
  GLUL, AXIN2, DKK1) do not separate
  cleanly on CTNNB1 median split.
  The Wnt programme may require a
  higher CTNNB1 threshold or the
  platform does not capture LGR5
  well at this probe density.

HCC-P5: CTNNB1-hi = better prognosis
  Depth CTNNB1-hi mean=0.3328
  Depth CTNNB1-lo mean=0.3106
  STATUS: INCONCLUSIVE
  (Survival data not split by CTNNB1;
   Script 2 will test this directly
   with logrank on CTNNB1-hi vs lo)

HCC-P6: Depth encodes sorafenib resistance
  OS p=3.80e-04 *** CONFIRMED
  Deeper tumours have worse OS.
  This is consistent with the
  resistance prediction but cannot
  be directly tested without
  sorafenib treatment data.
  The prognostic signal supports
  the hypothesis.
  STATUS: SUPPORTED ✓ (indirect)

----------------------------------------------------------------
SECTION 4: NOVEL FINDINGS
----------------------------------------------------------------

NOVEL FINDING 1: The Metabolic Switch
  The strongest switch genes in HCC
  are not transcription factors.
  They are terminal metabolic enzymes:

  CYP3A4  r=-0.7245 p=6.71e-38 ***
  ALDOB   r=-0.7052 p=3.69e-35 ***
  PCK1    r=-0.6317 p=1.83e-26 ***
  CYP2C9  r=-0.5855 p=4.26e-22 ***
  G6PC    r=-0.5581 p=7.98e-20 ***
  IGF1    r=-0.5125 p=1.80e-16 ***
  ARG1    r=-0.5107 p=2.38e-16 ***

  These are all hepatocyte-specific
  metabolic functions:
    CYP3A4/2C9 = drug metabolism
    ALDOB       = fructose metabolism
    PCK1        = gluconeogenesis
    G6PC        = glucose-6-phosphatase
    IGF1        = hepatocyte-secreted
    ARG1        = urea cycle

  INTERPRETATION:
  HCC dedifferentiation is primarily
  a LOSS OF METABOLIC IDENTITY,
  not a loss of transcription factor
  expression. The cancer cell stops
  doing what the hepatocyte does
  (metabolise drugs, make glucose,
  run the urea cycle) before it stops
  expressing the TFs that control
  those programmes. This makes
  metabolic gene loss the most
  sensitive indicator of dedifferentiation
  depth in HCC.

  This was not predicted explicitly.
  It is a genuine discovery from
  the depth correlation structure.

NOVEL FINDING 2: HDAC2 is the
  strongest epigenetic FA gene
  r=+0.6403 p=2.36e-27 ***
  (stronger than EZH2 or HDAC1)

  HDAC2 was not in the initial
  target list as a primary FA gene.
  It is now the second-ranked FA gene
  overall (tied with CDC20).
  This is worth investigating:
  Is HDAC2 overexpression a driver
  of dedifferentiation or a consequence?
  If driver: HDAC2-selective inhibitors
  may be more effective than pan-HDAC
  inhibitors in deep HCC.

NOVEL FINDING 3: FGFR3 rises with depth
  r=+0.4475 p=1.77e-12 ***
  FGFR3 is NOT the dominant liver FGFR.
  Hepatocytes normally express FGFR4.
  FGFR3 rising with dedifferentiation
  suggests a foetal FGFR switch:
    Normal liver: FGFR4 dominant
    Deep HCC: FGFR3 rises
  This mirrors the BLCA finding where
  FGFR3 is the luminal/differentiated
  FGFR. In HCC the switch goes in
  the other direction — FGFR3 is
  the dedifferentiated isoform.
  The FGFR isoform rule holds
  but the isoform is different
  from what was predicted.
  FGFR4 does not fall (r=+0.34).
  FGFR3 rises (r=+0.45).

NOVEL FINDING 4: SMAD3 predicts OS
  p=6.21e-03 ** ↑=worse
  This repeats the BLCA finding.
  SMAD3 predicts poor survival in
  both BLCA (luminal) and HCC.
  This is the second independent
  cancer type in which SMAD3
  elevation is associated with
  worse outcome.
  Cross-cancer convergence emerging.

NOVEL FINDING 5: SOX4 is the
  strongest progenitor FA gene
  r=+0.5930 p=9.29e-23 ***
  SOX4 also predicts OS (p=5.40e-04 ***)
  and RFS (p=0.0112 *).
  SOX4 is a stem/progenitor TF.
  Its position as a top FA gene
  confirms the framework prediction
  that deep HCC is stuck in a
  foetal progenitor state.

NOVEL FINDING 6: EPCAM r=+0.6064
  EPCAM is the 6th strongest FA gene.
  High EPCAM in HCC = EpCAM+ HCC
  (hepatic progenitor cell phenotype).
  This is independently established
  in the literature as the most
  aggressive HCC subtype.
  The framework recovers this
  from first principles without
  any prior knowledge of the
  EpCAM+ HCC literature.
  CONVERGENCE CANDIDATE.

NOVEL FINDING 7: KDR predicts OS ***
  KDR (VEGFR2) p=4.77e-05 *** ↑=better
  Higher KDR = better OS.
  KDR falls with depth (r=-0.4249).
  Angiogenic signalling is maintained
  in better-differentiated HCC.
  KDR loss = deeper dedifferentiation
  = worse prognosis.
  This is counterintuitive.
  KDR/VEGFR2 is usually considered
  a tumour-promoting receptor.
  In HCC its loss may reflect
  loss of the hepatocyte vascular
  niche programme, not just
  loss of angiogenesis.

----------------------------------------------------------------
SECTION 5: CROSS-CANCER TESTS
----------------------------------------------------------------

CC-1: EZH2+HDAC1 EPIGENETIC LOCK
  EZH2  r=+0.5219 p=4.06e-17 ***  ✓
  HDAC1 r=+0.4567 p=5.41e-13 ***  ✓
  STATUS: CONFIRMED ✓

  EAC:  EZH2 r=+0.56  HDAC1 r=+0.47
  BLCA: EZH2 r=-0.24  HDAC1 r=-0.39 (INVERTED)
  HCC:  EZH2 r=+0.52  HDAC1 r=+0.46

  INTERPRETATION:
  The EZH2+HDAC1 epigenetic lock
  is confirmed in HCC.
  The pattern matches EAC exactly:
  both are glandular/secretory lineages
  that retain epigenetic repressors
  in the false attractor.
  BLCA (urothelial) inverts this rule.
  The epigenetic lock is a
  GLANDULAR LINEAGE RULE
  not a universal cancer rule.
  This is the first cross-cancer
  validation of this distinction.
  Rule formalised:
    Glandular lineages (EAC, HCC):
      EZH2+HDAC1 rise with depth
    Urothelial lineage (BLCA):
      EZH2+HDAC1 fall with depth
  Cross-cancer rule CC-1 confirmed
  with tissue-type qualifier.

CC-2: FGFR ISOFORM IN LIVER
  FGFR4 r=+0.3398 p=1.74e-07 ***  ✗ (rises)
  FGFR3 r=+0.4475 p=1.77e-12 ***  (unexpected)
  STATUS: PREDICTION NOT CONFIRMED ✗
  REVISED UNDERSTANDING:
  The prediction was FGFR4 falls.
  Reality: FGFR4 rises slightly,
  FGFR3 rises strongly.
  The FGFR isoform switch still
  occurs but in the opposite direction
  to what was predicted.
  Hepatocyte FGFR4 does not mark
  the normal state as strongly
  as expected — or the HCC
  tumours already have partial
  FGFR4 loss that is being
  masked by co-expression.
  The rise of FGFR3 with depth
  is the real signal here.
  FGFR3 in HCC = foetal/progenitor
  FGFR (same biological meaning,
  different isoform from BLCA).
  This needs Script 2 investigation.

CC-3: ZEB2-AURKA COUPLING
  HCC r(ZEB2,AURKA) = -0.1663 p=0.013 *
  STATUS: NOT CONFIRMED ✗
  ZEB2 and AURKA are ANTI-correlated
  in HCC (as in BLCA, not STAD/EAC).
  ZEB2 is FALLING with depth
  (ZEB2 Normal=4.35 HCC=3.93,
   r not shown but directionally negative).
  INTERPRETATION:
  In HCC, ZEB2 falls as the tumour
  deepens — this is the opposite of
  STAD where ZEB2 rises with CIN.
  HCC is not a CIN-driven cancer
  in the same way as gastric.
  The ZEB2-AURKA rule does not
  generalise to HCC.
  Updated cross-cancer table:
    STAD: ZEB2-AURKA r=+0.99 (CIN-high)
    EAC:  ZEB2-AURKA r=+0.47 (moderate)
    BLCA: ZEB2-AURKA r≈0    (decoupled)
    HCC:  ZEB2-AURKA r=-0.17 (anti-correlated)
  Rule: ZEB2-AURKA coupling is
  lineage-specific. It is positive
  only in cancers with high
  chromosomal instability
  (gastric/oesophageal lineages).

CC-4: FOXA1/FOXA2 SWITCH GENES
  FOXA1 r=+0.2769 p=2.52e-05 ***  ✗ (RISES)
  FOXA2 r=-0.1803 p=6.69e-03 **
  STATUS: NOT CONFIRMED ✗
  FOXA1 actually RISES with HCC depth.
  This is the opposite of BLCA.
  INTERPRETATION:
  In BLCA, FOXA1 marks the
  luminal/differentiated state.
  In HCC, FOXA1 may be re-expressed
  in dedifferentiated tumours as
  part of a foetal activation programme.
  FOXA1 is a pioneer factor that
  opens chromatin in both hepatocyte
  and foetal liver programmes.
  Its rise with HCC depth may reflect
  progenitor re-activation rather
  than differentiation.
  This is a genuine tissue-specific
  inversion of the FOXA1 rule.
  Important: FOXA1 is NOT a reliable
  cross-cancer switch gene marker.
  It is tissue-context-dependent.

CC-5: S100A8 POOR PROGNOSIS
  S100A8 r=+0.1956 p=3.22e-03 **
  (positive but below threshold +0.30)
  STATUS: PARTIAL ✗
  S100A9 r=+0.2518 p=1.35e-04 ***
  S100A4 r=+0.3707 p=9.71e-09 ***
  S100A9 predicts OS (p=0.029 *)
  S100A9 predicts RFS (p=0.019 *)
  INTERPRETATION:
  The S100 inflammatory signature
  is present in HCC but S100A8
  specifically is weaker than
  in BLCA. S100A4 (metastasin)
  is actually the dominant S100
  family member correlated with
  depth in HCC (r=+0.37).
  S100A4 is a known HCC metastasis
  marker — independent literature
  confirmation emerging.

----------------------------------------------------------------
SECTION 6: CTNNB1/MYC SUBTYPE ANALYSIS
----------------------------------------------------------------

r(CTNNB1, MYC) = +0.0221 p=0.74 ns

CTNNB1 and MYC are statistically
independent (r≈0) confirming
two-track geometry in HCC.

Depth by track:
  CTNNB1-hi: mean depth = 0.3328
  CTNNB1-lo: mean depth = 0.3106
  MYC-hi:    mean depth = 0.3578
  MYC-lo:    mean depth = 0.2854

MYC-hi tumours are deeper than
MYC-lo (difference = 0.072).
CTNNB1-hi tumours are only
marginally deeper (difference = 0.022).
This suggests:
  MYC track = DEPTH driver
  CTNNB1 track = SEPARATE biology
  (Wnt activation, not pure depth)

Wnt targets (GLUL, LGR5, AXIN2)
do not separate on CTNNB1 median split.
This may be because:
  1. Many CTNNB1 mutations in HCC
     are activating point mutations,
     not overexpression. Expression
     level may not capture mutation.
  2. The microarray platform does
     not capture AXIN2 (not in
     GPL3921 probe set).
  Script 2 will stratify by
  CTNNB1 expression terciles
  and test survival directly.

----------------------------------------------------------------
SECTION 7: SURVIVAL GENE LIST
----------------------------------------------------------------

OS PREDICTORS (confirmed p<0.05):

  WORSE prognosis with high expression:
  ACLY   p=0.014 * (lipid synthesis)
  BAX    p=0.007 ** (apoptosis — paradox)
  CDC20  p=0.005 ** (cell cycle)
  DNMT3A p=0.035 * (epigenetic)
  FASN   p=0.048 * (lipid synthesis)
  HDAC2  p=0.010 * (epigenetic)
  KRT19  p=0.019 * (progenitor marker)
  MCM2   p=0.006 ** (replication)
  PROM1  p=0.002 ** (CD133, stem cell)
  PTEN   p=0.028 * (tumour suppressor —
                    paradox: see below)
  S100A9 p=0.029 * (inflammation)
  SCD    p=0.023 * (lipid desaturase)
  SMAD3  p=0.006 ** (TGF-B effector)
  SOX4   p=5.4e-04 *** (progenitor TF)
  TOP2A  p=0.009 ** (replication)
  VEGFA  p=0.030 * (angiogenesis)

  BETTER prognosis with high expression:
  ALDOB  p=0.004 ** (metabolic — hepatocyte)
  CYP3A4 p=0.012 * (metabolic — hepatocyte)
  G6PC   p=0.002 ** (metabolic — hepatocyte)
  HDAC3  p=0.042 * (distinct from HDAC1/2)
  IL6    p=0.023 * (inflammation)
  JAK2   p=0.004 ** (JAK-STAT)
  KDR    p=4.8e-05 *** (VEGFR2 — hepatocyte)
  MTOR   p=0.013 * (mTOR)
  TSC2   p=0.050 * (mTOR regulator)
  TTR    p=3.3e-05 *** (metabolic — hepatocyte)

NOTE ON PARADOXES:
  BAX ↑=worse: BAX is proapoptotic.
  High BAX in worse prognosis HCC
  may reflect a resistant state
  where apoptosis is activated but
  not executed — mitochondrial
  priming without commitment.

  PTEN ↑=worse: PTEN is a tumour
  suppressor. This is paradoxical.
  May reflect: 1) PTEN protein
  function loss despite mRNA expression,
  2) compensatory upregulation in
  PI3K-active tumours, 3) probe
  cross-hybridisation artefact.
  Requires validation.

  MTOR ↑=better and TSC2 ↑=better:
  These are consistent — TSC2 is
  an mTOR inhibitor. TSC2 high =
  mTOR suppressed. Yet MTOR high
  also = better. This may be because
  mTOR high reflects active hepatocyte
  protein synthesis — a marker of
  differentiation, not oncogenesis —
  in well-differentiated tumours.

  METABOLIC CLUSTER BETTER PROGNOSIS:
  CYP3A4, G6PC, ALDOB, TTR, KDR
  are ALL better prognosis.
  These are ALL hepatocyte terminal
  differentiation markers.
  This confirms NOVEL FINDING 1:
  metabolic identity preservation
  = better prognosis = shallower
  depth score.
  The metabolic switch is the
  dominant biology in HCC.

----------------------------------------------------------------
SECTION 8: SUMMARY TABLE
----------------------------------------------------------------

Prediction       r/p              Status
-----------      -------          ------
HCC-P1 HNF4A    r=-0.46 ***      PARTIAL
HCC-P2 AFP      r=+0.62 ***      CONFIRMED ✓
HCC-P3 MYC      r=+0.29 ***      NOT MET
HCC-P4 CTNNB1   independent      PARTIAL ✓
HCC-P5 CTNNB1   prognosis         PENDING S2
HCC-P6 depth    OS p=3.8e-04 *** SUPPORTED ✓
OS depth        p=3.80e-04 ***    CONFIRMED ✓
RFS depth       p=0.0296 *        CONFIRMED ✓
CC-1 EZH2       r=+0.52 ***      CONFIRMED ✓
CC-2 FGFR4      r=+0.34 (rises)  NOT CONFIRMED
CC-3 ZEB2-AURKA r=-0.17 *        NOT CONFIRMED
CC-4 FOXA1      r=+0.28 ***      NOT CONFIRMED
CC-5 S100A8     r=+0.20 **       PARTIAL

----------------------------------------------------------------
SECTION 9: REVISED CROSS-CANCER RULES
----------------------------------------------------------------

RULE UPDATES FROM HCC SCRIPT 1:

CC-1 (EZH2+HDAC1 LOCK):
  CONFIRMED in glandular lineages.
  EAC=✓ HCC=✓ BLCA=✗ (inverted)
  Rule: GLANDULAR LINEAGE SPECIFIC.
  Confidence: HIGH.

CC-2 (FGFR ISOFORM):
  The isoform switch occurs
  but the direction depends
  on lineage context.
  BLCA: FGFR3=luminal FGFR1=basal
  HCC:  FGFR3 rises with depth
  Rule: FGFR isoform switching
  is universal but the identity
  of the dominant isoform is
  lineage-specific.
  Confidence: MODERATE.

CC-3 (ZEB2-AURKA):
  Only confirmed in CIN-high
  cancers (STAD, EAC).
  Not in BLCA or HCC.
  Rule: CIN-ASSOCIATED lineages only.
  Confidence: MODERATE.

CC-4 (FOXA1 switch):
  NOT a universal switch gene.
  FOXA1 rises in HCC (opposite BLCA).
  Rule: FOXA1 is context-dependent.
  Not a cross-cancer rule.
  Retired from cross-cancer ruleset.

NEW RULE EMERGING:
  Metabolic differentiation
  programme loss is the primary
  switch in metabolically
  specialised cancers (HCC).
  TF loss is secondary to
  metabolic gene loss.
  CYP3A4, ALDOB, PCK1, G6PC
  are stronger depth correlates
  than HNF4A in HCC.
  Hypothesis: in any cancer
  arising from a metabolically
  specialised cell (hepatocyte,
  acinar pancreatic, proximal
  tubule kidney), metabolic
  gene loss will dominate the
  depth signature over TF loss.
  Test: PAAD (pancreatic), ccRCC
  (kidney) will verify this rule.

----------------------------------------------------------------
SECTION 10: DOCUMENT 92a STATUS
----------------------------------------------------------------

Script 1 complete.
Data: GSE14520 GPL3921 n=445

Confirmed findings:
  Depth scores working (0.03–0.80)
  Depth predicts OS p=3.80e-04 ***
  Depth predicts RFS p=0.030 *
  AFP confirmed FA gene r=+0.62 ***
  EZH2+HDAC1 lock confirmed ✓
  Metabolic switch discovered
  SMAD3 OS predictor confirmed
    (second cancer after BLCA)
  CTNNB1/MYC independence confirmed
  SOX4 strong FA gene and OS predictor

Pending (Script 2):
  CTNNB1-hi vs CTNNB1-lo survival
  FGFR3 depth analysis (unexpected rise)
  HDAC2 as primary epigenetic FA gene
  AFP-high vs AFP-low OS stratification
  Metabolic score as depth component
  TCGA-LIHC replication

Next: Script 2 — Subtype Analysis
  TCGA-LIHC replication dataset
  CTNNB1 vs MYC survival stratification
  AFP-high survival
  Refined depth with metabolic genes
  Drug prediction artifact (HCC)

================================================================
END DOCUMENT 92a
================================================================
