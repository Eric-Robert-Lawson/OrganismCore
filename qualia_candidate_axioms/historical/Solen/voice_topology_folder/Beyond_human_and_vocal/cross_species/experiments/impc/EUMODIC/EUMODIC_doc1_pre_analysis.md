# EUMODIC OPEN FIELD REPLICATION
# ANALYSIS — PRE-ANALYSIS RECORD
## Independent Cross-Dataset Validation
## of the ELF-Thigmotaxis Correlation
## IMPC Series — Document 4
## OrganismCore Cross-Species
## Communication Series
## qualia_candidate_axioms/historical/
## Solen/voice_topology_folder/
## Beyond_human_and_vocal/cross_species/
## experiments/impc/EUMODIC/
## February 27, 2026

---

## ARTIFACT METADATA

- **Series:** IMPC Spatial Navigation
  Analysis
- **Document number:** IMPC Document 4
- **Status:** Pre-analysis record —
  written before correlation script
  was run
- **Depends on:**
  - IMPC_Spatial_Navigation_Analysis.md
    (Document 1)
  - impc_spatial_navigation_doc2.md
    (Document 2)
  - impc_spatial_navigation_doc3.md
    (Document 3)
  - EUMODIC_README.md
    (folder pre-registration record)
- **Scripts run prior to this document:**
  - eumodic_query.py ✅
  - eumodic_diagnose.py ✅
  - eumodic_strain_audit.py ✅
  - eumodic_elf_assignment.py ✅
- **Script not yet run:**
  - eumodic_correlation.py ⏳
- **Pre-registration:** GitHub —
  Eric-Robert-Lawson/OrganismCore
- **Data source:** EMBL-EBI IMPC SOLR API
- **Procedure:** ESLIM_007_001
  (EUMODIC Pipeline 2 Open Field)
- **License:** CC-BY 4.0
- **Contact who provided data access:**
  Robert Wilson, EMBL-EBI Mouse
  Informatics Team
  mouse-informatics@ebi.ac.uk

---

## PART I: WHAT HAS BEEN
## ESTABLISHED — THE CHAIN
## LEADING HERE

### 1.1 The DR23 Primary Result

The IMPC DR23 analysis (Documents 1-3)
identified a significant negative
correlation between facility-level ELF
(Extremely Low Frequency electromagnetic
field) score and wildtype thigmotaxis
behavior across seven international
phenotyping centers:

- Spearman r = -0.775
- p = 0.0408
- N = 7 centers
- Strain: C57BL/6N wildtype
- Procedure: IMPC_OFD_001
- Primary parameter: IMPC_OFD_010_001
  (time in periphery / thigmotaxis)

Direction: higher ELF exposure at a
facility predicts higher thigmotaxis
(more wall-hugging, less center
exploration) in wildtype mice.

This result was further examined across
two additional behavioral procedures:

- Fear conditioning: ELF-correlated
  pattern in context and cue freezing,
  consistent with open field direction
- Acoustic startle / PPI: non-linear
  ELF-correlated pattern

The TCP/CCP-IMG behavioral split —
the two most divergent centers on the
ELF gradient — appeared consistently
across all three procedures, providing
internal cross-procedure validation.

### 1.2 Why the Result Requires
### Independent Replication

The DR23 result is observational.
ELF score is a proxy variable, not a
direct measurement. Seven centers is
a small N for a Spearman correlation.
Confounding variables (country,
institution culture, building age,
investigator effects) cannot be ruled
out from a single dataset.

Independent replication in a separate
dataset collected under a different
program, with a different procedure ID,
at partially overlapping centers,
reduces the space of alternative
explanations substantially.

### 1.3 Why EUMODIC Is the Right
### Replication Dataset

The EUMODIC (European Mouse Disease
Clinic) consortium collected
standardized open field behavioral
data across European phenotyping
centers from approximately 2006-2011.
This predates the IMPC DR23 collection
period for most centers.

Key properties that make EUMODIC
the correct replication dataset:

**Independence:** Different program,
different investigators, different
procedure ID (ESLIM_007_001 vs
IMPC_OFD_001), different time period.

**Overlap:** Four centers appear in
both datasets — HMGU, ICS, MRC Harwell,
WTSI. This enables a within-center
temporal stability test: does the same
facility show the same relative
thigmotaxis rank across two independent
data collection programs separated
by years?

**Same strain:** C57BL/6N controls are
available in sufficient numbers for
strict substrain matching to the DR23
analysis.

**Same measure:** Periphery permanence
time (EUMODIC) is a direct analog of
time in periphery (DR23 primary
parameter).

**Freely accessible:** CC-BY 4.0,
available via IMPC SOLR API. Data
access confirmed by Robert Wilson,
EMBL-EBI Mouse Informatics Team,
February 27, 2026.

---

## PART II: WHAT THE PIPELINE
## HAS PRODUCED — PRE-ANALYSIS
## FINDINGS

### 2.1 Data Acquisition
### (eumodic_query.py)

- Total records acquired:
  10,026
- Procedure: ESLIM_007_001
- Parameters retrieved:
  Centre permanence time,
  Periphery permanence time
- All records:
  biological_sample_group = control,
  zygosity = homozygote
- Centers present: 5
  (CMHD, HMGU, ICS, MRC Harwell, WTSI)

### 2.2 Diagnostic Findings
### (eumodic_diagnose.py)

Critical finding: the zygosity column
contains "homozygote" for all records,
not wildtype strings. The
biological_sample_group column confirms
all records are controls. No wildtype
string filtering was required — the
SOLR query already retrieved control
animals only.

Strain landscape confirmed:
- C57BL/6N strict strains: 4,828
  records across all centers
- C57BL/6 all substrains: 8,084 records
- 34 distinct strain names present

### 2.3 Strain Audit
### (eumodic_strain_audit.py)

All five centers qualified for
STRICT_B6N rule (N ≥ 8 C57BL/6N
strict controls per center):

| Center      | N B6N  | Rule       |
|-------------|--------|------------|
| CMHD        | 146    | STRICT_B6N |
| HMGU        | 1,938  | STRICT_B6N |
| ICS         | 1,810  | STRICT_B6N |
| MRC Harwell | 826    | STRICT_B6N |
| WTSI        | 108    | STRICT_B6N |

No centers required AGG_B6ALL fallback.
No centers were insufficient.
Primary analysis proceeds as strict
C57BL/6N only — per pre-registration.

Overlap with DR23:
- 4 centers in both datasets:
  HMGU, ICS, MRC Harwell, WTSI
- 1 EUMODIC-only center: CMHD
- 3 DR23 centers absent from EUMODIC:
  CCP, IMG, TCP

### 2.4 ELF Score Assignment
### (eumodic_elf_assignment.py)

ELF scores assigned before behavioral
medians were computed — per
pre-registration record in
EUMODIC_README.md.

Final ELF score table:

| Center      | ELF | DR23  | Source              |
|-------------|-----|-------|---------------------|
| CMHD        | 72  | NEW   | new_assignment_blind|
| HMGU        | 65  | 65    | DR23_carried_fwd    |
| MRC Harwell | 59  | 59    | DR23_carried_fwd    |
| ICS         | 36  | 36    | DR23_carried_fwd    |
| WTSI        | 28  | NEW   | new_assignment_blind|

Notes on assignments:

**CMHD (72):** Hospital-adjacent urban
academic facility at Mount Sinai
Hospital, Toronto. 60 Hz grid. High
surrounding electrical infrastructure
density. No shielding documentation.
Assigned blind to behavioral values.

**HMGU (65):** Carried from DR23.
Large suburban research campus, mixed
building ages, moderate HV.

**MRC Harwell (59):** Carried from DR23.
Historic rural campus with modern
additions, lower HV density.

**ICS (36):** Carried from DR23.
Purpose-built modern facility,
low ambient ELF.

**WTSI (28):** Not present in DR23.
New blind assignment. Purpose-built
rural genomics campus, low HV
proximity, likely shielding.

Cross-check passed: all five centers
have both a strain rule and an ELF
score.

---

## PART III: PRE-REGISTERED
## PREDICTIONS — STATED BEFORE
## CORRELATION SCRIPT IS RUN

### 3.1 Primary Prediction

Higher ELF score at a EUMODIC center
will correlate positively with higher
median periphery permanence time
(thigmotaxis) in C57BL/6N wildtype
controls.

Spearman r is predicted to be negative
(ELF and thigmotaxis move in the same
direction — higher ELF, more
wall-hugging — therefore when ELF is
the x-axis and periphery time is the
y-axis, r will be positive; when
framed as ELF disrupting spatial
confidence, r is positive).

**Clarification of sign convention:**
In the DR23 analysis, r = -0.775
because higher ELF was associated with
higher thigmotaxis AND the correlation
was framed as ELF vs. proportion of
time in periphery normalized to
total test time. In the EUMODIC
analysis, periphery permanence time
is an absolute duration. The predicted
direction is: higher ELF → higher
periphery permanence time. The sign
of r depends on the specific
parameterization in the script —
what matters is the direction of
the association, not the sign.

### 3.2 Predicted Rank Order

Pre-registration anchor — stated
before behavioral medians are computed:

```
Rank 1 (highest thigmotaxis): CMHD
Rank 2:                        HMGU
Rank 3:                        MRC Harwell
Rank 4:                        ICS
Rank 5 (lowest thigmotaxis):   WTSI
```

This prediction follows directly from
the ELF score gradient:
72 → 65 → 59 → 36 → 28.

### 3.3 Within-Center Prediction

For the three centers present in both
DR23 and EUMODIC (HMGU, ICS,
MRC Harwell), the relative rank order
of thigmotaxis is predicted to be
preserved across datasets.

DR23 rank order among these three
centers (highest to lowest thigmotaxis):
HMGU > MRC Harwell > ICS

This rank order is predicted to
replicate in EUMODIC — because ELF
is a stable physical property of
the facility, not a property of
the data collection period.

### 3.4 Secondary Prediction

Centre permanence time (the inverse
measure) is predicted to show the
opposite direction to periphery
permanence time — higher ELF centers
should show lower centre permanence
time. This is an internal consistency
check, not an independent prediction.

### 3.5 What Would Constitute
### Replication

**Strong replication:**
- Spearman r in predicted direction
- p < 0.05
- Rank order preserved for ≥ 4/5
  centers
- Within-center rank order preserved
  for ≥ 2/3 overlapping centers
- LOO sensitivity: majority of
  leave-one-out results remain
  significant or trend

**Partial replication:**
- Spearman r in predicted direction
- p < 0.10 (trend)
- Rank order partially preserved

**Null result:**
- No significant association
- Direction inconsistent

All outcomes will be reported in full
regardless of direction — per
methodology of the full series.

---

## PART IV: CONTEXT —
## THE THREE-VECTOR PROGRAM

The IMPC / EUMODIC analysis is one
of three parallel observational probes
of the EM coherence hypothesis:

**Vector 1: IMPC / EUMODIC**
Species: Mus musculus (C57BL/6N)
EM channel: ELF (power grid, building
  infrastructure, 50-60 Hz)
Behavioral measure: Thigmotaxis
  (spatial navigation anxiety)
Current status:
  DR23 — significant (r=-0.775, p=0.04)
  EUMODIC — correlation script
  about to run

**Vector 2: Monarch butterfly**
Species: Danaus plexippus
EM channel: FM broadcast infrastructure
  (88-108 MHz RF)
Behavioral measure: Migration trajectory
  coherence / false attractor deflection
Current status:
  Rayleigh test — significant
  (p=0.000517, mean false attractor
  bearing 218.9° SW)
  NW permutation — significant
  Recovery data — awaiting Monarch
  Watch response

**Vector 3: Sea turtle**
Species: Caretta caretta (loggerhead)
EM channel: AM broadcast transmitters
  + submarine cable geomagnetic
  disruption
Behavioral measure: Natal homing
  cohort spread, stranding patterns
Current status:
  Pre-registered — awaiting FWC
  nesting data and NOAA stranding data

All three vectors test the same
theoretical claim under the EM
Coherence Unified Framework:
biological navigation systems are
coherence detectors operating on
eigenfunction spaces, and disruption
of EM field coherence — regardless
of frequency, species, or channel —
produces measurable degradation in
navigation behavior.

---

## PART V: WHAT COMES AFTER
## THE CORRELATION SCRIPT

### 5.1 If Replication Is Supported

Write EUMODIC_doc2_results.md —
full results document with all
numerical outputs, figures, and
honest assessment.

Update the pre-registered analysis
record on GitHub with results.

Proceed to DR24 extension when
DR24 releases (expected within
days per Robert Wilson, EBI).

Begin drafting manuscript introduction
and methods — the two-dataset
observational result plus the Faraday
cage pre-registration constitutes
a publishable unit.

### 5.2 If Null or Inconsistent

Write EUMODIC_doc2_results.md with
full null result documented.

Analyze which alternative explanation
best fits the pattern — institution
effects, strain composition differences,
procedure differences between
ESLIM_007_001 and IMPC_OFD_001.

Do not suppress the result. The DR23
finding stands on its own. The null
replication is informative and
constrains the interpretation.

Proceed to Faraday cage experiment —
the causal test is not contingent
on observational replication.

### 5.3 Immediate Next Steps
### Regardless of Result

- DR24 release: query open field
  data for new centers, extend
  gradient
- JAX response: if JAX data becomes
  available, add to DR23 analysis
- Faraday cage: proceed toward
  IACUC submission and facility
  identification
- Monarch Watch: continue waiting
  for recovery data response
- Sea turtle: send FWC and NOAA
  emails

---

## PART VI: PROVENANCE AND
## REPRODUCIBILITY

### 6.1 Data Provenance

All EUMODIC data retrieved from
EMBL-EBI IMPC SOLR API,
procedure ESLIM_007_001,
parameter names "Centre permanence
time" and "Periphery permanence time",
biological_sample_group = control.

Query executed: February 27, 2026.
License: CC-BY 4.0.

Citation per IMPC guidelines:
https://www.mousephenotype.org/
help/faqs/how-do-i-cite-the-impc/

### 6.2 Script Inventory

All scripts in this folder in
execution order:

1. eumodic_query.py
   — data acquisition ✅
2. eumodic_diagnose.py
   — column structure audit ✅
3. eumodic_strain_audit.py
   — strain rule per center ✅
4. eumodic_elf_assignment.py
   — ELF scores before behavioral
   values examined ✅
5. eumodic_correlation.py
   — primary analysis ⏳

### 6.3 Pre-Registration Status

Methodological decisions documented
in EUMODIC_README.md and this
document prior to running the
correlation script.

Pre-registration hosted on GitHub:
Eric-Robert-Lawson/OrganismCore

Not yet submitted to OSF —
GitHub repository serves as the
timestamped pre-registration record.

---

## VERSION

- v1.0 — February 27, 2026
  Pre-analysis record.
  Written after pipeline scripts 1-4
  completed successfully.
  Written before eumodic_correlation.py
  was run.
  All predictions in Part III stated
  before behavioral medians examined.
