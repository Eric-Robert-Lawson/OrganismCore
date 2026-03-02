# chRCC False Attractor — Methodological Record
## OrganismCore | Document 96-METHOD | 2026-03-02
### Author: Eric Robert Lawson

---

## PURPOSE OF THIS DOCUMENT

This document records the methodological failure in Documents 96a and 96b
and establishes the correct framework for Script 3 onward.

It is preserved permanently in the OrganismCore record because the failure
mode is instructive and because the raw geometric data produced in 96a/96b
remains valid and is carried forward.

---

## 1. The Framework as Intended

The false attractor framework has a single epistemological commitment:

```
The data defines the geometry.
The geometry defines the biology.
The biology is not known in advance.
```

Applied to cancer:

```
NORMAL SAMPLES     → anchor the normal pole
TUMOUR SAMPLES     → occupy the attractor basin
PC1 of joint space → the transition trajectory
Top PC1 correlates → empirical attractor identity
```

The attractor identity is whatever the geometry says it is.
Not whatever the literature says chRCC should be.
Not whatever was found in a related cancer.
Not whatever was predicted before the analysis ran.

The framework is a discovery instrument.
It produces knowledge only when it is allowed to be surprised.

---

## 2. What Actually Happened in Scripts 1 and 2

### The contamination sequence

**Stage 1 — Pre-selected gene panels (Script 1, OBJ-3)**

Before running any analysis, gene panels were constructed from literature:

```python
INTERCALATED = ["ATP6V1B1", "FOXI1", "SLC4A1", ...]
PROXIMAL     = ["SLC22A6", "SLC34A1", "CUBN", ...]
BILIARY      = ["KRT7", "KRT19", "ERBB2", ...]
INVASION     = ["LAMC2", "VIM", "SNAI1", ...]
MITO         = ["SDHA", "PPARGC1A", "ESRRA", ...]
```

These panels encode the prior belief that chRCC biology is organised
around intercalated cell identity, proximal tubule metabolism, biliary
transition, EMT, and mitochondrial accumulation — because that is what
the chRCC literature says.

The data was then measured against these panels.
The result — PROXIMAL_TUBULE mean_r = +0.4265 — does not tell you
what the attractor is. It tells you how well the attractor fits
the proximal tubule panel that was designed to test it.
These are not the same thing.

**Stage 2 — Pre-registered predictions**

Six predictions were locked before analysis:

```
C1-P1: ATP6V1B1 falls with depth r < -0.30
C1-P2: FOXI1 falls with depth r < -0.30
C1-P3: KRT7 rises with depth r > +0.20
C1-P4: EZH2 rises with depth r > +0.20
C1-P5: OGDHL falls with depth r < -0.20
```

These predictions were derived from:
- Known chRCC biology (IC origin, biliary transition)
- PRCC analysis results imported as analogical priors
- General RCC chromatin literature (EZH2 in PRCC)

When predictions failed 0/5, the failure was attributed to platform artefacts.
That explanation may be partially correct — but the deeper failure is that
the prediction structure itself was the wrong epistemological frame.
A discovery instrument should not have predictions.
It should have questions.

**Stage 3 — PRCC fixed reference (Script 1, OBJ-5)**

60 genes were imported with fixed r-values from Documents 95a-95g
(the PRCC analysis) and used to classify chRCC genes:

```
SHARED_ATTRACTOR, DIVERGENT(+/-), PRCC_SPECIFIC, chRCC_SPECIFIC
```

This framing made PRCC's geometry the reference standard for chRCC.
The chRCC attractor was characterised as deviations from PRCC,
not as an independent geometric structure.

**Stage 4 — Literature drug target panels (Scripts 1 and 2, OBJ-6/7)**

Drug targets were pre-selected from known RCC biology:

```python
DRUG_TARGETS = [
    ("EZH2_inhibitor",  "EZH2"),
    ("mTOR_rapalogue",  "MTOR"),
    ("ERBB2_TDXd",      "ERBB2"),
    ...
]
```

The analysis then measured these pre-selected genes against the depth axis.
The result is a confirmation check on known targets, not a discovery of
new targets from the geometry.

**Stage 5 — ccRCC fixed reference (Script 2, OBJ-8)**

A three-way comparison was constructed using ccRCC r-values from literature.
The ccRCC values were not computed from data — they were imported as constants.
This further anchored the analysis to prior knowledge rather than geometry.

### Summary of contamination

| Script | OBJ | Contamination type | Impact |
|---|---|---|---|
| Script 1 | OBJ-3 | Pre-selected IC/PT/biliary panels | Measured data against prior, not prior against data |
| Script 1 | OBJ-3 | Pre-registered predictions | Imposed hypothesis-testing on discovery analysis |
| Script 1 | OBJ-5 | PRCC fixed reference | Defined chRCC geometry relative to another cancer |
| Script 1 | OBJ-6 | Literature drug target list | Confirmation of known targets, not discovery |
| Script 2 | OBJ-1 | Pre-selected chromatin panel | Same contamination as OBJ-3 |
| Script 2 | OBJ-2 | Pre-selected PT TF panel | Same contamination |
| Script 2 | OBJ-3 | Pre-selected metabolic panels | Same contamination |
| Script 2 | OBJ-5 | Pre-selected cell cycle panel | Same contamination |
| Script 2 | OBJ-6 | Pre-selected immune panel | Same contamination |
| Script 2 | OBJ-7 | Literature drug tier system | Confirmation bias |
| Script 2 | OBJ-8 | ccRCC fixed reference imported | Prior-anchored three-way |

### The consequence

The literature check performed in Scripts 1 and 2 is not just limited —
it is actively misleading within this framework.

If the geometry confirms the literature, you cannot distinguish:
  (a) The literature is correct and the data agrees
  (b) The analysis was designed to find what was expected

If the geometry contradicts the literature, the contradiction gets
explained away as a technical artefact rather than treated as
information about the biology.

The framework lost its ability to be surprised.
A framework that cannot be surprised cannot discover.

---

## 3. What Is Clean and Carried Forward

### Geometrically valid outputs

The following outputs were produced by direct geometric measurement
with no prior contamination:

**depth_scores.csv**
- PC1 of the joint normal+tumour expression space
- No gene panels, no priors, no predictions involved
- PC1 = 72.7% variance
- Normal mean = 0.022, chRCC mean = 0.929
- MW p = 4.31×10⁻⁹
- This is a valid geometric measurement

**attractor_gene_panel.csv**
- r(gene, depth) for 14,833 expressed genes
- Computed directly from the data
- No pre-selection, no panels
- This is the raw geometry of the transition
- It is the primary valid output of the entire pipeline

**oncocytoma_separator.csv**
- Direct MW test between chRCC and oncocytoma expression
- No pre-selection involved
- 4,320 significant discriminators
- Valid

**The four uncontaminated findings**

These genes appeared at the top of the geometric ranking
without being in any pre-selected panel and without being predicted.
They are the only findings that are genuinely data-driven:

```
FOXA2   r = +0.899 ★★★   pioneer TF — not predicted, not in any panel
RUNX2   r = +0.849 ★★★   bone TF — not predicted, not in any panel
EED     r = −0.785 ★★★   PRC2 scaffold — appeared in chromatin panel
                          but as a surprise, not a prediction
IDH1    r = −0.845 ★★★   cytoplasmic IDH — not predicted, not in any panel
```

These four define the starting point for Script 3.

### What is contaminated but numerically recoverable

The r-values for individual genes in the pre-selected panels are geometrically
valid numbers — the contamination was in the selection and framing, not in
the computation. These values can be re-used in Script 3 if the genes
are encountered as outputs of an unbiased analysis rather than as
pre-selected inputs.

---

## 4. The Correct Framework for Script 3 Onward

### The single methodological rule

```
No gene, panel, or target enters the analysis
as an input.

Every gene, programme, and target must emerge
as an output of the geometric analysis.

Biological interpretation happens after
the geometry is fully characterised.
It does not shape the geometry.
```

### The correct analysis sequence

```
STEP 1 — FULL MANIFOLD GEOMETRY
  Input:  expression matrix + depth scores
  Method: PC1 through PC5
          Variance explained per component
          What axis does each PC represent?
          (determined after computation, not before)
  Output: The shape of the expression manifold

STEP 2 — BIMODALITY TEST
  Input:  PC1 depth scores
  Method: Hartigan's dip test
          Gaussian mixture model (k=2,3,4)
  Question: Is the attractor discrete or continuous?
            Are there subgroups within the tumour basin?
  Output: Nature of the attractor basin

STEP 3 — UNBIASED PROGRAMME DISCOVERY
  Input:  Top 200 and bottom 200 PC1 correlates
          from attractor_gene_panel.csv
          (already computed — no new data needed)
  Method: GO enrichment, KEGG enrichment
          on the ranked gene list
          NO pre-selected panels
  Output: What programmes does the data say
          are gained and lost?
          These are the attractor identity
          and the lost normal identity.

STEP 4 — MODULE STRUCTURE
  Input:  Expression matrix, depth scores
  Method: Partial correlations given depth
          r(gene_i, gene_j | PC1)
          Identifies co-regulated modules
          independent of the depth axis
  Output: Programme modules that are not
          explained by the transition alone

STEP 5 — PC2 INTERPRETATION
  Input:  PC2 scores per sample
  Method: Correlate genes with PC2
          Compare PC2 positions of chRCC vs oncocytoma
  Question: Do chRCC and oncocytoma separate on PC2?
            What is PC2 capturing?
  Output: Secondary structure of the manifold
          Potential chRCC subtypes

STEP 6 — REVERSAL VECTOR
  Input:  PC1 loadings, expression matrix
  Method: Identify minimum gene set S such that
          forcing S toward normal-pole values
          shifts PC1 score by > 0.5
  Output: The minimal intervention set
          This is the geometry-derived
          drug target list

STEP 7 — BIOLOGICAL INTERPRETATION
  Input:  Outputs of steps 1-6 only
  Method: Map gene sets to known biology
          AFTER the geometry is complete
  Rule:   Interpretation is constrained by
          geometry. Geometry is not shaped
          by interpretation.
```

### What Script 3 does not contain

```
✗ No pre-registered predictions
✗ No pre-selected gene panels
✗ No imported fixed references
  from other cancers
✗ No literature drug target lists
✗ No prediction scorecard
✗ No hypothesis testing structure
```

### What Script 3 does contain

```
✓ Full manifold geometry (PC1-PC5)
✓ Bimodality test
✓ GO/KEGG enrichment on ranked geometry
✓ Partial correlation modules
✓ PC2 structure and subtype analysis
✓ Reversal vector calculation
✓ Biological interpretation
  constrained by geometry
✓ Drug targets from reversal vector only
```

---

## 5. What Documents 96a and 96b Are

They are a record of a prior-driven analysis applied to valid geometric data.

The geometric data they produced is correct.
The interpretive framework applied to that data was wrong.

They are preserved because:
1. The raw geometric outputs (depth_scores.csv,
   attractor_gene_panel.csv) are carried forward
2. The failure mode is part of the scientific record
3. The four uncontaminated findings (FOXA2, RUNX2,
   EED, IDH1) emerged from these scripts and are valid

They should be read as:
- Documents 96a/96b produced valid geometry
- Documents 96a/96b applied contaminated interpretation
  to that geometry
- Document 96c (Script 3) applies correct interpretation
  to the same geometry

---

## 6. The State of Knowledge Entering Script 3

### What is known from geometry alone

```
The chRCC expression manifold has a dominant
axis (PC1, 72.7% variance) that separates
normal kidney from chRCC/oncocytoma.

Along this axis:

MOST POSITIVE (attractor pole):
  FOXA2, PFKP, G6PC3, RUNX2, HNF1B,
  KHK, MLXIPL, KLF15, FOXP3, IDH2
  [and 14,823 others ranked below these]

MOST NEGATIVE (normal pole):
  IDH1, EED, FBP1, TET2, NR3C1,
  PPARGC1A, DNMT1, SMARCA2
  [and 14,823 others ranked below these]

chRCC and oncocytoma are geometrically
indistinguishable on PC1.
They are distinguishable at the gene level
(4,320 significant MW differences).
The nature of their separation requires
PC2 analysis.
```

### What is not yet known

```
What the attractor identity means biologically
— this requires unbiased GO enrichment
  on the ranked gene list (Step 3)

What the secondary structure is
— this requires PC2 analysis (Step 5)

Whether the attractor is discrete or continuous
— this requires bimodality test (Step 2)

What the minimal intervention set is
— this requires reversal vector (Step 6)

What chRCC actually is
— the geometry will say
```

---

## 7. A Note on the PRCC Comparison

Documents 95a-95g (the PRCC analysis) were produced with the same
literature-contaminated method as Documents 96a-96b.

The PRCC r-values used as fixed references in Script 1 OBJ-5 were
themselves produced by a prior-driven analysis.

This means the cross-cancer comparison in OBJ-5, while numerically valid
for the specific genes measured, cannot be used as a clean geometric
comparison between two independently characterised attractors.

A clean cross-cancer comparison would require:
1. Independent geometric characterisation of PRCC (no prior panels)
2. Independent geometric characterisation of chRCC (Script 3)
3. Comparison of the two geometries
   (angle between attractor axes,
    overlap of top correlate gene sets,
    shared vs unique manifold structure)

This is work for a future document after Script 3 is complete.

---

## 8. Status Summary

| Component | Status | Action |
|---|---|---|
| Expression matrix | ✓ Valid | Carry forward |
| Depth scores | ✓ Valid | Carry forward |
| attractor_gene_panel.csv | ✓ Valid | Primary input for Script 3 |
| oncocytoma_separator.csv | ✓ Valid | Input for Script 3 PC2 analysis |
| Panel scores (96a OBJ-4) | ✗ Prior-contaminated | Discard interpretive layer |
| Prediction scorecard (96a) | ✗ Wrong frame | Discard |
| PRCC fixed reference (96a OBJ-5) | ✗ Prior-contaminated | Discard framing, numbers recoverable |
| Drug target panels (96a/96b) | ✗ Prior-contaminated | Discard, replace with reversal vector |
| Four uncontaminated findings | ✓ Valid | Starting point for Script 3 |
| ccRCC fixed reference (96b) | ✗ Imported prior | Discard |
| GO enrichment | ✗ Not yet done | Script 3 Step 3 |
| PC2-PC5 analysis | ✗ Not yet done | Script 3 Step 2/5 |
| Bimodality test | ✗ Not yet done | Script 3 Step 2 |
| Reversal vector | ✗ Not yet done | Script 3 Step 6 |

---

*Document 96-METHOD | OrganismCore | 2026-03-02 | Eric Robert Lawson*
*Purpose: Methodological record and framework correction*
*Supersedes: Interpretive layers of Documents 96a and 96b*
*Followed by: Document 96c (Script 3 — geometry-first analysis)*
