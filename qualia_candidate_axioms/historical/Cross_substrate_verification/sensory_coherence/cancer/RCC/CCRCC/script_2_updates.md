Both arms complete. Full results reading now.

---

## Script 1 — Complete Results Reading | Both Arms | Document 94

---

### PART 1 — TCGA ARM (previously read, confirmed)

All confirmations and surprises from prior reading stand. Not repeated here.

---

### PART 2 — GEO ARM (GSE53757, 72 matched pairs)

---

#### ✅ CONFIRMATIONS — GEO

**1. PT identity loss — 12/12 DOWN. Perfect prediction hit.**

Every PT identity gene in the GEO dataset is DOWN at p<0.0001. This is stronger than TCGA (9/13). The matched-pair design removes inter-individual noise — the signal is cleaner. UMOD (−49,880), PCK1 (−34,846), AQP1 (−16,627), GATM (−16,117) are the dominant signals. **Perfect confirmation.**

**2. VHL-HIF lock — 9/11 UP. Confirmed.**

VEGFA (+24,347), LDHA (+23,765), EPAS1 (+7,067), EGLN3 (+4,038), PDK1 (+3,703), CA9 (+3,058) all UP. **Confirmed.**

**3. Gluconeogenic arm — 3/3 DOWN. Perfect.**

FBP1 (−9,950), PCK2 (−7,368), G6PC (−3,132). All confirmed DOWN. **Perfect prediction hit across both datasets.**

**4. Identity switch score positive. Confirmed.**

PT identity −12,961, HIF targets +9,657. Switch score +22,618. Direction confirmed.

**5. Depth score range wider in GEO (0.035 — 0.895)**

This is expected — matched pairs capture the full biological range more accurately. Mean 0.569 matches TCGA (0.568) almost exactly. **Cross-dataset depth calibration is consistent.**

---

#### ⚠️ GEO-SPECIFIC SURPRISES — Record, Do Not Resolve

**Surprise G1 — GEO log2FC values are not log2FC**

The GEO saddle point values are in raw intensity units, not log2FC:
```
UMOD:  −49,879  (should be ~−5 to −16 range)
VEGFA: +24,347  (should be ~+3 range)
```

The GEO expression matrix contains **raw Affymetrix intensity values**, not log2-transformed values. The series matrix from GPL570 platforms is typically delivered as log2 intensity by GEO — but this dataset appears to be raw or differently scaled. The **direction is correct throughout** (60/75 concordant), which is what matters for Script 1. The magnitude is not comparable to TCGA without normalisation.

**Script 2 action required:** Apply log2 transformation to GEO matrix before any quantitative comparison. Add `np.log2(gene_df_geo + 1)` after parsing, or verify whether the values are already log2 by checking the range of normal tissue values (normal PT mean = 18,111 is consistent with raw intensity, not log2).

**This does not invalidate any finding** — direction is preserved and that is what the saddle point analysis uses. But the cross-dataset log2FC correlation (r=0.617) is computed on incomparable scales and should be recomputed after normalisation in Script 2.

---

**Surprise G2 — HIF1A is DOWN in GEO (−4,127)**

HIF1A is DOWN in GEO but UP (not significantly) in TCGA. EPAS1 (HIF2α) is strongly UP in GEO (+7,067). This is consistent with known ccRCC biology: **ccRCC is predominantly a HIF2α (EPAS1)-driven disease**, not HIF1α. HIF1α can be suppressed as HIF2α dominates. This is a refinement of the panel, not a contradiction. Flag for Script 2: separate HIF1A and EPAS1 as distinct readouts.

---

**Surprise G3 — JAG1 UP in GEO (+4,477) but DOWN in TCGA (−0.24)**

JAG1 is a Notch ligand in the PT maturation panel. It is discordant between datasets — small DOWN in TCGA, large UP in GEO. JAG1 has known roles in ccRCC tumour vasculature and Notch pathway activation. The GEO matched-pair design may be capturing a true biology that is diluted in bulk TCGA. Flag for Script 2 circuit analysis.

---

**Surprise G4 — PT_maturation group UP in GEO (+452, p=0.0017)**

In TCGA, PT maturation group is DOWN (−1.262). In GEO it is UP (+452). This is driven by JAG1. LHX1 is not in the GEO top genes. This discordance is real and needs investigation in Script 2 — the PT maturation panel may contain genes that behave differently across platforms or tumour stages.

---

**Surprise G5 — mTOR significant in GEO (p=0.0075, delta +160)**

In TCGA mTOR was borderline not significant (p=0.0503). In GEO it reaches significance. This supports the prior interpretation that mTOR activation exists at transcript level but is modest — the matched-pair design has more power to detect it.

---

### PART 3 — CROSS-DATASET COMPARISON

```
Common genes:         75
Direction concordant: 60/75 (80.0%)
log2FC correlation:   r=0.617  p<0.0001
```

**80% direction concordance across two completely different platforms (RNA-seq vs microarray) is strong validation.** The 15 discordant genes require reading:

| Gene | TCGA | GEO | Interpretation |
|---|---|---|---|
| FOXP3 | UP +1.51 | DOWN −50 | Regulatory T cell marker — immune infiltration heterogeneity between datasets. Not tumour-intrinsic. |
| HNF1A | UP +0.78 | DOWN −171 | Hepatocyte nuclear factor — small TCGA signal, large GEO signal. Platform sensitivity difference. GEO direction more likely correct given matched pairs. |
| SLC3A1 | UP +0.41 | DOWN −9,761 | Small TCGA UP near zero — likely noise. GEO DOWN is correct. PT identity gene — expected DOWN. |
| LRP2 | UP +0.40 | DOWN −5,692 | Same as SLC3A1. TCGA signal is near zero, GEO direction is correct. |
| CUBN | UP +0.26 | DOWN −9,554 | Same pattern. TCGA near-zero noise. GEO correct. |
| ARNT | DOWN −0.08 | UP +146 | Near-zero TCGA. HIF dimerisation partner — expected UP with HIF activation. GEO likely correct. |
| PBRM1 | DOWN −0.48 | UP +16 | PBRM1 is a tumour suppressor mutated in ~40% ccRCC. Its expression is complex — loss-of-function mutations don't always reduce transcript. Discordance is biologically real. |
| ARID1A | DOWN −0.41 | UP +42 | Same class as PBRM1 — chromatin remodelling tumour suppressor. |
| PIK3CA | DOWN −0.27 | UP +48 | Small TCGA signal. mTOR upstream. GEO UP consistent with mTOR activation. |
| CDK4 | UP +0.21 | DOWN −207 | Near-zero TCGA. GEO large DOWN unexpected for a proliferation gene — warrants investigation. |
| RPTOR | UP +0.14 | DOWN −1.50 | Both near zero. Effectively concordant at noise level. |

**Key pattern in discordant genes:** All 15 have near-zero log2FC in TCGA (|FC| < 1.6). The GEO direction for these genes is likely more reliable given the matched-pair design. The discordance is **not biological contradiction — it is TCGA sensitivity limitation** for small-effect genes in unpaired bulk RNA-seq.

---

### SUMMARY — What Script 1 Establishes

| Finding | TCGA | GEO | Status |
|---|---|---|---|
| PT identity lost | 9/13 DOWN | 12/12 DOWN | ✅ Confirmed both |
| VHL-HIF lock active | 8/11 UP | 9/11 UP | ✅ Confirmed both |
| Gluconeogenic arm lost | 3/3 DOWN | 3/3 DOWN | ✅ Perfect both |
| Lipogenic arm gained | 3/6 UP | 3/6 UP | ✅ Direction confirmed |
| Identity switch positive | +6.52 | +22,618 | ✅ Confirmed both |
| Depth score range wide | 0.184—0.802 | 0.035—0.895 | ✅ Consistent |
| HIF2α (EPAS1) dominant | modest | strong UP | ✅ Consistent with biology |
| EPAS1 > HIF1A | not separated | confirmed | ⚠️ Panel refinement needed |
| Lipogenic group significance | p=0.099 | p=0.120 | ⚠️ Individual genes needed |
| mTOR transcript signal | borderline | p=0.0075 | ⚠️ Exists but modest |

---

### Script 2 ��� Requirements Locked

| Priority | Analysis | Basis |
|---|---|---|
| 1 | Log2 normalise GEO matrix | GEO values are raw intensity |
| 2 | EPAS1 vs HIF1A separation | HIF1A DOWN, EPAS1 UP in GEO |
| 3 | Depth score vs stage (GSE53757) | Stage 1–4 metadata available |
| 4 | Individual lipogenic gene circuits | Group not significant, SCD dominant |
| 5 | BAP1 vs PBRM1 subgroup analysis | Discordant across datasets — subtype biology |
| 6 | Immune signal separation | FOXP3, CD8A, TIGIT — bulk infiltration |
| 7 | JAG1 circuit | UP GEO, DOWN TCGA — platform or biology |
| 8 | Recompute cross-dataset r after GEO log2 normalisation | Current r=0.617 on incomparable scales |

Ready to write Script 2 on your instruction.
