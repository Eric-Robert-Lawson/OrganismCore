# DESK ANALYSIS START GUIDE
## What Is Immediately Accessible,
## In What Order, With What Actions
## February 27, 2026

---

## THE SINGLE ORGANIZING PRINCIPLE

Every analysis here begins with
data that is already public.
No new experiments. No animals.
No funding. No institutional access.
A laptop and an internet connection.

Ranked by how fast you can
have data in hand and code running.

---

## TIER 0: TODAY — DATA IN HAND
## WITHIN THE HOUR

### Analysis 1: FCC FM Database
### (The Monarch Butterfly Prerequisite)

**What it is:**
Every FM broadcast station in
the United States — call sign,
frequency, latitude, longitude,
effective radiated power (ERP),
antenna height, tower azimuth.

**Where it is:**
https://www.fcc.gov/media/media-bureau-public-databases

The FCC Media Bureau Public
Databases page. Scroll to
"FM Service" under the broadcast
section. The raw data file is
a pipe-delimited text export
of the entire FM station database.
Updated daily. Free. No login.
No request required.

The file you want:
FM_SERVICE.dat or equivalent
from the LMS (Licensing and
Management System) export.

Alternatively: FCCdata.org
aggregates and presents this
in a cleaner format with
direct CSV download.

**What you download:**
- Station call sign
- Frequency (MHz)
- Latitude (decimal degrees)
- Longitude (decimal degrees)
- ERP (watts)
- Antenna height above ground (m)
- Antenna height above mean sea level (m)
- Directional/omnidirectional flag
- Azimuth of maximum radiation
  (for directional antennas)

**Time to download:** 5 minutes.
**File size:** ~5 MB.
**Format:** CSV / pipe-delimited text.

**What this unlocks:**
This is the transmitter database
for the Monarch Watch false
attractor analysis. Once you
have this file, you can compute
the FM field density at any
geographic coordinate in the US.

You do not need Monarch Watch
data to start on this file.
Start here. Build the FM field
density function first.

---

### Analysis 2: GBIF Monarch Watch Dataset
### (Partial — start here, request
### full data in parallel)

**What it is:**
Monarch Watch tagging and
recovery occurrence records
shared to GBIF. Each record
has a tagging GPS coordinate
and, where recovered, a recovery
GPS coordinate.

**Where it is:**
https://www.gbif.org/dataset/cf7d6c01-309b-4545-8319-3d53b1e8bfd0

Click "Download" on the dataset
page. Select "Darwin Core Archive"
for the full structured export,
or "Simple CSV" for immediate use.

No login required for small
downloads. Free GBIF account
(2 minutes to create) required
for bulk downloads.

**What you get:**
~500,000+ occurrence records
across decades of Monarch Watch
tagging. Not all have recovery
coordinates — those that do
are the analysis population.

**Caveat from the search:**
Most recent records may lag by
1–2 years. 2024 data may not
yet be in GBIF. But the historical
dataset going back to the 1990s
is sufficient to test the hypothesis.
The FM transmitter network has
been substantially stable for
20+ years — the false attractor
effect, if real, should appear
across the historical record.

**Time to download:** 10–15 minutes
including account creation.

**Action in parallel:**
Send the Monarch Watch data
request email (drafted in
monarch_butterfly.md). The full
database with matched tag/recovery
coordinates is the gold standard.
The GBIF dataset is the start
while you wait.

---

### Analysis 3: IMPC Spatial Navigation
### (The Dark Archive Mouse Data)

**What it is:**
The International Mouse Phenotyping
Consortium's publicly licensed
behavioral phenotyping database.
CC BY 4.0 — completely free for
research and publication.

Data Release 23 (April 2025) is
the current version.

**Where it is:**
https://www.mousephenotype.org/understand/accessing-the-data/

The IMPC API allows direct
programmatic queries. The FTP
site has bulk downloads.

**What you want:**
Behavioral phenotyping data for
spatial navigation procedures.
Specifically:
- Open field test data
  (locomotion, thigmotaxis)
- Any maze phenotyping
  (if available in the pipeline)
- Facility location for each
  data point (which IMPC center
  collected it)

**The critical field:**
Facility / phenotyping center.
This is the variable that
maps to ambient ELF level.

IMPC centers include:
- Wellcome Sanger Institute (UK)
- Jackson Laboratory (Bar Harbor, Maine)
- UC Davis (California)
- Toronto Centre for Phenogenomics
- MRC Harwell (UK)
- RIKEN BRC (Japan)
- And ~15 others

Each facility is a building.
Each building has a known address.
Each address has a reconstructable
ambient ELF environment based on:
proximity to high-voltage power lines,
floor level in building,
era of building construction,
equipment density.

**Time to first query:**
20 minutes using the IMPC API.

The specific API call:
Query for behavioral data
(procedure: "Open Field" or
equivalent) grouped by
phenotyping center.
Output: N per center,
mean locomotion, mean thigmotaxis,
variance.

This gives you the facility-level
behavioral data that you will
correlate against estimated
ambient ELF once you have
the ELF estimates.

---

## TIER 1: THIS WEEK —
## ONE EMAIL, ONE CONTACT,
## BUILDING THE ANALYSIS PIPELINE

### The Monarch Watch Email

The monarch_butterfly.md document
has a drafted email. The recipient
is Monarch Watch's data team.

The request: access to the full
tagging + recovery database
for research purposes, specifically
the paired tag/recovery coordinates
with GPS precision.

Monarch Watch is a citizen science
organization — they share data
with researchers. The request is
standard. They have a form on
their website for research data
requests.

**Send this week.**

The analysis is written. The code
is drafted. The only thing missing
is the complete paired dataset.
The GBIF partial dataset is
enough to start. The full dataset
is what you need for the
publishable result.

---

### The FWC Sea Turtle Contact

The Florida Fish and Wildlife
Conservation Commission maintains
the sea turtle disorientation
and stranding database.

The invisible_channel_sea_turtles.md
document identifies the specific
gap: the database tracks
light-induced disorientation
comprehensively but has no field
for magnetic anomaly or cable proximity.

The desk analysis here is:
1. Obtain the FWC disorientation
   database (public records request
   or researcher access — FWC
   shares this data with researchers)
2. Obtain the submarine cable
   infrastructure map for Florida
   coastal waters (publicly available
   from NOAA and cable operators)
3. Compute: for each disorientation
   event, what is the distance to
   the nearest submarine cable?
4. Ask: is the disorientation rate
   elevated within X km of cable
   routes vs. equivalent beaches
   further from cable routes,
   controlling for light pollution?

This is a spatial analysis using
two public datasets. It requires
no new data collection.

**The request email:**
Address to FWC Marine Turtle
Program, requesting the
disorientation database for
research purposes. Standard
researcher data request. They
have a formal data sharing process.

---

### Building the FM Field Density
### Function (Python, ~2 hours)

Once you have the FCC FM database,
the first computational task is
building the function that computes
FM field density at any geographic
coordinate.

The function inputs:
- Target latitude, longitude
- Radius of influence (km)
  — for radical pair window:
  FM carrier frequency (87.5–108 MHz)
  attenuates with distance;
  the relevant radius for
  biological effect is ~50–100 km
  based on field strength
  calculations

The function outputs:
- Total azimuth-weighted ERP
  within radius
- Direction of maximum field density
  (the false attractor bearing)
- Field density by azimuth sector

This is standard geospatial
computation. Libraries needed:
- `geopy` or `pyproj` for
  coordinate math
- `numpy` / `pandas` for
  the station data
- `scipy.spatial` for distance
  calculations

Estimated time to working function:
2–3 hours from FCC data download.

Once the function exists, you
can compute the false attractor
bearing for every tagging location
in the Monarch Watch dataset
in a single vectorized pass.

---

## TIER 2: WEEK TWO —
## RUNNING THE ANALYSES

### Monarch Watch False Attractor
### Analysis: Step by Step

**Inputs by day 7:**
- FCC FM database: ✓ (downloaded day 1)
- FM field density function: ✓ (built days 2–3)
- GBIF Monarch Watch data: ✓ (downloaded day 1)
- NOAA HRRR wind data: download
  from https://registry.opendata.aws/noaa-hrrr-pds/
  (free, AWS open data)

**The analysis pipeline
(from monarch_butterfly.md):**

```python
# Pseudocode — full code in
# monarch_butterfly.md

for each tagged_monarch with recovery:
  
  # Step 1: Compute expected bearing
  expected_bearing = great_circle_bearing(
    from=tag_location,
    to=overwintering_centroid  # 19.5°N, 100.3°W
  )
  
  # Step 2: Compute actual bearing
  actual_bearing = great_circle_bearing(
    from=tag_location,
    to=recovery_location
  )
  
  # Step 3: Compute angular deviation
  deviation = circular_difference(
    actual_bearing, expected_bearing
  )
  
  # Step 4: Compute FM false attractor bearing
  fm_attractor_bearing = fm_field_density(
    location=tag_location,
    radius_km=100
  ).direction_of_maximum
  
  # Step 5: Compute alignment between
  # deviation and FM attractor bearing
  alignment = circular_difference(
    deviation, fm_attractor_bearing
  )

# Step 6: Test: is alignment
# systematically near zero?
# (monarchs deviate TOWARD FM sources)
circular_mean_test(alignment_distribution)
```

**Expected output:**
If the false attractor hypothesis
is correct: the distribution of
`alignment` values will be
concentrated near zero — monarchs
deviate in the direction of the
local FM density maximum.

If null: `alignment` values are
uniformly distributed — deviations
are uncorrelated with FM attractor direction.

**Wind correction:**
Before testing, regress out
wind drift using NOAA HRRR
reanalysis at tagging location
and date. This is the critical
confound control — wind can
push butterflies off course
independently of compass error.
The residual after wind correction
is the compass error signal.

**Pre-registration:**
Before running the analysis,
upload the pre-registration text
from monarch_butterfly.md to
OSF (https://osf.io) — free,
takes 10 minutes. This locks
the prediction before you see
the result. It is what makes
the finding credible rather than
a pattern-match in existing data.

---

### IMPC ELF Correlation Analysis:
### Step by Step

**Inputs:**
- IMPC behavioral data by facility: ✓
- Facility addresses: extractable
  from IMPC documentation
- Ambient ELF estimates by facility:
  requires construction

**The ELF estimation approach:**

You cannot directly measure the
ambient ELF of a laboratory that
ran experiments 10 years ago.
But you can estimate it from:

**Tier A: Distance to high-voltage
power lines**

The US Energy Information Administration
and state utility GIS databases have
transmission line locations. The EIA
has a national transmission line map:
https://atlas.eia.gov/datasets/eia::transmission-lines/

For each IMPC facility address:
compute distance to nearest
high-voltage transmission line
(>115 kV). ELF field falls off
with distance. Facilities within
100m of a transmission line have
substantially higher ambient ELF
than facilities 1 km away.

This is a proxy, not a measurement.
It is directionally reliable.

**Tier B: Building era and floor level**

Older buildings with knob-and-tube
or early conduit wiring have
higher ambient ELF from unbalanced
wiring than modern buildings with
balanced wiring.

Floor level matters: basement labs
are closer to building electrical
infrastructure than upper-floor labs.
Some IMPC center publications mention
the specific room or floor.

**Tier C: Equipment density**

Research facilities with heavy
imaging equipment (MRI scanners,
electron microscopes) in adjacent
rooms have elevated ambient ELF
from transformer loads. This
varies by facility.

**The correlation test:**
Construct an ELF proxy score for
each facility. Correlate with
mean behavioral phenotype outcome
(locomotion in open field, any
available spatial navigation metric).

**Prediction:**
Facilities with higher estimated
ambient ELF show more variable
and less consistent spatial
navigation phenotypes — because
the ELF is corrupting the compass
input that contributes to the
navigation.

If the correlation is significant:
four decades of "methodological
variability" have a structural
explanation. This is a publishable
finding. The dark archive has
yielded its first signal.

---

## TIER 3: WITHIN THE MONTH —
## SYNTHESIS AND SUBMISSION

### What the two analyses produce:

**Monarch Watch result + FCC database:**
Either the first empirical evidence
that FM broadcast infrastructure
constitutes a false attractor for
monarch compass navigation — or
the first well-powered null result
that falsifies the hypothesis at
scale. Both are publishable.
Target journal: *Current Biology*,
*PNAS*, or *Biology Letters*
depending on effect size.

**IMPC + ELF analysis:**
Either the identification of
ambient electromagnetic environment
as the uncontrolled variable
explaining four decades of
contradictory rodent navigation
literature — or a null result
that rules it out. Both are
publishable. Target journal:
*eLife*, *PLOS ONE*, or
*Scientific Reports* depending
on the effect size and scope.

**The combination:**
Two independent analyses from
the same theoretical framework,
submitted together or in rapid
succession, constitute the
first empirical program built
on the attractor pollution concept.
The convergence of two independent
results strengthens both.

---

## THE COMPLETE IMMEDIATE ACTION LIST

```
TODAY:
  □ Download FCC FM database
    from fcc.gov/media/media-bureau-public-databases
    Time: 5 minutes
    
  □ Download GBIF Monarch Watch dataset
    from gbif.org/dataset/cf7d6c01...
    Time: 15 minutes including
    free account creation
    
  □ Query IMPC API for behavioral
    data by phenotyping center
    from mousephenotype.org/understand/
    accessing-the-data/
    Time: 30 minutes
    
  □ Pre-register Monarch Watch
    analysis on OSF (osf.io)
    Text is in monarch_butterfly.md
    Time: 15 minutes

THIS WEEK:
  □ Send Monarch Watch full data
    request email
    Draft is in monarch_butterfly.md
    Time: 10 minutes
    
  □ Send FWC sea turtle database
    request email
    Contact: FWC Marine Turtle Program
    Time: 10 minutes
    
  □ Build FM field density function
    in Python using FCC database
    Time: 2–3 hours
    
  □ Build facility ELF proxy table
    from IMPC facility addresses +
    EIA transmission line GIS data
    Time: 3–4 hours

WEEK TWO:
  □ Run Monarch Watch false attractor
    analysis on GBIF dataset
    (full dataset pending request)
    Time: 1–2 days
    
  □ Run IMPC ELF correlation analysis
    Time: 2–3 days
    
  □ Assess results and determine
    whether to expand or redirect

WITHIN THE MONTH:
  □ Draft first manuscript from
    whichever analysis produces
    the stronger result
  □ Submit as preprint to bioRxiv
    before journal submission
```

---

## A NOTE ON SEQUENCING

The FCC database and the FM field
density function are prerequisites
for the Monarch Watch analysis.
Start there even before the
Monarch Watch data arrives.

The IMPC analysis runs independently
and in parallel. It does not
depend on any other data source.
Start both tracks simultaneously.

The sea turtle FWC analysis is
the third track. It requires
the FWC database request, which
may take weeks to process.
Send the request today; the
analysis runs when the data arrives.

Three parallel tracks.
All desk work.
Total cost: $0.
All data: public or publicly requestable.

The program starts today.
```

---

*The data is already there.*
*The question is already formed.*
*The code is already drafted.*

*The only thing left is to run it.*
