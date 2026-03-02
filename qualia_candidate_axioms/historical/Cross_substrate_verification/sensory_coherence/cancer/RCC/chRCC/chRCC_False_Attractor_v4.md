# chRCC False Attractor — Script 4 Reasoning Artifact
**OrganismCore | Document 96d-R | 2026-03-02**
**Author: Eric Robert Lawson**

---

## Methodological commitment

The data defines the geometry.
The geometry defines the biology.
The biology is not known in advance.

No predictions. No pre-selected gene panels. No imported references
from other cancers. No literature drug target lists.

Every finding in this document emerges from the geometry.
Biological interpretation is constrained to what the geometry produced.
It does not shape the geometry.

---

## Inputs consumed from Script 3

| File | Content |
|---|---|
| `pc_scores.csv` | PC1–PC5 per sample (83 samples) |
| `pc_loadings.csv` | PC1–PC5 loadings per gene (top 5000) |
| `reversal_vector.csv` | Per-gene pc1_shift for all 5000 genes |
| `reversal_min_set.csv` | Gap/2 set from Script 3 (n=4933) |
| `top200_attractor.csv` | Top 200 PC1 correlates |
| `bot200_normal.csv` | Bottom 200 PC1 correlates |
| `partial_corr.csv` | 100×100 partial correlation matrix |
| `pc2_correlates.csv` | PC2 gene correlates (all 83 samples) |
| `pc2_subtype_genes.csv` | PC2-hi vs PC2-lo chRCC genes |
| `depth_scores.csv` | Normalised PC1 depth per sample |

---

## S1 — GMM Cluster Anatomy

### What was done
GMM k=4 was re-fitted on PC1 scores (all 83 samples). Clusters were
ordered by ascending mean PC1. Each cluster was characterised by
PC1 mean, PC2 mean, depth mean, and class composition.

### What the geometry produced

```
Cluster  n    PC1_mean   PC2_mean  depth_mean  composition
0       31    -46.732    +15.979     0.010      normal (31)
1       22    -42.508    -23.318     0.040      normal (22)
2       21    +76.610     -0.619     0.907      chRCC (11) + oncocytoma (10)
3        9    +86.118     +3.404     0.976      chRCC (4) + oncocytoma (5)
```

### Key observations

**Normal basin splits on PC2, not depth.**
Clusters 0 and 1 are both depth ≈ 0 (normal), but their PC2 means
are +15.979 and −23.318 respectively. The normal samples span the
full PC2 range. This means PC2 is not a tumour-specific axis — it
has large variance in normal kidney too. The PC2 separation of
chRCC vs oncocytoma observed in Script 3 must be understood against
this background.

**Attractor basin also splits on PC2.**
Clusters 2 and 3 are both in the attractor (depth 0.907 and 0.976),
but differ on PC2 (−0.619 vs +3.404) and differ significantly in
depth (MW p<0.0001). Cluster 3 is the deeper, smaller group (n=9)
with slightly higher PC2. This is a within-attractor gradient, not
a discrete second state.

**MW tumour cluster 2 vs 3 on PC2: p=0.0001.**
The two tumour GMM clusters are statistically distinguishable on PC2.
However, both clusters contain mixed chRCC and oncocytoma. Cluster 2:
chRCC=11, oncocytoma=10. Cluster 3: chRCC=4, oncocytoma=5. The PC2
axis does not cleanly separate chRCC from oncocytoma within the
attractor at the GMM cluster level.

**Interpretation (geometry-constrained):**
The GMM k=4 structure reflects one depth gradient in the normal basin
(two normal clusters on opposite ends of PC2) and one depth gradient
in the attractor basin (a shallower mixed cluster and a deeper mixed
cluster). There is no evidence of a discrete second attractor state.
Cluster 3 is the deepest subpopulation of the attractor, not a
qualitatively different state.

---

## S2 — Reversal Vector Triage

### What was done
The 5000-gene reversal vector from Script 3 was filtered to three
nested tiers using geometry-only criteria:

- **Tier 1:** |expression gap| ≥ 0.50 AND |loading| ≥ Q75 of all
  loadings (Q75 = 0.0157). Both conditions must hold.
- **Tier 2:** Tier 1 ∩ top-200 PC1 attractor correlates.
- **Tier 3:** Tier 2 ∩ module genes (genes present in the 100-gene
  partial-correlation matrix from Script 3 S4).

No external knowledge was used to set any threshold. The gap
threshold of 0.50 divides the normalised [0,1] expression range
at the midpoint. The loading threshold is the empirical Q75.

### Results

| Tier | n | Criterion |
|---|---|---|
| Full reversal set | 5000 | All genes |
| Tier 1 | 468 | High gap + high loading |
| Tier 2 | 33 | Tier 1 ∩ attractor-correlated |
| Tier 3 | 7 | Tier 2 ∩ independently co-regulated |

### Tier 1 top genes (first 10 by pc1_shift)

| Gene | loading | N_mean | T_mean | gap | pc1_shift |
|---|---|---|---|---|---|
| RPL10 | +0.0165 | 0.093 | 0.995 | 0.902 | −0.0149 |
| AKR1C1 | +0.0165 | 0.089 | 0.943 | 0.853 | −0.0141 |
| GNAO1 | +0.0166 | 0.084 | 0.927 | 0.843 | −0.0140 |
| AKR1C3 | −0.0162 | 0.963 | 0.105 | 0.858 | −0.0139 |
| PRR11 | +0.0164 | 0.121 | 0.951 | 0.830 | −0.0136 |
| LARP1 | +0.0164 | 0.115 | 0.942 | 0.827 | −0.0136 |
| SPCS2 | +0.0163 | 0.150 | 0.973 | 0.823 | −0.0134 |
| RAB3GAP2 | −0.0165 | 0.850 | 0.038 | 0.812 | −0.0134 |
| UGT2B17 | −0.0161 | 0.874 | 0.042 | 0.832 | −0.0134 |
| POMP | +0.0163 | 0.143 | 0.959 | 0.816 | −0.0133 |

### Tier 2 (33 genes)
All 33 Tier 2 genes have positive loading, meaning they are all
high in tumour, low in normal, and co-directional with the PC1
attractor axis. Every Tier 2 gene is a SUPPRESS target. There are
no RESTORE targets in Tier 2 — the attractor-correlated high-gap
genes are exclusively in the direction of genes the tumour acquires.

### Tier 3 (7 genes — the minimal geometrically coherent set)

| Gene | loading | gap | pc1_shift | Action |
|---|---|---|---|---|
| C4orf17 | +0.0164 | 0.652 | −0.0107 | SUPPRESS |
| AKR1E2 | +0.0159 | 0.646 | −0.0103 | SUPPRESS |
| C1orf94 | +0.0161 | 0.635 | −0.0102 | SUPPRESS |
| ZNF574 | +0.0160 | 0.631 | −0.0101 | SUPPRESS |
| PAK3 | +0.0160 | 0.614 | −0.0098 | SUPPRESS |
| BTNL3 | +0.0161 | 0.602 | −0.0097 | SUPPRESS |
| MAP3K19 | +0.0158 | 0.601 | −0.0095 | SUPPRESS |

**All 7 Tier 3 genes are SUPPRESS targets.** They are high in tumour
(T_mean 0.739–0.852), low in normal (N_mean 0.088–0.206), have
strong PC1 loadings, and are members of independently co-regulated
modules from Script 3.

### Reasoning on the triage logic

The triage from 5000 → 468 → 33 → 7 is a three-stage geometry
filter. Each stage removes genes that satisfy fewer geometric
constraints:

1. **5000 → 468:** Many reversal genes have either a small
   expression gap (the gene does change direction but the absolute
   difference between normal and tumour is modest) or a small
   loading (the gene contributes little to the PC1 axis). Tier 1
   keeps only genes that are both strong movers and strong
   contributors.

2. **468 → 33:** Of the 468 high-quality reversal genes, only 33
   are in the top-200 PC1 correlates. The top-200 list (from Script
   3 S3) was derived by a completely different method — Pearson
   correlation with depth scores. Agreement between two independent
   geometric rankings is a convergence criterion, not a pre-selection.

3. **33 → 7:** The module genes in Script 3 S4 were identified by
   partial correlation independent of PC1 depth. A gene that appears
   in the partial-correlation module structure is independently
   co-regulated with its module partners after removing the global
   depth gradient. These 7 genes pass all three geometric filters
   simultaneously.

---

## S3 — Minimal Intervention Set (MIS)

### What was done
The Tier 1 set (n=468) was sorted by pc1_shift (most negative first)
and a cumulative shift curve was computed. MIS at 10/25/50/75/90%
of total Tier 1 shift was defined.

### Results

| Threshold | n_genes | cum_shift |
|---|---|---|
| 10% | 57 | −0.7112 |
| 25% | 137 | −1.5913 |
| 50% | 261 | −2.8157 |
| 75% | 372 | −3.8150 |
| 90% | 433 | −4.3258 |
| 100% (all Tier1) | 468 | −4.6106 |

**Total Tier 1 shift: −4.6106.**
The MIS@50% set (n=261) covers exactly half of the achievable
geometric reversal shift within Tier 1, using 261 genes.

### MIS@50% action breakdown
- **SUPPRESS** (positive loading, gene high in tumour): n=183 (70%)
- **RESTORE** (negative loading, gene high in normal, lost in tumour): n=78 (30%)

The 70/30 split reflects the asymmetry in the attractor: the tumour
state is primarily characterised by a large set of acquired genes
(gains) and a smaller set of lost genes (losses). Geometrically,
the gains are more numerous and contribute more per-gene shift because
their expression gap is larger (genes like RPL10: gap 0.902, AKR1C1:
gap 0.853) than the losses.

### The compression problem
The Script 3 gap/2 min_set contained 4933 genes — nearly the full
panel. That set was derived from the raw PC1 loading space without
any gap filter. The Tier 1 + MIS approach compresses this to 261
genes that cover 50% of the same geometric shift. The remaining 50%
is distributed across ~4700 genes each contributing a small shift.
This is the standard geometric structure of a dense loading vector:
the first few percent of genes cover a disproportionate fraction of
the variance, and the tail is long and flat.

The MIS@50% is not a therapeutic shortlist. It is the geometry's
answer to the question: *if you could only intervene in 261 of the
5000 positions, which 261 move the point furthest?*

---

## S4 — Module Score Validation

### What was done
Each of the 16 Script 3 modules was scored per sample by mean
z-scored expression of its constituent genes. Module scores were
correlated with depth and PC2. Scores were then residualised on
depth and re-correlated with PC2 to test depth-independence.
MW tests compared chRCC vs oncocytoma per module.

### Full results table

| Module | genes | r_depth | r_PC2 | r_PC2\|depth | chRCC | onco | normal | MW p(chRCC vs onco) |
|---|---|---|---|---|---|---|---|---|
| 1 | NFATC1, INO80C | +0.016 | −0.039 | −0.039 | +0.007 | +0.007 | −0.004 | 0.901 |
| 2 | INSM2, NSL1, ZKSCAN3, ZNF227, SNRPD1 | +0.346 | −0.269 | −0.287 | +0.076 | +0.075 | −0.043 | 0.901 |
| 3 | METTL6, C6orf52 | +0.737 | −0.362 | −0.535 | +0.737 | +0.959 | −0.480 | 0.561 |
| 4 | FEZ1, MESP1 | +0.358 | −0.196 | −0.210 | +0.256 | +0.320 | −0.163 | 1.000 |
| 5 | MAEL, CYP4F2, RAB3IL1, CTSV | −0.257 | +0.887 | **+0.918** | −0.324 | −0.235 | +0.158 | 0.507 |
| 6 | SLAMF1, SAFB2, KIAA0430 | −0.765 | +0.044 | +0.068 | −0.275 | −0.408 | +0.193 | 0.561 |
| 7 | LINC00599, SEMA6A, KRT83 | +0.537 | +0.638 | **+0.756** | +0.533 | +0.602 | −0.321 | 1.000 |
| 8 | FLYWCH1, C1RL-AS1 | +0.885 | −0.310 | **−0.666** | +1.126 | +1.125 | −0.637 | 0.836 |
| 9 | C4orf17, PRPF38B, ZNF326 | −0.118 | −0.182 | −0.183 | −0.165 | +0.067 | +0.028 | 0.407 |
| 10 | PLSCR1, GTF2B | +0.343 | −0.360 | **−0.384** | −0.003 | +0.775 | −0.219 | **0.042** |
| 11 | TMEM56, MAP3K8, SIN3A | −0.729 | −0.341 | **−0.498** | −0.300 | −1.440 | +0.492 | **0.0004** |
| 12 | GOLGA5, IL13RA1, UPRT, ATP11C, PHLPP1 | −0.522 | −0.098 | −0.115 | −0.093 | −0.875 | +0.274 | **0.018** |
| 13 | PRDM10, SWAP70 | −0.930 | −0.168 | **−0.457** | −1.340 | −1.073 | +0.683 | 0.229 |
| 14 | CCDC90B, AASDHPPT | −0.060 | +0.137 | +0.137 | −0.372 | +0.341 | +0.009 | **0.020** |
| 15 | TDRD7, NKAP | −0.880 | −0.104 | −0.220 | −1.046 | −1.192 | +0.634 | 0.507 |
| 16 | PTS, ENAH | +0.016 | −0.153 | −0.153 | +0.049 | +0.011 | −0.017 | 0.709 |

### Modules with strong depth-independent PC2 signal (|r_PC2\|depth| ≥ 0.30)

Seven modules retain substantial PC2 correlation after depth
residualisation. These modules carry information about the PC2 axis
that is not explained by where a sample sits on the PC1 depth gradient.

**Module 5 (MAEL, CYP4F2, RAB3IL1, CTSV): r_PC2\|depth = +0.918**

This is the dominant PC2 module. After removing depth, the module
score correlates at 0.918 with PC2. The score is *negatively*
correlated with depth (r_depth = −0.257), meaning this module is
actually *lower* in the deepest attractor samples. Normal samples have
the highest score (mean +0.158), chRCC the lowest (−0.324), oncocytoma
intermediate (−0.235). MW chRCC vs oncocytoma p=0.507 — the module
does not significantly distinguish the two tumour types at p<0.05
despite the numerical difference in means.

The strong r_PC2\|depth means Module 5 is a PC2 driver: it varies
along the PC2 axis independently of how deep a sample is in the
attractor. The partial correlation structure (Script 3 S4) showed
CYP4F2, RAB3IL1, and CTSV as one of the tightest clusters in the
entire partial-correlation network (r_partial +0.869, +0.868, +0.845).
This is a coherent, independently co-regulated unit with a clear
geometric signature.

**Module 7 (LINC00599, SEMA6A, KRT83): r_PC2\|depth = +0.756**

Second-strongest PC2 module. Score is higher in oncocytoma (+0.602)
than chRCC (+0.533) than normal (−0.321). MW p=1.0 — no significant
difference between chRCC and oncocytoma, but both tumour classes
are clearly elevated over normal. This module tracks with depth
(r_depth = +0.537) but retains substantial PC2 signal after depth
is removed.

**Module 8 (FLYWCH1, C1RL-AS1): r_PC2\|depth = −0.666**

Strong negative PC2 module. This module is the most depth-correlated
of all 16 (r_depth = +0.885) — it tracks depth almost perfectly.
Yet after removing depth, it retains r_PC2\|depth = −0.666. Both
chRCC and oncocytoma have identical scores (+1.126 vs +1.125), and
normal is −0.637. MW p=0.836. This module is a marker of the attractor
state generally, and its PC2 residual signal suggests it has an
additional depth-independent component aligned with the negative
PC2 direction.

**Module 3 (METTL6, C6orf52): r_PC2\|depth = −0.535**

Depth-correlated module (r_depth = +0.737) that retains strong
PC2 residual signal. Oncocytoma mean (+0.959) is higher than chRCC
(+0.737), with normal at −0.480. MW p=0.561.

**Module 11 (TMEM56, MAP3K8, SIN3A): r_PC2\|depth = −0.498, MW p=0.0004**

The most significant chRCC vs oncocytoma discriminant module.
chRCC mean = −0.300, oncocytoma mean = −1.440, normal mean = +0.492.
MW p=0.0004. This module is substantially more suppressed in
oncocytoma than in chRCC. After depth removal, r_PC2\|depth = −0.498,
confirming the chRCC/oncocytoma difference is not a depth artefact.
MAP3K8 (a kinase), SIN3A (a transcriptional co-repressor), and TMEM56
are independently co-regulated partners that sit closer to normal in
chRCC than in oncocytoma.

**Module 13 (PRDM10, SWAP70): r_PC2\|depth = −0.457**

Strongest depth correlation of any module (r_depth = −0.930).
This module is almost perfectly anti-correlated with depth — it
is highest in normal (+0.683) and lowest in chRCC (−1.340). After
depth removal, r_PC2\|depth = −0.457, indicating a residual PC2
component. MW chRCC vs oncocytoma p=0.229.

**Module 10 (PLSCR1, GTF2B): r_PC2\|depth = −0.384, MW p=0.042**

Significant chRCC vs oncocytoma contrast (p=0.042). chRCC mean =
−0.003, oncocytoma mean = +0.775. This module is near-zero in chRCC
but elevated in oncocytoma. After depth removal, the PC2 residual
signal (−0.384) remains. This module is a geometry-derived
oncocytoma-specific signal.

### Modules with no significant PC2 signal after depth removal

Modules 1, 2, 4, 6, 9, 12, 14, 15, 16 all have |r_PC2\|depth| < 0.30.
These modules are either depth-tracking only (their PC2 correlation
is fully explained by depth) or are noise at this sample size.

Module 12 (GOLGA5, IL13RA1, UPRT, ATP11C, PHLPP1) has MW p=0.018
for chRCC vs oncocytoma but |r_PC2\|depth| = 0.115, meaning the
chRCC/oncocytoma difference in this module is primarily a depth
effect rather than a genuine PC2 signal.

Module 14 (CCDC90B, AASDHPPT) has MW p=0.020 and nearly zero depth
and PC2 correlations, meaning the chRCC/oncocytoma difference is
not explained by either axis — it is a residual contrast that sits
off both major geometric axes.

---

## S5 — PC2 Subtype Depth Independence

### What was done
For each of the top 30 PC2-subtype genes (from Script 3 S5, the
PC2-high vs PC2-low chRCC comparison), three correlations were
computed across all 83 samples:
- r(gene, depth)
- r(gene, PC2)
- r(gene|depth, PC2) — Pearson correlation of residuals

### Verdict criteria
- **PC2-GENUINE:** |r_PC2\|depth| ≥ 0.40
- **DEPTH-CONFOUNDED:** |r_PC2\|depth| < 0.20
- **MIXED:** 0.20 ≤ |r_PC2\|depth| < 0.40

### Results

| Verdict | n | % |
|---|---|---|
| DEPTH-CONFOUNDED | 19 | 63% |
| MIXED | 8 | 27% |
| PC2-GENUINE | 3 | 10% |

Only 3 of 30 genes survive depth residualisation as PC2-genuine.

### The 3 PC2-genuine subtype genes

**TMEM52B: r_depth = −0.244, r_PC2 = +0.550, r_PC2\|depth = +0.567**

The depth correlation is weak (−0.244), and the PC2 correlation
(+0.550) is largely preserved after depth removal (+0.567). TMEM52B
is the most depth-independent PC2 gene in the subtype list. It sits
almost entirely on the PC2 axis. Its PC2 signal does not come from
being in a deeper or shallower attractor — it comes from the
chRCC/oncocytoma secondary axis directly.

**NOX4: r_depth = −0.623, r_PC2 = +0.397, r_PC2\|depth = +0.507**

Substantially depth-correlated (−0.623), meaning NOX4 is higher in
normal samples. Yet after removing depth, PC2 correlation improves
(+0.507 vs +0.397). The depth component of NOX4 expression is
confounded with its PC2 component, but the latter is real and
independent. NOX4 is a NADPH oxidase and is suppressed in the
attractor — the residual PC2 signal means it also varies along
the chRCC/oncocytoma axis independently.

**DDIT4L: r_depth = −0.714, r_PC2 = −0.380, r_PC2\|depth = −0.544**

Strong depth correlation (−0.714) but the PC2 residual is even
stronger (−0.544) than the raw PC2 correlation (−0.380). Depth
confounds the raw PC2 correlation downward here. After removing the
depth component, DDIT4L's alignment with the negative PC2 direction
(oncocytoma side) becomes clearer. DDIT4L is a stress-response gene
(DNA damage inducible transcript 4-like).

### What the 63% depth-confounded rate means

The Script 3 S5 analysis identified genes distinguishing PC2-high
from PC2-low chRCC (using only the 15 chRCC samples at median split).
Those 30 genes were identified within a depth-homogeneous group —
all chRCC samples have depth ≈ 0.93. Yet when tested across all 83
samples including normal and oncocytoma, most of those genes turn
out to be primarily depth-discriminating. This is a within-class
vs across-class confound: a gene that separates PC2-high from
PC2-low within the 15 chRCC samples may be doing so for reasons
that, in the full dataset, correlate more with depth than with PC2.

The 3 surviving genes (TMEM52B, NOX4, DDIT4L) are those for which
the PC2 signal genuinely exists across the full manifold independent
of depth.

---

## S6 — Cross-Axis Geometry

### MIS50 score on the manifold

All 261 MIS50 genes were found in the expression matrix.

| Class | MIS50_score mean | std |
|---|---|---|
| chRCC | +0.513 | 0.036 |
| oncocytoma | +0.516 | 0.034 |
| normal | −0.291 | 0.015 |

**r(MIS50_score, depth) = +0.9986**
**r(MIS50_score, PC2) = +0.018**

The MIS50 aggregate score is almost perfectly correlated with depth
(0.9986) and has essentially zero PC2 correlation (0.018). This is
expected and correct: the MIS was constructed from the PC1 loading
space, so it should be a near-perfect depth tracker. The near-zero
PC2 correlation confirms the MIS50 is not contaminated with PC2
structure — it is a pure PC1 reversal set.

The chRCC and oncocytoma MIS50 scores are indistinguishable (0.513
vs 0.516). This is a critical geometric observation: the MIS50 does
not differentiate chRCC from oncocytoma. Both tumour types are
equally deep in the attractor as measured by the PC1 reversal
signature. The difference between chRCC and oncocytoma is entirely
in the PC2 direction, not the PC1 depth direction.

### GMM tumour cluster depth

```
Cluster 2  n=21  depth=0.907  PC2_mean=−0.619  (chRCC=11, onco=10)
Cluster 3  n=9   depth=0.976  PC2_mean=+3.404  (chRCC=4,  onco=5)
```

Cluster 3 is both deeper and has a higher PC2 mean than Cluster 2.
The two attractor clusters differ on both axes. The depth difference
is significant (MW p<0.0001). Whether the PC2 difference is causal,
consequential, or coincidental cannot be determined from this
geometry alone.

---

## S7 — Biological Interpretation

*Constrained strictly by geometry. No prior knowledge.*

### What the attractor acquires (Tier 3 — the minimal coherent core)

All 7 Tier 3 genes are SUPPRESS targets. They are high in tumour
(T_mean 0.739–0.852), low in normal (N_mean 0.088–0.206), and
co-regulated with each other in modules that are independent of
the global depth gradient.

The gene names are noted here without interpretation of their prior
literature roles, because the geometry selected them by three
independent criteria simultaneously:
1. Large expression gap between tumour and normal states
2. High PC1 loading (they define the attractor direction)
3. Independent co-regulation within the partial-correlation module
   structure

**C4orf17** is in Module 9 (C4orf17, PRPF38B, ZNF326). This module
has a small negative depth correlation (−0.118) and weak PC2 signal.
The Tier 3 classification comes from geometric filter convergence,
not from module strength.

**AKR1E2** is in the top-200 attractor (r_depth = +0.9408, rank 20)
and in the module structure. The aldo-keto reductase family has
metabolic roles, but the geometric evidence for AKR1E2 as a priority
target is independent of that classification.

**ZNF574** is in the top-200 attractor (r_depth = +0.9594, rank 2)
and module-member. It ranks second in the full PC1 correlation
list — it is one of the most depth-correlated genes in the entire
panel.

**PAK3** and **MAP3K19** are kinases. The geometry identified them
independently through three filters. Their kinase classification is
noted as an observation from the gene name, not as a basis for their
selection.

### The PC1 vs PC2 geometry — a key structural finding

The cross-axis analysis reveals a clean geometric dissociation:

| Measurement | PC1 (depth) | PC2 |
|---|---|---|
| MIS50 score | r = +0.999 | r = +0.018 |
| chRCC vs oncocytoma depth | identical (0.513 vs 0.516) | diverges |
| Module 5 (MAEL cluster) | r_depth = −0.257 | r_PC2\|depth = +0.918 |
| Module 8 (FLYWCH1) | r_depth = +0.885 | r_PC2\|depth = −0.666 |
| Module 11 (SIN3A cluster) | r_depth = −0.729 | r_PC2\|depth = −0.498, MW p=0.0004 |

**PC1 (depth) is the attractor axis.** It captures the
normal-to-tumour transition and is shared by chRCC and oncocytoma
equally. The MIS50 reversal set lives entirely on this axis.

**PC2 is the within-attractor discrimination axis.** It carries
information about the chRCC/oncocytoma boundary, is represented by
at least 7 depth-independent modules, and has 3 depth-independent
gene-level markers (TMEM52B, NOX4, DDIT4L). Module 11 (TMEM56,
MAP3K8, SIN3A) is the strongest geometric discriminant between
chRCC and oncocytoma (MW p=0.0004) and retains PC2 signal after
depth removal.

### What this geometry does and does not show

**The geometry shows:**
- chRCC and oncocytoma share the same attractor depth (they are
  equally far from the normal basin on PC1)
- They are distinguished on PC2 by a set of independently
  co-regulated modules, most prominently Module 11 (SIN3A, MAP3K8,
  TMEM56)
- The Module 5 signature (MAEL, CYP4F2, RAB3IL1, CTSV) is the
  dominant driver of the PC2 axis (r_PC2\|depth = +0.918) but does
  not significantly separate chRCC from oncocytoma (p=0.507)
- The reversal vector compresses to 7 highest-priority targets when
  three independent geometric filters converge

**The geometry does not show:**
- Which of the 7 Tier 3 genes is causally upstream
- Whether suppressing them would collapse the attractor or merely
  shift a sample's position on PC1
- What happens to PC2 if PC1 is reversed
- Clinical correlates (the geometry has no outcome data)

---

## Summary table — Script 4 outputs

| Output file | Content |
|---|---|
| `gmm4_clusters.csv` | Per-sample GMM cluster (0–3), PC1, PC2, depth, class |
| `reversal_tier1.csv` | 468 genes: high gap + high loading |
| `reversal_tier2.csv` | 33 genes: Tier1 ∩ top200 |
| `reversal_tier3.csv` | 7 genes: Tier2 ∩ module — the minimal coherent core |
| `mis50.csv` | 261 genes: MIS at 50% of Tier1 total shift |
| `module_summary.csv` | 16 modules: r_depth, r_PC2, r_PC2\|depth, class means, MW p |
| `pc2_subtype_depth_independence.csv` | 30 genes: r_depth, r_PC2, r_PC2\|depth, verdict |
| `cross_axis_table.csv` | Per-sample: PC1, PC2, depth, MIS50 score, GMM cluster |
| `chrcc_script4_figure.pdf` | 9-panel figure |

---

## What Script 5 should address

The geometry has now produced:

1. A Tier 3 minimal coherent core (7 genes, all SUPPRESS, all in
   modules, all in the top-200 attractor set, all with large
   expression gaps)
2. A confirmed PC2 axis with depth-independent module and gene-level
   support
3. A Module 11 (SIN3A, MAP3K8, TMEM56) chRCC/oncocytoma discriminant
   at MW p=0.0004

**Open geometric questions for Script 5:**

1. **Module 11 structure:** What is the full correlation neighbourhood
   of SIN3A, MAP3K8, and TMEM56? Are there additional genes that
   co-vary with this module beyond the partial-correlation window?

2. **PC2 gene programme:** The PC2 positive pole (SLC51B, RDH5,
   HSD17B14, NECAB2, MAPT, PROZ, APOH, SLC22A8...) and negative
   pole (SULT2B1, OLFM1, ABCA4, NUP93, SH3GL3...) — what is the
   depth-independent subset of these? Only the full PC2 correlate
   list residualised on depth will answer this.

3. **Tier 3 module membership:** C4orf17, AKR1E2, C1orf94, ZNF574,
   PAK3, BTNL3, MAP3K19 are all in the partial-correlation module
   structure, but the module analysis used only 100 genes. What
   is the full neighbourhood of these 7 genes if the partial
   correlation is extended to the full Tier 2 (33 genes) or
   Tier 1 (468 genes)?

4. **TMEM52B, NOX4, DDIT4L — the 3 genuine PC2 genes:** What is
   their expression pattern across all 83 samples on a PC1 × PC2
   plot? Do they cluster spatially on the manifold?

5. **Attractor depth heterogeneity within chRCC:** GMM Cluster 3
   (depth = 0.976, n=9) is deeper than Cluster 2 (depth = 0.907,
   n=21). Within the 15 chRCC samples, is there a clinical or
   pathological correlate of this depth difference? (This requires
   survival or stage data if available.)

---

*End of Script 4 Reasoning Artifact*
*OrganismCore | Document 96d-R | 2026-03-02*
*Author: Eric Robert Lawson*
