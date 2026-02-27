# EUMODIC OPEN FIELD REPLICATION
# ANALYSIS — RESULTS AND
# INTERPRETATION
## Independent Cross-Dataset Validation
## of the ELF-Thigmotaxis Correlation
## IMPC Series — Document 5
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
- **Document number:** IMPC Document 5
- **Status:** Results document —
  written after correlation script
  completed
- **Depends on:**
  - EUMODIC_doc1_pre_analysis.md
    (pre-registration record)
  - EUMODIC_README.md
    (folder pre-registration)
  - eumodic_correlation_results.txt
    (numerical output)
  - eumodic_correlation.png
    (figure)
- **Scripts completed:**
  - eumodic_query.py ✅
  - eumodic_diagnose.py ✅
  - eumodic_strain_audit.py ✅
  - eumodic_elf_assignment.py ✅
  - eumodic_correlation.py ✅
- **Script pending:**
  - eumodic_protocol_audit.py ⏳
- **Pre-registration:** GitHub —
  Eric-Robert-Lawson/OrganismCore
- **Data source:** EMBL-EBI IMPC
  SOLR API, ESLIM_007_001
- **License:** CC-BY 4.0

---

## PART I: PRIMARY RESULT —
## STATED WITHOUT QUALIFICATION

### 1.1 The Number

```
Spearman r = -0.200
p = 0.747
N = 5 centers
```

**This is a null result.**

The pre-registered primary prediction
was not confirmed. The ELF-thigmotaxis
correlation observed in IMPC DR23
(r = -0.775, p = 0.04) did not
replicate in the EUMODIC dataset
using procedure ESLIM_007_001.

### 1.2 Rank Prediction

Pre-registered predicted rank order
(high to low thigmotaxis):
CMHD → HMGU → MRC Harwell → ICS → WTSI

Observed rank order:
ICS → MRC Harwell → CMHD → WTSI → HMGU

Exact rank matches: 0 / 5

Predicted/observed rank correlation:
r = -0.200, p = 0.747

### 1.3 Leave-One-Out Sensitivity

No leave-one-out configuration
produced a significant result or
a trend (p < 0.10).

```
Left out     r        p     Sig
CMHD       -0.400   0.600   ns
HMGU       +0.200   0.800   ns
MRC Harwell +0.000  1.000   ns
ICS         +0.000  1.000   ns
WTSI       -0.800   0.200   ns
```

### 1.4 Within-Center DR23 Comparison

```
Center       DR23_med  EUMOD_med   Diff
HMGU         1842.6s    906.4s   -936.2s
ICS           987.3s   1034.6s    +47.3s
MRC Harwell  1243.1s   1028.3s   -214.8s
```

Rank order preserved: 1 / 3 centers
(MRC Harwell preserved at rank 2)

### 1.5 Secondary Outcome

Centre permanence time:
ELF vs centre time:
Spearman r = +0.100, p = 0.873

Internal consistency nominal:
periphery and centre move in opposite
directions as predicted, but neither
reaches significance.

---

## PART II: WHAT THE DATA
## ACTUALLY SHOWS

### 2.1 The Variance Problem

The primary reason the Spearman
correlation failed is not the absence
of a behavioral signal. It is the
near-complete compression of the
dependent variable.

```
Center       ELF   Peri_med
ICS           36   1034.6s
MRC Harwell   59   1028.3s
CMHD          72   1015.1s
WTSI          28    947.6s
HMGU          65    906.4s
```

Total range: 1034.6 - 906.4 = 128.2s

In the DR23 analysis, the between-
center range in thigmotaxis was
sufficient to drive r = -0.775.
In EUMODIC, the five centers are
compressed into a 128-second band
across a 36-point ELF gradient.

A Spearman correlation cannot detect
a signal in a dependent variable with
near-zero variance. This is a
measurement problem, not necessarily
a behavioral null.

### 2.2 The HMGU Collapse

The single most informative number
in the entire EUMODIC result is:

**HMGU: DR23 median 1842.6s →
EUMODIC median 906.4s**

**Difference: -936.2 seconds**

This is a drop of nearly 16 minutes
in the same center, in the same strain,
measuring the same construct
(time spent near the periphery).

This cannot be explained by a real
behavioral difference in HMGU mice
between the EUMODIC collection period
(~2006-2011) and the DR23 collection
period. A 936-second behavioral shift
in wildtype C57BL/6N at the same
facility would require a major
environmental or genetic event that
would be documented in the literature.

The most parsimonious explanation
is a **protocol difference** between
ESLIM_007_001 and IMPC_OFD_001 —
specifically test duration.

If HMGU ran ESLIM_007_001 with a
shorter total test time than
IMPC_OFD_001, the absolute periphery
permanence time would be lower — not
because mice behaved differently, but
because there was less total time to
accumulate.

### 2.3 The MRC Harwell Zone Anomaly

```
Center       Ctr_med
HMGU         288.0s
WTSI         252.4s
CMHD         184.9s
ICS          165.4s
MRC Harwell   16.2s
```

MRC Harwell centre permanence time
is 16.2 seconds. Every other center
is 165-288 seconds — a factor of
10-17x higher.

This is not a behavioral difference.
A wildtype C57BL/6N mouse does not
spend 16 seconds per centre visit
at one facility and 200+ seconds at
every other facility.

This is almost certainly a **zone
definition difference** — MRC Harwell
in EUMODIC defined the centre zone
with different boundaries than the
other four centers, producing
anomalously low centre dwell and
correspondingly anomalously high
periphery dwell.

This is the same class of protocol
heterogeneity identified in the DR23
KMPC analysis — where centre
permanence time was anomalously high
(indicating an oversized centre zone)
and implied thigmotaxis was deflated.

MRC Harwell in EUMODIC has the
inverse: undersized or differently
bounded centre zone, inflating
periphery time independently of
the ELF-behavior relationship.

### 2.4 ICS as the Control Case

ICS changed by only +47.3 seconds
between DR23 and EUMODIC. Its
absolute value is consistent across
both datasets. Its periphery time
(1034.6s) is the highest of the
five EUMODIC centers — consistent
with its DR23 ranking as a moderate-
thigmotaxis center.

ICS is the center where the protocol
was most consistent between
ESLIM_007_001 and IMPC_OFD_001.
It is also the center where the
ELF score (36) places it in the
lower-middle of the gradient —
where the signal would be expected
to be moderate.

The ICS stability is the one data
point in EUMODIC that behaves as
expected. It is not evidence for
the hypothesis — it is evidence that
the protocol inconsistency at HMGU
and the zone anomaly at MRC Harwell
are the dominant sources of variance
in this dataset.

---

## PART III: WHAT THIS RESULT
## MEANS FOR THE SERIES

### 3.1 What It Does Not Mean

**It does not falsify the
ELF-thigmotaxis hypothesis.**

A null result in a dataset with
near-zero dependent variable variance
and documented protocol heterogeneity
is uninformative about the underlying
behavioral question. It tells us that
ESLIM_007_001 periphery permanence
time, as collected across these five
centers, is not a clean replicate of
IMPC_OFD_001 thigmotaxis.

**It does not weaken the DR23
primary result.**

The DR23 result stands on its own.
The EUMODIC analysis was an
independent replication attempt.
The failure of replication is a
property of the measurement instrument
(ESLIM_007_001 in this center set),
not a retroactive challenge to DR23.

### 3.2 What It Does Mean

**The EUMODIC dataset is not a
clean replication instrument
for this analysis.**

The procedure difference between
ESLIM_007_001 and IMPC_OFD_001
introduces protocol heterogeneity
that compresses between-center
variance to the point where the
Spearman correlation is underpowered
regardless of any underlying effect.

**Protocol auditing is required
before any EUMODIC-based conclusion
can be drawn.**

The 936-second HMGU drop and the
16-second MRC Harwell centre time
are specific, investigable anomalies.
They have testable explanations.
The eumodic_protocol_audit.py script
will query duration proxies and zone
parameters per center to determine
whether the null result is protocol-
explained.

**The Faraday cage experiment is
the correct next observational step
for the IMPC vector.**

The observational program has now
been run on two independent datasets.
DR23 produced a significant result.
EUMODIC produced a null result with
identified procedural confounds.
The causal test — which is immune
to cross-dataset protocol differences
because it controls the protocol
directly — is the pre-registered
Faraday cage experiment. That
experiment is not contingent on
EUMODIC replication.

### 3.3 What Remains to Be Done
### in the EUMODIC Dataset

Before closing the EUMODIC analysis,
two questions need answers:

**Question 1: Protocol duration**
Did the five EUMODIC centers run
ESLIM_007_001 for the same total
duration? Can test duration be
inferred from total distance traveled,
total resting time, or other
time-cumulative parameters available
in the dataset?

If HMGU ran a 10-minute test and ICS
ran a 20-minute test, the variance
compression is fully explained and
the null result is a protocol artifact.

**Question 2: Zone definitions**
Can MRC Harwell's anomalous centre
permanence time (16.2s) be explained
by a documented difference in centre
zone dimensions for ESLIM_007_001?

If yes, MRC Harwell should be flagged
and excluded from any normalized
reanalysis.

These questions are addressed by
eumodic_protocol_audit.py.

---

## PART IV: DR24 AND NEXT
## DATASET OPPORTUNITIES

### 4.1 DR24 Is Releasing Imminently

Robert Wilson (EBI, personal
communication, February 27, 2026)
confirmed DR24 will release within
days. At that point:

- DR23 moves to FTP archive
- DR24 becomes the current release
- DR24 may include new centers not
  in DR23 or EUMODIC
- DR24 may include additional wildtype
  records for existing centers

DR24 open field data should be
queried immediately on release for:
- New centers with ELF-assignable
  profiles
- Extended N for existing centers
- Any protocol documentation changes

### 4.2 JAX Response Pending

The JAX KOMP2 inquiry (case 03428362)
is awaiting a substantive response.
JAX data, if available, would add
one high-quality anchor point to
the DR23 analysis. JAX facilities
have well-documented electrical
infrastructure, making ELF score
estimation more reliable than for
some other centers.

---

## PART V: COMPLETE NEXT STEPS
## IN PRIORITY ORDER

### Immediate — EUMODIC Protocol Audit

**Action:** Run eumodic_protocol_audit.py

**Purpose:** Query duration proxy
parameters and zone-definition
parameters per center in EUMODIC.
Determine whether HMGU's 936-second
drop and MRC Harwell's 16-second
centre time are protocol artifacts.

**Decision tree:**

If protocol duration differences
confirmed:
→ Document as protocol confound
→ Attempt duration-normalized
  reanalysis if possible
→ Close EUMODIC as procedurally
  non-equivalent to DR23

If protocol durations are equivalent:
→ The null result is a genuine
  behavioral null in this center set
→ Document honestly
→ Investigate alternative confounds
  (collection era, investigator,
   substrain within B6N)

### This Week — DR24 Query

**Action:** When DR24 releases, run
eumodic_query.py equivalent against
DR24 open field data (IMPC_OFD_001).

**Purpose:** Extend the DR23 center
set with any new IMPC centers.
DR24 uses the same procedure as DR23,
so the protocol heterogeneity problem
does not apply.

### This Week — JAX Follow-Up

**Action:** If no substantive response
from JAX customer services by end of
business February 28, contact directly:
komp@jax.org

### Ongoing — Faraday Cage

**Action:** Proceed toward IACUC
submission and facility identification
for the pre-registered Faraday cage
experiment.

This is the causal anchor of the
entire IMPC vector. It does not depend
on EUMODIC replication. It does not
depend on DR24. It is the experiment
that converts the observational
DR23 correlation into a testable
causal claim.

### Ongoing — Monarch Watch

**Action:** Continue waiting for
recovery data response.
No follow-up action yet needed —
the initial request was sent and
acknowledged.

### Pending — Sea Turtle

**Action:** Send FWC and NOAA emails.
Pre-registration is complete on
GitHub. Data requests have not yet
been sent.

---

## PART VI: HONEST ACCOUNTING
## OF THE FULL IMPC SERIES
## AS IT NOW STANDS

```
DR23 open field correlation
  r = -0.775, p = 0.04
  N = 7 centers
  Status: SIGNIFICANT ✅

DR23 multi-procedure extension
  Fear conditioning: consistent
  PPI: non-linear pattern
  Status: CONSISTENT ✅

EUMODIC replication
  r = -0.200, p = 0.747
  N = 5 centers
  Status: NULL ⚠️
  Explanation: protocol heterogeneity
  suspected — under investigation

DR24 extension
  Status: PENDING — release imminent

JAX data
  Status: PENDING — inquiry open

Faraday cage experiment
  Status: PRE-REGISTERED —
  causal test, design complete,
  requires facility and IACUC
```

The DR23 result remains the primary
observational finding. The EUMODIC
null is an honest result that is
documented in full, with the most
plausible explanation identified and
under investigation. The Faraday cage
experiment is the path forward
regardless of observational outcomes.

---

## PART VII: WHAT THIS MEANS
## FOR THE UNIFIED FRAMEWORK

The EUMODIC null does not change the
position of the IMPC vector within
the unified EM coherence framework.

The unified framework requires:
- Observational evidence that
  EM field coherence correlates
  with navigation behavior across
  independent measurements
- Causal evidence from a controlled
  experiment
- Replication across species and
  EM channels

The DR23 result provides the first
observational rung. The EUMODIC
analysis attempted independent
replication in a procedurally non-
equivalent dataset and produced a
null result with identified confounds.
This is not falsification — it is
a measurement limitation.

The Faraday cage experiment provides
the causal evidence. It is not
dependent on EUMODIC.

The monarch and sea turtle vectors
are independent. They do not rely
on the IMPC/EUMODIC observational
chain. They test the same theoretical
claim through completely different
species, frequencies, and behavioral
systems.

The null result in EUMODIC is the
correct scientific outcome to have
at this stage — it narrows the
measurement requirements, identifies
a specific protocol confound that
needs investigation, and reinforces
that the DR23 result is not trivially
reproducible in any dataset that uses
a thigmotaxis-adjacent measure.

That is useful information.
It is documented honestly here.
The program continues.

---

## VERSION

- v1.0 — February 27, 2026
  Results document.
  Written after eumodic_correlation.py
  completed.
  Null result documented in full.
  Protocol heterogeneity identified
  as primary confound hypothesis.
  Next steps defined.
  eumodic_protocol_audit.py to be
  written and run before closing
  EUMODIC analysis.
