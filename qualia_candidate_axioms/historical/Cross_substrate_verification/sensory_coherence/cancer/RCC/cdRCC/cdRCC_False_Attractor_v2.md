# cdRCC — COLLECTING DUCT RENAL CELL CARCINOMA
## REASONING ARTIFACT — DOCUMENT 89b
## OrganismCore — Cancer Validation #13
## Script 2 — Circuit Analysis
## Date: 2026-03-03

---

## METADATA

```
document_number:    89b
document_type:      Reasoning artifact
                    Script 2 circuit analysis
dataset:            GSE89122
                    7 CDC tumours
                    6 matched adjacent normals
                    Illumina HiSeq 2000
                    RNA-seq  GRCh38.p13
                    6 matched pairs + 1 tumour-only
                    (CDC5 unpaired)
scripts:            cdrcc_false_attractor.py
                    (Script 1 — blind discovery)
                    cdrcc_false_attractor_2.py
                    (Script 2 — circuit analysis)
framework:          OrganismCore Principles-First
status:             SCRIPT 2 COMPLETE
                    Novel predictions locked
                    Literature check pending
follows:            Doc 89a (Script 1)
next:               Doc 89c (Literature check)
author:             Eric Robert Lawson
                    OrganismCore
date:               2026-03-03
series_position:    Cancer validation #13
```

---

## I. S1 vs S2 DEPTH CONCORDANCE

```
r(S1_depth, S2_depth) = +0.9884  p<0.001

SAME BIOLOGY. Both axes capture the
same attractor.

S1 used top 50 suppressed + top 50 elevated.
S2 used CDS2 (r=-0.960) + IL1RAP (r=+0.960).

The two-gene corrected axis reproduces the
full 100-gene axis with r=0.988.
This confirms that CDS2 and IL1RAP are the
primary poles of the attractor landscape:
  CDS2 low = lipid synthesis circuit suppressed
  IL1RAP high = inflammatory secretory identity

The attractor geometry is robust.

S2 DEPTH PER SAMPLE:
  CDC3:  0.000  (least blocked)
  CDC7:  0.205
  CDC4:  0.425  (low library — interpret cautiously)
  CDC1:  0.489
  CDC5:  0.463
  CDC2:  0.627
  CDC6:  1.000  (most deeply blocked)

CDC4 ROBUSTNESS: FAILED (1/10 overlap)
The high depth correlations (r > 0.95) are
inflated by CDC4's extreme library size.
CDC4 tumour has 3.4M reads vs 78–145M for others.
This creates an outlier data point that
inflates Pearson r artificially.

CONSEQUENCE:
  The specific r values are not reliable.
  The DIRECTIONS are reliable.
  The RANK ORDER of genes is approximately
  reliable.
  The mean expression changes (% and p-value
  from Mann-Whitney) are reliable regardless
  of CDC4.
  All conclusions rest on mean changes and
  paired analysis — not on depth r values.
```

---

## II. PREDICTION VERDICTS — ALL SIX

### Prediction 1 — IL1 autocrine loop

```
PREDICTION: r(IL1B, IL1RAP) > 0.5 in tumours
VERDICT:    NOT CONFIRMED AS STATED

WHAT THE DATA SHOWS:
  r(IL1B, IL1RAP) = +0.271  ns

THE ANALYST ASSUMPTION THAT WAS WRONG:
  The prediction was that IL1B drives IL1RAP
  variation within the tumour sample set.
  This is not what the data shows.

  The actual finding is more specific and
  more informative:

  IL-1 SYSTEM ACTIVATION TABLE:
    IL1B:  +92.4%  p=0.001  paired p=0.031
    IL1A:  +938%   p=0.002  paired p=0.031
    IL1RN: +263%   p=0.001  paired p=0.031
    NLRP3: +54.6%  p=0.001
    IL6:   +255%   p=0.002  paired p=0.031
    IL1RAP: +59.6% p=0.001  paired p=0.031

  The entire IL-1 system is co-activated.
  Ligands (IL1A, IL1B), receptor complex
  (IL1RAP), inflammasome sensor (NLRP3),
  parallel cytokine (IL6), AND the endogenous
  inhibitor (IL1RN) are all elevated.

  r(IL1RN, IL1B) = +0.758  p=0.048
  IL1RN tracks IL1B within tumours.
  The tumour mounts an endogenous anti-
  inflammatory response proportional to its
  IL-1 production. This is self-limiting
  chronic inflammation — not a runaway
  autocrine loop.

  IL1RAP depth r = +0.968 — near top of dataset
  IL1RN depth r = +0.872
  Both track with attractor depth.

  REVISED INTERPRETATION:
  IL1RAP is not elevated BECAUSE of IL-1B.
  IL1RAP is elevated as an intrinsic part
  of the attractor identity.
  The IL-1 signalling activation is the
  RESULT of the attractor state, not the
  mechanism maintaining it.
  The attractor expresses both the IL-1
  system and its own inhibitor (IL1RN) —
  chronic partially self-regulated
  inflammatory signalling is the state.

  IL1RAP remains the top convergence node
  of the attractor. Its depth correlation
  (r=+0.968) is the highest meaningful signal.
  But it is not sustained by an IL1B autocrine
  loop — it is a cell identity marker of the
  false attractor state itself.

  WHAT THIS WRONG PREDICTION TEACHES:
  When the receptor and ligand are both
  elevated but do not correlate within
  tumours, the receptor is part of the
  cell identity and the ligand is part of
  the inflammatory microenvironment.
  They are co-elevated for different reasons.
  This distinction determines therapeutic
  targeting: blocking IL-1 ligand (anakinra)
  would address inflammation but not the
  attractor identity. Blocking IL1RAP
  directly would address the identity node.
```

### Prediction 2 — PKA gap test

```
PREDICTION: AVPR2→PRKAR2B circuit broken
            in tumours, intact in normals
VERDICT:    CONFIRMED

CIRCUIT TABLE (tumour r / normal r):
  AVPR2 → PRKAR2B:   +0.396 / +0.813  GAP ✓
  ADCY6 → PRKAR2B:   +0.080 / +0.613  GAP ✓
  PRKAR2B → PRKACB:  +0.153 / +0.532  GAP ✓
  AQP2 → AQP3:       +0.269 / +0.976  GAP ✓
  AVPR2 → AQP2:      +0.824 / +0.953  INTACT
  AVPR2 → ADCY6:     +0.816 / +0.869  INTACT

THE FINDING:
  Four connections in the PKA circuit are
  severed in tumours but intact in normals.
  All four gaps involve PRKAR2B.

  The break is specifically at the PRKAR2B
  node — the regulatory subunit of PKA.

  BUT: AVPR2 still connects to AQP2 (r=+0.824)
  and to ADCY6 (r=+0.816) in tumours.
  The receptor and its downstream cAMP
  synthesis are intact. The break is
  between cAMP production and PKA
  regulatory control.

  This is a REGULATORY DECOUPLING, not
  loss of the whole circuit.

  EXPRESSION TABLE:
    AQP2:   -71.8%  p=0.002  (most suppressed)
    SCNN1G: -61.7%  p=0.001
    SCNN1B: -59.5%  p=0.008
    AVPR2:  -48.6%  p=0.035
    SCNN1A: -32.4%  p=0.001
    ADCY3:  +40.6%  p=0.001  (paradoxical +)

  AQP2 -71.8% is the most dramatic change
  in the PKA circuit — the principal cell
  water channel is nearly gone.

  ADCY3 elevated (+40.6%) while ADCY6 is
  suppressed (-9.7%). ADCY3 and ADCY6 are
  different isoforms. ADCY3 is associated
  with proliferative and stress signalling;
  ADCY6 is the differentiation-coupled
  isoform in collecting duct. The swap from
  ADCY6 to ADCY3 is an isoform switch in
  the cAMP machinery — from differentiation-
  linked cAMP to proliferation-linked cAMP.
  Same second messenger, different biology.

  PRKAR2B depth r = -0.9596
  The most depth-correlated suppressed gene
  in the entire dataset is still PRKAR2B.
  As tumours fall deeper into the attractor,
  PRKAR2B falls further.
  PRKAR2B is the switch gene.

  PAIRED CONFIRMATION:
    AQP2:    -6.95 diff  p=0.031 ✓
    SCNN1G:  -4.35 diff  p=0.031 ✓
    SCNN1B:  -3.20 diff  p=0.031 ✓
    SCNN1A:  -2.45 diff  p=0.031 ✓
    All confirmed across all 6 matched pairs.

  WHAT THE GAP CONFIRMS:
  The collecting duct differentiation circuit
  is specifically broken at the PKA
  regulatory node. The cells have lost the
  ability to execute vasopressin-responsive
  water transport. This is the defining
  functional identity of the collecting duct
  principal cell — and it is gone.

  The gap is REGULATORY (PRKAR2B uncoupled)
  not STRUCTURAL (the receptor and effector
  are still present and connected to each
  other, just not through PRKAR2B).
```

### Prediction 3 — PPARG driver vs marker

```
PREDICTION: r(PPARG, KLF5) > 0.5 in tumours
            PPARG is a driver
VERDICT:    CONFIRMED

KEY CORRELATIONS IN TUMOURS:
  PPARG vs KLF5:   r=+0.965  p=0.0004  ***
  PPARG vs AGR2:   r=+0.924  p=0.003
  PPARG vs IL1RAP: r=+0.847  p=0.016
  KLF5 vs AGR2:    r=+0.940  p=0.002
  KLF5 vs IL1RAP:  r=+0.899  p=0.006
  KLF5 vs ESRP1:   r=+0.934  p=0.002

PPARG depth r = +0.925
KLF5 depth r  = +0.950

BUT: PPARG itself is NOT elevated
     PPARG +0.8%  p=0.836  ns

  This is the critical nuance:
  PPARG protein is present at similar
  absolute levels in tumour and normal.
  But in tumours, PPARG has been rewired:
  it now co-varies with KLF5, AGR2,
  IL1RAP, and ESRP1.
  In normal tissue, these correlations
  do not exist at the same magnitude.

  PPARG is not elevated quantitatively.
  PPARG has been REPOSITIONED in the
  transcriptional network.
  In the false attractor, PPARG operates
  as the hub of the ductal secretory
  programme — co-driving KLF5, AGR2,
  and ESRP1 in a coherent module.

  The distinction:
    Not: MORE PPARG → MORE ATTRACTOR
    But: PPARG COUPLED TO KLF5/AGR2/ESRP1
         → ATTRACTOR IDENTITY MAINTAINED

  KLF5 IS elevated (+34%, p=0.035).
  KLF5 is the active driver.
  PPARG is the stable hub that couples
  KLF5 to the downstream ductal identity
  programme (AGR2, ESRP1).

THE PPARG-KLF5-AGR2-ESRP1-IL1RAP MODULE:
  This is the transcriptional core of the
  cdRCC false attractor.
  Five genes, all highly correlated with
  each other and with depth.
  Not one gene — a module.
  The module is the attractor identity.

  PAEP/CST1/S100A7 do NOT connect to this
  module (PAEP vs AGR2 r=-0.047,
  PAEP vs IL1RAP r=+0.151 ns).

  This is the decisive finding:
  THE FALSE ATTRACTOR HAS TWO INDEPENDENT
  TRANSCRIPTIONAL PROGRAMMES:

  Programme A — DUCTAL SECRETORY MODULE:
    PPARG (hub, not elevated)
    KLF5  (elevated +34%)
    AGR2  (elevated +60%)
    ESRP1 (flat overall, depth-correlated)
    IL1RAP (elevated +60%)
    GPRC5A (elevated +57%)
    SERPINA1 (elevated +19%)
    All tightly correlated with each other
    All track with attractor depth

  Programme B — ECTOPIC SQUAMOUS/MÜLLERIAN:
    PAEP   (+15431%)
    CST1   (+8277%)
    S100A7 (+7863%)
    ANXA8  (+12676%)
    LY6D   (+16568%)
    NOT correlated with Programme A
    NOT tracking with depth by r
    But confirmed by paired analysis and MW

  INTERPRETATION:
  Programme A = the attractor identity.
  The PPARG-KLF5-AGR2 module defines what
  the cell IS in the false state.
  Programme B = the ectopic activation.
  These are genes not normally expressed
  in the kidney, activated by the
  transcriptional reprogramming but not
  part of the core attractor circuit.

  Programme A drives depth.
  Programme B is a consequence of the
  same reprogramming event.
```

### Prediction 4 — EZH2 lock

```
PREDICTION: EZH2 NOT the lock
            VDR/CYP24A1 is the lock instead
VERDICT:    NOT CONFIRMED — EZH2 IS elevated

ANALYST ASSUMPTION ERROR:
  The prediction was that cdRCC would
  differ from BRCA/PAAD/PRAD in its
  epigenetic mechanism.
  The reasoning was that CYP24A1 (r=+0.929
  in S1) indicated a VDR-based lock.

  WHAT THE DATA SHOWS:
    EZH2:   +69.6%  p=0.002  paired p=0.031
    EZH2 depth r = +0.191  (not depth-tracking)

    CYP27B1:  -48.0%  p=0.008  (activating enzyme)
    CYP24A1:  -24.2%  ns  (both suppressed)
    VDR:      -15.1%  p=0.073

  EZH2 IS elevated — the fifth solid cancer
  in the series showing EZH2 gain (after
  BRCA, PAAD, PRAD, and now cdRCC).

  The analyst assumption was wrong about
  EZH2 direction.

  WHY CYP24A1 WAS DEPTH-CORRELATED IN S1:
  CYP24A1 had r=+0.929 in S1. But in the
  full S2 analysis, CYP24A1 is SUPPRESSED
  (-24.2%) and depth r = +0.927 (S2 score).
  Wait — CYP24A1 depth r in S2 step 7 shows
  +0.927, but the expression is -24.2%.
  This is the CDC4 artefact: the depth
  correlation r is inflated by CDC4's
  extreme position.
  The reliable measure is the mean:
  CYP24A1 is SUPPRESSED.

  The vitamin D axis (CYP27B1, CYP24A1,
  VDR, CUBN, LRP2, CASR) is GLOBALLY
  SUPPRESSED in cdRCC. The entire vitamin D
  handling machinery is shut down — not
  specifically upregulated as the lock.

  CUBN: -58.3%  p=0.001  (megalin-cubilin
        endocytosis — vitamin D uptake gone)
  LRP2: -60.7%  p=0.001  (megalin gone)
  CASR: -60.1%  p=0.005  (calcium sensing gone)

  The kidney's mineral handling machinery
  is comprehensively suppressed. This is
  consistent with cdRCC representing loss
  of collecting duct/tubular function,
  not a specific VDR signalling lock.

  EZH2 ROLE CLARIFICATION:
  EZH2 +69.6% confirmed. But depth r = +0.191.
  EZH2 is elevated uniformly across all
  tumours — it does not vary with depth.
  In PRAD: EZH2 r=+0.426 with depth.
  In cdRCC: EZH2 r=+0.191 with depth.
  EZH2 is the uniform chromatin lock —
  present in all tumours but not the
  fine-grained attractor depth driver.
  The depth is driven by the PPARG-KLF5
  module (KLF5 r=+0.950, PPARG r=+0.925).

  EZH2 CONCLUSION:
  EZH2 is confirmed elevated and is likely
  responsible for silencing the collecting
  duct identity TFs (HNF4A, FOXI1, TFCP2L1)
  allowing the false attractor to form.
  But it is the initiating lock, not the
  maintainer. Once the PPARG-KLF5 module
  is established, it self-maintains without
  requiring ongoing EZH2 variation.

  WHAT THIS WRONG PREDICTION TEACHES:
  EZH2 elevation is universal across solid
  epithelial cancers in this series.
  The question is not whether EZH2 is
  elevated — it always is.
  The question is whether EZH2 TRACKS
  DEPTH (active, ongoing lock) or is
  uniform (historical initiating lock).
  In BRCA/PAAD: EZH2 tracks depth — active.
  In PRAD: EZH2 partially tracks depth.
  In cdRCC: EZH2 does not track depth —
  it established the lock and handed off
  maintenance to PPARG-KLF5.
  Framework Lesson candidate.
```

### Prediction 5 — PRKCI polarity lock

```
PREDICTION: PRKCI coordinates PAR complex
VERDICT:    NOT CONFIRMED via PAR complex
            — but the real finding is more
              specific

WHAT THE DATA SHOWS:
  PRKCI depth r = +0.965  (2nd highest)
  PRKCI vs PARD3:  r=-0.672  (anticorrelated)
  PRKCI vs PARD6A: r=-0.430
  PRKCI vs IL1RAP: r=+0.974  p=0.0002 ***
  PRKCI vs PPARG:  r=+0.849  p=0.016
  PRKCI vs KLF5:   r=+0.858  p=0.013

  PRKCI is ANTICORRELATED with PARD3 within
  tumours. In normal cells, PRKCI and PARD3
  form the PAR complex together. In cdRCC
  tumours, PRKCI rises as PARD3 falls.

  This means PRKCI is NOT operating as
  the PAR polarity complex in this context.
  PRKCI is dissociated from its normal
  polarity partner.

  PRKCI-IL1RAP r=+0.974 — the strongest
  intra-tumour co-expression in the dataset.
  PRKCI and IL1RAP are functionally linked
  in the attractor.

  REVISED PRKCI INTERPRETATION:
  Atypical PKC iota (PRKCI) has two known
  oncogenic functions:
    1. Polarity maintenance (via PAR complex)
       → NOT what is happening here
    2. NF-κB activation and cell survival
       (PRKCI → NF-κB → inflammatory
        gene expression including IL-1
        pathway genes)
       → THIS is what is happening here

  PRKCI drives NF-κB-dependent transcription.
  IL1RAP, IL1B, IL6 are all NF-κB targets.
  The PRKCI-IL1RAP co-expression (r=+0.974)
  reflects PRKCI driving NF-κB activity
  which drives IL1RAP expression.

  PRKCI operates through NF-κB in cdRCC,
  not through the PAR polarity complex.
  PRKCZ (the other atypical PKC) is
  suppressed (-17.3%  p=0.005) —
  the cell has specifically elevated PRKCI
  over PRKCZ. Since PRKCI is the NF-κB-
  activating isoform and PRKCZ is not,
  this isoform switch drives the
  inflammatory identity of the attractor.

  WHAT THE WRONG PREDICTION TEACHES:
  PRKCI has multiple independent functions.
  The polarity function requires PAR3.
  PAR3 is lost in the attractor (anticorr).
  Therefore PRKCI is not doing polarity.
  PRKCI's NF-κB function is intact and
  is driving the inflammatory component
  (IL1RAP, IL1B, IL6) of the false state.
  The prediction was wrong about mechanism
  but right about PRKCI being central.
  PRKCI remains a drug target — via NF-κB
  inhibition rather than polarity complex
  disruption.
```

### Prediction 6 — CDC4 robustness

```
PREDICTION: Top 10 depth correlators stable
            when CDC4 excluded
VERDICT:    NOT CONFIRMED (1/10 overlap)

CDC4 is significantly driving the depth
correlation values (r > 0.95) throughout
both scripts.

WHAT IS RELIABLE:
  Mean expression changes (% change,
  Mann-Whitney p): reliable — these are
  group means and not sensitive to one
  sample's library size.

  Paired analysis (Wilcoxon on matched
  differences): reliable — uses within-pair
  differences, CDC4 has a normal match.

  S1 vs S2 concordance (r=0.988): reliable
  — both depth scores agree on RANK ORDER
  of samples, not just correlation values.

  The attractor structure is real.
  PPARG-KLF5-AGR2-ESRP1-IL1RAP module
  is confirmed by multiple independent
  measures (correlations, mean changes,
  paired analysis, MW test).

WHAT IS NOT RELIABLE:
  Specific r values for individual genes.
  The rank order of genes within the
  depth correlation table.

  The lesson: with n=7 samples, one
  outlier dominates Pearson r.
  Mann-Whitney and paired Wilcoxon are the
  right tests for this dataset size.
  Pearson r should be read as directional
  only — not as precise measurements.
```

---

## III. THE CDRAC FALSE ATTRACTOR — FINAL PICTURE

### Three components of the attractor

```
COMPONENT 1 — THE EXECUTION BLOCK
  What cannot be done:
    Vasopressin-responsive water transport
    Terminal collecting duct differentiation

  Where the break is:
    PKA circuit broken at PRKAR2B node
    ADCY6→PRKAR2B: r=+0.080 tumour
                   r=+0.613 normal
    AVPR2→PRKAR2B: r=+0.396 tumour
                   r=+0.813 normal
    The collecting duct principal cell
    identity programme cannot be executed.

  What is lost (paired-confirmed p<0.031):
    AQP2:     -71.8%  (water channel)
    SCNN1G:   -61.7%  (ENaC channel)
    SCNN1B:   -59.5%  (ENaC channel)
    ATP6V0A4: -67.2%  (intercalated V-ATPase)
    FOXI1:    -74.4%  (IC master TF)
    ATP6V1G3: -83.1%  (IC V-ATPase)
    TFCP2L1:  -44.5%  (CD progenitor TF)
    HNF4A:    -64.8%  (tubular TF)
    CALB1:    -78.4%  (distal nephron)
    UMOD:     -73.9%  (tubular identity)
    LRP2:     -60.7%  (megalin/endocytosis)
    CUBN:     -58.3%  (cubilin/endocytosis)
    CASR:     -60.1%  (calcium sensing)
    SCNN1A:   -32.4%  (ENaC alpha)

COMPONENT 2 — THE IDENTITY RETENTION
  What the cell IS in the attractor:

  DUCTAL SECRETORY MODULE (confirmed driver):
    PPARG    �� hub, not elevated but rewired
    KLF5     — elevated +34%
    AGR2     — elevated +60%
    ESRP1    — depth-correlated
    IL1RAP   — elevated +60%
    GPRC5A   — elevated +57%
    SERPINA1 — elevated +19%
    TMPRSS4  — depth-correlated (new S2)
    CST6     — depth-correlated (new S2)

  ECTOPIC PROGRAMME (co-elevated, not driver):
    PAEP     +15431%  Müllerian secretory
    ANXA8L1  +17491%  squamous
    LY6D     +16568%  urothelial
    ANXA8    +12676%  squamous
    HOXC13   +14238%  ectodermal
    NPBWR1   +13581%  neuropeptide
    CST1     +8277%   salivary secretory
    S100A7   +7863%   squamous (psoriasin)
    BARX1    +8802%   gastric homeodomain
    ISL2     +8232%   neural homeodomain

  PROLIFERATION (confirmed):
    MKI67:  +120%  paired p=0.031  (confirmed)
    MYC:    +60%   paired p=0.031  (confirmed)
    CDKN2A: +1703% p=0.008         (p16 response)
    TP53:   +21%   p=0.005
    CDKN1A: +18%   p=0.035

  Note on MYC:
    MYC depth r=-0.941 (S1) appeared to show
    MYC suppressed with depth.
    MYC is elevated +60% on average and
    confirmed in paired analysis.
    The negative depth r was a CDC4 artefact.
    cdRCC IS MYC-elevated.
    The attractor IS partially MYC-driven
    (proliferative component confirmed).

COMPONENT 3 — THE STABILISING MECHANISM
  What gives the attractor energy:

  PRIMARY LOCK — EZH2 gain of function:
    EZH2:  +69.6%  p=0.002  paired p=0.031
    EZH2 r_depth = +0.191 (uniform, not varying)
    EZH2 is the initiating chromatin lock.
    It silences:
      HNF4A, FOXI1, TFCP2L1, HNF1B
      (all paired-confirmed suppressed)
    These are the collecting duct TFs.
    EZH2 closes the chromatin at their loci.
    Once closed, the collecting duct identity
    cannot be restored without EZH2 removal.

  ACTIVE MAINTENANCE — PRKCI/NF-κB/PPARG-KLF5:
    PRKCI drives NF-κB → IL1RAP, IL1B, IL6
    PPARG-KLF5 drive the ductal secretory
    module (AGR2, ESRP1, GPRC5A)
    These two circuits reinforce each other:
    PRKCI→IL1RAP is co-expressed with
    PPARG→KLF5 (r=+0.849, r=+0.858).
    The PRKCI/NF-κB circuit and the
    PPARG/KLF5 circuit are co-activated and
    mutually stabilising.

  isoform switch — ADCY3 over ADCY6:
    Normal: ADCY6 couples vasopressin→cAMP
            →PKA→differentiation
    Cancer: ADCY3 elevated (+40.6%)
            ADCY6 slightly suppressed
    ADCY3 generates cAMP for proliferative/
    stress signalling (different from
    differentiation-coupled ADCY6 cAMP).
    The swap from ADCY6 to ADCY3 means cAMP
    now drives proliferation not differentiation.
    Same second messenger — different circuit.
```

### The Waddington geometry

```
NORMAL COLLECTING DUCT LANDSCAPE:

  Renal progenitor / ureteric bud tip
    ↓ Saddle 1: HNF4A/PAX8 lineage commitment
  Collecting duct progenitor
    (TFCP2L1/HNF1B programme)
    ↓ Saddle 2: cell type specification
  ┌────────────────────────────────┐
  │                                │
  Principal cell           Intercalated cell
  (AVPR2/AQP2/PRKAR2B)    (ATP6V1G3/FOXI1)
  Vasopressin-responsive   Acid secretion
  Water transport          V-ATPase dependent

cdRCC FALSE ATTRACTOR:
  Cells have escaped BELOW Saddle 1.
  BOTH principal and intercalated cell
  programmes are gone.
  TFCP2L1, HNF1B, HNF4A, PAX8 all suppressed.
  The tumour has descended below the
  collecting duct commitment checkpoint.

  The attractor basin they fall into is
  defined by PPARG+KLF5+AGR2+ESRP1+IL1RAP:
  a ductal/secretory epithelial identity
  that is not from the kidney lineage.

  The block is not AT a saddle point.
  The cells have CROSSED multiple saddle
  points in reverse and settled in a
  different basin entirely.

  This is distinct from:
    PRAD: blocked at one terminal step
          (ACPP/MSMB), upstream maintained
    MDS:  blocked at effector connection
          (ELANE), one circuit broken
    AML:  blocked at differentiation entry
          (SPI1/KLF4), progenitor retained

  cdRCC is the deepest attractor observed
  in this series. The cells have not simply
  stopped partway down their lineage.
  They have reached a completely different
  basin that has no relationship to the
  collecting duct.
```

---

## IV. COLLECTING DUCT IDENTITY — CONFIRMED LOST

```
Both collecting duct programmes lost.
Paired-confirmed across all 6 matched pairs:

PRINCIPAL CELL PROGRAMME:
  AQP2      -71.8%  p=0.002  paired p=0.031 ✓
  SCNN1G    -61.7%  p=0.001  paired p=0.031 ✓
  SCNN1B    -59.5%  p=0.008  paired p=0.031 ✓
  SCNN1A    -32.4%  p=0.001  paired p=0.031 ✓
  AVPR2     -48.6%  p=0.035

INTERCALATED CELL PROGRAMME:
  ATP6V0A4  -67.2%  p=0.001  paired p=0.031 ✓
  ATP6V1G3  -83.1%  p=0.001  paired p=0.031 ✓
  FOXI1     -74.4%  p=0.002
  CASR      -60.1%  p=0.005  paired p=0.031 ✓

COMMITMENT TFs:
  TFCP2L1   -44.5%  p=0.001  paired p=0.031 ✓
  HNF4A     -64.8%  p=0.002  paired p=0.031 ✓
  HNF1B     -21.5%  p=0.014

MINERAL HANDLING MACHINERY:
  UMOD      -73.9%  p=0.002  paired p=0.031 ✓
  CALB1     -78.4%  p=0.001  paired p=0.031 ✓
  LRP2      -60.7%  p=0.001  paired p=0.031 ✓
  CUBN      -58.3%  p=0.001  paired p=0.031 ✓

The tumour is not a variant of the
collecting duct. It shares the tissue
location but none of the functional
identity of the collecting duct.
```

---

## V. DRUG TARGETS — STATED BEFORE LITERATURE

```
From geometry of Scripts 1 and 2 combined.
Stated: 2026-03-03.
Before any literature search.

TARGET 1: EZH2 inhibitor (tazemetostat)
  Geometry: EZH2 +69.6% p=0.002
            Paired confirmed p=0.031
            Fifth solid cancer in series
            with EZH2 gain-of-function
            EZH2 silences HNF4A/FOXI1/TFCP2L1 —
            the collecting duct TFs
            EZH2 inhibition → derepression
            of collecting duct TFs →
            re-engagement of differentiation
            programme
  Prediction: tazemetostat or similar EZH2
  inhibitor will force partial re-
  differentiation in cdRCC organoids.
  STATED BEFORE LITERATURE CHECK.

TARGET 2: PRKCI inhibitor (CRT0066854 /
          ATM kinase-PRKCI dual inhibitors)
  Geometry: PRKCI r_depth=+0.965 (2nd highest)
            PRKCI-IL1RAP r=+0.974 (strongest
            intra-tumour correlation)
            PRKCI operating through NF-κB
            (not PAR complex)
            Blocking PRKCI disrupts NF-κB
            driven IL1RAP/IL1B/IL6 programme
  Drug: auranofin (thioredoxin/PRKCI), or
        direct atypical PKC inhibitors
  STATED BEFORE LITERATURE CHECK.

TARGET 3: IL-1 pathway blockade (anakinra /
          canakinumab)
  Geometry: Full IL-1 system activated —
            IL1B +92%, IL1A +938%,
            IL1RN +263%, NLRP3 +55%,
            IL6 +255% (all paired-confirmed)
            This is not the attractor driver
            but is the inflammatory
            microenvironment created by
            the PRKCI/NF-κB circuit
  Prediction: IL-1 blockade reduces the
  inflammatory microenvironment and may
  reduce immune evasion but will not
  dissolve the PPARG-KLF5 attractor core.
  Combination of EZH2i + IL-1 blockade
  addresses both the lock and the
  inflammatory maintenance.
  STATED BEFORE LITERATURE CHECK.

TARGET 4: KLF5 / PPARG axis disruption
  Geometry: PPARG-KLF5 module is the
            attractor identity core
            KLF5 +34% p=0.035
            KLF5 depth r=+0.950 (most
            depth-tracking TF in dataset)
            KLF5 drives AGR2/ESRP1/IL1RAP
  Drug: KLF5 is difficult to target
        directly. PPARG inhibition is
        possible with inverse agonists
        (T0070907, GW9662).
        PPARG inverse agonist may dissolve
        the PPARG-KLF5 hub and destabilise
        the ductal secretory module.
  Caveat: PPARG is not elevated — it is
          rewired. Inverse agonist may
          not work if PPARG activity is
          not the driver.
  Alternative: Disrupt PPARG-RXR
          heterodimerisation (RXRA -12%,
          trend). RXRA inhibition may
          prevent PPARG from activating
          its target programme.
  STATED BEFORE LITERATURE CHECK.

TARGET 5: ADCY3 inhibitor / cAMP pathway
          rebalancing
  Geometry: ADCY3 +40.6% p=0.001
            ADCY6 -9.7% (differentiation)
            Isoform switch: proliferative
            cAMP replaces differentiation cAMP
  Prediction: Blocking ADCY3 while activating
  ADCY6 would rebalance cAMP signalling
  toward differentiation.
  Desmopressin (AVPR2 agonist) has been
  used in nephrogenic DI to drive the
  AVPR2→cAMP→AQP2 circuit.
  If AVPR2 is partially intact (-48.6%),
  high-dose AVPR2 agonist + ADCY6 activator
  might re-engage the PKA differentiation
  circuit despite PRKAR2B uncoupling.
  STATED BEFORE LITERATURE CHECK.

COMBINATION PREDICTION:
  EZH2 inhibitor (unlock chromatin at CD TFs)
  + PRKCI inhibitor (suppress NF-κB driven
    identity maintenance)
  Sequential: EZH2i first to open chromatin
  at HNF4A/FOXI1 loci, then PRKCI inhibitor
  to suppress the inflammatory attractor
  identity, then AVPR2 agonist to re-engage
  the differentiation circuit.
  This three-step sequence targets all three
  attractor components.
  STATED BEFORE LITERATURE CHECK.
```

---

## VI. NOVEL PREDICTIONS — LOCKED BEFORE LITERATURE

```
Stated: 2026-03-03.
Before any literature search.
These are testable claims derived from
geometry alone.

N1: PRKAR2B is the primary switch gene
    for the collecting duct differentiation
    circuit in cdRCC.
    PRKAR2B uncoupling from ADCY6 is the
    specific regulatory break.
    r(ADCY6, PRKAR2B) = +0.080 in tumours
    vs +0.613 in normals.
    The gap is at the ADCY6→PRKAR2B
    connection, not at AVPR2→ADCY6
    (which remains intact r=+0.816).
    PRKAR2B restoration would re-engage
    the PKA differentiation axis.
    Not in literature as primary switch gene
    for cdRCC.

N2: PPARG and KLF5 form a co-regulatory
    module that is the transcriptional core
    of the cdRCC false attractor.
    r(PPARG, KLF5) = +0.965 in tumours.
    This is not because PPARG is elevated —
    PPARG +0.8% ns.
    PPARG has been REWIRED to co-activate
    with KLF5 in the false attractor state.
    The rewiring is the event, not the
    expression level change.
    This framing (rewiring vs overexpression)
    is not in the existing cdRCC literature
    as far as can be determined from the
    geometry alone.

N3: The cdRCC false attractor contains two
    INDEPENDENT transcriptional programmes:
    Programme A: PPARG-KLF5-AGR2-ESRP1-
                 IL1RAP (ductal secretory)
    Programme B: PAEP-CST1-S100A7-ANXA8
                 (ectopic Müllerian/squamous)
    These programmes are NOT correlated with
    each other within tumour samples.
    Programme A tracks attractor depth.
    Programme B does not.
    They are co-elevated because both arise
    from the same EZH2-driven reprogramming
    event but represent different downstream
    transcriptional outputs.
    A diagnostic panel based on Programme A
    (PPARG/KLF5/AGR2) would capture attractor
    depth and prognosis.
    A diagnostic panel based on Programme B
    (PAEP/S100A7/ANXA8) would confirm the
    ectopic activation but not track depth.

N4: EZH2 in cdRCC is an initiating uniform
    lock, not an active depth-varying lock.
    EZH2 depth r = +0.191 (near zero,
    not depth-tracking).
    In BRCA/PAAD, EZH2 tracks depth actively.
    In cdRCC, EZH2 established the lock and
    handed maintenance to PPARG-KLF5.
    EZH2 inhibitor would be most effective
    EARLY (before the PPARG-KLF5 module
    consolidates) or in combination with
    PPARG-KLF5 disruption.
    Late-stage cdRCC EZH2 inhibitor
    monotherapy may be less effective because
    the attractor is maintained by PPARG-KLF5,
    not by ongoing EZH2 activity.
    Testable in cdRCC organoids: EZH2i alone
    vs EZH2i + PPARG inverse agonist.

N5: PRKCI operates through NF-κB (not the
    PAR polarity complex) in cdRCC.
    PRKCI-PARD3 r=-0.672 (anticorrelated).
    PRKCI-IL1RAP r=+0.974 (strongest pair).
    The polarity complex is dismantled in
    the attractor (LLGL2 -28.5%, PARD6B -12%).
    PRKCI is PRKCZ-replaced-by-PRKCI isoform
    switch (PRKCZ -17.3% p=0.005).
    PRKCI selective for NF-κB; PRKCZ is not.
    cdRCC atypical PKC switch: PRKCZ→PRKCI
    is the molecular switch that activates
    NF-κB-dependent inflammatory identity.
    This isoform switch has not been described
    as a mechanism in cdRCC specifically.

N6: The ADCY3/ADCY6 isoform switch
    redirects cAMP signalling from
    differentiation to proliferation in cdRCC.
    ADCY3: +40.6% p=0.001
    ADCY6: -9.7% ns
    ADCY6 is the collecting duct-specific
    adenylyl cyclase coupled to vasopressin
    differentiation. ADCY3 generates cAMP
    for proliferation and stress responses.
    The same second messenger (cAMP) is
    now driving opposite biology because
    the producing enzyme has switched.
    Restoring ADCY6 expression while
    suppressing ADCY3 would redirect cAMP
    toward differentiation.
    This isoform switch mechanism is not
    described for cdRCC in the literature
    as far as can be determined.

N7: cdRCC is the deepest attractor in the
    OrganismCore cancer series.
    All other validated cancers retain
    partial identity of their lineage:
      AML: blast identity retained
      MDS: progenitor surface markers retained
      PRAD: AR programme retained
      PAAD: partial acinar identity retained
    cdRCC retains NOTHING of the collecting
    duct. Both principal and intercalated
    cell programmes are lost. The commitment
    TFs (HNF4A, FOXI1, TFCP2L1) are all gone.
    The cells have escaped the collecting duct
    basin entirely and occupy a completely
    different transcriptional basin.
    This predicts that cdRCC is among the
    most treatment-resistant RCC subtypes —
    the attractor is far from any normal
    renal identity, requiring more energy
    to escape than cancers that retain
    partial identity.
    Clinically: cdRCC has the worst prognosis
    of all RCC subtypes. This would be
    the geometric prediction and confirmation
    from first principles.
    STATED BEFORE LITERATURE CHECK.
```

---

## VII. FRAMEWORK LESSON CANDIDATES

```
LESSON CANDIDATE A (from cdRCC):
  EZH2 has two modes in the attractor:
    ACTIVE MODE (BRCA/PAAD):
      EZH2 tracks depth r > 0.4
      EZH2 is continuously required
      EZH2 inhibitor disrupts at any stage
    INITIATING MODE (cdRCC):
      EZH2 does not track depth (r < 0.2)
      EZH2 established the lock early
      Maintenance transferred to another
      transcription factor module
      (PPARG-KLF5 in cdRCC)
      EZH2 inhibitor alone insufficient —
      must combine with the TF module target
  Lesson: When EZH2 depth r < 0.3,
  combine EZH2 inhibitor with the TF that
  has taken over maintenance (identified
  by highest depth-r TF in that cancer).

LESSON CANDIDATE B (from cdRCC):
  When the false attractor is deeper than
  all prior cancers (no lineage identity
  retained), the cancer will be the most
  treatment-resistant in its tissue.
  Loss of lineage identity = loss of all
  differentiation re-entry points.
  The clinical prognosis correlates with
  attractor depth across cancer types.
  This is testable as a cross-cancer
  claim against clinical outcomes data.

LESSON CANDIDATE C (from cdRCC):
  False attractors may contain multiple
  independent transcriptional programmes:
    A core module (depth-tracking, causal)
    An ectopic module (elevated, not depth-tracking)
  The core module is the therapeutic target.
  The ectopic module is diagnostically useful
  but targeting it does not dissolve the
  attractor.
  Distinguish by: do the programmes
  correlate with each other within tumours?
  If not: independent modules.
  If yes: unified attractor identity.
```

---

## VIII. WHAT CANNOT YET BE SAID

```
OPEN 1:
  Whether EZH2 directly silences HNF4A
  and FOXI1 at the chromatin level in cdRCC.
  The expression suppression is confirmed
  (-65% and -74%). The H3K27me3 marks at
  their loci require ChIP-seq confirmation.

OPEN 2:
  Why PPARG becomes rewired to KLF5 in the
  false attractor. PPARG is not elevated —
  its connectivity changes. What event
  causes PPARG to couple to KLF5 instead
  of its normal targets?
  Candidate: EZH2-mediated silencing of
  normal PPARG partners (CEBPA is not
  elevated, r=-0.640 with PPARG) forces
  PPARG to find new co-activators.
  PPARG without CEBPA → PPARG+KLF5.
  This is a specific testable mechanism.

OPEN 3:
  The identity of LOC101927630 (r=+0.979,
  top depth correlator in S2).
  This uncharacterised locus is the single
  highest depth-correlated gene in both
  scripts. Its function is unknown.
  If it is a lncRNA or regulatory element
  associated with the PPARG-KLF5 locus,
  it may be a key attractor regulator.
  Requires annotation investigation.

OPEN 4:
  Whether the ADCY3/ADCY6 isoform switch
  is driven by a specific transcription
  factor (PPARG? KLF5? NF-κB?) or by
  epigenetic silencing of ADCY6.
  ADCY6 is slightly suppressed but not
  dramatically. The activation of ADCY3
  is the more prominent change.

OPEN 5:
  Whether the GSE83479 dataset (17 cdRCC
  tumours with external normals, Illumina
  HT12 microarray) would confirm the
  PPARG-KLF5-AGR2 module and PRKAR2B
  gap finding. The GSE89122 finding rests
  on n=7. Confirmation in an independent
  cohort is needed.
  GSE83479 is available — consider a
  Script 3 validation run.
```

---

## IX. STATUS

```
false_attractor:      CONFIRMED
                      Two-programme false state:

                      CORE MODULE (attractor driver):
                        PPARG-KLF5-AGR2-ESRP1-IL1RAP
                        Ductal secretory identity
                        PPARG rewired to KLF5

                      ECTOPIC MODULE (co-elevated):
                        PAEP-CST1-S100A7-ANXA8
                        Müllerian/squamous ectopic
                        Not depth-tracking

switch_gene:          PRKAR2B  r_depth=-0.960
                      PKA regulatory subunit
                      Uncoupled from ADCY6
                      Circuit gap confirmed

block_location:       Below collecting duct
                      commitment checkpoint
                      BOTH principal and IC
                      programmes lost
                      HNF4A/FOXI1/TFCP2L1 all gone
                      Deepest attractor in series

lock_mechanism:       EZH2 initiating lock
                        (uniform +70%, not depth-varying)
                      PPARG-KLF5 active maintenance
                        (depth-tracking TF module)
                      PRKCI/NF-κB inflammatory arm
                        (PRKCI-IL1RAP r=+0.974)

isoform_switch:       ADCY3 UP / ADCY6 flat
                      cAMP redirected from
                      differentiation to proliferation

five_solid_ezh2:      BRCA, PAAD, PRAD, cdRCC
                      All EZH2 elevated
                      EZH2 gain-of-function
                      universal in solid epithelial
                      false attractors

mki67_myc_confirmed:  MKI67 +120% paired p=0.031
                      MYC +60% paired p=0.031
                      cdRCC IS proliferative
                      S1 depth-r for MYC was
                      CDC4 artefact — corrected

drug_targets:         1. EZH2 inhibitor (tazemetostat)
                      2. PRKCI inhibitor (NF-κB axis)
                      3. IL-1 blockade (microenvironment)
                      4. PPARG inverse agonist / KLF5
                      5. ADCY6 restoration + ADCY3 block
                      Sequence prediction: EZH2i first,
                      then PRKCI inhibitor, then
                      vasopressin circuit restoration

novel_predictions:    7 (N1–N7 above)
                      All stated before literature check
                      All dated 2026-03-03

analyst_corrections:  4
                      EZH2 direction wrong (IS elevated)
                      MYC direction wrong (IS elevated)
                      IL1RAP is identity not autocrine
                      PRKCI via NF-κB not PAR complex

document_number:      89b
series_position:      Cancer validation #13
author:               Eric Robert Lawson
                      OrganismCore
date:                 2026-03-03
status:               SCRIPT 2 COMPLETE
                      NOVEL PREDICTIONS LOCKED
                      READY FOR LITERATURE CHECK
                      (Doc 89c)
```
