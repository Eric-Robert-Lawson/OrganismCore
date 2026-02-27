# EUMODIC OPEN FIELD REPLICATION ANALYSIS
## Independent Cross-Dataset Validation of the
## ELF-Thigmotaxis Correlation
## Reasoning Artifact — IMPC Series
## OrganismCore — Cross-Species Communication Series
## qualia_candidate_axioms/historical/Solen/
## voice_topology_folder/Beyond_human_and_vocal/
## cross_species/experiments/impc/EUMODIC/
## February 27, 2026

---

## ARTIFACT METADATA

- **Series:** IMPC Spatial Navigation Analysis
- **Document number:** IMPC Document 4
- **Status:** Active — query pipeline in progress
- **Depends on:** IMPC_Spatial_Navigation_Analysis.md,
  impc_spatial_navigation_doc2.md,
  impc_spatial_navigation_doc3.md
- **Pre-registration:** GitHub —
  Eric-Robert-Lawson/OrganismCore
- **Data source:** EMBL-EBI IMPC SOLR API
- **Procedure:** ESLIM_007_001
  (EUMODIC Pipeline 2 Open Field)
- **License:** CC-BY 4.0
- **Contact:** Robert Wilson,
  EMBL-EBI Mouse Informatics Team
  mouse-informatics@ebi.ac.uk

---

## PART I: WHY THIS FOLDER EXISTS

### 1.1 The Primary Result Being Replicated

The IMPC DR23 analysis (Documents 1-3)
identified a significant negative correlation
between facility-level ELF score and wildtype
thigmotaxis behavior across seven international
phenotyping centers:

- Spearman r = -0.775
- p = 0.0408
- N = 7 centers
- Strain: C57BL/6N wildtype
- Procedure: IMPC_OFD_001
- Parameters: IMPC_OFD_010_001
  (time in periphery),
  IMPC_OFD_009_001 (time in center)

Direction of effect: higher ELF exposure
at a facility predicts lower thigmotaxis
(more center exploration) in wildtype mice.

This result is observational. It cannot
establish causation. The EUMODIC dataset
provides the first opportunity for
independent replication using a separate
data collection program, a different
procedure ID, and a partially overlapping
set of centers — some of which collected
data years before the DR23 records.

### 1.2 What EUMODIC Is

The EUMODIC (European Mouse Disease Clinic)
consortium ran a standardized phenotyping
pipeline across European centers from
approximately 2006 to 2011. This predates
the IMPC DR23 data collection period for
most centers.

The open field procedure in EUMODIC
Pipeline 2 is ESLIM_007_001, with
parameters:

- Centre permanence time — direct analog
  to IMPC_OFD_009_001
- Periphery permanence time — direct analog
  to IMPC_OFD_010_001 (thigmotaxis measure)

The EUMODIC data is incorporated into the
IMPC resource and is freely accessible
under CC-BY 4.0 via the IMPC SOLR API.

### 1.3 Why This Replication Matters

Independent replication in EUMODIC provides
three things the DR23 analysis alone cannot:

**A) Cross-dataset replication**
The EUMODIC data was collected independently,
under a different program, with different
investigators, using a different procedure
ID. If the ELF-thigmotaxis correlation
appears in EUMODIC with the same direction,
it is not a DR23 artifact.

**B) Within-center temporal stability**
Centers present in both datasets — ICS,
MRC Harwell, HMGU — allow a direct test:
does the same facility show the same
relative thigmotaxis rank across two
independent data collection periods
separated by years?

If yes: the effect is a stable,
facility-level property. This is the
strongest possible observational evidence
that ELF — a stable physical property
of a building and its infrastructure —
is the operative variable, not any
transient feature of a single data
collection period.

**C) Extension of the ELF gradient**
EUMODIC centers not present in DR23
may extend the ELF gradient at either
end, increasing the power and range
of the Spearman correlation.

---

## PART II: METHODOLOGICAL DECISIONS
## PRE-REGISTERED BEFORE QUERYING
## BEHAVIORAL VALUES

The following decisions were made and
documented before any behavioral data
values from EUMODIC were examined.
This constitutes the pre-registration
record for the EUMODIC analysis.

### 2.1 Strain Decision

**Primary analysis:** C57BL/6N controls
only — strict substrain match to DR23
analysis.

**Rationale:** Direct comparability with
the primary DR23 result requires the same
strain. C57BL/6J and C57BL/6N have known
behavioral differences in anxiety-related
measures. Aggregating substrains would
introduce a confound.

**Secondary analysis:** All C57BL/6
related background strains aggregated —
run as sensitivity check only if C57BL/6N
strict N per center is insufficient for
meaningful center-level medians.

**Decision threshold:** If any center has
fewer than 8 C57BL/6N wildtype records,
that center will be flagged and the
aggregated substrain analysis will be
reported alongside the strict analysis
with the difference noted.

### 2.2 Primary Outcome Measure

Periphery permanence time
(ESLIM_007_001 equivalent of
IMPC_OFD_010_001) is the primary
thigmotaxis measure — direct analog
to the DR23 primary outcome.

Centre permanence time is the secondary
outcome — used for internal consistency
check (expect inverse relationship to
periphery permanence time).

### 2.3 Primary Statistical Test

Spearman rank correlation:
ELF score (facility-level) vs.
median periphery permanence time
(center-level wildtype C57BL/6N).

Same method as DR23 primary analysis.

### 2.4 ELF Score Assignment

ELF scores for EUMODIC centers will be
assigned using the same method as DR23:
facility metadata (building age, country,
grid frequency, proximity to high-voltage
infrastructure, available shielding
documentation).

For centers present in both DR23 and
EUMODIC, the same ELF score will be
used — ELF is a property of the
facility, not of the data collection
period.

New centers (EUMODIC-only) will receive
ELF scores assigned blind to their
behavioral values — scores assigned
before behavioral medians are computed.

### 2.5 Within-Center Temporal
### Comparison Method

For centers present in both datasets,
the within-center comparison will use:

- DR23 median periphery time (wildtype
  C57BL/6N) from the existing analysis
- EUMODIC median periphery permanence
  time (wildtype C57BL/6N or aggregated
  if N insufficient — documented)
- Reported as: direction of difference,
  magnitude of difference, and whether
  the center's rank position in the
  ELF gradient is preserved across
  datasets

### 2.6 What Will Be Reported
### Regardless of Direction

All results will be reported regardless
of direction. If the EUMODIC correlation
is null, opposite in direction, or
confined to a subset of centers, that
result will be documented in full and
its implications for the DR23 finding
addressed directly.

Consistent with the methodology of
the full series: honest accounting
is not optional.

---

## PART III: FOLDER STRUCTURE
## AND FILE INVENTORY

### Scripts (to be added)

- `eumodic_query.py` —
  Primary data acquisition script.
  Queries ESLIM_007_001 via IMPC SOLR
  API for centre and periphery
  permanence time, wildtype controls,
  all centers. Outputs raw CSV.

- `eumodic_strain_audit.py` —
  Checks N per center for C57BL/6N
  strict vs. aggregated C57BL/6.
  Determines which strain rule applies
  per center. Outputs strain decision
  table.

- `eumodic_elf_assignment.py` —
  Assigns ELF scores to EUMODIC centers.
  Runs before behavioral medians are
  computed. Outputs ELF score table
  with documentation.

- `eumodic_correlation.py` —
  Primary Spearman correlation:
  ELF vs. median periphery permanence
  time. Leave-one-out sensitivity.
  Within-center cross-dataset
  comparison for overlapping centers.
  Outputs results table and figures.

### Documents (to be added)

- `EUMODIC_doc1_initial_results.md` —
  First results document. Structure
  mirrors IMPC_Spatial_Navigation_
  Analysis.md. Will contain: data
  pipeline findings, strain audit
  results, ELF assignments, primary
  correlation result, sensitivity
  analyses, within-center comparison,
  honest assessment.

### Data files (local only,
### not committed to repository)

- `eumodic_raw.csv` —
  Raw SOLR query output
- `eumodic_by_center.csv` —
  Center-level summary
- `eumodic_elf_scores.csv` —
  ELF assignments with documentation

---

## PART IV: CONNECTION TO THE
## BROADER SERIES

### Position in the analysis chain

The EUMODIC replication is the second
observational rung in the IMPC analysis
chain:

```
DR23 correlation (r=-0.775, p=0.04)
        ↓
EUMODIC replication (this folder)
        ↓
DR24 extension (when released)
        ↓
Faraday cage experiment
(pre-registered — causal test)
```

Observational convergence across
DR23 and EUMODIC strengthens the
prior for the Faraday cage experiment
and narrows the range of alternative
explanations.

### Connection to the unified framework

The IMPC analysis is one of three
parallel probes of the EM coherence
hypothesis:

- **IMPC / EUMODIC:** ELF coherence
  vs. thigmotaxis in laboratory mice
- **Monarch butterfly:** FM false
  attractor vs. migration trajectory
  coherence
- **Sea turtle:** AM broadcast and
  submarine cable disruption vs.
  natal homing cohort spread

All three operate under the same
theoretical claim: biological navigation
systems are coherence detectors, and
disruption of EM field coherence —
regardless of frequency, magnitude,
or species — produces measurable
degradation in navigation behavior.

EUMODIC replication does not directly
test this claim across species. It
tests whether the DR23 result is
reproducible. Reproducibility is the
prerequisite for the claim to carry
weight in the unified framework.

---

## PART V: IMMEDIATE NEXT STEPS

1. Run `eumodic_query.py` —
   acquire raw ESLIM_007_001 data

2. Run `eumodic_strain_audit.py` —
   determine strain rule per center
   before examining behavioral values

3. Assign ELF scores to all
   EUMODIC centers blind to
   behavioral medians

4. Run `eumodic_correlation.py` —
   primary result and sensitivity
   analyses

5. Write `EUMODIC_doc1_initial_
   results.md` — full results
   document regardless of direction

---

## VERSION

- v1.0 — February 27, 2026
  Initial folder reasoning artifact.
  Pre-registration record for
  methodological decisions.
  Written prior to any EUMODIC
  behavioral data examination.
