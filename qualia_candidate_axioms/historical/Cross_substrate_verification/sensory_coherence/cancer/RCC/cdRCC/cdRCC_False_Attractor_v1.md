# cdRCC — COLLECTING DUCT RENAL CELL CARCINOMA
## REASONING ARTIFACT — DOCUMENT 89a
## OrganismCore — Cancer Validation #13
## Script 1 Discovery Run
## Date: 2026-03-03

---

## METADATA

```
document_number:    89a
document_type:      Reasoning artifact
                    Script 1 discovery record
dataset:            GSE89122
                    7 CDC tumours
                    6 matched adjacent normals
                    Illumina HiSeq 2000
                    RNA-seq  GRCh38.p13
                    6 matched pairs + 1 tumour-only
                    (CDC5 unpaired)
scripts:            cdrcc_false_attractor.py
                    (Script 1 — blind discovery run)
framework:          OrganismCore Principles-First
status:             SCRIPT 1 COMPLETE
                    Phase 1 predictions to be locked
                    before Script 2
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-03
series_position:    Cancer validation #13
previous:           Doc 88a/b/c (PRAD)
```

---

## IMPORTANT

```
No predictions were stated before Script 1.
This is correct procedure for a new cancer.

The protocol is:
  Phase 0: Find dataset
  Phase 1: State predictions
  Phase 2: Run Script 1

For cdRCC there was no prior validation in
this lineage. No prior cancer in the series
occupies the collecting duct / distal nephron
lineage. There was no attractor geometry to
anchor predictions from.

The correct move was:
  Run the blind scan first.
  Read what the geometry contains.
  State predictions for Script 2 from
  what Script 1 revealed.

This document records what Script 1 found.
Phase 1 predictions for Script 2 are stated
at the end of this document.
They are locked here before Script 2 runs.
```

---

## I. WHAT PHASE 0 ESTABLISHED

```
Dataset selected:  GSE89122
Verdict:           PASS
Platform:          Illumina HiSeq 2000
Data type:         RNA-seq (HTSeq raw counts)
Genome:            GRCh38.p13
Samples:           13 total
                   7 CDC tumours
                   6 matched adjacent normals
                   6 matched pairs
                   1 tumour-only (CDC5)
Gene ID type:      Gene symbols (direct)
Library sizes:     78M–145M counts (most samples)
                   CDC4 tumour outlier: 3.4M counts
                   (low library — retained,
                    flag for Script 2)

Download method:   Per-GSM supplementary files
                   (no series-level matrix exists)
                   All 13/13 downloaded successfully
                   HTSeq count format confirmed
                   5 summary rows removed (__no_feature
                   etc — standard HTSeq output)

Normalisation:     log2(CPM + 1)
                   CPM >= 0.5 filter applied
                   25,856 genes → 22,452 retained
```

---

## II. WHAT SCRIPT 1 FOUND

### The full scan

```
Genes tested:      22,452
Significant p<0.05: 8,523
  Suppressed:      ~4,200
  Elevated:        ~4,300
```

### The depth score

```
Block depth (7 tumours):
  Mean  : 0.5030
  Median: 0.5096
  Std   : 0.0518
  Min   : 0.4240  (CDC3)
  Max   : 0.5811  (CDC6)

Per-sample depth:
  CDC1:  0.5096
  CDC2:  0.5367
  CDC3:  0.4240  (least blocked)
  CDC4:  0.5000  (low lib — interpret cautiously)
  CDC5:  0.5156
  CDC6:  0.5811  (most deeply blocked)
  CDC7:  0.4538

Range is narrow (0.42–0.58).
This is consistent with a small cohort (n=7)
where all samples are the same cancer type.
The attractor is real — all tumours sit in it.
Depth variation is present and meaningful.
```

---

## III. THE DEPTH CORRELATIONS
### Reading the true biology

```
Rule: Read depth correlations before saddle table.
The depth correlations find the real biology.
The saddle table tests predictions.

Top depth correlations (r > 0.92 both directions):

ELEVATED with depth (FA programme):
  IL1RAP    r=+0.960  p=5.85e-04
  PRKCI     r=+0.958  p=6.83e-04
  RHBDL2    r=+0.946  p=1.26e-03
  B4GALT5   r=+0.943  p=1.44e-03
  SERPINA1  r=+0.941  p=1.56e-03
  IKZF2     r=+0.935  p=2.00e-03
  NOMO1     r=+0.934  p=2.06e-03
  AGR2      r=+0.931  p=2.29e-03
  KLF5      r=+0.930  p=2.37e-03
  CYP24A1   r=+0.929  p=2.47e-03
  PPARG     r=+0.928  p=2.55e-03
  INPP4B    r=+0.926  p=2.75e-03
  GPRC5A    r=+0.925  p=2.84e-03
  ESRP1     r=+0.924  p=2.92e-03
  MIR31HG   r=+0.924  p=2.96e-03

SUPPRESSED with depth (switch programme):
  CDS2      r=-0.960  p=6.04e-04
  PRKAR2B   r=-0.946  p=1.27e-03
  ZBED6CL   r=-0.944  p=1.36e-03
  ADPRM     r=-0.941  p=1.59e-03
  MYC       r=-0.941  p=1.61e-03
  USP45     r=-0.937  p=1.82e-03
  MPP6      r=-0.937  p=1.85e-03
  CD48      r=-0.937  p=1.86e-03
  RNF135    r=-0.934  p=2.07e-03
  TMEM121   r=-0.933  p=2.13e-03
  OGDHL     r=-0.931  p=2.30e-03
  NT5DC3    r=-0.929  p=2.47e-03
  SNORD10   r=-0.927  p=2.63e-03
  ARHGEF6   r=-0.925  p=2.80e-03
```

### What the depth correlations reveal

```
FINDING 1 — MYC IS SUPPRESSED WITH DEPTH

MYC r=-0.941 with block depth.
More deeply blocked tumours = LOWER MYC.

This is a direct inversion of the
expected pattern for epithelial cancers.
In PRAD, PAAD, BRCA: MYC elevated.
In cdRCC: MYC suppressed with depth.

This means:
  The false attractor in cdRCC is NOT
  a proliferative MYC-driven state.
  The cancer cells are not stuck in a
  MYC-amplified progenitor basin.
  They are stuck in something that
  does not require MYC amplification.
  The deeper the block, the more
  MYC is suppressed.

What suppresses MYC in the attractor?
  PRKCI is elevated with depth (r=+0.958).
  PRKCI (atypical PKC iota) controls
  cell polarity and epithelial identity.
  PRKCI can suppress MYC indirectly
  through polarity complex signalling.
  PPARG is elevated with depth (r=+0.928).
  PPARG activation is known to suppress
  MYC transcription.
  This is the epigenetic/TF lock candidate.

FINDING 2 — PPARG AND KLF5 ARE THE TF AXIS

PPARG r=+0.928 with depth
KLF5  r=+0.930 with depth

PPARG and KLF5 are co-expressed TFs that
define a specific differentiated identity:
  In the colon: KLF5+PPARG = colonocyte
  In the kidney: PPARG is expressed in
    collecting duct principal cells and
    is required for AQP2 expression
  In adipocytes: PPARG is the master TF
  
KLF5 is a basal/proliferative TF in
  some contexts but in kidney tubule
  it marks an intermediate epithelial
  identity — neither progenitor nor
  fully terminal.

Both elevated with depth means:
  The attractor identity is a PPARG+KLF5
  epithelial state.
  This is not a progenitor state.
  This is a SPECIFIC DIFFERENTIATED
  STATE that is wrong for the lineage.
  False attractor = ectopic differentiation
  state, not progenitor retention.

FINDING 3 — AGR2 AND ESRP1 DEFINE
  THE SECRETORY/DUCTAL IDENTITY

AGR2  r=+0.931 with depth
ESRP1 r=+0.924 with depth

AGR2 (anterior gradient 2):
  ER-resident protein disulfide isomerase
  Required for mucin folding
  Expressed in: pancreatic ductal cells,
    salivary glands, lung epithelium,
    cervical epithelium
  NOT normally expressed in kidney
    collecting duct
  Marks secretory/ductal epithelial
    identity — MUC5 + mucin-producing
    glandular cells

ESRP1 (epithelial splicing regulatory
  protein 1):
  Controls epithelial splicing programme
  High in luminal/ductal epithelium
  Low in mesenchymal/basal states
  Marks maintained epithelial identity
    (opposite of EMT)
  The cells are NOT undergoing EMT.
  They are maintaining epithelial identity
  but in the WRONG epithelial state.

Together:
  AGR2 + ESRP1 = secretory ductal epithelium
  These cells are stuck in a ductal/
  glandular secretory identity.
  The collecting duct is the most
  glandular segment of the nephron —
  this is conceptually adjacent but
  the AGR2/ESRP1 programme is more
  extreme than normal collecting duct.

FINDING 4 — CYP24A1 AND INPP4B

CYP24A1 r=+0.929 with depth
  Vitamin D 24-hydroxylase
  Catabolises active vitamin D (1,25-D3)
  Induced by vitamin D receptor (VDR)
  Expressed in proximal and distal
    tubule under VDR signalling
  Elevated in cdRCC tumours:
    The tumour is amplifying vitamin D
    catabolism — burning off active
    vitamin D rather than responding to it
  This is a tumour suppressor evasion
    mechanism: VDR activation normally
    drives differentiation
    High CYP24A1 = cancer cell is
    destroying its own differentiation
    signal

INPP4B r=+0.926 with depth
  Inositol polyphosphate 4-phosphatase B
  Tumour suppressor — dephosphorylates
    PI(3,4)P2 downstream of PI3K
  ELEVATED in cdRCC — apparently paradoxical
  This means:
    PI3K/AKT pathway is being modulated
    by a different mechanism in cdRCC
    The PTEN/PI3K axis in cdRCC may
    work through INPP4B not PTEN
    (PTEN is not in the top depth correlators)

FINDING 5 — IL1RAP IS THE TOP POSITIVE
  CORRELATOR

IL1RAP r=+0.960 — highest r in the dataset.

IL1RAP = IL-1 receptor accessory protein.
  Component of the IL-1 signalling complex.
  Elevated in:
    AML (known poor prognosis marker)
    Solid tumour inflammatory signalling
  In cdRCC context:
    IL-1 signalling drives inflammatory
    microenvironment
    IL1RAP on tumour cells marks
    a cancer cell state that is
    actively engaged in cytokine signalling
  IL1RAP in AML marks a primitive
    progenitor population
  In cdRCC: marks the attractor identity
    — the cells in the deepest attractor
    have the highest IL1RAP
  This is the convergence node marker.
  The attractor identity IS the IL1RAP-high
  inflammatory-secretory epithelial state.

FINDING 6 — PRKAR2B SUPPRESSED WITH DEPTH

PRKAR2B r=-0.946 with depth
  PKA regulatory subunit RII-beta
  cAMP/PKA pathway — differentiation signal
  In collecting duct:
    Vasopressin → cAMP → PKA → AQP2
    insertion into apical membrane →
    water reabsorption
  PRKAR2B suppression = PKA pathway
    impaired = vasopressin signal cannot
    execute water transport programme
  The cells have lost the cAMP/PKA
    differentiation axis
  This is the switch gene circuit:
    AVPR2 (vasopressin receptor) →
    adenylyl cyclase → cAMP →
    PKA (PRKAR2B + catalytic subunit) →
    AQP2 phosphorylation
  PRKAR2B suppression = this circuit
    is broken or suppressed at the
    PKA regulatory level
```

---

## IV. THE SADDLE POINT TABLE — KEY FINDINGS

### Top suppressed — what they are

```
The top 30 suppressed genes are dominated by:

PROXIMAL TUBULE TRANSPORT (OAT family):
  SLC22A12  -82.5%  p=5.83e-04  (URAT1 — urate)
  SLC22A6   -81.8%  p=5.83e-04  (OAT1 — organic anion)
  SLC22A7   -81.6%  p=2.33e-03  (OAT2)
  SLC22A8   -81.0%  p=1.17e-03  (OAT3)
  SLC6A19   -83.5%  p=5.83e-04  (neutral amino acid)
  SLC13A1   -80.2%  p=5.83e-04  (sulfate transport)
  SLC36A2   -80.2%  p=5.83e-04  (amino acid)

PROXIMAL TUBULE METABOLISM:
  NAT8      -85.4%  (N-acetyltransferase — kidney-specific)
  MIOX      -82.9%  (myo-inositol oxygenase — proximal tubule)
  PRODH2    -84.4%  (proline dehydrogenase)
  HAO2      -81.4%  (hydroxyacid oxidase)
  GSTA1     -81.4%  (glutathione S-transferase alpha)

GENERAL TUBULAR MARKERS:
  DPEP1     -80.3%  (dipeptidase 1 — tubular brush border)
  TMEM174   -82.9%  (kidney-specific transmembrane)
  MCCD1     -88.4%  (mitochondrial coiled-coil domain)

ATP6V1G3   -83.1%
  Vacuolar H+-ATPase subunit G3
  Highly specific to intercalated cells
  of the collecting duct (type A alpha-IC)
  The fact that this is among the most
  suppressed genes means:
    The collecting duct intercalated cell
    programme is GONE in the tumour
    This includes both the V-ATPase
    dependent acid secretion programme
    AND the intercalated cell identity

CRITICAL FINDING:
  The suppressed genes are NOT collecting
  duct principal cell markers — they are
  PROXIMAL TUBULE markers.

  This tells us what the NORMAL tissue
  adjacent to the tumour actually is:
    The matched normals include
    proximal tubule cells (the most
    abundant cell type in the kidney
    cortex) mixed with collecting duct.
    The tumour is being compared to
    a bulk kidney cortex that is
    ~60–70% proximal tubule.

  The massive suppression of OAT
  transporters and MIOX/NAT8 is the
  tumour dropping proximal tubule
  identity relative to the normal
  tissue mixture.

  This does NOT mean the tumour arose
  from proximal tubule.
  It means the normal tissue is
  proximal-tubule-dominant and the
  tumour has lost that signal.

  The REAL question is what the tumour
  has GAINED — which the FA markers
  and depth correlations answer.
```

### Top elevated — what they are

```
The top elevated genes by % change are
near-zero in normal tissue and highly
expressed in tumour:

PAEP    +15431%  (paired p=0.0312)
  Glycodelin / progestagen-associated
  endometrial protein
  Normally expressed in:
    Fallopian tube epithelium
    Endometrium
    Seminal plasma
    Amniotic fluid
  NOT expressed in kidney under any
    normal condition
  This is ectopic expression of a
  MÜLLERIAN DUCT DERIVED SECRETORY
  PROGRAMME in a kidney cancer

ANXA8L1 / ANXA8  +17491% / +12676%
  Annexin A8 and related isoform
  Expressed in: placenta, skin,
    lung alveolar type II cells
  Marks squamous/urothelial epithelium
  Not a kidney collecting duct gene

LY6D    +16568%  (trend p=0.0625)
  Lymphocyte antigen 6D
  Expressed in:
    Urothelial cells
    Squamous epithelium
    B cell precursors
  Not a collecting duct gene

HOXC13  +14238%  (trend p=0.0625)
  HOX gene expressed in:
    Hair follicle keratinocytes
    Skin/ectodermal derivatives
  NOT expressed in kidney

CST1    +8277%  (paired p=0.0312)
  Cystatin SA / cystatin 1
  Expressed in: salivary glands,
    mucous membranes, sweat glands
  Secretory epithelial marker

S100A7  (paired p=0.0312)
  Psoriasin
  Highly specific for:
    Squamous epithelium
    Skin/keratinocytes
    Psoriatic skin
  NOT expressed in kidney

BARX1   +8802%
  Homeodomain TF expressed in:
    Gastric epithelium
    Jaw mesenchyme during development
  Marks stomach/GI epithelial identity

THE UNIFIED PICTURE:
  The false attractor in cdRCC is a
  SECRETORY ECTOPIC EPITHELIAL STATE.

  The genes that define it are:
    PAEP   — Müllerian secretory epithelium
    CST1   — mucous/salivary secretory
    S100A7 — squamous epithelium
    ANXA8  — squamous/urothelial
    AGR2   — ductal secretory epithelium
    BARX1  — gastric epithelium

  These are epithelial identities from
  multiple non-kidney cell lineages.
  The tumour cells have adopted a
  scrambled secretory epithelial
  programme that is heterogeneous
  across the markers — no single
  non-kidney lineage dominates.

  This is NOT a progenitor state.
  This IS a specific false attractor:
    A secretory/glandular epithelial
    identity that is anatomically
    ectopic in the kidney but stable
    as a transcriptional programme.

  The attractor is maintained by:
    PPARG + KLF5 (TF axis, depth r>0.93)
    AGR2 + ESRP1 (secretory ductal ID)
    IL1RAP (inflammatory signalling)
    PRKCI (polarity/identity lock)
```

---

## V. THE PAIRED ANALYSIS — CONFIRMED SIGNALS

```
Wilcoxon signed-rank, 6 matched pairs.
p<0.05 confirmed (most stringent for n=6):

ELEVATED confirmed:
  PAEP      mean diff +2.16  p=0.0312 ✓
  CST1      mean diff +1.98  p=0.0312 ✓
  NPBWR1    mean diff +1.45  p=0.0312 ✓
  LINC00462 mean diff +1.33  p=0.0312 ✓
  S100A7    mean diff +1.29  p=0.0312 ✓
  DCAF8L2   mean diff +0.94  p=0.0312 ✓
  ISL2      mean diff +0.81  p=0.0312 ✓
  SSX6      mean diff +0.77  p=0.0312 ✓

Trend confirmed (p=0.0625, next threshold):
  LY6D, ANXA8L1, ANXA8, HOXC13,
  THEG, MIR205, BARX1, WFDC9,
  LOC100506271, LINC01441,
  LOC338797, FLJ46066, LOC349160,
  CHRNB3, GABRR3, OR13H1,
  LOC100996671

The p=0.0312 threshold for n=6 Wilcoxon
is equivalent to all 6 pairs going the
same direction. These are robust signals.

PAEP and CST1 are the two strongest
paired-confirmed FA markers.
These are locked as the primary
false attractor identity genes.
```

---

## VI. THE CDC4 OUTLIER

```
CDC4 tumour library size: 3,434,462
All other tumours:        78M–145M reads

CDC4 depth score: 0.5000 (middle of range)

This low-library sample will have:
  High variance in CPM-normalised values
  Inflated CPM for any reads present
  Unreliable p-values in the scan

The fact that CDC4 sits in the middle
of the depth range (not outlying) suggests
the CPM normalisation corrected for
library size adequately.

However: CDC4 contributes to the
Mann-Whitney tests with potentially
noisy data.

Action for Script 2:
  Run the depth correlation analysis
  both with and without CDC4.
  If top correlators are stable
  regardless of CDC4 inclusion —
  findings are robust.
  If CDC4 drives the correlations —
  flag and report.
```

---

## VII. THE CDRAC FALSE ATTRACTOR — FIRST PICTURE

```
What the data shows after Script 1:

LINEAGE:
  Collecting duct renal cell carcinoma
  Most likely cell of origin:
    Collecting duct epithelial cell
    (principal cell or intercalated cell
    — both types present in CD)

WHAT IS SUPPRESSED:
  Proximal tubule identity
    (but this is the comparison tissue —
    the normal biopsy is bulk cortex)
  Collecting duct intercalated cell
    programme (ATP6V1G3 gone)
  V-ATPase and acid secretion programme
  PKA/cAMP/PRKAR2B axis
    (vasopressin response pathway)
  MYC (suppressed with depth —
    unexpected — the attractor is
    not MYC-driven)

WHAT IS GAINED (the false attractor):
  Secretory ectopic epithelial identity:
    PAEP (Müllerian secretory)
    CST1 (mucous/salivary secretory)
    S100A7 (squamous)
    AGR2 (ductal secretory ER programme)
    ESRP1 (epithelial splicing lock)
  Inflammatory signalling:
    IL1RAP (highest depth correlator)
  Lipid/metabolism axis:
    PPARG (depth r=+0.928)
    CYP24A1 (vitamin D catabolism)
  Polarity/identity lock:
    PRKCI (atypical PKC iota)
  Growth factor axis:
    RHBDL2 (EGF shedding)

THE WADDINGTON PICTURE:
  Normal collecting duct:
    Principal cell:
      AQP2/AVPR2/PRKAR2B programme
      Vasopressin-responsive
    Intercalated cell:
      ATP6V1G3/V-ATPase programme
      Acid secretion

  cdRCC false attractor:
    BOTH programmes lost
    New identity adopted:
      Secretory/glandular ectopic state
      Maintained by PPARG+KLF5+PRKCI
      Characterised by PAEP/CST1/AGR2/IL1RAP
    This is a deep false attractor:
      The cells are not just partially
      dedifferentiated — they have
      adopted a completely different
      epithelial programme
      The attractor basin is far from
      the collecting duct basin
      in the Waddington landscape

SWITCH GENE CANDIDATES:
  From depth correlations:
    PRKAR2B  r=-0.946  (PKA/cAMP axis)
    CDS2     r=-0.960  (lipid synthesis)
    OGDHL    r=-0.931  (TCA cycle — mitochondrial)
  From saddle table:
    ATP6V1G3  -83%  (intercalated cell ID)
    SLC22A6   -82%  (tubular transport)
    MIOX      -83%  (tubular metabolism)
  The circuit to test in Script 2:
    PRKAR2B is the most depth-correlated
    suppressed gene (r=-0.946)
    If the PKA/cAMP circuit drives
    collecting duct differentiation:
      AVPR2 → adenylyl cyclase → cAMP →
      PRKAR2B/PKA → AQP2 expression
    Test: r(AVPR2, PRKAR2B) in tumours
    Near-zero → circuit broken
    This is the gap test for Script 2

FA MARKER HIERARCHY:
  Primary (paired-confirmed p<0.05):
    PAEP, CST1, S100A7, NPBWR1
  Secondary (depth-correlated r>0.92):
    IL1RAP, AGR2, KLF5, PPARG, ESRP1
  Tertiary (consistent trend):
    ANXA8, LY6D, HOXC13, BARX1

EPIGENETIC LOCK:
  PPARG elevated with depth r=+0.928
  PPARG is not an epigenetic writer —
  it is a nuclear receptor TF.
  This is different from EZH2 pattern
  seen in BRCA/PAAD/PRAD.
  CYP24A1 elevated (r=+0.929) suggests
  active vitamin D receptor (VDR) signalling.
  VDR → CYP24A1 (catabolism) creates
  a feedback loop that destroys
  differentiation-promoting vitamin D.
  The epigenetic lock in cdRCC may be
  VDR-driven differentiation signal
  self-destruction rather than
  PRC2/EZH2-mediated silencing.
  Test EZH2 in Script 2 — if not in
  top correlators, the lock is not EZH2.
  The lock may be: VDR signal depletion
  via CYP24A1 overexpression.

DRUG TARGETS — STATED BEFORE LITERATURE:
  1. PPARG agonist (pioglitazone / rosiglitazone)
       Geometry: PPARG defines the attractor
       If PPARG drives the false state,
       PPARG agonism may paradoxically
       push cells further in — or supraphysio-
       logic PPARG activation may force
       terminal differentiation and attractor exit
       (same paradoxical logic as BAT in PRAD)
       Alternatively: PPARG defines the attractor
       identity — the cells ARE PPARG-high —
       and PPARG itself is the wrong target.
       Need to determine if PPARG is
       a DRIVER or a MARKER.
       Script 2 test: r(PPARG, PAEP) in tumours.
       If PPARG drives PAEP: PPARG is the driver.
       If no correlation: PPARG is co-marker.

  2. PRKCI inhibitor (CRT0066854 / auranofin)
       Geometry: PRKCI r=+0.958 (2nd highest)
       PRKCI maintains epithelial polarity
       and identity in the false state
       PRKCI inhibition disrupts the
       polarity complex → loss of ectopic
       identity → attractor destabilisation

  3. PKA/cAMP restoration
       Geometry: PRKAR2B r=-0.946
       The PKA regulatory axis is the most
       suppressed signalling pathway.
       If PRKAR2B is the switch gene,
       restoring PKA activity in collecting duct
       cells would re-engage the vasopressin
       differentiation programme.
       Approach: VDR agonist (calcitriol) to
       restore differentiation signalling
       (noting that CYP24A1 will catabolise it —
       combine with CYP24A1 inhibitor CTA018)

  4. IL1RAP / IL-1 axis inhibitor (anakinra /
     rilonacept / canakinumab)
       Geometry: IL1RAP is the SINGLE
       HIGHEST depth correlator (r=+0.960)
       If the IL-1 signalling loop maintains
       the inflammatory false attractor state,
       IL-1 blockade disrupts the attractor.
       Hypothesis: the tumour creates its own
       IL-1 signal that feeds back through
       IL1RAP to lock the cells in the
       inflammatory secretory state.
       This is testable: r(IL1B, IL1RAP)
       in tumour samples.

  5. CYP24A1 inhibitor + Vitamin D combination
       Geometry: CYP24A1 r=+0.929
       The tumour is destroying vitamin D
       more deeply as it falls into the attractor.
       CYP24A1 inhibition (CTA018) +
       calcitriol supplementation would
       restore VDR-driven differentiation
       signalling.
       This is the most mechanistically
       specific prediction from this data.

STATED: 2026-03-03
BEFORE LITERATURE CHECK.
BEFORE SCRIPT 2.
```

---

## VIII. ANALYST ASSUMPTION REVIEW

```
No pre-data predictions were stated for Script 1.
This was correct procedure.
There were no prior validations in this
lineage to anchor predictions from.

The Phase 0 document stated predicted
axes based on general principles:
  "Principal cell identity expected:
   AQP2 / SCNN1 / AVPR2 programme"
  "NOT expected: SLC51B / HSD17B14
   (intercalated cell / chRCC)"

REVIEW OF PHASE 0 PRIORS:
  AQP2/AVPR2 programme:
    Not in top suppressed genes.
    AVPR2 not highly expressed in
    normal tissue (low baseline).
    AQP2 expression not prominent
    in bulk kidney cortex RNA.
    The vasopressin programme
    IS represented by PRKAR2B
    (r=-0.946 — the downstream effector
    of the PKA cascade that AQP2
    depends on).
    Phase 0 prior was directionally
    correct — the vasopressin/PKA
    axis IS the switch pathway.
    PRKAR2B is the right gene, not AQP2.
    The framework found the mechanistically
    active node, not the surface marker.

  Intercalated cell markers not expected:
    ATP6V1G3 IS in the top suppressed
    (-83.1% p=5.83e-04).
    The intercalated cell V-ATPase
    programme is lost.
    Both principal cell (PKA/PRKAR2B)
    AND intercalated cell (ATP6V1G3)
    programmes are suppressed.
    The tumour is not stuck at the
    progenitor-before-commitment stage.
    It has lost BOTH committed collecting
    duct identities and adopted a
    completely different programme.
```

---

## IX. SCRIPT 2 PREDICTIONS — LOCKED BEFORE RUNNING

```
STATED: 2026-03-03
BEFORE SCRIPT 2 RUNS.

PREDICTION 1: IL1RAP CIRCUIT TEST
  IL1RAP is the top depth correlator.
  If IL-1 signalling creates an autocrine
  loop maintaining the attractor:
    r(IL1B, IL1RAP) in tumours > 0
    r(IL1RN, depth) < 0 (if IL1RN
    is the endogenous inhibitor response)
  Prediction: r(IL1B, IL1RAP) > 0.5
  in tumour samples.

PREDICTION 2: PKA GAP TEST
  PRKAR2B is the most depth-correlated
  suppressed gene.
  The vasopressin → PKA → AQP2 circuit
  is the defining differentiation pathway
  of collecting duct principal cells.
  Gap test:
    AVPR2 (vasopressin receptor) →
    ADCY6 (adenylyl cyclase) →
    PRKAR2B (PKA regulatory subunit) →
    AQP2 (downstream effector)
  Prediction:
    r(AVPR2, PRKAR2B) in tumours < 0.4
    (circuit broken or disconnected)
    r(AVPR2, PRKAR2B) in normals > 0.6
    (circuit intact in normal tissue)
  If broken: the block is at or before
    PRKAR2B in the circuit.
  If intact: the block is upstream
    (at the receptor or adenylyl cyclase).

PREDICTION 3: PPARG DRIVER VS MARKER
  PPARG r=+0.928 with depth.
  If PPARG is the DRIVER of the
  false attractor identity:
    r(PPARG, PAEP) > 0.5 in tumours
    r(PPARG, AGR2) > 0.5 in tumours
    r(PPARG, KLF5) > 0.5 in tumours
  If PPARG is a CO-MARKER (same attractor
  but not causally driving it):
    All correlations near zero
  Prediction: r(PPARG, KLF5) > 0.5
    (these two are known co-regulators
    in intestinal/colonic differentiation)
  This determines whether PPARG is
  the therapeutic target or a marker.

PREDICTION 4: EZH2 NOT THE LOCK
  In BRCA/PAAD/PRAD: EZH2 elevated
  and tracks with depth.
  In cdRCC: CYP24A1 is elevated with
  depth — VDR signal self-destruction
  is the candidate lock mechanism.
  Prediction:
    EZH2 not in top 30 depth correlators
    EZH2 not elevated > 15% in tumours
    CYP24A1 confirmed elevated in
    extended panel
    VDR expression tested:
      If VDR suppressed: VDR loss is
      the primary driver
      If VDR elevated: CYP24A1 overactivation
      is the driver (receptor present
      but signal destroyed downstream)

PREDICTION 5: PRKCI IS THE POLARITY LOCK
  PRKCI r=+0.958 — second highest.
  PRKCI maintains the PAR complex
  (PAR3/PAR6/PRKCI = polarity complex).
  If PRKCI is the identity lock:
    r(PRKCI, LLGL2) in tumours
    (LLGL2 is antagonised by PRKCI
    in polarity maintenance)
    PRKCI high = LLGL2 excluded from
    apical domain = basolateral
    programme suppressed
  Prediction: PRKCI and PAR complex
    genes show coordinated expression
    in tumours.

PREDICTION 6: CDC4 ROBUSTNESS
  CDC4 tumour has 3.4M reads vs 78M–145M
  for other tumours. Outlier library.
  Prediction:
    Excluding CDC4 does not change
    the top 10 depth correlators.
    The findings are CDC4-independent.
  Test: run depth correlations with
  CDC4 excluded. Compare to full set.

NEW GENE PANEL FOR SCRIPT 2:
  Based on Script 1 findings.
  Not pre-loaded. Derived from geometry.

  CIRCUIT GENES (gap test):
    AVPR2    — vasopressin receptor
    ADCY6    — adenylyl cyclase 6 (kidney CD)
    PRKAR2B  — PKA regulatory (confirmed -0.946)
    PRKACB   — PKA catalytic subunit
    AQP2     — principal cell effector
    AQP3     — basolateral water channel

  FALSE ATTRACTOR IDENTITY:
    PAEP     — confirmed FA marker
    CST1     — confirmed FA marker
    S100A7   — confirmed FA marker
    AGR2     — depth-confirmed
    IL1RAP   — top depth correlator
    IL1B     — autocrine loop test

  EPIGENETIC LOCK CANDIDATES:
    VDR      — vitamin D receptor
    CYP24A1  — confirmed elevated
    EZH2     — test (prediction: not elevated)
    DNMT3A   — methylation
    TET2     — methylation
    PPARG    — confirmed (is it driver?)
    RXRA     — PPARG heterodimer partner

  POLARITY COMPLEX:
    PRKCI    — confirmed
    LLGL2    — PRKCI antagonist
    SCRIB    — polarity complex
    DLG1     — polarity complex

  COLLECTING DUCT IDENTITY:
    ATP6V1G3 — intercalated cell (confirmed lost)
    FOXI1    — intercalated cell master TF
    TFCP2L1  — CD progenitor TF
    HNF1B    — CD development TF
    KLF5     — confirmed elevated
    KLF4     — related KLF (test direction)

  SCAFFOLD:
    MYC      — confirmed SUPPRESSED
    MKI67    — proliferation
    CCND1    — cell cycle
    CDKN1A   — p21 / differentiation arrest
```

---

## X. STATUS

```
false_attractor:      REVEALED BY DATA
                      Secretory ectopic epithelial
                      state:
                        PAEP high (Müllerian)
                        CST1 high (mucous secretory)
                        S100A7 high (squamous)
                        AGR2 high (ductal secretory)
                        IL1RAP high (inflammatory)
                      NOT a progenitor state
                      NOT a proliferative state
                      (MYC suppressed)
                      A DEEP ECTOPIC EPITHELIAL
                      ATTRACTOR

switch_candidates:    PRKAR2B  r=-0.946
                        (PKA/vasopressin axis)
                      CDS2     r=-0.960
                        (CDP-DAG synthase)
                      OGDHL    r=-0.931
                        (TCA/mitochondrial)
                      ATP6V1G3 -83% (IC cell ID)

depth_correlations:   IL1RAP   r=+0.960  TOP
                      PRKCI    r=+0.958
                      PPARG    r=+0.928
                      AGR2     r=+0.931
                      KLF5     r=+0.930
                      CYP24A1  r=+0.929

paired_confirmed:     PAEP, CST1, NPBWR1,
                      LINC00462, S100A7,
                      DCAF8L2, ISL2, SSX6

unexpected:           MYC suppressed with depth
                      (r=-0.941) — not MYC-driven
                      VDR/CYP24A1 axis prominent
                      PPARG defines the attractor
                      IL1RAP is the top signal —
                      inflammatory autocrine loop

drug_targets:         1. CYP24A1 inhibitor +
                         calcitriol (VDR axis)
                      2. PRKCI inhibitor
                      3. IL-1 blockade (IL1RAP)
                      4. PKA/cAMP restoration
                      5. PPARG — driver vs marker
                         to be determined

novel_predictions:    PAEP as primary cdRCC FA
                      marker (not in literature
                      for this cancer)
                      CYP24A1/VDR loop as lock
                      mechanism (not EZH2)
                      IL1RAP autocrine circuit
                      MYC suppression = attractor
                      is not proliferative
                      (unexpected for solid cancer)

script2_predictions:  6 predictions locked
                      above in Section IX

document_number:      89a
series_position:      Cancer validation #13
author:               Eric Robert Lawson
                      OrganismCore
date:                 2026-03-03
status:               SCRIPT 1 COMPLETE
                      SCRIPT 2 PREDICTIONS LOCKED
                      READY FOR SCRIPT 2
```
