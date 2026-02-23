# VEDIC SANSKRIT PHONEME INVENTORY
## Rigveda Reconstruction — Master Reference
## February 2026

---

## WHAT THIS DOCUMENT IS

The master phoneme reference for the
Vedic Sanskrit reconstruction project.

Every phoneme used in the reconstruction
is documented here with:
- IPA symbol and Devanāgarī character
- Śikṣā classification
- Articulatory description
- Formant targets (F1, F2, F3, F4)
- Formant bandwidths
- Duration parameters
- Coarticulation parameters
- Synthesis parameters
- Diagnostic thresholds
- Verification status
- First verified word

This document is VS-specific.
It does not inherit values from
any other language project.
Every value is derived from:
  1. Physics of the vocal tract
  2. Śikṣā treatise classification
  3. Vedic orthographic record
  4. Comparative Indo-European evidence
  5. Acoustic measurement of living
     cognate languages and reciters
  6. VS-internal diagnostic results

---

## ARCHITECTURE NOTE

**This inventory is self-contained.**

Where a VS phoneme occupies the same
position in the universal vocal topology
as a phoneme verified in another project,
this is noted as a convergence observation.
It is not a dependency. The VS value
is independently derived and independently
verified. The agreement is evidence that
the acoustic phonological space is real
and universal — not evidence that one
project borrowed from another.

---

## HOW TO USE THIS DOCUMENT

**For synthesis:**
Use the F, B, and GAINS arrays directly
in voice_physics_vs.py. Do not adjust
verified parameters without re-running
the diagnostic and updating this document.

**For diagnostics:**
The DIAGNOSTIC THRESHOLDS section gives
the pass/fail ranges for each phoneme.
These are derived from the parameter
values plus acoustic measurement margins.

**For new phonemes:**
Follow the NEW PHONEME INTRODUCTION
WORKFLOW at the end of this document.
A new phoneme is PENDING until its
diagnostic passes AND the ear confirms.
Only then is it VERIFIED.

**For agents:**
Read VERIFIED entries as ground truth.
Read PENDING entries as current best
estimates — subject to revision.
Never re-derive a VERIFIED phoneme
without documented evidence of error.

---

## SYNTHESIS ENGINE

**File:** `voice_physics_vs.py`

This is the VS-specific synthesis engine.
It implements the source-filter model
from physics. It is not imported from
or dependent on any other project.

### Source
Rosenberg glottal pulse model.
Open quotient: 0.65 (male reciter).
Differentiated for formant filtering.
Pitch: 120.0 Hz default
(Vedic recitation — chest register,
male voice, ritual performance).

### Formant filter
IIR resonator bank — four formants.
F1–F4 with independent bandwidths
and gains. Applied to Rosenberg source.

### Retroflex F3 dip model
`iir_notch()` applied at F3 frequency
for all mūrdhanya phonemes.
The notch models the acoustic zero
caused by the retroflexed tongue.
F3 target for mūrdhanya class:
below 2500 Hz. Neutral (alveolar)
F3 reference: 2700 Hz.
Depression >= 200 Hz required for
mūrdhanya confirmation.

### Aspirated stop architecture
Four-phase model for aspirated stops:
  Phase 1: voiced closure murmur
  Phase 2: burst at place locus
  Phase 3: aspiration noise
           (turbulent airflow,
            broad spectrum,
            no voicing)
  Phase 4: short voiced VOT release
This is new territory — no aspirated
stops exist in the OE inventory.
The aspiration phase is the
phonemically distinctive feature.

### Nasal antiresonance model
`iir_notch()` applied at the nasal
zero frequency for all nasal phonemes.
[m]: notch ~800 Hz (bilabial)
[n]: notch ~800 Hz (dental/alveolar)
[ɳ]: notch ~1000 Hz (retroflex)
[ɲ]: notch ~1200 Hz (palatal)
[ŋ]: notch ~2000 Hz (velar)
The notch-to-neighbour ratio < 0.60
confirms the antiresonance is present.

### Pitch accent F0 modulation
Udātta:   F0 × 1.20–1.35 above baseline
Anudātta: F0 at baseline
Svarita:  F0 falls continuously
          from udātta to anudātta
          through syllable duration

### Coarticulation model
Linear interpolation of formant targets
across coarticulation windows.
Window size: 10–15% of segment duration
at onset and offset.
F_prev and F_next passed to each
segment synthesiser.

### Room simulation
Schroeder reverb approximation.
VS default: rt60 = 1.5 s
(temple courtyard / outdoor ritual).
direct_ratio = 0.55.
Less reverberant than OE mead hall.
More direct signal.

### Time stretching
OLA (overlap-add) at 4× factor.
Window: 40 ms Hanning.
Used for all diagnostic slow versions.

---

## DIAGNOSTIC THRESHOLDS

### Voicing
Voiced phonemes:       voicing >= 0.50
Strongly voiced:       voicing >= 0.65
Voiceless phonemes:    voicing <= 0.30
Aspirated stops:
  closure phase:       voicing >= 0.40
  aspiration phase:    voicing <= 0.20

### Formant centroid bands
F1 measurement band:   depends on vowel
                       specified per phoneme
F2 measurement band:   depends on vowel
                       specified per phoneme
F3 mūrdhanya check:    centroid < 2500 Hz
                       depression >= 200 Hz
                       vs neutral 2700 Hz

### Voiced stop closure
LF energy ratio (below 500 Hz): >= 0.40
Confirms voiced closure murmur
without pitch period detection.

### Nasal antiresonance
Notch-to-neighbour ratio: < 0.60
Notch band: ±200 Hz around notch centre
Neighbour bands: immediately adjacent

### Duration
Specified per phoneme in ms.
Long vowels: >= 1.7× corresponding
             short vowel duration.
Aspirated stops: aspiration phase
                 20–40 ms.

### VS-internal separation
Once >= 3 VS phonemes verified in
a given articulatory dimension,
separation checks use VS-internal
reference values only.
Minimum separation: 150 Hz in F2
between adjacent phoneme categories.

---

## PHONEME TABLES

### NOTATION SYSTEM

```
STATUS:
  VERIFIED  — diagnostic passed, ear confirmed
  PENDING   — in progress, parameters estimated
  TRANSFER  — same vocal topology position as
              a phoneme verified in another
              reconstruction; requires independent
              VS diagnostic confirmation before
              status becomes VERIFIED

Each TRANSFER entry notes the convergence
observation but requires its own diagnostic
pass to become VERIFIED. A TRANSFER is a
starting hypothesis, not a verified value.
```

---

### VOWELS — SHORT

#### [a] — short open central unrounded — अ
**Śikṣā:** kaṇṭhya (guttural)
**Status:** PENDING (AGNI in progress)
**First word target:** AGNI

```
VS_A_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B      = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS = 55.0
VS_A_COART_ON  = 0.12
VS_A_COART_OFF = 0.12
```

Diagnostic targets:
- F1 centroid 620–800 Hz
- F2 centroid 900–1300 Hz
- Voicing >= 0.50
- Duration 45–70 ms

Note: Śikṣā places [a] in the
kaṇṭhya (velar/guttural) class —
the maximally open vocal tract.
This is consistent with high F1.
The Sanskrit [a] is a full open vowel,
not a reduced schwa. It is the
phonological default of the language.

---

#### [aː] — long open central unrounded — आ
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```
VS_AA_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_AA_B      = [130.0,  160.0,  220.0,  280.0]
VS_AA_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_AA_DUR_MS = 110.0   — long: >= 1.7× [a]
VS_AA_COART_ON  = 0.10
VS_AA_COART_OFF = 0.10
```

Same formant targets as [a].
Duration is the phonemic distinction.

---

#### [i] — short close front unrounded — इ
**Śikṣā:** tālavya (palatal)
**Status:** PENDING (AGNI in progress)
**First word target:** AGNI

```
VS_I_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_I_B      = [ 80.0,  130.0,  180.0,  250.0]
VS_I_GAINS  = [ 12.0,    8.0,    1.5,    0.5]
VS_I_DUR_MS = 50.0
VS_I_COART_ON  = 0.12
VS_I_COART_OFF = 0.12
```

Diagnostic targets:
- F1 centroid 220–340 Hz
- F2 centroid 2000–2400 Hz
- Voicing >= 0.50
- Duration 40–65 ms

Śikṣā places [i] in the tālavya
(palatal) class — high F2, front
tongue position. The high F2 target
of ~2200 Hz is consistent with
palatal articulation.

---

#### [iː] — long close front unrounded — ई
**Śikṣā:** tālavya
**Status:** PENDING

```
VS_II_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_II_B      = [ 80.0,  130.0,  180.0,  250.0]
VS_II_GAINS  = [ 12.0,    8.0,    1.5,    0.5]
VS_II_DUR_MS = 100.0   — long: >= 1.7× [i]
```

---

#### [u] — short close back rounded — उ
**Śikṣā:** oṣṭhya (labial)
**Status:** PENDING

```
VS_U_F      = [300.0,  800.0, 2300.0, 3100.0]
VS_U_B      = [ 80.0,  120.0,  200.0,  260.0]
VS_U_GAINS  = [ 16.0,    8.0,    1.5,    0.5]
VS_U_DUR_MS = 50.0
VS_U_COART_ON  = 0.12
VS_U_COART_OFF = 0.12
```

Śikṣā places [u] in the oṣṭhya
(labial) class. Lip rounding
lowers F2. Back tongue position
also lowers F2. Both effects
converge on low F2 target ~800 Hz.

---

#### [uː] — long close back rounded — ऊ
**Śikṣā:** oṣṭhya
**Status:** PENDING

```
VS_UU_F      = [300.0,  800.0, 2300.0, 3100.0]
VS_UU_DUR_MS = 100.0   — long: >= 1.7× [u]
```

---

#### [ɻ̩] — syllabic retroflex approximant — ऋ
**Śikṣā:** mūrdhanya (retroflex/cerebral)
**Status:** VERIFIED — ṚG
**Date verified:** February 2026
**Diagnostic:** rg_diagnostic.py v1

```
VS_RV_F      = [420.0, 1300.0, 2200.0, 3100.0]
VS_RV_B      = [150.0,  200.0,  280.0,  300.0]
VS_RV_GAINS  = [ 14.0,    7.0,    1.5,    0.4]
VS_RV_DUR_MS      = 60.0
VS_RV_COART_ON    = 0.15
VS_RV_COART_OFF   = 0.15
```

Verified values:
- F1 centroid:  385 Hz  (target 350–500)
- F2 centroid: 1212 Hz  (target 1100–1500)
- F3 centroid: 2355 Hz  (target < 2500)
- F3 depression: 345 Hz (target >= 200)
- Voicing: 0.6013       (target >= 0.50)
- Duration: 60 ms       (target 50–80)

The mūrdhanya marker: F3 depression
of 345 Hz below the neutral alveolar
reference of 2700 Hz. The tongue curl
is present in the acoustic output.
The retroflex sector of the vocal
topology is mapped.

Śikṣā confirmation: mūrdhanya class
predicts low F2 and retroflexed tongue.
Measured F2 at 1212 Hz and F3 depression
of 345 Hz confirm Śikṣā classification.

---

#### [ɻ̩ː] — long syllabic retroflex — ॠ
**Śikṣā:** mūrdhanya
**Status:** PENDING

Same formant targets as [ɻ̩].
Duration >= 1.7× [ɻ̩] duration.
Rare in the Rigveda.

---

#### [ḷ] — syllabic lateral approximant — ऌ
**Śikṣā:** dantya (dental)
**Status:** PENDING

Synthesised as a vowel with lateral
approximant formant targets.
Very rare. Appears in specific
grammatical forms only.

---

### VOWELS — LONG MONOPHTHONGS

#### [eː] — long close-mid front — ए
**Śikṣā:** tālavya
**Status:** PENDING

```
VS_EE_F      = [380.0, 2000.0, 2700.0, 3300.0]
VS_EE_B      = [100.0,  140.0,  200.0,  260.0]
VS_EE_GAINS  = [ 14.0,    8.0,    1.5,    0.5]
VS_EE_DUR_MS = 90.0
```

Sanskrit [e] is always long.
No short [e] in the Sanskrit system.

---

#### [oː] — long close-mid back — ओ
**Śikṣā:** kaṇṭhya + oṣṭhya
**Status:** PENDING

```
VS_OO_F      = [380.0,  900.0, 2400.0, 3100.0]
VS_OO_B      = [100.0,  130.0,  200.0,  260.0]
VS_OO_GAINS  = [ 14.0,    8.0,    1.5,    0.5]
VS_OO_DUR_MS = 90.0
```

Sanskrit [o] is always long.
No short [o] in the Sanskrit system.

---

### VOWELS — DIPHTHONGS

#### [ai] — diphthong — ऐ
**Śikṣā:** tālavya
**Status:** PENDING

Synthesised as [a] → [i] trajectory.
Duration: ~120 ms total.
F2 rises from [a] target to [i] target.

---

#### [au] — diphthong — औ
**Śikṣā:** oṣṭhya
**Status:** PENDING

Synthesised as [a] → [u] trajectory.
Duration: ~120 ms total.
F2 falls from [a] target to [u] target.

---

### CONSONANTS — STOPS
### THE FIVE-ROW SYSTEM

Each row: voiceless / voiceless aspirated /
          voiced / voiced aspirated / nasal

---

#### VELAR ROW — kaṇṭhya

##### [k] — voiceless velar stop — क
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```
VS_K_CLOSURE_MS = 35.0
VS_K_BURST_F    = 2500.0
VS_K_BURST_BW   = 1200.0
VS_K_BURST_MS   = 10.0
VS_K_ASPIR_MS   = 0.0     — unaspirated
VS_K_VOT_MS     = 25.0    — long positive VOT
```

---

##### [kʰ] — voiceless velar aspirated — ख
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```
VS_KH_CLOSURE_MS = 35.0
VS_KH_BURST_F    = 2500.0
VS_KH_BURST_MS   = 10.0
VS_KH_ASPIR_MS   = 30.0   — aspiration phase
VS_KH_ASPIR_GAIN = 0.25
```

The aspiration phase: broad-spectrum
turbulent noise, low voicing fraction
(< 0.20), 20–40 ms duration.
This is the primary diagnostic marker
for the aspirated class.

---

##### [g] — voiced velar stop — ग
**Śikṣā:** kaṇṭhya
**Status:** VERIFIED — ṚG
**Date verified:** February 2026
**Diagnostic:** rg_diagnostic.py v1
**Convergence note:** Same vocal topology
position as OE [g] — independently
confirmed in VS context.

```
VS_G_F           = [300.0, 1900.0, 2500.0, 3200.0]
VS_G_B           = [120.0,  200.0,  280.0,  350.0]
VS_G_GAINS       = [ 14.0,    6.0,    1.5,    0.4]
VS_G_CLOSURE_MS  = 30.0
VS_G_BURST_F     = 2500.0
VS_G_BURST_BW    = 1200.0
VS_G_BURST_MS    = 8.0
VS_G_VOT_MS      = 10.0
VS_G_MURMUR_GAIN = 0.70
VS_G_BURST_GAIN  = 0.30
```

Verified values (ṚG context):
- LF ratio (closure): 0.9703 (target >= 0.40)
- Burst centroid: 2403 Hz (target 1800–3200)

---

##### [gʰ] — voiced velar aspirated — घ
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```
VS_GH_CLOSURE_MS = 30.0
VS_GH_BURST_F    = 2500.0
VS_GH_BURST_MS   = 8.0
VS_GH_ASPIR_MS   = 25.0   — aspiration phase
VS_GH_MURMUR_GAIN = 0.60
```

Voiced aspirated: closure is voiced,
aspiration phase has breathy voicing
(voicing fraction 0.20–0.40).
Distinct from voiceless aspirated
(voicing fraction < 0.20 in aspiration).

---

##### [ŋ] — voiced velar nasal — ङ
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```
VS_NG_F       = [280.0, 2200.0, 2800.0, 3200.0]
VS_NG_B       = [120.0,  300.0,  400.0,  400.0]
VS_NG_GAINS   = [  8.0,    2.0,    0.4,    0.2]
VS_NG_DUR_MS  = 60.0
VS_NG_ANTI_F  = 2000.0
VS_NG_ANTI_BW = 300.0
```

---

#### PALATAL ROW — tālavya

##### [c] — voiceless palatal stop — च
**Śikṣā:** tālavya
**Status:** PENDING

Palatal burst: F2 locus ~3000 Hz.
Higher F2 than velar at burst.

---

##### [cʰ] — voiceless palatal aspirated — छ
**Śikṣā:** tālavya
**Status:** PENDING

---

##### [ɟ] — voiced palatal stop — ज
**Śikṣā:** tālavya
**Status:** PENDING

---

##### [ɟʰ] — voiced palatal aspirated — झ
**Śikṣā:** tālavya
**Status:** PENDING

---

##### [ɲ] — voiced palatal nasal — ञ
**Śikṣā:** tālavya
**Status:** PENDING

```
VS_NY_ANTI_F  = 1200.0
VS_NY_ANTI_BW = 250.0
```

---

#### RETROFLEX ROW — mūrdhanya

##### [ʈ] — voiceless retroflex stop — ट
**Śikṣā:** mūrdhanya
**Status:** PENDING

```
VS_TT_BURST_F    = 1500.0   — LOW locus
VS_TT_BURST_BW   = 800.0
VS_TT_F3_NOTCH   = 2200.0   — mūrdhanya marker
VS_TT_F3_NOTCH_BW = 300.0
```

The retroflex stop burst locus is
LOWER than dental (~1800 Hz) because
the tongue tip is retroflexed —
the place of closure is behind
the alveolar ridge.

---

##### [ʈʰ] — voiceless retroflex aspirated — ठ
**Śikṣā:** mūrdhanya
**Status:** PENDING

---

##### [ɖ] — voiced retroflex stop — ड
**Śikṣā:** mūrdhanya
**Status:** PENDING

---

##### [ɖʰ] — voiced retroflex aspirated — ढ
**Śikṣā:** mūrdhanya
**Status:** PENDING

---

##### [ɳ] — voiced retroflex nasal — ण
**Śikṣā:** mūrdhanya
**Status:** PENDING

```
VS_NN_ANTI_F  = 1000.0   — between dental and velar
VS_NN_ANTI_BW = 250.0
VS_NN_F3_NOTCH = 2200.0  — mūrdhanya marker
```

---

#### DENTAL ROW — dantya

##### [t] — voiceless dental stop — त
**Śikṣā:** dantya
**Status:** PENDING

```
VS_T_BURST_F  = 1800.0   — dental locus
VS_T_BURST_BW = 1000.0
VS_T_VOT_MS   = 20.0
```

---

##### [tʰ] — voiceless dental aspirated — थ
**Śikṣā:** dantya
**Status:** PENDING

---

##### [d] — voiced dental stop — द
**Śikṣā:** dantya
**Status:** PENDING

```
VS_D_BURST_F  = 1800.0
VS_D_BURST_BW = 1000.0
```

---

##### [dʰ] — voiced dental aspirated — ध
**Śikṣā:** dantya
**Status:** PENDING

---

##### [n] — voiced dental/alveolar nasal — न
**Śikṣā:** dantya
**Status:** PENDING (AGNI in progress)
**First word target:** AGNI

```
VS_N_F       = [250.0,  900.0, 2000.0, 3000.0]
VS_N_B       = [100.0,  200.0,  300.0,  350.0]
VS_N_GAINS   = [  8.0,    2.5,    0.5,    0.2]
VS_N_DUR_MS  = 60.0
VS_N_ANTI_F  = 800.0
VS_N_ANTI_BW = 200.0
VS_N_COART_ON  = 0.15
VS_N_COART_OFF = 0.15
```

Diagnostic targets:
- Voicing >= 0.50
- Antiresonance ratio < 0.60
  (notch-to-neighbour at ~800 Hz)

---

#### LABIAL ROW — oṣṭhya

##### [p] — voiceless bilabial stop — प
**Śikṣā:** oṣṭhya
**Status:** PENDING

```
VS_P_BURST_F  = 1000.0   — bilabial locus
VS_P_BURST_BW = 800.0
VS_P_VOT_MS   = 20.0
```

---

##### [pʰ] — voiceless bilabial aspirated — फ
**Śikṣā:** oṣṭhya
**Status:** PENDING

---

##### [b] — voiced bilabial stop — ब
**Śikṣā:** oṣṭhya
**Status:** PENDING

---

##### [bʰ] — voiced bilabial aspirated — भ
**Śikṣā:** oṣṭhya
**Status:** PENDING

---

##### [m] — voiced bilabial nasal — म
**Śikṣā:** oṣṭhya
**Status:** PENDING

```
VS_M_F       = [250.0, 1000.0, 2500.0, 3200.0]
VS_M_B       = [100.0,  200.0,  300.0,  350.0]
VS_M_GAINS   = [  8.0,    2.0,    0.5,    0.2]
VS_M_DUR_MS  = 65.0
VS_M_ANTI_F  = 800.0
VS_M_ANTI_BW = 200.0
```

---

### CONSONANTS — SIBILANTS

#### [s] — voiceless dental sibilant — स
**Śikṣā:** dantya
**Status:** PENDING

```
VS_S_NOISE_CF = 5500.0
VS_S_NOISE_BW = 3000.0
VS_S_GAIN     = 0.20
VS_S_DUR_MS   = 80.0
```

---

#### [ɕ] — voiceless palatal sibilant — श
**Śikṣā:** tālavya
**Status:** PENDING

```
VS_SH_NOISE_CF = 3800.0   — lower than [s]
VS_SH_NOISE_BW = 2500.0
VS_SH_GAIN     = 0.22
VS_SH_DUR_MS   = 80.0
```

Palatal sibilant: centre frequency
lower than dental [s] because
palatal constriction produces
a larger resonant cavity ahead
of the constriction.

---

#### [ʂ] — voiceless retroflex sibilant — ष
**Śikṣā:** mūrdhanya
**Status:** PENDING

```
VS_SS_NOISE_CF = 2800.0   — lower than [ɕ]
VS_SS_NOISE_BW = 2000.0
VS_SS_GAIN     = 0.22
VS_SS_DUR_MS   = 85.0
VS_SS_F3_NOTCH = 2200.0   — mūrdhanya marker
```

Retroflex sibilant: the lowest
centre frequency of the three
sibilants. The retroflexion
creates a larger cavity.
The mūrdhanya F3 notch applies.

---

### CONSONANTS — SONORANTS

#### [r] — voiced alveolar trill — र
**Śikṣā:** dantya
**Status:** PENDING

```
VS_R_F       = [450.0, 1700.0, 2700.0, 3300.0]
VS_R_B       = [200.0,  300.0,  350.0,  380.0]
VS_R_GAINS   = [ 10.0,    5.0,    1.5,    0.5]
VS_R_DUR_MS  = 70.0
VS_R_TRILL_RATE_HZ = 25.0
VS_R_CLOSURE_FRAC  = 0.30
```

The trill: periodic AM modulation
at ~25 Hz. Each closure cycle:
brief amplitude reduction as
tongue tip contacts alveolar ridge.
30% of time in closure.

---

#### [l] — voiced alveolar lateral — ल
**Śikṣā:** dantya
**Status:** PENDING

```
VS_L_F       = [350.0, 1100.0, 2700.0, 3300.0]
VS_L_B       = [150.0,  300.0,  350.0,  380.0]
VS_L_GAINS   = [ 10.0,    4.0,    1.5,    0.5]
VS_L_DUR_MS  = 65.0
```

---

#### [j] — voiced palatal approximant — य
**Śikṣā:** tālavya
**Status:** PENDING

```
VS_J_F       = [280.0, 2100.0, 2800.0, 3300.0]
VS_J_B       = [100.0,  200.0,  300.0,  350.0]
VS_J_GAINS   = [ 10.0,    6.0,    1.5,    0.5]
VS_J_DUR_MS  = 55.0
```

---

#### [v] — voiced labio-dental approximant — व
**Śikṣā:** oṣṭhya
**Status:** PENDING

Note: Vedic [v] is typically described
as a labio-dental approximant, not a
fricative as in most modern languages.
Lighter constriction than fricative [v].

```
VS_V_F       = [300.0,  900.0, 2300.0, 3100.0]
VS_V_B       = [200.0,  350.0,  400.0,  400.0]
VS_V_GAINS   = [ 10.0,    5.0,    1.5,    0.5]
VS_V_DUR_MS  = 60.0
VS_V_VOICING_FRAC = 0.60
```

---

#### [h] — voiceless glottal fricative — ह
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```
VS_H_NOISE_CF = 1500.0
VS_H_NOISE_BW = 3000.0
VS_H_GAIN     = 0.15
VS_H_DUR_MS   = 55.0
VS_H_ASPIR_FORMANTS = True   — vowel-colour
```

H is vowel-coloured — the aspiration
noise is filtered through the formants
of the adjacent vowel. Same synthesis
principle as other fricatives but with
glottal source location.

---

### SPECIAL PHONOLOGICAL ELEMENTS

#### Anusvāra — nasalisation — ं
**Status:** PENDING

Not a full nasal consonant.
Nasalisation of the preceding vowel.
Formant targets: nasalised version
of preceding vowel formants.
Additional nasal formant at ~250 Hz.
Antiresonance at frequency determined
by following consonant's place.
Duration: 30–50 ms added to vowel.

---

#### Visarga — voiceless release — ः
**Status:** PENDING

Voiceless h-like fricative at
phrase boundary or before voiceless
consonant. Vowel-coloured aspiration
noise. Short (30–50 ms).

---

## COMPLETE INVENTORY — QUICK REFERENCE

### Verification status by class

| Class | Śikṣā | Verified | Pending | Total |
|---|---|---|---|---|
| Vowels short | various | [ɻ̩] | [a][i][u] + 1 | 4 |
| Vowels long | various | — | [aː][iː][uː][ɻ̩ː] | 4 |
| Diphthongs | various | — | [eː][oː][ai][au] | 4 |
| Velar stops | kaṇṭhya | [g] | [k][kʰ][gʰ][ŋ] | 5 |
| Palatal stops | tālavya | — | [c][cʰ][ɟ][ɟʰ][ɲ] | 5 |
| Retroflex stops | mūrdhanya | — | [ʈ][ʈʰ][ɖ][ɖʰ][ɳ] | 5 |
| Dental stops | dantya | — | [t][tʰ][d][dʰ][n] | 5 |
| Labial stops | oṣṭhya | — | [p][pʰ][b][bʰ][m] | 5 |
| Sibilants | various | — | [s][ɕ][ʂ] | 3 |
| Sonorants | various | — | [r][l][j][v][h] | 5 |
| Special | — | — | anusvāra/visarga | 2 |
| **Total** | | **2** | **~46** | **~48** |

---

## VS VOWEL SPACE — CURRENT STATE

```
Verified or in-progress positions:

F2 (Hz, high = front)
2200  [i] — front close           (PENDING)
1300  [ɻ̩] — retroflex mid         (VERIFIED)
1100  [a] — back open             (PENDING)
 800  [u] — back close            (PENDING)

F1 (Hz, high = open)
 700  [a] — open                  (PENDING)
 420  [ɻ̩] — mid                   (VERIFIED)
 300  [u] — close                 (PENDING)
 280  [i] — close                 (PENDING)
```

The vowel triangle anchors when
[a], [i], and [u] are verified.
[ɻ̩] occupies a unique retroflex
position distinct from all three corners.

---

## OPEN INVENTORY POLICY

This inventory is not closed.

New phonemes are introduced as the
reconstruction encounters them in
the text. Every new phoneme follows
the introduction workflow.

No phoneme is VERIFIED until:
1. The diagnostic script passes
   all numeric checks
2. The ear confirms the perceptual
   result is correct
3. The entry is updated in this
   document with verified values

A phoneme that passes the diagnostic
but fails the ear check is NOT verified.
A phoneme that sounds right but fails
the diagnostic requires investigation —
either the diagnostic is incomplete
or the parameters need adjustment.

Both conditions must be met.
The numbers support the ear.
The ear does not serve the numbers.

---

## NEW PHONEME INTRODUCTION WORKFLOW

When a new phoneme is encountered:

```
1. CLASSIFY
   Assign Śikṣā class.
   Map to articulatory position.
   Predict formant targets from
   Śikṣā classification and physics.

2. ESTIMATE
   Write initial parameter block
   with PENDING status.
   Add to this inventory.

3. SYNTHESISE
   Implement in voice_physics_vs.py.
   Produce isolated output and
   in-word context.

4. DIAGNOSE
   Write diagnostic for the new phoneme.
   Include:
     — Voicing check
     — Formant centroid checks
     — Śikṣā confirmation check
     — VS-internal separation checks
       (once >= 3 VS phonemes verified
        in the relevant dimension)
     — Duration check

5. ITERATE
   If diagnostic fails:
     Identify which check failed.
     Adjust the specific parameter.
     Re-synthesise. Re-run diagnostic.
     Document each iteration.

6. CONFIRM
   When diagnostic passes:
     Run perceptual check.
     Listen. Does it sound correct?
     Does it occupy the right
     room in the vocal topology?

7. VERIFY
   When both diagnostic and ear pass:
     Update status: PENDING → VERIFIED
     Record verified parameter values.
     Record diagnostic values.
     Record first verified word.
     Update COMPLETE INVENTORY table.

8. DOCUMENT
   Write evidence.md for the word.
   The evidence file is the
   permanent record of the verification.
```

---

## LINE STATUS

| Word | IPA | Status | New phonemes |
|---|---|---|---|
| ṚG | [ɻ̩g] | ✓ VERIFIED | [ɻ̩] |
| AGNI | [ɑgni] | ✓ VERIFIED | [ɑ][n][i] |
| ĪḶE | [iːɭe] | ✓ VERIFIED | [iː][ɭ] |
| PUROHITAM | [puroːhitɑm] | IN PROGRESS | [p][oː][h] |
| YAJÑASYA | [jɑdʒɲɑsjɑ] | PENDING | [dʒ][ɲ] |
| DEVAM | [devɑm] | PENDING | [dʰ]→[d][e] |
| ṚTVIJAM | [ɻ̩tvidʒɑm] | PENDING | [ʈ]→[t][dʒ] |
| HOTĀRAM | [hoːtaːrɑm] | PENDING | [ɳ]→hoː |
| RATNADHĀTAMAM | [rɑtnɑdʰaːtɑmɑm] | PENDING | [dʰ] |

---

*February 2026.*
*VS-isolated. Physics first.*
*Every phoneme derived from the instrument.*
*Every value verified VS-internally.*
*The Śikṣā described the space.*
*The physics confirms it.*
*They agree.*
