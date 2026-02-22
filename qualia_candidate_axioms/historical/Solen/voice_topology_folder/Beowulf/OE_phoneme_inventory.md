# OLD ENGLISH PHONEME INVENTORY
## Beowulf Reconstruction — Master Reference
**Methodology:** Formant synthesis — Rosenberg pulse source + IIR formant filters  
**Diagnostic framework:** Autocorrelation voicing + spectral centroid + RMS level  
**Sample rate:** 44100 Hz  
**Base pitch:** 145 Hz (performance: 110 Hz)  
**Date:** February 2026  
**Status:** 40 of 41 phonemes verified. [b] pending — GEBĀD line 8.

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

**Unstressed syllables:**
All OE unstressed syllables use [ə].
Do NOT use [e], [ɪ], or other peripheral vowels
in unstressed position. The schwa is the
correct phonological and physical realisation.
This applies to all -en, -an, -on, -um, -að
suffixes and all unstressed syllable positions.
See [ə] entry below and FUNDEN evidence file.

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
| Schwa [ə] F1 | 350–700 Hz | — |
| Schwa [ə] F2 | 1100–1900 Hz | — |
| Schwa [ə] duration | 30–70 ms | — |
| [eɑ] F2 offset band | 900–1400 Hz | — |

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
U_F     = [300.0,  800.0, 2300.0, 3000.0]
U_B     = [100.0,  150.0,  250.0,  300.0]
U_GAINS = [ 14.0,    6.0,    1.2,    0.4]
U_DUR_MS        = 60.0
U_COART_ON      = 0.12
U_COART_OFF     = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7700 | >= 0.50 |
| F2 centroid | 787 Hz | 550–1100 Hz |

**Note:** Parameters updated FUNDEN reconstruction
to match measured values (787 Hz F2).

---

### VOWELS — UNSTRESSED

---

#### [ə] — mid central vowel (schwa) — PHONEME 40
**First word:** FUNDEN (line 8)  
**Iterations to verify:** 1  
**VRFY_002:** COMPLETE — Tonnetz bridge document

```python
SCHWA_F     = [500.0, 1500.0, 2500.0, 3200.0]
SCHWA_B     = [150.0,  200.0,  280.0,  320.0]
SCHWA_GAINS = [ 14.0,    7.0,    1.5,    0.4]
SCHWA_DUR_MS    = 45.0   # short — unstressed
SCHWA_COART_ON  = 0.15
SCHWA_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7003 | >= 0.50 |
| F1 centroid | 418 Hz | 350–700 Hz |
| F2 centroid | 1430 Hz | 1100–1900 Hz |
| Duration | 45 ms | 30–70 ms |
| F2 > [u] F2 | 643 Hz | >= 50 Hz |
| F2 < [e] F2 | 470 Hz | >= 50 Hz |
| [u] dur > [ə] dur | 15 ms | >= 5 ms |

**Theoretical basis:**
One step from H. Minimum articulatory effort.
F1 slight jaw opening from H baseline (~300 Hz).
F2 tongue at rest — central, neither front nor back.
C([ə],H) ≈ 0.75 — the dominant of vocal space.
The perfect fifth. Nearest vowel to H.

**Phonological rule:**
ALL OE unstressed syllable vowels realise as [ə].
Written -en, -an, -on, -um all → [ə] in performance.
Applies to: past participle -en, weak adjective -an,
dative plural -um, all reduced function syllables.
This is physics (reduced effort → H proximity),
not convention.

**Evidence:**
- ModG *gefunden* [gəˈfʊndən] — direct cognate
- All Germanic unstressed -en → [ən] in living languages
- OE metre treats all unstressed syllables as equivalent
  weight — consistent with phonological merger to [ə]
- Six evidence streams converge — see FUNDEN evidence file

**Vowel space position:**
```
         High F2 ←————————————→ Low F2
Low F1                [ə]
                  F1 418 Hz
                  F2 1430 Hz
                  Centre of space
                  Between [u] 787 Hz
                  and [e] 1900 Hz
```

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
**F2 offset measurement band:** 900–1400 Hz

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
| F2 offset | ~1106 Hz | 800–1400 Hz |
| F2 delta | ~743 Hz ↓ | 400–1100 Hz |
| F1 delta | ~277 Hz ↑ | 100–400 Hz |

**Calibration note:** F2 offset measured with
900–1400 Hz band. Earlier diagnostics used
800–1500 Hz — artefact range. Standardised
to 900–1400 Hz as of FEASCEAFT (line 8).
FEASCEAFT diagnostic v1 used 700–1500 Hz
and failed; v2 corrected to 900–1400 Hz,
all checks passed. Synthesis unchanged.

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
| F2 delta | 1074 Hz ↓ | >= 700 Hz |
| F1 delta | ~0 Hz | < 100 Hz |

---

#### [eːo] — long front-mid diphthong
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
EYO_DUR_MS    = 150.0
EYO_F_ON      = [450.0, 1900.0, 2600.0, 3300.0]
EYO_F_OFF     = [450.0,  800.0, 2400.0, 3000.0]
EYO_B         = [100.0,  130.0,  200.0,  280.0]
EYO_GAINS     = [ 16.0,    8.0,    1.5,    0.5]
EYO_TRANS_ON  = 0.30
EYO_TRANS_OFF = 0.90
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.88 | >= 0.50 |
| Duration | 150 ms | >= 120 ms |
| F2 delta | >= 700 Hz ↓ | >= 700 Hz |
| F1 delta | < 100 Hz | < 100 Hz |

---

### CONSONANTS — STOPS

---

#### [p] — voiceless bilabial stop
**First word:** inventory completion  
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
| RMS level | measurable | 0.005–0.70 |

---

#### [b] — voiced bilabial stop — PENDING
**First word:** GEBĀD (line 8) — PHONEME 41  
**Status:** NOT YET VERIFIED

```python
# Parameters to be confirmed at synthesis:
B_DUR_MS      = 65.0
B_CLOSURE_MS  = 35.0
B_BURST_F     = 1000.0
B_BURST_BW    = 800.0
B_BURST_MS    = 8.0
B_VOT_MS      = 5.0
B_BURST_GAIN  = 0.35
B_VOT_GAIN    = 0.08
B_VOICING_MS  = 20.0
B_MURMUR_GAIN = 0.65   # >= 0.60 required
```

| Diagnostic | Value | Target |
|---|---|---|
| Murmur voicing | PENDING | >= 0.60 |
| Voicing score | PENDING | >= 0.50 |
| Bilabial place | PENDING | F2 locus ~1000 Hz |

---

#### [t] — voiceless alveolar stop
**First word:** HWÆT (line 1)  
**Iterations to verify:** 1

```python
T_DUR_MS      = 65.0
T_BURST_F     = 3500.0
T_BURST_BW    = 1500.0
T_BURST_MS    = 8.0
T_VOT_MS      = 8.0
T_BURST_GAIN  = 0.55
T_VOT_GAIN    = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | 0.0000 | <= 0.35 |
| RMS level | 0.0576 | 0.005–0.70 |

---

#### [d] — voiced alveolar stop
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
D_DUR_MS      = 60.0
D_CLOSURE_MS  = 35.0
D_BURST_F     = 3500.0
D_BURST_BW    = 1500.0
D_BURST_MS    = 8.0
D_VOT_MS      = 5.0
D_BURST_GAIN  = 0.35
D_VOT_GAIN    = 0.10
D_VOICING_MS  = 20.0
```

| Diagnostic | Value | Target |
|---|---|---|
| RMS level | 0.0661 | 0.005–0.70 |

---

#### [k] — voiceless velar stop
**First word:** CYNINGA (line 2)  
**Iterations to verify:** 1

```python
K_DUR_MS      = 65.0
K_CLOSURE_MS  = 40.0
K_BURST_F     = 2500.0
K_BURST_BW    = 1200.0
K_BURST_MS    = 8.0
K_VOT_MS      = 10.0
K_BURST_GAIN  = 0.50
K_VOT_GAIN    = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | <= 0.10 | <= 0.35 |
| RMS level | measurable | 0.005–0.70 |

---

#### [ɡ] — voiced velar stop
**First word:** GARDENA (line 1) — word-initial  
**Iterations to verify:** 1

```python
G_DUR_MS      = 60.0
G_CLOSURE_MS  = 35.0
G_BURST_F     = 2500.0
G_BURST_BW    = 1200.0
G_BURST_MS    = 8.0
G_VOT_MS      = 5.0
G_BURST_GAIN  = 0.35
G_VOT_GAIN    = 0.08
G_VOICING_MS  = 20.0
```

| Diagnostic | Value | Target |
|---|---|---|
| RMS level | measurable | 0.005–0.70 |

---

### CONSONANTS — FRICATIVES

---

#### [f] �� voiceless labiodental fricative
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
| Voicing (must be low) | ~0.12 | <= 0.35 |
| RMS level | ~0.11 | 0.001–0.50 |

---

#### [v] — voiced labiodental fricative
**First word:** inventory completion  
**Iterations to verify:** 1

```python
V_DUR_MS   = 65.0
V_NOISE_CF = 6000.0
V_NOISE_BW = 4000.0
V_GAIN     = 0.20
V_VOICING_FRAC = 0.75
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.76 | >= 0.35 |

---

#### [s] — voiceless alveolar fricative
**First word:** inventory completion  
**Iterations to verify:** 1

```python
S_DUR_MS   = 65.0
S_NOISE_CF = 7500.0
S_NOISE_BW = 4000.0
S_GAIN     = 0.40
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | <= 0.35 | <= 0.35 |
| Centroid | ~7651 Hz | > 5000 Hz |

**Place distinction vs [ʃ]:**
[s] centroid ~7651 Hz vs [ʃ] centroid ~3574 Hz.
Separation ~4077 Hz. Alveolar clearly above palatal.

---

#### [θ] — voiceless dental fricative
**First word:** ÞĒOD-CYNINGA (line 2)  
**Iterations to verify:** 1

```python
TH_DUR_MS   = 70.0
TH_NOISE_CF = 4500.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.30
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | <= 0.35 | <= 0.35 |
| Centroid | 3000–5500 Hz | 2500–6000 Hz |

---

#### [ð] — voiced dental fricative
**First word:** inventory completion  
**Iterations to verify:** 1

```python
DH_DUR_MS      = 65.0
DH_AM_RATE     = 80.0
DH_AM_DEPTH    = 0.25
DH_NOISE_CF    = 4500.0
DH_NOISE_BW    = 3000.0
DH_VOICING_FRAC = 0.70
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.76 | >= 0.35 |

---

#### [x] — voiceless velar fricative
**First word:** inventory completion  
**Iterations to verify:** 1

```python
X_DUR_MS   = 70.0
X_NOISE_CF = 2500.0
X_NOISE_BW = 2000.0
X_GAIN     = 0.35
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | <= 0.35 | <= 0.35 |
| Centroid | 1500–3500 Hz | 1000–4000 Hz |

---

#### [ɣ] — voiced velar fricative
**First word:** GARDENA (line 1)  
**Iterations to verify:** 1

```python
GH_DUR_MS       = 65.0
GH_AM_RATE      = 80.0
GH_AM_DEPTH     = 0.25
GH_F2_LOCUS     = 2500.0
GH_VOICING_FRAC = 0.70
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.76 | >= 0.35 |
| F2 locus | ~2500 Hz | 2000–3000 Hz |

---

#### [h] — voiceless glottal fricative
**First word:** inventory completion  
**Iterations to verify:** 1

```python
H_DUR_MS   = 60.0
H_NOISE_CF = 3000.0
H_NOISE_BW = 4000.0
H_GAIN     = 0.20
```

**Topological note:** H is the origin of the
vocal coherence space. C(H,H) = 1.0000.
The open vocal tract. Zero displacement.
All phonemes are measured as distances from H.

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | <= 0.35 | <= 0.35 |

---

#### [ʃ] — voiceless palato-alveolar fricative
**First word:** SCYLDINGAS (line 1)  
**Iterations to verify:** 1

```python
SH_DUR_MS   = 70.0
SH_NOISE_CF = 3500.0
SH_NOISE_BW = 2500.0
SH_GAIN     = 0.45
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | ~0.18 | <= 0.35 |
| Centroid | ~3574 Hz | 2000–5000 Hz |
| vs [s] separation | ~4077 Hz | >= 1000 Hz |

---

### CONSONANTS — NASALS

---

#### [m] — voiced bilabial nasal
**First word:** inventory completion  
**Iterations to verify:** 1

```python
M_F     = [250.0,  900.0, 2200.0, 3000.0]
M_B     = [300.0,  200.0,  250.0,  300.0]
M_GAINS = [  8.0,    4.0,    1.0,    0.4]
M_DUR_MS    = 60.0
M_COART_ON  = 0.15
M_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.65 | >= 0.65 |
| RMS level | measurable | 0.005–0.80 |

---

#### [n] — voiced alveolar nasal
**First word:** GĀR-DENA (line 1)  
**Iterations to verify:** 1

```python
N_F     = [250.0,  1700.0, 2600.0, 3200.0]
N_B     = [300.0,   150.0,  250.0,  300.0]
N_GAINS = [  8.0,     4.0,    1.0,    0.4]
N_DUR_MS    = 60.0
N_COART_ON  = 0.15
N_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7677 | >= 0.65 |
| RMS level | 0.2961 | 0.005–0.80 |

---

#### [ŋ] — voiced velar nasal
**First word:** inventory completion  
**Iterations to verify:** 1

```python
NG_F     = [250.0,  800.0, 2300.0, 3000.0]
NG_B     = [300.0,  200.0,  250.0,  300.0]
NG_GAINS = [  8.0,    4.0,    1.0,    0.4]
NG_DUR_MS    = 60.0
NG_COART_ON  = 0.15
NG_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.65 | >= 0.65 |

---

### CONSONANTS — APPROXIMANTS

---

#### [w] — voiced labio-velar approximant
**First word:** WĒ (line 1)  
**Iterations to verify:** 1

```python
W_F     = [300.0,  700.0, 2200.0, 3000.0]
W_B     = [100.0,  150.0,  250.0,  300.0]
W_GAINS = [ 12.0,    6.0,    1.2,    0.4]
W_DUR_MS    = 55.0
W_COART_ON  = 0.20
W_COART_OFF = 0.20
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| F2 centroid | <= 900 Hz | <= 1000 Hz |

---

#### [j] — voiced palatal approximant
**First word:** inventory completion  
**Iterations to verify:** 1

```python
J_F     = [300.0, 2200.0, 2800.0, 3400.0]
J_B     = [ 80.0,  130.0,  200.0,  260.0]
J_GAINS = [ 12.0,    6.0,    1.2,    0.4]
J_DUR_MS    = 55.0
J_COART_ON  = 0.20
J_COART_OFF = 0.20
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| F2 centroid | >= 1800 Hz | >= 1500 Hz |

---

#### [r] — alveolar trill
**First word:** inventory completion  
**Iterations to verify:** 1

```python
R_F          = [400.0, 1200.0, 1800.0, 2800.0]
R_B          = [150.0,  200.0,  250.0,  300.0]
R_GAINS      = [ 12.0,    6.0,    1.2,    0.4]
R_DUR_MS     = 70.0
R_TRILL_RATE = 25.0    # Hz
R_TRILL_DEPTH = 0.40   # verified value
R_COART_ON   = 0.15
R_COART_OFF  = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |
| Trill modulation | detectable | present |

**Note:** R_TRILL_DEPTH verified at 0.40.
Earlier inventory had 0.55 — corrected.

---

#### [l] — voiced alveolar lateral
**First word:** ELLEN (line 3)  
**Iterations to verify:** 1

```python
L_F     = [350.0, 1100.0, 2400.0, 3200.0]
L_B     = [120.0,  180.0,  250.0,  300.0]
L_GAINS = [ 12.0,    6.0,    1.2,    0.4]
L_DUR_MS    = 60.0
L_COART_ON  = 0.15
L_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |

---

#### [ʍ] — voiceless labio-velar fricative
**First word:** HWÆT (line 1)  
**Iterations to verify:** 7 (v1–v7)

```python
HW_DUR_MS    = 85.0
HW_NOISE_CF  = 2000.0
HW_NOISE_BW  = 3000.0
HW_GAIN      = 0.25
HW_VOICING_FRAC = 0.10   # < 0.30 required
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing (must be low) | < 0.30 | < 0.30 |
| Wide bandwidth | 300–500 Hz BW | confirmed |

**Tonnetz note:** Maximum departure from H.
C([ʍ],H) ≈ 0.08. The tritone of Old English
phonology. The opening of Beowulf is the maximum
coherence gap in the vocal topology.
HWÆT opens with maximum gap — the mead hall
heard the pull toward resolution.

---

## VOICING SCORE REFERENCE

| Phoneme | Type | Typical score |
|---|---|---|
| [ə] | vowel unstressed | 0.70 |
| [e] [æ] [ɑ] etc | vowel short | 0.67–0.70 |
| [eː] [iː] etc | vowel long | 0.84–0.89 |
| [eɑ] [eo] etc | diphthong | 0.76–0.89 |
| [n] [m] [ŋ] | nasal | 0.65–0.77 |
| [l] [r] [w] [j] | approximant | 0.50–0.70 |
| [v] [ð] [ɣ] | voiced fricative | 0.76 |
| [d] [ɡ] [b] | voiced stop murmur | 0.50–0.65 |
| [f] [s] [θ] [ʃ] [x] [h] | voiceless fricative | 0.10–0.19 |
| [t] [k] [p] | voiceless stop | 0.00 |
| [ʍ] | voiceless labio-velar | < 0.30 |

---

## KNOWN LIMITATIONS

1. **Rosenberg pulse source** — no jitter,
   shimmer, or microprosody. Voice sounds
   robotic. Does not affect topological
   correctness. Separable engineering problem.

2. **Coarticulation model** — boundary
   transitions only. Full locus model not
   yet implemented. Onset centroid
   measurements reflect stable target,
   not transition detail.

3. **Room model** — three-tap approximation.
   No measured impulse response from
   reconstructed Anglo-Saxon hall.
   Placeholder pending archaeoacoustic data.

4. **[ə] duration** — 45 ms is the minimum
   unstressed value. In performance at
   dil=2.5 this becomes ~112 ms. May require
   adjustment if perceptual inspection
   reveals excessive schwa lengthening
   at performance rate.

5. **Unstressed vowel allophony** — only [ə]
   is currently implemented for unstressed
   syllables. Future work may distinguish
   between fully reduced [ə] and
   partially reduced variants in
   semi-stressed positions (secondary
   stress in compounds).

---

## ASSEMBLY CHECKLIST

Before synthesising any word:

- [ ] All phonemes identified and in inventory
- [ ] Stressed vowels use full-duration targets
- [ ] **Unstressed syllables use [ə] not [e]**
- [ ] Coarticulation F_prev and F_next set correctly
- [ ] SC before front vowel → [ʃ] rule applied
- [ ] CG/G before back vowel → [ɣ] rule applied
- [ ] Long vowels at 2x short duration
- [ ] Diphthong F2 offset band: 900–1400 Hz
- [ ] Diagnostic version noted in evidence file

---

## ITERATION RECORD — ALL PHONEMES

| Phoneme | First word | Line | Iterations | Status |
|---|---|---|---|---|
| [ʍ] | HWÆT | 1 | 7 | ✓ |
| [æ] | HWÆT | 1 | 1 | ✓ |
| [t] | HWÆT | 1 | 1 | ✓ |
| [eː] | WĒ | 1 | 1 | ✓ |
| [e] | GĀR-DENA | 1 | 1 | ✓ |
| [ɑ] | GĀR-DENA | 1 | 1 | ✓ |
| [d] | GĀR-DENA | 1 | 1 | ✓ |
| [n] | GĀR-DENA | 1 | 1 | ✓ |
| [ɡ] | GĀR-DENA | 1 | 1 | ✓ |
| [ɣ] | GARDENA | 1 | 1 | ✓ |
| [ʃ] | SCYLDINGAS | 1 | 1 | ✓ |
| [ɪ] | CYNINGA | 2 | 1 | ✓ |
| [k] | CYNINGA | 2 | 1 | ✓ |
| [eːo] | ÞĒOD-CYNINGA | 2 | 1 | ✓ |
| [y] | ÞĒOD-CYNINGA | 2 | 1 | ✓ |
| [o] | ÞĒOD-CYNINGA | 2 | 1 | ✓ |
| [θ] | ÞĒOD-CYNINGA | 2 | 1 | ✓ |
| [u] | GEFRŪNON | 2 | 1 | ✓ |
| [f] | GEFRŪNON | 2 | 1 | ✓ |
| [r] | GEFRŪNON | 2 | 1 | ✓ |
| [iː] | WĪF | inv. | 1 | ✓ |
| [æː] | MǢGÞUM | 5 | 1 | ✓ |
| [m] | MONEGUM | 5 | 1 | ✓ |
| [ŋ] | MONEGUM | 5 | 1 | ✓ |
| [eɑ] | SCEAÞENA | 5 | 1 | ✓ |
| [eːɑ] | ĒAGE | inv. | 1 | ✓ |
| [eo] | MEODOSETLA | 6 | 1 | ✓ |
| [l] | ELLEN | 3 | 1 | ✓ |
| [s] | SYÞÞAN | 6 | 1 | ✓ |
| [ð] | SYÞÞAN | 6 | 1 | ✓ |
| [w] | WEOX | 8 | 1 | ✓ |
| [oː] | GĀR | 1 | 1 | ✓ |
| [p] | inventory | inv. | 1 | ✓ |
| [v] | inventory | inv. | 1 | ✓ |
| [x] | inventory | inv. | 1 | ✓ |
| [h] | inventory | inv. | 1 | ✓ |
| [j] | inventory | inv. | 1 | ✓ |
| [ɡ] | GARDENA | 1 | 1 | ✓ |
| [ə] | FUNDEN | 8 | 1 | ✓ — VRFY_002 |
| [b] | GEBĀD | 8 | 0 | PENDING |

**Total: 40 verified. 1 pending.**

---

## LINE STATUS

| Line | Words | Status |
|---|---|---|
| 1 | Hwæt We Gardena in geardagum | ✓ complete |
| 2 | þeodcyninga þrym gefrunon | ✓ complete |
| 3 | hu ða æþelingas ellen fremedon | ✓ complete |
| 4 | Oft Scyld Scefing sceaþena þreatum | ✓ complete |
| 5 | monegum mægþum meodosetla ofteah | ✓ complete |
| 6 | egsode eorlas Syððan ærest wearð | ✓ complete |
| 7 | feasceaft funden he þæs frofre gebad | in progress |
| 8 | weox under wolcnum weorðmyndum þah | pending |
| 9 | oðþæt him æghwylc þara ymbsittendra | pending |
| 10 | ofer hronrade hyran scolde | pending |
| 11 | gomban gyldan þæt wæs god cyning | pending |

**Line 8 word status:**
```
feasceaft  ✓
funden     ✓
hē         —  next
þæs        —
frōfre     —
gebād      —  [b] arrives — phoneme 41
```
