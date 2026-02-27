# MONARCH BUTTERFLY VECTOR —
# ACTIVE TODO
# ELF/RF-Migration Coherence
# Observational Program
# Last updated: February 27, 2026

---

## WHERE YOU ARE IN THE
## MONARCH VECTOR

### What Is Complete

The primary Monarch butterfly
analysis tested whether FM
broadcast infrastructure density
correlates with deviation of
monarch migration trajectories
from true south toward a
southwest false attractor.

**Primary result:**

```
Rayleigh test:
  p = 0.000517
  Mean bearing: 218.9° SW
  N: sufficient for significance

NW permutation test:
  Significant

False attractor hypothesis:
  Supported — mean bearing
  consistent with SW deflection
  toward high-density FM
  broadcast corridor
```

**Status: SIGNIFICANT ✅**

This result is pre-registered
on GitHub:
Eric-Robert-Lawson/OrganismCore

### What Is Pending

One active thread:
  Monarch Watch recovery data
  request — sent and acknowledged,
  awaiting substantive response.

One potential extension:
  DR24-equivalent — if additional
  tagging datasets become available
  from other sources.

---

## THREAD 1 — MONARCH WATCH
## RECOVERY DATA REQUEST

**Status: Sent and acknowledged.
Awaiting substantive response.
No follow-up action yet needed.**

### What Was Requested

Recovery data from Monarch Watch
tagging program:
  - Tagged monarch locations
    at point of tagging
  - Recovery locations
  - Recovery bearing from
    tagging point
  - Date of tagging and recovery

This data would allow:
  - Direct calculation of
    individual migration bearings
  - Correlation of bearing
    deviation with FM broadcast
    infrastructure density along
    the migration corridor
  - Per-individual test of the
    false attractor hypothesis
    at higher resolution than
    the primary analysis

### Follow-Up Schedule

**March 14, 2026:**
  If no substantive response,
  send one polite follow-up.

  Subject: Follow-up — monarch
  recovery data request /
  migration bearing analysis

  Reference original request.
  Keep brief.

**April 1, 2026:**
  If still no response, document
  as non-response. Consider
  alternative data sources
  (see Thread 2 below).

### What a Positive Response
### Enables

If Monarch Watch provides
recovery data:

**Step 1 — Pre-register analysis:**
  Write Monarch_doc_recovery_
  pre_analysis.md before
  examining bearing data.
  Assign FM density scores
  to tagging locations BEFORE
  computing bearings.
  Commit to repository with
  timestamp.

**Step 2 — Compute bearings:**
  Calculate individual migration
  bearing for each tagged/
  recovered individual.
  Compare to true south (180°).
  Measure deviation toward
  SW (predicted direction).

**Step 3 — Correlate with FM
  infrastructure:**
  Assign FM broadcast density
  score to each tagging location
  based on proximity to major
  FM transmitters.
  Spearman correlation:
  FM density vs bearing
  deviation from true south.

**Step 4 — Rayleigh test
  on recovery bearings:**
  Test whether individual
  recovery bearings are
  uniformly distributed or
  cluster toward SW.
  Compare to primary analysis
  result (p=0.000517).

**Step 5 — Write results:**
  Monarch_doc_recovery_results.md

---

## THREAD 2 — ALTERNATIVE
## DATA SOURCES

**Status: Not yet needed.
Activate if Monarch Watch
does not respond.**

If Monarch Watch does not
provide usable data by
April 1, 2026, the following
alternative sources should
be contacted:

**Journey North:**
  journeynorth.org
  Citizen science monarch
  sighting database.
  Contains georeferenced
  sighting locations with dates.
  Can be used to reconstruct
  migration corridor patterns.
  Contact: via website form.

**WWF Mexico — Monarch
Butterfly Biosphere Reserve:**
  wwf.org.mx
  Winter roost location data
  at overwintering sites in
  Michoacán.
  Roost locations relative to
  predicted true-south corridor
  vs observed SW corridor.
  Contact: reserve management
  office.

**USGS Movebank:**
  movebank.org
  Check for any publicly
  available monarch GPS
  tracking datasets.
  Search: "Danaus plexippus"
  Filter: migration studies,
  North America.

**iNaturalist:**
  inaturalist.org
  Large georeferenced monarch
  observation database.
  Less precise than tagging
  data but high N.
  API access available.
  Can reconstruct migration
  front timing and position.

---

## THREAD 3 — FM INFRASTRUCTURE
## DENSITY MAP EXTENSION

**Status: Primary analysis
complete. Extension possible.**

### What Exists

The primary analysis used an
FM broadcast infrastructure
density score per geographic
region to test the false
attractor hypothesis.

### What Could Be Extended

**Higher resolution FM mapping:**
  The FCC database (fcc.gov/
  media/radio/fm-query) contains
  exact transmitter locations,
  power levels, and frequencies
  for all licensed FM stations
  in the United States.

  A higher-resolution FM density
  map — weighted by transmitter
  power, not just presence —
  would allow:
  - Per-county FM exposure
    estimates
  - Correlation with monarch
    count data at finer spatial
    resolution
  - Identification of specific
    high-power transmitter
    clusters that could act as
    false attractors

**This extension is not urgent.**
  The primary result is already
  significant. Extension would
  strengthen the analysis for
  publication but is not needed
  to proceed.

---

## THREAD 4 — SEASONAL
## VARIATION ANALYSIS

**Status: Not started.
Low priority until recovery
data arrives.**

### The Question

Does the false attractor effect
vary by season or migration
timing?

Early migrators (August-September)
vs late migrators (October-November)
may show different degrees of
deflection if:
  - FM broadcast patterns vary
    seasonally (unlikely)
  - Early migrators use different
    navigation cues (possible)
  - Early migrators travel
    different routes (documented)

This is a secondary analysis
that requires individual-level
bearing data (recovery data)
to address.

**Activate after recovery data
arrives.**

---

## CURRENT EVIDENCE STATE

```
Primary Rayleigh test:
  p = 0.000517
  Mean bearing: 218.9° SW
  Status: SIGNIFICANT ✅

NW permutation test:
  Significant
  Status: CONSISTENT ✅

False attractor identification:
  SW corridor consistent with
  high-density FM infrastructure
  Status: HYPOTHESIS SUPPORTED ✅

Recovery data analysis:
  Status: PENDING MONARCH
  WATCH RESPONSE ⏳

Individual bearing correlation
with FM density:
  Status: PENDING RECOVERY
  DATA ⏳

Alternative data sources:
  Status: ON HOLD — activate
  April 1 if no MW response ☐

FM density map extension:
  Status: NOT URGENT ☐

Seasonal variation analysis:
  Status: NOT STARTED —
  requires recovery data ☐
```

---

## HOW MONARCH FITS THE
## UNIFIED FRAMEWORK

The monarch vector tests the
EM coherence hypothesis in a
completely different species,
frequency range, and behavioral
system from the IMPC vector:

```
IMPC vector:
  Species: Mus musculus
  EM channel: ELF (50-60 Hz)
  Source: Power grid,
    building infrastructure
  Behavior: Thigmotaxis
    (spatial anxiety)

Monarch vector:
  Species: Danaus plexippus
  EM channel: RF (88-108 MHz)
  Source: FM broadcast
    transmitters
  Behavior: Migration bearing
    (long-distance navigation)
```

The two vectors are independent.
The monarch result does not
depend on the IMPC result.
The IMPC result does not depend
on the monarch result.

Both test the same theoretical
claim: biological navigation
and spatial cognition systems
are sensitive to EM field
coherence, and disruption of
that coherence — regardless
of frequency or species —
produces measurable behavioral
effects.

The monarch result is currently
the strongest single result in
the unified framework:
p = 0.000517 on the Rayleigh
test. This is not a trend.
This is a highly significant
clustering of migration bearings
toward the predicted false
attractor direction.

---

## DOCUMENTS TO WRITE NEXT

```
On Monarch Watch response:
  Monarch_doc_recovery_pre_
  analysis.md
    (ELF/FM scores BEFORE
    examining bearings —
    same pre-registration
    discipline as IMPC)

  Monarch_doc_recovery_results.md
    (after analysis runs)

On alternative data source
activation:
  Monarch_doc_altdata_pre_
  analysis.md

On FM density map extension:
  Monarch_doc_fm_extension.md
```

---

## CONTACTS

```
Monarch Watch:
  monarchwatch.org
  Request sent and acknowledged.
  Follow-up: March 14, 2026
  if no response.

Journey North (if needed):
  journeynorth.org
  Activate: April 1, 2026
  if Monarch Watch non-response.

WWF Mexico (if needed):
  wwf.org.mx
  Activate: April 1, 2026
  if Monarch Watch non-response.
```

---

## CRITICAL DISCIPLINE NOTE

When recovery data arrives —
from any source — the same
pre-registration discipline
applies as in the IMPC vector:

**FM density scores must be
assigned to tagging locations
BEFORE individual bearings
are examined.**

**The pre-analysis document
must be committed to the
repository with a timestamp
BEFORE the bearing data is
opened.**

This is not optional. The
entire evidentiary value of
the analysis depends on the
predictions preceding the
results. The monarch primary
result is already pre-registered.
The recovery data analysis
must follow the same standard.

---

## VERSION

- v1.0 — February 27, 2026
  Created after EUMODIC phase
  closure and full program
  review.
  Primary monarch result
  documented as significant.
  One active thread (Monarch
  Watch recovery data).
  Follow-up schedule set.
  Alternative data sources
  identified and staged.
  Pre-registration discipline
  note included — applies
  to all future monarch
  analyses without exception.
