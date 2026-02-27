# IMPC VECTOR — ACTIVE TODO
## ELF-Thigmotaxis Observational
## Program
## Last updated: February 27, 2026

---

## WHERE YOU ARE IN THE IMPC
## VECTOR

### What Is Complete

The DR23 primary analysis produced
a significant cross-sectional
correlation between facility-level
ELF score and wildtype C57BL/6N
thigmotaxis across seven
international phenotyping centers:

```
Spearman r = -0.775
p = 0.0408
N = 7 centers
```

The EUMODIC replication analysis
is complete across seven scripts
and six reasoning artifacts. The
primary pre-registered analysis
produced a null result in periphery
permanence time (floor effect).
The reanalysis on sensitive measures
produced a partial signal. The HMGU
temporal shift hypothesis — that
HMGU's behavioral reversal between
2006-2011 and 2015-2024 is explained
by a facility ELF increase driven
by GMCII construction (completed
2017) — is documented, timestamped,
and supported by back-calculation:

```
Back-calculated HMGU ELF
(EUMODIC period): ~19
DR23 ELF:          65
Implied delta:     +46 units
Counterfactual r
(latency, HMGU corrected): +0.600
```

### What Is Pending

Five active threads:
  1. GMC email — sent, awaiting
     response
  2. DR24 — awaiting EBI release
  3. JAX — awaiting response
  4. Bundesnetzagentur search —
     not started
  5. Faraday cage — pre-registered,
     IACUC not submitted

---

## THREAD 1 — GMC EMAIL
## HMGU TEMPORAL HYPOTHESIS

**Status: Email sent February 27,
2026. Awaiting response.**

### What You Asked

Email sent to:
  info@mouseclinic.de
  CC: martin.hrabe-de-angelis
      @helmholtz-munich.de

Three questions:
  1. Was the open field testing
     room the same physical location
     for EUMODIC (2006-2011) and
     DR23 (2015-2024)?

  2. Did GMCII construction or
     occupation affect the electrical
     infrastructure of the existing
     GMC I animal facility or
     behavioral testing rooms?

  3. Have any ambient ELF
     measurements been conducted
     in the behavioral testing rooms?

### Decision Tree on Response

**If testing room moved to GMCII
OR electrical infrastructure
confirmed changed:**

  → Write EUMODIC_doc7_hmgu_
    confirmed.md

  → EUMODIC assessment upgrades
    from partial to full replication:

    "Cross-sectional replication
    in four centers. Longitudinal
    blind validation at HMGU —
    undesigned natural experiment
    confirming directional
    prediction."

  → Update evidence chain in
    IMPC_TODO.md and TODO.md

  → Begin drafting manuscript
    methods section

**If ELF measurements provided:**

  → Add to EUMODIC_doc7
  → If HMGU ELF in testing room
    today >> HMGU ELF pre-2011
    estimate, hypothesis confirmed
    quantitatively

**If GMC team cannot confirm
or does not respond by
March 14, 2026:**

  → Document non-confirmation
    honestly in EUMODIC_doc7
  → Hypothesis remains unconfirmed
  → DR23 primary result unaffected
  → Program continues to DR24
    and Faraday cage

### Follow-Up Schedule

  March 7, 2026:
    If no response, send one
    polite follow-up to
    info@mouseclinic.de

  March 14, 2026:
    If still no response,
    document as non-response.
    Close GMC thread.
    Hypothesis remains open.

---

## THREAD 2 — DR24
## IMPC DATA RELEASE EXTENSION

**Status: Awaiting EBI release.
Imminent as of February 27, 2026
per Robert Wilson confirmation.**

Contact: mouse-informatics@ebi.ac.uk

### Why DR24 Matters

DR24 uses procedure IMPC_OFD_001 —
the same procedure as DR23. No
floor effect problem. No ESLIM
vs IMPC procedure mismatch.

DR24 may include:
  - New centers not in DR23
    (each new center with
    assignable ELF extends N)
  - Additional wildtype records
    for existing centers
    (increases per-center n,
    tightens medians)
  - Updated data for centers
    already in DR23

### Pre-Analysis Steps
### (Must be done in this order)

**Step 1 — Check DR24 release:**
  Monitor IMPC portal:
  mousephenotype.org
  When DR24 appears, proceed
  immediately to Step 2.

**Step 2 — Identify new centers:**
  Query IMPC_OFD_001 for all
  phenotyping centers with
  wildtype C57BL/6N data.
  Compare to DR23 center list.
  Identify any new centers.

**Step 3 — Assign ELF scores
  BEFORE querying behavior:**
  For any new centers:
    Assign ELF scores blind —
    based on facility location,
    building type, HV proximity —
    before examining behavioral
    medians.
  Document in DR24_doc1_pre_
  analysis.md with timestamp.
  Commit to repository BEFORE
  running behavioral query.

  This step is non-negotiable.
  ELF scores must precede
  behavioral data inspection.

**Step 4 — Query behavioral data:**
  Run DR24 equivalent of
  eumodic_query.py against
  IMPC_OFD_001.
  Parameter: IMPC_OFD_010_001
  (same as DR23 primary parameter)
  Strain: C57BL/6N strict

**Step 5 — Run correlation:**
  Spearman ELF vs thigmotaxis
  across all available centers.
  Include DR23 centers for
  updated data check.
  Report LOO sensitivity.
  Report predicted vs observed
  rank order.

**Step 6 — Write results document:**
  DR24_doc2_results.md

### What to Watch For

  New center with assignable ELF
  and behavioral data:
    → Extends gradient
    → Each new center increases
       power of Spearman test
    → N=8+ starts to become
       a robust result

  Existing centers with more data:
    → Tighter median estimates
    → Reduced noise in correlation

  Any center with known ELF change:
    → Flag for temporal analysis
       (same as HMGU)

---

## THREAD 3 — JAX DATA
## KOMP2 INQUIRY

**Status: Case 03428362 open.
Awaiting substantive response.**

### What Was Requested

JAX KOMP2 open field wildtype
C57BL/6N data under
IMPC_OFD_001 or equivalent
procedure.

JAX facilities:
  - Well-documented electrical
    infrastructure
  - Rural Maine campus
  - Low expected ELF
  - High-quality inbred colonies
    from cryopreserved stock

### Action Required

**If no response by
February 28, 2026 COB:**

  Email directly:
  komp@jax.org

  Subject: KOMP2 open field
  wildtype data access inquiry
  (Case 03428362 follow-up)

  Reference case number.
  Ask for direct contact with
  data team.

### What JAX Data Would Add

JAX ELF estimate: likely 20-30
(rural, purpose-built, no
adjacent HV infrastructure,
active EM management for
genetics research)

If JAX data confirms low
thigmotaxis at low ELF:
  → Adds anchor at low end
     of gradient
  → Extends DR23 N from 7
     to 8 centers
  → Strengthens Spearman r

If JAX data contradicts:
  → Document honestly
  → Investigate JAX-specific
     confounds

---

## THREAD 4 — BUNDESNETZAGENTUR
## GRID INFRASTRUCTURE SEARCH

**Status: Not started.**

### What This Tests

The HMGU temporal hypothesis
proposes that Germany's grid
expansion (Energiewende,
2010-2020) contributed to
elevated ELF at the Neuherberg
campus in the DR23 period
relative to the EUMODIC period.

This is a secondary test
independent of the GMC team
response. It tests whether
new HV infrastructure was
approved or built near
Neuherberg during the relevant
interval.

### How to Search

**Bundesnetzagentur:**
  bundesnetzagentur.de
  → Energy → Electricity
  → Network development plan
  → Search for projects in
    Bayern / Munich / Neuherberg

**TenneT TSO:**
  tennet.eu
  → Grid projects → Germany
  → Search Munich region
  → Filter 2010-2020

**Amprion:**
  amprion.net
  → Grid development
  → Project map
  → Munich / Upper Bavaria region

### What to Record

  Any new 220kV or 380kV line
  within 5km of Neuherberg:
    → Document route, completion
       date, operator
    → Add to EUMODIC_doc5 as
       additional evidence

  Any new substation within
  2km of HMGU campus:
    → High-value evidence
    → Document in
       EUMODIC_doc5 update

  No new infrastructure found:
    → Document as negative result
    → Grid expansion hypothesis
       not supported locally
    → GMCII hypothesis remains
       primary candidate

---

## THREAD 5 — FARADAY CAGE
## CAUSAL EXPERIMENT

**Status: Pre-registered.
Design complete.
IACUC not yet submitted.**

### Why This Is the Anchor

All observational results —
DR23, EUMODIC, DR24, JAX —
are correlational. They cannot
establish causation. Unmeasured
confounders cannot be fully
excluded from cross-facility
data.

The Faraday cage experiment
is the only test that can
establish whether ELF causes
the thigmotaxis change by
directly manipulating ELF
exposure in a controlled
setting.

**This experiment proceeds
regardless of any observational
outcome.** A significant DR24
result does not replace it.
A null GMC response does not
cancel it. It is the causal
anchor of the entire vector.

### Design Summary

  Species: Mus musculus
           C57BL/6N wildtype
  Condition A: Standard housing
               ambient ELF
  Condition B: Faraday cage
               housing, ELF
               attenuated
  Test: Open field
        IMPC_OFD_001 equivalent
        protocol
  Primary measure: Thigmotaxis
  Primary prediction:
    Mice in Faraday cage (lower
    ELF) show lower thigmotaxis
    than standard housing mice

### What Is Needed to Proceed

**☐ Facility identification:**
  Need a facility willing to
  host the experiment with:
  - Standard SPF animal housing
  - Space for Faraday cage
    installation
  - Open field testing equipment
  - IACUC oversight

  Candidate approach:
  Contact academic institutions
  with behavioral neuroscience
  facilities and existing
  IACUC infrastructure.

**☐ PI sponsor:**
  An IACUC-registered PI must
  sponsor the protocol submission.
  This is the primary bottleneck.
  Without an affiliated PI,
  IACUC submission is not possible
  as an independent researcher.

  Approach: identify a behavioral
  neuroscience or animal facility
  PI who has reviewed the DR23
  result and is willing to
  sponsor or collaborate.

**☐ IACUC protocol draft:**
  Once facility and PI are
  identified, draft the IACUC
  protocol. The pre-registered
  design document provides the
  scientific justification.

**☐ Faraday cage specification:**
  Identify a commercial or
  custom Faraday cage supplier
  capable of producing an
  enclosure suitable for
  standard mouse housing racks.
  Must attenuate 50-60 Hz ELF
  to below detectable levels
  within the housing space.

### Timeline Target

  Q2 2026: Facility and PI
    identified
  Q3 2026: IACUC submitted
  Q4 2026: Experiment running

---

## CURRENT EVIDENCE CHAIN

```
DR23 primary
  r = -0.775
  p = 0.0408
  N = 7 centers
  Status: SIGNIFICANT ✅

DR23 multi-procedure
  Fear conditioning: consistent
  PPI: non-linear
  Status: CONSISTENT ✅

EUMODIC cross-sectional
  Primary (peri time): NULL
  Sensitive measures: PARTIAL
  4/5 centers predicted direction
  Status: PARTIAL ✅⚠️

HMGU longitudinal hypothesis
  Back-calc ELF ~19 (EUMODIC)
  vs 65 (DR23)
  Delta +46 units
  GMCII completed 2017
  Counterfactual r = +0.600
  Status: HYPOTHESIS —
  PENDING GMC CONFIRMATION ⏳

DR24 extension
  Status: PENDING RELEASE ⏳

JAX data
  Status: PENDING RESPONSE ⏳

Bundesnetzagentur search
  Status: NOT STARTED ☐

Faraday cage
  Status: PRE-REGISTERED
  FACILITY/PI NEEDED ☐
```

---

## DOCUMENTS TO WRITE NEXT

```
On GMC confirmation:
  EUMODIC_doc7_hmgu_confirmed.md

On DR24 release:
  DR24_doc1_pre_analysis.md
    (ELF scores BEFORE data)
  DR24_doc2_results.md
    (after correlation runs)

On Bundesnetzagentur search:
  Update EUMODIC_doc5_hmgu_
  temporal_hypothesis.md
  with findings

On Faraday cage PI identified:
  Faraday_doc1_iacuc_prep.md
```

---

## CONTACTS

```
EBI Mouse Informatics:
  mouse-informatics@ebi.ac.uk
  Robert Wilson (confirmed
  February 27, 2026)

German Mouse Clinic (GMC):
  info@mouseclinic.de
  CC: martin.hrabe-de-angelis
      @helmholtz-munich.de
  Email sent: February 27, 2026

JAX KOMP2:
  Via portal case 03428362
  Direct: komp@jax.org
  (if no response by Feb 28)
```

---

## VERSION

- v1.0 — February 27, 2026
  Created after EUMODIC phase
  closure.
  Five active threads documented.
  Evidence chain current.
  Faraday cage bottleneck
  (facility + PI) identified
  as primary long-lead item.
