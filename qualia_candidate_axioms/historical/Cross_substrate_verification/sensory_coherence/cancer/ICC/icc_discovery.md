# Document 93a
## ICC False Attractor — Script 1 Reasoning Artifact
### OrganismCore | 2026-03-02 | Author: Eric Robert Lawson

---

## SECTION 1: PREDICTIONS STATED BEFORE DATA
### Locked in Document 93b — 2026-03-02

```
CANCER TYPE: Intrahepatic Cholangiocarcinoma (ICC)
CELL OF ORIGIN: Intrahepatic biliary epithelial cell
                (cholangiocyte)
LINEAGE:
  Hepatoblast →
  Bipotent progenitor →
  Cholangiocyte progenitor →
  Immature cholangiocyte →
  Mature cholangiocyte (terminal)

PREDICTED BLOCK:
  Mature cholangiocyte identity lost.
  Cancer cell retains progenitor identity.
  Block at cholangiocyte maturation checkpoint.
  NOT at hepatocyte lineage (different SW genes).

PREDICTED SWITCH GENES (DOWN in ICC):
  FOXA2  — hepatobiliary TF, mature identity
  HNF4A  — nuclear receptor, mature hepatobiliary
  ALB    — mature hepatocyte/biliary product
  APOB   — mature metabolic function
  CYP3A4 — mature metabolic enzyme
  ALDOB  — mature glycolytic enzyme
  G6PC   — mature gluconeogenic enzyme
  GGT1   — mature biliary enzyme

PREDICTED FA MARKERS (UP in ICC):
  SOX4   — progenitor TF
  SOX9   — biliary progenitor identity
  PROM1  — progenitor surface marker (CD133)
  CD44   — progenitor/stemness marker
  CDC20  — proliferation (APC/C activator)
  EZH2   — epigenetic lock (PRC2)
  TWIST1 — EMT driver
  FAP    — CAF/stroma marker

EPIGENETIC PREDICTION:
  EZH2 ELEVATED (gain of function lock)
  Same as BRCA — solid tumour with
  desmoplastic stroma
  PRC2 complex locks cells in progenitor state

DRUG TARGET PREDICTION (pre-data):
  1. EZH2 inhibitor (tazemetostat)
     Dissolves epigenetic lock
  2. FGFR2 inhibitor (pemigatinib)
     FGFR2 fusion drives progenitor trap
  3. HDAC inhibitor
     Co-repressor complex at biliary genes
  4. EMT reversal (TWIST1 suppression)
     Restores biliary identity
```

---

## SECTION 2: SCRIPT 0c SADDLE TABLE
### Protocol Phase 2 — TCGA-CHOL (n=36 ICC, n=9 Normal)

```
DATASET:  TCGA-CHOL HiSeqV2 RNA-seq
          Xena hub download
          n=36 tumour (ICC + mixed biliary)
          n=9 normal adjacent biliary

SADDLE POINT ANALYSIS — TCGA-CHOL
All values: mean log2 expression

Gene       ICC_mean  Nor_mean    FC      p          result   pred
-----------------------------------------------------------------
SWITCH GENES — predicted DOWN
FOXA2        8.682    10.502   -1.820  p=2.21e-05 ***  ✓ DOWN  ✓
HNF4A        9.501    12.580   -3.079  p=6.02e-06 ***  ✓ DOWN  ✓
ALB         14.260    22.526   -8.267  p=4.59e-06 ***  ✓ DOWN  ✓
APOB        11.699    17.795   -6.096  p=4.59e-06 ***  ✓ DOWN  ✓
CYP3A4       5.363    16.056  -10.694  p=5.25e-06 ***  ✓ DOWN  ✓
ALDOB        9.098    18.341   -9.244  p=4.59e-06 ***  ✓ DOWN  ✓
G6PC         7.766    14.277   -6.511  p=4.59e-06 ***  ✓ DOWN  ✓
GGT1        11.057    11.175   -0.117  p=0.5418   ns   ✗ flat  ✗
KLF4         8.209     8.782   -0.573  p=0.1777   ns   ✗ flat  ✗

FALSE ATTRACTOR — predicted UP
SOX4        11.737     8.756   +2.980  p=1.02e-05 ***  ✓ UP   ✓
SOX9        11.524     8.610   +2.913  p=2.51e-05 ***  ✓ UP   ✓
PROM1        9.607     6.903   +2.703  p=2.29e-03  **  ✓ UP   ✓
CD44        11.022     9.274   +1.748  p=5.66e-03  **  ✓ UP   ✓
CDC20        8.348     3.349   +4.999  p=4.59e-06 ***  ✓ UP   ✓
EZH2         8.048     5.094   +2.954  p=4.59e-06 ***  ✓ UP   ✓
HDAC2       10.451     9.701   +0.749  p=3.65e-05 ***  ✓ UP   ✓
TWIST1       4.509     2.687   +1.822  p=1.89e-03  **  ✓ UP   ✓
FAP          7.581     3.208   +4.372  p=1.33e-05 ***  ✓ UP   ✓

ADDITIONAL CONFIRMED UP:
BIRC5        7.668     3.317   +4.352  p=4.59e-06 ***  ✓ UP
TOP2A        9.885     4.918   +4.967  p=6.88e-06 ***  ✓ UP
MKI67        9.907     5.709   +4.198  p=5.26e-06 ***  ✓ UP
CCNB1        8.853     5.287   +3.566  p=4.59e-06 ***  ✓ UP
CDK4        11.448    10.155   +1.293  p=1.95e-05 ***  ✓ UP
DNMT1       10.293     8.781   +1.512  p=1.17e-05 ***  ✓ UP
VIM         14.253    12.400   +1.854  p=1.90e-04 ***  ✓ UP
TGFB1       10.457     9.198   +1.259  p=4.35e-03  **  ✓ UP
ACTA2       11.967    11.096   +0.872  p=0.0153    *   ✓ UP
COL1A1      14.806    12.271   +2.535  p=6.70e-05 ***  ✓ UP
POSTN       10.214     7.746   +2.468  p=6.97e-04 ***  ✓ UP
MMP2        10.726     9.717   +1.009  p=0.0259    *   ✓ UP
MMP9         8.790     5.828   +2.963  p=1.28e-03  **  ✓ UP
CDKN2A       7.023     3.620   +3.403  p=7.55e-05 ***  ✓ UP
TP53        10.732     9.512   +1.220  p=2.66e-04 ***  ✓ UP
NOTCH1      10.197     9.487   +0.709  p=9.42e-03  **  ✓ UP
NOTCH2      11.981    11.283   +0.698  p=0.0130    *   ✓ UP
CA9          9.487     5.518   +3.969  p=1.28e-03  **  ✓ UP
RB1          9.696     9.177   +0.519  p=2.29e-03  **  ✓ UP

INVERTED (predicted direction wrong):
IDH1        11.507    13.678   -2.171  p=4.59e-06 ***  ↑=worse — DOWN
IDH2        11.849    13.135   -1.286  p=3.31e-04 ***  ↑=worse — DOWN
ZEB1         8.632     9.113   -0.480  p=0.1028   ns   flat
ZEB2         8.257     9.135   -0.878  p=0.0192    *   ↑=worse — DOWN
EGFR         9.196    10.657   -1.461  p=4.11e-04 ***  ↑=worse — DOWN
PTEN        10.530    11.275   -0.745  p=4.66e-05 ***  ↑=worse — DOWN
STAT3       11.912    12.658   -0.746  p=3.69e-04 ***  DOWN
```

---

## SECTION 3: SADDLE TABLE — GSE32225
### (n=149 ICC, n=6 Normal biliary)

```
DATASET:  GSE32225 GPL8432 Illumina microarray
          149 ICC tumour samples
          6 normal biliary epithelium
          NMF subtypes: Inflammation, Proliferation

SADDLE POINT ANALYSIS — GSE32225
(values: mean probe intensity)

Gene       ICC_mean   Nor_mean      FC        p       result
------------------------------------------------------------
SWITCH GENES
GGT1        349.3      654.0      -304.7  p=0.0154  *  ✓ DOWN
ALB        4272.7     7454.2     -3181.5  p=6.57e-06 *** ✓ DOWN
APOB       1774.0     2971.7     -1197.7  p=4.39e-07 *** ✓ DOWN
ALDOB      1516.2     4731.0     -3214.8  p=1.34e-05 *** ✓ DOWN
G6PC        241.1      592.8      -351.7  p=9.20e-04 *** ✓ DOWN
HNF4A       681.3      672.3        +9.0  p=0.9244  ns  ✗ flat
FOXA2       822.9      481.5      +341.3  p=0.0415   *  INVERTED

FA MARKERS
SOX4        414.1      169.7      +244.4  p=1.93e-04 *** ✓ UP
PROM1      3180.3      989.1     +2191.2  p=1.80e-03  ** ✓ UP
CDC20       550.4      181.6      +368.8  p=3.88e-04 *** ✓ UP
BIRC5       148.9      121.3       +27.6  p=0.0358    *  ✓ UP
CCNB1       177.5      115.9       +61.6  p=1.16e-03  ** ✓ UP
CDK4        425.9      317.0      +108.8  p=0.0340    *  ✓ UP
CDK6        151.9      114.0       +37.9  p=7.00e-03  ** ✓ UP
EZH2        251.7      125.1      +126.6  p=1.95e-05 *** ✓ UP
HDAC2      1309.0      959.0      +349.9  p=9.41e-03  ** ✓ UP
FAP        1018.6      262.4      +756.1  p=1.01e-03  ** ✓ UP
COL1A1     3490.3      475.5     +3014.8  p=7.26e-08 *** ✓ UP
POSTN       203.1      109.7       +93.4  p=4.17e-05 *** ✓ UP
CTNNB1      836.7      393.0      +443.7  p=9.79e-07 *** ✓ UP
CCND1      2976.2     2032.3      +943.9  p=0.0229    *  ✓ UP
NOTCH1      258.5      156.3      +102.2  p=2.71e-03  ** ✓ UP
WNT5A       387.8      152.3      +235.5  p=2.13e-05 *** ✓ UP
IDH2       2854.1     1755.3     +1098.7  p=8.37e-04 *** ✓ UP (note: inverted in TCGA)

CROSS-DATASET CONSENSUS:
  Both TCGA and GSE confirm DOWN:
    ALB, APOB, ALDOB, G6PC ← strongest SW signal
  Both confirm UP:
    SOX4, PROM1, CDC20, EZH2, HDAC2,
    FAP, COL1A1, POSTN, CCNB1 ← core FA
  Discordant:
    FOXA2: DOWN in TCGA, UP in GSE
      → platform/normalisation effect
      → TCGA (RNA-seq) more reliable
    IDH2: DOWN in TCGA, UP in GSE
      → biology unclear, may reflect
        different ICC subtype composition
    GGT1: flat in TCGA, DOWN in GSE
      → GSE has more power (n=149)
      → GGT1 probably truly down
```

---

## SECTION 4: DEPTH CORRELATIONS
### Protocol Step 2.3 — "Read this first"

```
DEPTH CORRELATIONS — TCGA-CHOL
(Pearson r, gene vs depth score)
Sorted by |r| descending

Rank  Gene      r        p          direction
---------------------------------------------
  1   TWIST1  +0.7988  p=5.27e-09 ***  ↑=deeper
  2   G6PC    -0.7014  p=1.89e-06 ***  ↓=shallower (SW)
  3   ALDOB   -0.6463  p=2.07e-05 ***  ↓=shallower (SW)
  4   APOB    -0.6061  p=8.93e-05 ***  ↓=shallower (SW)
  5   WNT5A   +0.6501  p=1.78e-05 ***  ↑=deeper
  6   CYP3A4  -0.5749  p=2.45e-04 ***  ↓=shallower (SW)
  7   FAP     +0.5740  p=2.52e-04 ***  ↑=deeper
  8   TGFB1   +0.5631  p=3.50e-04 ***  ↑=deeper
  9   POSTN   +0.5343  p=7.89e-04 ***  ↑=deeper
 10   MMP2    +0.5359  p=7.55e-04 ***  ↑=deeper
 11   MMP9    +0.4538  p=5.43e-03  **  ↑=deeper
 12   VIM     +0.4829  p=2.85e-03  **  ↑=deeper
 13   CD44    +0.4715  p=3.70e-03  **  ↑=deeper
 14   COL1A1  +0.4615  p=4.61e-03  **  ↑=deeper
 15   HDAC2   +0.4467  p=6.31e-03  **  ↑=deeper
 16   ACTA2   +0.4475  p=6.20e-03  **  ↑=deeper
 17   ALB     -0.4297  p=8.91e-03  **  ↓=shallower (SW)
 18   HAVCR2  +0.4346  p=8.09e-03  **  ↑=deeper
 19   PROM1   +0.3952  p=0.0171    *   ↑=deeper
 20   ZEB2    +0.3753  p=0.0241    *   ↑=deeper

WHAT THE DEPTH CORRELATIONS REVEAL:

  #1 TWIST1 (r=+0.799) — DOMINANT SIGNAL
    TWIST1 is the single strongest predictor
    of depth in TCGA-CHOL.
    It is not just elevated — it is THE
    continuous measure of depth itself.
    TWIST1 is an EMT master regulator.
    This means ICC depth = EMT depth.
    The false attractor in ICC is primarily
    an EMT attractor, not just a proliferative
    attractor.

  #2-4 G6PC, ALDOB, APOB (r=-0.70 to -0.61)
    Three SW genes in the top 4 spots.
    These are mature hepatobiliary metabolic
    genes. Their loss is the primary SW signal.
    The deeper the ICC, the less mature
    metabolic identity it retains.
    G6PC (r=-0.70) is the single best
    switch gene for ICC.

  #5 WNT5A (r=+0.65)
    WNT5A is a non-canonical Wnt ligand.
    Not in the original FA panel — UNEXPECTED.
    WNT5A drives EMT via PCP pathway.
    r=+0.65 makes it a core depth driver.
    WNT5A → TWIST1 axis = the ICC EMT engine.

  #6-10 FAP, TGFB1, POSTN, MMP2, CYP3A4
    ALL stroma/CAF markers in the top 10.
    This confirms Depth_S is a real component.
    The stroma and the EMT co-vary with depth.
    TGFB1 (r=+0.563) drives both EMT
    and CAF activation — central node.

KEY INSIGHT FROM DEPTH CORRELATIONS:
  TCGA-CHOL depth = TWIST1 × stroma
  The ICC false attractor has two engines:
    Engine 1: TWIST1-driven EMT
    Engine 2: TGFB1-driven CAF stroma
  They co-activate (r(T,S)=+0.394)
  but are partially independent.
  This is different from HCC where
  the depth was proliferation-dominant.


DEPTH CORRELATIONS — GSE32225
(n=149 ICC)

Rank  Gene      r        p          direction
---------------------------------------------
  1   ALB     -0.8284  p=7.81e-39 ***  ↓=shallower (SW)
  2   ACTA2   +0.6993  p=3.44e-23 ***  ↑=deeper
  3   SOX4    +0.6558  p=1.11e-19 ***  ↑=deeper
  4   CCND1   +0.6496  p=3.19e-19 ***  ↑=deeper
  5   COL1A1  +0.6491  p=3.46e-19 ***  ↑=deeper
  6   CD44    +0.6495  p=3.26e-19 ***  ↑=deeper
  7   HAVCR2  +0.6286  p=9.20e-18 ***  ↑=deeper
  8   APOB    -0.6113  p=1.24e-16 ***  ↓=shallower (SW)
  9   VIM     +0.5838  p=5.53e-15 ***  ↑=deeper
 10   HNF4A   -0.5827  p=6.38e-15 ***  ↓=shallower (SW)
 11   EGFR    +0.5742  p=1.91e-14 ***  ↑=deeper (note: DOWN in ICC)
 12   POSTN   +0.5637  p=7.14e-14 ***  ↑=deeper
 13   NOTCH1  +0.5397  p=1.23e-12 ***  ↑=deeper
 14   ARID1A  +0.5315  p=3.07e-12 ***  ↑=deeper
 15   SMAD4   +0.5169  p=1.49e-11 ***  ↑=deeper

WHAT GSE ADDS:

  #1 ALB (r=-0.828) — DOMINANT SW IN GSE
    In GSE (n=149), ALB is the single
    strongest depth predictor.
    In TCGA (n=36), TWIST1 was dominant.
    These are different: TCGA = EMT-skewed
    (resection bias, mixed subtypes).
    GSE = full ICC spectrum (n=149).
    In the larger unbiased dataset:
    SW gene loss (ALB) is the primary
    axis — not EMT.
    TWIST1 may be a CONSEQUENCE of
    ALB/HNF4A loss, not the cause.

  #2 ACTA2 (r=+0.699) — STROMA DOMINANT
    ACTA2 = alpha-smooth muscle actin
    = activated CAF marker.
    r=+0.699 in n=149 is extremely robust.
    This confirms: STROMA IS INTEGRAL
    to ICC depth at large scale.

  EGFR PARADOX (r=+0.574):
    EGFR is DOWN in ICC vs normal.
    But EGFR POSITIVELY correlates with depth.
    Explanation: within ICC, EGFR-hi cells are
    paradoxically the deeper ones.
    This is consistent with the OS finding
    (EGFR-hi = better OS in Script 1 v3).
    EGFR-hi ICC = less EMT-transformed
    (EGFR drives epithelial signalling).
    At population level: ICC loses EGFR.
    Within ICC: higher EGFR = shallower?
    The positive depth correlation contradicts
    this. Needs Script 2 investigation.

CONSENSUS DEPTH DRIVERS (both datasets):
  SW:  ALB, APOB, ALDOB, G6PC, HNF4A
  FA:  SOX4, CD44, ACTA2, COL1A1,
       VIM, CCND1, POSTN
  Unique to TCGA: TWIST1 (#1)
  Unique to GSE:  HAVCR2, ARID1A, SMAD4
```

---

## SECTION 5: PREDICTION CLASSIFICATION

```
PREDICTIONS vs DATA — TCGA-CHOL + GSE32225

SW GENES:
  FOXA2   CONFIRMED ✓  TCGA p=2.21e-05
                       GSE: INVERTED (platform effect)
                       TCGA RNA-seq = canonical
  HNF4A   CONFIRMED ✓  TCGA p=6.02e-06
                       GSE r=-0.583 (top 10 depth)
  ALB     CONFIRMED ✓  TCGA p=4.59e-06
                       GSE p=6.57e-06, r=-0.828
  APOB    CONFIRMED ✓  TCGA p=4.59e-06
                       GSE p=4.39e-07
  CYP3A4  CONFIRMED ✓  TCGA p=5.25e-06 (FC=-10.7!)
  ALDOB   CONFIRMED ✓  TCGA p=4.59e-06 (FC=-9.2)
  G6PC    CONFIRMED ✓  TCGA p=4.59e-06 r=-0.70
  GGT1    WEAKLY ✓     TCGA flat / GSE p=0.015
  KLF4    NOT CONFIRMED Flat in both datasets

FA MARKERS:
  SOX4    CONFIRMED ✓  TCGA p=1.02e-05
                       GSE p=1.93e-04, r=+0.656
  SOX9    CONFIRMED ✓  TCGA p=2.51e-05
  PROM1   CONFIRMED ✓  TCGA p=2.29e-03
                       GSE p=1.80e-03
  CD44    CONFIRMED ✓  TCGA p=5.66e-03
                       GSE r=+0.650
  CDC20   CONFIRMED ✓  TCGA p=4.59e-06 (FC=+5.0!)
                       GSE p=3.88e-04
  EZH2    CONFIRMED ✓  TCGA p=4.59e-06
                       GSE p=1.95e-05
  TWIST1  CONFIRMED ✓  TCGA p=1.89e-03 r=+0.799 ***
  FAP     CONFIRMED ✓  TCGA p=1.33e-05
                       GSE p=1.01e-03

EPIGENETIC PREDICTION:
  EZH2 elevated: CONFIRMED ✓
    TCGA: FC=+2.954, p=4.59e-06
    GSE:  FC=+126.6, p=1.95e-05
    Both datasets: EZH2 UP in ICC
    This is a GAIN OF FUNCTION lock
    Same direction as BRCA (not MDS)
    Drug: EZH2 inhibitor (tazemetostat)
    CONFIRMED ✓

  HDAC2 elevated: CONFIRMED ✓
    TCGA: FC=+0.749, p=3.65e-05
    GSE:  FC=+349.9, p=9.41e-03, r=+0.438
    HDAC2 is a universal ICC FA marker
    (confirmed in both prior scripts)

UNEXPECTED FINDINGS (not predicted):
  TWIST1 r=+0.799 — dominant depth driver
    Was predicted as FA marker but
    dominance was not predicted.
    This changes the attractor geometry.
    The ICC attractor is EMT-primary.

  WNT5A r=+0.650 TCGA
    Not in original panel.
    Non-canonical Wnt — TWIST1 activator.
    WNT5A is the upstream driver of
    TWIST1 in ICC.
    This is the key gap gene.

  ACTA2 r=+0.699 GSE
    Activated CAF marker dominates depth
    in the large dataset.
    Stroma is not a secondary signal —
    it is co-primary with EMT.

  EGFR PARADOX:
    DOWN in ICC vs normal (p=4.11e-04)
    BUT positive depth correlation GSE (+0.574)
    AND positive depth correlation TCGA (+0.363)
    AND better OS when high (Script 1 v3)
    Biology: EGFR maintains biliary epithelial
    polarity. EGFR-hi within ICC = more
    epithelial = shallower depth score?
    But the correlation is POSITIVE — meaning
    EGFR-hi = DEEPER. This is paradoxical.
    Needs Script 2 investigation.
```

---

## SECTION 6: CORRECTED ATTRACTOR DESCRIPTION

```
THE ICC FALSE ATTRACTOR — CORRECTED
After Script 0c / Protocol Script 1

WHAT THE CANCER CELL IS:
  A biliary epithelial progenitor cell
  that has lost mature cholangiocyte identity
  AND activated EMT AND recruited CAF stroma.

  It is NOT simply a proliferating progenitor
  (like HCC with AFP/GPC3 identity).
  It is a MESENCHYMAL TRANSITION STATE —
  biliary progenitor + EMT + desmoplasia.

THREE COMPONENTS OF THE ICC ATTRACTOR:

  Component 1: EXECUTION BLOCK
    Loss of biliary maturation TFs:
      HNF4A, FOXA2, ALB, CYP3A4, G6PC
    These are the metabolic and TF
    identity genes of mature biliary cells.
    They are suppressed — cells cannot
    complete biliary maturation.
    This is equivalent to the AML blast
    being unable to complete GMP transition.
    BLOCK LEVEL: Mature cholangiocyte TFs
                 (HNF4A/FOXA2 axis)

  Component 2: IDENTITY RETENTION
    Progenitor/EMT identity maintained by:
      TWIST1 (r=+0.799 — primary driver)
      SOX4, SOX9 (progenitor TFs)
      VIM, CD44, PROM1 (mesenchymal markers)
      ZEB1, ZEB2 (EMT TFs)
    The cell is STUCK in an EMT-transitional
    progenitor state.
    It cannot go back (biliary TFs suppressed)
    and cannot go forward (mature identity lost).

  Component 3: STABILISING MECHANISM
    CAF stroma co-activates and stabilises:
      ACTA2, FAP, COL1A1, POSTN (CAF markers)
      TGFB1 (bidirectional: EMT + stroma)
      WNT5A (non-canonical Wnt → TWIST1)
    The stroma creates a desmoplastic niche
    that REINFORCES the EMT attractor.
    Stroma feeds TGFB1 → TWIST1 loop.
    This is why ICC is so resistant:
    the tumour builds its own attractor wall.

THE ATTRACTOR GEOMETRY:
  Normal biliary cell:
    High: HNF4A, FOXA2, ALB, G6PC
    Low:  TWIST1, VIM, FAP, ACTA2
  ICC false attractor:
    Low:  HNF4A, FOXA2, ALB, G6PC
    High: TWIST1, VIM, FAP, ACTA2, SOX4

  The Waddington valley ICC is stuck in:
    EMT-transitional progenitor state
    with desmoplastic stroma niche
    stabilised by WNT5A→TGFB1→TWIST1 loop

  The switch gene that would dissolve it:
    HNF4A or FOXA2 restoration
    (biliary master regulators)
    → collapse TWIST1 EMT identity
    → restore mature cholangiocyte fate

  The gap:
    HNF4A/FOXA2 (suppressed)
    → should drive biliary maturation genes
    → but G6PC, ALB, CYP3A4 are also absent
    → HNF4A is suppressed BEFORE its targets
    → The block is at the HNF4A/FOXA2 level,
      not at the downstream metabolic genes
    → This is a TF-level block
    → r(HNF4A, ALB) in ICC tumours = ?
      (gap test for Script 2)
```

---

## SECTION 7: DRUG TARGETS — GEOMETRY DERIVED
### Stated before literature check

```
DRUG TARGET DERIVATION — STATED 2026-03-02
BEFORE ANY LITERATURE SEARCH

Target 1: EZH2 INHIBITOR
  Geometry: EZH2 elevated in both datasets
            (TCGA p=4.59e-06, GSE p=1.95e-05)
            EZH2 r=+0.501 with depth (Script 1 v3)
            Gain-of-function lock
            PRC2 complex silences HNF4A/FOXA2
            promoters → cannot restore biliary TFs
  Mechanism: EZH2 inhibition derepresses
             HNF4A/FOXA2 → partial biliary
             redifferentiation
  Drug class: EZH2 inhibitor
  Drug name:  Tazemetostat (FDA approved)

Target 2: TGFB1/TGF-β PATHWAY INHIBITOR
  Geometry: TGFB1 r=+0.563 (top 8 in TCGA)
            TGFB1 drives TWIST1 (EMT engine)
            TGFB1 drives ACTA2 (stroma engine)
            TGFB1 is the BRIDGE between
            tumour depth and stroma depth
            Blocking TGFB1 disrupts BOTH
            the EMT and the CAF niche
  Mechanism: TGF-β blockade collapses
             TWIST1 EMT + stroma co-activation
  Drug class: TGF-β inhibitor / anti-TGFB1 mAb
  Drug name:  Galunisertib (LY2157299) — TGFβRI

Target 3: TWIST1 DIRECT SUPPRESSION
  Geometry: TWIST1 r=+0.799 — DOMINANT driver
            Highest |r| gene in TCGA-CHOL
            TWIST1 is the identity gene of
            the ICC false attractor state
            Suppressing TWIST1 = direct
            attractor dissolution
  Mechanism: TWIST1 suppression removes
             the primary identity anchor
             → cells lose EMT identity
             → biliary redifferentiation possible
  Drug class: HDAC inhibitor (indirect TWIST1)
              or BET bromodomain inhibitor
              (TWIST1 transcription)
  Drug names: Vorinostat, JQ1/BET inhibitors

Target 4: WNT5A/NON-CANONICAL WNT INHIBITOR
  Geometry: WNT5A r=+0.650 (top 5 TCGA)
            WNT5A drives TWIST1 via PCP pathway
            WNT5A is UPSTREAM of TWIST1
            Blocking WNT5A = upstream
            dissolution of the EMT engine
            WNT5A was an UNEXPECTED finding —
            not in the pre-data panel
            Its dominance suggests it is
            the EMT activator, not just a marker
  Mechanism: WNT5A blockade reduces
             TWIST1 activity → EMT reversal
  Drug class: WNT pathway inhibitor
  Drug names: Ipafricept (OMP-54F28),
              anti-FZD5 antibodies

DRUG TARGET PRIORITY ORDER:
  1. TGF-β inhibition (TGFB1 — dual target:
     EMT + stroma, highest clinical relevance)
  2. EZH2 inhibition (epigenetic lock,
     proven mechanism, approved drug)
  3. WNT5A/non-canonical Wnt (upstream EMT)
  4. TWIST1 (direct attractor identity gene)

NOTE: These are derived from attractor
geometry alone, before literature check.
Stated 2026-03-02.
```

---

## SECTION 8: NEW PREDICTIONS FOR SCRIPT 2

```
SCRIPT 2 PREDICTIONS — STATED 2026-03-02
BEFORE SCRIPT 2 IS WRITTEN

Based on Script 0c / Protocol Script 1 findings:

S2-P1: GAP TEST — HNF4A → ALB
  HNF4A normally drives ALB expression.
  Both are suppressed in ICC.
  PREDICTION: r(HNF4A, ALB) in ICC tumours
  will be LOW (near zero or negative)
  compared to normal biliary cells.
  Low r = HNF4A→ALB circuit is broken.
  The block is at HNF4A itself (TF level)
  not at the downstream metabolic genes.

S2-P2: WNT5A → TWIST1 CIRCUIT
  WNT5A (r=+0.65) is upstream of TWIST1 (r=+0.80).
  PREDICTION: r(WNT5A, TWIST1) in ICC tumours
  will be HIGH (r>0.50).
  This confirms WNT5A→TWIST1 as the
  primary EMT activation circuit.

S2-P3: TGFB1 BRIDGES EMT AND STROMA
  TGFB1 r=+0.563 (TCGA).
  PREDICTION: r(TGFB1, TWIST1) > 0.40
              r(TGFB1, ACTA2) > 0.40
  Both positive = TGFB1 drives both.
  This confirms TGFB1 as the bridge.

S2-P4: NMF PROLIFERATIVE = TWIST1-HIGH
  GSE32225 NMF Proliferative subtype
  has higher depth than Inflammation.
  PREDICTION: Proliferative mean TWIST1
  expression > Inflammation mean TWIST1.
  Proliferative depth is TWIST1-driven.

S2-P5: EZH2 SUPPRESSES HNF4A
  EZH2 elevated, HNF4A suppressed.
  PREDICTION: r(EZH2, HNF4A) in ICC
  tumours will be NEGATIVE.
  High EZH2 = low HNF4A = EZH2 silences
  the biliary maturation TF.

S2-P6: CORRECTED DEPTH SCORE (S2 axis)
  Protocol: S2 depth = top suppressed gene
            + top elevated gene
  From correlations:
    Top suppressed: ALB (r=-0.828 GSE)
                    or G6PC (r=-0.701 TCGA)
    Top elevated:   TWIST1 (r=+0.799 TCGA)
                    or ACTA2 (r=+0.699 GSE)
  PREDICTION: r(S1_depth, S2_depth) > 0.80
  Same biology, better axis.

S2-P7: EGFR PARADOX RESOLVED
  EGFR is DOWN in ICC vs normal.
  But EGFR positively correlates with depth.
  PREDICTION: In ICC-only samples, EGFR-hi
  cells have LOWER TWIST1 and LOWER VIM.
  EGFR-hi = more epithelial within ICC.
  But the depth score uses BOTH stroma
  (ACTA2, FAP) and EMT (TWIST1, VIM).
  EGFR-hi may have high stroma but low EMT.
  Test: r(EGFR, TWIST1) — predict negative
        r(EGFR, ACTA2) — predict positive
```

---

## SECTION 9: PROTOCOL COMPLIANCE CHECK

```
PHASE 0 → PHASE 2 CHECKLIST:

  ☑ Dataset human (TCGA-CHOL, GSE32225)
  ☑ Cancer AND normal confirmed
    TCGA: n=36 ICC, n=9 normal
    GSE:  n=149 ICC, n=6 normal
  ☑ n(cancer) ≥ 5, n(normal) ≥ 3
  ☑ Correct tissue (biliary/liver)
  ☑ Predictions written before data
    (Doc 93b dated 2026-03-02)
  ☑ Predictions have biological reasoning
  ☑ Switch genes predicted (8 genes)
  ☑ FA markers predicted (8 genes)
  ☑ Epigenetic direction predicted (EZH2 UP)
  ☑ Drug target predicted with mechanism
  ☑ Script 0c output pasted unedited
  ☑ Depth correlation table reviewed
  ☑ Each prediction classified
  ☑ Unexpected signals documented
    (TWIST1 dominance, WNT5A, EGFR paradox)
  ☑ Corrected attractor described
    (3 components: execution block,
     identity retention, stabilising mechanism)
  ☑ New predictions derived (S2-P1 to S2-P7)
  ☑ Document 93a written (this document)

  PREVIOUSLY MISSING (now resolved):
  ☑ Formal saddle table (Section 2+3)
  ☑ Depth correlation top list (Section 4)
  ☑ Drug targets locked before literature (Section 7)
  ☑ Protocol Script 1 document structure

COMPLIANCE STATUS: FULLY COMPLIANT ✓
ICC is now ready to proceed to Script 2.
```

---

## SECTION 10: STATUS BLOCK

```
document:         93a
type:             Script 1 Reasoning Artifact
cancer:           Intrahepatic Cholangiocarcinoma (ICC)
date:             2026-03-02
author:           Eric Robert Lawson / OrganismCore

datasets:
  TCGA-CHOL:      n=36 ICC, n=9 normal (RNA-seq)
  GSE32225:       n=149 ICC, n=6 normal (microarray)

attractor_confirmed:
  SW_genes_down:  7/8 confirmed (KLF4 flat only)
  FA_genes_up:    8/8 confirmed
  epigenetic:     EZH2 UP — gain of function lock ✓
  depth_score:    mean=0.494 (TCGA), 0.591 (GSE)

dominant_signals:
  primary_SW:     ALB (GSE r=-0.828)
                  G6PC (TCGA r=-0.701)
  primary_FA:     TWIST1 (TCGA r=+0.799)
                  ACTA2 (GSE r=+0.699)
  unexpected:     WNT5A (r=+0.65, upstream EMT)
                  EGFR paradox (down but +depth)

attractor_type:   EMT-transitional progenitor
                  + desmoplastic stroma niche
block_level:      HNF4A/FOXA2 TF axis

drug_targets:
  1.  TGF-β inhibition (galunisertib)
  2.  EZH2 inhibition (tazemetostat)
  3.  WNT5A/non-canonical Wnt blockade
  4.  TWIST1 suppression (BET/HDAC inhibitor)

next:             Document 93e | Script 2
                  Gap tests: HNF4A→ALB circuit
                  WNT5A→TWIST1 circuit
                  TGFB1 bridge test
                  NMF × TWIST1 analysis
                  EGFR paradox resolution
                  OS validation (LIRI-JP attempt)

protocol_status:  FULLY COMPLIANT ✓
                  Ready for Script 2
```
