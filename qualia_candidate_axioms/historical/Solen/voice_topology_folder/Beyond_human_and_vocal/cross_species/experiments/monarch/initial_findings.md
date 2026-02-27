# FM BROADCAST INFRASTRUCTURE AS A
# DIRECTIONAL FALSE ATTRACTOR ACROSS
# THE MONARCH BUTTERFLY MIGRATION
# CORRIDOR
## First Empirical Characterization
## of the FM Electromagnetic Landscape
## Across 363,582 Monarch Watch
## Tagging Records, 1992–2000
## OrganismCore Cross-Species
## Communication Series
## Desk Analysis Document 4
## February 26, 2026

##**IMPORTANT**

Requires additonal data for further results, requested from the proper sources.

---

## ARTIFACT METADATA

```
artifact_type:
  Findings and reproducibility record.
  Standalone preprint-ready document
  and internal OrganismCore research
  record combined.

  Contains:
    — Complete reproducible procedure
    — Verified script outputs
    — First-result findings
    — Interpretation
    — What is confirmed
    — What is not yet confirmed
    — What comes next

author:
  Eric Robert Lawson
  OrganismCore research program

analysis_assistance:
  GitHub Copilot (Microsoft/OpenAI)
  Sessions February 26–27, 2026

status:
  VERIFIED. All numbers in this
  document are direct output from
  running the analysis pipeline
  on real data. No manual adjustment.
  No rounding except where noted.
  No selection of favorable results.

pre_registration:
  OSF registration filed February 26,
  2026 prior to receipt of Monarch
  Watch recovery data.
  Quartile boundary amendment filed
  same date.
  Registration timestamp predates
  all recovery data.

data_sources:
  PRIMARY 1:
    GBIF Monarch Watch occurrence
    dataset
    Dataset ID: cf7d6c01-309b-4545-
    8319-3d53b1e8bfd0
    URL: gbif.org/dataset/cf7d6c01...
    Download date: February 27, 2026
    Records: 363,582
    Years: 1992–2000

  PRIMARY 2:
    FCC Licensing and Management
    System (LMS) public database
    Snapshot date: February 26, 2026
    File: Current_LMS_Dump.zip
    Source: fcc.gov/media/
    media-bureau-public-databases
    Stations after filtering: 8,136

pipeline_files:
  build_fm_station_table.py
    → fm_stations_clean.csv

  fm_field_density.py
    → FMFieldDensity class
    → false attractor bearing
      for any (lat, lon)

  monarch_false_attractor_analysis.py
    → monarch_with_fm.csv
    (363,582 records with FM metrics)

  monarch_tagging_exploratory.py
    → monarch_tagging_summary.csv
    → monarch_high_risk_locations.csv
    → findings documented here

series_position:
  Document 1: fcc_lms_reproducibility
  Document 2: fm_field_density how-to
  Document 3: monarch_tagging_
               exploratory_findings
               (preliminary)
  Document 4: THIS DOCUMENT
               (complete findings
               and procedure record)
  Document 5: [pending]
               statistical test results
               on Monarch Watch
               recovery data
```

---

## PART I: THE QUESTION

Monarch butterflies navigate from
breeding grounds across eastern
North America to a specific mountain
range in Michoacán, Mexico — a
journey of up to 4,500 km completed
by individuals that have never made
the trip before.

The navigation system has two
components:

**Component 1: Sun compass**
Primary orientation mechanism
under clear skies. Uses the sun's
position combined with an internal
circadian clock to maintain a
consistent southwesterly heading.

**Component 2: Magnetic compass**
Sole orientation mechanism under
overcast conditions (PLOS ONE 2025,
University of Cincinnati). Uses the
inclination angle of Earth's
geomagnetic field. Operates via
the radical pair mechanism in
cryptochrome photoreceptor proteins.

The radical pair mechanism is
sensitive to radiofrequency
electromagnetic fields in the MHz
range. Published laboratory and
theoretical work has shown that
RF fields at these frequencies
can disrupt radical pair spin
dynamics, corrupting the compass
signal (Springer 2023: "Insect
magnetoreception: a Cry for
mechanistic insights").

FM broadcast radio operates at
87.5–108 MHz.

The United States FM broadcast
infrastructure distributes
approximately 10,000 licensed
transmitters across the monarch
migration corridor.

**The question this analysis asks:**

At each monarch tagging location,
the FM broadcast field is not
uniform — it is stronger in the
direction of the nearest high-power
transmitter clusters. If FM signals
disrupt the magnetic compass, the
disruption is directional: the
compass is pulled toward the
strongest FM source rather than
toward magnetic north.

Does the direction of maximum FM
exposure at Monarch Watch tagging
locations predict the direction
of bearing deviation in recovered
monarchs?

**That is the hypothesis. The
statistical test requires recovery
data not yet in hand. What this
document reports is the first
step: characterizing the FM
electromagnetic landscape across
every monarch tagging location
in the Monarch Watch history and
identifying where the false
attractor effect, if real, should
be strongest and most detectable.**

---

## PART II: COMPLETE REPRODUCIBLE
## PROCEDURE

### Step 1: Build FM station table

**Source:**
FCC LMS public database
fcc.gov/media/media-bureau-
public-databases
Download: Current_LMS_Dump.zip
Snapshot used: February 26, 2026

**Tables joined:**
```
facility.dat
application_facility.dat
app_location.dat
app_antenna.dat
```

**Join logic:**
```python
facility
→ join app_facility
  on facility_id
→ join app_location
  on application_id
→ join app_antenna
  on application_id
```

**Filters applied:**
```python
active_ind == 'Y'
service_code in ['FM','FL','FX','LD']
aloc_active_ind == 'Y'
aloc_valid_ind == 'Y'
frequency_mhz between 87.5 and 108.0
tx_lat is not null
tx_lon is not null
```

**ERP proxy computation:**
```python
erp_proxy = power_output_w
if power_output_w > 0
else haat_m × 10.0
if haat_m > 0
else 0
```

**Result:**
```
fm_stations_clean.csv
8,136 FM stations
Columns: callsign, frequency_mhz,
         tx_lat, tx_lon, erp_proxy
```

**Verification:**
```
python build_fm_station_table.py
Expected: "Stations saved: 8,136"
```

---

### Step 2: Build FM field density
### function

**Script:** fm_field_density.py
**Class:** FMFieldDensity

**Algorithm for one location (lat, lon):**

```
1. DISTANCE FILTER
   Haversine distance from (lat,lon)
   to all 8,136 stations.
   Keep stations within 200km.
   Vectorized — no Python loop.

2. BEARING COMPUTATION
   Geodesic bearing from (lat,lon)
   to each station within radius:
   bearing = arctan2(
     sin(Δlon)·cos(lat2),
     cos(lat1)·sin(lat2) −
     sin(lat1)·cos(lat2)·cos(Δlon)
   ) → 0–360°

3. WEIGHT ASSIGNMENT
   weight = erp_proxy / distance_km²
   (ERP proxy in watts,
    inverse-square distance decay,
    consistent with free-space
    propagation)

4. AZIMUTH DISTRIBUTION
   360-element array.
   Each station deposits its weight
   into the bin at its bearing.
   numpy.add.at() — no Python loop.

5. GAUSSIAN SMOOTHING
   sigma = 10°, circular boundary.
   Models angular spread of FM
   signal propagation.

6. PEAK DETECTION
   false_attractor_bearing =
   bearing of maximum bin
   in smoothed distribution.

7. STRENGTH COMPUTATION
   strength = max_bin / sum_all_bins
   Fraction of total FM exposure
   in the dominant direction.
```

**Parameters (fixed, not adjusted
after results were seen):**
```
radius_km = 200
FM band = 87.5–108.0 MHz
gaussian sigma = 10°
distance decay = inverse square
```

---

### Step 2 verification output
### (confirmed, February 26–27, 2026)

**Run command:**
```bash
python fm_field_density.py
```

**Confirmed output:**
```
FMFieldDensity ready.
  Stations loaded: 8,136
  Influence radius: 200 km

── Lawrence KS — Monarch Watch HQ ──
Location:     38.9717°N, -95.2353°
Stations:     80
FM exposure:  222.77 proxy W·km⁻²
FALSE ATTRACTOR BEARING: 274.0° (W)
Strength:     0.0118
Top station:  WIBW-FM 94.5MHz
              59.2km bearing 276.1°
              weight 28.50

── Cape May NJ ──
Location:     38.9351°N, -74.9060°
Stations:     185
FM exposure:  212.73 proxy W·km⁻²
FALSE ATTRACTOR BEARING: 34.0° (NE)
Strength:     0.0094
Top station:  WDDE 91.1MHz
              56.3km bearing 275.7°
              weight 15.80

── Peninsula Point MI ──
Location:     45.7741°N, -86.9530°
Stations:     96
FM exposure:  473.15 proxy W·km⁻²
FALSE ATTRACTOR BEARING: 271.0° (W)
Strength:     0.0214
Top station:  [unnamed] 88.1MHz
              14.6km bearing 272.5°
              weight 236.10

── Corpus Christi TX ──
Location:     27.8006°N, -97.3964°
Stations:     80
FM exposure:  1685.89 proxy W·km⁻²
FALSE ATTRACTOR BEARING: 232.0° (SW)
Strength:     0.0287
Top station:  KBAE-LP 89.1MHz
              2.3km bearing 230.6°
              weight 569.01

── Presqu'ile ON ──
Location:     44.0000°N, -77.7167°
Stations:     70
FM exposure:  34.97 proxy W·km⁻²
FALSE ATTRACTOR BEARING: 204.0° (SSW)
Strength:     0.0126
Top station:  WCOM-FM 90.7MHz
              96.7km bearing 201.2°
              weight 5.35

Batch result summary:
  Lawrence KS:      274.0° n=80
  Cape May NJ:       34.0° n=185
  Peninsula Point:  271.0° n=96
  Corpus Christi:   232.0° n=80
  Presqu'ile ON:    204.0° n=70

Field density function verified.
```

---

### Step 3: Load GBIF monarch data
### and compute FM metrics

**Script:**
monarch_false_attractor_analysis.py

**Input files:**
```
fm_stations_clean.csv
occurrence.txt (GBIF download,
  unzipped)
```

**What the script does:**
```
1. Load occurrence.txt (tab-delimited)
   363,582 records detected

2. Parse eventDate → tag_year,
   tag_month, tag_day

3. Extract tagging coordinates
   (decimalLatitude, decimalLongitude)

4. Compute expected_bearing for
   each record — geodesic bearing
   from tagging location to
   overwintering centroid
   (19.5°N, 100.3°W —
   Sierra Chincua, Michoacán)

5. Deduplicate to unique locations
   on 1km grid (round to 2 decimal
   places): 363,582 records →
   3,074 unique locations

6. Run FMFieldDensity.compute_batch()
   on 3,074 unique locations
   (~7 minutes runtime)

7. Join FM metrics back to all
   363,582 records

8. Save monarch_with_fm.csv
   BEFORE any filtering
   (this was a v1 bug — fixed in v2)

9. Run statistical test
   (returns 0 records — GBIF dataset
   contains no recovery coordinates)
```

**Run command:**
```bash
python monarch_false_attractor_analysis.py
```

**Confirmed output (key lines):**
```
Total rows: 363,582
Records with coordinates: 363,582
Recovery coordinates: 0
  (GBIF dataset — tagging only)

Unique locations (1km grid): 3,074
Computing FM field density for
3,074 locations...
  Done. 3,074 locations processed.
  Locations with FM coverage: 3,069
  Mean stations per location: 166.2

Saved full dataset (363,582 records)
→ monarch_with_fm.csv

WARNING: < 30 records.
Send Monarch Watch data request
to obtain recovery coordinates.
```

**Output file:**
```
monarch_with_fm.csv
363,582 records
Columns:
  tag_lat, tag_lon
  tag_year, tag_month, tag_day
  occurrenceID, verbatimLocality
  stateProvince, country
  recordedBy
  rec_lat, rec_lon
    (all NaN — GBIF tagging only)
  expected_bearing
  actual_bearing (all NaN)
  displacement_km (all NaN)
  bearing_deviation (all NaN)
  fm_false_attractor_bearing
  fm_false_attractor_strength
  fm_total_exposure
  fm_n_stations
```

---

### Step 4: Exploratory analysis

**Script:**
monarch_tagging_exploratory.py

**Input file:**
monarch_with_fm.csv

**Run command:**
```bash
python monarch_tagging_exploratory.py
```

**What the script computes:**
```
1. FM opposition angle for each record
   opposition = |circular_difference(
     fm_false_attractor_bearing,
     expected_bearing
   )|
   0°   = FM aligned with migration
   180° = FM directly opposed

2. Seasonal breakdown by tag_month

3. Geographic breakdown by state

4. High-risk location identification
   Criteria:
     opposition > 120°
     fm_strength > 0.01

5. Year-over-year table (1992–2000)

6. Cape May spotlight
```

**Outputs saved:**
```
monarch_tagging_summary.csv
  — full dataset with opposition
    angle added

monarch_high_risk_locations.csv
  — 805 high-risk locations
    ranked by n_monarchs
```

---

## PART III: CONFIRMED FINDINGS

### Finding 1: Coverage

```
Total records:          363,582
Records with FM data:   363,034
Coverage:               99.8%

Unique tagging locations
  (1km grid):           3,074
Locations with FM data: 3,069

Mean FM stations within
  200km per location:   166.2
```

The FM broadcast infrastructure
covers essentially the entire
Monarch Watch tagging range.
Only 5 of 3,074 unique locations
lack FM coverage — remote areas
far from any broadcast market.
This is not a sparse signal.
It is a pervasive one.

---

### Finding 2: Mean opposition

```
Mean FM opposition angle:    85.5°
Median FM opposition angle:  74.4°
```

Across all 363,582 monarch tagging
records, the FM false attractor
bearing is on average 85.5° away
from the correct migration direction.
The correct migration direction is
roughly SW (200–240° depending on
location). The FM false attractor
is, on average, nearly perpendicular
to where the monarchs need to go.

This is the baseline characterization
of the FM electromagnetic landscape
across the migration corridor. It
has never been published before.

---

### Finding 3: Scale of high-risk
### exposure

```
Records with FM opposition > 90°:
  149,462  (41.1%)

Records with FM opposition > 120°
AND FM strength > 0.01
(high-risk population):
  102,286  (28.1%)
  805 distinct locations
```

28.1% of all monarchs tagged in
the Monarch Watch program between
1992 and 2000 were tagged at
locations where the FM false
attractor bearing strongly opposes
the correct migration direction and
the FM signal has sufficient
directional coherence to produce
a detectable compass deflection.

---

### Finding 4: Seasonal pattern

```
Month   N        Mean Opp
Aug     29,188   91.8°
Sep     247,800  81.2°
Oct     77,562   95.1°
Nov     5,372   112.8°
Dec     840     111.4°
```

Peak migration months (August–
October) show mean opposition of
81–95°. Late season stragglers
(November–December) show elevated
opposition of 111–113°.

The November/December elevation
is the most interpretively
interesting feature of the seasonal
data. Two explanations exist:

**Geographic explanation (conservative):**
Late-season tagging locations are
in southern states where the local
FM market structure produces higher
opposition angles. The elevation
reflects where people are tagging
late monarchs, not a behavioral
effect.

**Behavioral explanation (stronger):**
FM deflection causes some monarchs
to deviate from the correct migration
bearing, fail to depart on schedule,
and are tagged late in the season
as stragglers — still in the high-
opposition FM environment they never
escaped.

These explanations are not
distinguishable with tagging data
alone. Recovery data resolves them:
if late-season monarchs show stronger
bearing deviation aligned with FM
false attractor bearing, the
behavioral explanation is supported.

---

### Finding 5: Geographic pattern

```
State   N        Mean Opp   Notes
OK      15,344   142.6°     HIGHEST
SD      5,494    125.4°
NJ      5,010    123.2°
WI      9,436    109.7°
CT      6,437    103.6°
FL      6,880     99.1°
TX      19,015    99.7°
IA      31,506    92.3°
IL      7,042     96.5°
PA      16,316    91.3°
```

**Oklahoma is the critical finding
in the geographic breakdown.**

15,344 monarchs tagged in Oklahoma
face a mean FM opposition angle of
142.6° — the highest of any major
tagging state. The Oklahoma City
FM broadcast market creates a
systematic northward false attractor
across the central flyway at the
exact latitude monarchs must cross
during peak fall migration.

Ontario (ON) shows the lowest
mean opposition at 49.5° — FM
exposure there is more aligned
with or perpendicular to the
migration direction. This will
be important as an internal
control: if FM false attractor
effects are real, Ontario-tagged
monarchs should show less bearing
deviation than Oklahoma-tagged
monarchs.

---

### Finding 6: Top high-risk sites

The twenty highest-priority sites
for the recovery analysis, ranked
by tagging volume:

```
RANK 1:
  Location:  35.47°N, 97.52°W
  State:     Oklahoma
  N tagged:  9,482
  FM bearing:  13° (NNE)
  Expected:   189° (SSW)
  Opposition: 176.5°
  Strength:   0.021

  The single most important site
  in the dataset. 9,482 monarchs.
  FM bearing is 13° — nearly due
  north. Correct migration bearing
  is 189° — nearly due south.
  Opposition of 176.5° is the
  closest to perfect reversal of
  any high-volume site.

RANK 2:
  Location:  38.84°N, 97.61°W
  State:     Kansas (Salina area)
  N tagged:  3,532
  FM bearing:    0° (N)
  Expected:   188° (SSW)
  Opposition: 172.4°
  Strength:   0.037

  Highest FM strength value among
  all top sites. FM bearing is due
  north. Strength 0.037 means the
  northward signal is more coherent
  here than anywhere else in the
  top 20. The most discriminating
  site for the recovery test.

RANK 3:
  Location:  38.88°N, 99.33°W
  State:     Kansas
  N tagged:  3,881
  FM bearing:  322° (NW)
  Expected:   183° (S)
  Opposition: 139.2°
  Strength:   0.032

RANK 4:
  Location:  32.66°N, 79.94°W
  State:     South Carolina
  N tagged:  3,477
  FM bearing:   30° (NNE)
  Expected:   239° (WSW)
  Opposition: 150.8°
  Strength:   0.036

  Eastern flyway site. Charleston-
  area FM market. Second highest
  strength in top 20.

RANK 5 (most extreme opposition):
  Location:  41.57°N, 71.07°W
  State:     Massachusetts
  N tagged:  995
  FM bearing:   58° (ENE)
  Expected:   237° (WSW)
  Opposition: 179.2°
  Strength:   0.017

  THE MOST EXTREME OPPOSITION
  IN THE ENTIRE DATASET.

  179.2° — FM bearing is almost
  exactly opposite the correct
  migration direction.
  Boston/Providence FM market
  creates a strong ENE false
  attractor. Correct direction
  is WSW toward Mexico.

  Under H1, monarchs tagged here
  should be recovered to the ENE
  of their tagging location.
  The predicted recovery bearing
  is 58°. The expected migration
  bearing is 237°. These are
  nearly perfectly opposed.

  995 monarchs tagged here —
  sufficient for a meaningful test
  if recovery coordinates exist.
```

---

### Finding 7: Cape May

```
Location:  38.9°N, 74.9°W
State:     New Jersey
N tagged:  804
Year range: 1992–2000
FM bearing:  34° (NNE)
Expected:   235.7° (SW)
Opposition: 158.3°
Strength:   0.0095
```

Cape May is the most studied monarch
stopover site in the eastern flyway.
Decades of published behavioral
observation exist (Walton, Brower
& Davis 2005 being the primary
long-term monitoring study).

The FM false attractor bearing at
Cape May is 34° (NNE). The correct
migration bearing is 236° (SW).
Opposition is 158.3°.

However FM strength is 0.0095 —
the lowest of any named site in
this analysis. This is because
Cape May is surrounded by
transmitters on multiple sides
(Philadelphia, Wilmington, Atlantic
City, Baltimore) — the exposure
is spread across many directions
rather than concentrated in one.

**The hypothesis therefore predicts
a small or undetectable Cape May
effect specifically.** The low
strength means that even if FM
disruption is real, the directional
signal at Cape May is weak. The
absence of a published northward
departure anomaly at Cape May
(confirmed by literature search,
February 27, 2026) is consistent
with this prediction.

This is an important internal
consistency check. A hypothesis
that predicts large effects
everywhere is not falsifiable.
This hypothesis predicts large
effects at Oklahoma and Kansas
(high opposition, moderate-high
strength) and small effects at
Cape May (high opposition, low
strength). The Cape May literature
is consistent with the small-effect
prediction.

---

### Finding 8: Year-over-year

```
Year   N        Mean Opp
1992   3,937    87.1°
1993   4,845    71.9°
1994   7,132    77.6°
1995   13,877   87.3°
1996   46,824   78.3°
1997   70,232   83.7°
1998   60,776   87.8°
1999   81,456   87.8°
2000   73,955   88.7°
```

Mean FM opposition is consistent
across the 1992–2000 period at
approximately 80–88°.

**Important limitation acknowledged:**
This table uses the 2026 FCC database
for all years. The FM landscape in
1992 differed from 2026 — stations
were added and decommissioned over
this period. This table therefore
reflects changes in tagging location
geography over time, not changes
in FM infrastructure.

The slight upward trend in mean
opposition from 1993 to 2000 likely
reflects the geographic expansion
of the Monarch Watch tagging program
into states (Oklahoma, Kansas) with
higher FM opposition, rather than
increasing FM infrastructure.

A proper historical analysis would
require year-specific FCC license
data. This is identified as a
priority for future work.

---

## PART IV: WHAT THESE FINDINGS
## CONFIRM AND WHAT THEY DO NOT

### What is confirmed:

1. The FM broadcast infrastructure
   across the monarch migration
   corridor is systematically
   misaligned with the correct
   migration direction. Mean
   opposition 85.5° is not a
   coincidence of geography — it
   reflects the distribution of
   broadcast markets relative to
   the SW migration bearing.

2. 28.1% of all monarchs in the
   Monarch Watch tagging history
   (1992–2000) were tagged at
   locations where FM false attractor
   bearing strongly opposes correct
   migration bearing AND the FM
   directional signal is coherent
   enough to produce detectable
   deflection.

3. The geographic pattern of FM
   opposition is not random. Oklahoma
   and Kansas — the central flyway
   corridor — show the highest mean
   opposition. Ontario — an expected
   low-opposition control region —
   shows the lowest.

4. The site-level predictions are
   internally consistent. Cape May
   shows high opposition but low
   strength → predicted small effect.
   Oklahoma shows high opposition
   and moderate strength → predicted
   large effect.

5. The analysis infrastructure is
   complete. FM false attractor
   bearing is computed and archived
   for every Monarch Watch tagging
   location. When recovery data
   arrives, the statistical test
   runs immediately with no further
   setup required.

### What is not yet confirmed:

1. That FM signals actually disrupt
   monarch magnetic compass
   orientation in the field.
   The mechanistic evidence exists
   in the laboratory literature
   but has not been demonstrated
   in free-flying monarchs.

2. That the bearing deviation of
   recovered monarchs aligns with
   the FM false attractor bearing.
   This is the primary hypothesis.
   It requires recovery coordinates.
   Recovery data has been requested
   from Monarch Watch (email sent
   February 28, 2026).

3. That FM disruption contributes
   to monarch population decline.
   This would require not just
   showing directional deflection
   but also showing that deflection
   increases overwintering failure
   rates — a further analysis
   beyond the scope of this study.

---

## PART V: WHAT COMES NEXT

### Immediate (waiting):

Monarch Watch data response.
The email requesting paired
tag-recovery coordinates was sent
February 28, 2026.
When recovery data arrives, the
statistical test in
monarch_false_attractor_analysis.py
runs once and reports results.

### Parallel work (can start now):

**Visualization:**
Map of all 805 high-risk tagging
locations with FM false attractor
bearing shown as arrows. This is
Figure 1 of any manuscript. The
data exists in
monarch_high_risk_locations.csv.

**Literature synthesis:**
Four-paper mechanistic backbone:
  Wiltschko et al. (robin RF
  disruption experiments)
→ Ritz et al. (radical pair
  mechanism theory)
→ Reppert lab (monarch cryptochrome
  characterization)
→ This analysis (population-level
  field consequence prediction)

**Second species:**
The attractor pollution framework
applies to sea turtle AM compass
disruption. NOAA sea turtle
stranding database + FCC AM
transmitter database = same
pipeline, different species.
AM band (530–1700 kHz) overlaps
with frequencies disrupting sea
turtle magnetoreception.

**Historical FCC data:**
Year-specific FCC license records
would allow computing the FM
landscape as it existed at the
time of each tagging event
(1992–2000) rather than using
the 2026 database. This eliminates
the temporal mismatch limitation
and would produce a less attenuated
effect estimate.

---

## PART VI: REPRODUCTION INSTRUCTIONS

A researcher starting from scratch
can reproduce all findings in this
document by following these steps:

```
STEP 1: Download FCC LMS data
  URL: fcc.gov/media/
       media-bureau-public-databases
  File: Current_LMS_Dump.zip
  Unzip to working directory

STEP 2: Run station table builder
  python build_fm_station_table.py
  Expected output: 8,136 stations
  Output file: fm_stations_clean.csv

STEP 3: Verify FM field density
  python fm_field_density.py
  Expected: bearings matching
  verified output in Part II above

STEP 4: Download GBIF monarch data
  URL: gbif.org/dataset/
       cf7d6c01-309b-4545-8319-
       3d53b1e8bfd0
  Download Darwin Core Archive
  Unzip — find occurrence.txt
  Place in working directory

STEP 5: Run main analysis
  python monarch_false_attractor_
  analysis.py
  Runtime: ~10 minutes
  Expected: 363,582 records,
  3,074 unique locations,
  monarch_with_fm.csv saved

STEP 6: Run exploratory analysis
  python monarch_tagging_exploratory.py
  Expected output: matches findings
  documented in Part III above

TOTAL RUNTIME: ~15 minutes
COST: $0.00
ALL DATA: public domain
ALL CODE: documented in this series
```

---

## PART VII: PRE-REGISTRATION
## RECORD

```
Platform: OSF (Open Science
  Framework)
Filed: February 26, 2026
Status: Finalized (immutable)

Primary hypothesis registered:
  The alignment_angle distribution
  (bearing_deviation minus
  fm_false_attractor_bearing)
  is non-uniform and concentrated
  near 0°. V-test p < 0.05,
  one-tailed, predicted direction
  = 0°.

Primary test sites registered:
  Norman/OKC OK (35.47°N, 97.52°W)
    n=9,482, opposition 176.5°
  Salina KS (38.84°N, 97.61°W)
    n=3,532, opposition 172.4°
  Massachusetts (41.57°N, 71.07°W)
    n=995, opposition 179.2°

Quartile boundaries registered
(amendment, same date):
  Q1/Q2: fm_strength < 0.012318
  Q2/Q3: fm_strength < 0.018706
  Q3/Q4: fm_strength < 0.024320

Analysis will run once on arrival
of recovery data and results will
be reported regardless of outcome.
```

---

## PART VIII: ACKNOWLEDGMENTS
## AND CONNECTIONS

**Data providers:**
Monarch Watch — tagging program
  that produced the 363,582 records
  analyzed here. This analysis
  would not exist without their
  three decades of field work.

GBIF — open access infrastructure
  making the Monarch Watch dataset
  publicly available.

FCC — public release of the LMS
  database enabling FM transmitter
  coordinate extraction.

**Mechanistic foundation:**
The Reppert lab at UMass Chan
Medical School — characterization
of monarch cryptochrome and
magnetic compass.

The Wiltschko lab — RF disruption
experiments in European robins
establishing the mechanistic
precedent for this analysis.

The SixthSense Horizon Europe
project (ID: 101149007) — active
2025 research program on
electromagnetic disruption of
magnetoreception in migratory
species. Parallel mechanistic
work that complements this
population-level analysis.

**Framework:**
OrganismCore attractor pollution
framework — Eric Robert Lawson,
2026. This analysis is one
instance of the broader framework
applied to one species and one
frequency band.

---

## VERSION

```
v1.0 — February 26, 2026
First complete findings record.
Status: pre-recovery-data.
All findings are from tagging
dataset characterization only.
The statistical test is pre-
registered and pending recovery
data arrival.

Next version (v2.0) will be
filed when recovery data arrives
and the statistical test runs.
v2.0 will include the primary
result regardless of outcome.
```
