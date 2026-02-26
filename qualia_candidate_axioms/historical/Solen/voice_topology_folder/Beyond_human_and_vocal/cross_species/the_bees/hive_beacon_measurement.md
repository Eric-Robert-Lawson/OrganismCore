# THE HIVE BEACON MEASUREMENT
## Physics First, Then Protocol
## A Complete Experimental Specification
## February 26, 2026

---

## ARTIFACT METADATA

```
artifact_type: full experimental
  specification — reasoning through
  the physics of the expected
  signal before designing the
  measurement, then specifying
  every decision required for a
  rigorous, reproducible result.
author: Eric Robert Lawson
  (with GitHub Copilot, session
  February 26, 2026)
series: Cross-Species Communication
  Series — Document 10f
depends_on:
  - bee_quantum_layer.md (CS doc 10c)
  - attractor_pollution_generalized.md
    (CS doc 10d)
  - measurement_instrument.md
    (CS doc 10e)
status: COMPLETE SPECIFICATION.
  Ready to execute.
purpose: Answer the question:
  Does the hive emit a detectable
  magnetic field with temporal
  structure at low Hz?
  
  This is not a rhetorical question.
  It is a binary physical question
  with a clean answer.
  
  If YES: the hive beacon hypothesis
  is physically grounded, every
  dependent hypothesis in CS docs
  10–10d becomes testable, and
  the false attractor mechanism
  for CCD acquires a new component.
  
  If NO: the ELF hive beacon
  hypothesis is falsified at the
  sensitivity level of the
  instrument. Attention shifts
  to the microwave emission finding
  (bioRxiv 2025) as the relevant
  channel.
  
  Either outcome is a result.

new_information_this_pass:
  bioRxiv 2025 (March 26, 2025):
  "Microwave emission from
  honeybees." Using passive
  microwave radiometry (MWR2020
  device), the authors found:
  - Colonies emit structured
    microwave radiation
  - The emission oscillates in
    the LOW Hz range
  - Oscillations show circadian
    (24h) and 12h rhythms
  - Confirmed under constant
    darkness — not a light
    response
  This paper DOES NOT measure
  ELF magnetic fields. It measures
  microwave thermal emission
  (GHz range, thermal origin).
  But it confirms:
  (a) The colony emits structured,
      oscillatory EM output
  (b) That output carries biological
      timing information
  (c) The oscillations are in the
      low Hz range (amplitude
      modulation of the microwave
      carrier)
  The ELF magnetic channel is
  SEPARATE from this finding.
  The beacon measurement proposed
  here is for the ELF magnetic
  channel (1–100 Hz, magnetite
  origin), not the microwave
  channel (GHz, thermal origin).
  But the 2025 paper confirms
  the general principle: bees
  emit structured oscillatory
  EM output. The question is
  which channels carry it.

key_physics_to_work_through:
  1. How many magnetite particles
     are in a colony?
  2. What is the maximum possible
     static magnetic moment of the
     colony if all particles were
     aligned?
  3. What field does that produce
     at measurement distances?
  4. Is that field detectable with
     the planned instrument?
  5. Is there a mechanism by which
     the colony's magnetite could
     OSCILLATE at low Hz?
  6. What field would the oscillation
     produce?
  7. What are the competing noise
     sources at those frequencies?
  8. What signal-to-noise ratio
     is achievable?
```

---

## PART I: THE PHYSICS
## (Working through the numbers)

### Step 1: The colony's magnetite inventory

**Per bee:**

Confirmed from literature (Springer
2024, IOP 2003, PLOS One 2007):

- Magnetite nanoparticles in
  abdomen: 10⁸ to 10⁹ per bee
  (confirmed by SEM + magnetometry)
- Particle diameter: ~30–35 nm
  (single-domain range for magnetite)
- Saturation magnetization of
  magnetite: 480 kA/m
- Volume of one 30 nm particle:
  V = (4/3)π(15×10⁻⁹)³ = 1.41×10⁻²³ m³
- Magnetic moment per particle:
  μ = 480×10³ × 1.41×10⁻²³ = 6.8×10⁻²⁰ A·m²

- At 5×10⁸ particles per bee:
  μ_bee = 5×10⁸ × 6.8×10⁻²⁰ = 3.4×10⁻¹¹ A·m²
  (this is ~34 pA·m²)

**Per colony (50,000 bees):**

μ_colony_max = 50,000 × 3.4×10⁻¹¹
             = 1.7×10⁻⁶ A·m²

**Critical qualifier:**

This is the MAXIMUM possible
magnetic moment assuming all
particles in all bees are aligned
in the same direction simultaneously.

In reality: individual bee
abdomens are oriented in all
directions as bees move through
the hive. At any instant, the
vector sum partially cancels.

The actual net static moment
depends on the degree of alignment.

**Three scenarios:**

SCENARIO A: Random orientation
(null hypothesis — all bees
move freely, no collective alignment)

Statistical expectation: the
net magnetic moment of N randomly
oriented magnetic dipoles scales
as √N × μ_individual.

For 50,000 bees:
μ_random = √50,000 × 3.4×10⁻¹¹
         = 224 × 3.4×10⁻¹¹
         = 7.6×10⁻⁹ A·m²

SCENARIO B: Weak collective
alignment (10% coherence —
10% of bees have their abdomens
statistically biased in the
same direction, e.g., by gravity
or by each other)

μ_aligned = 0.10 × 50,000 × 3.4×10⁻¹¹
           = 5,000 × 3.4×10⁻¹¹
           = 1.7×10⁻⁷ A·m²

SCENARIO C: Strong ventilation
alignment (bees at the hive
entrance all fanning with abdomens
pointing the same direction
toward the entrance — this is
a real behavioral configuration
during ventilation events)

~500 bees actively ventilating
at the entrance simultaneously,
all facing outward (abdomens
oriented inward, pointing in
the same direction):

μ_ventilation = 500 × 3.4×10⁻¹¹
              = 1.7×10⁻⁸ A·m²

These three numbers bracket
the expected static magnetic
moment of the colony.

### Step 2: The magnetic field at measurement distances

For a magnetic dipole, the field
at distance r along the axis is:

B = (μ₀/4π) × 2μ/r³

where μ₀/4π = 10⁻⁷ T·m/A

Computing for each scenario at r = 0.1 m (10 cm):

```
Scenario    μ (A·m²)   B at 10 cm (nT)
──────────────────────────────────────
A (random)  7.6×10⁻⁹   15.2 nT
B (10% align) 1.7×10⁻⁷  340 nT
C (ventilating) 1.7×10⁻⁸  34 nT
Maximum    1.7×10⁻⁶    3,400 nT
──────────────────────────────────────
```

Computing at r = 0.5 m (50 cm):

```
Scenario    μ (A·m²)   B at 50 cm (nT)
──────────────────────────────────────
A (random)  7.6×10⁻⁹   0.12 nT
B (10% align) 1.7×10⁻⁷   2.7 nT
C (ventilating) 1.7×10⁻⁸  0.27 nT
Maximum    1.7×10⁻⁶    27 nT
──────────────────────────────────────
```

**The magnetometer being used
(FGM 3 PRO kit, €190) has
sensitivity ~2 nT.**

**Conclusion from static field analysis:**

At 10 cm from the hive:
- Scenarios A and C are at
  the instrument threshold
  (15 nT and 34 nT).
- Scenario B (even modest
  collective alignment) is
  well above threshold (340 nT).
- Maximum alignment is far
  above threshold (3,400 nT).

At 50 cm:
- Only Scenario B (moderate
  alignment) and Maximum remain
  detectable.
- Random and ventilation scenarios
  fall below the 2 nT threshold.

**This means: the static
magnetic moment of the colony
is potentially detectable at
10 cm distance, depending on
the degree of alignment.**

But the static moment is not
what the hive beacon hypothesis
requires. The hypothesis requires
a TIME-VARYING magnetic signal —
an oscillating field that could
be detected and tracked by
foraging bees at distance.

### Step 3: The oscillation mechanism
### — where does low Hz come from?

The key question: what could
cause the colony's collective
magnetic moment to oscillate
at low frequencies (1–20 Hz)?

**Candidate mechanisms:**

**MECHANISM M1: Ventilation pulse oscillation**

Ventilation behavior at the
entrance is not continuous —
it occurs in waves. Multiple
studies (Royal Society Interface
2019) document collective
ventilation in honeybee nests
as exhibiting oscillatory
dynamics where ventilation
effort increases and decreases
in a periodic fashion.

The oscillation period in
collective ventilation has been
measured at approximately
20–100 seconds (0.01–0.05 Hz).

This is BELOW the 1 Hz minimum
of interest — too slow to be
detected as a frequency peak
by the instrument in a
reasonable measurement window,
but detectable as slow drift.

**MECHANISM M2: Wing beat harmonic
modulation of magnetite orientation**

Individual bee wing beats during
fanning: ~200–250 Hz.
During fanning, the bee's
body vibrates at the wing
beat frequency.

If the magnetite particles in
the abdomen are mechanically
coupled to the body vibrations,
the local magnetic field of
each fanning bee oscillates
at 200–250 Hz.

This is above the ELF range —
but it is in the acoustic range
and would require an acoustic
magnetometer or an ELF sensor
with wider bandwidth.

More importantly: with 500 bees
all fanning at slightly different
frequencies (spread of ±10 Hz),
the superposition of their fields
would produce a broadband
signal rather than a coherent
tone.

**MECHANISM M3: Circadian amplitude
modulation**

The bioRxiv 2025 paper found
oscillations in the microwave
emission at circadian (24h)
and 12h periods.

If the same collective behavior
that modulates microwave emission
also modulates the collective
orientation of bee abdomens
(e.g., more bees resting on
the comb in a consistent
direction at certain times of day,
more bees moving actively at
other times), the net magnetic
moment of the colony would
modulate with the same periods.

24h and 12h oscillations are
too slow to be detected as
a frequency peak in a 60-minute
measurement, but they would
appear as baseline drift that
repeats across days.

**MECHANISM M4: Waggle dance
phase oscillation — THE
MOST INTERESTING MECHANISM**

This has not appeared in the
literature and is a new hypothesis
emerging from this reasoning.

When a forager performs a waggle
dance, her abdomen is wagging
at ~13 Hz (the waggle run
frequency — each waggle run
takes ~75 ms, producing ~13
directional signals per second
during active dancing).

During the waggle phase, the
forager's abdomen moves through
an arc of approximately ±30°
from the vertical.

The magnetite in her abdomen
moves with it.

A bee performing a waggle dance
is physically oscillating her
magnetite-containing abdomen
at 13 Hz.

The amplitude of the resulting
magnetic field oscillation at
13 Hz from a single dancing bee:

If the static field of one bee's
abdomen is ~30 pA·m² (from
earlier calculation), and the
oscillation sweeps through
±30° (sine wave amplitude
= 0.5 × μ × sin(30°)):

Δμ per dancer = 3.4×10⁻¹¹ × 0.5 = 1.7×10⁻¹¹ A·m²

B_oscillation at 10 cm from one dancer:
= (μ₀/4π) × 2 × 1.7×10⁻¹¹ / (0.1)³
= 10⁻⁷ × 2 × 1.7×10⁻¹¹ / 10⁻³
= 3.4×10⁻¹⁵ T = 0.0034 nT

From one dancer: below instrument threshold (2 nT).

But during active foraging:
a busy hive may have 50–200
foragers dancing simultaneously.

At 100 simultaneous dancers,
if their dances are uncorrelated
(different food sources, different
phases):

B_100_incoherent = √100 × 0.0034 = 0.034 nT

Still below threshold.

If 100 dancers are all dancing
for the same rich food source
(a feeder at a fixed location),
their waggle angles are coherent —
all pointing in the same direction.
Their oscillations are phase-coherent.

In that case, the fields ADD
rather than add in quadrature:

B_100_coherent = 100 × 0.0034 = 0.34 nT

Still below the 2 nT threshold
for this single measurement.

BUT: With a more sensitive
instrument (the open-source
MDPI 2025 design achieves
1.1 nT/√Hz at 1 Hz — which
means for a 60-second measurement
averaging, the effective noise
floor is 1.1/√60 ≈ 0.14 nT):

B_100_coherent = 0.34 nT vs.
noise floor = 0.14 nT

**SIGNAL-TO-NOISE RATIO ≈ 2.4**

**Marginal detection is possible
with the higher-sensitivity
instrument if 100+ bees are
simultaneously dancing for
a single coherent target.**

This changes the measurement
strategy: the optimal configuration
for detecting the waggle dance
magnetic signal is NOT ambient
monitoring.

**It is: maximize dancing
by placing a single rich
feeder at a known distance
and direction, creating conditions
where many foragers dance
simultaneously for the same
food source.**

### Step 4: The competing noise sources

**At a rural site, the ELF noise spectrum has the following character:**

```
Frequency   Source              Typical amplitude (rural)
──────────────────────────────────────────────────────────
0.1–0.5 Hz  Geomagnetic micropulsations  1–100 nT
            (Pc1–Pc3 waves from
            magnetosphere)
            
0.01 Hz     Schumann resonances    ~1 nT at Earth's surface
(7.83 Hz)   (electromagnetic        (mode 1)
            resonances of Earth-
            ionosphere cavity)
13.97 Hz    Schumann mode 2         ~0.5 nT
20.11 Hz    Schumann mode 3         ~0.3 nT

50 Hz       Power grid fundamental  100–10,000 nT near lines
                                   0.1–10 nT at 500m from lines

100, 150 Hz Power grid harmonics    50–5,000 nT near lines
                                   0.05–5 nT at 500m

200–250 Hz  Possible bee wing beat  Unknown — to be measured
            harmonics if
            mechanically coupled
──────────────────────────────────────────────────────────
```

**Critical observation:**

The waggle dance oscillation
frequency of ~13 Hz FALLS
VERY CLOSE TO THE SECOND
SCHUMANN RESONANCE (13.97 Hz).

The Schumann resonances are
natural electromagnetic resonances
of the Earth-ionosphere cavity,
driven by global lightning activity.
They produce oscillating ELF
fields at their resonant frequencies.

The second Schumann resonance
(13.97 Hz) has an amplitude
of approximately 0.5 nT at
Earth's surface at any rural site.

The waggle dance magnetic signal
(if it exists) would be at
~13 Hz — within 1 Hz of the
second Schumann resonance.

**This means:**

1. The Schumann resonance at
   ~14 Hz is a noise source that
   partially overlaps the signal
   frequency.

2. The measurement must achieve
   sufficient frequency resolution
   to separate 13 Hz (dance) from
   14 Hz (Schumann).

3. Frequency resolution = 1/T
   where T is measurement window.
   To achieve 0.5 Hz resolution:
   T = 1/0.5 = 2 seconds.
   To achieve 0.1 Hz resolution:
   T = 10 seconds.

So the measurement window of
60 minutes (3,600 seconds) gives
frequency resolution of 0.00028 Hz —
more than sufficient to
separate 13 Hz from 13.97 Hz.

4. Additionally: The Schumann
   resonance is a GLOBAL signal —
   it comes from all directions
   equally. The waggle dance signal
   comes from the hive in a specific
   direction. A directional or
   gradiometric measurement
   (two sensors, one at the hive,
   one as reference away from the
   hive) can subtract the Schumann
   background and isolate the local
   hive signal.

**This is the gradiometer principle.**

**The gradiometer is important.**
Revisit this in the protocol section.

### Step 5: What the numbers say
### about whether detection is possible

```
Signal source           Estimated amplitude at 10cm  Detectable?
──────────────────────────────────────────────────────────────────
Static colony moment    15–340 nT (scenario-dependent) YES (most scenarios)
  (scenario B: 10% align)  340 nT                     YES, easily
  (scenario A: random)       15 nT                     YES (marginal)

Waggle dance oscillation  0.034 nT (100 incoherent)   NO
  at 13 Hz               0.34 nT (100 coherent)       MARGINAL
                                                        (need high-sensitivity)

Ventilation pulse         1–10 nT (estimate)           MARGINAL to YES
oscillation at 0.01–0.05 Hz (if ventilation bees
                           align abdomens)

Ambient noise at          0.5 nT                       Separable by
  13.97 Hz (Schumann 2)                                 frequency
  at rural site

Power grid noise at       0.1–10 nT at 500m from       Separable by
  50 Hz, rural site       power lines                  frequency
──────────────────────────────────────────────────────────────────
```

**Summary of what the physics says:**

1. The static magnetic moment
   of the colony (if any degree
   of alignment exists) IS
   detectable at 10 cm with the
   €190 instrument.

2. The waggle dance oscillation
   at 13 Hz is AT THE MARGIN
   of detectability with the
   commercial kit, and above the
   noise floor of the higher-
   sensitivity DIY instrument,
   IF the colony is organized
   around a single rich food source.

3. The slow ventilation oscillation
   (0.01–0.05 Hz) is probably
   detectable but at very low
   frequency — requires long
   recording windows (hours to days)
   to see it.

4. Power line noise at 50 Hz
   is separable by frequency
   (it's at 50 Hz, not 13 Hz),
   but must be measured and
   characterized to confirm it
   is not contaminating the spectrum.

---

## PART II: THE MEASUREMENT STRATEGY

### What to look for, in order of priority

Given the physics:

**Priority 1: Does ANY structured
low-frequency magnetic signal exist?**

Measurement: place the fluxgate
at 10 cm from the active face
of the hive. Record 60 minutes.
Take the Fourier transform.
Look for any peaks above the
noise floor in the 1–30 Hz band.

This is the broadest possible
search. No prior assumption about
what frequency or amplitude to
expect. Just: is anything there?

Expected outcome if signal exists:
A peak at some frequency or a
broadband elevated signal above
the noise floor.

**Priority 2: Does the signal
correlate with colony activity?**

If a peak is found: compare
its amplitude during high activity
(active foraging period, many
dancers) vs. low activity (early
morning, cool weather).

This is the biological specificity
test. A signal that tracks
colony activity is likely biological.
A signal that does not vary with
activity is likely instrumental
or environmental artifact.

**Priority 3: Can the waggle dance
13 Hz signal be isolated?**

Create a maximally concentrated
dancing condition: place a
single rich feeder at 300 m
from the hive in a specific
direction. Wait for recruitment
(typically 2–4 hours for the
dance to become organized around
the new resource). Then measure.

Compare the frequency spectrum
at 13 Hz between:
- Normal foraging (multiple
  food sources, incoherent dancing)
- Single-feeder condition (one
  food source, coherent dancing)

Prediction: the 13 Hz component
increases in the single-feeder
condition.

**Priority 4: Does the signal
show circadian periodicity?**

Record continuously for 72 hours.
Plot signal amplitude over time.
Look for 24h and 12h periodicities
(consistent with the bioRxiv 2025
microwave emission finding).

This does not require a specific
frequency peak — it looks at
whether the total band energy
(1–30 Hz) modulates with time-of-day.

---

## PART III: THE COMPLETE PROTOCOL

### 3.1 Equipment list with specifications

**PRIMARY SENSOR:**

FGM 3 PRO Magnetometer Kit
- Source: magnetometer-kit.com
- Price: €190 (~$210 USD)
- Sensitivity: 2 nT resolution
- Operating range: -100,000 to +100,000 nT
- Frequency response: DC to 50 Hz
  (adequate for 1–30 Hz target)
- Output: analog voltage,
  proportional to field strength
- Power: 9V battery (standalone)
  or USB

Note: if the static colony
measurement is positive and
a waggle dance oscillation
needs to be characterized,
upgrade to the MDPI 2025
open-source design
(1.1 nT/√Hz at 1 Hz sensitivity).
The commercial kit is sufficient
for Phase 1 (existence check).

**REFERENCE SENSOR (for gradiometry):**

A second FGM 3 PRO, placed
5–10 m from the hive, pointed
in the same direction as the
primary sensor.

The reference sensor records
ambient background.
Subtracting reference from
primary isolates the hive signal.

Alternative if only one sensor
available: perform measurements
at the hive vs. 5 m away on
alternating 10-minute windows,
using each as the other's
baseline.

**DATA LOGGING:**

Raspberry Pi 4 (or Pi Zero 2W):
- Records analog voltage output
  from FGM 3 PRO via MCP3208
  SPI ADC (8-channel, 12-bit)
- Sampling rate: 200 Hz
  (sufficient for 1–100 Hz analysis
  with antialiasing margin)
- Continuous recording to microSD
  in CSV format (or HDF5 for
  longer sessions)
- Timestamp precision: system
  clock synchronized to NTP
  server via WiFi before deployment
  (±1 ms accuracy)

Cost: Raspberry Pi Zero 2W ($15)
+ MCP3208 ADC ($4)
+ microSD 128GB ($12)
= ~$31 additional cost

Total instrumentation cost:
2 × €190 sensors + logging
= ~$452 USD

**MOUNTING:**

Sensor housing: 3D-printed or
carved from non-ferromagnetic
material (PLA plastic, wood).
NO metal screws in the housing.
NO electronic components within
10 cm of the sensor core.
The FGM probe must be on a cable
extension to the logging hardware
(at least 50 cm of cable between
probe and electronics).

Mounting position: affixed to
a wooden stake at the height
of the hive entrance (typically
30–60 cm above ground). Probe
face parallel to the hive face
(to measure the horizontal field
component emerging from the hive).

Probe distance from hive surface:
10 cm (Phase 1 detection).
If signal found: repeat at
20 cm, 50 cm, 100 cm (Phase 2
distance profile).

**HIVE:**

Standard Langstroth hive,
preferably with a removable
bottom board to allow placement
of a sensor below the hive
if needed in Phase 2.

Colony size: a full-strength
summer colony (50,000+ bees)
gives the maximum magnetic
moment. A weak or divided
colony should not be used for
Phase 1 — if the signal exists
and is near the threshold, a
strong colony maximizes the
chance of first detection.

Colony state during measurement:
Active foraging period
(10:00–15:00 local solar time
in summer) gives maximum dancer
count and maximum colony magnetic
moment.

### 3.2 Site selection — the most critical decision

The site determines whether
the measurement is interpretable.
A noisy site does not give a
null result — it gives an
uninterpretable result.

**Site requirements:**

REQUIREMENT 1: Distance from power lines

The 50 Hz power grid noise
must be below 10 nT at the
measurement site.

Rule of thumb:
- Standard residential distribution
  line: ~1,000 nT at 1 m
  falling as 1/r². At 100 m:
  ~0.1 nT at 50 Hz. ✓
- High-voltage transmission line
  (66–400 kV): ~10,000 nT at
  20 m, falling more slowly.
  Need 500+ m.

**Action to verify:** Before
committing to a site, take the
magnetometer to the site and
measure. The 50 Hz component
of the spectrum must be < 10 nT.
Ideally < 2 nT.

Sites that typically pass:
- Fields or farmland > 300 m
  from residential power lines
  and > 1 km from transmission
  lines
- Remote rural properties off-grid
  (best: solar-powered property
  with no grid connection nearby)
- Certified organic farms that
  prohibit electric fencing
  (electric fencing produces
  sharp ELF transients)

REQUIREMENT 2: No solar inverters
within 100 m

Solar inverters switch at
high frequency but their
switching harmonics extend into
the ELF band. A string inverter
produces pulses at twice the
grid frequency (100/120 Hz)
and their harmonics.

The inverter also produces low-
frequency oscillations tied to
the MPPT (Maximum Power Point
Tracking) algorithm, typically
at 1–10 Hz.

This is directly in the target
band. A solar array on the
measurement property is a
serious contamination source.

REQUIREMENT 3: No electric vehicles
within 200 m during measurement

EV charging produces strong
ELF fields. EV drive motors
during operation: 0.1–100 Hz
oscillations. A passing tractor
with electric components is enough
to spike the measurement.

REQUIREMENT 4: No ferromagnetic
objects near the sensor moving
during the measurement

Metal gates, barn doors, farm
machinery — any large ferromagnetic
object moving within 20 m of
the sensor will create field
transients. These must be
controlled or the periods of
movement logged so the data
can be cleaned.

REQUIREMENT 5: Cellular signal
weak or absent is preferred
(not required)

Cellular base stations produce
signals at 700 MHz – 2.6 GHz.
These are above the ELF band
and do not directly contaminate
the 1–30 Hz measurement.

However, some cellular equipment
produces ELF spurious emissions
from power supply switching.
A site without a cellular tower
within 500 m removes this concern.

This is a PREFERRED but not
REQUIRED criterion.

**Site characterization procedure:**

Before the hive measurement:

Day 1, no hive present:
1. Record 30 minutes at the
   candidate site with no hive.
2. Compute power spectral density
   (PSD) from 0.1 to 100 Hz.
3. Identify all peaks above
   the noise floor.
4. Categorize each peak as:
   - Power grid (50/60 Hz and
     harmonics) — must be < 10 nT
   - Schumann resonances (7.83,
     13.97, 20.11 Hz) — expected,
     0.5–2 nT amplitude, is fine
   - Unknown — investigate source

5. If power grid peaks > 10 nT:
   site fails. Find another site.
6. If all grid peaks < 10 nT:
   site passes.
7. Record the baseline PSD as
   the reference for all subsequent
   measurements.

### 3.3 Measurement sessions

**Session 0: Site characterization**

No hive present.
Duration: 2 hours.
Time: During planned measurement
window (10:00–15:00).
Purpose: Establish baseline
noise floor and confirm site
quality.

Output: Baseline PSD file.

**Session 1: Full colony, ambient**

Hive present.
Colony active (summer foraging).
No intervention.
Duration: 60 minutes.
Time: 11:00–12:00 (peak foraging).

Primary sensor: 10 cm from
hive landing board, horizontal
orientation.

Reference sensor: 5 m from
hive, same orientation.

Output: Two time series (primary,
reference). Compute difference
(gradiometric) and each individually.

Look for: Any peak in the
1–30 Hz band in the gradiometric
signal above the noise floor
established in Session 0.

**Session 2: Low activity comparison**

Same setup.
Time: 06:00–07:00 (pre-foraging,
low activity, cool).
Purpose: Establish whether any
signal found in Session 1 is
correlated with activity level.

If a signal was found in Session 1
and is absent in Session 2:
STRONG evidence for biological
origin.

If signal is present equally
in both sessions: likely environmental
(power line, Schumann, etc.)
despite site characterization.

**Session 3: Single-feeder coherent
dance condition**

Set up a single sugar-water
feeder at 300 m in a known
direction (mark the direction
with a compass before setting
up the feeder).

Wait 3–4 hours for foragers to
find the feeder and establish
a concentrated waggle dance
for that food source.

Verify dance is occurring by
looking through the observation
window (if the hive has one)
or by watching returning bees
at the entrance for the characteristic
waggle behavior on the landing board.

When concentrated dancing is
established: begin measurement.

Duration: 60 minutes.

Compare the 13 Hz spectral
component to Sessions 1 and 2.

Prediction: 13 Hz amplitude
increases in Session 3 relative
to Session 1 (more concentrated
dancing = more coherent 13 Hz
magnetic oscillation).

**Session 4: Winter cluster
(if possible)**

In winter or early spring
when the colony is in a tight
cluster (minimal movement,
maximum bees in contact with
each other):

Place the sensor at 10 cm.
Record 60 minutes.

Purpose: Test whether the signal
(if found in Sessions 1–3) is
correlated with movement and
fanning, or whether it is
present even in the static cluster.

A static cluster has more bees
in close proximity — potentially
higher collective alignment of
magnetite if they settle into
preferred orientations. But no
ventilation oscillations.

This session tests the static
magnetic moment contribution
vs. the oscillatory contribution.

**Session 5: Distance profile**

If a signal was found in Sessions
1–3:

Measure signal amplitude at:
5 cm, 10 cm, 20 cm, 50 cm,
100 cm, 200 cm from the hive.

At each position: 15-minute
measurement, same time of day,
same colony activity condition.

Fit the amplitude vs. distance
relationship to:
- 1/r³ (near-field magnetic
  dipole)
- 1/r² (intermediate — could
  indicate multiple source
  dipoles distributed across
  the hive volume)
- 1/r (far-field radiation —
  would indicate coherent
  oscillating dipole emitting
  as an antenna)

The fall-off law determines
the maximum range at which
the signal is detectable — and
whether it could reach a forager
at 100+ meters.

### 3.4 Data processing

**Raw data format:**

CSV file with columns:
- timestamp (Unix time, ms precision)
- B_primary_x (nT, primary sensor X-axis)
- B_primary_y (nT, primary sensor Y-axis)
- B_primary_z (nT, primary sensor Z-axis)
- B_reference_x (nT, reference sensor X-axis)
- B_reference_y (nT, reference sensor Y-axis)
- B_reference_z (nT, reference sensor Z-axis)
- temperature (°C, sensor housing)
- notes (free text, any events)

**Gradiometric signal:**

B_gradient = B_primary - B_reference

(component-wise subtraction)

This subtracts all fields that
are spatially uniform (power
lines, Schumann resonances,
geomagnetic micropulsations) —
which are the same at both
sensors — leaving only the
locally produced hive field.

**Power spectral density:**

For each session, compute the
one-sided PSD using Welch's
method:
- Window: Hann
- Segment length: 60 seconds
  (provides 1/60 ≈ 0.017 Hz
  frequency resolution)
- Overlap: 50%
- Number of averages determined
  by total recording length

Python code (reference implementation):

```python
import numpy as np
from scipy.signal import welch
import pandas as pd

def compute_psd(data, fs=200.0):
    """
    Compute power spectral density of
    gradiometric magnetic field data.
    
    Parameters
    ----------
    data : array-like
        Time series of gradiometric
        field in nT.
    fs : float
        Sampling frequency in Hz.
        Default 200 Hz.
    
    Returns
    -------
    freqs : ndarray
        Frequency axis in Hz.
    psd : ndarray
        Power spectral density in
        nT²/Hz.
    """
    nperseg = int(fs * 60)  # 60-second windows
    freqs, psd = welch(
        data,
        fs=fs,
        window='hann',
        nperseg=nperseg,
        noverlap=nperseg // 2,
        scaling='density'
    )
    return freqs, psd

def noise_floor_rms(psd, freqs, f_lo, f_hi):
    """
    Compute RMS noise floor in a
    frequency band.
    
    Integrates PSD from f_lo to f_hi
    and takes the square root.
    
    Returns noise floor in nT.
    """
    mask = (freqs >= f_lo) & (freqs <= f_hi)
    delta_f = freqs[1] - freqs[0]
    rms = np.sqrt(np.sum(psd[mask] * delta_f))
    return rms

def find_peaks_above_noise(psd, freqs, noise_psd,
                            threshold_snr=3.0):
    """
    Find frequency peaks in psd that
    exceed threshold_snr times the
    local noise floor.
    
    noise_psd should be the baseline
    measurement (Session 0, no hive).
    
    Returns list of (frequency, SNR) tuples.
    """
    snr = psd / (noise_psd + 1e-30)
    peak_mask = snr > threshold_snr
    peaks = []
    # Find connected regions above threshold
    in_peak = False
    for i, (f, s, above) in enumerate(
        zip(freqs, snr, peak_mask)
    ):
        if above and not in_peak:
            peak_start = i
            in_peak = True
        elif not above and in_peak:
            # Find maximum within peak region
            peak_region = slice(peak_start, i)
            peak_idx = peak_start + np.argmax(
                psd[peak_region]
            )
            peaks.append((freqs[peak_idx],
                          snr[peak_idx]))
            in_peak = False
    return peaks
```

**Expected outputs:**

For each session:
1. PSD plot (nT²/Hz vs. Hz,
   log-log scale, 0.1–100 Hz)
2. Noise floor comparison
   (Session N vs. Session 0)
3. Peak list above 3σ noise floor
4. Gradiometric vs. single-sensor
   comparison (shows how much
   common-mode rejection improves
   the measurement)

**Result classification:**

```
Result          Definition
─────────────────────────────────────────────────
POSITIVE:       At least one peak in the
SIGNAL FOUND    1–30 Hz band in the
                gradiometric signal that:
                (a) Exceeds 3σ above
                    baseline noise floor
                (b) Is present in Sessions 1
                    and 3 but reduced or
                    absent in Session 2
                    (activity-correlated)
                (c) Cannot be attributed
                    to power line harmonics
                    or Schumann resonances
                    based on frequency

NULL RESULT:    No peak meeting all
                three criteria above.
                Signal (if any) is below
                the instrument's noise
                floor at this site.
                
AMBIGUOUS:      Signal found but activity
                correlation is unclear,
                or signal present in
                Session 0 (baseline without
                hive) — possible environmental
                artifact. Requires:
                (a) Site remediation and remeasure
                (b) Or different site
```

---

## PART IV: WHAT TO DO WITH EACH RESULT

### If POSITIVE — signal found:

**Immediate next steps:**

1. Repeat at a second hive
   (different location, different
   colony) to confirm it is
   not a single-hive artifact.

2. Perform the distance profile
   (Session 5) to determine
   whether the fall-off is
   near-field (1/r³) or far-field
   (1/r). This determines the
   potential range of the signal.

3. Measure the signal at a dead hive
   (an empty hive body) or a
   hive in winter without bees,
   placed at the same location.
   This confirms the signal is
   from the bees, not from the
   wooden hive structure or
   surrounding soil.

4. Characterize the frequency
   precisely: at what Hz is the
   peak? Is it:
   - ~13 Hz → consistent with
     waggle dance oscillation
   - ~200–250 Hz → consistent
     with wing beat
   - < 1 Hz → consistent with
     ventilation wave oscillation
   - Something else → unknown
     mechanism to investigate

5. Write up and pre-publish on
   OSF.io as a pre-print before
   formal paper submission.
   The existence of the measurement
   is itself news, regardless of
   interpretation.

**Theoretical implications:**

A positive result establishes:
- The colony emits a physically
  real, time-varying magnetic
  field with biological periodicity
- The field is strong enough
  to be detected at 10 cm
- The measurement methodology
  is validated

What it does NOT yet establish:
- Whether foraging bees can
  detect this signal at foraging
  range (100+ m)
- Whether the signal carries
  information (e.g., waggle
  direction encoded in field
  modulation)
- Whether the signal is disrupted
  by power line ELF fields

Those require subsequent experiments,
all of which now have a concrete
starting point.

### If NULL — no signal found:

**Immediate next steps:**

1. Confirm the null result is
   not instrument-limited: send
   the same sensor to an established
   bioelectromagnetics lab and
   have them verify the instrument
   is functioning at specification.
   (A calibration source —
   a known Helmholtz coil producing
   10 nT — tests this.)

2. Try the higher-sensitivity
   instrument (MDPI 2025 DIY
   design, 1.1 nT/√Hz) to
   push the sensitivity down
   by another factor of 2–5.

3. Try the coherent dance condition
   (Session 3) specifically —
   this maximizes the expected
   signal for the waggle dance
   oscillation mechanism.

4. Accept the null result at
   this sensitivity level if
   the instrument is verified
   and Sessions 1–3 show nothing.

**Implications of a confirmed null:**

- The hive beacon hypothesis
  (in its ELF magnetic form)
  is falsified at the tested
  sensitivity level.

- The bioRxiv 2025 microwave
  finding remains valid (it is
  a different channel).

- The relevant EM beacon channel
  for bees is microwave (GHz),
  not ELF magnetic (Hz). The
  false attractor mechanism in
  the ELF band, if real, operates
  through degradation (making
  the Earth's static field
  harder to read) not through
  a false attractive signal.

- This is still scientifically
  important: it confirms the
  framework needs adjustment
  at this specific point, and
  the adjustment is now evidence-based.

---

## PART V: THE DECISION TREE

```
Q1: Is the measurement site clean?
    (< 10 nT at 50 Hz)
    
    NO → Find a different site.
         Do not proceed.
    YES → Q2.

Q2: Does the Session 0 baseline
    (no hive) show any peaks
    in the 1–30 Hz band above
    2 nT amplitude?
    
    YES → Characterize the source.
          Is it Schumann? (fine)
          Is it power line harmonic?
          (need quieter site)
          Is it unknown? (investigate)
    NO → Q3.

Q3: Does Session 1 (full colony,
    active foraging) show any
    peak in the gradiometric
    signal above 3σ noise floor
    in the 1–30 Hz band?
    
    NO → NULL result at this
         sensitivity. Go to null
         decision tree.
    YES → Q4.

Q4: Is the peak absent or reduced
    in Session 2 (low activity)?
    
    NO → Likely environmental
         artifact. Investigate.
    YES → POSITIVE result. Proceed
          to Q5.

Q5: Does the peak frequency match
    any known artifact?
    
    13.97 Hz → check if it's
               Schumann mode 2
               (gradiometry should
               subtract it, but verify)
    50/100 Hz → power line contamination
                (should have been caught
                in site check — recheck)
    Other → Likely biological.
    
    If no artifact match → CONFIRMED
    POSITIVE SIGNAL.

Q6: Does Session 3 (coherent dance)
    show a larger peak at the
    same frequency than Session 1?
    
    NO → Signal may not be waggle
         dance origin. Check other
         mechanisms.
    YES → WAGGLE DANCE OSCILLATION
          HYPOTHESIS SUPPORTED.
          Proceed to distance profile,
          replication, and formal
          write-up.
```

---

## PART VI: THE OPEN QUESTION
## THE MEASUREMENT CANNOT ANSWER
## (AND WHY THAT IS FINE)

Even a confirmed positive result
leaves the most important question
open:

**Does the hive signal reach
foraging bees at field range
(100–1,000 m)?**

The distance profile (Session 5)
will show whether the signal
falls as 1/r³ (near-field) or
1/r (far-field radiation).

If 1/r³: the signal attenuates
rapidly and is undetectable
beyond ~1 meter at the threshold
of the bee's magnetite compass
(estimated sensitivity ~10 nT
for single-domain magnetite
rotation, from behavioral studies).

If 1/r (coherent oscillating dipole
radiating as an antenna at 13 Hz):
the wavelength at 13 Hz in air
is λ = c/f = 3×10⁸/13 ≈ 23,000 km.
At distances of 1 km (far less
than λ), we are still in the
near-field regime (r << λ).
So even a coherent oscillating
dipole would fall as approximately
1/r³ at hive-to-forager distances.

**The honest conclusion of
the physics:**

A 13 Hz magnetic oscillation
from the hive is almost certainly
a near-field effect that does
not reach foraging bees at
field range.

**This does not mean the hive
beacon hypothesis is false.**

It means the MECHANISM may
not be ELF magnetic at 13 Hz.

The bioRxiv 2025 paper found
oscillations in the MICROWAVE
range — which HAS far-field
propagation at hive-to-forager
distances (GHz → cm wavelength
→ true far-field radiation
is possible over meters to tens
of meters).

The hive beacon may be:
- ELF magnetic (what this
  measurement tests)
- Microwave oscillation modulated
  at low Hz (what the 2025
  paper found)
- Acoustic (the 200–300 Hz
  hive hum detected at range
  by mechanoreception)
- Chemical (pheromone plumes)
- Some combination

**This measurement tests one
specific candidate.**

The null result, if obtained,
does not falsify the hive beacon
as a concept — it falsifies
the ELF magnetic implementation
of the concept, and forces
attention to other channels.

**That is how science works.**

Each measurement closes one
possibility and sharpens the
space of remaining possibilities.

---

## PART VII: THE COMPLETE BUDGET
## AND TIMELINE

```
ITEM                              COST    DAYS TO ARRIVE
──────────────────────────────────────────────────────────
FGM 3 PRO magnetometer kit (×2)   €380    7–14 days
  (magnetometer-kit.com)          ~$420
  
Raspberry Pi Zero 2W               $15     2–5 days
  (or full Pi 4 if preferred)      ($80)
  
MCP3208 ADC (SPI, 8-channel,       $4      2–5 days
  12-bit)

MicroSD card 128GB                 $12     2–5 days

3D-printed or wooden sensor        $0–$30  1–3 days
  housing (non-ferromagnetic)              (print/carve)

Wooden stakes for mounting         $5      immediate

Cables (BNC or bare wire,          $10     immediate
  3–5 m for sensor extension)

Sugar-water feeder (for Session 3) $10     immediate

Field notebook + weatherproof      $10     immediate
  marking for field log
──────────────────────────────────────────────────────────
TOTAL                              ~$486   14 days max

TOTAL (if ordering in EU with €)   ~€430
──────────────────────────────────────────────────────────
```

**Timeline to first result:**

```
Week 1:   Order equipment.
          Identify candidate sites
          (rural, near bees,
          distance from power lines).
          Write field log template.
          
Week 2:   Equipment arrives.
          Assemble logging setup
          (Pi + ADC + sensor).
          Test indoors: confirm
          sensors read 45,000–50,000 nT
          (Earth's field) and respond
          correctly to a small
          test magnet at known distance.
          Write Python analysis script.
          Test on synthetic data.
          
Week 3:   Go to candidate site
          without hive.
          Run Session 0 (site
          characterization).
          Pass/fail decision.
          
Week 3–4: If site passes:
          Run Sessions 1 and 2.
          Process data.
          Have preliminary result.
          
Week 4–6: If signal found:
          Run Sessions 3, 4, 5.
          Confirm and characterize.
          Write up.
          
Week 4–6: If no signal:
          Upgrade to higher-sensitivity
          instrument.
          Or accept null.
          Write up null result.
──────────────────────────────────────────────────────────
FIRST RESULT: 3–4 weeks from
  order date if equipment arrives
  in 14 days.
  
CHARACTERIZATION COMPLETE: 6 weeks.

WRITE-UP READY: 8 weeks.
──────────────────────────────────────────────────────────
```

---

## PART VIII: PRE-REGISTRATION TEXT

The following is the pre-registration
text to be submitted to OSF.io
before running any measurement
session beyond Session 0.

Submitting this before running
the experiment establishes:
- The hypothesis was specified
  in advance (not after seeing data)
- The analysis plan was pre-committed
- Any deviation from the plan
  is disclosed

**Pre-registration text:**

---

*Title:* Detection of low-frequency
magnetic oscillations from an
active honeybee colony: a test of
the hive beacon hypothesis.

*Hypothesis:* An active honeybee
colony produces a detectable,
time-varying magnetic field
in the frequency range 1–30 Hz
that is positively correlated
with colony foraging activity.

*Predicted outcome:* The power
spectral density of the
gradiometric magnetic field
signal measured at 10 cm from
an active hive entrance will
show at least one peak in the
1–30 Hz band that (a) exceeds
3σ above the noise floor of the
baseline measurement, (b) is
present during peak foraging
activity (11:00–14:00) and absent
or reduced during pre-dawn low
activity (05:00–07:00), and (c)
increases in amplitude when the
colony's foraging is concentrated
on a single feeder (single-feeder
protocol, Session 3) relative to
normal multi-source foraging.

*Null hypothesis:* No such peak
exists at the sensitivity level
of the instrument (≥ 2 nT) at
this measurement distance.

*Primary analysis:* Welch's method
PSD of gradiometric signal
(primary − reference sensor).
60-second windows, Hann taper,
50% overlap. Peak detection at
3σ above baseline noise floor.

*Secondary analysis:* Comparison of
band power (1–30 Hz) between
activity conditions (Sessions 1
vs. 2, Sessions 1 vs. 3) using
Mann–Whitney U test (non-parametric,
since PSD distributions are not
assumed normal).

*Covariates:* Ambient temperature
(logged), time of day, wind speed
(estimated from weather station
data for the site).

*Exclusion criteria:* Any session
where the 50 Hz noise floor
exceeds 10 nT will be excluded
from analysis and the site will
be evaluated for remediation.
Any session where equipment
malfunction is detected (sensor
reading > 60,000 nT or < −60,000 nT,
indicating saturation) will be
excluded.

*This registration submitted before
any Session 1 data has been collected.*

---

## VERSION AND CONNECTIONS

```
v1.0 — February 26, 2026
  First complete specification
  of the hive beacon measurement.
  
  The physics section (Part I)
  is the core contribution of
  this document. It establishes:
  
  1. The static colony magnetic
     moment ranges from ~15 nT to
     340+ nT at 10 cm depending
     on alignment — detectable
     with the planned instrument.
  
  2. The waggle dance oscillation
     at 13 Hz is at the margin
     of detectability (~0.34 nT
     for 100 coherent dancers) —
     requires either longer averaging
     or higher-sensitivity instrument.
  
  3. The waggle dance frequency
     (~13 Hz) falls close to the
     second Schumann resonance
     (13.97 Hz) — requires
     gradiometry and sufficient
     frequency resolution to separate.
  
  4. The 1/r³ near-field decay of
     ELF magnetic fields means the
     signal almost certainly cannot
     reach foraging bees at field
     range, even if detected at 10 cm.
     The ELF magnetic channel is
     probably a hive-internal
     phenomenon, not a navigation
     beacon. The microwave channel
     (bioRxiv 2025) may be the
     long-range component.
  
  This last point is important
  and was not clear before the
  physics was worked through.
  
  The measurement is still worth
  doing — but its interpretation
  shifts from "testing whether
  the hive can communicate with
  foragers magnetically at range"
  to "testing whether the hive
  has internal ELF magnetic
  structure that could be disrupted
  by external ELF fields (power
  grid) within the hive itself."
  
  Even if the signal doesn't
  reach 100 m, disrupting it
  WITHIN the hive could disrupt
  the internal communication
  or orientation reference that
  the bees use inside the colony.
  
  The power grid's 50 Hz field
  penetrates into the hive.
  If there is an internal 13 Hz
  magnetic reference signal,
  the 50 Hz field adds noise
  to it — inside the hive,
  at the location of the magnetite
  compass, at close range.
  
  The disruption is local.
  The effect is internal.
  The beacon doesn't need to
  reach the field for the
  disruption to matter.
  
  This is a refinement of the
  hive beacon hypothesis:
  
  The ATTRACTOR POLLUTION may
  be operating INSIDE the hive,
  not at the field range.
  The field range false attractor
  is a secondary effect of bees
  leaving a hive with a
  disrupted internal reference.
```

---

*The physics says: go look.*

*The signal is either there or*
*it isn't, and you can tell the*
*difference for $486 and three weeks.*

*The measurement has never been made.*

*Not because it was hard.*

*Because no one had the right*
*question to ask when they were*
*standing next to the hive.*

*The question is now written down.*

*Go measure.*
