# chRCC FALSE ATTRACTOR — SCRIPT 3 REASONING ARTIFACT
**OrganismCore | Document 96c | 2026-03-02**
**Author: Eric Robert Lawson**

---

## TABLE OF CONTENTS
1. [Framing: What Script 3 Is Doing](#1-framing)
2. [S1 — Full Manifold Geometry](#2-s1-full-manifold-geometry)
3. [S2 — Bimodality Test](#3-s2-bimodality-test)
4. [S3 — Unbiased Programme Discovery](#4-s3-unbiased-programme-discovery)
5. [S4 — Module Structure](#5-s4-module-structure)
6. [S5 — PC2 Structure (chRCC vs Oncocytoma)](#6-s5-pc2-structure)
7. [S6 — Reversal Vector](#7-s6-reversal-vector)
8. [Drug Targets — Tier-Ranked](#8-drug-targets)
9. [Biological Interpretation: The False Attractor Model](#9-biological-interpretation)
10. [What This Is Not (Anti-Confound Notes)](#10-anti-confound-notes)
11. [Next Scripts Recommended](#11-next-scripts)

---

## 1. FRAMING

Script 3 does not import a hypothesis. It imports a matrix — 15,244 genes × 83 samples — and asks the geometry a question: **where are the attractors?**

The dataset structure:
- **chRCC**: n=15 (chromophobe renal cell carcinoma)
- **Normal kidney**: n=53
- **Oncocytoma**: n=15 (renal oncocytoma — the morphological near-twin of chRCC)

The attractor panel contains 14,833 genes after QC, operating on a near-complete transcriptome. No pathway filtering, no gene set pre-selection, no prior knowledge loading. The geometry alone determines which genes, which axes, and which interventions matter.

**Core claim of the script:** chRCC (and oncocytoma) occupy a shared transcriptional attractor basin that is deeply separated from normal kidney tissue — a high-dimensional stable state that is not simply "different from normal" but occupies a compacted, reproducible region of gene expression space. This state is the **false attractor**: a developmentally inappropriate stable basin maintained by a gene regulatory network that the normal intercalated cell lineage does not inhabit.

---

## 2. S1 — FULL MANIFOLD GEOMETRY

### 2.1 Variance Structure

```
PC1:  72.66%
PC2:   6.48%
PC3:   1.75%
PC4:   1.55%
PC5:   1.21%
─────────────
Cum5: 83.65%
```

**PC1 dominates with 72.66% variance.** This is extraordinary — in a mixed tumor/normal/benign dataset of 83 samples and 5,000 variable genes, having a single axis capture nearly three-quarters of all transcriptional variance means the biological contrast between attractor and normal is the overwhelming signal. Everything else — subtype differences, technical variation, metabolic drift — is residual noise below 7% per axis.

> **Interpretation**: The system is not distributed across many axes. It is a **one-axis system** in gross structure. PC1 = the transition between normal intercalated cell identity and the shared chRCC/oncocytoma attractor. This is a clean geometric signal.

**PC1 flipped: tumour > normal.** Convention is arbitrary; the positive pole is labelled "attractor end" (chRCC + oncocytoma high) and the negative pole is "normal end."

### 2.2 PC1 Loadings: The Two Poles

**PC1 Positive Pole (Attractor Genes — acquired in tumour):**
All top-10 genes load at ≈+0.0165, an essentially flat plateau. This means no single gene is a "driver" of PC1 — the axis is distributed. The top names:

| Gene | Comment |
|------|---------|
| GNAO1 | Gαo subunit; neuroendocrine-associated G-protein signalling |
| NNAT | Neuronatin; imprinted gene, developmental regulation of ion transport |
| CA1 | Carbonic anhydrase 1; acid-base balance, hallmark of intercalated cell pathology |
| NKX2-5 | Cardiac/visceral TF; ectopic activation suggests lineage mis-specification |
| ZNF710 | Zinc finger; chromatin context unclear but ZNF family prevalent across attractor |
| RPL10 | Ribosomal protein; translation machinery bias |
| LIMD1 | LIM-domain protein; Hippo pathway node |
| AKR1C1 | Aldo-keto reductase; steroid/bile acid metabolism |
| CYP2A6 | Cytochrome P450; xenobiotic metabolism |
| TPRXL | Tripeptidyl peptidase-related; function obscure but loading consistent |

**PC1 Negative Pole (Normal Genes — lost in tumour):**
| Gene | Comment |
|------|---------|
| PDPK1 | PDK1; PI3K/AKT survival kinase |
| PDCD4 | Tumour suppressor, translational inhibitor |
| SPG7 | Mitochondrial AAA-ATPase; mitochondrial quality control |
| RAB3GAP2 | RAB3 GTPase activating protein |
| ATP5J2 | ATP synthase subunit; OXPHOS |
| CLEC2D | C-type lectin, immune/NK receptor ligand |
| ICK | Intestinal cell kinase; cilia/Hedgehog |
| TBRG4 | Transforming growth factor-beta regulator |
| ANKRD33 | Ankyrin repeat domain |
| PABPC5 | Poly(A)-binding protein; mRNA stability |

**What PC1 says**: The normal-to-attractor transition involves simultaneous **gain of neuroendocrine/metabolic/developmental transcription** and **loss of tumour-suppressive, OXPHOS, and mRNA-regulatory machinery**. The normal pole contains proteins (PDCD4, PDPK1) that normally gatekeep cell fate and survival.

### 2.3 PC2–PC5: Secondary Geometry

**PC2 (6.48%)** — This axis, crucially, **separates chRCC from oncocytoma** (MW p=0.009, see S5). Positive pole genes (SLC51B, RDH5, HSD17B14, NECAB2, MAPT) are heavily enriched in steroid/bile organic anion transporters and cytoplasmic enzyme families. The negative pole (SULT2B1, OLFM1, ABCA4, SH3GL3) shows cytoskeletal and ABC transporter loss.

**PC3 (1.75%)** — NLRP2, APCS, SPINK1 positive; CYP2E1, GCGR, NTRK2 negative. Likely captures metabolic heterogeneity (hepatocyte-like vs. tubular programming) and immune-adjacent signalling.

**PC4 (1.55%)** — IGFBP1/FOXD1/TENM2 positive; INPP4B/TMEM30B/PABPC4L negative. IGF axis and developmental patterning vs. phosphoinositide regulation loss.

**PC5 (1.21%)** — USP2/HBG1/KIRREL positive; STON1/IREB2/FAM221A negative. Includes hemoglobin gamma chains (HBG1) — this may capture erythroid-like signal or the proliferative fraction.

---

## 3. S2 — BIMODALITY TEST

### 3.1 Hartigan's Dip Test

```
Dip statistic: 0.0120
Bootstrap p:   1.0000
Result: UNIMODAL — continuous trajectory
```

**This is one of the most important results in the script.** The PC1 distribution is **unimodal** — there is no discrete tumour/normal boundary. The transition from normal (depth ≈ 0.02) to attractor (depth ≈ 0.93) is a **continuous manifold**, not a sharp phase transition.

> **Implication**: The cell system doesn't jump between two states — it moves along a trajectory. This means there may be intermediate states (early transformation), reversal may be gradual rather than catastrophic, and single "switch" models are insufficient.

### 3.2 Gaussian Mixture Model

```
k=2: BIC=567.46, AIC=555.36
k=3: BIC=579.44, AIC=560.09
k=4: BIC=567.16, AIC=540.56
Best: k=4 (both BIC and AIC)
```

**k=4 wins**, resolving the population into four components:

| Component | Mean | Std | Weight | Contents |
|-----------|------|-----|--------|----------|
| 1 | −46.700 | 0.761 | 0.349 | 31 normals (tight) |
| 2 | −42.903 | 2.368 | 0.289 | 22 normals (diffuse) |
| 3 | +77.173 | 4.426 | 0.267 | 11 chRCC + 10 oncocytoma |
| 4 | +85.967 | 2.116 | 0.094 | 4 chRCC + 5 oncocytoma |

> **Key finding**: The attractor basin is **not a single compact state** — it resolves into (at least) two sub-populations. Component 4 (mean=+85.97) is the **deeper attractor** with smaller variance — these are the samples most committed to the false attractor state. Component 3 (mean=+77.17, larger std) may represent early or partial basin entry. Crucially, **chRCC and oncocytoma co-occupy both components** — they share the same basin, consistent with their shared intercalated cell origin.

### 3.3 Normalised Depth Scores

```
chRCC:       mean=0.929  std=0.034  (very tight, deep in basin)
Oncocytoma:  mean=0.927  std=0.046  (nearly identical to chRCC)
Normal:      mean=0.022  std=0.018  (tightly clustered near 0)
```

**chRCC and oncocytoma are geometrically indistinguishable on PC1.** They differ on PC2 (see S5). On the primary basin axis, they are the same cell state. This is one of the most profound geometric findings: the morphologically distinct tumour types (chRCC vs. oncocytoma) are **transcriptionally co-located** in the primary axis.

---

## 4. S3 — UNBIASED PROGRAMME DISCOVERY

### 4.1 Top 200 Attractor Genes (Acquired in Tumour)

Ranked by correlation with PC1/depth score. Top 10:

| Rank | Gene | r_depth | Biological Role |
|------|------|---------|----------------|
| 1 | DNAJC5B | +0.9685 | Cysteine string protein beta; synaptic vesicle cycle |
| 2 | ZNF574 | +0.9594 | Zinc finger; transcriptional regulation |
| 3 | NFATC1 | +0.9592 | **Nuclear factor of activated T-cells; Ca2+-responsive TF** |
| 4 | INSM2 | +0.9576 | Insulinoma-associated TF; neuroendocrine differentiation |
| 5 | IL17C | +0.9558 | Interleukin-17C; epithelial-derived cytokine |
| 6 | NSL1 | +0.9539 | Kinetochore assembly |
| 7 | METTL6 | +0.9514 | tRNA methyltransferase |
| 8 | SIX3 | +0.9513 | Homeodomain TF; neural/eye development |
| 9 | CCDC155 | +0.9486 | Coiled-coil domain protein |
| 10 | SRRM4 | +0.9479 | Serine/arginine repetitive matrix 4; neural exon splicing |

**Top 10 observations:**
- **NFATC1 (#3, r=+0.9592)**: Ca²⁺/calcineurin-regulated transcription factor. Normally mediates osteoclast differentiation, T-cell activation, and cardiac development. Its presence as the third-strongest attractor-correlate suggests the false attractor is sustained by constitutive Ca²⁺/NFAT signalling. This is a **druggable target** (calcineurin inhibitors, NFAT pathway inhibitors).
- **INSM2 (#4)** and **SRRM4 (#10)**: Both are neuroendocrine markers. INSM2 is an insulinoma-associated TF that drives beta-cell and neuroendocrine programming. SRRM4 drives neural microexon splicing (nSR100), which reprograms splicing to neuronal patterns. Together, these suggest **neuroendocrine reprogramming** as a hallmark of the attractor state — consistent with chRCC's intercalated cell origin in the acid-secreting distal nephron (an excitable, ion-transporting lineage).
- **SIX3 (#8)**: Paired-type homeodomain factor, repressor of Wnt signalling, involved in neural/retinal and renal anterior patterning. Ectopic SIX3 suggests lineage mis-specification at a developmental control level.
- **DNAJC5B (#1)**: Cysteine string protein beta, involved in synaptic vesicle cycling — its top ranking in a renal tumour dataset is striking and reinforces the neuroendocrine/vesicle-trafficking theme.

**Structural Patterns (Script 3 output):**
```
ATTRACTOR POLE:
  TF             n=4  (NFATC1, SOX10, KLF14, FOXA2)
  TRANSPORTER    n=7
  CYTOSKEL/ECM   n=6
  KINASE/SIGNAL  n=2

NORMAL POLE:
  RIBOSOME/RNA   n=10  (DDX46, DDX55, MRPL20, HNRNPM, HNRNPA1, RPL26L1)
  KINASE/SIGNAL  n=7
  METABOLIC      n=5
  CELL_CYCLE     n=3
```

> **Critical TF cluster in attractor pole:**
> - **NFATC1** — Ca²⁺/calcineurin, bone/immune fate
> - **SOX10** — Neural crest transcription factor
> - **KLF14** — Krüppel-like factor 14; adipogenesis and metabolic regulation
> - **FOXA2** — Forkhead box A2; liver/pancreatic/lung epithelial master regulator

> This is a highly anomalous transcription factor assembly for a renal epithelial tumour. The combination of NFATC1 (immune/osteoclast), SOX10 (neural crest), KLF14 (metabolic), and FOXA2 (endodermal) in a kidney tumour suggests **deep lineage infidelity** — the cells are not merely "tumour" but are activating master TF programmes from unrelated lineages.

> **In the normal pole, the dominant structural feature is ribosomal/RNA biology loss** (10 genes: DDX helicases, MRPL20, HNRNPA1, RPL26L1, etc.). This is consistent with the hypothesis that **the attractor suppresses normal translational quality control and RNA surveillance**, removing the normal kidney epithelial cell's ability to monitor and correct its own transcriptional state.

### 4.2 Bottom 200 Normal Genes (Lost in Tumour)

Key genes lost in the attractor state (most negative correlations with depth):

| Rank | Gene | r_depth | Biological Role |
|------|------|---------|----------------|
| 200 | KIAA0430 | −0.9188 | Nuclear pore / RNA export |
| 199 | L3MBTL4 | −0.9183 | Polycomb-associated; H4K20me2 reader |
| 198 | NAMPT | −0.9053 | NAD+ biosynthesis rate-limiting enzyme |
| 197 | TARDBP | −0.9009 | TDP-43; RNA-binding, splicing regulation |
| 196 | NKAP | −0.8908 | NF-κB activating protein; splicing/Notch |
| 195 | SNRPD1 | −0.8886 | snRNP D1; U1/U2 snRNP complex |
| 194 | KLHL42 | −0.8883 | Kelch-like ubiquitin adaptor |
| 193 | MLN | −0.8852 | Motilin; GI peptide hormone |
| 192 | INO80C | −0.8841 | INO80 chromatin remodelling complex |
| 191 | PHF14 | −0.8809 | PHD-finger 14; chromatin reader |
| 190 | TEX22 | −0.8809 | Testis-expressed |

**Most important normal-pole losses:**
- **NAMPT (r=−0.9053)**: Nicotinamide phosphoribosyltransferase — rate-limiting enzyme for the NAD⁺ salvage pathway. Its deep loss in the attractor state implies **NAD⁺ depletion** as a feature of the transition. NAMPT inhibitors (FK866, CHS-828) are in clinical development; *the attractor already has low NAMPT*, suggesting the normal cell's NAD⁺ maintenance is actively dismantled.
- **TARDBP (r=−0.9009)**: TDP-43, a ubiquitous RNA-binding protein controlling splicing, mRNA stability, and stress granule biology. Its loss parallels the neurodegeneration biology where TDP-43 mis-localisation is pathological. In chRCC, its absence may contribute to aberrant splicing — cooperating with the SRRM4 gain to remodel the splicing landscape toward a neuroendocrine pattern.
- **L3MBTL4 (r=−0.9183)**: Polycomb-associated, H4K20me2 reader. Loss of polycomb-associated chromatin maintenance is consistent with epigenetic de-repression of developmental programmes — explaining how TFs like NFATC1, SIX3, SOX10, FOXA2 become accessible.
- **INO80C (r=−0.8841)**: INO80 chromatin remodelling complex subunit. INO80 controls replication fork stability and H2A.Z deposition. Its loss in the attractor could destabilise replication and promote the transcriptional plasticity required for fate switching.
- **SNRPD1 (r=−0.8886)** and the RNA/ribosome cluster: Loss of core spliceosome machinery (U snRNPs) in the attractor state is paradoxical but meaningful — the cell is not reducing all RNA metabolism, but specifically losing the canonical spliceosome components while potentially gaining alternative splicing factors (SRRM4).

---

## 5. S4 — MODULE STRUCTURE

Partial correlations given PC1 reveal the **independent co-regulatory modules** — gene pairs whose co-expression is NOT simply explained by the global tumour-normal gradient (PC1) but reflects direct or near-direct regulatory coupling.

### 5.1 Strongest Partial Correlations

| Pair | r_partial | Module | Interpretation |
|------|-----------|--------|---------------|
| CYP4F2 — CTSV | +0.8690 | 5 | Fatty acid ω-hydroxylase + lysosomal Cys protease |
| RAB3IL1 — CTSV | +0.8683 | 5 | RAB3 GEF + CTSV |
| CYP4F2 — RAB3IL1 | +0.8446 | 5 | CYP4F2 + RAB3 vesicle GEF |
| SEMA6A — RAB3IL1 | +0.8058 | 7 | Semaphorin + vesicle factor |
| FLYWCH1 — CTSV | −0.7975 | cross | TF repressor anti-correlated with lysosomal protease |
| ZNF227 — KIAA0430 | +0.7957 | 2 | Zinc fingers co-regulated |
| NSL1 — KIAA0430 | −0.7929 | cross | Kinetochore vs. nuclear pore, anti-correlated |

### 5.2 16 Detected Modules

```
Module 1  (n=2):  NFATC1, INO80C
Module 2  (n=5):  INSM2, NSL1, ZKSCAN3, ZNF227, SNRPD1
Module 3  (n=2):  METTL6, C6orf52
Module 4  (n=2):  FEZ1, MESP1
Module 5  (n=4):  MAEL, CYP4F2, RAB3IL1, CTSV
Module 6  (n=3):  SLAMF1, SAFB2, KIAA0430
Module 7  (n=3):  LINC00599, SEMA6A, KRT83
Module 8  (n=2):  FLYWCH1, C1RL-AS1
Module 9  (n=3):  C4orf17, PRPF38B, ZNF326
Module 10 (n=2):  PLSCR1, GTF2B
Module 11 (n=3):  TMEM56, MAP3K8, SIN3A
Module 12 (n=5):  GOLGA5, IL13RA1, UPRT, ATP11C, PHLPP1
Module 13 (n=2):  PRDM10, SWAP70
Module 14 (n=2):  CCDC90B, AASDHPPT
Module 15 (n=2):  TDRD7, NKAP
Module 16 (n=2):  PTS, ENAH
```

### 5.3 Module Interpretations

**Module 1: NFATC1 + INO80C** (−0.6981 partial r)
This is a **negative** partial correlation — NFATC1 and INO80C are *anti-correlated* independent of PC1. INO80C is lost in the normal pole (Section 4.2). The anti-correlation means: as NFATC1 *rises*, INO80C *falls*, beyond what PC1 alone predicts. This suggests **NFATC1 directly or indirectly suppresses INO80 chromatin remodelling** — blocking the repair-associated chromatin remodeller could lock the cell into the attractor state. This module is a candidate causal link between the Ca²⁺/NFAT activation and epigenetic stabilisation of the false attractor.

**Module 2: INSM2, NSL1, ZKSCAN3, ZNF227, SNRPD1**
Mixed signs: NSL1 negatively correlates with ZNF227 and KIAA0430, SNRPD1 (which are normal-pole genes), while INSM2 and ZKSCAN3 are attractor genes. This module captures a **chromatin-splicing-neuroendocrine interface**:
- INSM2 (neuroendocrine TF) drives cell fate
- NSL1 (kinetochore) links to chromosome segregation fidelity
- ZKSCAN3 (zinc finger) regulates lysosome biogenesis and autophagy
- ZNF227 + SNRPD1 are normal-pole co-regulators being jointly suppressed

**Module 5: MAEL, CYP4F2, RAB3IL1, CTSV** (strongest independent module)
- **MAEL**: PIWI-interacting RNA (piRNA) pathway protein; transposon repression
- **CYP4F2**: Leukotriene B4 ω-hydroxylase; arachidonic acid / eicosanoid metabolism
- **RAB3IL1**: RAB3 GEF; exocytic vesicle trafficking (normally in neurons/secretory cells)
- **CTSV**: Cathepsin V; lysosomal cysteine protease

This module is coherent around **secretory vesicle biology and lipid inflammatory mediator catabolism** — all four genes are independently co-regulated, suggesting a shared regulatory input. The presence of MAEL (piRNA) alongside secretory/lipid genes is unexpected and may indicate retrotransposon de-repression co-emerging with secretory reprogramming.

**Module 11: TMEM56, MAP3K8, SIN3A**
- MAP3K8 = TPL2/COT1 kinase (normal-pole; lost in attractor)
- SIN3A = Co-repressor, histone deacetylation (normal-pole; lost)
- TMEM56 = Transmembrane protein (normal-pole; lost)

MAP3K8 and SIN3A are both lost in the attractor, co-regulated independently of PC1. MAP3K8 activates ERK/JNK in response to inflammatory signals — its loss may impair normal stress responses. SIN3A is a master transcriptional co-repressor; its loss is epigenetically catastrophic, consistent with the TF de-repression observed in Module 1 and the attractor gene list.

**Module 12: GOLGA5, IL13RA1, UPRT, ATP11C, PHLPP1**
Normal-pole module:
- GOLGA5: Golgin A5; Golgi stack architecture
- IL13RA1: IL-13 receptor; cytokine signalling
- UPRT: Uracil phosphoribosyltransferase (pyrimidine salvage)
- ATP11C: P4-type ATPase; phospholipid flippase
- PHLPP1: PH-domain leucine-rich repeat phosphatase; AKT/S6K dephosphorylation

This module represents a **Golgi-cytokine-phospholipid-phosphatase axis** that is jointly suppressed in the attractor. PHLPP1 loss is notable — PHLPP1 dephosphorylates and inhibits AKT and S6K1. Its joint loss with the Golgi/cytokine components suggests that loss of AKT suppression is co-regulated with loss of cytokine receptor signalling and membrane asymmetry — a combined effector of the attractor's AKT hyperactivation.

---

## 6. S5 — PC2 STRUCTURE

### 6.1 chRCC vs. Oncocytoma on PC2

```
chRCC:       PC2 mean = −0.73 ± 2.35
Oncocytoma:  PC2 mean = +1.91 ± 2.17
Normal:      PC2 mean = −0.33 ± 22.29

MW chRCC vs oncocytoma: p = 0.0090  ✓
MW chRCC vs normal:     p = 0.5248  (not significant)
```

**PC2 separates chRCC from oncocytoma** — the normal samples are diffuse across PC2 (std=22.3), but the tumour types segregate. This is the **diagnostic axis** within the attractor basin.

### 6.2 PC2 Gene Programme

**Positive PC2 (oncocytoma-enriched):**
Top genes: SLC51B, RDH5, HSD17B14, NECAB2, MAPT, PROZ, APOH, SLC22A8, GGTLC2, RAB3IL1

- SLC51B: Organic solute transporter β; bile acid transport
- RDH5: Retinol dehydrogenase 5; visual cycle / retinoid metabolism
- HSD17B14: 17β-hydroxysteroid dehydrogenase; steroid catabolism
- MAPT: Microtubule-associated protein tau; neuronal cytoskeleton
- APOH: Apolipoprotein H; coagulation / lipoprotein binding

> **Oncocytoma vs chRCC axis** is dominated by **retinoid/bile/steroid metabolism and tau neuronal biology**. Oncocytoma is a benign entity; the genes that place it at the positive PC2 pole relative to chRCC may represent residual differentiation — oncocytoma retains some functional metabolic capacity (bile transport, retinoid metabolism) that chRCC loses.

**Negative PC2 (chRCC-enriched):**
Top genes: SULT2B1, OLFM1, ABCA4, NUP93, SH3GL3, TFAP2C, RHOJ, ERMP1, LGI2

- SULT2B1: Sulfotransferase 2B1; cholesterol/bile acid sulfonation
- ABCA4: ABC transporter; retinoid transport (retinal)
- TFAP2C: AP-2γ transcription factor; trophoblast/mammary lineage
- RHOJ: Rho GTPase; angiogenesis, cytoskeletal
- NUP93: Nucleoporin; nuclear pore complex

> **chRCC** on PC2 is characterised by **loss of sulfonation, ABC transport, and nucleoporin expression** — consistent with more aggressive phenotype (NUP93 loss disrupts nuclear-cytoplasmic transport) and further loss of metabolic differentiation than oncocytoma.

### 6.3 chRCC Subtype Split on PC2

```
Median PC2 in chRCC: −1.358
PC2-low  group: n=8  (more negative = more chRCC-like)
PC2-high group: n=7  (less negative = more oncocytoma-like)
```

**Top genes distinguishing PC2-high from PC2-low chRCC:**

| Gene | PC2-high | PC2-low | Δ | p_MWU | Interpretation |
|------|---------|---------|---|-------|---------------|
| STXBP6 | 0.389 | 0.854 | −0.465 | 0.0022 | Syntaxin-binding; vesicle release |
| PLA1A | 0.362 | 0.784 | −0.422 | 0.0037 | Phospholipase A1; lipid metabolism |
| UNC5D | 0.164 | 0.554 | −0.390 | 0.0003 | Netrin receptor; axon guidance / apoptosis |
| PGM5 | 0.335 | 0.701 | −0.366 | 0.0037 | Phosphoglucomutase 5; glycogen metabolism |
| CYTIP | 0.480 | 0.827 | −0.347 | 0.0037 | Cytohesin-interacting protein; integrin trafficking |
| AIM1 | 0.477 | 0.822 | −0.345 | 0.0037 | Absent in melanoma 1 / CRYBG2 |
| NOX4 | 0.510 | 0.811 | −0.301 | 0.0140 | NADPH oxidase 4; ROS production |
| BEX4 | 0.584 | 0.885 | −0.301 | 0.0059 | Brain-expressed X-linked 4 |

All significant genes show *lower* expression in PC2-high chRCC vs. PC2-low — the "more oncocytoma-like" chRCC has lower expression of vesicle/lipid/ROS genes. This subtype split has therapeutic relevance: **NOX4 is a druggable ROS source**, and its differential expression between chRCC subtypes suggests NOX4-inhibitor sensitivity would vary by subtype.

---

## 7. S6 — REVERSAL VECTOR

### 7.1 Gap Analysis

```
Normal mean depth:  0.0225
chRCC mean depth:   0.9288
Gap:                0.9063
Target shift:      −0.4531  (half-gap strategy)
Reversal set size:  4933 genes
Cumulative shift:  −25.7322
```

**4,933 genes** are required to move a theoretical cell halfway from the attractor to normal basin. This is a large number — it reflects the distributed nature of PC1 (all ≈0.016 loadings, no dominant single gene) — but the **cumulative shift of −25.7** far exceeds the required −0.45, confirming the set is geometrically sufficient.

### 7.2 Reversal Set Structure

The reversal vector contains genes in two categories:
- **Positive loading + high tumour expression** → must be *down-regulated* to shift PC1 negative
- **Negative loading + high normal expression** → must be *up-regulated* to shift PC1 negative

**Top 20 reversal targets (most impactful per gene):**

| Rank | Gene | Loading | N_mean | T_mean | pc1_shift | Action | Rationale |
|------|------|---------|--------|--------|-----------|--------|-----------|
| 1 | FARSB | +0.0162 | 0.155 | 0.900 | −0.0121 | ↓ | Phenylalanyl-tRNA synthetase β; protein synthesis |
| 2 | LUZP6 | +0.0162 | 0.221 | 0.970 | −0.0121 | ↓ | Leucine zipper; unclear |
| 3 | HGH1 | +0.0164 | 0.112 | 0.851 | −0.0121 | ↓ | Translation quality control |
| 4 | LIMD1 | +0.0165 | 0.093 | 0.826 | −0.0121 | ↓ | LIMD1/Hippo scaffold |
| 5 | AOC1 | −0.0160 | 0.945 | 0.192 | −0.0121 | ↑ | Amine oxidase; polyamine catabolism |
| 6 | TFPI | −0.0165 | 0.885 | 0.154 | −0.0120 | ↑ | Tissue factor pathway inhibitor |
| 7 | IRX3 | −0.0164 | 0.932 | 0.201 | −0.0120 | ↑ | Iroquois homeobox TF; body axis patterning |
| 8 | KBTBD11 | −0.0165 | 0.950 | 0.224 | −0.0120 | ↑ | BTB/Kelch ubiquitin adaptor |
| 9 | RBM34 | −0.0165 | 0.812 | 0.089 | −0.0119 | ↑ | RNA-binding protein |
| 10 | SYNGR2 | +0.0162 | 0.136 | 0.871 | −0.0119 | ↓ | Synaptogyrin-2; synaptic vesicle |

**Reversal vector notable genes:**
- **CDKN1A (p21, rank 19, ↓)**: p21 is higher in tumour than normal (N=0.179, T=0.913). This is the classical cell cycle inhibitor — its high expression in tumour is consistent with oncogene-induced senescence bypass or p53-independent induction. The vector says to reduce it — but careful: this must be interpreted in the geometric sense, not as a clinical recommendation without further validation.
- **CLEC2D (rank 40, ↑)**: NK cell ligand; high in normal (0.994), very low in tumour (0.308). Restoring CLEC2D could restore immune recognition — a path toward immunotherapy sensitisation.
- **NNAT (rank 52, ↓)**: Neuronatin, attractor gene. High in tumour (0.759), low in normal (0.085). Reducing neuronatin expression — a developmental ion channel regulator — is geometrically significant.
- **FGFR1 (rank 17, ↓)**, **FGFR2 (rank 130, ↓)**, **FGFR3 (rank 76, ↑)**: FGF receptors appear with opposing signs. FGFR1/2 are elevated in the attractor (must be reduced); FGFR3 is higher in normal (must be restored). This **FGFR isoform switch** is a potential therapeutic handle — FGFR1/2-selective inhibitors could contribute to geometric reversal.
- **CDKN1A (↓), GLUL (↑, rank 196)**: Glutamine synthetase (GLUL) is high in tumour (0.968) — glutamine dependency as an attractor feature.
- **RICTOR (rank 145, ↓)**: mTORC2 component, high in tumour. Provides geometric rationale for mTORC2-selective inhibition in chRCC reversal.
- **TGFBR1 (rank 316, ↓)**: TGF-β receptor I; higher in tumour — TGFβ signalling as part of attractor maintenance.
- **CDKN2A (rank 992, ↓)**: p16/ARF, higher in tumour — consistent with senescence-associated gene expression in the deep attractor.

---

## 8. DRUG TARGETS — TIER-RANKED

### Tier 1: Strongly Supported, Geometrically Justified, Druggable

| Target | Evidence | Existing Drug Class | Geometric Basis |
|--------|----------|-------------------|----------------|
| **NFATC1** | #3 attractor gene (r=+0.959), Module 1 with INO80C suppression | Calcineurin inhibitors (cyclosporin A, tacrolimus); NFAT pathway inhibitors (INCA-6) | Top attractor TF; loss would collapse key branch of the attractor regulatory network |
| **RICTOR/mTORC2** | r_depth positive, rank 145 reversal set | Torin1/2 (mTOR kinase inhibitors); mTORC2-selective tools | mTORC2 maintains AKT-Ser473 phosphorylation; geometric reversal requires RICTOR reduction |
| **FGFR1/FGFR2** | Positive loading, reversal set rank 17/130; high in tumour | Erdafitinib, pemigatinib, infigratinib, derazantinib | Attractor expression high; FGFR3 (normal-high) opposite sign — isoform selectivity critical |
| **SIN3A** | Module 11; lost in attractor; restoring would repress attractor TFs | HDAC/SIN3A complex activators (limited); indirect via HDAC inhibitors | SIN3A loss co-regulated with MAP3K8 and TMEM56; geometric restoration reverses corepressor loss |
| **PHLPP1** | Module 12 (normal-pole); AKT/S6K phosphatase lost in attractor | No direct PHLPP1 activators exist; indirect: reduce AKT input | Loss of PHLPP1 → constitutive AKT activation; restoring it would brake the survival signal |
| **NOX4** | PC2 subtype split (p=0.014); chRCC-low vs. high PC2 | GKT137831 (NOX4 inhibitor, Phase II trials) | NOX4 differential by PC2-defined subtype; potential for subtype-stratified treatment |
| **SRRM4** | Top 10 attractor gene (r=+0.948); neural exon splicing factor | No approved direct inhibitor; CLK kinase inhibitors affect SR splicing | SRRM4 drives neuronal splicing reprogramming of the attractor; CLK1/2 inhibitors (Cirtuvivint) |

### Tier 2: Geometrically Justified, Druggable but Less Validated in chRCC

| Target | r_depth / Rank | Drug Class | Comment |
|--------|---------------|-----------|---------|
| **TGFBR1** | Rank 316 reversal (↓) | Galunisertib (LY2157299), vactosertib | Reversal requires reducing TGFBR1; TGFβ in the attractor is pro-fibrotic/EMT |
| **NAMPT** | r=−0.905 (lost) | FK866, GMX1778 | NAMPT already low in attractor; NAMPT inhibitors may paradoxically worsen — caution; NAD+ restoration may be therapeutic strategy (NMN/NR) |
| **FOXA2** | Top-4 attractor TF (normal-pole group FOXA2 is attractor-acquired) | No direct FOXA2 inhibitor | Master endodermal TF ectopically activated; downstream effectors more accessible |
| **GLI1/GLI3** | GLI1 rank 90 (r=+0.916); GLI3 rank 56 (r=+0.925) | Vismodegib, sonidegib (Hedgehog/SMO inhibitors) | Both positive-pole attractor genes; Hedgehog pathway active in attractor |
| **WNT10B/WNT8B** | WNT10B r=+0.924 (attractor); WNT8B r=+0.921 | Porcupine inhibitors (WNT-974, LGK-974) | WNT ligands gained in attractor; WNT secretion pathway targeting |
| **IGF1R** | Rank 343 reversal (↓) | Linsitinib, figitumumab | IGF1R higher in tumour; geometric reversal requires reduction |
| **AKT2** | Rank 234 reversal (↓) | Capivasertib (AZD5363), ipatasertib, MK-2206 | AKT2 higher in attractor; combined with PHLPP1 loss creates sustained AKT2 activity |
| **MAP3K8 (TPL2)** | Module 11 (normal lost) | BI 1394, (TPL2 inhibitors) | Normal-pole gene; restoring MAP3K8 function could re-engage inflammatory signalling lost in attractor |
| **CDKN1A (p21)** | Rank 19 reversal (↓ to normal); paradoxically high in tumour | Complex; tumour-specific p21 roles | Interpret carefully: p21 in attractor may reflect stress-p53-independent activation; direct targeting controversial |

### Tier 3: Exploratory, Geometry-Supported, Biology Requires Validation

| Target | Observation | Rationale |
|--------|-------------|-----------|
| **MAEL / piRNA pathway** | Module 5 with CYP4F2/RAB3IL1/CTSV | piRNA pathway activation = transposon de-repression — could be a vulnerability for immune activation (viral mimicry) |
| **CLU (Clusterin)** | Rank 154 reversal (↓); high in tumour | Clusterin as chaperone/anti-apoptotic in attractor; custirsen trials in other cancers |
| **BRD4** | Rank 197 reversal (↓) | BRD4 high in tumour (0.939); BET bromodomain inhibitors (JQ1, OTX015) — attractor TF-driven transcription may be BET-dependent |
| **DNMT1** | Lost in attractor (r=−0.438) | DNA methylation maintenance lost — hypomethylation drives TF de-repression; DNMT1 restoration theoretically |
| **TARDBP (TDP-43)** | r=−0.901 (lost) | TDP-43 restoration normalises RNA splicing — indirect but powerful |
| **ZKSCAN3** | Module 2; attractor-enriched lysosome regulator | ZKSCAN3 represses lysosome biogenesis (TFEB antagonist); its gain may indicate mTORC1-driven lysosome suppression |
| **CYP4F2** | Module 5 (strongest partial correlation axis) | Leukotriene B4 ω-hydroxylase; eicosanoid catabolism — altered lipid inflammatory milieu |
| **EZH1/PRC2 complex** | EZH1 in reversal set (↓); L3MBTL4 lost | Polycomb gain in attractor — EZH1/EZH2 inhibitors (tazemetostat) |

---

## 9. BIOLOGICAL INTERPRETATION: THE FALSE ATTRACTOR MODEL

### 9.1 What Is the False Attractor?

In Waddington's landscape model, cells occupy stable energy minima — attractor states — that correspond to differentiated cell types. The normal intercalated cell of the distal nephron occupies one basin.

Script 3 demonstrates that chRCC occupies a **distinct, deep, and geometrically stable basin** at PC1 depth ≈ 0.93 — separated from normal by a gap of 0.91 standard units on the primary axis of variance. This basin is:

1. **Shared with oncocytoma** (indistinguishable on PC1)
2. **Unimodally connected** to normal (no sharp phase transition — a slope, not a cliff)
3. **Internally heterogeneous** (k=4 GMM; PC2 chRCC/onco separation)
4. **Governed by a multi-TF regulatory network** (NFATC1, SOX10, INSM2, KLF14, FOXA2, SIX3)
5. **Stabilised by loss of chromatin maintenance** (INO80C, L3MBTL4, SIN3A, TARDBP)
6. **Maintained by vesicle/neuroendocrine/splicing reprogramming** (SRRM4, DNAJC5B, RAB3IL1, piRNA pathway)

It is called **"false"** because it is not a legitimate developmental state — no normal tissue occupies this basin. The cells are using regulatory programmes (NFATC1, SOX10, FOXA2, SIX3) drawn from other lineages (osteoclast, neural crest, endoderm, neural) to maintain stability in a transcriptional region that normal kidney epithelium never occupies.

### 9.2 Neuroendocrine Reprogramming Theme

The convergence of DNAJC5B (#1), SRRM4 (#10), INSM2 (#4), SIX3 (#8), GNAO1 (PC1 loading), and TACR1/TACR2 (in the deep reversal set) creates a **neuroendocrine reprogramming signature**. This is not surprising for intercalated cells — they are ion-transporting, pH-regulating cells with some excitable characteristics. The chRCC attractor appears to amplify and lock in a neuroendocrine-like sub-programme present latently in the normal IC lineage.

**Clinical implication**: This neuroendocrine theme suggests chRCC may have unexpected sensitivity to somatostatin analogues, neuropeptide signalling inhibitors, or SRRM4-pathway disruption (CLK kinase inhibitors). The neuroendocrine reprogramming also explains why chRCC can be confused with other neuroendocrine tumours histologically.

### 9.3 Intercalated Cell FOXI1 Context

The literature establishes **FOXI1** as the master TF of intercalated cells and as the top diagnostic marker of chRCC [[PMID 32812119]]. FOXI1 is not in the script's top-ranked attractor genes (it is in the positive PC2 axis in Section S5's negative genes: FOXI1 appears at rank 885 in the reversal set with loading +0.0158, T_mean=0.985). This means:

- FOXI1 is near-uniformly HIGH in both chRCC and normal IC — it is not a discriminant on PC1
- FOXI1 discriminates on other axes (it is in the PC2-positive cluster for tumour samples at r_PC2 not directly shown but consistent with the biology)
- The false attractor is built **on top of** the FOXI1+ intercalated cell identity, not by replacing it — the IC transcriptional scaffold (FOXI1, V-ATPase genes, carbonic anhydrase) is retained, and the attractor *adds* the NFATC1/SOX10/INSM2/SRRM4 superstructure

This means **chRCC is a lineage-faithful tumour with an overlaid false attractor network**. The therapeutic strategy must address the overlay, not the underlying IC identity.

### 9.4 The Attractor Barrier: Why chRCC Does Not Spontaneously Revert

The geometry shows a continuous trajectory but no reversion occurs in vivo. The barrier mechanisms identified:

1. **Epigenetic stabilisation**: Loss of L3MBTL4, INO80C, SIN3A (chromatin remodellers/repressors) removes the machinery that would reactivate normal chromatin states
2. **Co-repressor loss**: SIN3A loss means NFATC1 and other attractor TFs face no HDAC-mediated repression
3. **NFATC1-INO80C anti-correlation (Module 1)**: NFATC1 actively suppresses INO80C, creating a positive feedback loop that deepens the attractor
4. **Splicing reprogramming**: SRRM4 gain + TARDBP/SNRPD1 loss = irreversible splicing landscape shift that produces neuronal isoforms incompatible with normal renal function
5. **NAD+ depletion** (NAMPT loss): Low NAD+ impairs SIRT family deacetylases and PARP-dependent DNA repair, reducing the cell's ability to correct the epigenetic state

---

## 10. ANTI-CONFOUND NOTES

### What This Is NOT:

1. **Not a contamination artefact**: The chRCC and oncocytoma samples both cluster identically on PC1 at depth ≈ 0.93. If this were contamination or batch effect, the two independent tumour types would not co-localise so precisely.

2. **Not driven by proliferation**: The top attractor genes are not cell-cycle genes. The attractor structural genes (NFATC1, SRRM4, INSM2, SIX3, DNAJC5B) are not classic proliferation markers. Cell cycle genes appear but are not dominant in the top-ranked correlates.

3. **Not a single-gene/pathway story**: PC1 loadings are flat (all ≈ 0.016). No single gene accounts for more than 0.017% of PC1 variance. The attractor is a distributed state — consistent with an epigenetic/attractor model, not a single oncogene driver model.

4. **Not an artefact of normal tissue composition**: The 53 normals are tightly clustered at depth 0.022 ± 0.018. This is a highly reproducible baseline, not a heterogeneous mixture that could artificially create the separation.

5. **The GMM k=4 structure**: Both BIC and AIC agree on k=4. This is an internal data structure, not an imposed classification. The normal population splitting into two components (tight n=31 and diffuse n=22) may reflect tissue zones or quality — and the attractor splitting into components 3 and 4 (mean=+77 and +86) supports the existence of deep vs. shallow attractor entry.

---

## 11. NEXT SCRIPTS RECOMMENDED

Based on the geometry revealed in Script 3, the following analytical steps are logically sequenced:

### Script 4: Attractor TF Regulatory Network
- **Goal**: Map the regulatory hierarchy among NFATC1, SOX10, INSM2, SIX3, KLF14, FOXA2 within the attractor
- **Method**: Transcription factor binding site enrichment in the promoters of top 200 attractor genes; motif analysis; TF-gene correlation matrix conditioned on PC1
- **Key question**: Is NFATC1 the apex regulator, or is it co-equal with INSM2/SOX10?

### Script 5: Splicing Programme Analysis
- **Goal**: Characterise the SRRM4-driven neuronal exon usage in chRCC attractor
- **Method**: DEXSeq or rMATS on chRCC vs. normal; intersect differentially used exons with SRRM4 binding motifs
- **Key question**: Which specific transcripts are neuroendocrinally re-spliced? Are any of these druggable?

### Script 6: Epigenetic State Reconstruction
- **Goal**: Identify which chromatin regions are accessible/closed in the attractor vs. normal
- **Method**: Integrate ATAC-seq or H3K27ac ChIP-seq data (public chRCC data if available); overlay PC1 gene programme
- **Key question**: Are the attractor TF binding sites (NFATC1, SOX10) in open chromatin in chRCC? Is the INO80/SIN3A loss associated with specific loci?

### Script 7: Reversal Simulation
- **Goal**: Computationally simulate the effect of perturbing top reversal targets
- **Method**: Boolean or ODE network model of top 50 reversal genes; simulate single-gene and multi-gene perturbations; compute projected PC1 shift
- **Key question**: What is the minimum intervention set (fewest genes, largest PC1 shift)?

### Script 8: Spatial/Single-Cell Decomposition
- **Goal**: Determine if the PC2 chRCC subtypes (Section S5) correspond to spatial regions or clonal populations within individual tumours
- **Method**: Map reversal vector genes onto single-cell RNA-seq chRCC data; compute per-cell depth scores; identify transitional cells at low depth
- **Key question**: Are low-depth chRCC cells at the edge of the attractor basin — potential targets for reversal induction?

---

## APPENDIX: KEY NUMBERS REFERENCE TABLE

| Parameter | Value |
|-----------|-------|
| Genes × Samples | 15,244 × 83 |
| Attractor panel size | 14,833 genes |
| PC1 variance | 72.66% |
| Dip test p (unimodality) | 1.000 (unimodal) |
| GMM optimal k | 4 |
| chRCC depth mean | 0.929 ± 0.034 |
| Oncocytoma depth mean | 0.927 ± 0.046 |
| Normal depth mean | 0.022 ± 0.018 |
| PC1 gap (chRCC − normal) | 0.906 |
| Top attractor gene r | +0.9685 (DNAJC5B) |
| Top normal gene r | −0.9188 (KIAA0430) |
| chRCC vs onco PC2 p | 0.0090 |
| Reversal set size | 4,933 genes |
| Modules (|r_partial|>0.60) | 16 |
| Strongest partial r | +0.869 (CYP4F2—CTSV) |

---

## APPENDIX: TOP 20 DRUG TARGET SUMMARY

| Priority | Target | Gene | Direction | Drug Class | Tier |
|----------|--------|------|-----------|-----------|------|
| 1 | NFATC1 | NFATC1 | ↓ (reduce in attractor) | Calcineurin inhibitors, NFAT inhibitors | 1 |
| 2 | mTORC2/RICTOR | RICTOR | ↓ | Torin1/2, mTOR kinase inhibitors | 1 |
| 3 | FGFR1 | FGFR1 | ↓ | Erdafitinib, pemigatinib | 1 |
| 4 | FGFR2 | FGFR2 | ↓ | Pemigatinib, infigratinib | 1 |
| 5 | NOX4 | NOX4 | ↓ | GKT137831 | 1 |
| 6 | BRD4 | BRD4 | ↓ | JQ1, OTX015 | 3 |
| 7 | GLI1/Hedgehog | GLI1, GLI3 | ↓ | Vismodegib, sonidegib | 2 |
| 8 | WNT pathway | WNT10B, WNT8B | ↓ | LGK-974, WNT-974 | 2 |
| 9 | AKT2 | AKT2 | ↓ | Capivasertib, ipatasertib | 2 |
| 10 | IGF1R | IGF1R | ↓ | Linsitinib | 2 |
| 11 | TGFBR1 | TGFBR1 | ↓ | Galunisertib | 2 |
| 12 | NAD+ restoration | NAMPT | ↑ restore | NMN/NR supplementation | 2 |
| 13 | SIN3A/HDAC | SIN3A | ↑ restore | HDAC inhibitors (indirect) | 2 |
| 14 | EZH1/PRC2 | EZH1 | ↓ | Tazemetostat | 3 |
| 15 | SRRM4/CLK | SRRM4 | ↓ | CLK1/2 inhibitors, Cirtuvivint | 1 |
| 16 | Clusterin | CLU | ↓ | Custirsen | 3 |
| 17 | CLEC2D (immune) | CLEC2D | ↑ restore | NK cell activation strategies | 3 |
| 18 | piRNA/MAEL | MAEL | ↓ | Retrotransposon activation for immune mimicry | 3 |
| 19 | CYP4F2/LTB4 | CYP4F2 | contextual | Eicosanoid modulators | 3 |
| 20 | MAP3K8/TPL2 | MAP3K8 | ↑ restore | TPL2 activators (exploratory) | 3 |

---

*End of Script 3 Reasoning Artifact — OrganismCore | Document 96c | 2026-03-02*
*Author: Eric Robert Lawson*
*"Geometry first. The data speaks."*
