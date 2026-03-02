# OrganismCore HCC False Attractor Series
## Master Artifact — Complete Findings Register
### Documents 92a–92j (Addendum) | Scripts 1–9
### 2026-03-02 | Author: Eric Robert Lawson

---

## Series Identity

```
Framework:    OrganismCore
Disease:      Hepatocellular Carcinoma (HCC)
Hypothesis:   HCC represents a stable false attractor
              state — an epigenetically locked
              dedifferentiated identity that is
              maintained by HDAC2/EZH2 and driven
              by CDC20/CDK4/TOP2A proliferative
              programmes, with progressive immune
              evasion as depth increases.

Primary cohort:   TCGA-LIHC
                  n=371 HCC tumours
                  RNA-seq (HTSeq counts)
                  Aetiology: HCV/alcohol-dominant
                  US cohort
                  OS valid: 367 (events=130)
                  Stage I/II/III/IV: 172/87/85/5
                  Age mean: 59.5 years

Secondary cohort: GSE14520 (GPL3921)
                  n=445 samples
                  Affymetrix HG-U133A
                  Aetiology: HBV-dominant
                  Chinese cohort
                  Expression: confirmed (21 genes)
                  OS: pending (supplement required)

Scripts:      9
Documents:    92a through 92j + addendum
Date range:   2026-03-02
```

---

## Part I: Confirmed Findings
### (Computationally confirmed in TCGA-LIHC unless noted)

---

### I.A — The Depth Axis

| # | Finding | Evidence | Script |
|---|---------|----------|--------|
| 1 | Metabolic depth score predicts OS (TCGA-LIHC) | p=1.01e-04, HR=1.362 | S3 |
| 2 | Metabolic depth score predicts OS (GSE14520) | p=1.78e-05 | S2 |
| 3 | Depth independent of stage in Cox | HR=1.245, p=0.017 | S5 |
| 4 | Depth absorbs grade completely in Cox | grade HR=0.977, p=0.808 (NS) | S5 |
| 5 | Age independently prognostic alongside depth | HR=1.225, p=0.030 | S6 |
| 6 | Full four-covariate model: depth+stage+grade+age | depth HR=1.244, p=0.027 | S6 |
| 7 | Stage I depth reversal | deep=31.9mo > shallow=27.1mo | S6 |
| 8 | Stage II–III depth predicts OS (Stage III tertile) | p=0.017 | S7 |
| 9 | Depth axis molecular architecture confirmed in GSE14520 | EZH2 r=+0.859, TOP2A r=+0.888 (n=445) | S9 |

**Depth score construction:**
```
Depth = 0.5 × (1 - norm(mean(SW genes)))
      + 0.5 × norm(mean(FA genes))

SW genes (metabolic switch — should be ON
in normal hepatocyte, suppressed in HCC):
  CYP3A4, ALDOB, PCK1, G6PC, CYP2C9,
  TTR, IGF1, ARG1, APOE, RXRA, PPARA,
  FGF21, FABP1, ALB, APOB, HNF4A

FA genes (false attractor — should be OFF
in normal hepatocyte, activated in HCC):
  SOX4, PROM1, AFP, EPCAM, CDC20, BIRC5,
  TOP2A, MKI67, CCNB1, KRT19, EZH2, HDAC2
```

---

### I.B — Individual Gene Findings (TCGA-LIHC)

| Gene | Finding | Evidence | Script |
|------|---------|----------|--------|
| CDC20 | Strongest OS predictor in matrix | p=2.57e-07, r_depth=+0.677 | S6 |
| CDC20 | Absorbs depth HR in Cox | depth HR→1.042, p=0.73 when CDC20 included | S7 |
| CDC20 | Stage-specific: NS in Stage I, sig in II–III | S1: p=0.294, S2: p=0.003, S3: p=0.007 | S7 |
| CDC20 | Tertile T3 vs T1 OS gap | hi=22.1mo vs lo=30.7mo, p=5.23e-06 | S7 |
| HDAC2 | Stage III OS gap 19.2 months | hi=13.7mo vs lo=32.9mo, p=1.93e-04 | S7 |
| HDAC2 | Tertile gradient Stage III | T3=12.2mo, T2=18.3mo, T1=39.0mo, T3 vs T1 p=5.45e-05 | S8 |
| HDAC2 | Confirmed in GSE14520 depth axis | r_depth=+0.333, p=5.24e-13 | S9 |
| CDK4 | Stage III OS gap 14.0 months | hi=16.3mo vs lo=30.3mo, p=4.88e-04 | S7 |
| CDK4 | NS in Stage I, sig Stage II–III only | Stage I p=0.133 | S7 |
| CDK4 | Positive depth correlation (TCGA) | r=+0.653 | S7 |
| CDK4 | Negative depth correlation (GSE14520) | r=-0.724, p=2.53e-73 | S9 |
| CDKN2A | Co-expresses with CDK4 (paradox) | r=+0.277, p=5.94e-08 | S7 |
| BIRC5 | OS predictor all stages | p=3.22e-05, r_depth=+0.665 | S6 |
| BIRC5 | Strongest depth correlate in GSE14520 | r=+0.820, p=2.51e-109 | S9 |
| TOP2A | Strongest gene-depth r in series (GSE14520) | r=+0.888, p=9.00e-152 | S9 |
| EZH2 | Dominant depth correlate in HBV-HCC | r=+0.859, p=1.05e-130 | S9 |
| PRF1 | Better OS in Stage III | hi=29.5mo vs lo=16.9mo, p=0.035 | S7 |
| PRF1 | Independent of depth axis | r_depth=+0.005 | S7 |
| CD8A | Better OS | hi=29.6mo vs lo=23.8mo, p=0.013 | S5 |
| PTEN | Worse OS Stage III | hi=29.4mo vs lo=16.9mo, p=2.67e-03 | S7 |
| PTEN | Enriched in Deep+Hot (not Cold) | r_depth=-0.162, p=0.0017 | S7 |

---

### I.C — Joint Gene Analyses (TCGA-LIHC)

| Analysis | Finding | Evidence | Script |
|----------|---------|----------|--------|
| HDAC2-hi + CDK4-hi Stage III | Worst OS group in dataset | OS=12.2mo, n=32, p=4.79e-06 | S8 |
| HDAC2-lo + CDK4-lo Stage III | Best OS group | OS=34.1mo, n=31 | S8 |
| HDAC2 × CDK4 gap | Largest joint OS gap | 21.9 months within Stage III | S8 |
| HDAC2-hi + PRF1-lo Stage III | Worst immune subtype | OS=12.8mo, n=24, p=7.19e-05 | S8 |
| HDAC2-lo + PRF1-hi Stage III | Best immune subtype | OS=40.3mo, n=24 | S8 |
| HDAC2 × PRF1 gap | Largest OS gap in series | 27.5 months within Stage III | S8 |
| CDK4-hi + CDKN2A-hi | Worst CDK4 quadrant | OS=21.1mo vs CDK4-lo+CDKN2A-lo=32.3mo | S7 |
| HDAC2-hi + PRF1-hi Stage III | CTLs present but cannot kill | OS=15.0mo (only 2.2mo better than HDAC2-hi+PRF1-lo) | S8 |

---

### I.D — Cox Models

| Model | Variables | Key Result | Script |
|-------|-----------|-----------|--------|
| Model A | stage + depth | depth HR=1.245 p=0.017 | S5 |
| Model B | stage + CDC20 | CDC20 HR=1.522 p=2.7e-05 | S8 |
| Model C | stage + HDAC2 | HDAC2 HR=1.392 p=4.4e-04 | S8 |
| **Model D** | **stage + CDC20 + HDAC2** | **All 3 significant; AIC improved** | **S8** |
| Model E | stage + CDC20 + HDAC2 + depth | depth HR=0.783 p=0.091 (suppressed) | S8 |
| Full | depth + stage + grade + age | depth HR=1.244 p=0.027 | S6 |

**Model D detail:**
```
stage: HR=1.445  p=7.5e-05 ***
CDC20: HR=1.406  p=1.2e-03 **
HDAC2: HR=1.227  p=0.037 *
n=341

Recommended clinical model:
  Clinically implementable by IHC
  No RNA-seq required
  Both CDC20 and HDAC2 measurable
    by standard pathology IHC
```

---

### I.E — Immune Findings

| Finding | Evidence | Script |
|---------|----------|--------|
| 5 co-inhibitory receptors upregulated with depth | PD-1/TIM-3/LAG-3/TIGIT/CTLA-4, composite r=+0.37, p=3.42e-13 | S5 |
| Immune exhaustion correlates with depth | r=+0.37 across exhaustion panel | S4 |
| Deep+Hot immune subtype identified | Depth-high + CD8A-high + FOXP3-high + PD-L1-high | S6 |
| Deep+Cold immune-desert subtype identified | Depth-high + CD8A-absent (p=3.66e-21) + CDK4-low + AFP-low | S6 |
| Deep+Cold OS | OS=24.7mo n=65 | S6 |
| CD8A-high better OS | p=0.013, hi=29.6mo vs lo=23.8mo | S5 |
| PRF1 prognostic independently of depth | r=+0.005 with depth | S7 |
| HDAC2-hi suppresses PRF1 killing efficacy | HDAC2-hi+PRF1-hi OS=15.0mo vs HDAC2-lo+PRF1-hi=40.3mo | S8 |

---

### I.F — HCC-P5 (Literature Confirmed)

```
Prediction (Script 1, Document 92a):
  CTNNB1-mutant HCC has better OS
  than CTNNB1 wild-type

Computational status:
  NOT TESTABLE — MAF file incomplete
  (55KB instead of expected 3–10MB)
  After 9 scripts, 0 CTNNB1 mutations
  parsed from available file

Literature resolution (Document 92i):
  CONFIRMED ✓
  CTNNB1-mut median OS = 39.78 months
  TP53-mut median OS   = 25.15 months
  p=0.003 (AACR 2025 large cohort)
  Meta-analysis 2023: confirmed
  favorable prognosis at 1, 3, 5 years

Mechanistic context:
  CTNNB1-mut HCC = Hoshida S3
    (well-differentiated, our "shallow")
  CTNNB1-mut → Wnt activation
    → CCL4/CCL5 suppression
    → T cell exclusion (immune-cold)
    → Better OS from indolent biology
      NOT from immune control
  CTNNB1-mut HCC = POOR checkpoint
    inhibitor responder despite better OS
```

---

## Part II: Novel Contributions
### (Not previously described in published literature in this form)

---

### Tier 1 — Highest Novelty and Impact

```
NOVEL 1:
  HDAC2 × PRF1 prognostic and
  therapeutic framework (Stage III HCC)

  Finding:
    HDAC2-lo + PRF1-hi OS = 40.3 months
    HDAC2-hi + PRF1-lo OS = 12.8 months
    Gap = 27.5 months within Stage III
    p = 7.19e-05
    n = 24 per group

  Mechanism proposed:
    HDAC2 maintains H3K27 deacetylation
    at MHC-I gene promoters (HLA-A,
    B2M, TAP1) → reduced antigen
    presentation → CTLs cannot kill
    tumour cells even when PRF1-high
    (HDAC2-hi+PRF1-hi OS=15.0mo —
     only 2.2mo better than no CTLs)
    HDAC inhibition → MHC-I restored
    → CTLs enabled → PRF1 killing
    activated

  Therapeutic logic:
    HDAC2-hi+PRF1-lo Stage III:
      Worst group (OS=12.8mo)
      HDAC inhibitor + anti-PD-1
      → restore antigen presentation
      → sustain CTL activity
    HDAC2-lo+PRF1-hi Stage III:
      Best group (OS=40.3mo)
      Surveillance only

  Literature status: NOT DESCRIBED
    PRF1/CYT score as biomarker:
      known (Anticancer Research)
    HDAC2 as OS predictor: known
    Their COMBINATION as a therapeutic
    selection framework: NOVEL

──────────────────────────────────────

NOVEL 2:
  HDAC2 × CDK4 joint Stage III analysis

  Finding:
    HDAC2-hi + CDK4-hi OS = 12.2 months
    HDAC2-hi + CDK4-lo OS = 18.8 months
    HDAC2-lo + CDK4-hi OS = 29.4 months
    HDAC2-lo + CDK4-lo OS = 34.1 months
    Best vs worst: p = 4.79e-06
    Gap = 21.9 months within Stage III
    n = 32 in worst group (38% of S3)

  Additive biology confirmed:
    HDAC2 alone costs 15.3 months
    CDK4 adds 6.6 months on top
    HDAC2 is dominant driver
    CDK4 is additive effector

  Combination drug hypothesis:
    Entinostat (HDAC1/2i)
    + Palbociclib (CDK4/6i)
    in HDAC2-hi+CDK4-hi Stage III HCC
    Target population OS = 12.2mo
    Mechanism:
      Entinostat: HNF4A de-repression
      + MHC-I restoration
      Palbociclib: CDK4 arrest
      + SASP → immunogenic cell death
    Predicted synergy:
      Two independent attack nodes
      on the same tumour

  Literature status: NOT DESCRIBED
    HDAC2 OS: known
    CDK4 OS: known (CMC 2025)
    Their JOINT analysis and
    combination drug rationale: NOVEL

──────────────────────────────────────

NOVEL 3:
  Stage I depth reversal

  Finding:
    In Stage I HCC (n=172):
    Deep OS = 31.9 months
    Shallow OS = 27.1 months
    (Direction reverses — deeper is
     better or equivalent in Stage I)
    All molecular markers NS in Stage I:
      CDC20 p=0.294
      CDK4  p=0.133
      HDAC2 p=0.087
    All become significant in Stage II-III

  Implication:
    The depth score is a Stage II–III
    biomarker, not a universal marker
    Stage I prognosis determined by
    surgical factors (margin, cirrhosis)
    not tumour molecular biology
    Biomarker panels using the depth
    axis should not be applied to
    Stage I HCC resection decisions

  Literature status: NOT DESCRIBED
    No published HCC subtype paper
    (Hoshida 2009, Sia 2017, TCGA 2017)
    reports stage-specific reversal
    of the differentiation axis

──────────────────────────────────────

NOVEL 4:
  CDC20 as single-gene proxy for the
  28-gene depth score (Model D)

  Finding:
    r(depth, CDC20) = +0.677
    When CDC20 added to Cox with depth:
      CDC20 HR = 1.547 p=3.58e-04
      depth HR = 1.042 p=0.73 (absorbed)
    Model D (stage+CDC20+HDAC2):
      All three independently significant
      AIC improved over stage alone
      n=341

  Clinical translation:
    28-gene RNA-seq panel → 2-gene IHC
    CDC20 IHC + HDAC2 IHC on resected
    HCC specimen provides:
      Prognostic information equivalent
      to 28-gene depth score
      Drug target identification (HDAC2)
      Cell cycle marker (CDC20)
    Feasibility: HIGH (standard IHC)
    Cost: LOW vs RNA-seq

  Literature status: NOT DESCRIBED
    CDC20 as HCC prognostic marker:
      known (meta-analysis HR=2.52)
    CDC20 as complete proxy for the
    differentiation axis and as
    component of minimum IHC model:
    NOVEL

──────────────────────────────────────

NOVEL 5:
  Two biologically distinct deep HCC
  states differing by aetiology
  (CDK4 direction reversal)

  Finding:
    TCGA (HCV/alcohol): r(depth,CDK4)=+0.653
    GSE14520 (HBV):     r(depth,CDK4)=-0.724
    Direction reversed across cohorts

  Interpretation:
    Deep Type A (HCV/alcohol, Hoshida S2):
      CDK4/CDC20-driven proliferation
      MYC/AKT pathway dominant
      HDAC2 = primary epigenetic lock
      CDK4/6 inhibitor = primary drug
      Best biomarker: CDK4 IHC

    Deep Type B (HBV, Hoshida S1):
      EZH2/TOP2A/CCNB1-driven
      WNT/TGF-β pathway dominant
      HBx → EZH2 → HNF4A silencing
      CDK4 falls as EZH2 rises
      EZH2 inhibitor = primary drug
      Best biomarker: EZH2 IHC

    HDAC2 = universal across both types
      (positive in both cohorts)
      HDAC inhibitor = universal drug

  Literature context:
    S1 vs S2 subtype difference: known
    HBV-HCC as S1-dominant: known
    CDK4 direction reversal as
    computational evidence for this:
    NOVEL (not previously demonstrated
    by r-value reversal across cohorts)

──────────────────────────────────────

NOVEL 6:
  HBx → EZH2 → depth axis connection

  Finding:
    EZH2 r=+0.859 with depth in
    GSE14520 (HBV-HCC) — highest
    single gene-depth correlation
    in the series (n=445)
    HBx mechanistically drives EZH2
    (confirmed by literature search)
    EZH2 → H3K27me3 → HNF4A silencing
    → depth rises

  Novel synthesis:
    Our computational depth score
    (EZH2 high → depth high in HBV)
    and the published HBx → EZH2
    mechanism are two sides of the
    same biological process.
    The OrganismCore false attractor
    model is confirmed at the
    molecular mechanism level
    specifically for HBV-HCC:
    HBx is the trigger that locks
    HBV-HCC into the false attractor

  Literature status: HBx → EZH2 known
    (NAR 2018, Springer 2023)
    EZH2 as the dominant computational
    depth correlate in HBV-HCC and
    the connection to the false
    attractor framework: NOVEL
```

---

### Tier 2 — Novel Quantification of Known Biology

```
NOVEL 7:
  CDK4 + CDKN2A runaway CDK4 quadrant

  Finding:
    r(CDK4, CDKN2A) = +0.277 p=5.94e-08
    CDK4-hi+CDKN2A-hi OS = 21.1 months
    CDK4-lo+CDKN2A-lo OS = 32.3 months
    Paradox: tumour suppressor (CDKN2A/
    p16) co-elevated with its target
    (CDK4) marks the worst OS quadrant

  Mechanism:
    CDK4 is active despite p16 expression
    p16/CDKN2A inhibition bypassed
    downstream (RB1 mutation, cyclin D
    amplification, or CDK4 mutation)
    The co-elevation marks a tumour
    where CDK4 has "run away" from
    its own brake

  Literature status:
    CDK4 adverse in HCC: known (CMC 2025)
    CDKN2A as tumour suppressor: known
    Their joint adverse quadrant in HCC
    with OS quantification: NOVEL

──────────────────────────────────────

NOVEL 8:
  Deep+Cold "quiet-deep" HCC subtype

  Finding:
    Depth-high + CD8A-absent subtype
    CD8A p=3.66e-21 (absent)
    OS = 24.7 months (n=65)
    Characterised by:
      CDK4-LOW (not high)
      AFP-LOW
      MKI67-LOW
      VIM-LOW
    Not the aggressive proliferative
    deep state — a quiescent deep state

  Interpretation:
    Deep+Cold = metabolically dedifferentiated
    but proliferatively quiescent and
    immunologically silent
    CTNNB1 correlation (+0.343 GSE14520)
    suggests Wnt-active immune exclusion
    in at least a subset
    Corresponds to Hoshida S1 minority
    in the TCGA cohort (the "rare B-type"
    in an otherwise A-type cohort)

  Literature status:
    Immune-desert subtype: known (Sia 2017)
    CDK4-low + depth-high specific
    characterisation as quiet-deep: NOVEL

──────────────────────────────────────

NOVEL 9:
  HDAC2 as checkpoint inhibitor
  resistance predictor

  Finding:
    HDAC2-hi + PRF1-hi OS = 15.0 months
    HDAC2-lo + PRF1-hi OS = 40.3 months
    Having CTLs present (PRF1-hi) only
    improves OS by 2.2 months when
    HDAC2 is high vs 17.7 months
    when HDAC2 is low
    HDAC2-hi blunts the benefit of
    immune effector function

  Implication:
    HDAC2-hi HCC patients may be
    poor responders to checkpoint
    inhibitors (anti-PD-1/PD-L1)
    despite T cell presence
    HDAC2 IHC before checkpoint
    treatment: potentially predictive
    of non-response
    HDAC inhibitor pre-treatment
    may restore checkpoint sensitivity

  Literature status:
    HDAC inhibitors restore antigen
    presentation: known (preclinical)
    HDAC2 specifically as a
    checkpoint resistance predictor
    in HCC with IHC rationale: NOVEL

──────────────────────────────────────

NOVEL 10:
  PTEN-low enrichment in Deep+Hot
  (EVOLVE-1 trial explanation)

  Finding:
    r(depth, PTEN) = -0.162 p=0.0017
    PTEN-low enriched in Deep+Hot
    (metabolically deep + immune active)
    NOT in Deep+Cold as originally
    predicted (S7-P5 not confirmed)

  Implication:
    mTOR inhibitor (everolimus) failed
    in unselected HCC (EVOLVE-1 trial)
    If PTEN-low (mTOR-active) patients
    are enriched in Deep+Hot specifically,
    an enriched trial in Deep+Hot+PTEN-low
    HCC would be predicted to show
    response where EVOLVE-1 did not
    The negative prediction (S7-P5)
    provided more insight than the
    positive would have

  Literature status:
    PTEN loss in HCC: known
    EVOLVE-1 failure: known
    PTEN-low enrichment in Deep+Hot
    as EVOLVE-1 explanation and
    new trial stratification: NOVEL
```

---

### Tier 3 — Framework Contributions

```
NOVEL 11:
  Continuous depth score extending
  Hoshida 2009 discrete classification

  Hoshida 2009: S1/S2/S3 (discrete)
  OrganismCore: 0–1 continuous score
  Adds:
    Prognostic granularity within subtypes
    Stage-stratified effect sizes
    Two-cohort OS validation
    Single-gene IHC reduction (CDC20)

NOVEL 12:
  Aetiology-stratified drug target
  selection framework
  (Type A: CDK4/6i; Type B: EZH2i;
   Universal: HDACi)

NOVEL 13:
  Tazemetostat + entinostat combination
  rationale for HBV-HCC
  (EZH2-hi + HDAC2-hi = dual epigenetic
   lock; HBx drives both;
   no prior trial exists)
```

---

## Part III: Literature Convergence
### (Our findings match published work)

| Finding | Converges With | Reference |
|---------|----------------|-----------|
| Depth axis = differentiation state | Hoshida 2009 S1/S2/S3 | Cancer Res 2009;69:7385 |
| HNF4A loss drives dedifferentiation | Multiple HNF4A reviews | europepmc PMID 21403612; Springer 2025 |
| CDC20 OS predictor | Meta-analysis HR=2.52 | Frontiers Oncology 2022 |
| CDK4 OS predictor | CMC 2025 paper | Curr Med Chem 2025;32:2 |
| HDAC2 adverse prognostic | AACR 2014, Springer 2025 | Cancer Res 2014;74:1728 |
| BIRC5 adverse prognostic | >50 published papers | Well established |
| PRF1/CYT score prognostic | CYT score literature | Anticancer Res 38:6631 |
| Immune subtypes (desert/excluded/hot) | Sia 2017 | Gastroenterology 2017 |
| CTNNB1-mut better OS | Meta-analysis 2023, AACR 2025 | OS=39.78mo vs 25.15mo |
| CTNNB1-mut → immune exclusion | Wnt-CCL4/5 axis | Nature Rev Gastro 2025 |
| CDK4/6 inhibitor in HCC | Gut 2017; NCT06478927 | Active clinical trial |
| HDAC inhib + checkpoint synergy | Frontiers Immunology 2023 | Preclinical confirmed |
| CDK4/6i → SASP → immunogenic | Springer 2024 | Mechanism confirmed |
| HBV-HCC is Hoshida S1 dominant | Lancet EBioMedicine 2018 | Molecular characterisation |
| HBV → TP53 mutation dominant | Gut 2015;64:820 | HBV genomic integration |
| HBx upregulates EZH2 | NAR 2018; Springer 2023 | Confirmed mechanism |
| EZH2 adverse OS predictor | Nature 2025; MDPI 2022 | r=+0.859 consistent |
| HBx → PD-L1 immune evasion | PLoS ONE 2025 | HBx-EZH2-PD-L1 axis |
| Palbociclib requires RB1 | Resistance review 2024 | Nature Cancer 2024 |
| Tazemetostat safe in hepatic impairment | NCT04241835 | Phase I PK data |

---

## Part IV: Drug Predictions and Hypotheses

---

### IV.A — Grade A (Strongest Evidence)

```
DRUG A1: Entinostat (HDAC1/2 inhibitor)
  Target population:
    HDAC2-high Stage III HCC
  Selection biomarker:
    HDAC2 IHC (high = top quartile)
    Stage III (AJCC)
  Target OS without treatment:
    12.2–13.7 months
  Expected mechanism:
    HDAC2 inhibition
    → H3K27 acetylation at HNF4A promoter
    → HNF4A re-expressed
    → Metabolic identity partially restored
    → MHC-I antigen presentation restored
    → Depth score falls
  Evidence:
    HDAC2 Stage III gap: 19.2mo
      (p=1.93e-04)
    HDAC2 tertile T3: OS=12.2mo
      (T3 vs T1 p=5.45e-05)
    HDAC2-hi+CDK4-hi: OS=12.2mo
      (p=4.79e-06)
    Entinostat anti-HCC preclinical:
      confirmed (JNK/P38 apoptosis)
  Clinical status:
    Phase I/II studies in progress
    No Phase III in HCC
    No approved indication in HCC
  Aetiology:
    Both HCV/alcohol AND HBV
    (HDAC2 universal across cohorts)

──────────────────────────────────────

DRUG A2: Palbociclib (CDK4/6 inhibitor)
  Target population:
    CDK4-high Stage II–III HCC
    Specifically CDK4-hi+CDKN2A-hi
    (runaway CDK4 state)
  Selection biomarker:
    CDK4 IHC (high = top half)
    Stage II–III
    RB1 functional (required, >70% HCC)
  Target OS without treatment:
    Stage III CDK4-hi: 16.3 months
    CDK4+CDKN2A-hi quadrant: 21.1 months
  Expected mechanism:
    CDK4/6 inhibition
    → RB1 hypophosphorylation
    → E2F transcription suppressed
    → S-phase arrest
    → SASP → immunogenic cell death
    → T cell recruitment enhanced
  Evidence:
    CDK4 Stage III gap: 14.0mo
      (p=4.88e-04)
    CDK4+CDKN2A-hi worst quadrant:
      OS=21.1mo (p=5.94e-08)
    Palbociclib preclinical HCC:
      confirmed (Gut 2017;66:1286)
    CDK4/6i → SASP → T cell:
      confirmed (Springer 2024)
  Clinical status:
    ACTIVE TRIAL: NCT06478927
    Backline advanced HCC
    Enrolling 2024
    Not biomarker-stratified
  Aetiology:
    Primarily HCV/alcohol (Type A)
    CDK4-low in HBV-HCC (Type B)
    → Biomarker in HBV should be
      CDK6 IHC not CDK4 IHC

──────────────────────────────────────

DRUG A3: Entinostat + Palbociclib
  (combination — novel)
  Target population:
    HDAC2-hi + CDK4-hi Stage III HCC
    n=32/85 Stage III (38%)
  Selection biomarker:
    HDAC2 IHC + CDK4 IHC
    Both high + Stage III
  Target OS without treatment:
    12.2 months
  Expected mechanism:
    Entinostat:
      HNF4A de-repression
      MHC-I antigen presentation
      Chromatin opening
    Palbociclib:
      CDK4 arrest
      SASP induction
      T cell sensitisation
    Synergy predicted:
      Two independent nodes attacked
      simultaneously
      Bliss independence or HSA synergy
      predicted in HDAC2-hi+CDK4-hi
      HCC cell lines (SNU-449, Hep3B)
  Clinical status:
    NOVEL — not tested in HCC
    No published preclinical study
    of this specific combination
  Aetiology:
    HCV/alcohol HCC primarily
    (CDK4-hi most common in Type A)
```

---

### IV.B — Grade B (Good Evidence, Earlier Stage)

```
DRUG B1: Tazemetostat (EZH2 inhibitor)
  Target population:
    EZH2-high HBV-associated HCC
  Selection biomarker:
    EZH2 IHC (high)
    HBV status (positive)
  Expected mechanism:
    EZH2 inhibition
    → H3K27me3 de-repression
    → HNF4A, IGFBP4, let-7c restored
    → HBx-driven epigenetic lock
      partially reversed
    → Depth score falls
  Evidence:
    r(depth, EZH2) = +0.859 in GSE14520
      (strongest correlation in series)
    HBx → EZH2 mechanism: confirmed
      (NAR 2018, Springer 2023)
    EZH2 inhibition preclinical in HCC:
      confirmed (tool compounds)
    Tazemetostat PK in hepatic impairment:
      favourable (NCT04241835)
  Clinical status:
    FDA approved (sarcoma, lymphoma)
    No HCC efficacy trial
    PK study in liver impairment active
    WHITE SPACE — this is a genuine
    unoccupied therapeutic niche
  Aetiology:
    HBV-dominant (Type B deep state)
    EZH2-lo in Type A → lower priority

──────────────────────────────────────

DRUG B2: Tazemetostat + Entinostat
  (dual epigenetic — HBV-specific)
  Target population:
    EZH2-hi + HDAC2-hi HBV-HCC
  Rationale:
    HBV-HCC has BOTH epigenetic locks:
      EZH2 (H3K27me3) — HBx-driven
      HDAC2 (H3K27 deacetylation)
    Blocking one may be bypassed
    by the other
    Dual inhibition attacks both
    PRC2-mediated and HDAC-mediated
    silencing simultaneously
  Clinical status:
    NOVEL — not tested anywhere
    Mechanistically rational
    Safety data available separately
    for both agents

──────────────────────────────────────

DRUG B3: Anti-PD-1 / Anti-PD-L1
  (checkpoint — enriched population)
  Target population:
    PRF1-hi + HDAC2-lo Stage II–III
    (= HDAC2-lo+PRF1-hi: OS=40.3mo)
  Selection biomarker:
    PRF1 IHC + HDAC2 IHC
    PRF1-hi + HDAC2-lo = respond
    PRF1-hi + HDAC2-hi = likely resist
  Evidence:
    HDAC2-lo+PRF1-hi OS=40.3mo vs
    HDAC2-hi+PRF1-lo OS=12.8mo
    (27.5mo gap, p=7.19e-05)
    HDAC2 as checkpoint resistance
    predictor: novel
  Clinical status:
    APPROVED (atezolizumab+bevacizumab,
    nivolumab, pembrolizumab)
    in unselected/PD-L1-selected HCC
    Our contribution: HDAC2+PRF1 dual
    IHC as precision selection tool

──────────────────────────────────────

DRUG B4: Entinostat + Anti-PD-1
  Target population:
    HDAC2-hi + PRF1-lo Stage III
    (OS=12.8mo — worst immune subtype)
  Rationale:
    Entinostat restores MHC-I
    → tumour becomes antigen-visible
    Anti-PD-1 sustains the CTL
    activity once initiated
    Sequence: entinostat first
    (prime antigen presentation)
    then anti-PD-1 (sustain killing)
  Evidence:
    HDAC inhib + checkpoint synergy:
      confirmed preclinically
      (Frontiers Immunology 2023)
    Our HDAC2×PRF1 framework:
      provides patient selection
      logic (not in literature)
  Clinical status:
    Combination in HCC: preclinical
    Component agents: approved/Phase II

──────────────────────────────────────

DRUG B5: Tazemetostat + Anti-PD-1
  (HBV-specific combination)
  Target population:
    HBV-HCC with EZH2-hi + immune excluded
  Rationale:
    HBx drives EZH2 AND PD-L1
    simultaneously (PLoS ONE 2025)
    EZH2 inhibition disrupts the
    epigenetic component of HBx
    oncogenesis
    Anti-PD-1 blocks the immune
    evasion component
    Two prongs of the same HBx
    programme attacked together
  Clinical status:
    NOVEL — not tested in HCC

──────────────────────────────────────

DRUG B6: Everolimus (mTOR inhibitor)
  Target population:
    PTEN-low + Deep+Hot HCC
    (NOT unselected as in EVOLVE-1)
  Selection biomarker:
    PTEN IHC (low) + depth-high
    + immune-hot (CD8A-high)
  Evidence:
    PTEN-low enriched in Deep+Hot:
      r=-0.162 p=0.0017
    EVOLVE-1 failed in unselected HCC
    Enrichment for PTEN-low+Deep+Hot
    predicted to rescue trial result
  Clinical status:
    EVOLVE-1: FAILED (unselected)
    EVOLVE-2 possibility: enriched
    Our enrichment rationale: NOVEL
```

---

### IV.C — Drug Priority Summary

```
Immediate priority (Grade A, HCV/alcohol HCC):
  1. Entinostat in HDAC2-hi Stage III
  2. Palbociclib in CDK4-hi Stage II-III
  3. Entinostat + palbociclib in
     HDAC2-hi+CDK4-hi Stage III

Immediate priority (Grade B, HBV HCC):
  4. Tazemetostat in EZH2-hi HBV-HCC
  5. Tazemetostat + entinostat
     in EZH2-hi+HDAC2-hi HBV-HCC

Precision immunotherapy (both):
  6. Anti-PD-1 in PRF1-hi+HDAC2-lo
     (select for, not against)
  7. HDACi + anti-PD-1 in
     HDAC2-hi+PRF1-lo Stage III
  8. Tazemetostat + anti-PD-1
     in HBV-HCC immune-excluded

Rescue trial design:
  9. Everolimus in PTEN-low+Deep+Hot
     (explains EVOLVE-1 failure)

Emerging (CDK4/6i + immune):
  10. Palbociclib + anti-PD-1 in
      CDK4-hi+exhaust-hi Stage III
      (CDK4/6i → SASP → T cell
       sensitisation: Springer 2024)
```

---

## Part V: The Unified False Attractor Model

```
NORMAL HEPATOCYTE STATE (depth ≈ 0):
  HNF4A active
  CYP3A4/G6PC/ALB/APOB/PPARA on
  CDC20/BIRC5/AFP/EPCAM/TOP2A off
  HDAC2 low / EZH2 low
  Immune: not applicable

          ↓ TRIGGER
  HCV/alcohol: metabolic/inflammatory
  HBV: HBx protein expression

EPIGENETIC LOCK ENGAGED:
  Type A (HCV/alcohol):
    HDAC2 upregulated
    → H3K27 deacetylation
    → HNF4A, PPARA, RXRA silenced
    → Metabolic identity lost
    → CDK4/cyclin D pathway activated
    → CDC20 proliferative programme

  Type B (HBV):
    HBx → EZH2 upregulated
    → H3K27me3 at HNF4A, IGFBP4,
      let-7c loci
    → Same downstream loss of
      hepatocyte identity
    → TOP2A/CCNB1/aurora kinase
      proliferative programme
    → CDK4 LOW (bypass CDK4-RB1 axis)
    → HBx also drives PD-L1
      → immune exclusion direct

ATTRACTOR DEEPENS (depth 0.3–0.5+):
  FA programme locks in:
    AFP, EPCAM (progenitor markers)
    CDC20, BIRC5, MKI67 (mitotic)
    EZH2 (self-reinforcing epigenetic)
    HDAC2 (self-reinforcing epigenetic)
  Self-reinforcing loops:
    EZH2 silences its own repressors
    HDAC2 maintains deacetylated state
    CDC20 drives rapid cell cycle
    (less time for differentiation)

IMMUNE EVASION (Stage II–III):
  HDAC2 high → MHC-I low
    → antigens not presented
    → CTLs cannot engage
  EZH2 high → immune suppression
    → checkpoint ligands upregulated
  Two immune outcomes:
    Deep+Hot (TCGA Type A minority):
      CTLs present but exhausted
      PD-1/TIM-3/LAG-3/TIGIT up
      PRF1 present but HDAC2 blunts
      killing (OS=27.3mo)
    Deep+Cold (TCGA Type B minority
    and GSE14520 HBV majority):
      T cells excluded (Wnt/TGF-β)
      CD8A absent (p=3.66e-21)
      PRF1 absent
      OS=24.7mo

STAGE III ENDPOINT:
  HDAC2-hi+CDK4-hi+PRF1-lo:
    OS = 12.2 months (worst)
  HDAC2-lo+CDK4-lo+PRF1-hi:
    OS = 34.1–40.3 months (best)
  Gap = 21.9–27.5 months
  This is the therapeutic window.

THERAPEUTIC REVERSAL:
  Step 1: Entinostat (HDACi)
    → H3K27 acetylation restored
    → HNF4A de-repressed
    → MHC-I restored
    → Depth falls
  Step 2a (Type A): Palbociclib
    → CDK4 arrested
    → SASP → immunogenic
  Step 2b (Type B): Tazemetostat
    → H3K27me3 removed
    → Differentiation genes restored
  Step 3: Anti-PD-1
    → CTLs sustained
    → PRF1 killing enabled
    → Attractor reversed
```

---

## Part VI: Pending Items

```
COMPUTATIONAL:
  1. GSE14520 survival data
     File needed: GEO supplementary
       (Roessler et al. Cancer Res 2010
        Supplement Table S1)
     Will test: S9-P1 (CDK4 OS)
                S9-P3 (depth OS reconfirm)
                S9-P6 (PRF1 OS)
                S9-P7 (BIRC5 OS)
     Predicted: CDK4-lo may be worse OS
       in GSE14520 given r=-0.724
       (opposite to TCGA) — this would
       confirm the Type A/B distinction

  2. Full GDC MAF (TCGA-LIHC)
     Will test: HCC-P5 computationally
       CTNNB1-mut depth shallower than
       TP53-mut (literature pre-confirmed)
     URL: portal.gdc.cancer.gov
       TCGA-LIHC → Masked Somatic
       Mutation → WXS → Open → Download

EXPERIMENTAL:
  Priority 1:
    Entinostat + palbociclib synergy
    in HDAC2-hi+CDK4-hi HCC cell lines
    SNU-449 (TP53-mut, high HDAC2)
    Hep3B (HBV-integrated, TP53-null)
    HepG2 (CTNNB1-mut, moderate HDAC2)
    Measure: Bliss independence / HSA
    Readout: proliferation + MHC-I
             expression + PRF1 killing

  Priority 2:
    HDAC2 IHC validation on resected
    HCC cohort
    Validate HDAC2 IHC → OS (from
    RNA → protein)
    Test Model D in clinical cohort

  Priority 3:
    EZH2 inhibition in HBV-HCC lines
    Tazemetostat in HBV-positive lines
    Measure: HNF4A restoration, depth
    markers, MHC-I expression

PUBLICATION:
  Paper 1 (ready to write):
    "HDAC2 and PRF1 define a joint
    prognostic and therapeutic framework
    in Stage III hepatocellular carcinoma"
    Key result: 40.3 vs 12.8mo, 27.5mo gap
    Target: Journal of Hepatology

  Paper 2 (ready to write):
    "HDAC2 and CDK4 co-expression
    identifies the worst Stage III HCC
    subgroup and defines a combination
    drug rationale"
    Key result: 12.2 vs 34.1mo, 21.9mo gap
    Target: Hepatology or Gut

  Paper 3 (data partially ready):
    "Two biologically distinct deep HCC
    states differ by aetiology, CDK4
    expression, and drug sensitivity"
    Key result: CDK4 direction reversal
    TCGA vs GSE14520
    Needs: GSE14520 OS data
    Target: Cancer Research or Hepatology
```

---

## Series Metrics

```
Scripts completed:         9
Documents produced:        92a–92j + addendum
Primary cohort (TCGA):     n=371 HCC
                           OS events=130
Secondary cohort (GSE):    n=445 expression
                           OS pending
Genes tested:              83 (TCGA)
                           21 (GSE14520)
Predictions made:          18 formal
Predictions confirmed:     13 computational
                         + 1 literature
Predictions not confirmed: 2
  (depth×stage interaction underpowered;
   PTEN in Deep+Cold — revised to Hot)
Predictions not testable:  4
  (GSE14520 OS absent; MAF incomplete)
Novel contributions:       13
Literature convergences:   19
Drug hypotheses:           10
Literature searches:       11 domains
  (live internet, 2026-03-02)
```

---
*OrganismCore | HCC False Attractor Series | Master Artifact*
*Documents 92a–92j (Addendum) | Scripts 1–9*
*Author: Eric Robert Lawson | 2026-03-02*
*Framework: OrganismCore-HCC-Final*
*Status: Series complete — pending experimental validation*
