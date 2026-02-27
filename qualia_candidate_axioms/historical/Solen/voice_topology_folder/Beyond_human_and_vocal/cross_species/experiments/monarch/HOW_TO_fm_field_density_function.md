# HOW TO: FM FIELD DENSITY FUNCTION
## Step 2 of the FM False Attractor
## Analysis Pipeline
## Reproducibility and Setup Guide
## OrganismCore — Cross-Species
## Communication Series
## February 2026

---

## WHAT THIS HOW-TO COVERS

This document covers everything needed
to go from a clean FM station table
(fm_stations_clean.csv — output of
Step 1) to a working FM field density
function that computes the false
attractor bearing for any geographic
coordinate on Earth.

By the end of this how-to you will
have verified output matching the
confirmed results below and a working
batch function ready to process the
full monarch tagging dataset.

**This how-to assumes you have already
completed Step 1 and have
fm_stations_clean.csv in your working
directory. If you do not have that
file, complete the FCC LMS station
table how-to first.**

---

## VERIFIED OUTPUT — WHAT YOU ARE
## TRYING TO REPRODUCE

When setup is complete and the script
runs correctly, your output will match
this exactly:

```
Loading FM station table...
FMFieldDensity ready.
  Stations loaded: 8,136
  Influence radius: 200 km

Running test locations...

── Lawrence KS — Monarch Watch HQ ──
FALSE ATTRACTOR BEARING: 274.0°
Attractor strength: 0.0118
Cardinal: W
Stations within: 80

── Cape May NJ — major fall stopover ──
FALSE ATTRACTOR BEARING: 34.0°
Attractor strength: 0.0094
Cardinal: NE
Stations within: 185

── Peninsula Point MI — Lake Michigan ──
FALSE ATTRACTOR BEARING: 271.0°
Attractor strength: 0.0214
Cardinal: W
Stations within: 96

── Corpus Christi TX — Gulf coast ──
FALSE ATTRACTOR BEARING: 232.0°
Attractor strength: 0.0287
Cardinal: SW
Stations within: 80

── Presqu'ile ON — Lake Ontario ──
FALSE ATTRACTOR BEARING: 204.0°
Attractor strength: 0.0126
Cardinal: SSW
Stations within: 70

Batch result summary:
  Lawrence KS:      274.0°  strength 0.0118  n=80
  Cape May NJ:       34.0°  strength 0.0094  n=185
  Peninsula Point:  271.0°  strength 0.0214  n=96
  Corpus Christi:   232.0°  strength 0.0287  n=80
  Presqu'ile ON:    204.0°  strength 0.0126  n=70

Field density function verified.
```

If your numbers match these, you are
ready to proceed to Step 3.

---

## PART I: PREREQUISITES

### What you need before starting

**From Step 1 (must already exist):**
```
fm_stations_clean.csv
```
This file must be in your working
directory. It contains 8,136 FM
stations with confirmed transmitter
coordinates, frequency, and ERP proxy.

If you see "Stations loaded: 8,136"
when the script runs, the file is
correct. Any substantially different
number indicates a Step 1 issue —
go back and re-run the station table
build before continuing.

**Python version:**
```
Python 3.9 or higher
```
Check your version:
```bash
python --version
```

**Virtual environment (recommended):**
```bash
# Create environment
python -m venv venv

# Activate — Mac/Linux:
source venv/bin/activate

# Activate — Windows:
venv\Scripts\activate
```

---

## PART II: DEPENDENCIES

### Install required packages

Step 2 requires two packages beyond
Step 1:

```bash
pip install scipy matplotlib
```

Full dependency list for Step 2:
```bash
pip install pandas numpy scipy matplotlib
```

If you already installed pandas and
numpy for Step 1, only scipy and
matplotlib are new.

**Verify installation:**
```python
import pandas
import numpy
import scipy
import matplotlib
print("all dependencies present")
```

If any import fails, install the
missing package:
```bash
pip install <package_name>
```

**Note on matplotlib:**
matplotlib is only required for the
`plot_azimuth_distribution()` function.
The core computation functions work
without it. If you do not need
visualization, matplotlib can be
skipped. The test block in
`__main__` does not call the plot
function by default.

---

## PART III: FILE SETUP

### Directory structure

All files in one directory:

```
working_directory/
  fm_stations_clean.csv     ← from Step 1
  fm_field_density.py       ← the script
```

No subdirectories needed.
No configuration files needed.
No API keys needed.
No internet connection needed
after the FCC data is downloaded.

---

## PART IV: THE SCRIPT

Save the complete fm_field_density.py
script provided in this session to
your working directory.

The script contains four sections:

**Section 1: Constants**
```
DEFAULT_RADIUS_KM = 200
FM_LOW_MHZ  = 87.5
FM_HIGH_MHZ = 108.0
```
These control which stations are
included in the computation.
200km radius captures all stations
with meaningful signal contribution
at typical FM field strengths.
Do not change these values unless
you have a specific reason — changing
them will produce different results
from the verified output above.

**Section 2: FMFieldDensity class**
The core computation engine.
Load once, call compute() many times.

**Section 3: Diagnostic functions**
plot_azimuth_distribution()
print_result()
These are utilities — not required
for the pipeline but useful for
understanding individual locations.

**Section 4: Test block (__main__)**
Runs automatically when you execute
the script directly. Tests five
known monarch tagging locations and
a small batch computation. This is
your verification step.

---

## PART V: RUNNING THE SCRIPT

```bash
python fm_field_density.py
```

### What happens step by step:

**Step 1 — Station table loads:**
```
Loading FM station table...
FMFieldDensity ready.
  Stations loaded: 8,136
  Influence radius: 200 km
```
Takes 1–2 seconds.
If you see a different station count,
check fm_stations_clean.csv.

**Step 2 — Test locations run:**
Each of the five test locations
computes in under 1 second.
The distance and bearing calculations
are fully vectorized — no Python
loop over stations.

**Step 3 — Batch test runs:**
5 locations processed as a batch.
Confirms that compute_batch() works
correctly before you use it on
363,582 monarch records.

**Total runtime: under 30 seconds.**

---

## PART VI: UNDERSTANDING THE OUTPUT

### For each test location you will see:

**FALSE ATTRACTOR BEARING:**
The compass direction (0–360°,
clockwise from North) of maximum
weighted FM exposure.
This is the direction a disrupted
magnetic compass would point toward.

**Attractor strength:**
Fraction of total FM exposure
concentrated in the dominant
bearing direction.
Range: 0.0 to 1.0

Interpreting strength values:
```
< 0.005  very weak — FM exposure
         nearly uniform in all
         directions. No dominant
         false attractor.

0.005    weak but present.
– 0.015

0.015    moderate. A detectable
– 0.030  directional signal exists.
         Most locations fall here.

> 0.030  strong. FM exposure clearly
         concentrated in one direction.
         Corpus Christi (0.029) is
         near this threshold.
```

The five test locations all fall in
the 0.009–0.029 range. This is normal
for US locations surrounded by
transmitters on multiple sides.
High-strength values (> 0.05) occur
at locations near a single dominant
transmitter cluster with open terrain
in other directions — rural locations
near a city on one side.

**n_stations:**
Number of FM stations within 200km
of the test location contributing
to the computation.
Cape May (185) is high because it
is near the dense Philadelphia/New
York/Baltimore transmitter cluster.
Presqu'ile ON (70) is lower because
it is across Lake Ontario from the
nearest US transmitters.

**Top 5 contributing stations:**
The five stations with the highest
weight (ERP proxy × distance decay)
at this location.
Weight = erp_proxy / distance_km²
The top station typically dominates
the false attractor bearing.

**Note on NaN callsigns:**
Peninsula Point shows one NaN
callsign. This is a station in
fm_stations_clean.csv with a missing
callsign field but valid coordinates
and ERP proxy. It contributes
correctly to the computation.
The callsign is cosmetic — only the
coordinates and ERP are used.

---

## PART VII: USING THE FUNCTION
## IN YOUR OWN CODE

### Import and initialize:

```python
from fm_field_density import FMFieldDensity

# Load once — takes 1-2 seconds
fmd = FMFieldDensity("fm_stations_clean.csv")
```

### Compute for a single location:

```python
result = fmd.compute(lat=38.97, lon=-95.24)

print(result['false_attractor_bearing'])
print(result['false_attractor_strength'])
print(result['n_stations'])
print(result['total_fm_exposure'])
```

### Compute with station list:

```python
result = fmd.compute(
    lat=38.97,
    lon=-95.24,
    return_station_list=True
)
# result['stations'] is a DataFrame
# sorted by weight descending
print(result['stations'].head(10))
```

### Override radius:

```python
# Use 300km radius instead of 200km
result = fmd.compute(
    lat=38.97,
    lon=-95.24,
    radius_km=300
)
```

Use 300km if n_stations is unexpectedly
low (< 10) for a US location.

### Batch compute for a DataFrame:

```python
import pandas as pd

locations = pd.DataFrame({
    'lat': [38.97, 38.94, 45.77],
    'lon': [-95.24, -74.91, -86.95],
})

result_df = fmd.compute_batch(
    locations,
    lat_col='lat',
    lon_col='lon',
    progress_every=100
)

# result_df now has four new columns:
#   fm_false_attractor_bearing
#   fm_false_attractor_strength
#   fm_total_exposure
#   fm_n_stations
```

---

## PART VIII: PERFORMANCE

### Speed characteristics:

**Single location:** < 0.01 seconds
Fully vectorized. Distance and bearing
to all 8,136 stations computed in
one numpy operation.

**Batch — naive (one location at a time):**
~0.01 seconds × n locations
363,582 locations would take ~1 hour

**Batch — with deduplication (recommended):**
The compute_batch() function includes
automatic location deduplication on
a 1km grid (coordinates rounded to
2 decimal places).
363,582 monarch records → 3,074
unique locations → compute FM once
per unique location → join back.
Actual runtime for full monarch
dataset: ~7 minutes.

**This is the approach used in
monarch_false_attractor_analysis.py
and is why the full dataset runs
in 7 minutes rather than 1 hour.**

---

## PART IX: WHAT THE COMPUTATION
## IS ACTUALLY DOING

### Step by step for one location:

**1. Distance filter**
Find all stations within 200km using
the haversine formula:
```
d = 2R × arcsin(√(sin²(Δlat/2) +
    cos(lat1)cos(lat2)sin²(Δlon/2)))
```
This is vectorized across all 8,136
stations simultaneously.

**2. Bearing computation**
Compute geodesic bearing from the
target location to each station
within radius:
```
bearing = arctan2(
  sin(Δlon)cos(lat2),
  cos(lat1)sin(lat2) -
  sin(lat1)cos(lat2)cos(Δlon)
) converted to 0–360°
```

**3. Weight assignment**
Each station gets a weight:
```
weight = erp_proxy / distance_km²
```
ERP proxy is in watts (0–100,000).
Distance decay is inverse square —
a station at 100km has 1/4 the
weight of the same station at 50km.

**4. Azimuth distribution**
360-bin array, one bin per degree.
Each station deposits its weight
into the bin corresponding to its
bearing from the target location.
numpy.add.at() handles this without
a Python loop.

**5. Gaussian smoothing**
Smooth the azimuth distribution
with sigma=10° to model the angular
spread of FM signal propagation.
Circular boundary handled by tripling
the array before smoothing.

**6. Peak detection**
false_attractor_bearing = index of
maximum bin in smoothed distribution.
This is the bearing toward which a
disrupted compass would point.

---

## PART X: TROUBLESHOOTING

**"Stations loaded: 0" or FileNotFoundError:**
fm_stations_clean.csv is not in the
working directory. Check the path.
Run from the same directory as the
file:
```bash
cd /path/to/your/working/directory
python fm_field_density.py
```

**Station count substantially different
from 8,136:**
You are using a different FCC LMS
snapshot. This is acceptable —
a more recent snapshot may have
more or fewer stations. Your
false attractor bearings will differ
slightly from the verified output.
This does not indicate an error.

**"ModuleNotFoundError: scipy":**
```bash
pip install scipy
```

**"ModuleNotFoundError: matplotlib":**
```bash
pip install matplotlib
```
Or remove the plot calls from the
test block if you do not need
visualization.

**n_stations = 0 for a US location:**
The location may be outside the
continental US (Alaska, Hawaii,
remote territories). Try increasing
radius:
```python
result = fmd.compute(lat, lon,
                     radius_km=500)
```

**false_attractor_bearing = None:**
Returned when n_stations = 0.
No FM stations within radius.
Extremely rare for any US location
with radius_km=200.

**Results differ from verified output:**
Three acceptable reasons:
1. Different FCC LMS snapshot date
2. Different radius_km setting
3. Different fm_stations_clean.csv
   (different filtering parameters
   in Step 1)

If none of these apply and results
differ, check that fm_stations_clean.csv
has columns: callsign, frequency_mhz,
tx_lat, tx_lon, erp_proxy.

---

## PART XI: OUTPUT COLUMNS
## ADDED BY compute_batch()

When compute_batch() runs on a
DataFrame, it adds four columns:

| Column | Type | Description |
|--------|------|-------------|
| `fm_false_attractor_bearing` | float | Degrees 0–360, direction of max FM exposure |
| `fm_false_attractor_strength` | float | 0–1, fraction of total exposure in dominant direction |
| `fm_total_exposure` | float | Sum of distance-weighted ERP proxy (proxy W·km⁻²) |
| `fm_n_stations` | int | Number of FM stations within radius contributing |

These four columns are everything
needed for the monarch false attractor
analysis. fm_false_attractor_bearing
is the key predictor variable.
fm_false_attractor_strength is the
dose-response variable used in the
secondary quartile analysis.

---

## PART XII: NEXT STEP

When this script runs and your
output matches the verified output
in Part I, you are ready for Step 3:

```
monarch_false_attractor_analysis.py
```

Step 3 loads the GBIF Monarch Watch
occurrence dataset (occurrence.txt),
calls compute_batch() on all 3,074
unique tagging locations, saves
monarch_with_fm.csv (363,582 records
with FM metrics), and runs the
statistical test when recovery
coordinates are available.

Proceed to the Step 3 how-to.

---

## VERSION

```
v1.0 — February 2026
Verified against FCC LMS snapshot:
  February 26, 2026
Verified station count: 8,136
Verified test location outputs:
  documented in Part I of this
  how-to

Pipeline position:
  Step 1: build_fm_station_table.py
          → fm_stations_clean.csv
  Step 2: fm_field_density.py  ← HERE
          → FMFieldDensity class
  Step 3: monarch_false_attractor_
          analysis.py
          → monarch_with_fm.csv
  Step 4: monarch_tagging_
          exploratory.py
          → exploratory findings
  Step 5: [pending recovery data]
          → statistical test
```
