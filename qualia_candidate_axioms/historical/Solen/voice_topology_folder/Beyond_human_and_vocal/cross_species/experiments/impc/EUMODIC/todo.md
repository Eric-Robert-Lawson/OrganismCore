# ORGANISMCORE — ACTIVE TODO
## Current position and next actions
## Last updated: February 27, 2026

---

## WHERE YOU ARE

The EUMODIC analysis phase is
complete. Six reasoning artifacts
and seven scripts are committed
to the repository. The folder
contains a full audit trail from
pre-registration through a
quantitative blind validation
hypothesis.

The key finding is the HMGU
temporal shift — mice at HMGU
were highly exploratory in the
EUMODIC period (2006-2011) and
highly thigmotactic in the DR23
period (2015-2024). This is
consistent with a facility ELF
increase driven by GMCII
construction (completed 2017).
The hypothesis is documented and
timestamped before any external
confirmation was sought.

---

## IMMEDIATE ACTIONS

### ☐ 1. Send GMC Email
**Priority: HIGHEST**
**Status: Email drafted, not sent**

Send the email to:
  info@mouseclinic.de
  CC: martin.hrabe-de-angelis
      @helmholtz-munich.de

Three specific questions:
  1. Was testing room the same
     location in both collection
     periods?
  2. Did GMCII construction affect
     electrical infrastructure of
     existing GMC I rooms?
  3. Have any ELF measurements been
     conducted in the behavioral
     testing rooms?

If confirmed → write
  EUMODIC_doc7_hmgu_confirmed.md

If not confirmed or no response →
  document honestly, hypothesis
  remains unconfirmed, program
  continues regardless.

---

### ☐ 2. DR24 Query
**Priority: HIGH**
**Status: Waiting on EBI release**

Robert Wilson (EBI) confirmed
DR24 releases within days of
February 27, 2026.

When DR24 releases:
  - Run DR24 equivalent of
    eumodic_query.py against
    IMPC_OFD_001 (same procedure
    as DR23, no floor effect)
  - Extend the DR23 center set
    with any new IMPC centers
  - Run Spearman correlation
    with ELF scores
  - If new centers: assign ELF
    scores blind before querying
    behavioral data

Contact: mouse-informatics@ebi.ac.uk
  Robert Wilson confirmed access.

---

### ☐ 3. Sea Turtle — Send Data
###    Request Emails
**Priority: HIGH**
**Status: Pre-registered, emails
  not yet sent**

Pre-registration is complete on
GitHub. No data requests have
been sent yet.

Send to:
  FWC (Florida Fish and Wildlife
  Conservation Commission):
    Request Caretta caretta
    nesting data — natal beach
    cohort spread and return rates

  NOAA (National Oceanic and
  Atmospheric Administration):
    Request loggerhead stranding
    data — geographic distribution
    relative to AM broadcast and
    submarine cable infrastructure

Draft both emails. They can be
sent simultaneously.

---

## THIS WEEK

### ☐ 4. JAX Follow-Up
**Status: Inquiry open,
  case 03428362**

If no substantive response from
JAX customer services by end of
business February 28, contact
directly:
  komp@jax.org

JAX data would add one high-
quality anchor point to the DR23
analysis. JAX facilities have
well-documented electrical
infrastructure.

---

### ☐ 5. Bundesnetzagentur Search
**Status: Not started**

Search public records for new
high-voltage infrastructure near
Neuherberg between 2010 and 2020.

TenneT and Amprion publish project
documentation for approved and
completed grid expansion projects.

URL: netzentwicklungsplan.de
     bundesnetzagentur.de

This is a secondary test of the
HMGU temporal hypothesis —
independent of the GMC team
response.

---

## ONGOING — NO DEADLINE

### ☐ 6. Monarch Watch Response
**Status: Waiting**

Recovery data request sent and
acknowledged. No action needed
until response arrives. Do not
follow up yet.

---

### ☐ 7. Faraday Cage Experiment
**Status: Pre-registered,
  design complete**

The causal anchor of the entire
IMPC vector. Does not depend on
any observational result.

Next steps when ready:
  - Identify facility willing to
    host the experiment
  - Identify IACUC-registered PI
    to sponsor submission
  - Submit IACUC protocol

This is not time-critical right
now — observational program is
still active. But it should not
be delayed past DR24 results.

---

## EVIDENCE CHAIN AS IT STANDS
## (February 27, 2026)

```
DR23 cross-sectional
  r = -0.775, p = 0.04, N=7
  Status: SIGNIFICANT ✅

DR23 multi-procedure extension
  Fear conditioning: consistent
  PPI: non-linear
  Status: CONSISTENT ✅

EUMODIC cross-sectional
  4/5 centers predicted direction
  on sensitive measures
  Status: PARTIAL ✅

HMGU longitudinal hypothesis
  Behavioral shift consistent
  with GMCII construction
  Back-calc ELF ~19 in EUMODIC
  vs 65 in DR23
  Status: HYPOTHESIS PENDING
  GMC CONFIRMATION ⏳

DR24 extension
  Status: PENDING RELEASE ⏳

JAX data
  Status: PENDING RESPONSE ⏳

Monarch butterfly
  Rayleigh p=0.000517
  Mean bearing 218.9° SW
  Status: SIGNIFICANT ✅
  Recovery data pending ⏳

Sea turtle
  Status: PRE-REGISTERED
  Data requests not sent ☐

Faraday cage
  Status: PRE-REGISTERED
  IACUC not yet submitted ☐
```

---

## FILES IN EUMODIC FOLDER

```
Reasoning artifacts:
  EUMODIC_README.md
  EUMODIC_doc1_pre_analysis.md
  EUMODIC_doc2_results.md
  EUMODIC_doc3_protocol_audit.md
  EUMODIC_doc4_final.md
  EUMODIC_doc5_hmgu_temporal_
    hypothesis.md
  EUMODIC_doc6_temporal_
    calculation.md

Scripts (in execution order):
  eumodic_query.py
  eumodic_diagnose.py
  eumodic_strain_audit.py
  eumodic_elf_assignment.py
  eumodic_correlation.py
  eumodic_protocol_audit.py
  eumodic_reanalysis.py
  eumodic_hmgu_temporal_analysis.py

Local data outputs (not in repo):
  eumodic_raw.csv
  eumodic_strain_decision.csv
  eumodic_elf_scores.csv
  eumodic_center_summary.csv
  eumodic_protocol_audit.csv
  eumodic_reanalysis_summary.csv
  eumodic_hmgu_temporal_analysis.csv

Local figures (not in repo):
  eumodic_correlation.png
  eumodic_reanalysis.png
  eumodic_hmgu_temporal_analysis.png

Local logs (not in repo):
  eumodic_centers.txt
  eumodic_strain_audit.txt
  eumodic_elf_assignment.txt
  eumodic_correlation_results.txt
  eumodic_protocol_audit.txt
  eumodic_reanalysis_results.txt
  eumodic_hmgu_temporal_analysis.txt
```

---

## NEXT DOCUMENT TO WRITE

**If GMC confirms:**
  EUMODIC_doc7_hmgu_confirmed.md
  — Update hypothesis to confirmed
  — Revise EUMODIC assessment from
    partial to full replication

**If DR24 releases:**
  DR24_doc1_pre_analysis.md
  — Pre-register ELF scores before
    querying behavioral data
  — Same structure as EUMODIC_doc1

**When sea turtle data arrives:**
  sea_turtle_doc1_pre_analysis.md
  — Pre-register analysis plan
    before examining data

---

## VERSION

- v1.0 — February 27, 2026
  Created after EUMODIC phase
  closure and GMC email draft.
  All EUMODIC scripts complete.
  Six reasoning artifacts committed.
  Three immediate actions pending.
