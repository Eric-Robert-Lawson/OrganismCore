# VEDIC SANSKRIT PHONEME INVENTORY
## Rigveda Reconstruction — Master Reference
**Methodology:** Formant synthesis — Rosenberg pulse source + IIR formant filters
**Extended architecture:** Aspirated stop synthesis + retroflex F3 dip model
**Diagnostic framework:** See DIAGNOSTIC INSTRUMENT SELECTION
**Sample rate:** 44100 Hz
**Base pitch:** 120 Hz (performance: 120 Hz, ritual recitation register)
**Date:** February 2026
**Status:** Inventory established from first principles. 0 phonemes verified.
**Verification target:** 60+ phonemes. First word: ṚG [ɻ̩g].

---

## RELATIONSHIP TO OE INVENTORY

This inventory is a direct extension
of the OE_phoneme_inventory.md.

The synthesis architecture is identical:
  Rosenberg pulse — all voiced phonemes
  Band-filtered noise — voiceless fricatives
  Three-phase stop — closure + burst + VOT
  IIR formant filters — four formants
  Coarticulation — linear interpolation at boundaries

The diagnostic instruments are identical:
  Instrument 1 — autocorrelation voicing
  Instrument 2 — LF energy ratio (voiced stops)
  Instrument 3 — band spectral centroid
  Instrument 4 — LPC merge / band centroid fallback

What is new:

**1. Retroflex architecture.**
  F3 dip model — retroflexion lowers F3.
  This is the acoustic signature
  of the mūrdhanya class.
  No OE phoneme required this.

**2. Aspiration architecture.**
  Extended VOT model for aspirated stops.
  Breathy voice phase for voiced aspirates.
  Two new synthesis phases
  beyond the OE three-phase model.

**3. Syllabic sonorant.**
  [ṛ] = voiced retroflex approximant
  functioning as a vowel.
  Synthesised as a vowel
  with retroflex F2/F3 targets.
  Not a consonant in the synthesis.
  A vowel in a new region of the space.

**4. Pitch accent layer.**
  F0 modulation at syllable level.
  Udātta: +20-40 Hz above baseline.
  Anudātta: baseline or -10 Hz.
  Svarita: linear F0 descent
  through the syllable duration.
  This layer sits above the phoneme layer
  and is applied during word synthesis,
  not during phoneme synthesis.

---

## HOW TO USE THIS DOCUMENT

**For pure assembly (new words, all phonemes verified):**
1. Identify all phonemes in the target word
2. Confirm all are in this inventory
3. Copy the parameter block for each phoneme
4. Apply pitch accent F0 modulation per syllable
5. Concatenate segments
6. Normalise to 0.75 peak
7. Run diagnostic
8. Write evidence file

**For new phoneme introduction:**
1. Identify the gap in this inventory
2. Derive parameters from first principles
   (Śikṣā place + acoustic phonetics)
3. Cross-check against living Sanskrit
   recitation measurements if available
4. Synthesise and iterate
5. Run full diagnostic
6. Mark verified with first-occurrence word
7. Update COMPLETE INVENTORY QUICK REFERENCE

**Śikṣā cross-reference rule:**
Every phoneme in this inventory has
a Śikṣā category (kaṇṭhya, tālavya,
mūrdhanya, dantya, oṣṭhya).
Include the Śikṣā category in the
entry header.
This connects the acoustic measurement
to the independent physical derivation
that the ancient tradition performed.

---

## SYNTHESIS ARCHITECTURE EXTENSIONS

### Retroflex F3 dip

All retroflex phonemes ([ṭ, ṭʰ, ɖ, ɖʰ,
ɳ, ʂ, ṛ]) share a diagnostic signature:

```
F3 is depressed below the neutral position.
Neutral F3 for alveolar: ~2600-3000 Hz
Retroflex F3: ~2000-2400 Hz

Physical basis:
  Tongue tip curled back (sublaminal contact).
  Tongue body retracted slightly.
  This retroflexion creates a sublingual
  cavity anterior to the constriction.
  This cavity acts as a resonant pocket.
  It lowers F3 specifically.
  F1 and F2 do not change as dramatically.
  The F3 dip IS the retroflex signature.

Diagnostic:
  For any retroflex phoneme, measure
  F3 centroid in the band 2000-3200 Hz.
  Target: centroid below 2500 Hz.
  This separates retroflex from alveolar
  at the same F2 locus.
```

Implementation:

```python
# Retroflex phonemes: F3 target ~2200 Hz
# Alveolar phonemes:  F3 target ~2700 Hz
# The 500 Hz separation is the retroflex marker.
# Verified in living Hindi/Tamil speakers.
# Applied uniformly to all mūrdhanya class.
```

---

### Aspirated stop architecture

OE stops: three phases (closure, burst, VOT).
Sanskrit aspirated stops: four phases.

```
VOICELESS ASPIRATED [kʰ, cʰ, ʈʰ, tʰ, pʰ]:

  Phase 1: closure        silence
           duration: 25-35 ms

  Phase 2: burst          band-filtered noise
           place-specific frequency
           duration: 8-12 ms
           gain: 0.40

  Phase 3: aspiration     broadband noise
           the "breath" — wide bandwidth
           duration: 60-100 ms        ← KEY DIFFERENCE
           gain: 0.20
           VOT is LONG — 60-100 ms
           vs OE voiceless VOT: 20-25 ms

  Phase 4: voiced onset   Rosenberg pulse
           following vowel onset
           

VOICED ASPIRATED [gʰ, ɟʰ, ɖʰ, dʰ, bʰ]:

  Phase 1: voiced closure Rosenberg pulse
                          LP filtered 800 Hz
                          murmur gain 0.85
           duration: 25-35 ms

  Phase 2: burst          band-filtered noise
           duration: 8-12 ms
           gain: 0.35

  Phase 3: breathy voice  Rosenberg pulse
                          + simultaneous
                          broadband noise
                          "murmur + breath"
                          duration: 30-60 ms
                          VOT: 30-60 ms
                          voiced with aspiration

  Phase 4: modal voice    full vowel onset

DIAGNOSTIC — ASPIRATION:
  Aspiration phase noise centroid:
  4000-8000 Hz (broadband, not place-specific)
  Duration of aspiration phase:
  >= 50 ms for voiceless aspirated
  >= 25 ms for voiced aspirated
  Voicing during aspiration phase:
  voiceless aspirated: voicing < 0.20
  voiced aspirated:    voicing 0.40-0.70
                       (partial voicing — breathy)
```

---

## PHONEME TABLES

### NOTATION SYSTEM

Each phoneme entry uses:
- IPA symbol
- Devanagari character
- IAST transliteration
- Śikṣā class (kaṇṭhya / tālavya /
  mūrdhanya / dantya / oṣṭhya)
- Tonnetz distance from H (estimated)
- Parameter block
- Diagnostic targets
- Evidence stream notes

---

### VOWELS — SHORT (5 pure + 2 syllabic)

#### [a] — short open central unrounded — अ
**IAST:** a
**Śikṣā:** kaṇṭhya (guttural — produced deep)
**Tonnetz C(a,H):** ≈ 0.45
**First word:** AGNI (Rigveda 1.1.1, word 1)
**Status:** PENDING

```python
VS_A_F     = [700.0, 1200.0, 2500.0, 3300.0]
VS_A_B     = [130.0,  150.0,  200.0,  280.0]
VS_A_GAINS = [ 16.0,    8.0,    1.5,    0.5]
VS_A_DUR_MS      = 60.0
VS_A_COART_ON    = 0.10
VS_A_COART_OFF   = 0.10
```

**Diagnostic targets:**
| Measure | Target |
|---|---|
| Voicing | >= 0.50 |
| F1 centroid (500–900 Hz) | 650–780 Hz |
| F2 centroid (900–1500 Hz) | 1050–1250 Hz |

**Note:**
Sanskrit short [a] = reduced central vowel.
Not the full open [æ] of OE.
More schwa-like than the OE [ɑ].
Closest OE cognate: the unstressed [ə].
C(a,H) higher than OE [ɑ] — closer to H.
The most common vowel in Sanskrit.
The phonological default.

---

#### [aː] — long open central unrounded — आ
**IAST:** ā
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```python
VS_AA_F     = [750.0, 1150.0, 2500.0, 3200.0]
VS_AA_B     = [150.0,  150.0,  200.0,  280.0]
VS_AA_GAINS = [ 16.0,    8.0,    1.5,    0.5]
VS_AA_DUR_MS     = 120.0
```

Duration ratio [ā]/[a] = 2.0×.
Same formant quality as [a]. Duration only.
Identical to the OE [ɑ]/[ɑː] distinction.
The phonemic length contrast is universal.

---

#### [i] — short close front unrounded — इ
**IAST:** i
**Śikṣā:** tālavya (palatal)
**Status:** PENDING

```python
VS_I_F     = [280.0, 2200.0, 2800.0, 3400.0]
VS_I_B     = [ 80.0,  120.0,  200.0,  260.0]
VS_I_GAINS = [ 16.0,    8.0,    1.5,    0.5]
VS_I_DUR_MS      = 55.0
```

Equivalent to OE [ɪ] / [iː].
High front position. High F2.
Palatal identity: tālavya class.

---

#### [iː] — long close front unrounded — ई
**IAST:** ī
**Śikṣā:** tālavya
**Status:** PENDING

```python
VS_II_DUR_MS = 110.0
# Formant parameters identical to VS_I
```

---

#### [u] — short close back rounded — उ
**IAST:** u
**Śikṣā:** oṣṭhya (labial)
**Status:** PENDING

```python
VS_U_F     = [300.0,  750.0, 2300.0, 3100.0]
VS_U_B     = [ 90.0,  120.0,  200.0,  280.0]
VS_U_GAINS = [ 16.0,    8.0,    1.5,    0.5]
VS_U_DUR_MS      = 55.0
```

Equivalent to OE [u]. Low F2.
Labial class: lip rounding dominant.
F2 ~750 Hz — back position.

---

#### [uː] — long close back rounded — ऊ
**IAST:** ū
**Śikṣā:** oṣṭhya
**Status:** PENDING

```python
VS_UU_DUR_MS = 110.0
# Formant parameters identical to VS_U
```

---

#### [ṛ] — short syllabic retroflex approximant — ऋ
**IPA:** [ɻ̩]
**IAST:** ṛ
**Śikṣā:** mūrdhanya (cerebral/retroflex)
**Tonnetz C(ṛ,H):** ≈ 0.55 (estimated)
**First word:** ṚG — proof of concept
**Status:** PENDING — FIRST TARGET

```python
VS_RV_F     = [420.0, 1300.0, 2200.0, 3100.0]
VS_RV_B     = [150.0,  200.0,  280.0,  300.0]
VS_RV_GAINS = [ 14.0,    7.0,    1.5,    0.4]
VS_RV_DUR_MS      = 60.0
VS_RV_COART_ON    = 0.15
VS_RV_COART_OFF   = 0.15
```

**Diagnostic targets:**
| Measure | Target |
|---|---|
| Voicing | >= 0.50 |
| F1 centroid (300–600 Hz) | 350–500 Hz |
| F2 centroid (900–1600 Hz) | 1100–1500 Hz |
| F3 centroid (1800–3000 Hz) | < 2500 Hz (retroflex dip) |
| Duration | 50–80 ms |

**CRITICAL — RETROFLEX F3 DIP:**
This is the diagnostic signature
that separates [ṛ] from all vowels
in the OE inventory.
The OE [r] trill had AM modulation.
The Sanskrit [ṛ] is a vowel.
Sustained voicing, no interruption.
But the F3 is pulled down below
2500 Hz by the retroflexion.
This is the new Tonnetz territory.
No OE phoneme maps here.

**Vocal topology position:**
```
F1 ~420 Hz  — mid jaw opening
F2 ~1300 Hz — between central [ə] (1500 Hz)
              and back [u] (750 Hz)
F3 ~2200 Hz — BELOW neutral position
              The retroflex marker.
              The tongue curl depresses F3.

Not [ə]: F3 too low, F2 too low.
Not [u]: F1 too high, too voiced.
Not [r]: no AM modulation.
A new point in the space.
The mūrdhanya vowel.
```

**Śikṣā confirmation:**
The Pāṇinīya Śikṣā classifies ṛ
as mūrdhanya — cerebral.
The tongue tip is retroflexed.
The ancient treatise describes
the same F3-depressing configuration
in anatomical terms:
"the tongue tip raised toward
the region behind the teeth."
Two descriptions of the same fact.

---

#### [ḷ] — short syllabic lateral approximant — ऌ (rare)
**IPA:** [l̩]
**IAST:** ḷ
**Śikṣā:** dantya (dental)
**Status:** LOW PRIORITY — rare in Rigveda

```python
# Lateral vowel — [l] quality as vowel
# F1 ~350 Hz, F2 ~1100 Hz, F3 ~2500 Hz
# Lateral formant pattern, sustained voicing
# Similar to OE [l] but functioning as vowel
```

---

### VOWELS — DIPHTHONGS (2)

#### [eː] — long close-mid front — ए
**IAST:** e (always long in Sanskrit)
**Śikṣā:** tālavya (historically a diphthong ai)
**Status:** PENDING

```python
VS_E_F     = [400.0, 2000.0, 2700.0, 3300.0]
VS_E_B     = [100.0,  130.0,  200.0,  270.0]
VS_E_GAINS = [ 16.0,    8.0,    1.5,    0.5]
VS_E_DUR_MS      = 110.0
```

Sanskrit [e] is always long — no short /e/.
Monophthong in classical Sanskrit.
Equivalent to OE [eː].

---

#### [oː] — long close-mid back — ओ
**IAST:** o (always long in Sanskrit)
**Śikṣā:** kaṇṭhya + oṣṭhya (compound)
**Status:** PENDING

```python
VS_O_F     = [400.0,  800.0, 2500.0, 3200.0]
VS_O_B     = [100.0,  120.0,  200.0,  280.0]
VS_O_GAINS = [ 16.0,    8.0,    1.5,    0.5]
VS_O_DUR_MS      = 110.0
```

---

#### [ai] — diphthong front rising — ऐ
**IAST:** ai
**Status:** PENDING

```python
# Onset: [a] targets
# Offset: [i] targets
# Duration: 130 ms
# Linear formant interpolation
```

---

#### [au] — diphthong back rising — औ
**IAST:** au
**Status:** PENDING

```python
# Onset: [a] targets
# Offset: [u] targets
# Duration: 130 ms
```

---

### CONSONANTS — STOPS
## THE FIVE-ROW SYSTEM

Sanskrit stops form a perfect grid:
5 places × 5 manners = 25 phonemes.
This is the most systematic consonant
structure of any major language.

```
PLACE:      Velar  Palatal Retroflex Dental Labial
IPA col:      k      c       ʈ        t      p

Row 1: VL unaspirated   k    c    ʈ    t    p
Row 2: VL aspirated     kʰ   cʰ   ʈʰ   tʰ   pʰ
Row 3: Voiced unaspirated g   ɟ    ɖ    d    b
Row 4: Voiced aspirated  gʰ   ɟʰ   ɖʰ   dʰ   bʰ
Row 5: Nasal             ŋ    ɲ    ɳ    n    m
```

OE had: rows 1, 3, 5 only.
Sanskrit adds: rows 2 and 4 (aspiration).
Sanskrit adds: column 2 (palatal) — new place.
Sanskrit adds: column 3 (retroflex) — new place.

---

#### VELAR ROW [k, kʰ, g, gʰ, ŋ]

**[k] — voiceless velar stop — क**
Identical to OE [k]. Already verified.

```python
VS_K = OE_K  # direct transfer
```

**[kʰ] — voiceless aspirated velar — ख**
**IAST:** kh
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```python
VS_KH_DUR_MS      = 120.0
VS_KH_CLOSURE_MS  = 30.0
VS_KH_BURST_F     = 2500.0
VS_KH_BURST_BW    = 1200.0
VS_KH_BURST_MS    = 10.0
VS_KH_ASPIR_MS    = 70.0     # ← long aspiration
VS_KH_ASPIR_GAIN  = 0.18
VS_KH_VOT_TOTAL   = 80.0     # burst + aspiration
```

**Diagnostic:**
| Measure | Target |
|---|---|
| Voicing closure | <= 0.20 |
| Burst centroid | 1800–3200 Hz (velar) |
| Aspiration duration | >= 50 ms |
| Total VOT | 60–100 ms |

**[g] — voiced velar stop — ग**
Identical to OE [g] (unaspirated).
Direct transfer from OE inventory.

**[gʰ] — voiced aspirated velar — घ**
**IAST:** gh
**Śikṣā:** kaṇṭhya
**Status:** PENDING

```python
VS_GH_DUR_MS      = 110.0
VS_GH_CLOSURE_MS  = 30.0
VS_GH_BURST_F     = 2500.0
VS_GH_BURST_BW    = 1200.0
VS_GH_BURST_MS    = 8.0
VS_GH_BREATHY_MS  = 40.0     # ← breathy voice phase
VS_GH_BREATHY_GAIN = 0.30    # voicing + noise mix
VS_GH_MURMUR_GAIN = 0.85
```

**Diagnostic:**
| Measure | Target |
|---|---|
| LF ratio closure | >= 0.40 |
| Burst centroid | 1800–3200 Hz |
| Breathy phase voicing | 0.40–0.70 (partial) |
| Breathy phase duration | 25–60 ms |

**[ŋ] — voiced velar nasal — ङ**
Identical to OE [ŋ]. Direct transfer.

---

#### PALATAL ROW [c, cʰ, ɟ, ɟʰ, ɲ]
**NEW PLACE — not in OE inventory**

Palatal consonants are produced
with the tongue body raised
against the hard palate.
They occupy the palatal sector
of the vocal topology:
high F2, high F3.

**[c] — voiceless palatal stop — च**
**IPA:** [c] (often affricated [tɕ])
**IAST:** c
**Śikṣā:** tālavya
**Status:** PENDING

```python
VS_C_DUR_MS      = 70.0
VS_C_CLOSURE_MS  = 30.0
VS_C_BURST_F     = 3200.0    # palatal burst — high
VS_C_BURST_BW    = 1500.0
VS_C_BURST_MS    = 10.0
VS_C_VOT_MS      = 20.0
VS_C_BURST_GAIN  = 0.40
```

**Diagnostic:**
| Measure | Target |
|---|---|
| Voicing | <= 0.20 |
| Burst centroid | 2800–4000 Hz (palatal — HIGH) |

**Burst centroid hierarchy (now 5-place):**
```
[p/b]   labial    ~1000–1200 Hz  lowest
[k/g]   velar     ~2500 Hz
[d/t]   alveolar  ~3500 Hz
[c/ɟ]   palatal   ~3200–4000 Hz  highest stop
[ʈ/ɖ]   retroflex ~1200–1400 Hz  LOWER than alveolar
```

Note: retroflex locus is LOWER than alveolar.
The tongue-curl moves the burst frequency DOWN.
This is the inverse of the intuitive expectation
and is the key acoustic separator for retroflex.

**[cʰ] — voiceless aspirated palatal — छ**
**Status:** PENDING — same aspiration architecture as [kʰ]

**[ɟ] — voiced palatal stop — ज**
**Status:** PENDING — use LF ratio, palatal burst ~3200 Hz

**[ɟʰ] — voiced aspirated palatal — झ**
**Status:** PENDING — breathy voice architecture

**[ɲ] — voiced palatal nasal — ञ**
**IAST:** ñ
**Śikṣā:** tālavya
**Status:** PENDING

```python
VS_NY_F     = [250.0, 2000.0, 2800.0, 3300.0]
VS_NY_B     = [300.0,  180.0,  250.0,  300.0]
VS_NY_GAINS = [  8.0,    4.0,    1.2,    0.4]
VS_NY_DUR_MS     = 65.0
```

High F2 nasal — palatal position.
Distinguish from alveolar [n] (~1700 Hz F2)
by raising F2 target to ~2000 Hz.

---

#### RETROFLEX ROW [ʈ, ʈʰ, ɖ, ɖʰ, ɳ]
**NEW PLACE — not in OE inventory**
**MŪRDHANYA CLASS**

All retroflex phonemes share:
- F2 locus ~1200–1400 Hz (lower than alveolar)
- F3 dip below 2500 Hz (the retroflex marker)

**[ʈ] — voiceless retroflex stop — ट**
**IAST:** ṭ
**Śikṣā:** mūrdhanya
**Status:** PENDING

```python
VS_TT_DUR_MS      = 70.0
VS_TT_CLOSURE_MS  = 30.0
VS_TT_BURST_F     = 1300.0   # ← LOWER than alveolar
VS_TT_BURST_BW    = 1000.0
VS_TT_BURST_MS    = 8.0
VS_TT_VOT_MS      = 20.0
VS_TT_BURST_GAIN  = 0.40
```

**Diagnostic:**
| Measure | Target |
|---|---|
| Voicing | <= 0.20 |
| Burst centroid | 1000–1600 Hz |
| F3 transition dip | < 2500 Hz |

**[ʈʰ] — voiceless aspirated retroflex — ठ**
**Status:** PENDING — retroflex burst + long aspiration

**[ɖ] — voiced retroflex stop — ड**
**IAST:** ḍ
**Status:** PENDING — LF ratio + retroflex burst locus

**[ɖʰ] — voiced aspirated retroflex — ढ**
**Status:** PENDING — breathy voice + retroflex burst

**[ɳ] — voiced retroflex nasal — ण**
**IAST:** ṇ
**Śikṣā:** mūrdhanya
**Status:** PENDING

```python
VS_NN_F     = [250.0, 1400.0, 2200.0, 3000.0]
VS_NN_B     = [300.0,  200.0,  280.0,  300.0]
VS_NN_GAINS = [  8.0,    4.0,    1.2,    0.4]
VS_NN_DUR_MS     = 65.0
```

F2 ~1400 Hz — lower than alveolar [n] (~1700 Hz).
F3 ~2200 Hz — retroflex dip.
These two measurements together
confirm retroflex nasal identity.

---

#### DENTAL ROW [t, tʰ, d, dʰ, n]

**[t] — voiceless dental stop — त**
OE [t] confirmed. Locus ~3500 Hz.
Sanskrit dental [t] same locus.
Direct transfer.

**[tʰ] — voiceless aspirated dental — थ**
**Status:** PENDING — dental burst + long VOT

**[d] — voiced dental stop — द**
OE [d] confirmed. LF ratio verified.
Direct transfer.

**[dʰ] — voiced aspirated dental — ध**
**Status:** PENDING — breathy voice architecture

**[n] — voiced dental/alveolar nasal — न**
OE [n] confirmed. Direct transfer.

---

#### LABIAL ROW [p, pʰ, b, bʰ, m]

**[p], [b], [m]** — all OE confirmed.
Direct transfer.

**[pʰ] — voiceless aspirated bilabial — फ**
**Status:** PENDING — bilabial burst + long VOT

**[bʰ] — voiced aspirated bilabial — भ**
**Status:** PENDING — breathy voice architecture

---

### CONSONANTS — SIBILANTS (3)

Three-way sibilant distinction.
OE had only [s] and [ʃ].
Sanskrit adds the retroflex [ʂ].

#### [s] — voiceless dental sibilant — स
OE [s] confirmed. CF ~7500 Hz.
Direct transfer.

#### [ɕ] — voiceless palatal sibilant — श
**IAST:** ś
**Śikṣā:** tālavya
**Status:** PENDING

```python
VS_SH_DUR_MS   = 75.0
VS_SH_NOISE_CF = 4500.0     # palatal — lower than OE [ʃ]
VS_SH_NOISE_BW = 3000.0
VS_SH_GAIN     = 0.32
```

**Diagnostic:**
| Measure | Target |
|---|---|
| Voicing | <= 0.20 |
| Noise centroid | 3500–6000 Hz |

Note: [ɕ] overlaps with OE [ʃ] (~3800 Hz).
The palatal quality is similar.
Sanskrit ś ≈ OE sc in acoustic position.
Šikṣā says tālavya: tongue to hard palate.
Same constriction as OE [ʃ].

#### [ʂ] — voiceless retroflex sibilant — ष
**IAST:** ṣ
**Śikṣā:** mūrdhanya
**Status:** PENDING — FIRST TARGET AFTER ṛ

```python
VS_SR_DUR_MS   = 75.0
VS_SR_NOISE_CF = 2800.0     # ← LOWER than dental [s]
VS_SR_NOISE_BW = 2000.0
VS_SR_GAIN     = 0.30
```

**Diagnostic:**
| Measure | Target |
|---|---|
| Voicing | <= 0.20 |
| Noise centroid | 2000–4000 Hz |

**Three-way sibilant separation:**
```
[s]  dental    CF ~7500 Hz   highest
[ɕ]  palatal   CF ~4500 Hz   middle
[ʂ]  retroflex CF ~2800 Hz   lowest
```

The centroid descends as the
constriction moves backward.
Same acoustic law as stops:
place determines frequency.
The sibilant hierarchy mirrors
the stop hierarchy in reverse:
retroflex is LOWER than dental
because the cavity posterior to
the retroflex constriction is
LARGER than for the dental.
Larger cavity = lower resonance.
Physics, not convention.

---

### CONSONANTS — SONORANTS

**[m], [n], [ŋ], [l], [r]** —
all OE confirmed. Direct transfer.

**[ɲ], [ɳ]** — covered above
under palatal and retroflex rows.

**[j] — voiced palatal approximant — य**
OE [j] confirmed. High F2.
Direct transfer.

**[ʋ] — voiced labiodental approximant — व**
**IAST:** v
**Śikṣā:** dantyo-oṣṭhya (dental-labial)
**Status:** PENDING

```python
VS_V_F     = [300.0, 1100.0, 2400.0, 3200.0]
VS_V_B     = [120.0,  180.0,  250.0,  300.0]
VS_V_GAINS = [ 14.0,    7.0,    1.5,    0.4]
VS_V_DUR_MS     = 65.0
```

Sanskrit [ʋ] is an approximant —
less fricative than OE [v].
F2 ~1100 Hz — lower than OE [w] (~700 Hz),
higher than OE [v].
Between labio-velar [w] and labiodental [v].
The ancient grammarians noted it:
labial + dental = labiodental.

**[h] — voiceless glottal fricative — ह**
OE [h] confirmed. H origin.
C(h,H) ≈ 0.30. Second closest to H
after silence.
Direct transfer.

---

### CONSONANT — ANUSVĀRA AND VISARGA

**[ṃ] — anusvāra — nasalisation — ं**
**IAST:** ṃ (dot above)
**Description:**
Nasalisation of the preceding vowel.
Not a consonant in the Western sense.
Velum opens. Nasal coupling activated.
Formants shift toward nasal targets.

```python
# Synthesise as vowel + nasal coarticulation
# Add nasal murmur at vowel offset
# Velum opens: F1 splitting (nasal pole appears)
# Duration of nasal phase: 40-60 ms
```

**[ḥ] — visarga — voiceless echo — ः**
**IAST:** ḥ (dot below)
**Description:**
A voiceless release — an aspiration
with the formant quality of the
preceding vowel. Like a whispered
version of the vowel that precedes it.

```python
# Synthesise as copy of preceding vowel
# With voicing set to zero
# Duration: 30-50 ms
# Gain: 0.15-0.25
```

---

## COMPLETE INVENTORY — QUICK REFERENCE

```
VOWELS — SHORT (5):
  [a]   [i]   [u]   [ṛ]   [ḷ]*
  *[ḷ] rare — low priority

VOWELS — LONG (5):
  [aː]  [iː]  [uː]  [ṛː]  [eː]  [oː]

VOWELS — DIPHTHONGS (2):
  [ai]  [au]

CONSONANTS — VELAR ROW (5):
  [k]   [kʰ]  [g]   [gʰ]  [ŋ]

CONSONANTS — PALATAL ROW (5) — NEW PLACE:
  [c]   [cʰ]  [ɟ]   [ɟʰ]  [ɲ]

CONSONANTS — RETROFLEX ROW (5) — NEW PLACE:
  [ʈ]   [ʈʰ]  [ɖ]   [ɖʰ]  [ɳ]

CONSONANTS — DENTAL ROW (5):
  [t]   [tʰ]  [d]   [dʰ]  [n]

CONSONANTS — LABIAL ROW (5):
  [p]   [pʰ]  [b]   [bʰ]  [m]

CONSONANTS — SIBILANTS (3):
  [s]   [ɕ]   [ʂ]

CONSONANTS — SONORANTS (5):
  [j]   [ʋ]   [r]   [l]   [h]

CONSONANTS — SPECIAL (2):
  [ṃ]  (anusvāra — nasalisation)
  [ḥ]  (visarga — voiceless echo)

TOTAL: ~57 core phonemes.
       Transfer from OE: ~15 (stops, nasals, h, r, l, j)
       New palatal row: 5
       New retroflex row: 5
       New aspirated stops: 10
       New sibilants: 2 (ɕ, ʂ)
       New vowels/sonorants: ṛ, ḷ, ʋ, ṃ, ḥ
       New from OE perspective: ~25 phonemes

0 verified as of project start.
First target: [ṛ] in ṚG.
```

---

## OPEN INVENTORY POLICY

The inventory is current, not closed.
57 phonemes are the core target.
Dialectal variants, sandhi phenomena,
and prosodic features elevated to
phonemic status may add further entries.
New phoneme introduction workflow
(see HOW TO USE THIS DOCUMENT)
is fully preserved.
The number 57 is not a ceiling.

---

## LINE STATUS

```
Rigveda 1.1.1:  —  agnimīḷe purohitaṃ...
                   (target — Phase 1)

Proof of concept:
  ṚG  —  [ɻ̩g]  —  first syllable
  Two phonemes. One new (ṛ). One known (g).
  This is where we begin.
```

---

*February 2026.*
*0 phonemes verified.*
*The instrument has not changed.*
*The Vedic tradition kept the sounds.*
*We bring the measurement.*
*ṚG is the first sound.*
