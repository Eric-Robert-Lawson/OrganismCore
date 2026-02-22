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
| F2 centroid (400–1200 Hz) | 687 Hz | 500–900 Hz |

Lowest F2 of any vowel in the system.
Rounding contributes ~400 Hz F2 lowering
vs unrounded back vowel.

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
Appears in: Gār, Ðā, Þāra, Hronrāde, Gār-Dena.

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
Minimal pair: *god* [ɡod] vs *gōd* [ɡoːd].

---

#### [iː] — long close front unrounded
**First word:** WĪF (inventory completion series)  
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
Pre-Great-Vowel-Shift value.
OE [iː] → ModE [aɪ] (wife, tide, mine).

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
OE [uː] → ModE [aʊ] (house, out, now).

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
| F2 onset | ~1851 Hz | 1500–2200 Hz |
| F2 offset | ~1131 Hz | 800–1400 Hz |
| F2 delta | ~720–753 Hz ↓ | 400–1000 Hz |
| F1 delta | ~250–281 Hz ↑ | 100–400 Hz |

F2 falls. F1 rises. Jaw opens as tongue
moves back. Cross-word stability confirmed
in SCEAÞENA, ĒAGE, WEARÐ: F2 onset
1849–1851 Hz across all instances.

---

#### [eːɑ] — long front-back diphthong
**First word:** ĒAGE (inventory completion series)  
**Iterations to verify:** 1

```python
EYA_F_ON  = [450.0, 1851.0, 2600.0, 3300.0]
EYA_F_OFF = [700.0, 1100.0, 2400.0, 3100.0]
EYA_DUR_MS    = 160.0   # ~2× short [eɑ]
EYA_TRANS_ON  = 0.15
EYA_TRANS_OFF = 0.85
```

| Diagnostic | Value | Target |
|---|---|---|
| Duration | >= 140 ms | >= 140 ms |
| F2 movement | same trajectory as [eɑ] | — |
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

F2 falls steeply. F1 stable.
Distinct from [eɑ]: F1 does NOT rise.
That is the diagnostic separator:
[eɑ] F1 rises ~250 Hz; [eo] F1 stable ±5 Hz.

---

#### [eːo] — long front-mid diphthong
**First word:** ÞĒOD (inventory completion series)  
**Iterations to verify:** 1

```python
EYO_F_ON  = [450.0, 1900.0, 2600.0, 3300.0]
EYO_F_OFF = [450.0,  800.0, 2400.0, 3000.0]
EYO_DUR_MS    = 150.0   # ~2× short [eo]
EYO_TRANS_ON  = 0.25
EYO_TRANS_OFF = 0.85
```

| Diagnostic | Value | Target |
|---|---|---|
| Duration | >= 130 ms | >= 130 ms |
| F2 movement | same trajectory as [eo] | — |
| Duration ratio [eːo]/[eo] | >= 1.7× | >= 1.7× |

Same formant trajectory as [eo].
Duration is the sole distinguishing feature.

---

### CONSONANTS — STOPS

#### [p] — voiceless bilabial stop
**First word:** PÆÞ (inventory completion series)  
**Iterations to verify:** 1

```python
P_CLOSURE_MS  = 60.0
P_BURST_MS    = 10.0
P_BURST_CF    = 800.0    # bilabial — lowest burst CF
P_BURST_BW    = 600.0
P_BURST_GAIN  = 0.15
P_VOT_MS      = 20.0
P_VOT_GAIN    = 0.08
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (voiceless) | <= 0.20 | <= 0.35 |
| Burst centroid | ~800 Hz | 500–1200 Hz |
| Stop distinction [p]/[t]/[k] | bilabial < alveolar < velar | ordered |

Lowest burst centroid of all stops —
bilabial place = largest cavity = lowest resonance.

---

#### [b] — voiced bilabial stop
**First word:** GEBĀD (line 8) — PENDING  
**Iterations to verify:** —

```python
# Based on [ɡ] lessons:
B_CLOSURE_MS  = 55.0
B_MURMUR_GAIN = 0.65   # >= 0.60 — learned from [ɡ]
B_BURST_CF    = 800.0
B_BURST_BW    = 600.0
B_BURST_GAIN  = 0.08
B_VOT_GAIN    = 0.05   # <= 0.10 — learned from [ɡ]
```

**Pre-verified parameters from [ɡ] lesson:**
Murmur gain must be >= 0.60 or voicing
bar is masked by VOT noise. VOT noise gain
must be <= 0.10. Apply these from iteration 1.

---

#### [t] — voiceless alveolar stop
**First word:** HWÆT (line 1)  
**Iterations to verify:** 1

```python
T_CLOSURE_MS  = 55.0
T_BURST_MS    = 12.0
T_BURST_CF    = 3500.0  # alveolar
T_BURST_BW    = 2000.0
T_BURST_GAIN  = 0.20
T_VOT_MS      = 18.0
T_VOT_GAIN    = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (voiceless) | <= 0.20 | <= 0.35 |
| Burst centroid | ~3500 Hz | 2500–5000 Hz |

---

#### [d] — voiced alveolar stop
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
D_CLOSURE_MS  = 50.0
D_MURMUR_GAIN = 0.65
D_BURST_CF    = 3500.0
D_BURST_BW    = 2000.0
D_BURST_GAIN  = 0.08
D_VOT_GAIN    = 0.05
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
K_CLOSURE_MS  = 60.0
K_BURST_MS    = 12.0
K_BURST_CF    = 1600.0  # velar
K_BURST_BW    = 1200.0
K_BURST_GAIN  = 0.18
K_VOT_MS      = 22.0
K_VOT_GAIN    = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (voiceless) | <= 0.20 | <= 0.35 |
| Burst centroid | ~1600 Hz | 800–2500 Hz |

---

#### [ɡ] — voiced velar stop
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 2

```python
G_CLOSURE_MS  = 50.0
G_MURMUR_GAIN = 0.65   # FIX: was 0.35
G_BURST_CF    = 1600.0
G_BURST_BW    = 1200.0
G_BURST_GAIN  = 0.08
G_VOT_GAIN    = 0.05   # FIX: was 0.25
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| Burst centroid | ~1600 Hz | 800–2500 Hz |

**Fix record:** Iteration 1 failed —
murmur masked by VOT noise.
Murmur gain 0.35→0.65. VOT noise 0.25→0.05.
Lesson applies to [b].

Burst centroid context-dependent:
before front vowel [e]: ~1627 Hz.
Before back vowel [u]: ~1237 Hz.
Both within velar target range.

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
# NO noise component
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| RMS | 0.005–0.80 | 0.005–0.80 |

**Fix record:** Iterations 1–2 failed —
noise source used, periodic voicing lost.
Fix: pure Rosenberg source, no noise.
AM modulation depth 0.25 at 80 Hz.

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
Anterior constriction = maximum turbulence
frequency. Ordering confirmed:
[x] < [θ] < [f] < [ʃ] < [s].

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

Known limitation: high-frequency tail
perceptually proximate to [ʃ].
Primary separator: [θ] voiceless, [ð] voiced.

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
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.40 | >= 0.40 |
| Centroid | 800–4000 Hz | 800–4000 Hz |

Voicing pulls centroid below [θ].
Source: undifferenced Rosenberg pulse
(differencing suppresses 145 Hz fundamental).
This applies to all voiced fricatives.

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
Scottish 'loch', German 'Bach' quality.

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
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| RMS | 0.005–0.80 | 0.005–0.80 |

Voiced counterpart of [x]. Dutch/Greek gamma quality.
Continuous voiced fricative — not a stop.

---

#### [h] — voiceless glottal fricative
**First word:** HU (line 3) — via synthesis  
**Iterations to verify:** 1

```python
H_NOISE_CF   = 1500.0
H_NOISE_BW   = 3000.0   # wide — glottal
H_GAIN       = 0.15
H_DUR_MS     = 55.0
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | <= 0.20 | <= 0.35 |
| Broadband noise | wideband | wideband |

Widest noise band of all fricatives.
Glottal constriction = no place-specific
filtering. Noise shaped by following vowel.

---

#### [ʃ] — voiceless postalveolar fricative
**First word:** SCYLD (line 5)  
**Iterations to verify:** 1

```python
SH_DUR_MS   = 80.0
SH_NOISE_CF = 3800.0
SH_NOISE_BW = 2400.0
SH_GAIN     = 0.30
SH_SEC_CF   = 6000.0
SH_SEC_BW   = 2000.0
SH_SEC_GAIN = 0.20
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | <= 0.20 | <= 0.35 |
| Centroid | ~4756 Hz | 2500–5500 Hz |

OE 'sc' spelling always = [ʃ].
Centroid lower than [s] (~7535 Hz) by ~2853 Hz.
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
M_ANTIFORM_F  = 1000.0  # bilabial — lower than [n]
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
N_ANTIFORM_F  = 800.0   # alveolar
N_ANTIFORM_BW = 180.0
N_VOICE_GAIN  = 0.55
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.77–0.80 | >= 0.65 |
| RMS (nasal murmur) | 0.22–0.25 | 0.005–0.25 |

Cross-instance stability: voicing
0.77–0.80 across 10 instances. Zero variance.

---

#### [ŋ] — voiced velar nasal
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
NG_DUR_MS      = 65.0
NG_ANTIFORM_F  = 1200.0  # velar — higher than [n]
NG_ANTIFORM_BW = 220.0
NG_VOICE_GAIN  = 0.55
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.65 | >= 0.65 |
| RMS (nasal murmur) | 0.005–0.25 | 0.005–0.25 |

---

### CONSONANTS — APPROXIMANTS

#### [w] — voiced labio-velar approximant
**First word:** WĒ (line 1)  
**Iterations to verify:** 1

```python
W_F     = [300.0,  700.0, 2000.0, 3000.0]
W_B     = [100.0,  150.0,  250.0,  300.0]
W_GAINS = [ 14.0,    7.0,    2.0,    0.5]
W_DUR_MS      = 55.0
W_COART_ON    = 0.15
W_COART_OFF   = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7506 | >= 0.50 |
| RMS | 0.005–0.80 | 0.005–0.80 |

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
**Iterations to verify:** 1

```python
R_F      = [300.0,  900.0, 2000.0, 3200.0]
R_B      = [100.0,  150.0,  250.0,  300.0]
R_GAINS  = [ 14.0,    7.0,    2.0,    0.5]
R_DUR_MS     = 65.0
R_TRILL_RATE = 28.0
R_TRILL_DEPTH= 0.40   # v2: was 0.55 — failed post-long-vowel
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| AM modulation | present | audible trill |

**TRILL_DEPTH NOTE:** 0.40 is the verified
value for all contexts. 0.55 passed in
early GĀR-DENA but failed post-long-vowel
in ǢREST (v1: 0.4320 < 0.50). 0.40 is
conservative and reliable across all contexts.
Cross-instance range at 0.40: 0.5923–0.8608.

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

Antiformant ~1900 Hz from lateral groove.
F3 pulled low relative to other voiced segments.

---

#### [ʍ] — voiceless labio-velar fricative
**First word:** HWÆT (line 1)  
**Iterations to verify:** 1 (7 iterations total across v1–v6 of HWÆT diagnostic development)

```python
WH_F        = [300.0,  700.0, 2000.0, 3000.0]
WH_BW       = [300.0,  400.0,  500.0,  500.0]  # wide — voiceless
WH_GAINS    = [  8.0,    4.0,    1.0,    0.3]
WH_DUR_MS   = 80.0
WH_VOICING  = 0.0   # voiceless — below 0.30 target
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | < 0.30 | < 0.30 |
| BW | 300–500 Hz | wide (voiceless) |

Maximum coherence distance from H in the inventory.
Tritone of the vocal topology.
The opening of Beowulf begins here.

---

### CONSONANTS — GEMINATES

**Framework:** Geminate consonants are phonemically
distinct from singleton consonants in Old English.
Duration is the primary cue. Formant targets identical.
Diagnostic: duration ratio >= 1.7× singleton.
Implementation: geminate=True flag in synth functions
extends plateau only — transitions unchanged.

#### [lː] — geminate lateral
**First word:** ELLEN (line 3)  
**Iterations to verify:** 1

```python
# geminate=True in synth_L():
LL_DUR_MS = 130.0   # 2.0× singleton 65 ms
# Formant parameters: identical to [l]
# L_F, L_B, L_GAINS — unchanged
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| Geminate ratio [lː]/[l] | 2.00× | 1.7–2.5× |
| Duration | 130 ms | >= 110 ms |

Geminate accounts for 41% of ELLEN total
duration (130/315 ms) — dominates temporal profile.
Framework established. All future geminates:
use geminate=True flag, same ratio target.
Future geminates expected: [tː], [nː], [sː]
in Phase 2 onward.

---

## VOICING SCORE REFERENCE

| Phoneme | Type | Score range | Notes |
|---|---|---|---|
| [ʍ] | voiceless | < 0.30 | wide BW aspiration |
| [p] [t] [k] | voiceless stops | < 0.20 | closure silence |
| [f] [s] [θ] [x] [ʃ] | voiceless fric. | < 0.20 | noise only |
| [h] | voiceless glottal | < 0.25 | wideband |
| [b] [d] [ɡ] | voiced stops | 0.50–0.80 | murmur bar |
| [v] [ð] [ɣ] | voiced fric. | 0.40–0.70 | periodic + AM |
| [m] [n] [ŋ] | nasals | 0.65–0.85 | sustained murmur |
| [l] [lː] | laterals | 0.65–0.80 | sustained voiced |
| [r] | trill | 0.50–0.86 | AM interruptions lower score |
| [w] [j] | approximants | 0.65–0.85 | fully voiced |
| [ʍ] | voiceless approx. | < 0.30 | voiceless |
| Short vowels | voiced | 0.65–0.85 | — |
| Long vowels | voiced | 0.84–0.89 | longer plateau → higher score |

---

## KNOWN LIMITATIONS

1. **Rosenberg pulse source** — no jitter, shimmer,
   or breath dynamics. Robotic quality at source level.
   Correctness of coordinates unaffected.

2. **Trill modelling** — AM amplitude modulation
   approximates trill. Not articulatorily accurate.
   Perceptually sufficient for diagnostic purposes.

3. **[θ]/[ʃ] centroid proximity** — high-frequency
   tail of [θ] overlaps low-frequency band of [ʃ].
   Primary separator: voiceless vs voiceless (place,
   not voicing). Perceptual review required.

4. **LPC failure at low pitch for back vowels** —
   [ɑː] and [ɑ] at 110–145 Hz: F1 and F2 merge.
   Band centroid method required (600–1400 Hz).
   Documented and handled.

5. **Coarticulation boundary-only** — formant
   interpolation at segment edges only (10–12%).
   Within-segment trajectory is context-independent.
   Cross-instance onset centroid measurements show
   near-zero difference across phonemic contexts.
   Known and noted in evidence files.

6. **Dark [ɫ] not separately modelled** — OE [l]
   before back vowels may be velarized. Current
   single [l] parameter set used throughout.
   If perceptual review flags it, a separate [ɫ]
   entry with higher F1 and lower F2 can be added.

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
  □ Voicing for each voiceless segment
  □ Centroid for fricatives
  □ Burst centroid for stops
  □ Duration within target range
  □ Full word RMS and duration
□ Write evidence file
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
| [eː] | 1 | — | — |
| [æː] | 1 | — | — |
| [ɑː] | 1 | — | — |
| [oː] | 1 | — | — |
| [iː] | 1 | — | — |
| [uː] | 1 | — | — |
| [eɑ] | 1 | — | — |
| [eːɑ] | 1 | — | — |
| [eo] | 1 | — | — |
| [eːo] | 1 | — | — |
| [p] | 1 | — | — |
| [b] | — | PENDING | — |
| [t] | 1 | — | — |
| [d] | 1 | — | — |
| [k] | 1 | — | — |
| [ɡ] | 2 | Murmur masked by VOT noise | Murmur gain 0.35→0.65, VOT noise 0.25→0.05 |
| [f] | 1 | — | — |
| [v] | 3 | Noise source used — periodic voicing lost | Pure Rosenberg source, no noise |
| [s] | 1 | — | — |
| [θ] | 1 | — | — |
| [ð] | 1 (recon v3) | Voicing failed — differenced pulse | Undifferenced pulse for voicing bar |
| [x] | 1 | — | — |
| [ɣ] | 1 | — | — |
| [h] | 1 | — | — |
| [m] | 1 | — | — |
| [n] | 1 | — | — |
| [ŋ] | 1 | — | — |
| [w] | 1 | — | — |
| [j] | 1 | — | — |
| [r] | 1 (depth fix in ǢREST) | Trill depth 0.55 failed post-long-vowel | Depth 0.55→0.40 |
| [l] | 1 | — | — |
| [lː] | 1 | — | — |
| [ʍ] | 1 | — | — |

**Total phonemes: 43 (42 verified + 1 pending)**  
**Total iterations across verified phonemes: 44**  
**Failures encountered: 5 (all resolved)**  
**First-run pass rate: 38/42 verified = 90%**

---

## LINE STATUS

| Line | OE text | Words | Status |
|---|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | 1–5 | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | 6–8 | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | 9–13 | ✓ complete |
| 4 | *þæt wæs gōd cyning* | 14–17 | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | 18–21 | ✓ complete |
| 6 | *monegum mægþum meodosetla ofteah* | 22–25 | ✓ complete |
| 7 | *egsode eorlas syþðan ǣrest wearð* | 26–30 | ✓ complete |
| 8 | *feasceaft funden hē þæs frōfre gebād* | 31–36 | feasceaft ✓ funden ✓ hē — in progress |
| 9 | *weox under wolcnum weorðmyndum þah* | 37–41 | pending |
| 10 | *oðþæt him æghwylc þara ymbsittendra* | 42–47 | pending |
| 11 | *ofer hronrade hyran scolde* | 48–51 | pending |
| 12 | *gomban gyldan þæt wæs gōd cyning* | 52–57 | pending |
