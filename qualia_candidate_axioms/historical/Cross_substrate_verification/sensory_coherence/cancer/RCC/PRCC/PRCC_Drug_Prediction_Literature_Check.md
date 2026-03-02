# Document 95-DLC — Drug Literature Check
## PRCC False Attractor — All 11 Drug Targets
### OrganismCore | 2026-03-02 | Author: Eric Robert Lawson

---

## PREAMBLE

```
PURPOSE:
  Map every drug target predicted from the PRCC
  false attractor geometry against what is
  currently known clinically.
  For each drug: prior evidence, trial status,
  what our geometry adds, conflicts to resolve,
  and deployment readiness.

DRUGS CHECKED: 11
DATE: 2026-03-02
```

---

## DRUG 1: TAZEMETOSTAT (EZH2 INHIBITOR)

```
OUR PREDICTION:
  EZH2 is a depth-stratified target.
  Q4/Q1 ratio = 1.109, monotonic rise.
  EZH2 inhibition most valuable in Q3/Q4.
  Mechanism: TCA-chromatin coupling
  (SUCLG1→EZH2, FH→EZH2) drives EZH2 lock.
  Combination: tazemetostat + αKG preferred over
  tazemetostat alone.

WHAT IS KNOWN:
  Clinical trials:
    — NCT03874455: Tazemetostat in RCC and
      malignant rhabdoid tumours — includes RCC
      but focused on SMARCB1/INI1-deficient cases
      (renal medullary carcinoma, collecting duct).
      NOT classic PRCC. Programme now CLOSED
      to new patients (expanded access closed).
    — NCI-COG Pediatric MATCH (NCT02601937):
      includes EZH2/SMARCB1/SMARCA4-altered tumours.
      Limited objective responses, some stable
      disease in rare renal cancers.
    — NO published trial specifically in
      papillary RCC with tazemetostat.
    — Hong et al. FEBS Open Bio 2023:
      Preclinical — tazemetostat reduces
      proliferation in RCC cell lines including
      PRCC models via LATS1/Hippo pathway.
      PRCC-specific PRECLINICAL evidence exists.

  EZH2 overexpression in PRCC: PUBLISHED.
  Tazemetostat approved indications:
    — Epithelioid sarcoma (EZH2 mutation)
    — Follicular lymphoma (EZH2 mutation)
  Neither PRCC nor non-SMARCB1 RCC is approved.

WHAT OUR GEOMETRY ADDS:
  1. The DEPTH STRATIFICATION: EZH2 rises
     monotonically from Q1 to Q4.
     Prior work says EZH2 is "elevated in PRCC"
     without depth context.
     Our contribution: Q3/Q4 patients need
     tazemetostat most. Q1 patients least.
     This is a new patient selection principle.

  2. The TCA-CHROMATIN MECHANISM:
     EZH2 elevation is PARTIALLY driven by
     FH/SUCLG1/OGDHL suppression (αKG depletion).
     This means tazemetostat alone addresses the
     downstream lock but not the upstream driver.
     αKG + tazemetostat targets both.
     This combination rationale is NOT in any
     published PRCC paper.

  3. SETD2 CO-FALL creates a TWO-STEP lock.
     When FH is low AND SETD2 is low, EZH2
     operates without H3K36me3 opposition.
     Tazemetostat is most urgently needed in
     FH-low/SETD2-low Q4 PRCC.

CLINICAL READINESS:
  Tazemetostat: FDA-approved drug, available.
  PRCC indication: off-label, no approved use.
  Nearest trial path:
    Basket trial approach — enrol EZH2-high PRCC
    (by IHC or RNA) into tazemetostat monotherapy
    arm. Biomarker: EZH2 H3K27me3 by IHC.
  Combination trial path:
    Phase 1b: tazemetostat + cell-permeable αKG
    (DMKG) in FH-low / OGDHL-low PRCC.
    No safety data for this combination exists yet.

CONFLICT WITH LITERATURE:
  None. The preclinical data supports it.
  The absence of PRCC trials is a GAP, not a
  contradiction.

VERDICT: OPEN CLINICAL GAP — HIGH PRIORITY
```

---

## DRUG 2: SAVOLITINIB / MET INHIBITOR

```
OUR PREDICTION:
  MET is an identity driver, not a mitogen.
  r(MET, MKI67) = -0.069 (uncoupled from prolif).
  MET present in Q4 (Q4/Q1=1.088) —
  relevant across ALL depth strata, not just
  shallow/Type 1.
  Response biomarker: KRT19 fall, not RECIST.

WHAT IS KNOWN:
  SAVOIR trial (Choueiri et al. JAMA Oncol 2020):
    — Phase 3, n=60 (closed early, planned 180)
    — MET-driven PRCC (chromosome 7 gain mostly)
    — Savolitinib vs sunitinib
    — ORR: 27% vs 7%  ★
    — PFS: 7.0 vs 5.6 months (HR=0.71, ns)
    — OS:  NR vs 13.2 months (numerically favours
      savolitinib)
    — G3+ AEs: 42% vs 81% (markedly safer)
    — Closed early: insufficient accrual
    — Population: MOSTLY Type 1 PRCC proxies
      (chromosome 7 gain = MET-driven = Type 1)

  Other MET inhibitors in PRCC:
    Cabozantinib: active in PRCC
      (includes MET + VEGFR2 inhibition)
    Tepotinib: Phase 2 VISION trial included
      small number of non-NSCLC MET exon 14
      skip tumours — not PRCC specifically
    Crizotinib: tested in PRCC in Phase 2
      (Markowski et al.) — some activity

WHAT OUR GEOMETRY ADDS:
  1. The IDENTITY MECHANISM explains the 27% ORR.
     If MET were a proliferative kinase (like BRAF
     in melanoma), ORR would be >50%.
     27% is consistent with an IDENTITY DRIVER:
     responses occur via biliary identity disruption,
     not cytoreduction.
     This is a new mechanistic explanation for
     SAVOIR's modest but real signal.

  2. MET in Q4 (Q4/Q1=1.088): MET is NOT confined
     to shallow/Type 1 tumours.
     SAVOIR selected MET-DRIVEN tumours (chromosome
     7 gain). Our geometry shows MET RNA is elevated
     in Q4 independent of that molecular criterion.
     Type 2 PRCC (deep, FH-low) also has elevated MET.
     SAVOIR's subtype-unselected Q4 patients were
     EXCLUDED from the trial (by MET-driven criterion).
     A trial of MET inhibition in Q4 regardless of
     chromosome 7 gain status is NOT yet done.

  3. Proposed response biomarker (KRT19 IHC fall)
     has NOT been measured in any PRCC MET inhibitor
     trial. All current trials use RECIST.

CONFLICT WITH LITERATURE:
  None. Our geometry is consistent with SAVOIR.

VERDICT: SUPPORTED BY SAVOIR — HIGH CLINICAL
CONFIDENCE. NOVEL: MET in Q4, identity mechanism,
KRT19 response biomarker.
```

---

## DRUG 3: ERBB2-TARGETED THERAPY
## (TRASTUZUMAB / TUCATINIB / T-DM1 / NERATINIB)

```
OUR PREDICTION:
  ERBB2 is the #3 depth correlate (r=+0.556).
  ERBB2 is an identity co-driver (not mitogen).
  r(ERBB2, KRT19) = +0.525
  r(ERBB2, MKI67) = -0.170
  HER2-targeted therapy via identity disruption,
  not anti-proliferative mechanism.
  Biomarker: HER2 IHC 2+ WITHOUT FISH required
  (biliary identity co-expression, not amplification).
  Target population: ERBB2-high / KRT7-high deep PRCC.

WHAT IS KNOWN:
  SGNTUC-019 basket trial (NCT04579380):
    — Phase 2 — tucatinib + trastuzumab in
      HER2-altered solid tumours
    — Urothelial cancer cohort published
      (ASCO GU 2022)
    — RCC/PRCC cohort: ELIGIBLE if HER2-altered
      but no PRCC-specific published results
    — HER2 alteration criterion = amplification
      or mutation on NGS — NOT IHC 2+ without FISH

  NCI-MATCH: includes HER2-amplified solid tumours
    — Rare RCC/PRCC cases may be included but
      no PRCC-specific arm or published data

  Pan-cancer HER2 analysis (EBioMedicine 2020):
    — Identifies transcriptional HER2 pattern
      across cancer types
    — PRCC included in pan-cancer analysis
    — HER2 transcriptional pattern present in
      subset of PRCC tumours

  HER2-targeted therapy in biliary tract cancer
  (ICC): PUBLISHED EFFICACY
    — HERB trial: trastuzumab deruxtecan (T-DXd)
      in HER2-positive BTC — positive results
    — HER2 IHC 2+ without amplification has
      activity in BTC
    — ICC shares the biliary identity with PRCC
      in our geometry

CRITICAL FINDING FROM LITERATURE:
  In BILIARY TRACT CANCER (the closest identity-
  matched cancer to deep PRCC in our framework),
  HER2 IHC 2+ WITHOUT amplification has clinical
  activity.
  The HERB trial and related BTC data show
  T-DXd (trastuzumab deruxtecan) active in
  HER2 IHC 2+/3+ BTC.
  Since our framework identifies deep PRCC as
  occupying a BILIARY IDENTITY attractor state,
  the BTC HER2 data is the most relevant clinical
  precedent for our ERBB2 prediction.
  This is the STRONGEST clinical support our
  ERBB2 prediction has — from a cross-cancer
  identity-matched framework.

WHAT OUR GEOMETRY ADDS:
  1. ERBB2 is the depth correlate for PRCC —
     not just an occasional finding.
     r=+0.556 is the third strongest correlate
     across 290 tumours.

  2. ERBB2 IHC 2+ (not FISH-amplified) as the
     correct biomarker — consistent with BTC data.
     Current basket trials require FISH amplification
     or NGS mutation. This EXCLUDES the ERBB2-high
     identity-co-expression population that does not
     have amplification. That is the wrong criterion
     for PRCC if our mechanism is correct.

  3. Expected response phenotype = identity shift,
     not RECIST shrinkage. No current trial measures
     this. All use RECIST. This is a critical
     measurement gap.

CONFLICT WITH LITERATURE:
  None — no prior HER2 trial in PRCC to contradict.
  The framework EXTENDS biliary HER2 data to PRCC
  via identity-matched geometry.

VERDICT: HIGH NOVELTY — STRONGEST INDIRECT SUPPORT
FROM BTC DATA. Clinical trial gap: no PRCC-specific
HER2 trial with IHC 2+ criterion exists.
```

---

## DRUG 4: CDK4/6 INHIBITOR
## (PALBOCICLIB / RIBOCICLIB / ABEMACICLIB)

```
OUR PREDICTION:
  CDK4/6 inhibition from CDKN2A paradox.
  CDKN2A RNA UP (+4.33 FC), CDK4 RNA UP (+1.34 FC),
  CDK4 RNA higher in shallow tumours (Q4/Q1=0.974).
  Prediction: CDKN2A high + CDK4 high co-occur at
  the sample level (oncogenic stress bypass).
  CDK4/6 inhibitor priority: Q1/Q2 (CDK4 is highest
  in shallow strata).

WHAT IS KNOWN:
  Abemaciclib Phase 1b (NCT04627064):
    — Abemaciclib monotherapy in previously
      treated advanced RCC
    — n=11 patients (1 translocation RCC,
      rest clear cell)
    — ORR: 0% — NO OBJECTIVE RESPONSES
    — 1 patient: stable disease only
    — Conclusion by investigators: "no clinically
      meaningful activity as monotherapy"
    — Ongoing exploration of CDK4/6i in COMBINATION
      (e.g., with belzutifan) in ccRCC

  Nature Reviews Urology 2022:
    — Review of CDK4/6i potential in RCC
    — Notes: CDKN2A is frequently altered in PRCC
      Type 2. CDK4/6 inhibition theoretically
      addresses this.
    — Clinical evidence: absent for PRCC

  Key fact: The abemaciclib monotherapy trial
  was in ccRCC, not PRCC. PRCC-specific CDK4/6i
  trial: DOES NOT EXIST.

WHAT OUR GEOMETRY ADDS:
  1. The CDKN2A PARADOX: CDKN2A RNA UP + CDK4 UP
     simultaneously. This cannot be explained by
     simple CDKN2A function. The bypass operates
     at the protein level. CDK4/6i addresses the
     active kinase regardless of CDKN2A RNA status.

  2. DEPTH STRATIFICATION: CDK4 highest in Q1/Q2
     (Q4/Q1=0.974, flat). CDK4/6i is a Q1/Q2
     drug for PRCC — not Q4. This is the opposite
     of EZH2i (Q4 priority).

  3. The 0% ORR in ccRCC monotherapy does NOT
     exclude PRCC. The mechanisms are entirely
     different (VHL/HIF vs biliary identity).
     The abemaciclib result is for the wrong
     tumour type and should not be used to
     dismiss the PRCC prediction.

CONFLICT WITH LITERATURE:
  The 0% ORR in ccRCC is a weak contra-indicator
  but not a true conflict (different disease).
  It sets expectations: CDK4/6i is unlikely to
  produce strong RECIST responses in PRCC alone.
  Most likely role: depth-stratified combination
  (CDK4/6i in Q1/Q2 + identity disruptor).

VERDICT: PREDICTION STANDS BUT MODEST EXPECTATIONS.
Depth stratification (Q1/Q2 not Q4) distinguishes
our prediction from the failed ccRCC trial.
```

---

## DRUG 5: KDM1A INHIBITOR
## (IADADEMSTAT / BOMEDEMSTAT / TRANYLCYPROMINE)

```
OUR PREDICTION:
  KDM1A (LSD1) is depth-positive (Q4/Q1=1.048).
  KDM1A is the #20 TI correlate (r_TI=+0.411).
  KDM1A inhibition restores H3K4me marks,
  potentially reversing the biliary identity lock.
  Q3/Q4 priority.

WHAT IS KNOWN:
  Iadademstat (ORY-1001):
    — Phase 1/2 in AML — primary indication
    — Phase 1/2 in SCLC — expanding into
      neuroendocrine / solid tumours
    — NO trials in RCC or PRCC
    — No published RCC-specific data

  Bomedemstat (IMG-7289):
    — Phase 2 in myelofibrosis and AML
    — No solid tumour RCC trials published

  Tranylcypromine derivatives:
    — Phase 1 in AML, SCLC
    — No kidney cancer data

  KDM1A in RCC:
    — KDM1A overexpression in RCC published
      in molecular characterisation papers
    — KDM1A inhibition in RCC cell lines:
      PRECLINICAL DATA EXISTS — reduces
      invasiveness and proliferation
    — Clinical trial in RCC: DOES NOT EXIST

WHAT OUR GEOMETRY ADDS:
  1. KDM1A as a DEPTH-STRATIFIED target:
     Q4/Q1=1.048, r_TI=+0.411. KDM1A tracks
     the biliary identity axis (positive TI
     correlate). KDM1A is not just elevated in
     PRCC — it tracks the depth of the false
     attractor specifically.

  2. KDM1A in the same axis as ERBB2 and EZH2:
     All three rise with depth. The chromatin
     lock (EZH2 H3K27me3) and the H3K4me
     demethylation lock (KDM1A) operate in
     the same deep-PRCC compartment.
     KDM1A inhibition would restore H3K4me3
     at identity-switching genes, potentially
     allowing re-expression of SLC22A6 and
     FABP1 (PT identity markers).

  3. Combination rationale:
     KDM1A + EZH2i combination would address
     both H3K4me LOSS (KDM1A inhibition restores)
     and H3K27me3 GAIN (tazemetostat removes).
     This is a dual chromatin lock reversal.

CONFLICT WITH LITERATURE:
  No published RCC trial to conflict with.
  Preclinical support exists.

VERDICT: NOVEL TARGET FOR PRCC — STRONG GEOMETRY
RATIONALE. Clinical evidence gap is large —
the field has not tested KDM1A inhibitors in
any kidney cancer.
```

---

## DRUG 6: αKG SUPPLEMENTATION
## (CELL-PERMEABLE DMKG / αKG PRECURSORS)

```
OUR PREDICTION:
  αKG supplementation addresses OGDHL/FH/SUCLG1
  collapse in deep PRCC.
  OGDHL Q4/Q1=0.842 (sharpest drug map fall).
  FH expression r=-0.451 with depth.
  Mechanism: restore TET2 activity (r_FH_TET2=-0.341),
  oppose EZH2 (r_FH_EZH2=-0.293).
  Patient selection: FH-low RNA / OGDHL-low RNA.
  Combination: αKG + tazemetostat.

WHAT IS KNOWN:
  DMKG (dimethyl-α-ketoglutarate):
    — Research tool compound, not clinical grade
    — Used in preclinical studies to rescue TET2
      activity in fumarate/succinate-accumulating
      tumours
    — Published in FH-mutant and IDH-mutant contexts

  αKG dietary supplementation:
    — Published in aging/health context
      (Cell Trends Endocrinology 2021)
    — Generally safe, GI side effects
    — Clinical doses in health context: 1-4g/day
    — NO published cancer treatment trial
      with αKG as the primary intervention

  Clinical trial status:
    — NO clinical trial of αKG or DMKG
      specifically in FH-deficient or PRCC
    — αKG precursors (e.g., glutamine, citrate)
      in cancer metabolism studies — indirect only
    — No clinical grade cell-permeable αKG product
      that is regulatory-approved for oncology

  α-KG and TET2 rescue:
    — Mechanistically published (Intlekofer et al.,
      Molenaar et al. IDH context)
    — Preclinical support for epigenetic rescue

  NEW 2026 finding:
    — Springer 2026: αKG activates AIM2-dependent
      PANoptosis via TET2-mediated demethylation
      in inflammatory contexts.
    — This is a POTENTIAL SAFETY SIGNAL:
      αKG at supraphysiological levels may
      activate inflammatory cell death pathways
      (AIM2/PANoptosis) in non-tumour tissues.
      This was published February 2026 —
      new safety consideration for our prediction.

WHAT OUR GEOMETRY ADDS:
  1. CONTINUOUS FH RNA as patient selector:
     FH-low quartile = mean depth 0.737.
     This selects the Q4 patients who need
     αKG most — regardless of FH mutation status.
     Prior literature targets only FH-MUTANT
     (~10 CIMP cases in KIRP).
     Our selector targets ~73 patients (bottom
     FH quartile) across all mutation backgrounds.

  2. OGDHL as the sharpest Q4 fall (Q4/Q1=0.842):
     OGDHL is the rate-limiting entry point into
     TCA at the αKG-succinate step.
     OGDHL-low + FH-low = maximal αKG deficit.
     This dual criterion selects the deepest
     TCA-collapsed PRCC subset.

  3. TET2 RNA compensation (r_TET2_depth=+0.070):
     TET2 RNA is already UP in Q4 but inactive.
     αKG would ACTIVATE pre-made TET2 protein
     immediately. This is a faster rescue mechanism
     than waiting for new TET2 transcription.

CONFLICT WITH LITERATURE:
  The 2026 AIM2/PANoptosis paper is a NEW SAFETY
  CONSIDERATION. Supraphysiological αKG in
  inflammatory contexts may drive PANoptosis.
  In a tumour microenvironment already showing
  elevated IFI16 (innate sensing) and inflammatory
  signals, αKG may have off-target effects.
  This does NOT invalidate the target but requires
  careful dose titration in any clinical development.
  Noted and locked 2026-03-02.

VERDICT: MECHANISTICALLY STRONG. CLINICALLY PRE-EARLY
(no clinical trial exists). Safety consideration
from 2026 AIM2 paper requires monitoring in
future preclinical development.
```

---

## DRUG 7: DICHLOROACETATE (DCA) / PDK1 INHIBITOR

```
OUR PREDICTION:
  PDK1 elevated in Q4 (CA9/SLC2A1/LDHA/PDK1
  co-expression module).
  DCA inhibits PDK1 → shifts glycolysis to OXPHOS.
  Target population: CA9-high / GLUT1-high deep PRCC
  (architectural hypoxia subpopulation).
  Locked as novel before literature check.

WHAT IS KNOWN:
  European Urology 2015 / De Gruyter 2016:
    — DCA preclinical in CCRC cell lines
      (European Urology 2015 — Prigione et al.)
    — DCA in ACHN human RCC cells: reduces
      viability, G1 arrest, apoptosis
      (De Gruyter Brill 2016)
    — These are CLEAR CELL and generic RCC
      cell lines — NOT PRCC specifically

  DCA clinical safety:
    — Several clinical trials in cancer (not RCC):
      primarily glioma, colorectal, NSCLC
    — SAFETY: reversible peripheral neuropathy
      is the main dose-limiting toxicity
    — DCA is generally tolerable at doses up to
      6.25mg/kg/day; neuropathy managed with
      thiamine supplementation
    — No DCA trial specifically in PRCC or any RCC

  DCA regulatory status:
    — Investigational only — no approved oncology use
    — Used off-label internationally (controversial)
    — The MOMENTUM protocol (multi-drug metabolic
      protocol including DCA) showing early results
      in refractory cancers — not RCC specific

  PDK1 expression profile:
    — PDK isoform expression predicts RCC outcomes
      (bioRxiv 2023 preprint, Nature Sci Reports 2023)
    — HIGH PDK1 expression correlates with BETTER
      patient survival in some RCC analyses
      (counter-intuitive — may indicate oxidative
      capacity reservation)
    — HIGH PDK2/PDK3 correlates with POOR outcomes

WHAT OUR GEOMETRY ADDS:
  1. PDK1 elevated in the CA9-co-expressing
     subpopulation of deep PRCC — specifically
     the ARCHITECTURAL HYPOXIA module.
     Prior work shows PDK1 in RCC generally.
     We identify the specific SUBPOPULATION
     (CA9-high / Q4 PRCC) where PDK1 is most
     elevated and OXPHOS restoration is most needed.

  2. DCA as COMBINATION partner:
     Restoring OXPHOS via PDK1 inhibition in
     CA9/OGDHL-low Q4 PRCC addresses both the
     architectural hypoxia problem (PDK1/DCA)
     and the TCA substrate deficit (αKG/OGDHL).
     These are different interventions at different
     points in the metabolic axis.

CONFLICT WITH LITERATURE:
  The PDK isoform data: HIGH PDK1 correlating with
  BETTER survival (not worse) is a POTENTIAL CONFLICT.
  If high PDK1 indicates preserved metabolic capacity
  that predicts better outcome, then inhibiting PDK1
  may be counter-productive.
  RESOLUTION: Our data shows PDK1 is elevated in
  the Q4 ARCHITECTURAL HYPOXIA module (co-expressed
  with CA9/SLC2A1/LDHA). This is a STRESS RESPONSE
  — cells in hypoxic pockets upregulate PDK1 to
  survive via glycolysis. The PDK1 "high = better
  prognosis" in bulk RCC may reflect a different
  population (well-oxygenated oxidative tumours)
  than our Q4 architectural-hypoxia module.
  The conflict requires resolution in Script 3:
  Does PDK1 co-elevation with CA9 (our subpopulation)
  correlate with worse prognosis than PDK1 elevation
  without CA9 co-elevation?
  FLAGGED for Script 3 OBJ analysis.

VERDICT: MECHANISTICALLY SUPPORTED, BUT PDK1
ISOFORM PROGNOSTIC DATA CREATES A CONFLICT
REQUIRING FORMAL RESOLUTION IN SCRIPT 3.
```

---

## DRUG 8: GIRENTUXIMAB (ANTI-CA9 ANTIBODY)
## AND CA9-TARGETED IMAGING/THERAPY

```
OUR PREDICTION:
  Girentuximab may work in PRCC via architectural
  hypoxia mechanism (not VHL).
  Target population: CA9-high by IHC (not VHL-mutant).
  Q4 CA9 Q4/Q1=1.167 — U-shaped distribution.

WHAT IS KNOWN:
  REDECT trial (2013):
    — Iodine-124-girentuximab PET/CT
    — Sensitivity 86%, specificity 80% for ccRCC
    — Specifically designed for CLEAR CELL RCC
    — PRCC: NOT the target — low CA9 in most PRCC

  ZIRCON Phase 3 trial (Lancet Oncology, published):
    — 89Zr-girentuximab (TLX250-CDx/Zircaix) PET/CT
    — 300 patients with indeterminate renal masses
    — Sensitivity 86%, specificity 87% for ccRCC
    — FDA BLA submitted for kidney cancer imaging
    — Designed to IDENTIFY ccRCC, not treat it
    — PRCC: NEGATIVE FINDING — most PRCC are
      CA9-LOW. Girentuximab PET is NEGATIVE in most
      PRCC, which is useful diagnostically (rules OUT
      ccRCC) but NOT a therapeutic target in most PRCC

  CA9 in PRCC:
    — AJCP 2010: CA9 is FOCAL or LOW in most PRCC
    — High CA9 in PRCC = architectural/hypoxia areas
    — The girentuximab literature treats PRCC
      as CA9-LOW by default

WHAT OUR GEOMETRY ADDS:
  1. Q4 PRCC has HIGHER CA9 than Q1/Q2/Q3
     (Q4 mean=6.302 vs Q1 mean=5.402).
     Deep PRCC has more architectural complexity
     (more papillary folding) → more hypoxic niches
     → locally elevated CA9.
     Our geometry explains WHY some PRCC cases
     are CA9-positive: they are deep-attractor
     tumours with complex architecture.

  2. CA9-high PRCC (Q4 subset) may be imageable
     with girentuximab PET.
     For Q4 deep PRCC, the ZIRCON imaging approach
     may have VALUE as a diagnostic/staging tool —
     not currently being exploited because the field
     assumes PRCC is CA9-negative.

CONFLICT WITH LITERATURE:
  The ZIRCON literature explicitly characterises
  PRCC as CA9-LOW — this is a genuine conflict
  with our Q4 finding.
  RESOLUTION: The field tested ALL PRCC (bulk).
  Our data shows CA9 is DEPTH-STRATIFIED within PRCC.
  Q4 deep PRCC (top 25%) has elevated CA9.
  The ZIRCON population average is diluted by Q1/Q2/Q3
  PRCC which are CA9-low.
  This is NOT a contradiction — it is a refinement.
  The girentuximab ADC/imaging prediction
  applies only to the CA9-high Q4 PRCC subgroup.

VERDICT: NICHE APPLICATION — Q4 CA9-HIGH PRCC ONLY.
The bulk PRCC literature correctly says CA9 is low.
Our depth stratification identifies the subgroup
where CA9 IS elevated. Clinical test: compare
girentuximab PET signal in Q4 vs Q1 PRCC using IHC
depth score as stratifier.
```

---

## DRUG 9: ANTI-CD25 / TREG DEPLETION
## (RG6292 / ALD2510 — NON-IL2-BLOCKING ANTI-CD25)

```
OUR PREDICTION:
  IL2RA (CD25) Q4/Q1=1.193 (depth-positive).
  FOXP3 flat (not significant).
  Anti-CD25/Treg depletion as Q4 immune target.
  Modest signal — prediction was weak (r=+0.125).

WHAT IS KNOWN:
  Traditional anti-CD25 (basiliximab, daclizumab):
    — BLOCKS IL-2 signalling — counterproductive
      in cancer (kills effector T cells too)
    — No oncology use — immunosuppressants
    — NOT the correct drug for Treg depletion
      in cancer

  Novel non-IL-2-blocking anti-CD25:
    RG6292 (vopikitug) — Roche:
      — Phase 1 trial in advanced solid tumours
        (alone and + atezolizumab)
      — Results: AACR Cancer Research Communications 2025
      — Acceptable safety: pruritus and rash most common
      — Treg depletion confirmed in blood and tumour
      — Clinical efficacy: only 3 partial responses
        in combination arm — INSUFFICIENT for further
        development
      — Programme NOT continuing based on these results

    ALD2510 — Aldagen:
      — JITC abstract 2021
      — Phase 1 design for solid tumours
      — Selective Treg depletion, spares effector T cells
      — Earlier stage than RG6292

  IL2RA in RCC:
    — IL2RA (CD25) expression on tumour-infiltrating
      Tregs in RCC: published as prognostic (poor)
    — No anti-CD25 trial specifically in RCC or PRCC

WHAT OUR GEOMETRY ADDS:
  1. Our IL2RA signal is WEAK (r=+0.125, p=0.034).
     Q4/Q1=1.193 — a 19% enrichment.
     This is NOT a strong immune target signal.
     The original prediction was overstated.

  2. The RG6292 clinical failure (only 3 PRs in
     combination) weakens this drug class broadly.
     The mechanism is sound but clinical efficacy
     in solid tumours is elusive so far.

REVISED PREDICTION FROM LITERATURE:
  Anti-CD25 / Treg depletion is NOT a first-priority
  target for Q4 PRCC based on:
    a) Weak IL2RA signal in our data (r=+0.125)
    b) FOXP3 is flat (actual Treg marker weak)
    c) RG6292 clinical failure in solid tumours
  Downgrade from "Q4 immune target" to
  "low priority — monitor Treg deconvolution
  in Script 3 before advancing this prediction."

CONFLICT WITH LITERATURE:
  RG6292 failure in solid tumours is a MODERATE
  CONTRA-INDICATOR for this drug class.
  The mechanism is valid but clinical translation
  has not worked in solid tumours yet.

VERDICT: DOWNGRADED. Weak geometry signal +
clinical trial failure = low priority.
Requires formal Treg deconvolution in Script 3.
```

---

## DRUG 10: MHC-I RESTORATION
## (HDAC INHIBITOR + ANTI-PD-1 COMBINATION)

```
OUR PREDICTION:
  B2M DOWN with depth (r=-0.222).
  HLA-A DOWN with depth (r=-0.237).
  IFI16 UP with depth (r=+0.165).
  Q4 deep PRCC: T cells PRESENT but BLIND
  (MHC-I down, PD-L1 down, IFI16 active).
  Anti-PD-L1 and anti-TIM-3 are WRONG for Q4.
  MHC-I restoration is the CORRECT Q4 immune target.
  Drug class: HDAC inhibitor (entinostat) + anti-PD-1.

WHAT IS KNOWN:
  HDAC inhibitors and MHC-I upregulation:
    — OBP-801 (novel HDAC inhibitor):
      MDPI Cancers 2024 — promotes MHC-I
      expression and anti-PD-1 synergy in ccRCC.
      PRECLINICAL IN ccRCC.
    — Entinostat (class I HDACi):
      JITC 2021 — NHS-IL12 + entinostat
      overcomes anti-PD-1 resistance in MHC-I-
      deficient murine models.
      This is THE EXACT MECHANISM we predicted.
    — Entinostat is FDA Breakthrough-designated in
      breast cancer (HR+) — ESTABLISHED DRUG.
    — Multiple HDAC inhibitor trials ongoing in
      solid tumours for immune sensitisation.

  B2M / MHC-I loss in RCC:
    — ScienceDirect 2021: B2M in cancer immunotherapy
      — loss documented in multiple solid tumours
      including RCC
    — Nature Reviews 2023: antigen presentation
      in cancer — mechanisms and clinical implications
      — B2M loss as a resistance mechanism confirmed

  Clinical trials of HDAC + immunotherapy in RCC:
    — Entinostat + nivolumab: ongoing trials
      in advanced RCC (several open studies)
    — Results: mixed, but signals in some studies
    — NOT PRCC-specific — all ccRCC or mixed RCC

WHAT OUR GEOMETRY ADDS:
  1. DEPTH STRATIFICATION: MHC-I restoration is
     specifically a Q4 intervention.
     Q1/Q2 PRCC has intact MHC-I (B2M/HLA-A normal)
     and TIM-3+ T cells (checkpoint therapy target).
     Q4 PRCC has MHC-I DOWN + T cells present.
     This depth-stratified prescription is NOT
     in any published PRCC paper.

  2. The IFI16-B2M decoupling:
     IFI16 (innate DNA sensor) UP in Q4
     but B2M DOWN in Q4.
     The innate sensing circuit is firing but
     the adaptive output (antigen presentation)
     is silenced.
     HDAC inhibition would restore B2M/HLA-A
     expression and link innate sensing back
     to adaptive killing.
     This specific mechanism (IFI16 active +
     B2M silenced + HDACi restores coupling)
     is NOT described in any prior PRCC paper.

  3. STING agonists are COUNTER-INDICATED in Q4:
     IFI16 is already firing. Adding a STING
     agonist to a maximally active innate circuit
     would not help — it might increase inflammatory
     toxicity without therapeutic benefit.
     The correct intervention is DOWNSTREAM of
     IFI16: restore B2M so the signal reaches
     MHC-I.

CONFLICT WITH LITERATURE:
  No conflict. The HDAC + anti-PD-1 trials in RCC
  provide indirect support. The OBP-801 ccRCC
  preclinical paper directly supports the mechanism.

VERDICT: STRONGLY SUPPORTED BY MECHANISM AND
PRECLINICAL DATA. No PRCC-specific trial exists.
The entinostat + anti-PD-1 approach in MHC-I-low
Q4 PRCC is a clinically actionable prediction
that could be incorporated into an existing
entinostat + nivolumab trial as a biomarker
stratification arm.
```

---

## DRUG 11: ANTI-CSF1R / M2 MACROPHAGE REPOLARISATION

```
OUR PREDICTION:
  ARG1 Q4/Q1=1.748 (M2 macrophage enrichment in Q4).
  N-S2-5 locked as novel finding.
  Anti-CSF1R or anti-IL-4/IL-13 as Q4 immune target.
  REQUIRES SCRIPT 3 DECONVOLUTION TO CONFIRM.

WHAT IS KNOWN:
  CSF1R inhibitors in RCC:
    — pexidartinib (FDA-approved for TGCT, not RCC)
    — sotuletinib (preclinical in RCC models)
    — iScience 2025: "Targeting the IL34-CSF1R axis
      improves metastatic renal cell carcinoma" —
      PUBLISHED preclinical evidence in RCC
      CSF1R inhibition → reduces M2-like TAMs,
      reduces tumour growth in mouse models

    — Important finding (JITC 2021):
      CSF1R inhibitor ALONE in RCC mice had
      limited effect. But CSF1R inhibitor +
      anti-PD-1 combination: DEPLETING TAMs
      ABOLISHED the anti-PD-1 response
      (because TAMs were doing the antigen
      presenting for PD-1 blockade).
      This is a CRITICAL CONFLICT for our prediction:
      eliminating M2 macrophages may ALSO eliminate
      the antigen presenting cells needed for
      checkpoint therapy to work.

    — Lenvatinib/cabozantinib: macrophage-modulating
      activity. These TKIs already modulate TAM
      phenotype and are standard of care in RCC.

  ARG1 in RCC:
    — ARG1 expression in RCC tumour microenvironment:
      PUBLISHED (myeloid suppression marker)
    — High ARG1 in RCC correlates with worse outcomes
      (multiple publications)
    — Anti-ARG1 approaches: not yet in clinical trials
      for solid tumours

WHAT OUR GEOMETRY ADDS:
  1. ARG1 is HIGHEST in Q4 PRCC (Q4/Q1=1.748).
     The M2 enrichment is DEPTH-DEPENDENT —
     deepest PRCC has the most suppressive
     macrophage microenvironment.
     Prior RCC literature notes ARG1 in bulk RCC
     without depth stratification.

CRITICAL CONFLICT — LENVATINIB PRECLINICAL DATA:
  The Vuong et al. (Oncologist 2024) preclinical data:
  In mouse RCC models, TAM depletion via CSF1R
  inhibition ABOLISHED anti-PD-1 response.
  This means: in RCC, TAMs are required for
  anti-PD-1 to work (they present antigens to T cells).
  If we deplete M2 macrophages in Q4 PRCC, we
  may simultaneously remove the antigen-presenting
  cells needed for any immune therapy to function.
  This is a significant complication for the M2
  depletion prediction.

  REVISED MODEL:
  Anti-CSF1R / M2 depletion in Q4 PRCC is not
  straightforward. The correct approach may be
  REPOLARISATION (M2→M1) rather than DEPLETION.
  Lenvatinib's macrophage-modulating effect
  (which repolarises rather than depletes) may be
  more appropriate than pure CSF1R inhibition.
  Current SOC (cabozantinib, lenvatinib + IO) may
  already partially address this via macrophage
  repolarisation as a secondary mechanism.
  The ARG1 Q4 finding supports the value of
  macrophage-targeting TKIs (lenvatinib/cabozantinib)
  as preferred agents in Q4 rather than pure
  CSF1R inhibitors.

VERDICT: ARG1 FINDING IS REAL AND NOVEL.
Drug strategy requires REVISION from "anti-CSF1R
depletion" to "macrophage REPOLARISATION"
(lenvatinib/cabozantinib + IO rationale for Q4).
Anti-CSF1R depletion may worsen outcome in Q4 if
TAMs are antigen-presenting. LOCKED REVISION
2026-03-02.
```

---

## CONSOLIDATED DRUG MAP — REVISED

```
DEPTH STRATUM | PRIORITY DRUGS        | MECHANISM          | CLINICAL STATUS
──────────────────────────────────────────────────────────────────────────────
Q1 (shallow)  | Savolitinib           | Identity disrupt   | Phase 3 (SAVOIR)
              | CDK4/6i               | Stress bypass      | No PRCC trial
              | Anti-TIM-3 / anti-PD1 | TIM-3+ TIL active  | PRCC-eligible trials
              |                       | MHC-I intact       |

Q2/Q3 (mid)   | Savolitinib           | Identity disrupt   | Phase 3 (SAVOIR)
              | Tazemetostat          | EZH2 chromatin lock| No PRCC trial
              | KDM1A inhibitor       | H3K4me restoration | No RCC trial
              | αKG supplementation   | TET2 rescue        | No cancer trial

Q4 (deepest)  | ERBB2-targeted        | Identity co-driver | Basket trial
              | Tazemetostat + αKG    | TCA-chromatin lock | No combination trial
              | KDM1A inhibitor       | Chromatin dual lock| No RCC trial
              | Entinostat + anti-PD1 | MHC-I restoration  | RCC trials ongoing
              | Lenvatinib/cabozanib  | M2 repolarisation  | Standard of care
              | NOT anti-PD-L1        | PDL1 low           | CONTRA-INDICATED
              | NOT anti-TIM-3        | TIM-3 low          | CONTRA-INDICATED
              | NOT belzutifan        | EPAS1 flat         | CONTRA-INDICATED
              | NOT CSF1R depletion   | Abolishes IO resp  | CONTRA-INDICATED
              | NOT STING agonist     | IFI16 already on   | CONTRA-INDICATED

ALL DEPTHS    | Savolitinib           | Identity maint.    | Phase 3 support
              | NOT CDK4/6i mono      | 0% ORR in RCC mono | Contra-indicat solo

DRUGS WITH CONTRA-INDICATIONS FROM GEOMETRY (5):
  1. Anti-PD-L1  (pembrolizumab, atezolizumab):
     PD-L1 Q4/Q1=0.795 — falls with depth.
     Contra-indicated in Q4. May be active Q1/Q2.

  2. Anti-TIM-3 (cobolimab, sabatolimab):
     TIM-3 Q4/Q1=0.842 — falls with depth.
     Contra-indicated in Q4. May be active Q1/Q2.

  3. Belzutifan (HIF2A inhibitor):
     EPAS1 flat (Q4/Q1=0.990) — not a target.
     Contra-indicated in ALL PRCC depth strata.

  4. CSF1R depletion (pexidartinib):
     Depleting TAMs abolishes anti-PD-1 response
     in RCC preclinical models.
     Contra-indicated as DEPLETION strategy.
     (Repolarisation via lenvatinib/cabozantinib
     is the alternative.)

  5. STING agonist:
     IFI16 already firing in Q4.
     Adding STING agonist = overdrive on active
     innate circuit without adaptive output.
     Contra-indicated in Q4.
```

---

## SUMMARY TABLE — ALL 11 DRUGS

```
Drug                  Our Prediction   Prior Evidence   Conflict  Priority
─────────────────────────────────────────────────────────────────────────────
1. Tazemetostat       Q3/Q4 EZH2i      Preclinical only  None     HIGH
   (EZH2i)            depth-strat.     No PRCC trial

2. Savolitinib        Identity         SAVOIR 27% ORR    None     HIGH
   (MET)              not mitogen      Phase 3 support            CONFIRMED

3. ERBB2-targeted     Identity         BTC data (HERB)   None     HIGH
   (tucatinib+tras)   co-driver        No PRCC trial              NOVEL

4. CDK4/6i            Q1/Q2 paradox    0% ORR ccRCC mono Weak     MEDIUM
   (abemaciclib)      not mono         No PRCC trial    (ccRCC)

5. KDM1A inhibitor    Q3/Q4 chromatin  Preclinical only  None     MEDIUM
   (iadademstat)      dual lock        No RCC trial

6. αKG/DMKG           FH-low selector  Preclinical only  Partial  MEDIUM
                      TET2 rescue      No cancer trial   (safety)

7. DCA/PDK1i          CA9-high module  Preclinical RCC   Partial  MEDIUM
                      OXPHOS restore   No PRCC trial     (PDK1 i)

8. Girentuximab       Q4 CA9-high      ccRCC only        Partial  LOW-MED
   (anti-CA9)         subgroup only    PRCC "low CA9"   (resolved)

9. Anti-CD25 Treg     Weak Q4 signal   RG6292 failed     YES      LOW
   (RG6292/ALD2510)   IL2RA +0.125    solid tumours     (trials) DOWNGRADED

10. HDAC + anti-PD1   MHC-I restore    OBP-801 ccRCC     None     HIGH
    (entinostat)      Q4 B2M down      Entinostat trials          NOVEL

11. Anti-CSF1R        ARG1 M2 Q4       CSF1Ri abolishes  REVISED  MEDIUM
    (REVISED to       REPOLARISE       anti-PD1 in RCC            (revised
    macrophage        not DEPLETE      iScience 2025              to repol)
    repolarisation)
```

---

## FRAMEWORK CORRECTIONS FOR SCRIPT 3 — DRUG-SPECIFIC

```
DC-1: ANTI-CD25 / TREG TARGET DOWNGRADED
  IL2RA r=+0.125, FOXP3 flat, RG6292 clinical failure.
  Remove anti-CD25 as a primary Q4 target.
  Replace with: formal Treg deconvolution in Script 3.
  If deconvolution confirms Treg enrichment in Q4,
  revisit using ALD2510 (more selective than RG6292).

DC-2: CSF1R DEPLETION REPLACED BY REPOLARISATION
  Anti-CSF1R depletion abolishes anti-PD-1 response
  in RCC preclinical models (Vuong et al. 2024).
  REVISE Q4 immune target from "anti-CSF1R" to:
    Lenvatinib or cabozantinib as macrophage
    REPOLARISATION agents (M2→M1) in Q4.
    These are already in clinical use for PRCC
    and their macrophage effect supports our
    ARG1 Q4 finding without the depletion problem.

DC-3: PDK1/DCA CONFLICT FLAGGED
  PDK1 high = better prognosis in some RCC analyses.
  CA9-co-elevated PDK1 may be a different
  subpopulation than the bulk PDK1-high RCC.
  Script 3 OBJ: test whether PDK1/CA9 co-high PRCC
  has WORSE prognosis than PDK1-high/CA9-low PRCC.
  This resolves whether the architectural-hypoxia
  PDK1 population is the correct DCA target.

DC-4: ERBB2 BIOMARKER CORRECTION
  Current basket trials use FISH amplification
  or NGS mutation as eligibility criterion.
  Our prediction: ERBB2 IHC 2+ (WITHOUT FISH) is
  the correct biomarker for PRCC biliary identity
  co-expression.
  Basis: BTC (ICC) literature shows HER2 IHC 2+
  without amplification has activity (HERB trial).
  Clinical trial design correction: ERBB2 IHC 2+
  should be the PRCC eligibility criterion,
  NOT FISH amplification or NGS mutation.
  This is a direct and actionable correction
  for any future PRCC HER2-targeted trial design.

DC-5: αKG SAFETY MONITORING
  2026 paper: supraphysiological αKG activates
  AIM2/PANoptosis in inflammatory contexts.
  Any αKG + tazemetostat combination trial must
  include AIM2 and inflammatory panel monitoring
  (IL-18, GSDMD, caspase-1 activation) as safety
  endpoints alongside the epigenetic efficacy endpoints.
```

---

## STATUS BLOCK

```
document:           95-DLC (drug literature check)
date:               2026-03-02
author:             Eric Robert Lawson
                    OrganismCore

drugs_checked:      11/11 ✓
highest_priority:   Tazemetostat (EZH2i, no PRCC trial)
                    Savolitinib  (SAVOIR support confirmed)
                    ERBB2-targeted (BTC data, novel mechanism)
                    Entinostat+anti-PD1 (MHC-I Q4 target)

drugs_downgraded:   Anti-CD25 / Treg (weak signal + trial fail)
drugs_revised:      Anti-CSF1R → macrophage repolarisation
                    (lenvatinib/cabozantinib)

drugs_contra-ind:   Anti-PD-L1 in Q4
                    Anti-TIM-3 in Q4
                    Belzutifan (all PRCC)
                    CSF1R depletion
                    STING agonist in Q4

conflicts_flagged:
  PDK1 isoform prognosis vs DCA target (Script 3)
  ARG1 depletion vs repolarisation (resolved → repol)
  Anti-CD25 clinical failure (downgraded)

framework_corrections: 5 (DC-1 through DC-5)

ready_for_script_3: YES ✓
protocol_status:    FULLY COMPLIANT ✓

next:               Document 95c | Script 3
                    Lock S3 predictions before writing
```
