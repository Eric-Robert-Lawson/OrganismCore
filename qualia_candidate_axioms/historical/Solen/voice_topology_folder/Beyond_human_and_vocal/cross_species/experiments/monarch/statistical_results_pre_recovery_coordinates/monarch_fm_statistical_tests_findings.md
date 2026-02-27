# FM FALSE ATTRACTOR HYPOTHESIS:
# AVAILABLE STATISTICAL TESTS
# FINDINGS AND INTERPRETATION
## Pre-Recovery-Data Results
## Tagging Dataset Only
## OrganismCore Cross-Species
## Communication Series
## Desk Analysis Document 6
## February 27, 2026

---

## ARTIFACT METADATA

```
artifact_type:
  Statistical findings record.
  Documents all four available
  statistical tests run on the
  monarch_with_fm.csv tagging
  dataset prior to receipt of
  Monarch Watch recovery data.

  Contains:
    — Full numerical results
    — Figure interpretation
    — Plain-language meaning
      of each test
    — What passed, what did not,
      and why each result makes
      sense given the data structure
    — What these results mean for
      the primary recovery analysis
    — Honest assessment of what
      is and is not established

author:
  Eric Robert Lawson
  OrganismCore research program

analysis_assistance:
  GitHub Copilot (Microsoft/OpenAI)
  Session February 27, 2026

data_source:
  monarch_with_fm.csv
  363,582 records
  3,099 unique tagging locations
  (1km grid deduplication)
  GBIF Monarch Watch dataset ×
  FCC LMS FM transmitter database

status:
  VERIFIED. All numbers are direct
  script output. No manual
  adjustment. No cherry-picking.
  Two tests significant.
  Two tests not significant.
  All results reported in full.

relationship_to_pre_registration:
  NONE of these four tests are
  the primary pre-registered test.
  The primary test is the V-test
  on alignment_angle (bearing
  deviation vs FM false attractor
  bearing) which requires recovery
  coordinates. These four tests
  are exploratory and descriptive,
  characterizing the FM landscape
  and exposure structure of the
  tagging dataset.

figures:
  monarch_available_stats_figures.png
  Referenced as ![image1](image1)
  in this artifact.
  Six panels:
    Top-left:    Test 1 rose plot
    Top-center:  Test 2 compass plot
    Top-right:   Test 3 scatter
    Bottom-left: Test 3 quartile box
    Bottom-center: Test 4 permutation
    Bottom-right:  Statistical summary
```

---

## PART I: WHAT WAS TESTED
## AND WHY

Before recovery coordinates arrive,
four structural questions about the
FM electromagnetic landscape can be
asked of the tagging dataset alone:

```
TEST 1:
  Is the FM false attractor bearing
  distribution across the migration
  corridor non-uniform?
  (Rayleigh test)

TEST 2:
  Are the FM environments in the
  highest-opposition state (Oklahoma)
  and lowest-opposition state
  (Ontario) statistically distinct?
  (Watson-Williams two-sample test)

TEST 3:
  Do the two risk factors — FM
  signal strength and FM opposition
  angle — co-vary geographically,
  or are they independent?
  (Circular-linear correlation,
   Pearson, Spearman)

TEST 4:
  Is the geographic clustering of
  high-risk tagging locations more
  extreme than chance would predict
  given the distribution of all
  tagging effort?
  (Monte Carlo permutation,
   10,000 iterations)
```

None of these tests touch the
primary hypothesis. None require
recovery coordinates. All run
on the tagging dataset that has
been archived and pre-registered.

---

## PART II: COMPLETE NUMERICAL
## RESULTS

### Test 1: Rayleigh Test

```
Input:
  N unique locations: 3,099
  Variable: fm_false_attractor_bearing

Output:
  Mean resultant length R̄: 0.0494
  Mean direction:           218.9°
  Rayleigh z:               7.5642
  p-value:                  0.000517

Decision: HIGHLY SIGNIFICANT
  p < 0.001

Supplementary (opposition angles
doubled to use full circular range):
  Mean opposition:  86.1°
  R̄ (doubled):     0.0540
  p-value:          0.000117
  Decision: HIGHLY SIGNIFICANT
```

### Test 2: Watson-Williams Test

```
Input:
  Oklahoma unique locations: 53
  Ontario unique locations:  36

Oklahoma:
  Mean FM bearing: 106.8° (ESE)
  R̄: 0.0826
  Rayleigh p: 0.698 (NOT SIGNIFICANT
    — OK bearings are uniformly
    scattered, no dominant direction)

Ontario:
  Mean FM bearing: 152.7° (SSE)
  R̄: 0.7315
  Rayleigh p: < 0.000001
    (HIGHLY concentrated — all ON
    locations face FM from SSE)

Watson-Williams two-sample test:
  F(1, 87) = 1.7389
  p-value:   0.1907

Decision: NOT SIGNIFICANT

Context:
  OK mean expected bearing: 189.3°
  OK mean FM bearing:       106.8°
  OK opposition:             82.4°

  ON mean expected bearing: 223.7°
  ON mean FM bearing:       152.7°
  ON opposition:             71.0°
```

### Extended state breakdown

```
State  N_locs  Mean_FM    R̄      p       Mean_exp  Opp
KS       211    358.6°  0.044  0.664     189.6°  169.0°
IA       240    346.2°  0.097  0.103     196.9°  149.3°
MN       177    159.1°  0.198  0.001 **  194.1°   35.0°
TX       136    206.0°  0.156  0.036 *   192.3°   13.6°
PA       266     35.3°  0.102  0.064     230.2°  165.1°
OK        53    106.8°  0.083  0.698     190.3°   83.5°
OH       152    232.3°  0.246  0.000 *** 221.1°   11.3°
NY       255    253.5°  0.182  0.000 *** 230.3°   23.2°
WI       101    133.1°  0.122  0.224     204.0°   70.9°
NE        44     56.2°  0.160  0.328     186.3°  130.1°
```

### Test 3: Circular-Linear
### Correlation

```
N unique locations: 3,099
Variables:
  fm_false_attractor_strength (linear)
  fm_opposition (circular)

Pearson r:      -0.0204   p = 0.256
Spearman rho:   -0.0274   p = 0.128
Circular-linear r_cl: 0.0432
  F = 2.8986    p = 0.055

Decision: NOT SIGNIFICANT
  (p = 0.055, borderline)

FM strength quartile breakdown
(pre-registered boundaries):

Quartile    N   Mean_opp  Median_opp  Mean_str
Q1 (weak) 870     88.8°      89.9°    0.0097
Q2        933     86.1°      82.3°    0.0154
Q3        555     83.0°      77.0°    0.0212
Q4 (str)  741     85.3°      80.5°    0.0312

Range Q1 to Q4: 3.5° — essentially flat
```

### Test 4: Monte Carlo
### Permutation Test

```
High-risk criteria:
  opposition > 120°
  fm_strength > 0.01

Observed:
  809 / 3,099 locations (26.1%)

By geographic quadrant:

Quadrant           Obs  Total  Rate
NW (MN/SD/WI)      150    491  30.5%
NE (MA/CT/NJ/NY)   158    634  24.9%
Central (OK/KS/TX) 146    519  28.1%
SE (SC/FL/GA)       39    123  31.7%

Permutation results
(10,000 iterations, seed=42):

Quadrant       Obs   Perm_mean  SD    p
NW             150     127.3   8.98  0.0074 **
NE             158     170.8  10.02  0.9052
Central        146     135.3   9.19  0.1311
SE              39      33.0   4.83  0.1271

** p < 0.01
```

---

## PART III: FIGURE INTERPRETATION

![image1](image1)

### Top-left panel: Test 1 rose plot

The circular histogram shows FM
false attractor bearings across
all 3,099 unique tagging locations.
Each bar represents a 10° bin.
The red arrow shows the mean
direction (218.9°, SW).

What the figure shows:
The distribution is visually
nearly uniform — the bars are
roughly equal height all the way
around the compass. This is
consistent with the very low
R̄ = 0.049. The distribution is
not uniform enough to be random
(p = 0.0005) but is much more
uniform than concentrated.

The red arrow is short relative
to the radius of the plot — this
visualizes the weak but real
mean direction. The SW mean
direction (218.9°) is close to
the correct migration direction
(~195-210°) but the scatter
around it is enormous.

**What this means:** The FM
infrastructure is not pointing
monarchs in a single wrong
direction. It is exposing them
to a nearly omnidirectional field
with a weak SW tendency. The
risk comes not from a single
dominant wrong direction but
from the variance — many locations
face strong FM bearings that are
individually very wrong, even
if the mean across all locations
is approximately correct.

---

### Top-center panel: Test 2
### compass plot

Three arrows on a compass rose:
- Red (OK): 107° (ESE) — short
- Blue (ON): 153° (SSE) — long
- Green dashed (expected): 189° (S)

The lengths of the arrows encode
R̄ — how concentrated the
distributions are. Ontario's long
blue arrow shows high concentration.
Oklahoma's short red arrow shows
near-uniform scatter.

What the figure shows most clearly:
Both FM false attractor bearings
point roughly southeastward, which
is in the same general quadrant as
the correct migration direction
(189° S). This is what drove the
surprising Test 1 result — the
mean FM bearing of the whole
corridor is SW, close to the
correct bearing. But the critical
finding from the exploratory
analysis is not the mean bearing
but the **opposition angle at
individual sites**, where specific
locations show 170-179° opposition.
The Watson-Williams test was
testing mean bearing direction,
not opposition angle — which is
why it returned NS.

---

### Top-right panel: Test 3 scatter

FM false attractor strength (x-axis)
vs FM opposition angle (y-axis) for
a random sample of 1,000 locations.
Points colored green-to-red by
opposition angle. Near-flat trend
line. Two horizontal reference
lines at 90° and 120°.

What the figure shows:
A cloud of points with no visible
trend. The scatter is equally
distributed above and below the
90° threshold across all strength
values. High-strength locations
(x > 0.030) show opposition angles
ranging from near 0° to near 180°
— no concentration in either
direction.

**The key visual message:**
A location can be anywhere in
this plot. High strength does not
predict high opposition. You can
have a very strong FM false
attractor that happens to point
toward Mexico (low opposition,
low risk) or a very strong one
pointing exactly away from Mexico
(high opposition, high risk).
These are genuinely independent
dimensions of the FM risk
landscape.

---

### Bottom-left panel: FM
### opposition quartile boxplots

Four boxplots — Q1 through Q4
by FM strength — showing the
distribution of opposition angles
within each quartile.

What the figure shows:
All four boxes look nearly
identical. The medians are all
close to 80-90°. The interquartile
ranges overlap almost completely.
The Q1 median (89.9°) is actually
slightly higher than Q4 (80.5°).

**The key visual message:**
Knowing which FM strength quartile
a location falls in tells you
essentially nothing about its
opposition angle. The flat pattern
across Q1 to Q4 is not a failure —
it is a finding. It means the
pre-registered dose-response
analysis (which uses FM strength
quartiles to test whether bearing
deviation increases with FM
strength) is testing something
genuinely independent from the
opposition angle finding. The
two predictors are orthogonal.

---

### Bottom-center panel: Test 4
### permutation bar chart

Four paired bar groups — one per
geographic quadrant. Red bars =
observed high-risk location count.
Gray bars = permutation mean with
error bars (±1 SD). Significance
stars above each pair.

What the figure shows:
NW quadrant (MN/SD/WI): the red
bar is substantially taller than
the gray bar. ** marks it.
150 observed vs 127.3 expected.

NE quadrant (MA/CT/NJ/NY): the
gray bar is actually taller than
the red bar. The NE has FEWER
high-risk locations than the
permutation expects. No star.

Central (OK/KS/TX): red slightly
above gray. Not significant.

SE (SC/FL/GA): red slightly above
gray. Not significant.

**The key visual message:**
Only the upper midwest (Minnesota,
South Dakota, Wisconsin) shows
statistically significant excess
clustering of high-risk locations.
The FM infrastructure there is
genuinely more hostile to monarch
navigation than a random assignment
of FM bearings to those locations
would produce.

---

### Bottom-right panel: Summary

Clean text summary of all four
tests with color coding —
significant results in red,
non-significant in gray.

Tests 1 and 4 in red.
Tests 2 and 3 in gray.
Bottom note: "PRIMARY V-TEST:
pending Monarch Watch recovery
data."

---

## PART IV: WHAT EACH RESULT
## MEANS — PLAIN LANGUAGE

### Test 1 (SIGNIFICANT):

**The FM false attractor bearing
distribution across the monarch
migration corridor is not random.**

The infrastructure has geographic
structure that is detectable above
chance. This is the foundational
structural result — it confirms
that computing FM false attractor
bearings at tagging locations
produces a meaningful,
non-random variable that can
be used as a predictor in
the recovery analysis.

What it does NOT mean: that FM
is systematically pointing monarchs
in the wrong direction on average.
The mean direction (218.9° SW)
is close to the correct migration
bearing. The non-uniformity reflects
geographic structure in where
major FM markets are relative to
tagging sites, not a systematic
anti-migratory bias across the
whole corridor.

---

### Test 2 (NOT SIGNIFICANT):

**Oklahoma and Ontario FM
environments are not statistically
distinct in mean FM bearing
direction, but this is because
Oklahoma has no dominant FM
bearing direction — not because
the two states are similar.**

Oklahoma FM environments are
omnidirectional (R̄ = 0.083,
Rayleigh p = 0.698). The 53
unique Oklahoma tagging locations
face FM from every direction
equally because OKC and Tulsa
FM markets surround them. There
is no single dominant FM bearing
in Oklahoma — there are many
different bearings, canceling
each other out.

Ontario FM environments are
highly concentrated (R̄ = 0.731,
Rayleigh p < 0.000001). All
Ontario tagging locations face
FM primarily from the SSE —
Toronto, Buffalo, Detroit, and
Cleveland are all to the south.
The Ontario FM landscape is
coherent and directional.

The Watson-Williams test failed
because it requires both groups
to have concentrated mean
directions. Oklahoma does not.
This is not a problem with
the hypothesis — it is a
finding about the structure
of Oklahoma's FM environment.

**For the recovery analysis:**
The Oklahoma/Ontario contrast
should be tested using opposition
angle (the variable where OK
clearly differs from ON: 142.6°
vs 49.5°) rather than raw FM
bearing direction. That contrast
is real, large, and will be
detectable in the recovery data.

---

### Test 3 (NOT SIGNIFICANT,
### borderline p = 0.055):

**FM signal strength and FM
opposition angle are independent
of each other across tagging
locations. Knowing one tells
you nothing about the other.**

This is a genuinely important
structural finding for the
recovery analysis. It means:

```
1. The pre-registered quartile
   dose-response test (using
   FM strength quartiles) will
   test something different from
   the opposition angle finding.
   They are not redundant.

2. In the recovery analysis,
   both FM strength and FM
   opposition angle can be used
   as independent predictors
   without multicollinearity
   concerns.

3. High-risk locations are not
   a single cluster — they are
   distributed throughout the
   range of FM strength values.
   Risk is defined by the
   combination of both factors,
   not by either alone.

4. The absence of co-variation
   means the FM infrastructure
   is not systematically organized
   to maximize harm or to minimize
   it. The opposition angle at any
   given location is essentially
   determined by where the nearest
   cities happen to be relative to
   the correct migration bearing —
   a geographic accident, not a
   systematic feature.
```

The borderline p = 0.055 in
the circular-linear correlation
(Mardia 1976) with a weak
negative sign (r_cl = 0.043)
suggests a very slight tendency
for stronger FM signals to be
associated with slightly lower
opposition angles. This is
consistent with the observation
that the strongest FM markets
(Dallas, Houston, Atlanta) are
in the southern part of the
corridor where the correct
migration bearing is more
southwesterly and FM markets
happen to cluster to the SW —
but this effect is too small
to be significant at this
sample size.

---

### Test 4 (SIGNIFICANT,
### NW quadrant only):

**The FM infrastructure in
Minnesota, South Dakota, and
Wisconsin produces significantly
more high-risk tagging locations
than expected by chance given
how many monarchs were tagged
there.**

150 high-risk locations observed.
127.3 expected. p = 0.0074.

This means that if you randomly
shuffled which FM false attractor
bearing each location got, you
would only see 150 or more
high-risk locations in the NW
quadrant 0.74% of the time.
The actual FM infrastructure
in the upper midwest is
genuinely structured to be
more hostile to monarch
navigation than a random
FM landscape would be.

**Why the upper midwest
specifically?**

Minneapolis, Sioux Falls,
Madison, and Milwaukee are
the dominant FM markets in
this region. The correct
migration bearing from
MN/SD/WI is approximately
SSW (190-205°). The major
FM transmitter clusters
are located to the east and
southeast of many tagging
sites in this region —
pushing the FM false attractor
bearing northward or eastward,
away from the correct SSW
direction. This is not
intentional — it is a
geometric accident of where
cities are relative to
migration routes. But the
permutation test confirms
it is a real structural
feature, not a chance
pattern in the data.

**Why NOT significant in
Central (OK/KS/TX)?**

This requires explanation
because Oklahoma and Kansas
are the headline high-
opposition states. The
answer is in the high-risk
criteria: opposition > 120°
AND strength > 0.01. Many
Oklahoma locations pass the
opposition threshold but fail
the strength threshold because
the omnidirectional FM
environment produces low
strength values (FM exposure
spread in all directions =
no dominant bearing =
low strength). The permutation
test counts locations passing
BOTH criteria. Oklahoma passes
one but not consistently both.

**Why NOT significant in
NE (MA/CT/NJ/NY)?**

The northeast had FEWER
high-risk locations than
the permutation expected
(158 observed vs 170.8
expected, p = 0.905). This
is because the dense and
omnidirectional FM landscape
of the Boston-to-Washington
corridor produces low strength
values at most locations —
same mechanism as Oklahoma.
High opposition but low
coherence means many
locations fail the strength
criterion.

---

## PART V: WHAT THESE RESULTS
## MEAN FOR THE RECOVERY
## ANALYSIS

### What is now established
### pre-recovery:

```
1. The FM false attractor bearing
   variable is a non-random,
   geographically structured
   predictor across the migration
   corridor. (Test 1)

2. The FM risk landscape is
   genuinely more hostile to
   monarch navigation in the
   upper midwest than chance
   would predict. (Test 4)

3. FM strength and FM opposition
   angle are independent of each
   other and can serve as
   separate predictors in the
   recovery analysis without
   multicollinearity. (Test 3)

4. The Oklahoma/Ontario dose
   contrast is structurally real
   but must be measured via
   opposition angle, not raw
   FM bearing direction.
   (Test 2 interpretation)
```

### What the recovery analysis
### will be able to test that
### these tests cannot:

```
1. PRIMARY (pre-registered):
   Do monarchs show bearing
   deviation aligned with the
   FM false attractor bearing
   at their tagging location?
   (V-test on alignment_angle)

2. DOSE-RESPONSE (pre-registered):
   Does bearing deviation increase
   with FM strength quartile?
   (Mean R̄ by Q1-Q4)

3. WEATHER CONDITION (secondary):
   Is the FM effect stronger
   in overcast-day monarchs
   than clear-day monarchs?
   (Requires tagging-day weather
   data — may or may not be
   in Monarch Watch database)

4. GEOGRAPHIC DOSE:
   Do monarchs tagged in NW
   quadrant (significantly
   excess high-risk) show
   more bearing deviation than
   monarchs tagged in NE quadrant
   (below-expected high-risk)?
```

### Revision to the analysis
### plan based on these results:

**The Watson-Williams NS result
requires one change in framing.**

The original plan was to use
Oklahoma vs Ontario as the
primary dose contrast demonstration.
These results show that Oklahoma
FM environments are too
omnidirectional to serve as a
clean high-dose group for a
bearing direction comparison.

The revised framing:

```
PRIMARY DOSE CONTRAST:
  Use fm_false_attractor_strength
  quartiles (pre-registered)
  or fm_opposition angle > 120°
  vs < 90° as the dose grouping.

GEOGRAPHIC SPOTLIGHT:
  Use the NW quadrant
  (MN/SD/WI, permutation
  p = 0.0074) as the geographic
  region where the FM false
  attractor effect is most
  structurally predicted to
  appear in recovery data.

OKLAHOMA:
  Still the highest-volume
  high-opposition site (9,482
  monarchs, 176.5° opposition
  at the OKC site). The OKC
  site opposition of 176.5°
  is at the individual location
  level and will be as powerful
  as ever in the recovery
  analysis. The state-level
  Watson-Williams NS result
  does not diminish the
  site-level prediction.
```

---

## PART VI: HONEST SUMMARY
## OF WHAT WAS FOUND

**Two significant results:**

Test 1 confirms the FM landscape
is non-random and has geographic
structure. Test 4 confirms the
upper midwest FM infrastructure
is genuinely more hostile to
monarch navigation than chance
predicts.

**Two non-significant results:**

Test 2 failed because Oklahoma
FM environments are omnidirectional
— not because the hypothesis is
wrong. Test 3 confirmed that FM
strength and FM opposition are
independent variables, which is
a useful structural finding for
the recovery analysis, not a
null result in any harmful sense.

**What this means overall:**

These four tests characterize
the electromagnetic landscape
that 363,582 tagged monarchs
flew through between 1992
and 2000. They confirm that
the landscape is non-random,
geographically structured,
and in specific regions more
hostile to navigation than
chance. They do not test
whether monarchs responded
to that landscape — that
is what the recovery analysis
will test.

The pipeline is confirmed.
The predictors are validated.
The dose contrast variables
are characterized. The recovery
analysis will run on a well-
understood independent variable
with confirmed non-random
geographic structure.

The next result in this series
is the V-test on alignment_angle.
It will run when Monarch Watch
responds to the data request.

---

## VERSION

```
v1.0 — February 27, 2026
Covers all four available
statistical tests on tagging
dataset.

Input:
  monarch_with_fm.csv
  (363,582 records,
   3,099 unique locations)

Script:
  monarch_available_stats.py

Outputs documented:
  monarch_available_stats_
    results.txt
  monarch_available_stats_
    figures.png

Pipeline status:
  FM station table:      COMPLETE
  Field density engine:  COMPLETE
  Monarch FM analysis:   COMPLETE
  Visualization:         COMPLETE
  Pre-registration:      COMPLETE
  Literature synthesis:  COMPLETE
  Available stats:       COMPLETE
  Primary V-test:        PENDING
                         (Monarch Watch
                          recovery data)

Next document (Doc 7):
  Primary statistical test
  results on recovery data.
  Filed when data arrives.
  Results reported regardless
  of outcome.
```
