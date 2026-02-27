# IMPC SPATIAL NAVIGATION ANALYSIS
# DOCUMENT 3: MULTI-PROCEDURE
# ELF CORRELATION — FEAR
# CONDITIONING AND ACOUSTIC
# STARTLE / PPI
## OrganismCore Cross-Species
## Communication Series
## Desk Analysis Document 10
## February 27, 2026

---

## ARTIFACT METADATA

```
artifact_type:
  Closing document of the IMPC
  analysis sub-series.
  Analysis 3, Document 4.

  Documents Fear Conditioning and
  Acoustic Startle/PPI analyses
  and their relationship to the
  primary OFD result. Closes the
  IMPC DR23 analysis phase with
  a complete multi-procedure
  picture.

precursor_documents:
  Document 1 (Desk Analysis 8):
    Primary OFD result.
    r=-0.886, p=0.019 *
    N=6 centers.

  Document 2 (Desk Analysis 9):
    Extended center queries.
    KMPC/JAX targeted search.
    MRC Harwell homozygote.
    All exclusions documented.

status:
  COMPLETE — IMPC DR23 initial
  analysis phase closed.

author:
  Eric Robert Lawson
  OrganismCore
```

---

## PART I: PROCEDURE LANDSCAPE

### What DR23 contains

```
Total procedures in DR23: 128
Procedures with behavioral
relevance to spatial navigation
or anxiety: 12

Procedures meeting minimum
suitability criteria
(≥4 ELF centers, ≥200 wildtype
records):

  1. Fear Conditioning
       ELF centers: 5 (wildtype)
       Wildtype N:  277,455
       Relevance:   HIGH
       (contextual memory,
        hippocampal-dependent)

  2. Acoustic Startle / PPI
       ELF centers: 7 (wildtype)
       Wildtype N:  356,623
       Relevance:   MODERATE
       (sensorimotor gating,
        thalamo-cortical circuits)

  3. Open Field (primary, complete)
       ELF centers: 6 (wildtype)
       Wildtype N:  16,161
       Relevance:   MODERATE
       (anxiety/exploration proxy)

ABSENT from DR23:
  Elevated plus maze: NOT PRESENT
  Morris water maze:  NOT PRESENT
  Barnes maze:        NOT PRESENT
  Y-maze:             1 center only
                      (RBRC, N=5,557)
  Radial arm maze:    NOT PRESENT

The absence of spatial navigation
mazes from DR23 is a structural
limitation. The IMPC phenotyping
battery does not include a direct
spatial memory test with multi-
center coverage. The closest
available proxy is contextual
fear conditioning (hippocampal-
dependent associative memory).
```

---

## PART II: FEAR CONDITIONING
## ANALYSIS

### Design and parameters

```
Procedure: IMPC_FEA_001 / variants
Standard protocol:
  Day 1 — Conditioning:
    Mouse placed in chamber.
    Baseline period (~3 min).
    Tone (conditioned stimulus).
    Foot shock (unconditioned
    stimulus).
    Post-shock period.
  Day 2 — Context test:
    Mouse returned to same chamber.
    No shock. Freezing measured.
    (hippocampal-dependent)
  Day 3 — Cue test:
    Mouse placed in novel chamber.
    Tone played. Freezing measured.
    (amygdala-dependent)

Primary parameter:
  Context % Freezing Time
  (IMPC_FEA_009_001 and
   center-specific equivalents)
  = percentage of time spent
    freezing during context test.
  = direct measure of hippocampal
    context memory.

Secondary parameters:
  Cue Tone % Freezing Time
  Post-shock % Freezing Time
  Context–Baseline difference

Center-specific parameter IDs:
  UC Davis, TCP, CCP-IMG:
    IMPC_FEA_009_001
  ICS:    ICS_FEA_009_001
  KMPC:   KMPCLA_FEA_009_001
  MRC Harwell: HRWLLA_FEA_009_001
    (zero wildtype records — excluded)
```

### Data

```
Center      ELF   N_wt  Context%  Cue%  PostShock%
UC Davis     31  2,395    14.2%  11.2%       5.2%
ICS          36  2,273    37.2%  64.2%         —
KMPC         67    788    15.3%  19.2%       4.4%
TCP          74  1,346    39.9%  29.1%      23.1%
CCP-IMG      74  3,938    17.4%  10.7%       8.7%

MRC Harwell  59      0    —       —           —
  (excluded: no wildtype records)

Total wildtype analyzed: 10,740
```

### Results

```
Context % Freezing vs ELF:
  Spearman r = +0.616  p = 0.269  ns
  Pearson  r = +0.047  p = 0.941
  N = 5 centers
  LOO: 0/5 significant
  Fragility: VERY FRAGILE

Cue % Freezing vs ELF:
  Spearman r = -0.154  p = 0.805  ns
  N = 5 centers
  LOO: 0/5 significant

Post-shock % Freezing vs ELF:
  Spearman r = +0.738  p = 0.262  ns
  N = 4 centers

Context–Baseline diff vs ELF:
  Spearman r = +0.738  p = 0.262  ns
  N = 4 centers

ALL RESULTS: NOT SIGNIFICANT.
```

### The TCP/CCP-IMG split in fear
### conditioning

```
TCP     (ELF 74):  Context 39.9%
CCP-IMG (ELF 74):  Context 17.4%
Difference:        22.5 percentage
                   points

Same building (25 Orde St Toronto).
Same strain (C57BL/6NCrl).
Same ELF assignment (score 74).
Same parameter ID (IMPC_FEA_009_001).

This 22.5 pp within-building
difference is larger than the
between-building range across
the other three centers:
  UC Davis–KMPC–CCP-IMG cluster:
    14.2–15.3–17.4% (3.2 pp range)
  ICS–TCP cluster:
    37.2–39.9% (2.7 pp range)

The within-building split exceeds
the between-building variance.
This means the between-center
variance in fear conditioning
is dominated by the TCP/CCP-IMG
protocol difference, not by
facility ELF.

This same split was observed in:
  OFD thigmotaxis:
    TCP 91.4% vs CCP-IMG 62.9%
  PPI global:
    TCP 60.5% vs CCP-IMG 53.2%
  Fear conditioning:
    TCP 39.9% vs CCP-IMG 17.4%

The TCP/CCP-IMG behavioral split
is consistent across all three
behavioral procedures and affects
measures of anxiety (OFD),
associative memory (FEA), and
sensorimotor gating (PPI). It is
a systematic facility-level
difference that is independent
of ELF score.

LIKELY EXPLANATION:
  TCP and CCP-IMG use the same
  procedure ID but different
  equipment calibration or
  experimental parameters. The
  most probable sources:
  (a) Shock intensity difference:
      TCP uses stronger shock →
      higher post-shock and context
      freezing. Supported by TCP
      post-shock freezing 23.1% vs
      CCP-IMG 8.7%.
  (b) Freezing detection threshold:
      Different motion threshold
      settings for what counts as
      freezing.
  (c) Context salience: different
      chamber designs produce
      different contextual memory
      consolidation.

  The shock intensity explanation
  is most parsimonious: TCP
  post-shock freezing (23.1%) is
  2.6× higher than CCP-IMG (8.7%)
  in the same session, before any
  memory consolidation. This is
  an acquisition difference, not
  a memory difference.
```

### Interpretation

```
Fear conditioning context freezing
does not correlate with facility
ELF score in the current dataset.

The between-center variance is
dominated by protocol calibration
differences (primarily the TCP/
CCP-IMG split) that obscure any
facility-level ELF signal.

This result does not contradict
the OFD finding. It means fear
memory circuits are not detectably
ELF-sensitive at the facility-level
scale of this analysis, OR that
protocol variance in fear conditioning
is too large to detect an ELF effect
with N=5 centers.

Both interpretations are honest
and are reported as such.
```

---

## PART III: ACOUSTIC STARTLE /
## PPI ANALYSIS

### Design and parameters

```
Procedure: IMPC_ACS_001 / variants
Standard protocol:
  Acoustic startle chamber.
  Series of trials:
    Startle-only (S): loud burst.
    Prepulse + startle (PP+S):
      weak tone precedes burst.
  PPI = % reduction in startle
    amplitude when preceded by
    prepulse.
  Higher PPI = stronger inhibition
    of startle = better sensorimotor
    gating.

Primary parameter:
  % Pre-pulse inhibition — Global
  (IMPC_ACS_037_001 and variants)
  = average PPI across all prepulse
    intensities.

ELF centers with wildtype data:
  UC Davis, ICS, RBRC, KMPC,
  TCP, CCP-IMG, BCM
  (MRC Harwell and HMGU:
   zero wildtype records)
```

### Data

```
Center      ELF   N_wt    PPI%    SD
UC Davis     31  4,375   51.3%  15.7%
ICS          36  2,399   59.6%  13.9%
RBRC         55  1,338   67.7%  17.9%
KMPC         67    986   72.1%  14.0%
TCP          74  1,840   60.5%  21.9%
CCP-IMG      74  3,931   53.2%  13.3%
BCM          94    230   26.6%  30.9%

Total wildtype: 14,899
```

### Results

```
PPI Global vs ELF:
  Spearman r = -0.180  p = 0.699  ns
  N = 7 centers
  LOO: 0/7 significant
  Fragility: VERY FRAGILE
```

### The non-linear PPI pattern

```
Reading the per-center data:

ELF 31 → 51.3%
ELF 36 → 59.6%   (+8.3 pp)
ELF 55 → 67.7%   (+8.1 pp)
ELF 67 → 72.1%   (+4.4 pp)
ELF 74 → 60.5% / 53.2%  (TCP/CCP split)
ELF 94 → 26.6%   (-33 pp)

From ELF 31 to ELF 67, PPI rises
monotonically at approximately
+1.0 pp per ELF unit. This is a
clear positive trend across four
centers.

BCM at ELF 94 breaks this trend
with 26.6% PPI — 45 pp below
KMPC at ELF 67 and 25 pp below
UC Davis at ELF 31.

Two explanations for BCM:

  1. TRUE BIOLOGICAL EFFECT:
     At very high ELF (BCM score 94,
     Texas Medical Center), the
     dose-response relationship
     reverses or saturates —
     extremely high chronic ELF
     impairs the sensorimotor gating
     circuits that were enhanced at
     moderate levels. A biphasic
     (hormetic) dose-response in
     ELF is biologically plausible
     and has precedent in the
     published literature.

  2. BCM DATA QUALITY:
     BCM has only 230 wildtype PPI
     records with SD=30.9% — the
     largest SD of any center by
     factor 2×. The wide dispersion
     suggests high measurement
     variability. The median of 26.6%
     may be unreliable with N=230
     and SD=31.

CANNOT DETERMINE WHICH without
additional BCM PPI data or
measured ELF values at BCM.

BCM is excluded from trend
description but reported in
full data table.

The monotonically positive trend
ELF 31→67 is noted as a
directional observation, not a
statistical finding.
```

---

## PART IV: CROSS-PROCEDURE
## SYNTHESIS

### Complete results table

```
Procedure         Parameter             N   r_S      p    sig
──────────────────────────────────────────────────────────────
Open Field        Thigmotaxis prop      6  -0.886  0.019   *
Fear Conditioning Context % Freezing   5  +0.616  0.269  ns
Fear Conditioning Cue % Freezing       5  -0.154  0.805  ns
Fear Conditioning Post-shock %         4  +0.738  0.262  ns
Fear Conditioning Context-BL diff      4  +0.738  0.262  ns
Acoustic Startle  PPI Global           7  -0.180  0.699  ns

One significant result of six tested.
```

### What the pattern means

```
The OFD thigmotaxis result
(r=-0.886, p=0.019) does not
replicate in fear conditioning
or acoustic startle/PPI.

Three interpretations:

  1. THE OFD RESULT IS SPECIFIC
     TO ANXIETY/EXPLORATION
     BEHAVIOR.
     ELF affects open-field
     anxiety and exploratory
     behavior in C57BL/6N mice
     but does not detectably affect
     hippocampal associative memory
     or sensorimotor gating at the
     facility level.
     This constrains the mechanism:
     ELF acts on circuits mediating
     anxiety and spatial exploration
     (hypothalamic-limbic-prefrontal)
     rather than on memory
     consolidation circuits
     (hippocampal CA1/CA3) or
     sensorimotor gating circuits
     (pedunculopontine-thalamo-
     cortical).

  2. THE OFD RESULT IS DRIVEN BY
     A CONFOUND THAT DOES NOT
     AFFECT FEA OR PPI.
     The OFD correlation may reflect
     a facility-level variable that
     co-varies with ELF score and
     specifically affects open-field
     thigmotaxis — for example,
     animal room noise levels,
     bedding type, or test room
     ambient conditions. If such
     a confound drives OFD but not
     FEA or PPI, the ELF
     interpretation is weakened.

  3. PROTOCOL VARIANCE MASKS ELF
     IN FEA AND PPI.
     The TCP/CCP-IMG behavioral
     split is larger in fear
     conditioning (22.5 pp) than
     in OFD (28.5 pp thigmotaxis
     proportion). Protocol
     calibration differences
     between centers dominate
     the between-center variance
     in FEA and PPI, preventing
     detection of a facility ELF
     signal even if one exists.
     The OFD result survives because
     thigmotaxis proportion has
     lower between-protocol variance
     than absolute freezing
     percentages.

All three interpretations are
consistent with the data.
None can be ruled out with
the current dataset.
They are reported in full.
```

### The TCP/CCP-IMG behavioral
### split — final assessment

```
Summary of TCP vs CCP-IMG
across all procedures:

  Procedure    TCP     CCP-IMG   Diff
  OFD thigmo   91.4%   62.9%   28.5 pp
  FEA context  39.9%   17.4%   22.5 pp
  FEA post-shk 23.1%    8.7%   14.4 pp
  PPI global   60.5%   53.2%    7.3 pp

The split is present in all four
measures. It is largest for
measures most sensitive to arousal
level (thigmotaxis, post-shock
freezing) and smallest for
measures less sensitive to
arousal (PPI).

This pattern is consistent with
a difference in animal baseline
arousal or acute stress reactivity
between the two facilities —
TCP animals are consistently more
anxious, freeze more, and hugg
walls more than CCP-IMG animals
in the same building.

The most parsimonious explanation
remains test duration for OFD
(TCP 90 min vs CCP-IMG 60 min)
plus shock intensity for FEA
(TCP post-shock 23.1% vs CCP-IMG
8.7%). These two protocol
differences together explain the
TCP/CCP-IMG behavioral profile
across all procedures without
requiring a biological difference.

DATASET RECOMMENDATION:
  For any cross-center IMPC
  behavioral analysis, TCP and
  CCP-IMG should be treated as
  a single facility with a within-
  facility protocol variable, not
  as two independent data points.
  Analyses should use one or the
  other, not both, with sensitivity
  testing for the choice.
```

---

## PART V: HONEST FINAL
## ASSESSMENT

```
WHAT IS ESTABLISHED IN THE
IMPC DR23 ANALYSIS:

  ONE SIGNIFICANT FINDING:
    Wildtype C57BL/6N thigmotaxis
    proportion correlates negatively
    with facility ELF score across
    6 IMPC centers.
    Spearman r = -0.886, p = 0.019.
    Effect size: 36 pp difference
    between lowest-ELF (ICS, 94.3%)
    and highest-ELF (BCM, 58.3%)
    center.

  ONE CONSISTENT NULL:
    Fear conditioning context and
    cue freezing do not correlate
    with ELF. The between-center
    variance is dominated by
    protocol calibration differences.

  ONE DIRECTIONAL NON-SIGNIFICANT
  OBSERVATION:
    PPI rises monotonically from
    ELF 31 to ELF 67, then collapses
    at ELF 94 (BCM). Non-linear
    dose-response possible but
    not statistically established.

  ONE SYSTEMATIC DATASET LIMITATION:
    The TCP/CCP-IMG behavioral split
    is present across all procedures
    and must be treated as a
    within-facility protocol effect
    in any cross-center analysis.

WHAT IS NOT ESTABLISHED:
  — Causation (ELF causes thigmotaxis
    change vs correlated confound)
  — Mechanism (which ELF-sensitive
    circuit produces the OFD effect)
  — Generalization to spatial memory
    (no maze data in DR23; fear
    conditioning null does not rule
    out maze impairment but does
    not support it)
  — Replication (N=6 centers, one
    significant result of six tests)

THE MOST HONEST SINGLE STATEMENT:
  In IMPC Data Release 23, wildtype
  C57BL/6N mice at higher estimated
  ELF facilities spend significantly
  less time in the periphery of the
  open field (r=-0.886, p=0.019,
  N=6 centers). This effect does not
  generalize to fear conditioning
  or sensorimotor gating measures
  in the same dataset. The result
  is strain-controlled, duration-
  corrected, and directionally
  consistent across sensitivity
  analyses. It is preliminary,
  fragile, and requires replication.
```

---

## PART VI: IMPC SERIES STATUS
## AND NEXT STEPS

### Analysis 3 IMPC phase — complete

```
Documents produced:
  Doc 1 (Desk 8): Primary OFD result
  Doc 2 (Desk 9): Extended queries,
    exclusion documentation
  Doc 3 (Desk 10): FEA + PPI,
    multi-procedure synthesis

Scripts produced: 10
  impc_open_field_query.py
  impc_summarize_by_center.py
  impc_elf_estimation.py
  impc_raw_audit.py
  impc_strain_controlled.py
  impc_proportion_correlation.py
  impc_kmpc_jax_query.py
  impc_kmpc_parameter_resolution.py
  impc_kmpc_pct_center_wildtype.py
  impc_maze_search.py
  impc_fear_conditioning_ppi.py

Total observations processed:
  851,255 OFD + 1,101,618 FEA +
  2,015,945 PPI = 3,968,818
```

### Next steps — prioritized

```
PRIORITY 1: MONARCH WATCH RESPONSE
  Analysis 1 primary V-test is
  pending Monarch Watch recovery
  data. This is the primary test
  of the OrganismCore series.
  Status: awaiting response.

PRIORITY 2: EUMODIC REPLICATION
  The European Mouse Disease Clinic
  dataset predates IMPC and contains
  overlapping European centers.
  OFD data from EUMODIC at centers
  with known ELF scores (ICS,
  MRC Harwell, HMGU) would provide
  independent replication of the
  primary OFD finding.

PRIORITY 3: JAX OFD DATA REQUEST
  Direct inquiry to JAX KOMP2.
  ELF ~15 (rural Bar Harbor).
  Would be the lowest-ELF anchor
  available. If JAX thigmotaxis
  proportion > 92%, gradient
  confirmed at the low end with
  highest-contrast point available.

PRIORITY 4: BCM PPI INVESTIGATION
  BCM shows anomalously low PPI
  (26.6%) with high SD (30.9%)
  and N=230. With more wildtype
  PPI records and/or measured ELF,
  the non-linear PPI pattern could
  be confirmed or disconfirmed.
  A biphasic ELF dose-response in
  PPI would be a significant and
  novel finding.
```

---

## VERSION

```
v1.0 — February 27, 2026

Document 10 of the OrganismCore
electromagnetic navigation series.
Document 3 of the IMPC sub-series.
FINAL document of IMPC DR23 phase.

Primary result (confirmed across
3 documents):
  OFD Thigmotaxis
  Spearman r = -0.886
  p = 0.019 *
  N = 6 centers
  Wildtype C57BL/6N
  100% C57BL/6N strain family
  Proportion-corrected

Fear conditioning: ns
Acoustic startle/PPI: ns
  (non-linear pattern noted)

Series continues with:
  Monarch Watch response (pending)
  EUMODIC replication (queued)
```
