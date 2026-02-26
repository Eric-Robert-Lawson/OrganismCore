# THE MEASUREMENT INSTRUMENT
## What Can Be Done, When, By Whom,
## With What Equipment
## A Tiered Action Document
## Principles-First Exploration —
## Fifth Pass
## February 26, 2026

---

## ARTIFACT METADATA

```
artifact_type: experimental design
  + action triage — maps every
  measurement proposed across
  CS docs 10–10d onto a tiered
  action space: (1) immediately
  executable with existing data,
  (2) buildable within weeks
  using available equipment,
  (3) full rigorous experiment
  requiring site + equipment +
  protocol.
author: Eric Robert Lawson
  (with GitHub Copilot, session
  February 26, 2026)
series: Cross-Species Communication
  Series — Document 10e
depends_on:
  - the_bee.md (CS doc 10)
  - the_false_attractor_hypothesis.md
    (CS doc 10b)
  - bee_quantum_layer.md (CS doc 10c)
  - attractor_pollution_generalized.md
    (CS doc 10d)
status: ACTIVE DESIGN DOCUMENT.
  The purpose of this document
  is to answer: what can I do,
  right now, with what I have,
  and what should I build toward?
central_finding: Three tiers exist.
  Tier 1 (this week): Monarch
  and bird directional analysis
  from existing public databases.
  No equipment needed. Just data
  and code.
  Tier 2 (weeks): Low-cost
  magnetic measurement at a hive
  or field site. ~$200–500 in
  hardware. Tests whether the
  hive emits a detectable magnetic
  beacon (the single most important
  new measurement).
  Tier 3 (months): The full
  Prediction 3 experiment —
  rotating AC source, waggle
  dance tracking, EM shielding.
  This is the definitive test.
  It requires a proper site,
  proper equipment, and careful
  protocol design. This document
  is the full protocol.
key_finding_about_turtle_data: The
  FWC sea turtle database tracks
  VISUAL disorientation (toward
  light sources), not magnetic
  disorientation. The magnetic
  false attractor test for turtles
  requires a laboratory swim-tank
  experiment, not field observation.
  The data gap is itself informative —
  we have been measuring the
  light channel because we could
  see it. The magnetic channel
  has been invisible to our
  measurement infrastructure.
```

---

## PART I: THE FULL PICTURE —
## WHAT WE ARE TRYING TO MEASURE

Five distinct measurements emerged
across CS docs 10–10d.
Not all require the same approach.
Not all require the same resources.

```
MEASUREMENT 1:
  Does waggle dance angle bias
  track a rotating artificial
  ELF field source?
  
  This is Prediction 3 from
  the_false_attractor_hypothesis.md.
  
  What it would prove: False
  attractor formation in the
  magnetite compass channel at
  ELF frequencies. Directional
  bias, not just degradation.
  
  Tier: 3 (full experiment).
  Requires: hive, EM shielding,
  AC field source, waggle dance
  tracking pipeline, clean site.

MEASUREMENT 2:
  Does the hive emit a detectable
  magnetic signal at low Hz?
  
  The hive beacon hypothesis
  from CS doc 10c.
  
  What it would prove: The colony
  produces a collective magnetic
  emission. First step toward
  establishing hive beacon as
  a real physical phenomenon.
  
  Tier: 2 (buildable this month).
  Requires: one sensitive magnetometer
  + a hive + a quiet site.
  Cost: $200–500.

MEASUREMENT 3:
  Are monarch butterfly recovery
  vectors deflected toward FM
  transmitter clusters?
  
  Directional false attractor
  test using existing data.
  
  What it would prove: That
  the radical pair compass in
  CRY1-bearing insects is being
  captured by FM broadcast
  infrastructure during migration.
  
  Tier: 1 (this week).
  Requires: Monarch Watch data
  + FCC broadcast database
  + Python.
  Cost: $0.

MEASUREMENT 4:
  Are urban European robin
  orientation directions aligned
  with FM transmitter azimuth?
  
  Directional false attractor
  test using existing published
  data.
  
  What it would prove: Same as
  Measurement 3 but for a
  species with direct experimental
  magnetic orientation data.
  
  Tier: 1 (this week if data
  is accessible; otherwise weeks
  via researcher contact).
  Requires: Published European
  robin cage orientation data
  + FM transmitter maps.
  Cost: $0.

MEASUREMENT 5:
  Do sea turtle hatchlings from
  beaches near cable infrastructure
  show magnetic swim direction
  bias toward cable?
  
  Address corruption / route
  corruption test for turtles.
  
  What it would prove: That
  submarine cable ELF fields
  corrupt hatchling magnetic
  address imprinting.
  
  Tier: 3 (requires laboratory
  swim tank + controlled field
  environment + hatchlings from
  specific beaches).
  Requires: Collaboration with
  turtle research program.
  Cost: High. Cannot be done alone.
  
  BUT: A preparatory analysis
  is Tier 1 —
  Map existing cable routes
  against FWC nesting beach
  database and look for cohort-
  level nesting site spread
  changes after cable installation.
  Tier 1 for the preparatory
  analysis. Tier 3 for the
  direct measurement.
```

---

## PART II: TIER 1 — THIS WEEK
## (Existing data, no equipment)

### ANALYSIS 1A: Monarch Butterfly
### Directional False Attractor Test

**What you have:**

Monarch Watch maintains decades
of tagging + recovery records.
Each record has:
- Tagging location (lat/lon)
- Recovery location (lat/lon)
- Date

From these two points, a
recovery vector can be computed:
- Bearing from tagging to recovery
  (actual migration direction
  taken by this individual)
- Expected bearing (toward
  Mexican overwintering sites —
  approximately 225° SW from
  eastern US tagging sites)
- Angular deviation = actual − expected

**What you need additionally:**

FCC FM Broadcast Station database
(public, downloadable CSV):
- All FM broadcast stations
  in the US
- Each has: lat/lon, power (watts),
  frequency (MHz)

Filter to: 87.5–108 MHz
(FM band, partial overlap with
75–85 MHz disruption window)

For each tagging location:
compute azimuth to each major
FM transmitter within 200 km,
weighted by power and attenuated
by distance.

This produces a "false attractor
bearing" for each tagging location —
the predicted direction the
compass should be pulled toward
if false attractor capture is occurring.

**The test:**

Null hypothesis: Angular deviation
is random with respect to false
attractor bearing.

Alternative hypothesis: Angular
deviation is correlated with false
attractor bearing. Specifically:
butterflies deviate from expected
SW bearing in the direction of
the predicted false attractor.

**Statistical approach:**

For each tagged individual:
- Compute: θ_actual (observed
  recovery bearing from tagging)
- Compute: θ_expected (~225° SW)
- Compute: δ = θ_actual − θ_expected
  (signed angular deviation)
- Compute: θ_FA = azimuth to
  nearest major FM cluster,
  weighted by power/distance²
- Test: Is δ correlated with
  (θ_FA − θ_expected)?

Prediction: When θ_FA is to the
west of θ_expected, δ should be
negative (deflected west).
When θ_FA is to the east,
δ should be positive.

The test is directional.
Not just "are they deviating?"
but "are they deviating TOWARD
the transmitter?"

**Confounds to address:**

1. Wind: Strong headwinds or
   crosswinds displace butterflies.
   Control by including wind
   data from NOAA reanalysis
   at tagging date/location.

2. Roost/stopover clustering:
   Monarchs aggregate at specific
   stopover sites. Some deviations
   reflect stopover choice, not
   compass error.
   Control: use only single-leg
   records between tagging and
   recovery at a stopover site
   > 100 km from tagging.

3. Geographic funneling: The
   landscape channels migration
   (Great Lakes, Appalachians).
   Control: stratify by geographic
   region and test within regions
   separately.

**Expected output:**

A scatter plot of δ (angular
deviation from expected) vs.
(θ_FA − θ_expected) for thousands
of individual tagged monarchs.

If false attractor capture is
occurring: a positive slope
(deviation tracks transmitter
direction).

If not: flat slope (random scatter).

**Data access:**

Monarch Watch data: Contact
monarchwatch.org for research
access. The tagging program
coordinator (Dr. Chip Taylor)
has historically been receptive
to research partnerships.
Alternatively, published papers
using the Monarch Watch database
contain processed forms of the
data that may be usable.

FCC FM database: 
media.fcc.gov/api/database/dump/FM
— free, public, CSV download.
Updated weekly.

**Time to first result: 1–2 weeks**
from data access confirmation.

**Code requirements:**
Python with:
- pandas (data handling)
- numpy (bearing calculations)
- scipy.stats (circular statistics)
- cartopy or folium (visualization)

All standard scientific Python.
No specialized tools required.

---

### ANALYSIS 1B: European Robin
### Directional False Attractor Test

**What you have
(or can access rapidly):**

The key papers showing urban
Robin disorientation are:

Wiltschko et al., various years.
Engels et al. 2014 (the definitive
Oldenburg study): European robins
in Oldenburg cannot orient
magnetically. In Faraday cages
in the same building they can.
The disruption source: urban
EM noise.

The paper reports mean preferred
orientation directions for birds
in different conditions.

**What is NOT in the published paper:**

The specific bearing of the
mean orientation direction in
the disrupted condition — where
ARE the birds orienting when
they're wrong?

This is the critical data point.

If the disrupted orientation
direction points toward the
city center (where the main
broadcast infrastructure is),
that is a false attractor.

If it is random, that is
consistent with degradation
but not false attractor.

**Action:**

Email the lead author (R. Wiltschko
or H. Mouritsen at Oldenburg)
and request the raw orientation
direction data from the urban
exposure experiments.

Ask specifically: In the
undisturbed (urban, unshielded)
condition, what was the mean
vector direction? Was it random
(low r value) or did it show
a preferred direction?

If it showed a preferred direction:
what was that direction?

Compare that direction to the
azimuth from the lab to the
main FM broadcast infrastructure
in Oldenburg.

**This is a one-email experiment.**

The data probably already exists
in the lab's records.
It was not reported in the
paper because the question being
asked at the time was
"can they orient at all?" not
"where are they orienting to?"

The false attractor question
makes the unreported direction
data suddenly critical.

**Time to data: weeks
(if researcher responds).**

---

### ANALYSIS 1C: Sea Turtle Cohort
### Spread Preparatory Analysis

**What you have:**

Florida FWC Sea Turtle ArcGIS Hub:
- Nesting beach locations
- Nesting records by year
- Individual turtle ID (from tags)
  where available

**What you need additionally:**

Submarine cable installation
dates and routes:
TeleGeography maintains a
global submarine cable map
(free to access online).
Cable landing station locations
and installation years are
documented.

**The test:**

For each major Florida nesting
beach adjacent to a cable
landing station within 50 km:

- Extract individual turtle
  nesting records before and
  after cable installation
  (cohort comparison: imprinting
  cohort A = imprinted before
  cable, cohort B = imprinted
  after cable)

- Measure: geographic spread
  of nesting sites for each
  cohort. Operationalized as
  the standard deviation of
  nesting latitude/longitude
  for turtles in each cohort.

- Prediction: Cohort B
  (imprinted after cable) shows
  higher geographic spread than
  cohort A (imprinted before cable).

- Control: Compare beaches
  near cables vs. beaches far
  from cables. Is the spread
  increase specific to cable-
  adjacent beaches?

**Caveats:**

Sea turtles mature in 20–30 years.
The analysis requires turtle
nesting records spanning at
least one generation (20+ years)
around cable installation dates.

Atlantic coast cable installations
largely occurred in the 1990s
and 2000s. Some earlier (TAT-1
was 1956, but on older routes).
The Florida coast has had
cable landings since at least
the 1970s.

Turtles born in the 1990s
near cable landings would be
nesting now. Their data
exists in the FWC records.

**Time to first result: 1–3 weeks
from data access.**

---

## PART III: TIER 2 — THIS MONTH
## (One piece of equipment, one site)

### THE HIVE BEACON MEASUREMENT

This is the single most important
new measurement in the entire
framework.

If the hive emits a detectable
magnetic signal at low Hz,
it changes the interpretation
of CCD. If it does not,
the hive beacon hypothesis
is falsified and the framework
simplifies.

It is a binary, critical measurement.
It requires minimal equipment.
It has never been done.

**What you need:**

A magnetometer with sensitivity
better than 10 nT at frequencies
below 100 Hz.

Options:

OPTION A: DIY Fluxgate
- MDPI 2025 homemade fluxgate:
  sensitivity 2.2 nT, noise
  1.1 nT/√Hz at 1 Hz.
  Full design published open access.
  Components: ~$150–300.
  Build time: 1–2 weeks with
  electronics experience.
  DATA LOGGING: Arduino or
  Raspberry Pi with ADC.

OPTION B: Commercial kit
- magnetometer-kit.com FGM 3 PRO:
  €190 (~$210), 2 nT sensitivity,
  battery operated, immediate.
  This is the fastest path.

OPTION C: Research-grade used
- Used three-axis fluxgate
  magnetometers available on
  eBay/LabX for $300–800.
  May need calibration.

RECOMMENDED: Option B for
immediate deployment. Option A
for longer-term precision work
if the signal is found and needs
characterization.

**Where to place it:**

A hive at a low-EM-noise site
is critical. The ambient ELF
noise from power line fields
is ~100 nT at 50/60 Hz near
a power line, falling as 1/r²
with distance.

At 100 meters from a residential
power line: ~1 nT at 50 Hz.
At 500 meters: ~0.04 nT at 50 Hz.

The hive beacon signal (if it
exists) is estimated to be
0.1–10 nT at the hive surface
(rough estimate based on
hundreds of magnetite compasses
in bees with ~10⁻¹⁵ Am² per
single-domain crystal, scaled
to a colony of 50,000 bees
with some collective coherence).

This means: to detect the hive
beacon, you need a site where
50 Hz power line noise is below
~1 nT. That requires > 100 m
from power lines.

Rural site: necessary.
Organic farm: ideal (no electric
fencing either).
A site that already has bees
in a rural location: perfect.

**Protocol:**

Step 1: Site characterization
(1 day)

Place magnetometer at the
candidate site with no hive.
Record 30 minutes of data.
Take Fourier transform.
Measure noise floor at each
frequency from 0.1 Hz to 100 Hz.

Assess: Is the noise at 2–20 Hz
below 10 nT? (This is the
expected beacon frequency range
based on wing ventilation rates
and colony oscillation estimates.)

If yes: site is usable.
If no: find a quieter site or
determine which infrastructure
is causing the noise and mitigate.

Step 2: Baseline measurement
(1 day)

Place magnetometer 10 cm from
the landing board of an active
hive. Orient sensor to detect
the horizontal component of
the field (parallel to the
hive face).

Record 60 minutes continuously.
Take Fourier transform.
Look for peaks between 1–20 Hz
above the noise floor.

Record colony activity level
(listening for hum, observing
bee traffic) to correlate with
any detected signal.

Step 3: Colony state correlation
(2–3 days)

Repeat measurement at different
colony activity states:
- Morning (low activity)
- Peak foraging (high activity,
  maximum bee numbers in hive)
- Evening (foragers returned,
  high ventilation activity)
- Winter cluster (low activity)

Prediction: If the hive beacon
is produced by collective wing
ventilation, the signal should
be strongest during ventilation
behavior (summer evening) and
absent during winter cluster.

Step 4: Distance profile
(1 day)

Measure signal amplitude at
5 cm, 10 cm, 20 cm, 50 cm,
100 cm, 200 cm from the hive.

This gives the fall-off with
distance, which determines:
- Maximum detection range
- Whether the signal could
  reach a forager at 100, 200,
  500 meters

If the signal falls as 1/r³
(magnetic dipole field decay):
at 10 nT at 10 cm → 0.0001 nT
at 100 m (undetectable).

If the signal falls as 1/r
(far-field radiation from a
coherently oscillating source):
at 10 nT at 10 cm → 1 nT at
1 m → 0.1 nT at 10 m → still
potentially detectable by a
bee's magnetite compass at
50–100 m range.

The fall-off profile distinguishes
near-field magnetic effect from
far-field radiation — the
difference between a static
magnetic dipole and an antenna.

If the colony is acting as an
antenna, the beacon has long
range. If it's just a near-field
effect, range is limited.

**Expected outcomes:**

OUTCOME A: No signal above noise
floor at any frequency.
→ Hive beacon hypothesis falsified.
→ The colony emission finding
  (bioRxiv 2025) may be a
  microwave phenomenon, not ELF.
→ Focus shifts to other mechanisms.
→ Clean null result. Science works.

OUTCOME B: Signal detected at
specific frequency, amplitude
correlated with colony activity.
→ Hive beacon hypothesis supported.
→ Proceed to colony comparison
  (do different colonies emit
  different frequencies?).
→ Proceed to distance profiling.
→ Proceed to forager attraction
  test (do bees orient toward
  a coil playing back the
  recorded frequency?).

OUTCOME C: Signal detected at
50 Hz (power line frequency)
even at a "quiet" site.
→ Site is not clean enough.
→ Need to characterize the
  source and move to a cleaner
  site or build shielding first.

**Total cost for Tier 2:**

Magnetometer kit (Option B): $210
Raspberry Pi + ADC for logging: $80
Cables and mounting hardware: $30
Total: ~$320

**Time to first result: 2–4 weeks**
from ordering equipment.

---

## PART IV: TIER 3 — THE FULL
## EXPERIMENT (Months)
## PREDICTION 3 PROTOCOL

This is the definitive test
of the false attractor hypothesis
in the bee compass system.

**The hypothesis being tested:**

A coherent ELF AC magnetic field
source acts as a false attractor
for the bee's magnetite compass.
If the source is rotated to
different azimuths around the
hive across multiple sessions,
the waggle dance angle distribution
should show a systematic bias
toward the source azimuth.

**Why this is the critical test:**

The Tier 1 and Tier 2 measurements
are correlational (existing data)
or observational (measuring
ambient signals).

This experiment is
**causal and manipulative.**

It is the only measurement that
can establish:
- That the field source IS causing
  the bias (not correlating with it)
- That the bias is directional
  (tracking the source as it rotates)
- That the effect size is physically
  significant (how many degrees
  of bias per unit field strength?)

### DESIGN REQUIREMENTS

**Site selection:**

The site must have ambient ELF
noise < 10 nT at 50/60 Hz.
This requires:
- > 200 m from power lines
- No electric fencing within 500 m
- No solar inverters within 100 m
- No underground cables within 50 m

Additionally:
- The site must have a known
  food resource in a known direction
  so that we know the expected
  waggle dance angle and can
  detect deviations from it.
- The food resource (feeder)
  should be > 200 m from the hive
  so that the dance encodes
  a clear directional signal.
- The resource direction should
  be > 45° from magnetic north
  so that small deviations are
  detectable without ambiguity.

**Hive preparation:**

A standard observation hive
with one glass side, allowing
the waggle dance surface to be
filmed.

The hive must be oriented so
that the dance surface is
vertical (natural orientation
for bees that converts the sun
angle into a gravity-referenced
angle on the comb).

The hive must be positioned so
that:
- The AC field source can be
  placed at any azimuth around
  the hive at a fixed distance
  (e.g., 3 m)
- The hive itself is within the
  uniform field region of the coil

**The field source:**

A Helmholtz coil pair producing
a uniform AC magnetic field
at 50 Hz over a region
encompassing the hive.

Design parameters:
- Coil diameter: 1.5 m
  (allows hive to fit within
  uniform field region)
- Coil separation: 0.75 m
  (= radius, for Helmholtz geometry)
- Field target: 100–1000 nT
  (above natural variation,
  well below disorienting levels)
- Frequency: 50 Hz (power line
  fundamental)
- Field orientation: horizontal,
  in the plane of the coil

The coil pair is mounted on
a rotating frame that can be
positioned at any azimuth around
the hive in 45° steps.

Positions: N, NE, E, SE, S,
SW, W, NW (8 azimuths).

At each position, the coil's
field vector points from the
coil toward the hive — creating
an artificial ELF field with
a specific horizontal direction.

**The control condition:**

The coil is present at the same
azimuth but powered off.
No field.
All physical setup identical.

Blinded: the observer recording
waggle dance angles does not
know whether the coil is on or off.

**The EM shielding:**

This is the hardest part.

The hive must be shielded from
all external ELF fields EXCEPT
the experimental coil.

Options:

OPTION A: Faraday enclosure + passive shielding
- Build a wooden frame structure
  around the hive (open side for
  filming)
- Line with mu-metal sheet
  (high magnetic permeability,
  attenuates low-frequency fields)
- Shielding factor: 10–50×
  attenuation for a single layer
  of 0.5 mm mu-metal sheet

OPTION B: Remote rural site
  (no shielding needed)
- Find a site with ambient ELF
  < 1 nT. Then the 100 nT
  experimental field gives
  100:1 signal-to-noise.
- This is possible but rare.
  Far from any grid power lines.
  Solar-powered recording setup.

RECOMMENDED APPROACH:
Combine both: remote rural site
PLUS passive mu-metal shielding.
The combination achieves 1000:1
signal to ambient noise.

**The waggle dance tracking:**

The existing ML pipeline
(deep learning, 2025 Springer
paper) achieves near-100%
detection accuracy for waggle runs
under natural conditions.

For this experiment:
- 4K camera mounted above
  the dance surface
- Recording in 15-minute segments
  during each coil position session
- Post-processing with ML pipeline
  to extract:
  - Each waggle run direction
    (angle relative to vertical)
  - Duration of each waggle run
  - Number of waggle runs per
    15-minute window

Output: A distribution of waggle
angles for each coil position.

**The measurement protocol
(one complete experiment cycle):**

Session 1 (day 1):
- Establish baseline with coil
  off at position N
- Record 60 minutes of waggle
  dance
- Measure ambient field with
  fluxgate magnetometer placed
  10 cm from hive
- Verify ambient ELF < 5 nT

Session 2 (day 2):
- Coil ON at position N (100 nT)
- Record 60 minutes of waggle dance
- Measure field at hive (verify
  100 nT at 50 Hz)

Session 3 (day 3):
- Coil OFF (control)
- Record 60 minutes

Session 4 (day 4):
- Coil ON at position E (90°
  from N)
- Record 60 minutes

Sessions 5–16:
- Continue rotating around the
  8 azimuths, each with paired
  on/off measurements
- Allow 1–2 days between sessions
  to allow colony to reset

Full cycle: 16 sessions over
4–6 weeks.

**Analysis:**

For each coil position, compute
the mean waggle dance angle
(circular mean of all waggle
run directions in the session).

Compute the deviation of each
session's mean angle from the
baseline (coil off) mean angle.

Test: Is the deviation correlated
with coil azimuth?

Prediction:
- Coil at N → mean angle
  deflects toward N (decreases
  by X°)
- Coil at E → mean angle
  deflects toward E (increases
  by Y°)
- Coil at S → mean angle
  deflects toward S (decreases
  from S side)
- Coil OFF → no deviation

A circular correlation between
(coil azimuth) and (dance
angle deviation) should be
positive.

The effect size (degrees of
deviation per 100 nT of field)
is the physically interesting
number — it gives the calibration
curve for how strong a power
line needs to be at what distance
to produce a measurable dance
angle error.

**Statistical power:**

Each 15-minute session typically
yields 30–100 waggle runs
(highly active hive in good
weather with rich forage).

Circular standard deviation
of waggle runs in a session:
typically 15–25°.

To detect a 5° mean shift
with 80% power at α = 0.05:
need approximately 30 runs per
session.

We have ≥ 30 runs per session.
With 8 coil positions × 2 sessions
each (on + off), total n = 16
sessions × ~50 runs = 800 runs.

Power is adequate to detect
effects as small as 3–5°.

**Confounds and controls:**

1. TIME OF DAY EFFECT:
   Waggle dance direction changes
   as the sun moves (bees
   compensate in real time).
   Control: always record within
   the same 2-hour window each day.
   Or: include sun azimuth as
   a covariate in the model.

2. COLONY STATE CHANGES:
   The colony changes behavior
   over weeks (swarm preparation,
   queen replacement, weather).
   Control: run each coil position
   multiple times across the season.
   Use within-day on/off pairs
   where possible.

3. FOOD SOURCE CHANGES:
   If the artificial feeder is
   the only food source, its
   distance and direction is
   fixed. Confirm by direct
   observation that bees are
   using the feeder.

4. MAGNETIC FIELD FROM THE
   COIL HOUSING:
   The coil frame should be
   non-magnetic (aluminum or PVC).
   Verify: measure field at hive
   with coil physically present
   but electrically off.
   Any residual field from the
   frame should be < 5 nT.

5. THERMAL EFFECT:
   The coil produces heat (I²R).
   This must not warm the hive.
   At 100 nT field level, the
   required current is very small
   (< 100 mA in a 1.5 m coil).
   Heat is negligible.

6. VISUAL CUE FROM COIL:
   Bees have excellent vision.
   The coil frame is physically
   present at different positions.
   Control: run sessions with
   the coil frame present at
   multiple positions simultaneously
   (only one electrically active)
   to eliminate visual tracking
   of the coil.

**Budget for Tier 3:**

Observation hive (commercial): $400
4K camera + tripod: $300
Helmholtz coil materials (wire,
  PVC frame, aluminum hardware): $200
Function generator (AC current
  source, 50 Hz): $150
Power amplifier (10W): $100
Fluxgate magnetometer (FGM 3 PRO
  kit or equivalent): $210
Mu-metal shielding (2 m² sheet,
  0.5 mm): $300–600
Raspberry Pi + storage for
  video recording: $80
Miscellaneous (cables, connectors,
  weatherproofing): $100

Total: $1,840–$2,140

This is the cost of one scientific
publication's worth of equipment.
It is not a grant-scale experiment.
It is a well-equipped garage-level
experiment with proper protocol.

**What it produces:**

If positive: First causal,
manipulative demonstration that
ELF fields produce directional
compass bias in honeybees.
First measurement of the effect
size. Foundation for all
subsequent conservation and
regulatory arguments.

If negative: Rules out directional
false attractor capture in the
magnetite compass at the tested
field strength. Shifts focus
to degradation-only model.
Still important: rules out
the directional component.

Either outcome advances the
science substantially.

---

## PART V: THE FULL EXPERIMENTAL
## PROGRAM — ALL SPECIES

### WHAT CAN BE DONE WITHOUT
### SPECIALIZED COLLABORATION

```
Species       Measurement        Tier  Cost    Time
──────────────────────────────────────────────────────────
Monarch       Directional        1     $0      1–2 weeks
butterfly     analysis of
              tagging data vs.
              FM transmitter map

European      Email to get       1     $0      Weeks
robin         unreported mean    (waiting
              orientation        for reply)
              direction in
              urban condition

Sea turtle    Cable route vs.    1     $0      2–3 weeks
(cohort       nesting spread
analysis)     cohort comparison

Honeybee      Hive beacon        2     $320    2–4 weeks
              detection
              (ambient
              magnetometer
              at active hive,
              quiet site)

Honeybee      Prediction 3:      3     $2,000  3–6 months
(full         rotating coil
experiment)   + waggle dance
              tracking + EM
              shielding
──────────────────────────────────────────────────────────
```

### WHAT REQUIRES COLLABORATION

```
Species       Measurement       What's Needed
─────────────────────────────────────────────────────────────
Sea turtle    Hatchling swim    Access to nesting beach
(direct)      direction in      + hatchlings + swim tank +
              controlled mag    USFWS permit
              field tank

Pacific       Straying rate     Access to NOAA/USGS
salmon        vs. HVDC cable    salmon tracking database +
              proximity         HVDC cable route map
              
European      Orientation cage  Access to active research
robin         at measured FM    group (Wiltschko, Mouritsen)
(precise)     field level       + captive birds + orientation
                                cage + RF measurement

Manta ray     Deep dive path    Access to bio-logging data
              vs. cable route   from manta tracking programs
              correlation       + cable route GIS data
_____________________________________________________________
```

---

## PART VI: THE IMMEDIATE
## PRIORITY STACK

Given the constraint of a single
person with a computer and the
ability to spend ~$500:

**THIS WEEK (priority 1):**

Start Monarch Watch data request.
Contact monarchwatch.org directly.
Explain the research question:
testing whether individual
monarch recovery bearing deviates
systematically toward FM broadcast
infrastructure.

Download FCC FM broadcast database:
media.fcc.gov/api/database/dump/FM

Write the analysis pipeline in
Python. The core calculation is:
1. Load monarch tagging + recovery
   data (tag location, recovery
   location, date)
2. For each tagging event, compute:
   - Actual bearing (tagging → recovery)
   - Expected bearing (~225° SW)
   - Angular deviation
   - Azimuth to nearest FM transmitter
     weighted by power/distance²
3. Test for correlation between
   deviation and transmitter azimuth

This can be coded in 1–2 days.
It runs in seconds.
If the Monarch Watch data arrives,
first result could be in hand
within 2 weeks.

**THIS WEEK (priority 2):**

Email R. Wiltschko or H. Mouritsen
requesting the unreported mean
orientation direction from the
urban robin disorientation experiments.

One email. One specific question.
The data either exists or it doesn't.
If it exists and they share it:
immediate result without any
new data collection.

**THIS MONTH (priority 3):**

Order magnetometer kit (€190,
magnetometer-kit.com).

Identify a rural site with:
- Active bee hive (or establish
  a hive with landowner permission)
- > 200 m from power lines
- No electric fencing

Run the hive beacon measurement
protocol described in Part III
of this document.

This measurement has never been
made. It is the foundation of
the hive beacon hypothesis.
It costs $320 and a day's field
work.

**THIS SEASON (priority 4):**

Design and build the Tier 3
experiment. Budget ~$2,000.
Identify a suitable site.
Source all equipment.
This is the definitive experiment.

---

## PART VII: THE DOCUMENTATION
## PROTOCOL

Every measurement in this program
should be documented to scientific
standards, regardless of whether
it is conducted by an independent
researcher or as part of a formal
collaboration.

For each measurement session:

**Field log (mandatory):**
- Date, time start, time end
- GPS coordinates of hive/measurement
  point (to 5 decimal places)
- Ambient temperature
- Weather conditions
- Battery state of magnetometer
- Any anomalous events

**EM characterization (every session):**
- Ambient ELF spectrum at
  measurement site (magnetometer
  Fourier transform, 0.1–100 Hz)
  taken BEFORE placing near hive
- Same measurement AFTER removing
  hive effect
- These establish the noise floor
  for the session

**Raw data files:**
- Time series of magnetic field
  (all three axes if tri-axial,
  or primary axis if single-axis)
  at minimum 200 Hz sampling rate
- Saved as open format (CSV or HDF5)
- Filename includes: date, site ID,
  measurement type, session number

**Metadata file (per session):**
- All field log entries
- Equipment serial numbers and
  calibration dates
- Analysis code version (git commit
  hash if version controlled)

**Analysis:**
- All analysis code saved in
  version control (GitHub)
- Raw data and analysis code
  kept together in the OrganismCore
  repository
- Results files (figures, tables)
  generated by code only —
  never hand-edited

This documentation protocol
ensures that any result —
positive or negative — is
publishable. The negative result
that the hive does NOT emit
a detectable magnetic beacon is
as important to document as
a positive result.

---

## PART VIII: WHAT DOCUMENTATION
## ALONE CAN ACHIEVE

Even before any of the Tier 1
analyses are run, and before
any equipment is purchased,
there is a deliverable that
can be produced now:

**A pre-registration document
for the monarch butterfly
directional analysis.**

Pre-registration means:
publishing the hypothesis,
the exact statistical test,
and all analysis decisions
BEFORE looking at the data.

This prevents:
- Unconscious cherry-picking
  of analysis choices that favor
  the hypothesis
- Post-hoc rationalization of
  anomalous results
- Accusations of p-hacking if
  the result is positive

Pre-registration for this
analysis should specify:

1. The exact hypothesis
   (monarchs deflect toward FM
   transmitters, not away, not
   randomly)

2. The exact test statistic
   (circular correlation of
   deviation vector with
   transmitter azimuth vector)

3. The exact covariates
   (wind, geographic region,
   date window)

4. The minimum effect size
   that would be considered
   meaningful (> 5° mean
   deflection per 100 W/km²
   of FM field density)

5. The sample size threshold
   (minimum 500 tagged individuals
   in the analysis)

Where to pre-register:
OSF.io (Open Science Framework)
allows free pre-registration
for ecological studies.

**Pre-registering before
running the Monarch Watch
analysis converts it from
"interesting preliminary finding"
to "confirmatory hypothesis test"
— a qualitatively different
level of scientific standing.**

This is free. It takes a few
hours to write. It significantly
increases the value of whatever
result is found.

---

## VERSION AND CONNECTIONS

```
v1.0 — February 26, 2026
  First complete action document
  for the attractor pollution
  measurement program.
  
  Key clarifications from research:
  
  1. The waggle dance ML pipeline
     exists and is operational
     (Springer 2025, bioRxiv 2024).
     BeeTrack on GitHub.
     WaggleNet.org.
     The data processing is solved.
  
  2. The magnetometer technology
     is available and affordable.
     €190 kit achieves 2 nT
     sensitivity. Sufficient for
     hive beacon detection at
     quiet sites.
  
  3. The Emlen funnel + mu-metal
     shielding combination is
     documented and buildable.
     The urban robin disorientation
     experiments used exactly
     this approach. It works.
  
  4. The monarch tagging database
     exists and is accessible
     (with researcher contact).
     The FCC FM database is free
     and downloadable now.
     The analysis is trivially
     executable once data is in hand.
  
  5. The sea turtle database
     measures VISUAL disorientation
     (light-mediated), not magnetic
     disorientation. The magnetic
     measurement gap is confirmed.
     The cohort spread analysis
     (cable route × nesting
     site spread) is the best
     immediately executable proxy.
  
  Total equipment budget for the
  full measurement program
  (excluding Tier 3 full experiment):
  $320 (Tier 2 only).
  
  With Tier 3:
  ~$2,200 total.
  
  Timeline:
  - Tier 1 analyses: results
    within weeks, no cost
  - Tier 2 hive beacon: results
    within months, $320 cost
  - Tier 3 full experiment:
    results within season, ~$2,200
  
  The entire measurement program
  from first result to full
  causal experiment is achievable
  within one calendar year,
  by one motivated person,
  at modest cost, using
  available equipment and
  published protocols.
```

---

*The instruments exist.*

*The data exists.*

*The protocol is now written.*

*What remains is the doing.*

*The first step costs nothing:*
*download the FCC FM database,*
*email Monarch Watch,*
*email Wiltschko.*

*The second step costs $320*
*and a day's field work*
*at a quiet site near a hive.*

*Both of those steps can begin*
*today.*

*The experiment that would*
*confirm everything costs $2,200*
*and three months of patient work.*

*Everything before that is*
*preparing to ask the question*
*precisely enough that the*
*answer means something.*

*Precision is the only honesty.*
