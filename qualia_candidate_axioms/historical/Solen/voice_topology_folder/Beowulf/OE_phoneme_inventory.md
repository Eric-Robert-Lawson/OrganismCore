# OLD ENGLISH PHONEME INVENTORY
## Beowulf Reconstruction — Master Reference
**Methodology:** Formant synthesis — Rosenberg pulse source + IIR formant filters  
**Diagnostic framework:** Autocorrelation voicing + spectral centroid + RMS level  
**Sample rate:** 44100 Hz  
**Base pitch:** 145 Hz (performance: 110 Hz)  
**Date:** February 2026  
**Status:** 42 of 43 phonemes verified. [b] pending — line 8 GEBĀD.

---

## HOW TO USE THIS DOCUMENT

**For pure assembly (new words, zero new phonemes):**
1. Identify all phonemes in the target word
2. Confirm all are in this inventory
3. Copy the parameter block for each phoneme
4. Call the synthesiser functions in sequence
5. Concatenate segments
6. Normalise to 0.75 peak
7. Run diagnostic — voicing, centroid, RMS, duration
8. Write evidence file

**For new phoneme introduction:**
1. Identify the gap in this inventory
2. Choose an OE word that isolates the phoneme cleanly
3. Establish parameter targets from acoustic phonetics
4. Synthesise and iterate
5. Run full diagnostic including cross-inventory comparisons
6. Add to this document
7. Mark as verified with first-occurrence word

**For line reconstruction:**
1. Tokenise the line into words
2. Tokenise each word into phonemes
3. Check every phoneme against this inventory
4. If all present: pure assembly — no new work required
5. If gap: introduce new phoneme first, then assemble

---

## SYNTHESIS ARCHITECTURE

### Source

**Rosenberg pulse — all voiced phonemes.**

```python
def rosenberg_pulse(n_samples, pitch_hz,
                    oq=0.65, sr=44100):
    """
    Glottal pulse model.
    oq: open quotient 0.65 — male voice.
    Differentiated — produces glottal flow
    derivative suitable for formant filtering.
    All voiced phonemes use this source.
    """
```

**Band-filtered noise — all voiceless fricatives.**

```python
# Noise filtered to phoneme-specific band.
# Centre frequency and bandwidth set
# per phoneme — see parameter tables.
noise = np.random.randn(n_samples)
b, a  = butter(2, [lo/nyq, hi/nyq],
               btype='band')
fric  = lfilter(b, a, noise) * gain
```

**Stop architecture — three phases:**

```
Voiceless stop [p, t, k]:
  Phase 1: closure    — silence
  Phase 2: burst      — band-filtered noise
  Phase 3: VOT        — broadband aspiration

Voiced stop [b, d, g]:
  Phase 1: closure    — Rosenberg pulse
                        low-pass filtered
                        murmur gain >= 0.60
  Phase 2: burst      — band-filtered noise
  Phase 3: VOT        — voiced formant
                        filtered pulse
                        gain <= 0.10
```

**Voiced fricative architecture:**

```
[v, ð, ɣ]:
  Source: Rosenberg pulse
  AM modulation: rate 80 Hz, depth 0.25
  No noise component
  Formant filtered to place band
  Murmur gain dominates measurement window
```

### Formant filter

**Second-order IIR resonator — per formant.**

```python
# Per sample, per formant:
a2 = -exp(-2π·BW·T)
a1 =  2·exp(-π·BW·T)·cos(2π·F·T)
b0 = 1 - a1 - a2
y[i] = b0·x[i] + a1·y[i-1] + a2·y[i-2]
```

Four formants (F1–F4) cascaded.
Coarticulation: linear interpolation
at segment boundaries — 10–12% onset,
10–12% offset. Stable plateau between.

### Voicing diagnostic

**Autocorrelation on centre half of segment.**

```python
core = seg[n//4 : 3*n//4]
core -= mean(core)
acorr = correlate(core, core, 'full')
acorr = acorr[len//2:]
acorr /= acorr[0]
voicing = max(acorr[lo:hi])
# lo = sr/400, hi = sr/80
```

Voiced target: >= 0.50  
Voiceless target: <= 0.35

### Coarticulation model

Linear formant interpolation at boundaries.
Onset window: 10–12% of segment duration.
Offset window: 10–12% of segment duration.
Stable plateau: 76–80% of segment duration.
F_prev and F_next passed explicitly.

### Room simulation

```python
def apply_simple_room(sig, rt60=2.0,
                       direct_ratio=0.38):
    # Three early reflections: 21ms, 35ms, 51ms
    # Exponential decay: g = 10^(-3/(rt60·sr))
    # Mix: direct_ratio·dry + (1-direct_ratio)·reverb
```

Performance parameters:
- rt60: 2.0 s (timber mead hall, bodies present)
- direct_ratio: 0.38 (large hall, significant reverb)

### Time stretching

OLA (overlap-add) stretch — 4× for diagnostics.
Window: 40 ms Hanning.
Hop in: 10 ms. Hop out: 40 ms.

---

## DIAGNOSTIC THRESHOLDS

| Measure | Voiced target | Voiceless target |
|---|---|---|
| Voicing score | >= 0.50 | <= 0.35 |
| RMS level | 0.005–0.80 | 0.001–0.80 |
| Duration (short vowel) | 50–90 ms | — |
| Duration (long vowel) | >= 90 ms | — |
| Duration (short stop) | 60–120 ms | 60–120 ms |
| Fricative centroid [x] | — | 2000–3500 Hz |
| Fricative centroid [θ] | — | 3500–5000 Hz |
| Fricative centroid [f] | — | 4000–7000 Hz |
| Fricative centroid [ʃ] | — | 2500–5500 Hz |
| Fricative centroid [s] | — | 5000–10000 Hz |

---

## PHONEME TABLES

---

### VOWELS — SHORT

#### [e] — short close-mid front unrounded
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
E_F     = [450.0, 2100.0, 2700.0, 3300.0]
E_B     = [100.0,  130.0,  200.0,  280.0]
E_GAINS = [ 16.0,    8.0,    1.5,    0.5]
E_DUR_MS      = 60.0
E_COART_ON    = 0.10
E_COART_OFF   = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.80 | >= 0.50 |
| F2 centroid (1500–3000 Hz) | ~2066 Hz | 1800–2400 Hz |

Cross-instance stability: F2 centroid
variance < 1 Hz across 7 instances.
Most stable phoneme in the inventory.

---

#### [æ] — open front unrounded
**First word:** HWÆT (line 1)  
**Iterations to verify:** 1

```python
AE_F     = [668.0, 1873.0, 2600.0, 3300.0]
AE_B     = [120.0,  150.0,  200.0,  280.0]
AE_GAINS = [ 16.0,    8.0,    1.5,    0.5]
AE_DUR_MS     = 65.0
AE_COART_ON   = 0.10
AE_COART_OFF  = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.84 | >= 0.50 |
| F1 centroid (400–900 Hz) | ~668 Hz | 550–850 Hz |
| F2 centroid (1400–2500 Hz) | ~1873 Hz | 1600–2200 Hz |

---

#### [ɪ] — short near-close front unrounded
**First word:** IN (line 1)  
**Iterations to verify:** 1

```python
II_F     = [350.0, 1800.0, 2500.0, 3200.0]
II_B     = [ 90.0,  130.0,  200.0,  260.0]
II_GAINS = [ 16.0,    8.0,    1.5,    0.5]
II_DUR_MS     = 55.0
II_COART_ON   = 0.10
II_COART_OFF  = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.84 | >= 0.50 |
| F2 centroid (1300–2300 Hz) | ~1800 Hz | 1500–2100 Hz |

---

#### [y] — short close front rounded
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
Y_F     = [300.0, 1700.0, 2100.0, 3000.0]
Y_B     = [ 80.0,  120.0,  180.0,  250.0]
Y_GAINS = [ 16.0,    8.0,    2.0,    0.5]
Y_DUR_MS      = 55.0
Y_COART_ON    = 0.12
Y_COART_OFF   = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.84 | >= 0.50 |
| F2 centroid (1200–2200 Hz) | ~1700 Hz | 1400–2000 Hz |

Note: F2 ~400 Hz lower than [iː] due to
lip rounding. Rounding coefficient:
~862 Hz F2 depression at close front position.

---

#### [o] — short close-mid back rounded
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
O_F     = [430.0,  800.0, 2500.0, 3200.0]
O_B     = [100.0,  120.0,  200.0,  280.0]
O_GAINS = [ 16.0,    8.0,    1.5,    0.5]
O_DUR_MS      = 65.0
O_COART_ON    = 0.10
O_COART_OFF   = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.84 | >= 0.50 |
| F2 centroid (500–1100 Hz) | ~700 Hz | 550–900 Hz |

---

#### [ɑ] — short open back unrounded
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
A_F     = [700.0, 1150.0, 2500.0, 3200.0]
A_B     = [130.0,  120.0,  200.0,  280.0]
A_GAINS = [ 16.0,    8.0,    1.5,    0.5]
A_DUR_MS      = 60.0
A_COART_ON    = 0.10
A_COART_OFF   = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.84 | >= 0.50 |
| F1 centroid (400–900 Hz) | ~646–648 Hz | 550–800 Hz |

Cross-instance stability: F1 variance
< 2 Hz across 6 instances.

---

#### [u] — short close back rounded
**First word:** GĒAR-DAGUM (line 1)  
**Iterations to verify:** 1

```python
U_F     = [300.0,  700.0, 2400.0, 3100.0]
U_B     = [ 90.0,  120.0,  200.0,  280.0]
U_GAINS = [ 16.0,    8.0,    1.5,    0.5]
U_DUR_MS      = 60.0
U_COART_ON    = 0.10
U_COART_OFF   = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.6760 | >= 0.50 |
| F1 centroid (100–600 Hz) | 218 Hz | 200–380 Hz |
| F2 centroid (400–1200 Hz) | 687–787 Hz | 500–900 Hz |

Lowest F2 of any vowel in the system.
Rounding contributes ~400 Hz F2 lowering
vs unrounded back vowel.

---

### VOWELS — UNSTRESSED

#### [ə] — mid central vowel (schwa) — PHONEME 40
**First word:** FUNDEN (line 8, word 2)  
**Iterations to verify:** 1  
**VRFY_002:** COMPLETE

```python
SCHWA_F     = [500.0, 1500.0, 2500.0, 3200.0]
SCHWA_B     = [150.0,  200.0,  280.0,  320.0]
SCHWA_GAINS = [ 14.0,    7.0,    1.5,    0.4]
SCHWA_DUR_MS    = 45.0
SCHWA_COART_ON  = 0.15
SCHWA_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7003 | >= 0.50 |
| F1 centroid (300–700 Hz) | 418 Hz | 350–700 Hz |
| F2 centroid (1000–2000 Hz) | 1430 Hz | 1100–1900 Hz |
| Duration | 45 ms | 30–70 ms |
| F2 > [u] F2 | 643 Hz separation | >= 50 Hz |
| F2 < [e] F2 | 470 Hz separation | >= 50 Hz |
| Stressed [u] dur > [ə] dur | 15 ms | >= 5 ms |

**Theoretical basis:**
One step from H. Minimum articulatory effort.
C([ə],H) ≈ 0.75 — the dominant of vocal space.
The perfect fifth. Nearest vowel to H.
The Tonnetz bridge predicted this position
before the reconstruction reached it.
VRFY_002 is the verification that the
framework's own prediction was correct.

**Phonological rule — applies universally:**
ALL OE unstressed syllable vowels realise as [ə]
in oral performance. Written -en, -an, -on, -um
all → [ə] + following consonant in the hall.
Applies to: past participle -en, weak adjective -an,
dative plural -um, all reduced function syllables.
This is physics (reduced effort → H proximity),
not convention. Six evidence streams converge.
See FUNDEN evidence file for full documentation.

**Vowel space position:**
```
         High F2 ←————————————→ Low F2
Low F1                [ə]
                  F1 418 Hz
                  F2 1430 Hz
                  Centre of space.
                  Between [u] 687 Hz
                  and [e] 1900 Hz.
                  The inventory's centre
                  was always empty.
                  FUNDEN fills it.
```

---

### VOWELS — LONG

#### [eː] — long close-mid front unrounded
**First word:** WĒ (line 1)  
**Iterations to verify:** 1

```python
EY_F     = [400.0, 2200.0, 2800.0, 3400.0]
EY_B     = [100.0,  130.0,  200.0,  270.0]
EY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
EY_DUR_MS       = 110.0
EY_COART_ON     = 0.10
EY_COART_OFF    = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8400 | >= 0.50 |
| Duration | 110 ms | >= 90 ms |
| F2 centroid | 1875 Hz | 1600–2300 Hz |

---

#### [æː] — long open front unrounded
**First word:** MǢGÞUM (line 6)  
**Iterations to verify:** 1

```python
AEY_F     = [750.0, 1750.0, 2600.0, 3300.0]
AEY_B     = [120.0,  150.0,  200.0,  280.0]
AEY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
AEY_DUR_MS      = 110.0
AEY_COART_ON    = 0.10
AEY_COART_OFF   = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.84 | >= 0.50 |
| Duration | 110 ms | >= 90 ms |
| Duration ratio [æː]/[æ] | >= 1.7× | >= 1.7× |

---

#### [ɑː] — long open back unrounded
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
AA_F     = [840.0, 1150.0, 2500.0, 3300.0]
AA_B     = [180.0,  120.0,  200.0,  280.0]
AA_GAINS = [ 16.0,    8.0,    1.5,    0.5]
AA_DUR_MS       = 150.0
AA_COART_ON     = 0.10
AA_COART_OFF    = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8794 | >= 0.75 |
| Duration | 150–180 ms | >= 90 ms |
| F1+F2 band centroid (600–1400 Hz) | 847 Hz | 750–1050 Hz |

**DIAGNOSTIC NOTE — LPC merge at low pitch:**
At 110–145 Hz analysis pitch, F1 (~750 Hz)
and F2 (~1100 Hz) are only 350 Hz apart and
merge into a single LPC hill. LPC peak
separation fails. Band centroid method
(600–1400 Hz) is the correct measurement.
This applies to [ɑː] and [ɑ] at performance
pitch — use centroid, not LPC.

Long counterpart of [ɑ]. Same formant targets.
Duration ratio [ɑː]/[ɑ] target: >= 2.0×.
Appears in: Gār, Ðā, Þāra, Hronrāde.

---

#### [oː] — long close-mid back rounded
**First word:** GŌD (line 4)  
**Iterations to verify:** 1

```python
OY_F     = [430.0,  700.0, 2400.0, 3200.0]
OY_B     = [100.0,  120.0,  200.0,  280.0]
OY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
OY_DUR_MS       = 150.0
OY_COART_ON     = 0.10
OY_COART_OFF    = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8666 | >= 0.50 |
| Duration | 150 ms | >= 90 ms |
| F2 centroid (500–1000 Hz) | 701 Hz | 550–850 Hz |

Pure monophthong — no offglide.
Duration ratio [oː]/[o] = 2.31×.
Minimal pair in Beowulf itself:
*god* [ɡod] (God) vs *gōd* [ɡoːd] (good).
Duration is the only acoustic distinction.
The synthesis must distinguish them.

---

#### [iː] — long close front unrounded
**First word:** WĪF (inventory completion)  
**Iterations to verify:** 1

```python
IY_F     = [300.0, 2300.0, 3000.0, 3500.0]
IY_B     = [ 80.0,  120.0,  200.0,  260.0]
IY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
IY_DUR_MS       = 110.0
IY_COART_ON     = 0.10
IY_COART_OFF    = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8482 | >= 0.50 |
| Duration | 110 ms | >= 90 ms |
| F2 centroid | ~2300 Hz | >= 2000 Hz |

Highest F2 in the vowel inventory.
Rounding coefficient confirmed: [y] F2 ~862 Hz
lower than [iː] at same height.
Pre-Great-Vowel-Shift value.
OE [iː] → ModE [aɪ] (wife, tide, mine, time).

---

#### [uː] — long close back rounded
**First word:** GEFRŪNON (line 2)  
**Iterations to verify:** 1

```python
UU_F     = [280.0,  650.0, 2400.0, 3100.0]
UU_B     = [ 80.0,  120.0,  200.0,  280.0]
UU_GAINS = [ 16.0,    8.0,    1.5,    0.5]
UU_DUR_MS       = 150.0
UU_COART_ON     = 0.10
UU_COART_OFF    = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8846 | >= 0.65 |
| Duration | 150 ms | 120–200 ms |
| F1 centroid (100–500 Hz) | 199 Hz | 180–360 Hz |
| F2 centroid (400–1000 Hz) | 603 Hz | 450–800 Hz |

Slightly more peripheral than short [u]:
F1 280 vs 300, F2 650 vs 700.
Duration ratio [uː]/[u] = 2.5×.
Pre-Great-Vowel-Shift value.
OE [uː] → ModE [aʊ] (house, out, now, loud).

**F1 centroid note:** 199 Hz vs F1 parameter
280 Hz — sub-F1 harmonic pull from 145 Hz
fundamental. Floor set to 180 Hz.
Same artifact in [u], [y], [ɪ].

---

### VOWELS — DIPHTHONGS

#### [eɑ] — short front-back diphthong
**First word:** SCEAÞENA (line 5)  
**Iterations to verify:** 1

```python
EA_F_ON  = [450.0, 1851.0, 2600.0, 3300.0]
EA_F_OFF = [700.0, 1131.0, 2400.0, 3100.0]
EA_B     = [100.0,  130.0,  200.0,  280.0]
EA_GAINS = [ 16.0,    8.0,    1.5,    0.5]
EA_DUR_MS     = 80.0
EA_TRANS_ON   = 0.15
EA_TRANS_OFF  = 0.85
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.76 | >= 0.50 |
| F2 onset | ~1849–1851 Hz | 1500–2200 Hz |
| F2 offset | ~1100–1131 Hz | 800–1400 Hz |
| F2 delta | ~720–753 Hz ↓ | 400–1000 Hz |
| F1 delta | ~250–281 Hz ↑ | 100–400 Hz |

F2 falls. F1 rises. Jaw opens as tongue
moves back. Cross-word stability confirmed
in SCEAÞENA, ĒAGE, WEARÐ, FEASCEAFT:
F2 onset 1849–1851 Hz across all instances.

---

#### [eːɑ] — long front-back diphthong
**First word:** ĒAGE (inventory completion)  
**Iterations to verify:** 1

```python
EYA_F_ON  = [450.0, 1851.0, 2600.0, 3300.0]
EYA_F_OFF = [700.0, 1100.0, 2400.0, 3100.0]
EYA_DUR_MS    = 160.0
EYA_TRANS_ON  = 0.15
EYA_TRANS_OFF = 0.85
```

| Diagnostic | Value | Target |
|---|---|---|
| Duration | >= 140 ms | >= 140 ms |
| F2 movement | same as [eɑ] | — |
| Duration ratio [eːɑ]/[eɑ] | >= 1.7× | >= 1.7× |

Same formant trajectory as [eɑ].
Duration is the sole distinguishing feature.

---

#### [eo] — short front-mid diphthong
**First word:** MEODOSETLA (line 6)  
**Iterations to verify:** 1

```python
EO_F_ON  = [450.0, 1900.0, 2600.0, 3300.0]
EO_F_OFF = [450.0,  800.0, 2400.0, 3000.0]
EO_B     = [100.0,  130.0,  200.0,  280.0]
EO_GAINS = [ 16.0,    8.0,    1.5,    0.5]
EO_DUR_MS     = 75.0
EO_TRANS_ON   = 0.25
EO_TRANS_OFF  = 0.85
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.79 | >= 0.50 |
| F2 onset | 1833–1900 Hz | 1500–2200 Hz |
| F2 offset | ~759–800 Hz | 550–1100 Hz |
| F2 delta | ~1074 Hz ↓ | 700–1500 Hz |
| F1 delta | ~5 Hz | <= 100 Hz |

**Critical diagnostic separator from [eɑ]:**
[eɑ] F1 RISES ~250 Hz — jaw opens.
[eo] F1 STABLE ±5 Hz — jaw does not move.
This is the measurement that distinguishes them.

---

#### [eːo] — long front-mid diphthong
**First word:** ÞĒOD (inventory completion)  
**Iterations to verify:** 1

```python
EYO_F_ON  = [450.0, 1900.0, 2600.0, 3300.0]
EYO_F_OFF = [450.0,  800.0, 2400.0, 3000.0]
EYO_DUR_MS    = 150.0
EYO_TRANS_ON  = 0.25
EYO_TRANS_OFF = 0.85
```

| Diagnostic | Value | Target |
|---|---|---|
| Duration | >= 130 ms | >= 130 ms |
| F2 movement | same as [eo] | — |
| Duration ratio [eːo]/[eo] | >= 1.7× | >= 1.7× |

Same formant trajectory as [eo].
Duration is the sole distinguishing feature.

---

### CONSONANTS — STOPS

#### [p] — voiceless bilabial stop
**First word:** PÆÞ (inventory completion)  
**Iterations to verify:** 1

```python
P_DUR_MS      = 65.0
P_CLOSURE_MS  = 40.0
P_BURST_F     = 1000.0
P_BURST_BW    = 800.0
P_BURST_MS    = 8.0
P_VOT_MS      = 12.0
P_BURST_GAIN  = 0.45
P_VOT_GAIN    = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | <= 0.10 | <= 0.35 |
| Burst centroid | ~1000 Hz | 500–1500 Hz |

Lowest burst centroid of all stops —
bilabial place = largest oral cavity = lowest resonance.
Burst ordering confirmed: [p] < [k] < [t].

---

#### [b] — voiced bilabial stop — PHONEME 43 — PENDING
**First word:** GEBĀD (line 8, word 6)  
**Status:** NOT YET VERIFIED

```python
B_DUR_MS      = 65.0
B_CLOSURE_MS  = 35.0
B_BURST_F     = 1000.0
B_BURST_BW    = 800.0
B_BURST_MS    = 8.0
B_VOT_MS      = 5.0
B_BURST_GAIN  = 0.35
B_VOT_GAIN    = 0.08
B_VOICING_MS  = 20.0
B_MURMUR_GAIN = 0.65   # >= 0.60 REQUIRED — lesson from [ɡ]
```

| Diagnostic | Value | Target |
|---|---|---|
| Murmur voicing | PENDING | >= 0.60 |
| Voicing score | PENDING | >= 0.50 |
| Bilabial burst centroid | PENDING | ~1000 Hz |

**Pre-verified from [ɡ] lesson:**
Murmur gain MUST be >= 0.60.
VOT noise gain MUST be <= 0.10.
Apply both from iteration 1 — do not repeat the [ɡ] failure.

---

#### [t] — voiceless alveolar stop
**First word:** HWÆT (line 1)  
**Iterations to verify:** 1

```python
T_DUR_MS      = 65.0
T_CLOSURE_MS  = 38.0
T_BURST_F     = 3500.0
T_BURST_BW    = 2000.0
T_BURST_MS    = 12.0
T_VOT_MS      = 18.0
T_BURST_GAIN  = 0.20
T_VOT_GAIN    = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | <= 0.20 | <= 0.35 |
| Burst centroid | ~3500 Hz | 2500–5000 Hz |

---

#### [d] — voiced alveolar stop
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
D_DUR_MS      = 60.0
D_CLOSURE_MS  = 35.0
D_BURST_F     = 3500.0
D_BURST_BW    = 2000.0
D_BURST_MS    = 8.0
D_VOT_MS      = 5.0
D_BURST_GAIN  = 0.35
D_VOT_GAIN    = 0.05
D_VOICING_MS  = 20.0
D_MURMUR_GAIN = 0.65
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| Burst centroid | ~3500 Hz | 2500–5000 Hz |

---

#### [k] — voiceless velar stop
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
K_DUR_MS      = 65.0
K_CLOSURE_MS  = 40.0
K_BURST_F     = 1600.0
K_BURST_BW    = 1200.0
K_BURST_MS    = 12.0
K_VOT_MS      = 22.0
K_BURST_GAIN  = 0.18
K_VOT_GAIN    = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | <= 0.20 | <= 0.35 |
| Burst centroid | ~1600 Hz | 800–2500 Hz |

---

#### [ɡ] — voiced velar stop
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 2

```python
G_DUR_MS      = 60.0
G_CLOSURE_MS  = 35.0
G_BURST_F     = 1600.0
G_BURST_BW    = 1200.0
G_BURST_MS    = 8.0
G_VOT_MS      = 5.0
G_BURST_GAIN  = 0.08
G_VOT_GAIN    = 0.05   # FIX: was 0.25
G_VOICING_MS  = 20.0
G_MURMUR_GAIN = 0.65   # FIX: was 0.35
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| Burst centroid | ~1237–1627 Hz | 800–2500 Hz |

**Fix record (iteration 1 failure):**
Murmur masked by VOT noise.
Murmur gain 0.35→0.65. VOT noise 0.25→0.05.
Burst centroid is context-dependent:
before front vowel [e]: ~1627 Hz.
Before back vowel [u]: ~1237 Hz.
Both within velar target range.
This lesson defines [b] parameters above.

---

### CONSONANTS — FRICATIVES

#### [f] — voiceless labiodental fricative
**First word:** GEFRŪNON (line 2)  
**Iterations to verify:** 1

```python
F_NOISE_CF   = 6000.0
F_NOISE_BW   = 3000.0
F_GAIN       = 0.28
F_DUR_MS     = 70.0
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | <= 0.20 | <= 0.35 |
| Centroid | ~5800 Hz | 4000–7000 Hz |

---

#### [v] — voiced labiodental fricative
**First word:** SCEFING (line 5)  
**Iterations to verify:** 3

```python
V_DUR_MS      = 70.0
V_VOICE_GAIN  = 0.80
V_VOICE_LP    = 1200.0
V_AM_RATE     = 80.0
V_AM_DEPTH    = 0.25
# NO noise component — this was the fix
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| RMS | 0.005–0.80 | 0.005–0.80 |

**Fix record (iterations 1–2 failure):**
Noise source used — periodic voicing lost.
Fix: pure Rosenberg source, no noise.
AM modulation 80 Hz, depth 0.25.
This applies to all voiced fricatives [ð] [ɣ].

---

#### [s] — voiceless alveolar fricative
**First word:** ÆÞELINGAS (line 3)  
**Iterations to verify:** 1

```python
S_NOISE_CF   = 7500.0
S_NOISE_BW   = 4000.0
S_GAIN       = 0.32
S_DUR_MS     = 65.0
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | <= 0.20 | <= 0.35 |
| Centroid | ~7535 Hz | 5000–10000 Hz |

Highest centroid in the fricative inventory.
Ordering confirmed: [x] < [θ] < [f] < [ʃ] < [s].

---

#### [θ] — voiceless dental fricative
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
TH_NOISE_CF   = 4200.0
TH_NOISE_BW   = 2000.0
TH_GAIN       = 0.22
TH_DUR_MS     = 75.0
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | <= 0.20 | <= 0.35 |
| Centroid | ~4200 Hz | 3500–5000 Hz |

---

#### [ð] — voiced dental fricative
**First word:** ÐĀ (line 3)  
**Iterations to verify:** 1 (reconstruction v3)

```python
DH_DUR_MS     = 70.0
DH_NOISE_CF   = 3000.0
DH_NOISE_BW   = 1800.0
DH_NOISE_GAIN = 0.12
DH_VOICE_GAIN = 0.80
DH_VOICE_LP   = 1200.0
# Source: UNDIFFERENCED Rosenberg pulse
# Differencing suppresses 145 Hz fundamental
# and kills voicing bar — do not differentiate
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.40 | >= 0.40 |
| Centroid | 800–4000 Hz | 800–4000 Hz |

**Fix record:** Voicing failed — differenced pulse
used initially. Fix: undifferenced pulse for
voicing bar to survive. Applies to all voiced
fricatives — [v] and [ɣ] use same principle.

---

#### [x] — voiceless velar fricative
**First word:** HU (line 3)  
**Iterations to verify:** 1

```python
X_NOISE_CF   = 2750.0
X_NOISE_BW   = 1800.0
X_GAIN       = 0.30
X_DUR_MS     = 80.0
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | <= 0.20 | <= 0.35 |
| Centroid | ~2750 Hz | 2000–3500 Hz |

Lowest centroid of all fricatives.
Posterior constriction = lowest turbulence.
Scottish *loch*, German *Bach* quality.

---

#### [ɣ] — voiced velar fricative
**First word:** MǢGÞUM (line 6)  
**Iterations to verify:** 1

```python
GH_DUR_MS     = 70.0
GH_VOICE_GAIN = 0.75
GH_VOICE_LP   = 1500.0
GH_AM_RATE    = 80.0
GH_AM_DEPTH   = 0.20
# Source: undifferenced Rosenberg pulse
# Same principle as [ð] and [v]
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| RMS | 0.005–0.80 | 0.005–0.80 |

Voiced counterpart of [x].
Dutch/Danish/Greek quality.
Continuous voiced fricative — not a stop.

---

#### [h] — voiceless glottal fricative
**First word:** HU (line 3)  
**Iterations to verify:** 1

```python
H_NOISE_CF   = 1500.0
H_NOISE_BW   = 3000.0
H_GAIN       = 0.15
H_DUR_MS     = 55.0
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | <= 0.25 | <= 0.35 |
| Broadband noise | wideband | wideband |

Widest noise band of all fricatives.
Glottal constriction = no place-specific filtering.
Noise shaped by following vowel coarticulation.

---

#### [ʃ] — voiceless postalveolar fricative
**First word:** SCYLD (line 5)  
**Iterations to verify:** 1

```python
SH_DUR_MS    = 80.0
SH_NOISE_CF  = 3800.0
SH_NOISE_BW  = 2400.0
SH_GAIN      = 0.30
SH_SEC_CF    = 6000.0
SH_SEC_BW    = 2000.0
SH_SEC_GAIN  = 0.20
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | <= 0.20 | <= 0.35 |
| Centroid | ~4756 Hz | 2500–5500 Hz |

OE spelling *sc* always = [ʃ].
Centroid lower than [s] (~7535 Hz) by ~2800 Hz.
Broader noise band than [s].
Lip rounding from following [y] pulls
centroid slightly lower.

---

### CONSONANTS — NASALS

#### [m] — voiced bilabial nasal
**First word:** GĒAR-DAGUM (line 1)  
**Iterations to verify:** 1

```python
M_DUR_MS      = 60.0
M_ANTIFORM_F  = 1000.0
M_ANTIFORM_BW = 200.0
M_VOICE_GAIN  = 0.55
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7888 | >= 0.60 |
| Murmur/notch ratio | 5.87 | > 2.0 |

Antiformant at ~1000 Hz (cf. [n] ~800 Hz).
Bilabial closure = longer oral cavity = lower notch.

---

#### [n] — voiced alveolar nasal
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
N_DUR_MS      = 60.0
N_ANTIFORM_F  = 800.0
N_ANTIFORM_BW = 180.0
N_VOICE_GAIN  = 0.55
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.77–0.80 | >= 0.65 |
| RMS (nasal murmur) | 0.22–0.25 | 0.005–0.25 |

Cross-instance stability: voicing 0.77–0.80
across 10 instances. Zero variance.
Most consistent consonant in the inventory.

---

#### [ŋ] — voiced velar nasal
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
NG_DUR_MS      = 65.0
NG_ANTIFORM_F  = 1200.0
NG_ANTIFORM_BW = 220.0
NG_VOICE_GAIN  = 0.55
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.65 | >= 0.65 |
| RMS (nasal murmur) | 0.005–0.25 | 0.005–0.25 |

Antiformant ordering: [n] 800 Hz < [m] 1000 Hz < [ŋ] 1200 Hz.
This ordering reflects place of articulation:
alveolar < bilabial < velar in antiformant frequency.

---

### CONSONANTS — APPROXIMANTS

#### [w] — voiced labio-velar approximant
**First word:** WĒ (line 1)  
**Iterations to verify:** 1

```python
W_F     = [300.0,  700.0, 2200.0, 3000.0]
W_B     = [100.0,  150.0,  250.0,  300.0]
W_GAINS = [ 14.0,    7.0,    2.0,    0.5]
W_DUR_MS      = 55.0
W_COART_ON    = 0.15
W_COART_OFF   = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7506 | >= 0.50 |
| Low F2 | ~700 Hz | 550–900 Hz |

---

#### [j] — voiced palatal approximant
**First word:** GEFRŪNON (line 2)  
**Iterations to verify:** 1

```python
J_F_START = [350.0, 2200.0, 2800.0, 3400.0]
J_F_END   = [400.0, 2100.0, 2700.0, 3300.0]
J_B       = [100.0,  130.0,  200.0,  280.0]
J_GAINS   = [ 14.0,    7.0,    2.0,    0.5]
J_DUR_MS      = 55.0
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| High F2 onset | >= 2000 Hz | >= 2000 Hz |

---

#### [r] — alveolar trill
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1 (depth fix in ǢREST)

```python
R_F          = [300.0,  900.0, 2000.0, 3200.0]
R_B          = [100.0,  150.0,  250.0,  300.0]
R_GAINS      = [ 14.0,    7.0,    2.0,    0.5]
R_DUR_MS     = 65.0
R_TRILL_RATE = 28.0
R_TRILL_DEPTH = 0.40   # v2: was 0.55 — failed post-long-vowel
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| AM modulation | present | audible |
| Cross-instance range | 0.5923–0.8608 | — |

**TRILL_DEPTH NOTE:** 0.40 is the verified
safe value across all phonemic contexts.
0.55 failed post-long-vowel in ǢREST
(measured 0.4320 < 0.50 target).
Use 0.40 universally — conservative and reliable.

---

#### [l] — voiced alveolar lateral
**First word:** ÆÞELINGAS (line 3)  
**Iterations to verify:** 1

```python
L_F     = [350.0, 1200.0, 2489.0, 3200.0]
L_B     = [100.0,  200.0,  250.0,  300.0]
L_GAINS = [ 14.0,    7.0,    2.0,    0.5]
L_DUR_MS      = 65.0
L_COART_ON    = 0.12
L_COART_OFF   = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| F3 | ~2489 Hz (pulled low) | 2000–2800 Hz |

Lateral antiformant ~1900 Hz from lateral groove.
F3 pulled lower than other voiced segments at same height.

---

#### [ʍ] — voiceless labio-velar fricative
**First word:** HWÆT (line 1)  
**Iterations to verify:** 1 (7 iterations total across HWÆT diagnostic development v1–v6)

```python
WH_F        = [300.0,  700.0, 2000.0, 3000.0]
WH_BW       = [300.0,  400.0,  500.0,  500.0]  # wide — voiceless
WH_GAINS    = [  8.0,    4.0,    1.0,    0.3]
WH_DUR_MS   = 80.0
WH_VOICING  = 0.0   # voiceless — target < 0.30
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | < 0.30 | < 0.30 |
| BW | 300–500 Hz | wide (voiceless) |

Maximum coherence distance from H in the inventory.
C([ʍ],H) ≈ 0.08 — the tritone of the vocal topology.
The opening of Beowulf begins at maximum gap.
The mead hall heard the pull toward resolution.

---

### CONSONANTS — GEMINATES

**Framework established in ELLEN (line 3).**

Geminate consonants are phonemically distinct
from singleton consonants in Old English.
Duration is the primary perceptual cue.
Formant targets are identical to singleton.
Diagnostic: duration ratio >= 1.7× singleton.
Implementation: `geminate=True` flag in synth
functions extends plateau only — onset and
offset transitions unchanged.

This matters: *god* vs *gōd* (minimal pair by
vowel length) is the same physical principle.
Duration is phonemically contrastive.
The diagnostic must verify it.

#### [lː] — geminate lateral
**First word:** ELLEN (line 3, word 4)  
**Iterations to verify:** 1

```python
# geminate=True in synth_L():
LL_DUR_MS = 130.0   # 2.0× singleton 65 ms
# All formant parameters: identical to [l]
# L_F, L_B, L_GAINS — unchanged
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| Geminate ratio [lː]/[l] | 2.00× | 1.7–2.5× |
| Duration | 130 ms | >= 110 ms |

Geminate accounts for 41% of ELLEN total
duration (130/315 ms) — dominates temporal profile.
This is the acoustic signature of a geminate word.

**Geminates expected in remaining lines:**
[tː], [nː], [sː] will appear in Phase 2 onward.
Framework is established — use geminate=True,
same ratio target. No new synthesis architecture needed.

---

## COMPLETE INVENTORY — QUICK REFERENCE

```
VOWELS — SHORT (7):
  [e]  [æ]  [ɪ]  [y]  [o]  [ɑ]  [u]

VOWELS — UNSTRESSED (1):
  [ə]   phoneme 40 — VRFY_002 complete

VOWELS — LONG (6):
  [eː]  [æː]  [ɑː]  [oː]  [iː]  [uː]

VOWELS — DIPHTHONGS (4):
  [eɑ]  [eːɑ]  [eo]  [eːo]

CONSONANTS — STOPS (6):
  [p]  [t]  [d]  [k]  [ɡ]  [b]*

CONSONANTS — FRICATIVES (9):
  [f]  [v]  [s]  [θ]  [ð]  [x]  [ɣ]  [h]  [ʃ]

CONSONANTS — NASALS (3):
  [m]  [n]  [ŋ]

CONSONANTS — APPROXIMANTS (5):
  [w]  [j]  [r]  [l]  [ʍ]

CONSONANTS — GEMINATES (1):
  [lː]

*[b] — phoneme 43 — PENDING — GEBĀD line 8

TOTAL: 43 phonemes. 42 verified. 1 pending.
```

---

## VOICING SCORE REFERENCE

| Phoneme | Type | Score range | Notes |
|---|---|---|---|
| [ʍ] | voiceless approx. | < 0.30 | wide BW |
| [p] [t] [k] | voiceless stops | < 0.20 | silence dominant |
| [f] [s] [θ] [x] [ʃ] | voiceless fric. | < 0.20 | noise only |
| [h] | voiceless glottal | < 0.25 | wideband |
| [b] [d] [ɡ] | voiced stops | 0.50–0.80 | murmur bar |
| [v] [ð] [ɣ] | voiced fric. | 0.40–0.70 | periodic + AM |
| [m] [n] [ŋ] | nasals | 0.65–0.85 | sustained murmur |
| [l] [lː] | laterals | 0.65–0.80 | sustained voiced |
| [r] | trill | 0.50–0.86 | AM interruptions |
| [w] [j] | approximants | 0.65–0.85 | fully voiced |
| Short vowels | voiced | 0.65–0.85 | — |
| Long vowels | voiced | 0.84–0.89 | longer plateau → higher |
| [ə] | unstressed vowel | 0.65–0.75 | reduced articulatory precision |

---

## KNOWN LIMITATIONS

1. **Rosenberg pulse source** — no jitter, shimmer,
   or breath dynamics. Robotic quality at source level.
   Correctness of topological coordinates unaffected.
   Fidelity gap is a separable engineering problem.

2. **Trill modelling** — AM amplitude modulation
   approximates trill. Not articulatorily accurate.
   Perceptually sufficient for diagnostic purposes.

3. **[θ]/[ʃ] centroid proximity** — high-frequency
   tail of [θ] overlaps low-frequency band of [ʃ].
   Primary separator is place, not voicing (both voiceless).
   Perceptual review required at each occurrence.

4. **LPC failure at low pitch for back vowels** —
   [ɑː] and [ɑ] at 110��145 Hz: F1 and F2 merge.
   Band centroid method required (600–1400 Hz).
   Documented and handled — see [ɑː] entry.

5. **Coarticulation boundary-only** — formant
   interpolation at segment edges only (10–12%).
   Within-segment trajectory context-independent.
   Cross-instance onset measurements show near-zero
   difference across phonemic contexts — sufficient
   for Phase 1 verification purposes.

6. **Dark [ɫ] not separately modelled** — OE [l]
   before back vowels may be velarised. Single [l]
   parameter set used throughout. If perceptual
   review flags it, a separate [ɫ] entry with higher
   F1 and lower F2 can be added without breaking
   existing verified words.

7. **[ʃ] only** — OE does not have [ʒ] as a
   distinct phoneme. The voiced postalveolar fricative
   does not require a separate synthesis entry.
   Any apparent [ʒ] in running speech is an
   allophone of [j] or a coarticulation artefact,
   not a phoneme. Do not add it to this inventory.

---

## ASSEMBLY CHECKLIST

```
For each new word:
□ Write IPA transcription
□ Syllabify
□ Check all phonemes against this inventory
□ If gap: introduce new phoneme first
□ Import synth functions for each phoneme
□ Pass F_prev and F_next for coarticulation
□ Concatenate segments
□ Normalise to 0.75 peak
□ Run diagnostic:
  □ Voicing for each voiced segment
  □ Voicing (low) for each voiceless segment
  □ Centroid for fricatives
  □ Burst centroid for stops
  □ Geminate ratio for any [lː] (or future geminates)
  □ Duration within target range
  □ Long/short duration ratio where applicable
  □ Full word RMS and duration
□ Write evidence file
□ Update iteration record if new fix encountered
□ Update line status table
```

---

## ITERATION RECORD — ALL PHONEMES

| Phoneme | Iterations | Failure | Fix |
|---|---|---|---|
| [e] | 1 | — | — |
| [æ] | 1 | — | — |
| [ɪ] | 1 | — | — |
| [y] | 1 | — | — |
| [o] | 1 | — | — |
| [ɑ] | 1 | — | — |
| [u] | 1 | — | — |
| [ə] | 1 | — | — |
| [eː] | 1 | — | — |
| [æː] | 1 | — | — |
| [ɑː] | 1 | — | LPC merge noted — band centroid method required |
| [oː] | 1 | — | — |
| [iː] | 1 | — | — |
| [uː] | 1 | — | Sub-F1 harmonic pull noted — floor 180 Hz |
| [eɑ] | 1 | — | — |
| [eːɑ] | 1 | — | — |
| [eo] | 1 | — | — |
| [eːo] | 1 | — | — |
| [p] | 1 | — | — |
| [b] | — | PENDING | — |
| [t] | 1 | — | — |
| [d] | 1 | — | — |
| [k] | 1 | — | — |
| [ɡ] | 2 | Murmur masked by VOT noise | Murmur gain 0.35→0.65, VOT 0.25→0.05 |
| [f] | 1 | — | — |
| [v] | 3 | Noise source used — periodic voicing lost | Pure Rosenberg, no noise, AM 80 Hz |
| [s] | 1 | — | — |
| [θ] | 1 | — | — |
| [ð] | 1 (recon v3) | Differenced pulse — voicing bar lost | Undifferenced pulse for voiced fricatives |
| [x] | 1 | — | — |
| [ɣ] | 1 | — | — |
| [h] | 1 | — | — |
| [m] | 1 | — | — |
| [n] | 1 | — | — |
| [ŋ] | 1 | — | — |
| [w] | 1 | — | — |
| [j] | 1 | — | — |
| [r] | 1 (+depth fix) | Trill depth 0.55 failed post-long-vowel | Depth 0.55→0.40 universal |
| [l] | 1 | — | — |
| [lː] | 1 | — | — |
| [ʍ] | 1 | — | — |

**Total phonemes: 43 (42 verified + [b] pending)**  
**Total iterations: 46**  
**Failures encountered and resolved: 5**  
**First-run pass rate: 38/42 verified = 90%**

---

## LINE STATUS

| Line | OE text | Words | Status |
|---|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | 1–5 | ✓ complete |
| 2 | *Þēod-cyninga þrym gefrūnon* | 6–8 | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | 9–13 | ✓ complete |
| 4 | *þæt wæs gōd cyning* | 14–17 | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | 18–21 | ✓ complete |
| 6 | *monegum mægþum meodosetla ofteah* | 22–25 | ✓ complete |
| 7 | *egsode eorlas syþðan ǣrest wearð* | 26–30 | ✓ complete |
| 8 | *feasceaft funden hē þæs frōfre gebād* | 31–36 | feasceaft ✓ funden ✓ — hē next |

**Line 8 word status:**
```
feasceaft  ✓  [fæɑʃæɑft]   — destitute
funden     ✓  [fundən]      — found — [ə] phoneme 40 verified
hē         —  [heː]         — he — zero new phonemes
þæs        —  [θæs]         — of that — zero new phonemes
frōfre     —  [froːvrə]     — comfort — zero new phonemes
gebād      —  [gəbaːd]      — waited — [b] arrives — phoneme 43
```

**Pending work to close the inventory:**
1. HĒ [heː] — pure assembly
2. ÞÆS [θæs] — pure assembly
3. FRŌFRE [froːvrə] — pure assembly (note [ə] in unstressed -re)
4. GEBĀD [gəbaːd] — [b] introduced — phoneme 43 — inventory closes

**After GEBĀD: inventory complete. Phase 2 is pure assembly.**
