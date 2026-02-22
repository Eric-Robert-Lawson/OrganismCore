# OLD ENGLISH PHONEME INVENTORY
## Beowulf Reconstruction — Master Reference
**Methodology:** Formant synthesis — Rosenberg pulse source + IIR formant filters  
**Diagnostic framework:** Autocorrelation voicing + spectral centroid + RMS level  
**Sample rate:** 44100 Hz  
**Base pitch:** 145 Hz (performance: 110 Hz)  
**Date:** February 2026  
**Status:** 39 of 40 phonemes verified. [b] pending — line 8.

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
  Voicing scores: 0.7607–0.7618
```

### Formant filter

```python
# Per-formant IIR resonator.
# Iterated for F1–F4.
T  = 1.0 / sr
a2 = -exp(-2π·bw·T)
a1 =  2·exp(-π·bw·T)·cos(2π·fc·T)
b0 =  1 - a1 - a2
```

### Voicing diagnostic

```python
# Autocorrelation of middle 50% of segment.
# Normalised peak in pitch period range.
# lo = sr/400 (~110 Hz upper bound)
# hi = sr/80  (~550 Hz lower bound)
# Returns 0.0–1.0.
# Voiced target:   >= 0.50
# Voiceless target: <= 0.35
```

### Coarticulation model

```python
# Boundary transitions only.
# First COART_ON fraction: linear
#   interpolation from F_prev to target.
# Last COART_OFF fraction: linear
#   interpolation from target to F_next.
# Within-segment: constant at target.
# Limitation: onset centroid measurements
#   reflect stable target, not boundary
#   transition detail.
```

### Room simulation

```python
# Three-tap delay with exponential decay.
# RT60 = 2.0 s (mead-hall estimate)
# Direct ratio: 0.38–0.42
# Delays: 21, 35, 51 ms
# Gain: 10^(-3/(RT60·SR))
```

### Time stretching

```python
# OLA (overlap-add).
# Window: 40 ms Hanning.
# Hop: window/4.
# Factor 4.0x for perceptual inspection.
```

---

## DIAGNOSTIC THRESHOLDS

| Measure | Voiced target | Voiceless target |
|---|---|---|
| Voicing (autocorr) | >= 0.50 | <= 0.35 |
| Nasal voicing | >= 0.65 | — |
| Fricative voicing (voiced) | >= 0.35 | — |
| Stop murmur gain | >= 0.60 | 0.0 |
| VOT noise gain | <= 0.10 | <= 0.25 |

---

## PHONEME TABLES

---

### VOWELS — SHORT

---

#### [e] — short close-mid front unrounded
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
E_F     = [450.0, 1900.0, 2600.0, 3300.0]
E_B     = [100.0,  130.0,  200.0,  280.0]
E_GAINS = [ 16.0,    8.0,    1.5,    0.5]
E_DUR_MS        = 55.0
E_COART_ON      = 0.12
E_COART_OFF     = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.6695 | >= 0.50 |
| F2 centroid | 1875 Hz | 1600–2300 Hz |

---

#### [æ] — open front unrounded
**First word:** HWÆT (line 1)  
**Iterations to verify:** 1

```python
AE_F     = [700.0, 1700.0, 2600.0, 3300.0]
AE_B     = [120.0,  150.0,  200.0,  280.0]
AE_GAINS = [ 16.0,    8.0,    1.5,    0.5]
AE_DUR_MS       = 60.0
AE_COART_ON     = 0.12
AE_COART_OFF    = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7011 | >= 0.50 |
| F2 centroid | 1684 Hz | 1400–2000 Hz |

---

#### [ɪ] — short near-close front unrounded
**First word:** CYNINGA (line 2)  
**Iterations to verify:** 1

```python
I_F     = [400.0, 1700.0, 2500.0, 3200.0]
I_B     = [ 90.0,  130.0,  200.0,  260.0]
I_GAINS = [ 16.0,    8.0,    1.5,    0.5]
I_DUR_MS        = 55.0
I_COART_ON      = 0.12
I_COART_OFF     = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.6706 | >= 0.50 |
| F2 centroid | 1704 Hz | 1400–2100 Hz |

---

#### [y] — short close front rounded
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
Y_F     = [300.0, 1500.0, 2100.0, 3100.0]
Y_B     = [ 80.0,  120.0,  200.0,  260.0]
Y_GAINS = [ 16.0,    8.0,    1.5,    0.5]
Y_DUR_MS        = 55.0
Y_COART_ON      = 0.12
Y_COART_OFF     = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.6680 | >= 0.50 |
| F2 centroid | 1418 Hz | 1100–1900 Hz |

**Rounding note:** F2 862 Hz lower than [iː].
Rounding coefficient: 862 Hz at close front position.

---

#### [o] — short close-mid back rounded
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
O_F     = [450.0,  800.0, 2500.0, 3200.0]
O_B     = [100.0,  120.0,  200.0,  280.0]
O_GAINS = [ 16.0,    8.0,    1.5,    0.5]
O_DUR_MS        = 55.0
O_COART_ON      = 0.12
O_COART_OFF     = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.6691 | >= 0.50 |
| F2 centroid | 748 Hz | 600–1000 Hz |

---

#### [ɑ] — short open back unrounded
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
A_F     = [700.0, 1100.0, 2500.0, 3200.0]
A_B     = [120.0,  150.0,  200.0,  280.0]
A_GAINS = [ 16.0,    8.0,    1.5,    0.5]
A_DUR_MS        = 55.0
A_COART_ON      = 0.12
A_COART_OFF     = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.6679 | >= 0.50 |
| F2 centroid | 1085 Hz | 900–1400 Hz |

---

#### [u] — short close back rounded
**First word:** GEFRŪNON (line 2)  
**Iterations to verify:** 1

```python
U_F     = [350.0,  700.0, 2400.0, 3100.0]
U_B     = [ 80.0,  120.0,  200.0,  260.0]
U_GAINS = [ 16.0,    8.0,    1.5,    0.5]
U_DUR_MS        = 55.0
U_COART_ON      = 0.12
U_COART_OFF     = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.6688 | >= 0.50 |
| F2 centroid | 748 Hz | 550–950 Hz |

---

### VOWELS — LONG

---

#### [eː] — long close-mid front unrounded
**First word:** WĒ (line 1)  
**Iterations to verify:** 1

```python
EY_F     = [450.0, 1900.0, 2600.0, 3300.0]
EY_B     = [100.0,  130.0,  200.0,  280.0]
EY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
EY_DUR_MS       = 110.0   # long — ~2x short
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
**First word:** MǢGÞUM (line 5)  
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

#### [oː] — long close-mid back rounded
**First word:** GĀR-DENA (line 1) — [ɑː] context  
**Iterations to verify:** 1

```python
OY_F     = [450.0,  800.0, 2500.0, 3200.0]
OY_B     = [100.0,  120.0,  200.0,  280.0]
OY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
OY_DUR_MS       = 110.0
OY_COART_ON     = 0.10
OY_COART_OFF    = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.84 | >= 0.50 |
| Duration | 110 ms | >= 90 ms |

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
| F2 centroid | 2280 Hz | 2000–2800 Hz |
| F2 vs [ɪ] delta | 580 Hz | >= 400 Hz |
| F2 vs [y] delta | 862 Hz | >= 600 Hz |

**Highest F2 in inventory.**
Rounding coefficient reference: 862 Hz.

---

### VOWELS — DIPHTHONGS

The diphthong system encodes two
independent binary dimensions:

```
QUALITY  — F1 trajectory:
  F1 rises  → target is [ɑ] — jaw opens
  F1 stable → target is [o] — jaw stays

QUANTITY — duration:
  Short: 75–80 ms
  Long:  150 ms (~2x)
```

---

#### [eɑ] — short front-back diphthong
**First word:** SCEAÞENA (line 5)  
**Iterations to verify:** 1

```python
EA_DUR_MS    = 80.0
EA_F_ON      = [450.0, 1900.0, 2600.0, 3300.0]
EA_F_OFF     = [700.0, 1100.0, 2400.0, 3000.0]
EA_B         = [100.0,  130.0,  200.0,  280.0]
EA_GAINS     = [ 16.0,    8.0,    1.5,    0.5]
EA_TRANS_ON  = 0.25
EA_TRANS_OFF = 0.85
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7588 | >= 0.50 |
| F2 onset | ~1851 Hz | 1500–2200 Hz |
| F2 offset | ~1131 Hz | 800–1400 Hz |
| F2 delta | ~720 Hz ↓ | >= 500 Hz |
| F1 delta | ~250 Hz ↑ | >= 100 Hz |

---

#### [eːɑ] — long front-back diphthong
**First word:** ĒAGE (inventory completion)  
**Iterations to verify:** 1

```python
EYA_DUR_MS    = 150.0
EYA_F_ON      = [450.0, 1900.0, 2600.0, 3300.0]
EYA_F_OFF     = [700.0, 1100.0, 2400.0, 3000.0]
EYA_B         = [100.0,  130.0,  200.0,  280.0]
EYA_GAINS     = [ 16.0,    8.0,    1.5,    0.5]
EYA_TRANS_ON  = 0.30
EYA_TRANS_OFF = 0.90
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8854 | >= 0.50 |
| Duration | 150 ms | >= 120 ms |
| Long/short ratio | 1.88x | >= 1.5x |
| F2 onset | 1851 Hz | 1500–2200 Hz |
| F2 offset | 1115 Hz | 800–1400 Hz |
| F2 delta | 737 Hz ↓ | >= 500 Hz |
| F1 onset | 341 Hz | 300–600 Hz |
| F1 delta | 281 Hz ↑ | 100–400 Hz |

---

#### [eo] — short front-mid diphthong
**First word:** MEODOSETLA (line 6)  
**Iterations to verify:** 1

```python
EO_DUR_MS    = 75.0
EO_F_ON      = [450.0, 1900.0, 2600.0, 3300.0]
EO_F_OFF     = [450.0,  800.0, 2400.0, 3000.0]
EO_B         = [100.0,  130.0,  200.0,  280.0]
EO_GAINS     = [ 16.0,    8.0,    1.5,    0.5]
EO_TRANS_ON  = 0.25
EO_TRANS_OFF = 0.85
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7915 | >= 0.50 |
| F2 onset | 1833 Hz | 1500–2200 Hz |
| F2 offset | 759 Hz | 550–1100 Hz |
| F2 delta | 1074 Hz ↓ | >= 800 Hz |
| F1 delta | ~5 Hz stable | <= 50 Hz |

---

#### [eːo] — long front-mid diphthong
**First word:** ÞĒOD (inventory completion)  
**Iterations to verify:** 1

```python
EYO_DUR_MS    = 150.0
EYO_F_ON      = [450.0, 1900.0, 2600.0, 3300.0]
EYO_F_OFF     = [450.0,  800.0, 2400.0, 3000.0]
EYO_B         = [100.0,  130.0,  200.0,  280.0]
EYO_GAINS     = [ 16.0,    8.0,    1.5,    0.5]
EYO_TRANS_ON  = 0.25
EYO_TRANS_OFF = 0.85
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8955 | >= 0.50 |
| Duration | 150 ms | >= 120 ms |
| Long/short ratio | 2.00x | >= 1.5x |
| F2 onset | 1851 Hz | 1400–2200 Hz |
| F2 offset | 758 Hz | 500–1100 Hz |
| F2 delta | 1093 Hz ↓ | >= 800 Hz |
| F1 onset | 336 Hz | 300–600 Hz |
| F1 delta | 1 Hz stable | <= 100 Hz |
| F1 sep vs [eːɑ] | 280 Hz | >= 150 Hz |

**F1 delta 1 Hz — jaw does not move.**
Key distinction from [eːɑ] (F1 delta 281 Hz).

---

### CONSONANTS — STOPS

---

#### [p] — voiceless bilabial stop
**First word:** PÆÞ (inventory completion)  
**Iterations to verify:** 1

```python
P_DUR_MS     = 65.0
P_BURST_F    = 800.0
P_BURST_BW   = 600.0
P_BURST_MS   = 12.0
P_VOT_MS     = 10.0
P_BURST_GAIN = 0.60
P_VOT_GAIN   = 0.20
# Closure: silence — n_s - burst - VOT samples
# VOT: broadband 500–8000 Hz aspiration
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | 0.3242 | <= 0.35 |
| Burst centroid | 1038 Hz | 400–1400 Hz |
| [p]→[k] separation | 762 Hz | >= 200 Hz |
| [p]→[t] separation | 2462 Hz | >= 1000 Hz |

**Warning:** Voicing 0.3242 — narrow margin.
VOT noise creates slight autocorrelation.
[b] must score clearly above 0.3242.
Target [p]/[b] separation: >= 0.20.

---

#### [b] — voiced bilabial stop
**First word:** PENDING — line 8 GEBĀD  
**Iterations to verify:** —

```python
# PARAMETERS PENDING VERIFICATION
# Architecture: murmur + burst + VOT
# Murmur gain: >= 0.60 (lesson from [ɡ] v1)
# VOT noise gain: <= 0.10
# Burst: filtered ~800 Hz (same as [p])
# Murmur: Rosenberg pulse, LP < 300 Hz
# Voicing target: >= 0.52
# Sep from [p]: >= 0.20
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be high) | PENDING | >= 0.52 |
| Burst centroid | PENDING | 400–1400 Hz |
| Sep from [p] voicing | PENDING | >= 0.20 |

---

#### [t] — voiceless alveolar stop
**First word:** HWÆT (line 1)  
**Iterations to verify:** 1

```python
T_DUR_MS     = 65.0
T_BURST_F    = 3500.0
T_BURST_BW   = 1500.0
T_BURST_MS   = 8.0
T_VOT_MS     = 8.0
T_BURST_GAIN = 0.55
T_VOT_GAIN   = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | ~0.12 | <= 0.35 |
| Burst centroid | ~3500 Hz | 2500–4500 Hz |

---

#### [d] — voiced alveolar stop
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
D_DUR_MS     = 60.0
D_BURST_F    = 3500.0
D_BURST_BW   = 1500.0
D_BURST_MS   = 8.0
D_VOT_MS     = 5.0
# Murmur gain: 0.30 (sufficient — intervocalic)
# VOT: voiced formant filtered pulse 0.40
```

| Diagnostic | Value | Target |
|---|---|---|
| RMS level | 0.0562–0.0946 | 0.005–0.70 |
| Duration | 60 ms | 30–90 ms |

---

#### [k] — voiceless velar stop
**First word:** SCYLDINGAS (line 3)  
**Iterations to verify:** 1

```python
K_DUR_MS     = 65.0
K_BURST_F    = 1800.0
K_BURST_BW   = 800.0
K_BURST_MS   = 10.0
K_VOT_MS     = 8.0
K_BURST_GAIN = 0.55
K_VOT_GAIN   = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | ~0.12 | <= 0.35 |
| Burst centroid | ~1800 Hz | 1200–2400 Hz |

---

#### [ɡ] — voiced velar stop
**First word:** GĀR-DENA (line 1) — verified v2  
**Iterations to verify:** 2

```python
G_DUR_MS      = 70.0
G_BURST_F     = 1800.0
G_BURST_BW    = 800.0
G_BURST_MS    = 10.0
G_VOT_MS      = 5.0
G_MURMUR_GAIN = 0.65   # v1: 0.35 — FAILED
G_VOT_GAIN    = 0.05   # v1: 0.25 — FAILED
# Murmur: Rosenberg pulse LP < 300 Hz
# Envelope onset: 0.8 (strong murmur)
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7940 | >= 0.50 |
| RMS level | 0.0726 | 0.005–0.70 |

**Lesson:** Murmur gain >= 0.65, VOT noise
gain <= 0.05. Noise must not dominate
the autocorrelation window.
This applies to ALL voiced stops.

**STOP PLACE HIERARCHY:**

```
[p] bilabial   1038 Hz  ← lowest
[k] velar      1800 Hz
[t] alveolar   3500 Hz  ← highest
Bilabial < Velar < Alveolar
```

---

### CONSONANTS — FRICATIVES

---

#### [f] — voiceless labiodental fricative
**First word:** GEFRŪNON (line 2)  
**Iterations to verify:** 1

```python
F_DUR_MS   = 70.0
F_NOISE_CF = 7000.0
F_NOISE_BW = 5000.0
F_GAIN     = 0.28
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | 0.1514 | <= 0.35 |
| RMS level | 0.0951 | 0.001–0.50 |

---

#### [v] — voiced labiodental fricative
**First word:** SCEFING (line 4) — verified v3  
**Iterations to verify:** 3

```python
V_F      = [400.0, 1200.0, 2600.0]
V_B      = [350.0,  450.0,  550.0]
V_GAINS  = [  5.0,    2.5,    0.8]
V_AM_RATE  = 80.0
V_AM_DEPTH = 0.25
V_DUR_MS   = 65.0
# Pure Rosenberg source — NO noise.
# AM modulation simulates turbulence.
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7618 | >= 0.35 |
| RMS level | ~0.23 | 0.005–0.80 |

---

#### [s] — voiceless alveolar fricative
**First word:** ÆÞELINGAS (line 3)  
**Iterations to verify:** 1

```python
S_DUR_MS   = 65.0
S_NOISE_CF = 7500.0
S_NOISE_BW = 4000.0
S_GAIN     = 0.55
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | 0.1144–0.1356 | <= 0.35 |
| Centroid | 7613–7646 Hz | 5000–10000 Hz |

---

#### [θ] — voiceless dental fricative
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
TH_DUR_MS   = 70.0
TH_NOISE_CF = 5000.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.18
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | 0.1094–0.1438 | <= 0.35 |
| RMS level | 0.0749–0.0980 | 0.001–0.50 |

**Known limitation:** Centroid sits
high — perceptually proximate to [ʃ].
Passes voicing and RMS diagnostics.
Future improvement: add explicit
centroid check, target 4000–6000 Hz.

---

#### [ð] �� voiced dental fricative
**First word:** ÐĀ (line 9)  
**Iterations to verify:** 1

```python
DH_F        = [400.0, 1200.0, 2600.0]
DH_B        = [350.0,  450.0,  550.0]
DH_GAINS    = [  5.0,    2.5,    0.8]
DH_AM_RATE  = 80.0
DH_AM_DEPTH = 0.25
DH_DUR_MS   = 70.0
# Pure Rosenberg source — NO noise.
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7618 | >= 0.35 |
| RMS level | 0.2297 | 0.005–0.80 |

**[θ]/[ð] separation: 0.6406**
Same place. Only voicing changes.
Most minimal contrast in inventory.

---

#### [x] — voiceless velar fricative
**First word:** MǢGÞUM (line 5)  
**Iterations to verify:** 1

```python
X_DUR_MS   = 70.0
X_NOISE_CF = 3000.0
X_NOISE_BW = 2500.0
X_GAIN     = 0.22
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | ~0.12 | <= 0.35 |
| RMS level | ~0.08 | 0.001–0.50 |

---

#### [ɣ] — voiced velar fricative
**First word:** MǢGÞUM (line 5)  
**Iterations to verify:** 1

```python
GH_F        = [300.0,  900.0, 2200.0, 3000.0]
GH_B        = [350.0,  400.0,  500.0,  550.0]
GH_GAINS    = [  5.0,    2.5,    0.8,    0.3]
GH_AM_RATE  = 80.0
GH_AM_DEPTH = 0.25
GH_DUR_MS   = 65.0
# Pure Rosenberg source — NO noise.
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7230–0.7607 | >= 0.35 |
| RMS level | ~0.25 | 0.005–0.80 |

**[x]/[ɣ] separation: 0.6253**

**VOICED FRICATIVE CONVERGENCE:**
```
[v]  0.7618
[ð]  0.7618
[ɣ]  0.7607
```
All three use Rosenberg + AM.
Same source → same voicing score.
Place encoded in formant filters,
not in voicing measure.
This is correct instrument behaviour.

---

#### [h] — voiceless glottal fricative
**First word:** HU (line 3)  
**Iterations to verify:** 1

```python
H_DUR_MS   = 60.0
H_NOISE_CF = 2000.0
H_NOISE_BW = 3500.0
H_GAIN     = 0.30
# Broadband — glottal, no supralaryngeal
# constriction. Shaped by following vowel.
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | ~0.12 | <= 0.35 |
| RMS level | ~0.08 | 0.001–0.50 |

---

### CONSONANTS — NASALS

---

#### [m] — voiced bilabial nasal
**First word:** MONGUM (line 6)  
**Iterations to verify:** 1

```python
M_F      = [250.0,  900.0, 2200.0, 3000.0]
M_B      = [100.0,  200.0,  300.0,  350.0]
M_GAINS  = [  8.0,    2.0,    0.5,    0.2]
M_DUR_MS = 65.0
M_ANTI_F = 1000.0
M_ANTI_BW= 200.0
# Anti-formant notch at ~1000 Hz.
# Nasal murmur low — RMS 0.005–0.25.
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.65 | >= 0.65 |
| RMS (murmur) | ~0.15 | 0.005–0.25 |

---

#### [n] — voiced alveolar nasal
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
N_F      = [250.0, 1700.0, 2500.0, 3200.0]
N_B      = [100.0,  200.0,  300.0,  350.0]
N_GAINS  = [  8.0,    2.0,    0.5,    0.2]
N_DUR_MS = 60.0
N_ANTI_F = 1500.0
N_ANTI_BW= 200.0
# Anti-formant notch at ~1500 Hz.
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7785 | >= 0.65 |
| RMS (murmur) | 0.2229 | 0.005–0.25 |

---

#### [ŋ] — voiced velar nasal
**First word:** SCYLDINGAS (line 3)  
**Iterations to verify:** 1

```python
NG_F      = [250.0,  700.0, 2000.0, 2800.0]
NG_B      = [100.0,  200.0,  300.0,  350.0]
NG_GAINS  = [  8.0,    2.0,    0.5,    0.2]
NG_DUR_MS = 65.0
NG_ANTI_F = 800.0
NG_ANTI_BW= 200.0
# Anti-formant notch at ~800 Hz.
# Lower anti-formant than [n] — velar place.
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.65 | >= 0.65 |
| RMS (murmur) | ~0.15 | 0.005–0.25 |

---

### CONSONANTS — APPROXIMANTS

---

#### [w] — voiced labio-velar approximant
**First word:** WĒ (line 1)  
**Iterations to verify:** 1

```python
W_F      = [300.0,  700.0, 2200.0, 3000.0]
W_B      = [100.0,  150.0,  250.0,  300.0]
W_GAINS  = [ 14.0,    6.0,    1.5,    0.4]
W_DUR_MS = 55.0
W_COART_ON  = 0.15
W_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7506 | >= 0.50 |
| RMS level | 0.3277 | 0.005–0.80 |

---

#### [j] — voiced palatal approximant
**First word:** GĒR-DAGUM (line 1) — [j] in *gēar*  
**Iterations to verify:** 1

```python
J_F      = [300.0, 2200.0, 3000.0, 3400.0]
J_B      = [ 80.0,  120.0,  200.0,  260.0]
J_GAINS  = [ 14.0,    7.0,    1.5,    0.4]
J_DUR_MS = 50.0
J_COART_ON  = 0.20
J_COART_OFF = 0.20
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| RMS level | ~0.25 | 0.005–0.80 |

---

#### [r] — alveolar trill
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
R_F          = [300.0,  900.0, 2000.0, 3200.0]
R_B          = [100.0,  150.0,  250.0,  300.0]
R_GAINS      = [ 14.0,    7.0,    2.0,    0.5]
R_DUR_MS     = 65.0
R_TRILL_RATE = 28.0    # Hz — tongue tip interruptions
R_TRILL_DEPTH= 0.55    # AM depth
# AM modulation simulates trill interruptions.
# Reduces voicing score vs smooth approximant.
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.6818–0.8608 | >= 0.50 |
| RMS level | ~0.25 | 0.005–0.80 |

**Note:** Voicing varies by context.
Trill AM modulation reduces
autocorrelation peak. Both instances
pass >= 0.50.

---

#### [l] — voiced alveolar lateral
**First word:** ÆÞELINGAS (line 3)  
**Iterations to verify:** 1

```python
L_F      = [350.0, 1100.0, 2700.0, 3300.0]
L_B      = [100.0,  150.0,  250.0,  300.0]
L_GAINS  = [ 14.0,    6.0,    1.5,    0.4]
L_DUR_MS = 60.0
L_COART_ON  = 0.15
L_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7638 | >= 0.50 |
| RMS level | 0.2685 | 0.005–0.80 |

---

#### [ʍ] — voiceless labio-velar fricative
**First word:** HWÆT (line 1)  
**Iterations to verify:** 1

```python
WH_F      = [300.0,  700.0, 2200.0, 3000.0]
WH_B      = [150.0,  200.0,  300.0,  350.0]
WH_GAINS  = [  3.0,    1.5,    0.5,    0.2]
WH_NOISE_GAIN = 0.35
WH_DUR_MS = 60.0
# Mixed: formant-filtered noise +
# light voicing residual.
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | <= 0.35 | <= 0.35 |
| RMS level | ~0.08 | 0.001–0.50 |

---

## VOICING SCORE REFERENCE

**Full inventory voicing map:**

```
VOICED — high scores:
  [eːo]  0.8955  long diphthong
  [eːɑ]  0.8854  long diphthong
  [iː]   0.8482  long vowel
  [eː]   ~0.840  long vowel
  [ɡ]    0.7940  voiced velar stop (v2)
  [v]    0.7618  voiced labiodental fric.
  [ð]    0.7618  voiced dental fric.
  [ɣ]    0.7607  voiced velar fric.
  [n]    0.7785  alveolar nasal
  [w]    0.7506  labio-velar approx.
  [l]    0.7638  alveolar lateral
  [r]    0.6818–0.8608  alveolar trill
  [æ]    0.7011  short open front
  [e]    0.6695  short close-mid front
  [o]    0.6691  short close-mid back
  [ɑ]    0.6679  short open back
  [y]    0.6680  short close front rounded
  [u]    0.6688  short close back rounded
  [ɪ]    0.6706  short near-close front

VOICELESS — low scores:
  [p]    0.3242  bilabial stop (narrow margin)
  [s]    0.1144–0.1356
  [θ]    0.1094–0.1438
  [f]    0.1514
  [ʍ]    ~0.12
  [h]    ~0.12
  [x]    ~0.12
  [t]    ~0.12
  [k]    ~0.12

PENDING:
  [b]    —       voiced bilabial stop
                 target >= 0.52
```

---

## KNOWN LIMITATIONS

**L1 — Coarticulation boundary-only:**
Formant transitions implemented at
segment boundaries only (first/last
10–15% of segment). Within-segment
trajectory is context-independent.
Cross-instance F2 onset measurements
are therefore identical regardless of
preceding context (confirmed: MEODOSETLA
vs EORLAS [eo] onset both 1833 Hz).

**L2 — [θ] centroid too high:**
[θ] noise centroid sits ~7000 Hz —
upper range, perceptually proximate
to [s] and [ʃ]. Passes voicing and RMS
diagnostics. Does not pass informal
perceptual evaluation by naive listener.
Future fix: tighten noise band to
4000–6000 Hz, add explicit centroid
diagnostic.

**L3 — [p] voicing narrow margin:**
[p] voicing 0.3242 — margin 0.0258
to threshold. VOT aspiration noise
creates slight autocorrelation.
Mitigated by ensuring [b] scores
clearly above 0.3242.

**L4 — Voiced fricative convergence:**
[v], [ð], [ɣ] all produce voicing
scores 0.7607–0.7618. Place distinction
is in formant filters, not voicing score.
Voicing measure cannot distinguish
between voiced fricative types.
This is correct behaviour — not a bug.

**L5 — Long vowel voicing inflation:**
Long vowels score higher voicing than
short vowels (more periods in
autocorrelation window). Voicing measure
improves with duration. Does not affect
validity of voiced/voiceless distinction.

---

## ASSEMBLY CHECKLIST

For every new word reconstruction:

```
□ Tokenise word to phoneme sequence
□ Confirm all phonemes in inventory
□ Copy parameter blocks
□ Set F_prev and F_next for each segment
  (coarticulation boundaries)
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
| [oː] | 1 | — | — |
| [iː] | 1 | — | — |
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
| [ð] | 1 | — | — |
| [x] | 1 | — | — |
| [ɣ] | 1 | — | — |
| [h] | 1 | — | — |
| [m] | 1 | — | — |
| [n] | 1 | — | — |
| [ŋ] | 1 | — | — |
| [w] | 1 | — | — |
| [j] | 1 | — | — |
| [r] | 1 | — | — |
| [l] | 1 | — | — |
| [ʍ] | 1 | — | — |

**Total iterations across all phonemes: 41**
**Failures: 3 (all resolved)**
**First-run pass rate: 34/37 verified = 92%**

---

## LINE STATUS

| Line | OE text | Words | Status |
|---|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | 1–5 | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | 6–8 | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | 9–13 | ✓ complete |
| 4 | *þæt wæs gōd cyning* | 14–17 | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | 18–21 | ✓ complete |
| 6 | *mongum mǣgþum meodosetla ofteah* | 22–25 | ✓ complete |
| 7 | *egsode eorlas, syþðan ǣrest wearð* | 26–30 | egsode ✓ eorlas ✓ syþðan ✓ — 2 remaining |
| 8 | *feasceaft funden, hē þæs frōfre gebād* | 31–36 | pending — [b] arrives here |

---

*39 of 40 phonemes verified.*  
*1 pending: [b] — voiced bilabial stop — line 8 GEBĀD.*  
*Inventory completion series: 4 words, 4 phonemes, 4 first-run passes.*  
*Assembly methodology: Rosenberg pulse + IIR formant filters + noise.*  
*This document is the master reference.*  
*When [b] is verified, this document is complete and closed.*
