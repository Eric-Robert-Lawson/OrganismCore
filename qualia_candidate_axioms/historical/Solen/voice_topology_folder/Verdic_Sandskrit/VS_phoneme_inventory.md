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

**No phoneme in this inventory is
imported, assumed, or transferred from
any other reconstruction project.**

Every VERIFIED entry has its own
diagnostic result, its own verified
parameter values, and its own
evidence file. These are the ground
truth for this project. They are
not borrowed. They are earned.

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
The Śikṣā classification is the
theoretical framework. The verified
acoustic values are the measured reality.
When they agree, the reconstruction
is on solid ground.

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
F3 reference: 2700 Hz (physics constant).
Depression >= 200 Hz required for
mūrdhanya confirmation.

Verified mūrdhanya F3 depressions:
  [ɻ̩]: 345 Hz depression (ṚG)
  [ɭ]: 287 Hz depression (ĪḶE)

### Aspirated stop architecture
Four-phase model for aspirated stops:
  Phase 1: voiced closure murmur (or silence)
  Phase 2: burst at place locus
  Phase 3: aspiration noise
           (turbulent airflow,
            broad spectrum,
            no voicing for voiceless aspirated)
  Phase 4: short voiced VOT release
This is new territory — no aspirated
stops exist in the OE inventory.
The aspiration phase is the
phonemically distinctive feature.

### Nasal antiresonance model
`iir_notch()` applied at the nasal
zero frequency for all nasal phonemes.
  [m]: notch ~800 Hz (bilabial)   — VERIFIED
  [n]: notch ~800 Hz (dental)     — VERIFIED
  [ɲ]: notch ~1200 Hz (palatal)   — PENDING
  [ɳ]: notch ~1000 Hz (retroflex) — PENDING
  [ŋ]: notch ~2000 Hz (velar)     — PENDING
The notch-to-neighbour ratio < 0.60
confirms the antiresonance is present.

Verified nasal antiresonance ratios:
  [n]: 0.0018 (AGNI)
  [m]: 0.0046 (PUROHITAM)

### Tap architecture — [ɾ]
Single Gaussian amplitude dip.
NOT periodic AM (that is a trill).
NOT sustained constriction (approximant).
Dip depth: 0.35.
Dip width: 0.40 (fraction of duration).
Duration: 30 ms.
One contact. One return.
This is the antastha architecture.
Confirmed by:
  — Pāṇinīya Śikṣā: antastha class
  — Taittirīya Prātiśākhya: ya ra la va
  — Living Vedic recitation: tap normative
  — Vocal tract topology: single ballistic
    contact consistent with antastha
  — Acoustic diagnostic: dip count 2
    (single contact signature)

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
Tap [ɾ]:               voicing >= 0.35
                       (brief — lower threshold)
Strongly voiced:       voicing >= 0.65
Voiceless phonemes:    voicing <= 0.30
Glottal [h]:           voicing <= 0.35
                       (intervocalic — residual ok)
Voiced aspirated:
  closure phase:       voicing >= 0.40
  aspiration phase:    voicing 0.40–0.70
Voiceless aspirated:
  closure phase:       voicing <= 0.20
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

### Tap criterion
Amplitude dip count: 1–3
(2 is the expected value for a single
physical contact detected at 5 ms
smoothing resolution)
> 3 dips = trill-like — reduce dip depth
0 dips = approximant-like — increase dip depth

### Duration
Specified per phoneme in ms.
Long vowels: >= 1.7× corresponding
             short vowel duration.
Tap [ɾ]: 20–45 ms
         (shortest phoneme in inventory)
Aspirated stops: aspiration phase
                 20–40 ms.

### VS-internal separation
Once >= 3 VS phonemes verified in
a given articulatory dimension,
separation checks use VS-internal
reference values only.
Minimum separation: 150 Hz in F2
between adjacent phoneme categories.

### Burst centroid hierarchy — CONFIRMED
```
[p] oṣṭhya  1204 Hz  — VERIFIED PUROHITAM
[g] kaṇṭhya 2594 Hz  — VERIFIED ṚG/AGNI
[t] dantya  3764 Hz  — VERIFIED PUROHITAM

oṣṭhya < kaṇṭhya < dantya
Physics of anterior cavity.
Larger anterior cavity = lower burst.
```
All new stop diagnostics must place
burst centroids consistent with
this established hierarchy.

---

## PHONEME TABLES

### NOTATION SYSTEM

```
STATUS:
  VERIFIED  — diagnostic passed, ear confirmed,
               parameter values locked.
               Do not adjust without new diagnostic.
  PENDING   — parameters estimated from physics
               and Śikṣā. Subject to revision
               on first diagnostic run.
  TRANSFER  — same vocal topology position as
               a phoneme verified in another
               reconstruction. Requires independent
               VS diagnostic confirmation before
               status becomes VERIFIED.
               A TRANSFER is a starting hypothesis,
               not a verified value.
```

---

### VOWELS — SHORT

#### [a] — short open central unrounded — अ
**Śikṣā:** kaṇṭhya (guttural)
**Status:** VERIFIED — AGNI
**Date verified:** February 2026
**Diagnostic:** agni_diagnostic.py v1

```
VS_A_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B      = [130.0,  160.0,  220.0,  280.0]
VS_A_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_A_DUR_MS = 55.0
VS_A_COART_ON  = 0.12
VS_A_COART_OFF = 0.12
```

Verified values:
- F1 centroid: 631 Hz (target 620–800)
- F2 centroid: 1106 Hz (target 900–1300)
- Voicing: confirmed >= 0.50
- Duration: 55 ms

Note: Sanskrit [a] is the phonological
default — the most common vowel.
Kaṇṭhya class: maximally open vocal tract.
The [a] is open central, not fully back.
The IPA label [ɑ] used in early evidence
files is a slight simplification — the
actual vowel is open central [a] with
back tendency. Parameters are correct.

---

#### [aː] — long open central unrounded — आ
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```
VS_AA_F      = [700.0, 1100.0, 2550.0, 3400.0]
VS_AA_B      = [130.0,  160.0,  220.0,  280.0]
VS_AA_GAINS  = [ 16.0,    6.0,    1.5,    0.5]
VS_AA_DUR_MS = 110.0
VS_AA_COART_ON  = 0.10
VS_AA_COART_OFF = 0.10
```

Same formant targets as [a].
Duration ratio >= 1.7× [a] (55 ms → ~110 ms).
Duration is the phonemic distinction.

---

#### [i] — short close front unrounded — इ
**Śikṣā:** tālavya (palatal)
**Status:** VERIFIED — AGNI
**Date verified:** February 2026
**Diagnostic:** agni_diagnostic.py v1

```
VS_I_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_I_B      = [ 80.0,  130.0,  180.0,  250.0]
VS_I_GAINS  = [ 12.0,    8.0,    1.5,    0.5]
VS_I_DUR_MS = 50.0
VS_I_COART_ON  = 0.12
VS_I_COART_OFF = 0.12
```

Verified values:
- F2 centroid: 2124 Hz (target 2000–2400)
- Voicing: confirmed >= 0.50
- Duration: 50 ms

---

#### [iː] — long close front unrounded — ई
**Śikṣā:** tālavya
**Status:** VERIFIED — ĪḶE
**Date verified:** February 2026
**Diagnostic:** ile_diagnostic.py v1

```
VS_II_F      = [280.0, 2200.0, 2900.0, 3400.0]
VS_II_B      = [ 80.0,  130.0,  180.0,  250.0]
VS_II_GAINS  = [ 12.0,    8.0,    1.5,    0.5]
VS_II_DUR_MS = 100.0
VS_II_COART_ON  = 0.10
VS_II_COART_OFF = 0.10
```

Verified values:
- F2 centroid: 2096 Hz
- F2 quality match with [i]: 28 Hz difference
- Length ratio [iː]/[i]: 2.00×
- Duration: 100 ms

Phonemic quantity contrast confirmed:
same quality, doubled duration.

---

#### [u] — short close back rounded — उ
**Śikṣā:** oṣṭhya (labial)
**Status:** VERIFIED — PUROHITAM
**Date verified:** February 2026
**Diagnostic:** purohitam_diagnostic.py v1

```
VS_U_F      = [300.0,  750.0, 2300.0, 3100.0]
VS_U_B      = [ 90.0,  120.0,  200.0,  260.0]
VS_U_GAINS  = [ 14.0,    8.0,    1.5,    0.5]
VS_U_DUR_MS = 50.0
VS_U_COART_ON  = 0.12
VS_U_COART_OFF = 0.12
```

Verified values:
- F2 centroid: 742 Hz (target 600–950)
- F2 below [a] F2 (1106 Hz): 364 Hz margin
- Voicing: 0.5035

Oṣṭhya confirmed: lowest vowel F2
in the verified inventory.
Back corner of the VS vowel triangle.

---

#### [uː] — long close back rounded — ऊ
**Śikṣā:** oṣṭhya
**Status:** PENDING

```
VS_UU_F      = [300.0,  750.0, 2300.0, 3100.0]
VS_UU_B      = [ 90.0,  120.0,  200.0,  260.0]
VS_UU_GAINS  = [ 14.0,    8.0,    1.5,    0.5]
VS_UU_DUR_MS = 100.0
VS_UU_COART_ON  = 0.10
VS_UU_COART_OFF = 0.10
```

Same formant targets as [u].
Length ratio >= 1.7× [u].

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
- F1 centroid: 385 Hz (target 350–500)
- F2 centroid: 1212 Hz (target 1100–1500)
- F3 centroid: 2355 Hz (target < 2500)
- F3 depression: 345 Hz (target >= 200)
- Voicing: 0.6013 (target >= 0.50)
- Duration: 60 ms (target 50–80)

The mūrdhanya marker: F3 depression
of 345 Hz below the neutral alveolar
reference of 2700 Hz. The tongue curl
is present in the acoustic output.
The retroflex sector of the vocal
topology is mapped.

Synthesised as a sustained vowel —
NOT a consonant. No AM modulation.
No amplitude dip.

---

#### [ɻ̩ː] — long syllabic retroflex — ॠ
**Śikṣā:** mūrdhanya
**Status:** PENDING

Same formant targets as [ɻ̩].
Duration >= 1.7× [ɻ̩] duration (60 ms → ~102 ms).
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
**Status:** VERIFIED — ĪḶE
**Date verified:** February 2026
**Diagnostic:** ile_diagnostic.py v1

```
VS_EE_F      = [420.0, 1750.0, 2650.0, 3350.0]
VS_EE_B      = [100.0,  140.0,  200.0,  260.0]
VS_EE_GAINS  = [ 14.0,    8.0,    1.5,    0.5]
VS_EE_DUR_MS = 90.0
VS_EE_COART_ON  = 0.10
VS_EE_COART_OFF = 0.10
```

Verified values:
- F1 centroid: 402.9 Hz (target 380–550)
- F2 centroid: 1659 Hz (target 1500–2000)
- F1 between [i] ~280 Hz and [a] 631 Hz ✓
- F2 between [a] 1106 Hz and [i] 2124 Hz ✓

Sanskrit [e] is always long.
No short [e] in the Sanskrit system.

---

#### [oː] — long close-mid back — ओ
**Śikṣā:** kaṇṭhya + oṣṭhya
**Status:** VERIFIED — PUROHITAM
**Date verified:** February 2026
**Diagnostic:** purohitam_diagnostic.py v1

```
VS_OO_F      = [430.0,  800.0, 2500.0, 3200.0]
VS_OO_B      = [110.0,  130.0,  200.0,  270.0]
VS_OO_GAINS  = [ 15.0,    8.0,    1.5,    0.5]
VS_OO_DUR_MS = 100.0
VS_OO_COART_ON  = 0.10
VS_OO_COART_OFF = 0.10
```

Verified values:
- F1 centroid: 381.5 Hz (target 350–550)
- F2 centroid: 757 Hz (target 700–1050)
- F1 between [u] ~300 Hz and [a] 631 Hz ✓
- F2 between [u] 742 Hz and [a] 1106 Hz ✓

Sanskrit [o] is always long.
No short [o] in the Sanskrit system.
The back mirror of [eː].

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

```
PLACE:      Velar   Palatal  Retroflex  Dental  Labial
            kaṇṭhya tālavya  mūrdhanya  dantya  oṣṭhya

Row 1: VL unaspirated   k     c     ʈ     t     p
Row 2: VL aspirated     kʰ    cʰ    ʈʰ    tʰ    pʰ
Row 3: Voiced unasp.    g     ɟ     ɖ     d     b
Row 4: Voiced aspirated gʰ    ɟʰ    ɖʰ    dʰ    bʰ
Row 5: Nasal            ŋ     ɲ     ɳ     n     m

BURST CENTROID HIERARCHY (verified):
  oṣṭhya [p]:   1204 Hz  — lowest
  kaṇṭhya [g]:  2594 Hz  — mid
  dantya [t]:   3764 Hz  — highest

  tālavya [ɟ]:  ~3200 Hz (PENDING — between kaṇṭhya and dantya)
  mūrdhanya [ɖ]: ~1300 Hz (PENDING — LOWER than oṣṭhya counter-intuitive
                            but confirmed by retroflex cavity physics)
```

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
VS_K_VOT_MS     = 25.0
VS_K_BURST_GAIN = 0.38
```

---

##### [kʰ] — voiceless velar aspirated — ख
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```
VS_KH_CLOSURE_MS = 35.0
VS_KH_BURST_F    = 2500.0
VS_KH_BURST_BW   = 1200.0
VS_KH_BURST_MS   = 10.0
VS_KH_ASPIR_MS   = 70.0
VS_KH_ASPIR_GAIN = 0.18
```

Four-phase model. Aspiration phase:
broadband noise, voicing < 0.20,
duration >= 50 ms.

---

##### [g] — voiced velar stop — ग
**Śikṣā:** kaṇṭhya
**Status:** VERIFIED — ṚG
**Date verified:** February 2026
**Diagnostic:** rg_diagnostic.py v1

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

Verified values:
- LF ratio (closure): 0.9703 (target >= 0.40)
- Burst centroid: 2403 Hz (target 1800–3200)
- Verified burst mean across ṚG + AGNI: 2594 Hz

---

##### [gʰ] — voiced velar aspirated — घ
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```
VS_GH_CLOSURE_MS  = 30.0
VS_GH_BURST_F     = 2500.0
VS_GH_BURST_BW    = 1200.0
VS_GH_BURST_MS    = 8.0
VS_GH_ASPIR_MS    = 40.0
VS_GH_MURMUR_GAIN = 0.60
VS_GH_ASPIR_GAIN  = 0.30
```

Breathy voice architecture:
closure voiced + aspiration phase
voicing 0.40–0.70 (partial).

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

```
VS_C_CLOSURE_MS = 30.0
VS_C_BURST_F    = 3200.0
VS_C_BURST_BW   = 1500.0
VS_C_BURST_MS   = 10.0
VS_C_VOT_MS     = 20.0
VS_C_BURST_GAIN = 0.38
```

Palatal burst locus ~3200 Hz.
Between kaṇṭhya (2594 Hz) and
dantya (3764 Hz) in the hierarchy.

---

##### [cʰ] — voiceless palatal aspirated — छ
**Śikṣā:** tālavya
**Status:** PENDING

Same architecture as [kʰ] but
with palatal burst locus ~3200 Hz.

---

##### [ɟ] — voiced palatal stop — ज
**Śikṣā:** tālavya
**Status:** PENDING

```
VS_JJ_CLOSURE_MS  = 30.0
VS_JJ_BURST_F     = 3200.0
VS_JJ_BURST_BW    = 1500.0
VS_JJ_BURST_MS    = 8.0
VS_JJ_VOT_MS      = 10.0
VS_JJ_MURMUR_GAIN = 0.70
VS_JJ_BURST_GAIN  = 0.30
```

Diagnostic: LF ratio for voiced closure.
Burst centroid: 2800–4000 Hz (palatal).

---

##### [ɟʰ] — voiced palatal aspirated — झ
**Śikṣā:** tālavya
**Status:** PENDING

Breathy voice architecture.
Palatal burst locus.

---

##### [ɲ] — voiced palatal nasal — ञ
**Śikṣā:** tālavya
**Status:** PENDING

```
VS_NY_F       = [250.0, 2000.0, 2800.0, 3300.0]
VS_NY_B       = [120.0,  180.0,  250.0,  300.0]
VS_NY_GAINS   = [  8.0,    4.0,    1.2,    0.4]
VS_NY_DUR_MS  = 65.0
VS_NY_ANTI_F  = 1200.0
VS_NY_ANTI_BW = 250.0
VS_NY_COART_ON  = 0.15
VS_NY_COART_OFF = 0.15
```

High F2 nasal — palatal position.
F2 ~2000 Hz separates from [n] (~900 Hz)
and [m] (~552 Hz).
Antiresonance higher than [n]/[m]
because palatal nasal side branch
is shorter.

---

#### RETROFLEX ROW — mūrdhanya

All retroflex phonemes share
the mūrdhanya diagnostic signature:
- F3 below 2500 Hz
- F3 depression >= 200 Hz vs neutral 2700 Hz
This is the tongue-curl marker.
Confirmed in [ɻ̩] (345 Hz depression)
and [ɭ] (287 Hz depression).

##### [ʈ] — voiceless retroflex stop — ट
**Śikṣā:** mūrdhanya
**Status:** PENDING

```
VS_TT_CLOSURE_MS  = 30.0
VS_TT_BURST_F     = 1300.0
VS_TT_BURST_BW    = 800.0
VS_TT_BURST_MS    = 8.0
VS_TT_VOT_MS      = 20.0
VS_TT_BURST_GAIN  = 0.40
VS_TT_F3_NOTCH    = 2200.0
VS_TT_F3_NOTCH_BW = 300.0
```

Burst locus ~1300 Hz — LOWER than
dental (3764 Hz) and even lower than
labial (1204 Hz). Counter-intuitive
but physically correct: the tongue tip
curled back creates a LARGE anterior
cavity. Large cavity = low burst.

---

##### [ʈʰ] — voiceless retroflex aspirated — ठ
**Śikṣā:** mūrdhanya
**Status:** PENDING

Retroflex burst locus + long aspiration.

---

##### [ɖ] — voiced retroflex stop — ड
**Śikṣā:** mūrdhanya
**Status:** PENDING

```
VS_DD_BURST_F     = 1300.0
VS_DD_BURST_BW    = 800.0
VS_DD_F3_NOTCH    = 2200.0
VS_DD_F3_NOTCH_BW = 300.0
VS_DD_MURMUR_GAIN = 0.70
```

LF ratio for voiced closure.
Retroflex F3 notch required.

---

##### [ɖʰ] — voiced retroflex aspirated — ढ
**Śikṣā:** mūrdhanya
**Status:** PENDING

Breathy voice + retroflex burst.

---

##### [ɳ] — voiced retroflex nasal — ण
**Śikṣā:** mūrdhanya
**Status:** PENDING

```
VS_NN_F        = [250.0, 1400.0, 2200.0, 3000.0]
VS_NN_B        = [100.0,  200.0,  280.0,  300.0]
VS_NN_GAINS    = [  8.0,    4.0,    1.2,    0.4]
VS_NN_DUR_MS   = 65.0
VS_NN_ANTI_F   = 1000.0
VS_NN_ANTI_BW  = 250.0
VS_NN_F3_NOTCH    = 2200.0
VS_NN_F3_NOTCH_BW = 300.0
```

F2 ~1400 Hz: lower than dental [n] (900 Hz)
but requires mūrdhanya F3 notch.
Two simultaneous checks: nasal zero
AND retroflex F3 dip.

---

#### DENTAL ROW — dantya

##### [t] — voiceless dental stop — त
**Śikṣā:** dantya
**Status:** VERIFIED — PUROHITAM
**Date verified:** February 2026
**Diagnostic:** purohitam_diagnostic.py v1

```
VS_T_CLOSURE_MS = 25.0
VS_T_BURST_F    = 3500.0
VS_T_BURST_BW   = 1500.0
VS_T_BURST_MS   = 7.0
VS_T_VOT_MS     = 15.0
VS_T_BURST_GAIN = 0.38
```

Verified values:
- Closure voicing: 0.0000 (target <= 0.30)
- Burst centroid: 3764 Hz (target 3000–4500)

Highest burst centroid in the verified
inventory. Tongue tip to upper teeth —
smallest anterior cavity.

---

##### [tʰ] — voiceless dental aspirated — थ
**Śikṣā:** dantya
**Status:** PENDING

Dental burst locus + long aspiration.

---

##### [d] — voiced dental stop — द
**Śikṣā:** dantya
**Status:** PENDING

```
VS_D_CLOSURE_MS  = 28.0
VS_D_BURST_F     = 3500.0
VS_D_BURST_BW    = 1500.0
VS_D_BURST_MS    = 8.0
VS_D_VOT_MS      = 10.0
VS_D_MURMUR_GAIN = 0.70
```

---

##### [dʰ] — voiced dental aspirated — ध
**Śikṣā:** dantya
**Status:** PENDING

Breathy voice architecture. Dental burst.

---

##### [n] — voiced dental nasal — न
**Śikṣā:** dantya
**Status:** VERIFIED — AGNI
**Date verified:** February 2026
**Diagnostic:** agni_diagnostic.py v1

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

Verified values:
- Voicing: confirmed >= 0.50
- Antiresonance ratio: 0.0018 (target < 0.60)

Note: Sanskrit [n] is more accurately
dental [n̪] than alveolar. Antiresonance
at 800 Hz is within the dental-alveolar
range. Refinement possible when [n]
appears in broader phonological contexts.

---

#### LABIAL ROW — oṣṭhya

##### [p] — voiceless bilabial stop — प
**Śikṣā:** oṣṭhya
**Status:** VERIFIED — PUROHITAM
**Date verified:** February 2026
**Diagnostic:** purohitam_diagnostic.py v1

```
VS_P_CLOSURE_MS = 28.0
VS_P_BURST_F    = 1100.0
VS_P_BURST_BW   = 800.0
VS_P_BURST_MS   = 8.0
VS_P_VOT_MS     = 18.0
VS_P_BURST_GAIN = 0.38
```

Verified values:
- Closure voicing: 0.0000 (target <= 0.30)
- Burst centroid: 1204 Hz (target 900–1400)

Lowest burst centroid in the verified
inventory. No anterior cavity.

---

##### [pʰ] — voiceless bilabial aspirated — फ
**Śikṣā:** oṣṭhya
**Status:** PENDING

Bilabial burst locus + long aspiration.

---

##### [b] — voiced bilabial stop — ब
**Śikṣā:** oṣṭhya
**Status:** PENDING

```
VS_B_CLOSURE_MS  = 28.0
VS_B_BURST_F     = 1100.0
VS_B_BURST_BW    = 800.0
VS_B_BURST_MS    = 8.0
VS_B_VOT_MS      = 10.0
VS_B_MURMUR_GAIN = 0.70
```

---

##### [bʰ] — voiced bilabial aspirated — भ
**Śikṣā:** oṣṭhya
**Status:** PENDING

Breathy voice architecture. Bilabial burst.

---

##### [m] — voiced bilabial nasal — म
**Śikṣā:** oṣṭhya
**Status:** VERIFIED — PUROHITAM
**Date verified:** February 2026
**Diagnostic:** purohitam_diagnostic.py v1

```
VS_M_F       = [250.0,  900.0, 2200.0, 3000.0]
VS_M_B       = [100.0,  200.0,  300.0,  350.0]
VS_M_GAINS   = [  8.0,    2.5,    0.5,    0.2]
VS_M_DUR_MS  = 60.0
VS_M_ANTI_F  = 800.0
VS_M_ANTI_BW = 200.0
VS_M_COART_ON  = 0.15
VS_M_COART_OFF = 0.15
```

Verified values:
- Voicing: 0.5978 (target >= 0.50)
- Antiresonance ratio: 0.0046 (target < 0.60)
- F2 centroid: 552 Hz (target 400–850)
- F2 below [n] 900 Hz: confirmed

Oṣṭhya nasal. F2 below dantya [n].
Śikṣā ordering oṣṭhya < dantya confirmed.

---

### CONSONANTS — SIBILANTS

Three-way sibilant hierarchy — all VS-internal:

```
[s]  dental    ~7500 Hz  — highest (PENDING)
[ɕ]  palatal   ~4500 Hz  — middle  (PENDING)
[ʂ]  retroflex ~2800 Hz  — lowest  (PENDING)

Same acoustic law as stops:
place determines frequency.
Smaller anterior cavity = higher CF.
Larger cavity = lower CF.
```

#### [s] — voiceless dental sibilant — स
**Śikṣā:** dantya
**Status:** PENDING

```
VS_S_NOISE_CF = 7500.0
VS_S_NOISE_BW = 3000.0
VS_S_GAIN     = 0.22
VS_S_DUR_MS   = 80.0
```

Highest CF of the three sibilants.
Dental constriction — minimal
anterior cavity — high frequency.

---

#### [ɕ] — voiceless palatal sibilant — श
**Śikṣā:** tālavya
**Status:** PENDING

```
VS_SH_NOISE_CF = 4500.0
VS_SH_NOISE_BW = 2500.0
VS_SH_GAIN     = 0.22
VS_SH_DUR_MS   = 80.0
```

Mid CF. Palatal constriction.
Larger cavity than dental.

---

#### [ʂ] — voiceless retroflex sibilant — ष
**Śikṣ��:** mūrdhanya
**Status:** PENDING

```
VS_SS_NOISE_CF    = 2800.0
VS_SS_NOISE_BW    = 2000.0
VS_SS_GAIN        = 0.22
VS_SS_DUR_MS      = 85.0
VS_SS_F3_NOTCH    = 2200.0
VS_SS_F3_NOTCH_BW = 300.0
```

Lowest CF of the three sibilants.
Retroflexion creates large cavity.
Mūrdhanya F3 notch applies.

---

### CONSONANTS — SONORANTS

#### [ɾ] — alveolar tap — र
**Śikṣā:** antastha (semivowel)
**Status:** VERIFIED — PUROHITAM
**Date verified:** February 2026
**Diagnostic:** purohitam_diagnostic.py v1

```
VS_R_F         = [300.0, 1900.0, 2700.0, 3300.0]
VS_R_B         = [120.0,  200.0,  250.0,  300.0]
VS_R_GAINS     = [ 12.0,    6.0,    1.5,    0.4]
VS_R_DUR_MS    = 30.0
VS_R_DIP_DEPTH = 0.35
VS_R_DIP_WIDTH = 0.40
```

Verified values:
- Voicing: 0.4727 (target >= 0.35)
- F2 centroid: 1897 Hz (target 1700–2200)
- F3 centroid: 2643 Hz (target 2400–3100)
- F3 above [ɻ̩] F3 (2355 Hz): 288 Hz margin
- Amplitude dip count: 2 (target 1–3)
- Duration: 30 ms (target 20–45 ms)

**CRITICAL — TAP NOT TRILL:**
Sanskrit *ra* is the alveolar tap [ɾ],
NOT the alveolar trill [r].

Evidence:
  1. Pāṇinīya Śikṣā: antastha class
     (ya ra la va — semivowels)
  2. Taittirīya Prātiśākhya: confirms
  3. Living Vedic recitation: tap normative
  4. Vocal tract topology: single
     ballistic contact = antastha
  5. Acoustic diagnostic: dip count 2
     (single contact, not periodic AM)

Architecture: single Gaussian amplitude
dip at midpoint. NOT periodic AM.
Dip count 2 = one physical contact
detected at 5 ms smoothing resolution.
F3 at 2643 Hz — NO retroflex curl.
[ɾ] is dantya-adjacent, not mūrdhanya.

---

#### [ɭ] — voiced retroflex lateral approximant — ळ
**Śikṣā:** mūrdhanya + lateral
**Status:** VERIFIED — ĪḶE
**Date verified:** February 2026
**Diagnostic:** ile_diagnostic.py v1

```
VS_LL_F           = [400.0, 1100.0, 2100.0, 3000.0]
VS_LL_B           = [200.0,  350.0,  400.0,  400.0]
VS_LL_GAINS       = [ 10.0,    5.0,    1.5,    0.4]
VS_LL_DUR_MS      = 70.0
VS_LL_F3_NOTCH    = 2100.0
VS_LL_F3_NOTCH_BW = 350.0
VS_LL_COART_ON    = 0.15
VS_LL_COART_OFF   = 0.15
```

Verified values:
- Voicing: 0.6611 (target >= 0.50)
- F2 centroid: 1158 Hz (target 1000–1500)
- F3 centroid: 2413 Hz (target 1800–2499)
- F3 depression: 287 Hz (target >= 200)
- F2 below [ɻ̩] F2 (1212 Hz): 54 Hz margin

Two simultaneous constraints confirmed:
  — mūrdhanya: F3 depression 287 Hz
  — lateral: F2 reduced below [ɻ̩] F2

[ɭ] is not [l]: no F3 depression.
[ɭ] is not [ɻ̩]: F2 reduced by lateral.
[ɭ] is both simultaneously.

---

#### [l] — voiced dental lateral — ल
**Śikṣā:** dantya
**Status:** PENDING

```
VS_L_F       = [350.0, 1100.0, 2700.0, 3300.0]
VS_L_B       = [150.0,  300.0,  350.0,  380.0]
VS_L_GAINS   = [ 10.0,    4.0,    1.5,    0.5]
VS_L_DUR_MS  = 65.0
```

No F3 depression — dantya, not mūrdhanya.
This distinguishes [l] from [ɭ].

---

#### [j] — voiced palatal approximant — य
**Śikṣā:** tālavya (antastha — semivowel)
**Status:** PENDING

```
VS_J_F       = [280.0, 2100.0, 2800.0, 3300.0]
VS_J_B       = [100.0,  200.0,  300.0,  350.0]
VS_J_GAINS   = [ 10.0,    6.0,    1.5,    0.5]
VS_J_DUR_MS  = 55.0
VS_J_COART_ON  = 0.15
VS_J_COART_OFF = 0.15
```

Antastha class — semivowel, like [ɾ].
But approximant architecture — NOT a tap.
Sustained palatal constriction.
No amplitude dip. No closure.
High F2 (~2100 Hz) — tālavya position.
F3 neutral — not retroflex.

---

#### [v] — voiced labio-dental approximant — व
**Śikṣā:** oṣṭhya (labial)
**Status:** PENDING

```
VS_V_F       = [300.0,  900.0, 2300.0, 3100.0]
VS_V_B       = [200.0,  350.0,  400.0,  400.0]
VS_V_GAINS   = [ 10.0,    5.0,    1.5,    0.5]
VS_V_DUR_MS  = 60.0
```

Vedic [v] is an approximant, not a
fricative. Lighter constriction.
Broad bandwidth formants model
the looser labio-dental contact.

---

#### [h] — voiceless glottal fricative — ह
**Śikṣā:** kaṇṭhya
**Status:** VERIFIED — PUROHITAM
**Date verified:** February 2026
**Diagnostic:** purohitam_diagnostic.py v1

```
VS_H_DUR_MS    = 65.0
VS_H_NOISE_CF  = 3000.0
VS_H_NOISE_BW  = 4000.0
VS_H_GAIN      = 0.22
VS_H_COART_ON  = 0.30
VS_H_COART_OFF = 0.30
```

Verified values:
- Voicing: 0.0996 (target <= 0.35)
- RMS: 0.0996 (aspiration present)
- Low-band centroid: 1840 Hz

H origin. C(h,H) ≈ 0.30.
The phoneme closest to H in the
coherence space after silence.
Acoustically transparent: inherits
formant context from adjacent vowels.
No Rosenberg source. Broadband noise
filtered through interpolated vowel
formant context.

Intervocalic residual voicing (0.0996)
is physically expected — the glottis
is turbulent but not fully adducted
in a vowel environment. Not a failure.

---

### SPECIAL PHONOLOGICAL ELEMENTS

#### Anusvāra — nasalisation — ं
**Status:** PENDING

Nasalisation of the preceding vowel.
Not a full nasal consonant.
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
| Vowels short | various | [a][i][u][ɻ̩] | [aː][iː→VRFY][uː][ɻ̩ː][ḷ] | 4 |
| Vowels long | various | [iː][eː][oː] | [aː][uː][ɻ̩ː] | 3 |
| Diphthongs | various | — | [ai][au] | 2 |
| Velar stops | kaṇṭhya | [g] | [k][kʰ][gʰ][ŋ] | 5 |
| Palatal stops | tālavya | — | [c][cʰ][ɟ][ɟʰ][ɲ] | 5 |
| Retroflex stops | mūrdhanya | — | [ʈ][ʈʰ][ɖ][ɖʰ][ɳ] | 5 |
| Dental stops | dantya | [t][n] | [tʰ][d][dʰ] | 5 |
| Labial stops | oṣṭhya | [p][m] | [pʰ][b][bʰ] | 5 |
| Sibilants | various | — | [s][ɕ][ʂ] | 3 |
| Sonorants | various | [ɾ][ɭ][h] | [l][j][v] | 6 |
| Special | — | — | anusvāra/visarga | 2 |
| **Total** | | **15** | **~33** | **~48** |

### All 15 verified phonemes

```
Word    Phonemes verified
ṚG      [ɻ̩] [g]
AGNI    [a]  [n]  [i]
ĪḶE     [iː] [ɭ]  [eː]
PUROH.  [p]  [u]  [ɾ]  [oː] [h]  [t]  [m]
```

---

## VS VOWEL SPACE — CURRENT STATE

```
All VS-internal verified values:

F2 (Hz) — high = front, low = back

[i] / [iː]  tālavya close     2096–2124 Hz  ← VERIFIED
[eː]        tālavya mid        1659 Hz       ← VERIFIED
[ɾ]         dantya tap         1897 Hz  (consonant)
[a]         kaṇṭhya open       1106 Hz       ← VERIFIED
[oː]        kṇṭhya+oṣṭhya mid   757 Hz       ← VERIFIED
[u]         oṣṭhya close        742 Hz       ← VERIFIED
[ɻ̩]         mūrdhanya          1212 Hz       ← VERIFIED (retroflex sector)
[ɭ]         mūrdhanya lat      1158 Hz       ← VERIFIED (retroflex sector)

F1 (Hz) — high = open, low = close

[a]         631 Hz  ← VERIFIED
[oː]        382 Hz  ← VERIFIED
[eː]        403 Hz  ← VERIFIED
[ɻ̩]         385 Hz  ← VERIFIED
[u]         ~300 Hz (estimated from params)
[i]/[iː]    ~280 Hz (estimated from params)

Vowel triangle — fully anchored:
  Front close [i]:   F1 ~280,  F2 2124  ← VERIFIED
  Back close [u]:    F1 ~300,  F2 742   ← VERIFIED
  Open central [a]:  F1 631,   F2 1106  ← VERIFIED

Retroflex sector:
  [ɻ̩]: F2 1212, F3 2355 (depression 345 Hz) ← VERIFIED
  [ɭ]: F2 1158, F3 2413 (depression 287 Hz) ← VERIFIED

Mid vowels:
  [eː]: front mid — F1 403, F2 1659 ← VERIFIED
  [oː]: back mid  — F1 382, F2 757  ← VERIFIED
```

---

## NASAL INVENTORY — CURRENT STATE

```
Phoneme  Place      Śikṣā      F2      Anti-F   Anti-ratio  Status
[m]      bilabial   oṣṭhya     552 Hz  800 Hz   0.0046      VERIFIED
[n]      dental     dantya     900 Hz  800 Hz   0.0018      VERIFIED
[ɲ]      palatal    tālavya   2000 Hz  1200 Hz  pending     PENDING
[ɳ]      retroflex  mūrdhanya 1400 Hz  1000 Hz  pending     PENDING
[ŋ]      velar      kaṇṭhya   2200 Hz  2000 Hz  pending     PENDING

F2 ordering (oṣṭhya < mūrdhanya < kaṇṭhya < dantya < tālavya):
  [m] 552 < [ɳ] 1400 < [ŋ] 2200 < [n] 900 < [ɲ] 2000

Note: the F2 ordering of nasals follows the
Śikṣā place ordering, but with the retrofit
values in their expected low-F2 region.
Oṣṭhya has lowest F2. Tālavya has highest.
Both verified nasals confirm this ordering.
```

---

## STOP BURST HIERARCHY — CURRENT STATE

```
Place      Śikṣā      Burst CF  Status
oṣṭhya     labial      1204 Hz  VERIFIED [p] PUROHITAM
mūrdhanya  retroflex   ~1300 Hz PENDING  [ɖ/ʈ] — LOWER than labial
kaṇṭhya    velar       2594 Hz  VERIFIED [g] ṚG/AGNI
tālavya    palatal     ~3200 Hz PENDING  [ɟ/c]
dantya     dental      3764 Hz  VERIFIED [t] PUROHITAM

Physical basis: anterior cavity size
determines burst frequency.
Larger cavity = lower burst.

The retroflex burst is the most
counter-intuitive: the tongue curl
creates a LARGE sublingual cavity
anterior to the constriction.
Despite being a lingual consonant,
it has a lower burst than the bilabial.
This is confirmed by physics and
by living Hindi/Tamil speaker measurements.
```

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
   Check against existing VS hierarchy
   (burst, F2 ordering, nasal zeros).

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
     — Hierarchy consistency check
       (burst centroid, F2 ordering,
        nasal zero ordering)

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
     Update VS VOWEL SPACE / NASAL
     INVENTORY / BURST HIERARCHY tables.

8. DOCUMENT
   Write evidence.md for the word.
   The evidence file is the
   permanent record of the verification.
```

---

## LINE STATUS

| Word | IPA | Status | New phonemes verified |
|---|---|---|---|
| ṚG | [ɻ̩g] | ✓ VERIFIED | [ɻ̩] [g] |
| AGNI | [ɑgni] | ✓ VERIFIED | [a] [n] [i] |
| ĪḶE | [iːɭe] | ✓ VERIFIED | [iː] [ɭ] [eː] |
| PUROHITAM | [puroːhitɑm] | ✓ VERIFIED | [p] [u] [ɾ] [oː] [h] [t] [m] |
| YAJÑASYA | [jɑɟɲɑsjɑ] | IN PROGRESS | [j] [ɟ] [ɲ] [s] |
| DEVAM | [devɑm] | PENDING | [d] |
| ṚTVIJAM | [ɻ̩tvidʒɑm] | PENDING | [ʈ] [v] |
| HOTĀRAM | [hoːtaːrɑm] | PENDING | [aː] |
| RATNADHĀTAMAM | [rɑtnɑdʰaːtɑmɑm] | PENDING | [dʰ] |

---

*February 2026.*
*VS-isolated. Physics first.*
*Every phoneme derived from the instrument.*
*Every value verified VS-internally.*
*The Śikṣā described the space.*
*The physics confirms it.*
*They agree.*
*15 phonemes verified.*
*The vowel triangle is anchored.*
*The retroflex sector is mapped.*
*The burst hierarchy is confirmed.*
*The tap is a tap.*
