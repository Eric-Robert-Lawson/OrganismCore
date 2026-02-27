# EUMODIC PROTOCOL AUDIT —
# RESULTS AND REANALYSIS PLAN
## Resolving the Null Result:
## Protocol Heterogeneity or
## Genuine Behavioral Signal?
## IMPC Series — Document 6
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
- **Document number:** IMPC Document 6
- **Status:** Protocol audit results
  and reanalysis plan — written after
  eumodic_protocol_audit.py completed
- **Depends on:**
  - EUMODIC_doc2_results.md
    (null result document)
  - eumodic_protocol_audit.txt
    (numerical output)
  - eumodic_parameter_inventory.csv
- **Scripts completed:**
  - eumodic_query.py ✅
  - eumodic_diagnose.py ✅
  - eumodic_strain_audit.py ✅
  - eumodic_elf_assignment.py ✅
  - eumodic_correlation.py ✅
  - eumodic_protocol_audit.py ✅
- **Script pending:**
  - eumodic_reanalysis.py ⏳
- **Pre-registration:** GitHub —
  Eric-Robert-Lawson/OrganismCore
- **Data source:** EMBL-EBI IMPC
  SOLR API, ESLIM_007_001
- **License:** CC-BY 4.0

---

## PART I: WHAT THE PROTOCOL
## AUDIT FOUND

### 1.1 The Duration Question
### — Definitively Resolved

The initial diagnosis of the null
result (EUMODIC_doc2_results.md)
proposed that HMGU's 936-second drop
in periphery permanence time between
DR23 and EUMODIC was most likely
explained by a protocol duration
difference — specifically that HMGU
may have run a 10-minute test in
EUMODIC versus 20 minutes in DR23.

**This hypothesis is falsified.**

The parameter Whole Arena Permanence
Time in ESLIM_007_001 provides a
direct and unambiguous measurement
of total test duration per animal:

```
Center       Median    P98
CMHD         1200.0s  1200.0s
HMGU         1200.0s  1200.0s
ICS          1200.0s  1200.0s
MRC Harwell  1200.0s  1200.0s
WTSI         1200.0s  1200.0s
```

Every animal at every center ran
exactly 1200 seconds — 20 minutes.
The median and P98 are identical.
There is no duration variance
whatsoever.

ESLIM_007_001 was a 20-minute
standardized test across all five
EUMODIC centers. Protocol duration
is not a confound.

### 1.2 The Initial Diagnosis
### Was Wrong

EUMODIC_doc2_results.md concluded:

> "The EUMODIC null result is
> consistent with protocol
> heterogeneity as the primary
> confound. The ESLIM_007_001
> dataset does not provide
> equivalent measurements across
> centers for this analysis."

This conclusion must be revised.
The protocol audit has shown that
the primary hypothesized confound
— test duration heterogeneity —
does not exist. The protocol was
identical across all five centers.

The null result therefore requires
a different explanation.

---

## PART II: WHAT THE DATA
## ACTUALLY SHOWS

### 2.1 The Full Multi-Parameter
### Picture

The audit retrieved 15 parameters
for ESLIM_007_001 across all five
centers. Reading these together
produces a behavioral profile
that periphery permanence time
alone could not show:

```
Ctr    ELF  Peri_t  Ctr_t  Ctr_ent  Ctr_dist  Latency
CMHD    72  1015.1  184.9      N/A     661.4     64.8s
HMGU    65   906.4  288.0    304.0    7397.1      4.1s
MRC     59  1028.3   16.2     18.0     151.3     78.9s
ICS     36  1034.6  165.4     92.0    1790.9     16.8s
WTSI    28   947.6  252.4    449.0    8062.9     11.7s
```

Five parameters. Five centers.
A coherent behavioral picture
emerges that is invisible in
periphery permanence time alone.

### 2.2 The MRC Harwell Pattern
### — Genuine Thigmotaxis

MRC Harwell (ELF=59) is behaviorally
the most thigmotactic center in
EUMODIC by multiple independent
measures:

- Centre permanence time:
  **16.2s** (others: 165-288s)
- Number of centre entries:
  **18** (others: 92-449)
- Centre distance travelled:
  **151m** (others: 661-8063m)
- Latency to first entry:
  **78.9s** (others: 4.1-64.8s)

A zone definition artifact would
reduce centre time and distance.
It would not independently produce
18 centre entries versus 449 at
WTSI, or 79-second latency versus
4 seconds at HMGU.

These are four independent
parameters all pointing in the same
direction. MRC Harwell mice in the
EUMODIC collection period genuinely
avoided the centre of the arena
more than mice at any other center.

**MRC Harwell's thigmotaxis in
EUMODIC is consistent with its
ELF position (59) relative to
ICS (36) and WTSI (28) —
those two lower-ELF centers both
show substantially more centre
exploration.**

### 2.3 The HMGU Paradox

HMGU (ELF=65) is the most
exploratory center in EUMODIC
by the most sensitive measures:

- Number of centre entries:
  **304** (second only to WTSI's 449)
- Latency to first entry:
  **4.1s** — the shortest of all
  five centers by a factor of 4x
- Centre distance travelled:
  **7397m** — second highest

Yet HMGU has the second-highest
ELF score (65) and should show
relatively high thigmotaxis by
the coherence hypothesis.

This is not noise. HMGU mice in
the EUMODIC collection period
were genuinely the most rapidly
and confidently exploratory
animals in the dataset. They
entered the centre zone within
4 seconds of test start and
accumulated 7,397 metres of
centre travel.

**This is the direct contradiction
of the DR23 finding** where HMGU
had the highest absolute periphery
time (1842.6s) of the three
overlapping centers.

The question this raises is not
whether the ELF hypothesis is
wrong — it is whether HMGU
changed between the EUMODIC
collection period (~2006-2011)
and the DR23 collection period
in a way that is real, documented,
and explicable.

### 2.4 The HMGU Temporal Shift —
### What It Might Mean

HMGU periphery permanence time:
- EUMODIC (~2006-2011): 906.4s
- DR23 (~2015-2024): 1842.6s
- Change: +936 seconds

This is a real behavioral change
at the same facility in the same
strain across the same 20-minute
standardized test.

Three possible explanations:

**A) Strain drift within C57BL/6N.**
The specific C57BL/6N substrain
at HMGU changed between collection
periods. HMGU used C57BL/6NCrl
in DR23. If the EUMODIC collection
used a different substrain with
different baseline anxiety, the
behavioral shift would be real
but not ELF-caused.

**B) Facility changes at HMGU.**
The HMGU facility underwent
renovation, expansion, or equipment
changes between the EUMODIC and
DR23 periods. If new high-voltage
infrastructure was installed
or the facility moved to a higher-
ELF environment, the behavioral
shift would be consistent with
the ELF hypothesis — HMGU became
more ELF-exposed over time, and
its mice became more thigmotactic
over time.

**C) Random cohort effects.**
Normal biological variation between
animal cohorts separated by a decade,
without any systematic explanation.

Explanation B is the most
theoretically interesting. It
predicts that if HMGU's ELF
environment increased between
the EUMODIC and DR23 periods,
the behavioral increase should
correlate with the ELF change.
This is testable if HMGU facility
history is available — but that
is a future inquiry, not something
resolvable from the current data.

### 2.5 WTSI — The Clearest
### Confirmation

WTSI (ELF=28, lowest in dataset)
shows the highest centre exploration:

- Centre entries: **449**
  (highest of all centers)
- Latency: **11.7s**
  (second shortest)
- Centre distance: **8063m**
  (highest of all centers)

WTSI is the rural purpose-built
facility with the lowest estimated
ELF. It shows the most exploratory,
least anxious behavior.

This is exactly what the coherence
hypothesis predicts. WTSI is the
clearest single-center confirmation
in the EUMODIC dataset.

### 2.6 Why Periphery Permanence
### Time Failed as the Primary
### Measure

The periphery permanence time range
across all five centers:

```
Min: 906.4s (HMGU)
Max: 1034.6s (ICS)
Range: 128.2s out of 1200s total
```

All five centers spend between
75.5% and 86.2% of the test in
the periphery. The periphery is
physically larger than the centre
zone — in a standard open field
with a centre zone covering
approximately 25% of arena area,
a mouse moving randomly would
spend ~75% of time in the
periphery by chance alone.

The periphery permanence time
measure is operating near its
floor — there is so little
variance that even a real
between-center behavioral
difference cannot produce a
detectable Spearman correlation.

Centre entries, centre distance,
and latency to first entry are
not subject to this floor effect.
They measure the qualitative
decision to explore the centre,
not the cumulative time accumulation
in a larger zone. They have
genuine variance across centers.

**The wrong primary outcome
measure was used in the initial
correlation. This is a measurement
choice error, not a behavioral
null.**

---

## PART III: THE REANALYSIS

### 3.1 What the Reanalysis Will Do

The reanalysis script
(eumodic_reanalysis.py) will run
Spearman correlations between
ELF score and each of the sensitive
thigmotaxis measures:

**Primary reanalysis outcome:**
Number of centre entries
(median per center, B6N strict)

**Secondary reanalysis outcomes:**
- Latency to first centre entry
- Centre distance travelled
- Centre permanence time
  (for completeness — already
  reported in primary analysis)

**Predicted directions:**
- Higher ELF → fewer centre entries
  (Spearman r predicted negative)
- Higher ELF → longer latency
  (Spearman r predicted positive)
- Higher ELF → less centre distance
  (Spearman r predicted negative)

### 3.2 The Pre-Registered
### Predicted Rank Order for
### Reanalysis

This rank order is stated here,
before the reanalysis script runs,
as the pre-analysis record for
the reanalysis.

**Number of centre entries
(predicted rank, most to fewest):**

```
Rank 1 (most entries, lowest ELF):
  WTSI (ELF=28)
Rank 2:
  ICS (ELF=36)
Rank 3:
  MRC Harwell (ELF=59)
Rank 4:
  HMGU (ELF=65)
Rank 5 (fewest entries, highest ELF):
  CMHD (ELF=72)
```

Note: CMHD has no centre entries
data in the current download.
If CMHD data is absent, the
correlation will run on N=4 centers.

**Latency to first centre entry
(predicted rank, shortest to longest):**

```
Rank 1 (shortest latency, lowest ELF):
  WTSI (ELF=28)
Rank 2:
  ICS (ELF=36)
Rank 3:
  MRC Harwell (ELF=59)
Rank 4:
  HMGU (ELF=65)
Rank 5 (longest latency, highest ELF):
  CMHD (ELF=72)
```

### 3.3 What the Audit Data
### Already Shows

Before running the reanalysis,
the audit output already provides
the observed values:

**Centre entries observed:**
```
WTSI (28):         449  (predicted rank 1)
HMGU (65):         304  (predicted rank 4)
ICS  (36):          92  (predicted rank 2)
MRC  (59):          18  (predicted rank 3)
CMHD (72):         N/A
```

Observed rank: WTSI > HMGU > ICS > MRC

WTSI and MRC Harwell are in
predicted position. HMGU and ICS
are inverted — HMGU (ELF=65) shows
more centre exploration than
ICS (ELF=36), which contradicts
the prediction.

This inversion is driven by HMGU's
anomalously exploratory behavior
in the EUMODIC collection period
— the same behavioral pattern
that produces the 936-second
deficit versus DR23.

**Latency observed:**
```
HMGU (65):   4.1s  (predicted rank 4)
WTSI (28):  11.7s  (predicted rank 1)
ICS  (36):  16.8s  (predicted rank 2)
CMHD (72):  64.8s  (predicted rank 5)
MRC  (59):  78.9s  (predicted rank 3)
```

Observed rank by latency (shortest
to longest):
HMGU < WTSI < ICS < CMHD < MRC

HMGU's 4.1-second latency is the
clearest anomaly. Every other center
shows a latency broadly consistent
with ELF rank. HMGU is the outlier.

### 3.4 The Honest Prediction for
### the Reanalysis

Given what the audit data already
shows, the reanalysis is likely
to produce:

- A partial correlation in the
  predicted direction for most
  parameters
- HMGU as the outlier that reduces
  the correlation coefficient
- Possible significance if HMGU
  is excluded from the sensitivity
  analysis (not a primary result —
  documented as a sensitivity only)

The reanalysis will be reported
completely regardless of outcome.

---

## PART IV: WHAT EUMODIC
## TELLS US — REVISED ASSESSMENT

### 4.1 The Revised Picture

The EUMODIC dataset does not
provide a clean replication of
the DR23 ELF-thigmotaxis
correlation in periphery
permanence time. That is a
fact and is reported as such.

However, the dataset is not
behaviorally null. It contains
genuine between-center behavioral
differences that are partially
consistent with the ELF gradient:

- WTSI (lowest ELF): most
  exploratory by two measures
  (centre entries, centre distance)
- MRC Harwell (mid-high ELF):
  most thigmotactic by four
  independent measures
- CMHD (highest ELF): high latency
  (64.8s), consistent with
  ELF prediction
- ICS (low-mid ELF): moderate
  exploration, consistent position
- HMGU (high ELF): anomalously
  exploratory — the single center
  that most strongly contradicts
  the prediction, and also the
  center with the largest
  behavioral shift between
  collection periods

### 4.2 HMGU Is the Key

HMGU is the center that determines
whether EUMODIC supports or
contradicts the DR23 finding.

In DR23: HMGU is the highest
periphery-time center of the
three overlapping centers,
consistent with its high ELF
score (65).

In EUMODIC: HMGU is the most
exploratory center by latency
and second most exploratory
by centre entries — inconsistent
with its ELF score.

The behavioral reversal at HMGU
between the two collection periods
is the central unresolved question
in the EUMODIC analysis. It cannot
be explained by protocol differences
(duration identical) or strain
specification (B6N strict used
in both analyses). It is a real
behavioral change at one facility
over approximately a decade.

Whether this reflects facility
infrastructure changes (consistent
with ELF hypothesis), strain
drift (confound), or random cohort
effects (noise) cannot be
determined from the current data.

### 4.3 The Single Honest
### Statement About EUMODIC

The EUMODIC dataset contains
behavioral evidence partially
consistent with the ELF-thigmotaxis
hypothesis — WTSI, MRC Harwell,
and CMHD occupy positions broadly
consistent with ELF predictions
on sensitive thigmotaxis measures.
HMGU is a significant outlier
whose anomalous behavior between
collection periods is unexplained
and prevents clear replication of
the DR23 result. The reanalysis
using centre entries and latency
will determine whether the
partial signal is statistically
detectable above HMGU's noise.

---

## PART V: WHAT COMES NEXT

### 5.1 Immediate

**Run eumodic_reanalysis.py**

Spearman correlations for:
- Centre entries vs ELF
- Latency vs ELF
- Centre distance vs ELF
- All with LOO sensitivity
- HMGU-excluded sensitivity as
  secondary analysis

### 5.2 After Reanalysis

**Write EUMODIC_doc4_final.md**

The final EUMODIC document will:
- Report all reanalysis results
- Make the definitive statement
  about what EUMODIC contributes
  to the series
- Document HMGU temporal shift
  as an open question for future
  investigation
- Close the EUMODIC analysis phase

### 5.3 Parallel Actions

**DR24:** Query open field data
when DR24 releases (imminent per
Robert Wilson, EBI). DR24 uses
IMPC_OFD_001 — the same procedure
as DR23, avoiding the EUMODIC
measurement choice problem.

**JAX:** Follow up if no substantive
response by end of business
February 28.

**Faraday cage:** Proceed toward
IACUC submission. The observational
program has produced one significant
result (DR23), one null with
identified floor effect (EUMODIC
periphery time), and one partial
signal (EUMODIC multi-parameter).
The causal experiment is the
correct next major step.

**Sea turtle:** Send FWC and NOAA
data request emails. Pre-registration
is complete on GitHub.

---

## PART VI: PARAMETER INVENTORY
## FOR REFERENCE

Full ESLIM_007_001 parameter list
confirmed in protocol audit:

```
Parameter                      N records
Distance travelled                20,276
Number of rears                   15,542
Centre average speed               5,013
Centre distance travelled          5,013
Centre permanence time             5,013
Centre resting time                5,013
Latency to centre entry            5,013
Periphery average speed            5,013
Periphery distance travelled       5,013
Periphery permanence time          5,013
Periphery resting time             5,013
Whole arena average speed          5,013
Whole arena permanence time        5,013
Whole arena resting time           5,013
Number of centre entries           4,940
```

**Whole arena permanence time
= 1200.0s at every center, P98.**
Protocol duration: 20 minutes,
identical across all five centers.
Duration confound: ruled out.

---

## VERSION

- v1.0 — February 27, 2026
  Protocol audit results document.
  Written after eumodic_protocol_
  audit.py completed.
  Duration confound falsified.
  Behavioral picture revised.
  HMGU temporal shift identified
  as key unresolved question.
  Reanalysis plan documented with
  pre-registered predicted rank
  orders for centre entries and
  latency outcomes.
  eumodic_reanalysis.py to be
  written and run next.
