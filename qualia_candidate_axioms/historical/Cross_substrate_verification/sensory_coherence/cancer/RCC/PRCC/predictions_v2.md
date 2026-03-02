Yes — but before writing Script 2, the predictions need to be locked. This is the protocol invariant: predictions before script.

---

## Script 2 Predictions — Locked 2026-03-02
### Before Script 2 is written

---

### What Script 1 established (the foundation Script 2 builds on)

```
PRIMARY ATTRACTOR AXIS:
  Positive pole: KRT19 r=+0.803 / KRT7 r=+0.643 / ERBB2 r=+0.556
  Negative pole: SLC22A6 r=-0.801 / FABP1 r=-0.671 / SLC5A2 r=-0.661

ATTRACTOR TYPE: Biliary-papillary cytokeratin identity
  NOT EMT. NOT Warburg glycolysis. NOT HIF-driven.
  A lateral lineage switch from renal PT identity
  to biliary-ductal epithelial identity.

THREE CONFIRMED STABILISERS:
  1. EZH2 + TCA-chromatin coupling (FH/OGDHL/SUCLG1 → αKG → EZH2)
  2. PBRM1 loss + KDM1A elevation (dual chromatin lock)
  3. CDKN2A/CDK4 paradox (oncogenic stress bypass)

KEY UNEXPECTED SIGNALS REQUIRING INVESTIGATION:
  ERBB2 at rank 8 — not predicted, needs circuit mapping
  MET → MKI67 BROKEN — MET drives identity not mitosis
  TWIST1 DOWN vs normal but Q4-enriched — within-tumour EMT?
  VHL→CA9 BROKEN — CA9 up via unknown mechanism
  PD-L1/TIM-3 both fall with depth — immune exclusion
```

---

### S2-P1 — ERBB2 is an identity component, not a proliferative driver

```
PREDICTION:
  r(ERBB2, KRT19) > 0.50
  r(ERBB2, KRT7)  > 0.40
  r(ERBB2, MKI67) < 0.25
  r(ERBB2, MET)   > 0.30

REASONING:
  ERBB2 was the third strongest depth correlate
  (r=+0.556) and was not predicted.
  ERBB2 + KRT19 + KRT7 is the canonical biliary
  ductal co-expression signature (cholangiocarcinoma,
  gallbladder, pancreatic ductal epithelium).
  If ERBB2 is part of the biliary identity circuit,
  it must co-vary with KRT19/KRT7 and NOT with MKI67.
  If r(ERBB2, MKI67) is high, ERBB2 is proliferative.
  If r(ERBB2, MKI67) is low and r(ERBB2, KRT19) is high,
  ERBB2 is identity — same logic as MET.
  Drug implication changes depending on outcome:
    Identity ERBB2 → target for identity disruption
    Proliferative ERBB2 → target for anti-mitotic effect
```

---

### S2-P2 — Two separable depth sub-axes exist

```
PREDICTION:
  Axis A (biliary identity):
    Anchor: KRT19 (positive) / SLC22A6 (negative)
    Additional: KRT7, ERBB2, ITGA3, SOX4
  
  Axis B (TCA-metabolic collapse):
    Anchor: FABP1 (negative) / EZH2 (positive)
    Additional: OGDHL, SUCLG1, FH, GOT1, ACADM
  
  r(Axis_A, Axis_B) < 0.80
  (They are related but separable — same
  direction but different biological content)

REASONING:
  ccRCC had separable metabolic and ECM sub-axes
  (Script 3, S3-P1).
  PRCC likely has:
    Sub-axis A: the identity switch
               (epithelial type transition)
    Sub-axis B: the metabolic collapse
               (TCA/FAO programme loss)
  Both move with depth but may capture
  different patient populations at intermediate
  depths. If separable:
    Type 1 may be primarily Axis A (identity switch,
    MET-driven, less metabolic collapse)
    Type 2 may be primarily Axis B + A combined
    (deeper metabolic lock + identity switch)
```

---

### S2-P3 — FH is a continuous depth stratifier

```
PREDICTION:
  r(FH, depth_s2) < -0.45
  FH-low quartile will have deeper mean depth
  than FH-high quartile (MW p < 0.05)

REASONING:
  FH had r=-0.451 in Script 1 depth correlations.
  FH mutation is the driver of the CIMP subtype.
  But FH EXPRESSION (not just mutation) may
  continuously stratify PRCC depth across
  the full population.
  If FH expression is a continuous sensor of
  the TCA-chromatin axis, then FH-low tumours
  (regardless of mutation status) will be deeper
  because the αKG production failure is graded.
  This would mean FH RNA level alone (without
  mutation data) is a depth biomarker.
  Clinical use: FH IHC as a stratifier for
  αKG + EZH2i combination eligibility.
```

---

### S2-P4 — PBRM1 loss releases biliary identity genes

```
PREDICTION:
  r(PBRM1, KRT19) < -0.20
  r(PBRM1, KRT7)  < -0.15
  r(PBRM1, depth) < -0.20
  Lower PBRM1 = higher biliary cytokeratin expression

REASONING:
  PBRM1 is a SWI/SNF ATPase (SMARCA-class).
  SWI/SNF complexes keep chromatin OPEN.
  Paradox: PBRM1 is a tumour suppressor in RCC —
  its loss should relax chromatin.
  But the PT identity genes (SLC22A6, FABP1) are
  ALSO suppressed when PBRM1 is lost.
  Resolution: PBRM1 maintains PT identity by
  keeping PT enhancers open.
  When PBRM1 is lost, PT enhancers close
  (EZH2 fills the vacuum) AND the biliary
  programme is derepressed (KRT19/KRT7
  enhancers open via alternative mechanism).
  If r(PBRM1, KRT19) is negative, PBRM1 loss
  is directly enabling the biliary switch.
  This would make PBRM1 mutation the INITIATING
  event for the PRCC identity conversion —
  before EZH2 and KDM1A accumulate.
```

---

### S2-P5 — Type 1 / Type 2 depth stratification

```
PREDICTION:
  Using cBioPortal or TCGA paper annotation:
  Type 2 mean depth > Type 1 mean depth
  MW p < 0.05
  
  MET-proxy stratification (if formal annotation
  unavailable):
  MET-high quartile (proxy Type 1):
    Higher MET, lower depth than MET-normal
  CDKN2A-high / FH-low (proxy Type 2/CIMP):
    Higher depth score

REASONING:
  S1-P1 was deferred because TCGA Xena matrix
  does not carry Type 1/Type 2 annotation.
  Two resolution strategies for Script 2:
  1. Fetch annotation from cBioPortal
     (paper_Histologic.type column in some versions)
     or from TCGA KIRP paper supplement Table S1
  2. Use known molecular proxies:
     Type 1 = MET-amplified/high
     Type 2 = CDKN2A-silenced (INVERTED in our data —
     CDKN2A is UP, meaning oncogenic stress is expressed)
     CIMP = FH-mutation/low expression
  The depth distribution std=0.170 suggests
  bimodal or heterogeneous population consistent
  with two subtypes mixed.
```

---

### S2-P6 — 3-gene clinical panel

```
PREDICTION:
  Best panel will include KRT19 (rank 1 positive)
  and SLC22A6 or FABP1 (rank 1/2 negative)
  r(best_panel, depth) > 0.85
  
  Most likely best panel:
    KRT19 / SLC22A6 / ERBB2
    or KRT19 / FABP1 / EZH2
    or KRT19 / SLC22A6 / FH

REASONING:
  The framework has found r > 0.85 3-gene panels
  in every validated cancer to date.
  KRT19 is rank 1 positive (r=+0.803) —
  it must be in the panel.
  SLC22A6 is rank 2 negative (r=-0.801) —
  it pairs with KRT19 as the two poles.
  The third gene adds orthogonal variance.
  ERBB2 (r=+0.556, identity axis) or
  FH (r=-0.451, TCA axis) or
  EZH2 (r not calculated explicitly but Q4/Q1=1.109)
  are the candidates for the third position.
  Clinical deployability: KRT19 and ERBB2
  already have FDA-approved IHC assays.
  SLC22A6 has research-grade IHC.
  This is the most deployable panel if confirmed.
```

---

### S2-P7 — Immune architecture: exclusion not checkpoint

```
PREDICTION:
  Q4 vs Q1:
    CD8A will be LOWER in Q4 (immune excluded)
    FOXP3 will be HIGHER in Q4 (Treg dominant)
    CD274 (PD-L1) will be LOWER in Q4
    HAVCR2 (TIM-3) will be LOWER in Q4
    B2M will be LOWER in Q4 (antigen presentation lost)

  r(depth, CD8A)  < -0.20
  r(depth, B2M)   < -0.15
  r(depth, IL2RA) > +0.20

REASONING:
  Script 1 showed:
    CD274 Q4/Q1=0.795 (down with depth)
    HAVCR2 r=-0.396 (down with depth)
    IL2RA Q4/Q1=1.193 (up with depth)
    IFI16→B2M weakly connected (not BROKEN as in ccRCC)
  The pattern points to immune EXCLUSION
  in deep PRCC, not immune checkpoint blockade.
  Checkpoint inhibitors (anti-PD-L1, anti-TIM-3)
  target cells that are present but exhausted.
  In deep PRCC, the relevant cells are
  EXCLUDED — not exhausted.
  Anti-Treg therapy (anti-CD25/IL2RA) is
  more relevant in Q4 than anti-PD-L1.
  Script 2 should formally compute depth
  correlations for immune gene panel to
  confirm exclusion architecture.
```

---

### S2-P8 — CA9 elevation mechanism

```
PREDICTION:
  r(CA9, EPAS1)  < 0.20 (VHL→CA9 BROKEN confirmed)
  r(CA9, HIF1A)  > 0.20 (HIF1A drives CA9 in PRCC)
  or
  r(CA9, depth)  > +0.25 (CA9 is a weak depth marker)
  CA9 is NOT driven by VHL — it may be driven
  by HIF1A or by microenvironmental hypoxia

REASONING:
  VHL→CA9 is BROKEN (r=-0.098).
  CA9 is UP in saddle (FC=+3.622 p=1.11e-11).
  CA9 is Q4-enriched (Q4/Q1=1.167, borderline p=0.068).
  CA9 without VHL drive means an alternative
  mechanism is responsible.
  HIF1A is flat vs normal but present —
  HIF1A can drive CA9 at tumour-normal oxygen levels.
  CA9 may reflect papillary folding architecture
  creating micro-hypoxic pockets regardless of
  EPAS1 status.
  This matters for girentuximab (anti-CA9 antibody)
  which is approved in ccRCC:
  CA9-positive PRCC may respond to girentuximab
  even though the mechanism of CA9 elevation
  differs from ccRCC.
```

---

### Script 2 Objectives — Locked

```
SCRIPT 2 OBJECTIVES — 2026-03-02

OBJ-1: Sub-axis separation
        Axis A (biliary identity) vs Axis B (TCA)
        r(A, B) < 0.80?

OBJ-2: ERBB2 identity circuit
        r(ERBB2, KRT19), r(ERBB2, MKI67)
        Confirm: identity not proliferative

OBJ-3: FH as continuous depth stratifier
        r(FH, depth_s2)
        FH-low quartile depth comparison

OBJ-4: PBRM1 → biliary circuit
        r(PBRM1, KRT19), r(PBRM1, KRT7)

OBJ-5: Type 1/Type 2 stratification
        Fetch annotation from cBioPortal or proxy

OBJ-6: 3-gene clinical panel
        Exhaustive 3-gene search from top-15
        candidates, r > 0.85 target

OBJ-7: Immune architecture confirmation
        Depth correlations for CD8A, B2M,
        FOXP3, IL2RA, CD274, HAVCR2

OBJ-8: Drug target depth map
        Q1/Q2/Q3/Q4 gene expression for
        all 6 drug targets

OBJ-9: S1-S2 depth concordance
        r(S1_depth, S2_depth)
        Are both axes capturing same biology?

OBJ-10: TWIST1 within-tumour EMT axis
         Separate from biliary axis?
         r(TWIST1, KRT19), r(TWIST1, VIM)
```

---

Predictions locked. Ready to write Script 2 now — go?
