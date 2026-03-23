# NAKED MOLE-RAT EIGENFUNCTION ANALYSIS
## Testing the Universal Tonnetz Prediction Against the Barker 2021 Dataset
## OC-OBS-004 Candidate
## OrganismCore — Eric Robert Lawson
## Document date: 2026-03-23

---

## DOCUMENT PURPOSE

This document specifies the analysis plan for testing the Universal Tonnetz
framework against the publicly available naked mole-rat vocalization dataset
from Barker et al. 2021 (Science, 371(6536), 503-507).

This is a pre-analysis specification. No data has been loaded or inspected
at the time of writing. All predictions are made before analysis begins.

---

## THEORETICAL ORIGIN

This analysis is derived from the Universal Tonnetz framework developed
within OrganismCore. The framework claims:

> All biological communication systems navigate eigenfunction spaces of
> bounded resonating systems. The topology of those eigenfunction spaces
> is physically determined by the geometry of the instrument. Colony
> dialects, individual variation, and cross-individual communication
> are navigations within a shared Tonnetz — not departures from it.

This is the same causal geometry that generated the sea turtle false
attractor prediction (OC-OBS-002), the monarch butterfly analysis
(OC-OBS-001), and the Vedic phonological reconstruction.

The naked mole-rat is selected as the next test case because:

1. A high-quality, publicly accessible dataset already exists
2. The Barker 2021 paper independently found eigenfunction structure
   in the same data — without asking the deeper question this framework asks
3. The vocal anatomy of Heterocephalus glaber is well-characterized,
   making the physical prediction derivable from first principles
4. The soft chirp is the dominant social call — bounded, stereotyped,
   and produced by a well-defined resonating system

---

## THE BARKER 2021 FINDING — WHAT THEY FOUND AND WHAT THEY DID NOT ASK

### What they found

Barker et al. (2021) analyzed soft chirp vocalizations from 166 naked
mole-rats across multiple colonies. Using PCA and spectral decomposition,
they found:

- Most acoustic variance is captured by a small number of eigenfunctions
- That variance is explained primarily at the colony level, not the
  individual level
- When colonies are merged or individuals transferred, call structure
  converges toward the new colony's dialect over time
- This demonstrates cultural transmission of vocal dialect

### What they did not ask

Barker et al. treated the eigenfunctions as statistical descriptors of
acoustic variance. They did not ask:

1. Do the empirical eigenfunctions correspond to the physically-predicted
   resonance modes of the naked mole-rat vocal anatomy?
2. Is the eigenfunction space a Tonnetz — a topologically structured space
   where positions are not arbitrary but determined by the instrument physics?
3. Are colony dialects positions or trajectories within a shared Tonnetz,
   or do different colonies navigate structurally different spaces?
4. Does the soft chirp's eigenfunction structure match the prediction
   derivable from the bounded resonating system geometry alone?

These are the questions this analysis asks.

---

## THE DATASET

**Source:** Zenodo, record 4104396
**URL:** https://zenodo.org/records/4104396
**Citation:** Barker, A.J., Wittenbach, J.D., et al. (2021). Cultural
transmission of vocal dialect in the naked mole-rat. Science, 371(6536),
503-507. DOI: 10.1126/science.abc6588
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
**Size:** ~1.2 GB
**Contents:** Audio recordings of soft chirp vocalizations from 166
naked mole-rats across multiple colonies

**No data request is required. This dataset is freely downloadable.**

---

## THE PHYSICAL PREDICTION — BEFORE TOUCHING THE DATA

The naked mole-rat vocal anatomy constitutes a bounded resonating system.
Its physical parameters determine a set of natural resonance modes —
the eigenfunction basis of the instrument.

From the anatomy:

- The vocal tract of Heterocephalus glaber is short, narrow, and
  highly constrained relative to body size
- The soft chirp is produced in a frequency range of approximately
  1–4 kHz
- The bounded domain has defined boundary conditions (closed at the
  lungs, open at the mouth) that determine the harmonic series
- The resonance modes are harmonically related with specific ratios
  determined by tract geometry

### The Tonnetz prediction

If the Universal Tonnetz framework is correct:

1. **The empirical eigenfunctions from PCA of the soft chirp recordings
   will correspond to the physically-predicted harmonic modes of the
   vocal tract** — not arbitrary statistical components

2. **The eigenfunction space will have Tonnetz topology** — meaning
   positions in the space are not uniformly distributed but cluster
   at physically-determined nodes

3. **Colony dialects will be positions or trajectories within this
   shared Tonnetz** — different colonies occupy different regions of
   the same space, not different spaces

4. **The number of eigenfunctions needed to capture most variance will
   match the number of physically-meaningful harmonic modes** — not
   an arbitrary dimensionality

5. **Individual variation within a colony will be lower-amplitude
   navigation within the colony's Tonnetz region** — coherent with
   the colony position but not departing from the shared topology

These predictions are falsifiable. If the empirical eigenfunctions are
arbitrary statistical components with no correspondence to vocal anatomy
physics, the framework is wrong.

---

## WHAT WE WILL CALCULATE

### Step 1 — Physical baseline: derive the predicted eigenfunction basis

Before loading any audio data:

- From the known anatomy of Heterocephalus glaber, derive the predicted
  resonance modes of the vocal tract
- Compute the expected harmonic frequency ratios from tract geometry
- Define the predicted Tonnetz topology: which eigenfunction positions
  should be occupied, and what the spacing between them should be
- Document all predictions before any data is loaded

This step produces the ground truth against which the empirical
eigenfunctions will be compared.

### Step 2 — Load and preprocess the audio data

- Download the Zenodo dataset
- Load soft chirp recordings using librosa or scipy.io.wavfile
- Segment individual calls using energy thresholding or onset detection
- Extract consistent time windows around each call peak
- Normalize amplitude across recordings
- Organize by colony ID and individual ID

### Step 3 — Spectral feature extraction

For each segmented call:

- Compute the Short-Time Fourier Transform (STFT)
- Extract the power spectral density (PSD)
- Compute the mel-frequency cepstral coefficients (MFCCs)
- Extract fundamental frequency (F0) and harmonic series
- Measure harmonic ratios: F1/F0, F2/F0, F3/F0
- Record colony ID and individual ID for each call

This produces a feature matrix: N calls × M spectral features

### Step 4 — Eigenfunction decomposition

- Apply PCA to the feature matrix
- Extract the principal components (empirical eigenfunctions)
- Compute variance explained by each component
- Identify how many components capture 90%, 95%, 99% of variance
- Map each component onto the frequency domain to interpret its
  physical meaning

**Key test:** Do the top eigenfunctions correspond to the physically-
predicted harmonic modes from Step 1?

### Step 5 — Tonnetz topology test

- Project all calls into the eigenfunction space
- Compute the density distribution of calls in eigenfunction space
- Test whether calls cluster at discrete positions (Tonnetz nodes)
  or are continuously distributed
- Apply a clustering algorithm (k-means, DBSCAN) to identify
  natural clusters in eigenfunction space
- Test whether the number of natural clusters matches the predicted
  number of Tonnetz nodes

**Key test:** Is the eigenfunction space structured (Tonnetz topology)
or unstructured (continuous uniform distribution)?

Use Hartigan's dip test for unimodality vs. multimodality on each
eigenfunction dimension.

### Step 6 — Colony dialect as Tonnetz navigation

- Compute the centroid of each colony's calls in eigenfunction space
- Compute within-colony variance vs. between-colony variance
  (mirrors the Barker ANOVA structure but in eigenfunction space)
- Test whether colony centroids correspond to distinct Tonnetz nodes
  or are arbitrary positions in a continuous space
- Compute the geodesic distance between colony centroids within the
  Tonnetz topology
- Test whether colonies that are geographically or socially closer
  occupy adjacent Tonnetz positions

**Key test:** Do colony dialects represent discrete navigational
positions within the Tonnetz, or arbitrary acoustic variation?

### Step 7 — Individual variation as local navigation

- For each colony, compute individual call trajectories within the
  eigenfunction space
- Test whether individual variation is bounded within the colony's
  Tonnetz region
- Compute the ratio of individual variance to colony variance in
  eigenfunction space
- Test whether this ratio is consistent with bounded local navigation
  (low ratio) vs. free variation (ratio approaching 1.0)

### Step 8 — Cross-colony convergence test (if data permits)

The Barker dataset includes cases where individuals were transferred
between colonies and their calls were recorded over time.

If those longitudinal records are included:

- Track the trajectory of transferred individuals in eigenfunction space
- Test whether convergence trajectories follow geodesics in the Tonnetz
  (shortest path between two Tonnetz positions) or arbitrary paths
- This would be direct evidence of navigation within the Tonnetz structure

---

## WHAT WE EXPECT TO FIND

### Primary prediction (falsifiable)

The top 3-5 principal components from PCA of the soft chirp recordings
will correspond to the physically-predicted harmonic modes of the naked
mole-rat vocal tract, not arbitrary statistical components.

**Confirmation:** Spearman correlation between empirical eigenfunction
frequencies and predicted harmonic mode frequencies > 0.8, p < 0.05.

**Falsification:** No correspondence between empirical eigenfunctions
and physical predictions. Components are arbitrary.

### Secondary prediction

Colony dialects will cluster at discrete positions in eigenfunction space
consistent with Tonnetz node structure, not continuously distributed.

**Confirmation:** Hartigan's dip test significant for multimodality.
Number of natural clusters matches predicted number of Tonnetz nodes.

**Falsification:** Continuous uniform distribution in eigenfunction space.
No evidence of discrete clustering.

### Tertiary prediction

Within-colony variance will be significantly lower than between-colony
variance in eigenfunction space, and the ratio will be consistent with
bounded local navigation.

**Confirmation:** F-statistic from one-way ANOVA of colony membership
on eigenfunction coordinates significant with large effect size (η² > 0.5).

**Falsification:** No significant colony effect in eigenfunction space.

---

## WHAT THIS RESULT MEANS IF CONFIRMED

### For the naked mole-rat specifically

The Barker 2021 finding that "most variance is explained by colony" would
be reinterpreted: colonies do not develop arbitrary dialects through
cultural drift. They navigate to specific positions within a physically-
determined eigenfunction space. The dial they are turning has discrete
positions. Cultural transmission is the mechanism by which new colony
members learn which position their colony occupies.

This reframes the naked mole-rat dialect from a social phenomenon to
a physical navigation phenomenon — which is consistent with and predicted
by the Universal Tonnetz framework.

### For the Universal Tonnetz framework

A confirmed result in naked mole-rats would be the second empirical
confirmation of the framework across two completely different:

- Species (loggerhead sea turtle vs. Heterocephalus glaber)
- Communication modalities (geomagnetic navigation vs. acoustic vocalization)
- Frequency ranges (AM band 530-1700 kHz vs. soft chirp 1-4 kHz)
- Analysis methods (circular statistics vs. eigenfunction decomposition)
- Dataset sources (NOAA STSSN restricted vs. Zenodo open access)

Two independent confirmations across five orders of magnitude of the
EM/acoustic spectrum, derived from the same theoretical framework, using
different methods, in different species, is the beginning of a consilience
argument for the Universal Tonnetz as a general law of biological
communication.

### For the Barker 2021 paper

This analysis does not contradict Barker et al. It extends their finding.
Their result (cultural transmission of dialect) remains fully valid.
This analysis asks whether the eigenfunction space within which that
cultural transmission operates has physical structure — which is a
question their paper did not pose.

The appropriate relationship to their work is collaborative extension,
not competition.

---

## WHAT THIS RESULT MEANS IF NULL

A null result — empirical eigenfunctions do not correspond to physical
predictions, eigenfunction space has no Tonnetz topology — is informative
in two ways:

1. It constrains the Universal Tonnetz framework: the framework may apply
   to navigational systems (magnetoreception, migration) but not to
   social vocalization systems
2. It provides a clean negative result that narrows the claim and
   makes the positive results in sea turtles and monarchs stronger
   by comparison

A null result will be reported fully regardless of direction.
This document constitutes the pre-registration of that commitment.

---

## RELATIONSHIP TO OTHER ANALYSES IN THE SERIES

| Study | Species | Channel | Status |
|---|---|---|---|
| OC-OBS-001 | Monarch butterfly | FM 88-108 MHz | Complete, Rayleigh p=0.000517 |
| OC-OBS-002 | Loggerhead sea turtle | AM 530-1700 kHz | Complete, R=0.80, r=0.59, p=0.0000 |
| OC-OBS-003 | Mouse | ELF 50-60 Hz | Complete, r=-0.886, p=0.019 |
| OC-OBS-004 | Naked mole-rat | Acoustic 1-4 kHz | THIS ANALYSIS |

---

## REQUIRED LIBRARIES

```python
# Core
numpy
scipy
pandas

# Audio processing
librosa          # STFT, MFCCs, onset detection
soundfile        # WAV loading

# Statistics
pingouin         # ANOVA, effect sizes
diptest          # Hartigan's dip test for unimodality
scikit-learn     # PCA, k-means, DBSCAN

# Visualization
matplotlib
seaborn
```

---

## DATA ACCESS

```
Dataset:   Naked mole-rat soft chirp vocalizations
Source:    Zenodo record 4104396
URL:       https://zenodo.org/records/4104396
License:   CC BY 4.0
Size:      ~1.2 GB
Citation:  Barker et al. (2021) Science 371(6536) 503-507
           DOI: 10.1126/science.abc6588

No data request required.
No restricted data involved.
No institutional approval required.
```

---

## BLOCKING ITEMS

None. This analysis can begin immediately.

- [x] Dataset publicly accessible
- [x] License permits research use
- [x] Physical predictions derivable from published anatomy
- [x] Analysis pipeline specifiable before data loading
- [x] Pre-registration document complete

---

## NEXT STEP

Download the Zenodo dataset and begin Step 1:
derive the physical baseline (predicted eigenfunction basis)
from naked mole-rat vocal anatomy before loading any audio.

Physical predictions must be fully documented and committed
before the first audio file is opened.

---

## VERSION AND AUDIT TRAIL

```
Document version:    1.0
Document date:       2026-03-23
Status:              Pre-registration (no data loaded)
Framework origin:    Universal Tonnetz (OrganismCore)
Dataset:             Barker et al. 2021, Zenodo 4104396
Extends:             OC-OBS-002 (sea turtle), OC-OBS-001 (monarch)
Author:              Eric Robert Lawson
```

---

*Predictions made before data is loaded.*
*All results will be reported regardless of direction.*
*This document is the pre-registration record.*
