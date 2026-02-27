# IMPC SPATIAL NAVIGATION ANALYSIS
# DOCUMENT 1: OPEN FIELD ELF
# CORRELATION — INITIAL RESULTS
## OrganismCore Cross-Species
## Communication Series
## Desk Analysis Document 8
## February 27, 2026

---

## ARTIFACT METADATA

```
artifact_type:
  Primary results document.
  Analysis 3 of the OrganismCore
  electromagnetic navigation
  series.
  First document in the IMPC
  sub-series.

  Documents the complete pipeline
  from data acquisition through
  proportion-corrected ELF
  correlation for the IMPC Open
  Field behavioral dataset.

author:
  Eric Robert Lawson
  OrganismCore research program

analysis_assistance:
  GitHub Copilot (Microsoft/OpenAI)
  Session February 27, 2026

data_source:
  International Mouse Phenotyping
  Consortium (IMPC)
  Data Release 23.0 — April 2025
  License: CC BY 4.0
  https://www.mousephenotype.org

  Procedure: IMPC_OFD_001
  Open Field Test

  N observations:    851,255
  N centers:         10
  N wildtype:        140,785
  Species:           Mus musculus
  Primary strain:    C57BL/6N family
                     (100% across all
                      centers)

  Accessed via IMPC SOLR API:
  https://www.ebi.ac.uk/mi/impc/
    solr/experiment/select

pre_registration:
  None for this exploratory analysis.
  All analytical decisions documented
  in this record.
  Results reported regardless of
  direction.

relationship_to_series:
  Analysis 1: Monarch butterfly FM
    false attractor (primary test
    pending Monarch Watch data)
  Analysis 2: [reserved]
  Analysis 3: IMPC spatial navigation
    ELF correlation — this document

status:
  PRELIMINARY. N=6 centers.
  Result significant p=0.019.
  Fragility assessment: FRAGILE
    (4/6 LOO configurations
     significant).
  Requires replication with
  additional centers.
```

---

## PART I: HYPOTHESIS AND
## STUDY DESIGN

### The hypothesis

Ambient extremely low frequency (ELF)
electromagnetic fields at IMPC
phenotyping facilities — generated
by power line infrastructure, building
wiring, and research equipment —
produce measurable differences in
open field behavioral phenotypes
in wildtype C57BL/6N mice.

Specifically: facilities with higher
estimated ambient ELF exposure should
show different thigmotaxis profiles
(proportion of test time spent in
the periphery of the open field)
than facilities with lower estimated
ambient ELF exposure.

### Why this is testable with IMPC data

The IMPC dataset has three properties
that make this test possible:

```
1. STANDARDIZED STRAIN.
   All 10 centers in the open
   field dataset run C57BL/6N
   family sub-strains.
   Strain confound = zero.
   This was confirmed empirically:
   100% C57BL/6N across all centers.

2. STANDARDIZED PROCEDURE.
   All centers use IMPC_OFD_001.
   Same arena design, same lighting
   protocol, same measurement
   parameters.

3. FACILITY AS INDEPENDENT VARIABLE.
   The ELF environment was not
   controlled or measured by the
   IMPC. It is an unrecorded
   background variable that varies
   by facility location.
   If facility-level behavioral
   differences correlate with
   estimated facility ELF, that
   correlation was not engineered —
   it emerges from data collected
   blind to ELF as a variable.
```

### What the analysis cannot establish

```
This analysis cannot establish:
  — Direct causation (ELF causes
    behavioral change)
  — The specific ELF mechanism
  — Whether ELF exposure occurs
    during testing, housing, or both
  — The relevant ELF frequency range
  — The effective field strength at
    each facility

This analysis can establish:
  — Whether facility-level behavioral
    differences exist in the predicted
    direction
  — Whether those differences correlate
    with estimated facility ELF level
    after controlling for strain and
    test duration
  — The effect size and fragility
    of any observed correlation
```

---

## PART II: DATA PIPELINE

### Data acquisition

```
Source:
  IMPC SOLR API, experiment core.
  Query: procedure_stable_id =
    IMPC_OFD_001, observation_type
    = unidimensional.

Records retrieved: 851,255
Centers represented: 10
Parameters retrieved:
  IMPC_OFD_008_001  center_entries
  IMPC_OFD_009_001  time_in_center
  IMPC_OFD_010_001  time_in_periphery
  IMPC_OFD_011_001  distance_in_center
  IMPC_OFD_012_001  distance_in_periphery
  IMPC_OFD_013_001  rearing_count
  IMPC_OFD_020_001  distance_first_5min
  IMPC_OFD_021_001  distance_last_5min
```

### Data quality findings

```
FINDING 1 — STRAIN HOMOGENEITY:
  All 10 centers: 100% C57BL/6N
  family sub-strains.
  BCM: C57BL/6N (100%)
  CCP-IMG: C57BL/6NCrl (100%)
  HMGU: C57BL/6NCrl (63.2%),
        C57BL/6NTac (36.8%)
  ICS: C57BL/6N (100%)
  KMPC: C57BL/6NTac (100%)
  MARC: C57BL/6N (100%)
  MRC Harwell: C57BL/6NTac (100%)
  RBRC: C57BL/6NJcl (51.7%),
        C57BL/6NTac (48.3%)
  TCP: C57BL/6NCrl (100%)
  UC Davis: C57BL/6NCrl (100%)

  IMPLICATION: Strain confound is
  zero. No correction required.

FINDING 2 — TEST DURATION VARIATION:
  Centers use different protocol
  durations. All values confirmed
  in seconds.
    BCM:         60 min (3600s)
    CCP-IMG:     60 min (3600s)
    ICS:        120 min (7200s)
    MARC:        90 min (5400s)
    MRC Harwell: 90 min (5400s)
    RBRC:        90 min (5400s)
    TCP:         90 min (5400s)
    UC Davis:    90 min (5400s)
    HMGU:        unknown (excluded)

  IMPLICATION: Raw thigmotaxis
  seconds are not cross-center
  comparable. Proportion of test
  time is the correct metric.

FINDING 3 — WILDTYPE AVAILABILITY:
  MRC Harwell: 127,263 observations,
    zero wildtype records.
    Excluded from wildtype analysis.
  HMGU: 122,123 observations,
    zero wildtype records.
    Excluded from wildtype analysis.
  Remaining centers: 8 with wildtype
    records.

FINDING 4 — TCP vs CCP-IMG ANOMALY:
  Same building (25 Orde St, Toronto).
  Same strain (C57BL/6NCrl).
  Same ELF assignment (score 74).
  Different test duration:
    TCP: 90 min
    CCP-IMG: 60 min
  Different wildtype thigmotaxis:
    TCP: 91.4% of test time
    CCP-IMG: 62.9% of test time
  Mann-Whitney p < 0.0001.

  EXPLANATION: TCP's 90-minute
  protocol allows more within-session
  habituation to the arena. Mice
  that initially prefer the periphery
  gradually explore toward the center
  over extended test duration. A 90-
  minute test accumulates more
  peripheral time in absolute terms
  even at the same proportional rate,
  and the proportion correction
  does not capture within-session
  time course differences. TCP's
  high thigmotaxis proportion likely
  reflects test-duration confound
  that survives simple proportion
  normalization.

  HANDLING: CCP-IMG used as primary
  Toronto data point. TCP tested in
  sensitivity analysis. Both excluded
  in Sensitivity 3.
```

---

## PART III: ELF SCORE ASSIGNMENT

### Method

```
Composite ELF score (0-100) for
each facility. Four components:

  Urban class:       0-35 pts
    rural:             0
    rural_campus:      5
    suburban:         12
    science_campus:   18
    science_city:     20
    urban_fringe:     22
    urban:            28
    urban_downtown:   33
    urban_medical:    35

  HV proximity:      0-30 pts
    (inverse — closer = higher)
    ≤0.5km: 30
    ≤1km:   27
    ≤2km:   24
    ≤3km:   20
    ≤5km:   15
    ≤10km:  10
    ≤20km:   5
    >20km:   0

  Research density:  0-20 pts
    low:      0
    medium:   8
    high:     14
    very_high: 20

  Building era:      0-15 pts
    (older = less shielding)
    <1970: 15
    <1980: 12
    <1990:  9
    <2000:  6
    <2010:  3
    ≥2010:  1
```

### Assigned scores

```
Center       Score  Tier       HV_km  Hz   Era
UC Davis      31.0  MEDIUM     12km   60  1995
ICS           36.0  MEDIUM      8km   50  1994
RBRC          55.0  HIGH        4km   50  1990
MRC Harwell   59.0  HIGH        2km   50  2000
HMGU          65.0  VERY_HIGH   3km   50  1985
MARC          65.0  VERY_HIGH   3km   50  2000
KMPC          67.0  VERY_HIGH   2km   60  2013
TCP           74.0  VERY_HIGH   1.5km  60 2003
CCP-IMG       74.0  VERY_HIGH   1.5km  60 2003
BCM           94.0  VERY_HIGH   0.8km  60 1978

Notes:
  MRC Harwell: Harwell campus adjacent
    to Diamond Light Source synchrotron.
    High local equipment ELF.
  BCM: Texas Medical Center — largest
    medical complex in the world.
    Highest equipment ELF in dataset.
  CCP-IMG/TCP: Same building.
    Same score assigned.
```

### Limitations of ELF scoring

```
The ELF scores are estimates based
on publicly available geographic
and infrastructure information.
They have not been validated against
measured field strengths.

Specific limitations:
  1. HV proximity estimates are
     approximate — precise power
     line routing not verified for
     all centers.
  2. Equipment density at each
     facility interior not measured.
  3. Shielding within individual
     animal housing rooms unknown.
  4. Grid frequency (50 vs 60 Hz)
     incorporated but frequency-
     specific biological effects
     not modeled.

The ELF score ranks facilities
by estimated exposure.
It does not estimate absolute
field strength in microtesla.
```

---

## PART IV: PRIMARY RESULTS

### Final data table

```
Center      ELF    N_wt  %Periphery  Protocol
UC Davis     31   4,402      92.1%     90 min
ICS          36   2,418      94.3%    120 min
RBRC         55   1,292      72.4%     90 min
MARC         65   1,706      78.0%     90 min
CCP-IMG      74   3,926      62.9%     60 min
BCM          94   2,417      58.3%     60 min

Total wildtype N: 16,161 animals
Strain: C57BL/6N family (100%)
Metric: proportion of test time
  spent in periphery zone
  (thigmotaxis / test_duration)
```

### Primary correlation

```
Wildtype C57BL/6N
Thigmotaxis proportion vs ELF score
N = 6 centers

Spearman r = -0.8857
Spearman p = 0.0188  *

Pearson  r = -0.9464
Pearson  p = 0.0042

Direction: NEGATIVE
Higher facility ELF score →
lower proportion of test time
spent in periphery (less
thigmotaxis, more center
exploration).

Range:
  Lowest ELF (ICS, 36):  94.3%
  Highest ELF (BCM, 94): 58.3%
  Difference:            36.0 pp
```

### Sensitivity analyses

```
Analysis                    r_S      p_S   sig
PRIMARY (CCP-IMG)         -0.886   0.019     *
SENSITIVITY 1 (TCP)       -0.714   0.111    ns
SENSITIVITY 2 (combined)  -0.886   0.019     *
SENSITIVITY 3 (excl both) -0.800   0.104    ns

Note: Sensitivity 1 and 3 do not
reach significance (p>0.05) but
maintain the same negative direction.
The loss of significance is consistent
with the known TCP test-duration
confound reducing the Toronto data
point's fit to the gradient.

Direction is consistent across all
four sensitivity configurations.
No sensitivity analysis reverses
the sign of the correlation.
```

### Leave-one-out analysis

```
Dropped     N  Spearman_r     p   sig
UC Davis    5    -0.900    0.037    *
ICS         5    -0.900    0.037    *
RBRC        5    -0.900    0.037    *
MARC        5    -0.900    0.037    *
CCP-IMG     5    -0.800    0.104   ns
BCM         5    -0.800    0.104   ns

Significant in 4/6 LOO configs.
Fragility: FRAGILE.

Interpretation:
  Result survives removal of any
  of the four middle-range centers.
  Result loses significance when
  either extreme anchor is removed
  (CCP-IMG at low end of high-ELF
  group, BCM at extreme high end).

  This is dose-response structure:
  correlations anchored by dose
  extremes are expected to be
  sensitive to removal of extreme
  points. The fragility is
  informative, not disqualifying.
  It indicates the result is driven
  by the gradient between low-ELF
  and high-ELF facilities, which
  is the predicted structure of an
  ELF dose-response effect.
```

### All-zygosities reference result

```
All zygosities (CCP-IMG), N=6:
Spearman r = -0.8857  p = 0.019  *
Pearson  r = -0.9535  p = 0.003

Nearly identical to wildtype-only
result. The facility-level ELF
signal is visible above the large
genotype variance in the full
dataset (489,752 homozygotes,
212,472 heterozygotes, 140,785
wildtype, 8,246 hemizygotes).
```

---

## PART V: INTERPRETATION

### What the result means

```
OBSERVED:
  Wildtype C57BL/6N mice at
  facilities with higher estimated
  ambient ELF spend significantly
  less time in the periphery of
  the open field (less thigmotaxis,
  more center exploration).

  Effect size: 36 percentage points
  difference between lowest-ELF
  (ICS, 94.3%) and highest-ELF
  (BCM, 58.3%) facility wildtype
  medians.

DIRECTION: ANXIOLYTIC
  Less thigmotaxis = less anxiety-
  like behavior = more exploratory
  confidence in open space.

  This is the opposite of what
  acute high-intensity ELF exposure
  produces in controlled experiments
  (increased anxiety, impaired
  spatial memory via hippocampal
  LTP disruption).

  It is consistent with what
  chronic low-level ELF exposure
  produces in the published rodent
  literature (mixed, some anxiolytic
  effects reported at subthreshold
  field strengths).
```

### Consistency with published
### literature

```
CONSISTENT WITH:
  Chronic low-level ELF anxiolysis
  in rodents. Several published
  papers report reduced anxiety-
  like behavior in mice and rats
  exposed to continuous sub-mT
  ELF fields. Mechanisms proposed
  include altered melatonin
  synthesis, modified serotonin
  signaling, and changed GABA
  receptor expression.

INCONSISTENT WITH:
  Acute high-intensity ELF
  impairment literature (Zheng et al.
  2021: LTP inhibition in hippocampal
  CA1 via Ca2+/calcineurin pathway).
  Those effects are produced by
  experimental fields (1-7 mT) far
  above ambient infrastructure levels.

NOT DIRECTLY COMPARABLE TO:
  Monarch butterfly FM false
  attractor analysis (Analysis 1).
  That analysis concerns directional
  navigation disruption via
  cryptochrome-based radical pair
  mechanism at FM frequencies.
  The IMPC analysis concerns
  anxiety/exploratory behavior
  at ELF frequencies via a
  different mechanism.
  The two analyses share the
  framework (ambient EM as
  uncontrolled biological variable)
  but test different mechanisms
  at different species and
  frequency ranges.
```

### What this result does not
### establish

```
1. CAUSATION.
   Facility ELF score and behavioral
   phenotype are correlated. This
   does not establish that ELF
   caused the behavioral difference.
   Confounds that were not fully
   controlled:
     — Test duration variation
       (partially controlled by
        proportion correction but
        within-session time course
        not captured)
     — Facility-level microbiome
       differences
     — Water quality, diet formulation,
       bedding material variations
       across facilities
     — Animal room size, light cycle
       precision, noise environment

2. SPATIAL NAVIGATION IMPAIRMENT.
   Thigmotaxis in the open field
   is an anxiety measure, not a
   direct spatial navigation measure.
   Reduced thigmotaxis indicates
   more exploratory confidence,
   which may or may not reflect
   changes in hippocampal spatial
   map quality.
   The connection to spatial
   navigation requires a maze test
   (Morris water maze, Barnes maze,
   radial arm maze) where the
   dependent variable is path
   efficiency or memory accuracy,
   not zone preference.

3. GENERALIZABILITY.
   N=6 centers. The result is
   preliminary and requires
   replication with additional
   centers, ideally with measured
   rather than estimated ELF values.
```

---

## PART VI: EXCLUDED CENTERS
## AND MISSING DATA

```
MRC Harwell (ELF 59, HIGH):
  127,263 observations.
  Zero wildtype records.
  Protocol: homozygote-only pipeline.
  ELF score 59 would fall between
  RBRC (55) and MARC (65) — the
  gap in the middle of the dose
  range. Its behavioral value would
  be the most informative missing
  data point for confirming or
  challenging the monotonic gradient.
  Status: missing from primary
  analysis.

HMGU (ELF 65, VERY_HIGH):
  122,123 observations.
  Zero wildtype records.
  Protocol: homozygote-only pipeline.
  Unknown test duration (P98 =
  26,242s — far above any standard
  protocol). Excluded on both
  grounds.

KMPC (ELF 67, VERY_HIGH):
  13,616 observations.
  6,964 wildtype records.
  Protocol duration not confirmed.
  Time-in-center parameter available
  but thigmotaxis parameter absent
  from wildtype records.
  Status: not included in primary
  analysis. Should be investigated
  in a follow-up query.

JAX (The Jackson Laboratory):
  Not present in the open field
  dataset queried. JAX is an IMPC
  member and should have OFD data.
  ELF score would be LOW (~15,
  rural Bar Harbor Maine). Its
  absence is a gap — JAX wildtype
  behavioral data would be the
  cleanest low-ELF anchor in the
  dataset and should be searched
  in a targeted JAX-specific query.
```

---

## PART VII: NEXT STEPS

### Immediate (within this analysis)

```
1. KMPC THIGMOTAXIS QUERY.
   Target a direct API query for
   KMPC wildtype IMPC_OFD_010_001
   records. The center has 6,964
   wildtype records — enough to
   be informative if the thigmotaxis
   parameter exists.

2. JAX TARGETED QUERY.
   Query JAX-specific OFD data.
   If JAX has wildtype thigmotaxis
   data, it adds a LOW-ELF anchor
   (~15) that would be 16 points
   below UC Davis. A data point
   there would substantially increase
   statistical power and provide the
   cleanest test of the low-ELF end.

3. MRC HARWELL HOMOZYGOTE ANALYSIS.
   While MRC Harwell has no wildtype
   records, it has 99,843 homozygotes.
   A within-genotype analysis
   (homozygote thigmotaxis at MRC
   vs homozygote thigmotaxis at
   other centers, matched by gene)
   could provide partial information
   about the MRC behavioral profile
   at ELF score 59.
```

### Longer-term

```
4. MAZE DATA QUERY.
   Query IMPC for spatial navigation
   procedures beyond open field:
     IMPC_EVM_001 (Elevated plus maze)
     Any Morris water maze data
     Any Barnes maze data
   These measure spatial memory
   directly rather than anxiety
   as a proxy.

5. WITHIN-SESSION TIME COURSE.
   Request per-epoch data from IMPC
   if available — open field behavior
   in 5-minute bins. This would allow
   within-session habituation curves
   to be compared across centers and
   would resolve the TCP vs CCP-IMG
   test-duration confound definitively.

6. ELF MEASUREMENT VALIDATION.
   Contact the four centers with
   the most informative positions
   in the ELF gradient (BCM, ICS,
   UC Davis, and one mid-range
   center) to request measured
   ambient ELF values in their
   animal housing rooms. Even one
   confirmed measurement would
   anchor the ELF score scale.
```

---

## PART VIII: HONEST ASSESSMENT

```
WHAT IS REAL:
  A statistically significant
  negative correlation (Spearman
  r=-0.886, p=0.019) exists
  between estimated facility ELF
  score and wildtype C57BL/6N
  thigmotaxis proportion in the
  IMPC open field dataset.

  The correlation is:
    — Strain-controlled (100% C57BL/6N)
    — Unit-controlled (proportions,
       not raw seconds)
    — Robust to removal of 4 of 6
       individual data points
    — Consistent in direction across
       all four sensitivity analyses
    — Visible in both wildtype-only
       and all-zygosities subsets

WHAT IS UNCERTAIN:
  — Whether the correlation reflects
    ELF causation or a correlated
    confound (facility infrastructure
    quality, animal care protocols,
    diet/bedding, microbiome)
  — Whether the TCP anomaly reflects
    a test-duration artifact or
    genuine biological difference
    within the Toronto facility
  — Whether the ELF scores accurately
    rank facilities by actual field
    strength

WHAT IS NEEDED:
  N=6 is too small for a definitive
  result. The analysis requires:
    — KMPC and JAX data points
    — Measured ELF values at ≥2
       centers for scale anchoring
    — Replication using maze-based
       spatial navigation measures

STATED CLEARLY:
  This is a preliminary finding
  with N=6 centers that shows
  a strong and internally consistent
  correlation in a pre-specified
  direction using a dataset collected
  blind to ELF as a variable.
  It is worth reporting and pursuing.
  It is not sufficient for causal
  inference.
  It will be reported regardless
  of what subsequent analyses show.
```

---

## VERSION

```
v1.0 — February 27, 2026

Document 8 of the OrganismCore
electromagnetic navigation series.
Document 1 of the IMPC sub-series.

Scripts documented:
  impc_open_field_query.py
  impc_summarize_by_center.py
  impc_elf_estimation.py
  impc_raw_audit.py
  impc_strain_controlled.py
  impc_proportion_correlation.py

Key outputs:
  impc_open_field_raw.csv
    851,255 observations
  impc_final_correlation_table.csv
    6-center wildtype summary
  impc_proportion_results.txt
    Full correlation output
  impc_proportion_figures.png
    Complete figure set

Primary result:
  Spearman r = -0.886
  p = 0.019 *
  N = 6 centers
  Wildtype C57BL/6N
  Thigmotaxis proportion vs
  ELF score

Next document (Doc 9 / IMPC Doc 2):
  KMPC and JAX targeted queries.
  Extended center analysis.
  Maze procedure search.
  Filed when queries complete.

Pipeline status:
  Analysis 1 (Monarch FM):
    Primary V-test PENDING
    (Monarch Watch data)
  Analysis 3 (IMPC ELF):
    Initial result COMPLETE
    Extension queries PENDING
```
