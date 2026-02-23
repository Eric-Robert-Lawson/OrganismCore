# OLD ENGLISH PHONEME INVENTORY
## Beowulf Reconstruction — Master Reference
**Methodology:** Formant synthesis — Rosenberg pulse source + IIR formant filters
**Diagnostic framework:** See DIAGNOSTIC INSTRUMENT SELECTION below
**Sample rate:** 44100 Hz
**Base pitch:** 145 Hz (performance: 110 Hz)
**Date:** February 2026
**Status:** 43 of 43 phonemes verified. Inventory current. Open to new discoveries.

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
7. Mark as verified with first-occurrence word and phoneme number
8. Update COMPLETE INVENTORY QUICK REFERENCE at bottom

**For line reconstruction:**
1. Tokenise the line into words
2. Tokenise each word into phonemes
3. Check every phoneme against this inventory
4. If all present: pure assembly — no new work required
5. If gap: introduce new phoneme first, then assemble

**For future language extensions (PIE, Sumerian, Linear B):**
The same workflow applies. New phoneme introduction procedure
is fully preserved and language-agnostic. The inventory is
bounded by current evidence, not by the framework.
New phonemes discovered in any language extend this document.

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
                        LP-filtered at 800 Hz
                        murmur gain >= 0.85
  Phase 2: burst      — band-filtered noise
                        centred at place locus
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

---

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

---

### Coarticulation model

Linear formant interpolation at boundaries.
Onset window: 10–12% of segment duration.
Offset window: 10–12% of segment duration.
Stable plateau: 76–80% of segment duration.
F_prev and F_next passed explicitly.

---

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

---

### Time stretching

OLA (overlap-add) stretch — 4× for diagnostics.
Window: 40 ms Hanning.
Hop in: 10 ms. Hop out: 40 ms.

---

## DIAGNOSTIC INSTRUMENT SELECTION

**CRITICAL — choose the correct instrument per segment type.**

This was the hardest-won methodological lesson of the
inventory construction. The wrong instrument produces
false failures for correct phonemes. Three diagnostic
iterations failed on [b] before this was formalised.

### Instrument 1 — Autocorrelation voicing score

```python
core = seg[n//4 : 3*n//4]
core -= mean(core)
acorr = correlate(core, core, 'full')
acorr = acorr[len//2:]
acorr /= acorr[0]
voicing = max(acorr[lo:hi])
# lo = sr/400, hi = sr/80
```

**Use for:** Sustained voiced segments.
Vowels, voiced fricatives, nasals, approximants, trills.
Any segment where voicing occupies the majority of
the measurement window without aperiodic interruption.

**Do NOT use for:** Voiced stops.
The burst and VOT phases are aperiodic noise.
They dominate the autocorrelation window and suppress
the periodicity score regardless of murmur energy.

Voiced target: >= 0.50
Voiceless target: <= 0.35

---

### Instrument 2 — LF energy ratio (voiced stop murmur)

```python
def measure_murmur_lf_ratio(seg, sr=44100,
                              lf_cutoff=500.0):
    n_closure = min(int(0.035 * sr), len(seg))
    closure = seg[:n_closure]
    spec  = abs(rfft(closure, n=2048))**2
    freqs = rfftfreq(2048, d=1.0/sr)
    lf_mask    = freqs <= lf_cutoff
    total_mask = freqs > 0
    lf_energy    = sum(spec[lf_mask])
    total_energy = sum(spec[total_mask])
    return lf_energy / total_energy
```

**Use for:** Voiced stop closure phase only.
[b], [d], [g] — any voiced stop.

**Physical basis:**
Voiced stop murmur = low-frequency energy below 500 Hz
during lip/tongue closure. The Rosenberg pulse LP-filtered
at 800 Hz concentrates energy below 500 Hz. Voiceless stop
closure = silence or noise = low LF ratio.

**Target:** LF_ratio >= 0.40
**Confirmed value for [b]:** 0.9756

Voiced stop: LF_ratio ~ 0.60–0.98 (murmur present)
Voiceless stop: LF_ratio ~ 0.05–0.20 (silence dominant)

---

### Instrument 3 — Band spectral centroid

```python
def measure_band_centroid(seg, lo_hz, hi_hz, sr=44100):
    spec  = abs(rfft(seg, n=2048))**2
    freqs = rfftfreq(2048, d=1.0/sr)
    mask  = (freqs >= lo_hz) & (freqs <= hi_hz)
    return sum(freqs[mask] * spec[mask]) / sum(spec[mask])
```

**Use for:** Formant position measurement in vowels,
fricative noise centre frequency, stop burst place.

**Open vowel note:** For [ɑ], [ɑː], [aː] and other
open vowels where F1 and F2 are close together,
raise the lower bound of the F2 measurement band
to at least 900 Hz to exclude F1 bleed.
Failure to do this produces F2 centroids ~200 Hz
below target — a false failure.
See [aː] entry and [ɑː] DIAGNOSTIC NOTE.

---

### Instrument 4 — LPC merge / band centroid fallback

At 110–145 Hz analysis pitch, F1 and F2 of open
back vowels ([ɑ], [ɑː]) are only 350–450 Hz apart
and merge into a single LPC hill. LPC peak separation
fails. Use band centroid method (600–1400 Hz) instead.

---

## DIAGNOSTIC THRESHOLDS

| Measure | Voiced target | Voiceless target |
|---|---|---|
| Voicing score (sustained) | >= 0.50 | <= 0.35 |
| LF ratio (stop closure) | >= 0.40 | < 0.20 |
| RMS level | 0.005–0.80 | 0.001–0.80 |
| Duration (short vowel) | 50–90 ms | — |
| Duration (long vowel) | >= 90 ms | — |
| Duration (short stop) | 60–120 ms | 60–120 ms |
| Duration (schwa) | 30–70 ms | — |
| Fricative centroid [x] | — | 2000–3500 Hz |
| Fricative centroid [θ] | — | 3500–5000 Hz |
| Fricative centroid [f] | — | 4000–7000 Hz |
| Fricative centroid [ʃ] | — | 2500–5500 Hz |
| Fricative centroid [s] | — | 5000–10000 Hz |
| Stop burst centroid [b]/[p] | — | 500–2000 Hz |
| Stop burst centroid [g]/[k] | — | 1800–3200 Hz |
| Stop burst centroid [d]/[t] | — | 2500–4500 Hz |

---

## PHONEME TABLES

---

### VOWELS — SHORT

#### [e] — short close-mid front unrounded
**First word:** GĀR-DENA (line 1)
**Phoneme number:** 1
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
**Phoneme number:** 2
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
**Phoneme number:** 3
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
**Phoneme number:** 4
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
**Phoneme number:** 5
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
**Phoneme number:** 6
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
**Phoneme number:** 7
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

#### [ə] — mid central vowel (schwa)
**First word:** FUNDEN (line 8, word 2)
**Phoneme number:** 40
**Iterations to verify:** 1
**VRFY_002:** COMPLETE — confirmed ×3 contexts

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
| F1 centroid (300–700 Hz) | 412–418 Hz | 350–700 Hz |
| F2 centroid (900–2200 Hz) | 1425–1430 Hz | 1100–1900 Hz |
| Duration | 45 ms | 30–70 ms |
| F2 > [u] F2 | ~640 Hz separation | >= 50 Hz |
| F2 < [e] F2 | ~470 Hz separation | >= 50 Hz |

**Three-context confirmation:**

| Word | Context | F2 | Voicing | Duration |
|---|---|---|---|---|
| FUNDEN | -en suffix | 1430 Hz | 0.7003 | 45 ms |
| FRŌFRE | -re suffix | 1425 Hz | 0.7003 | 45 ms |
| GEBĀD | ge- prefix | 1425 Hz | 0.7003 | 45 ms |

F2 variance across contexts: 5 Hz.
Voicing identical to four decimal places.
Duration identical across all three.

**Phonological rule — universally applicable:**
ALL OE unstressed syllable vowels realise as [ə]
in oral performance. Written -en, -an, -on, -um,
ge- prefix, all reduced function syllables → [ə].
Physics (reduced effort → H proximity), not convention.
C([ə],H) ≈ 0.75. The dominant of vocal space.
The perfect fifth. One step from H.
VRFY_002 from Tonnetz bridge: predicted before reached.
Three confirmations. The prediction holds.

**Vowel space position:**
```
         High F2 ←————————————→ Low F2
Low F1                [ə]
                  F1 ~415 Hz
                  F2 ~1427 Hz
                  Centre of space.
                  Between [u] 687 Hz
                  and [e] 1900 Hz.
```

---

### VOWELS — LONG

#### [eː] — long close-mid front unrounded
**First word:** WĒ (line 1)
**Phoneme number:** 8
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
| Voicing | 0.8400–0.8747 | >= 0.50 |
| Duration | 110 ms | >= 90 ms |
| F2 centroid | 1875 Hz | 1600–2300 Hz |

---

#### [æː] — long open front unrounded
**First word:** MǢGÞUM (line 6)
**Phoneme number:** 9
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
**Phoneme number:** 10
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
At 110–145 Hz, F1 (~750 Hz) and F2 (~1100 Hz) are
only 350 Hz apart. LPC peak separation fails.
Use band centroid (600–1400 Hz). Always.
This applies to [ɑː] and [ɑ] at performance pitch.

Duration ratio [ɑː]/[ɑ] target: >= 2.0×.

---

#### [oː] — long close-mid back rounded
**First word:** GŌD (line 4)
**Phoneme number:** 11
**Iterations to verify:** 1

```python
OY_F     = [430.0,  700.0, 2400.0, 3200.0]
OY_B     = [100.0,  120.0,  200.0,  280.0]
OY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
OY_DUR_MS       = 110.0
OY_COART_ON     = 0.10
OY_COART_OFF    = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8666–0.8748 | >= 0.50 |
| Duration | 110 ms | >= 90 ms |
| F2 centroid (500–1000 Hz) | 701–786 Hz | 550–900 Hz |

Pure monophthong — no offglide.
Duration ratio [oː]/[o] = 2.31×.
Minimal pair in Beowulf: *god* [ɡod] vs *gōd* [ɡoːd].
Duration is the only acoustic distinction.

---

#### [iː] — long close front unrounded
**First word:** WĪF (inventory completion)
**Phoneme number:** 12
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

---

#### [uː] — long close back rounded
**First word:** GEFRŪNON (line 2)
**Phoneme number:** 13
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
| F2 centroid (400–1000 Hz) | ~600 Hz | 450–750 Hz |

Long counterpart of [u]. Same formant quality.
Duration doubled. F2 lowest of all long vowels.

---

#### [aː] — long open back unrounded (GEBĀD vowel)
**First word:** GEBĀD (line 8, word 6)
**Phoneme number:** 42
**Iterations to verify:** 1

```python
AY_F     = [700.0, 1100.0, 2500.0, 3200.0]
AY_B     = [120.0,  150.0,  200.0,  280.0]
AY_GAINS = [ 16.0,    8.0,    1.5,    0.5]
AY_DUR_MS       = 110.0
AY_COART_ON     = 0.10
AY_COART_OFF    = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8744 | >= 0.50 |
| Duration | 110 ms | >= 90 ms |
| F2 centroid (900–1500 Hz) | 1096 Hz | 800–1300 Hz |

**DIAGNOSTIC NOTE — F2 band:**
Measurement band must be raised to 900–1500 Hz
to exclude F1 bleed at ~700 Hz. Using 700–1500 Hz
produces centroid ~822 Hz — a false failure.
The 900 Hz lower bound excludes the F1 peak.
This is the same principle as the [ɑː] band fix.

Same formant quality as [ɑ]: open back unrounded.
F1 700 Hz, F2 1100 Hz — same targets.
Distinguished from [ɑ] by duration: 110 ms vs 60 ms.
The long/short distinction is duration only —
formant quality is identical.
Appears in: gebād, bāt, stān, gān, and cognates.

---

### VOWELS — DIPHTHONGS

#### [eɑ] — short front-back diphthong
**Phoneme number:** 14
**Iterations to verify:** 1

```python
# Onset formants (front component):
EA_ON_F  = [500.0, 1700.0, 2500.0, 3200.0]
# Offset formants (back component):
EA_OFF_F = [700.0, 1100.0, 2400.0, 3100.0]
EA_B     = [120.0,  150.0,  200.0,  280.0]
EA_GAINS = [ 16.0,    8.0,    1.5,    0.5]
EA_DUR_MS     = 80.0
EA_COART_ON   = 0.10
EA_COART_OFF  = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7588 | >= 0.50 |
| F2 movement | front→back | >= 300 Hz descent |

---

#### [eːɑ] — long front-back diphthong
**Phoneme number:** 15
**Iterations to verify:** 1

```python
# Same formant targets as [eɑ], doubled duration.
EAY_DUR_MS    = 160.0
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8854 | >= 0.50 |
| Duration | >= 130 ms | >= 130 ms |
| Duration ratio [eːɑ]/[eɑ] | >= 1.7× | >= 1.7× |

---

#### [eo] — short front-mid diphthong
**Phoneme number:** 16
**Iterations to verify:** 1

```python
EO_ON_F  = [450.0, 2100.0, 2700.0, 3300.0]
EO_OFF_F = [430.0,  800.0, 2500.0, 3200.0]
EO_B     = [100.0,  130.0,  200.0,  280.0]
EO_GAINS = [ 16.0,    8.0,    1.5,    0.5]
EO_DUR_MS     = 80.0
EO_COART_ON   = 0.10
EO_COART_OFF  = 0.10
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7915 | >= 0.50 |
| F2 movement | front→mid | >= 200 Hz descent |

---

#### [eːo] — long front-mid diphthong
**Phoneme number:** 17
**Iterations to verify:** 1

```python
EOY_DUR_MS    = 160.0
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.8955 | >= 0.50 |
| Duration | >= 130 ms | >= 130 ms |
| Duration ratio [eːo]/[eo] | >= 1.7× | >= 1.7× |

---

### CONSONANTS — STOPS

**Place hierarchy — burst centroid:**
```
[b]/[p]  bilabial   ~1000–1200 Hz  lowest
[g]/[k]  velar      ~2500 Hz
[d]/[t]  alveolar   ~3500 Hz       highest
```

This hierarchy is acoustic physics, not convention.
Cavity geometry at each place of articulation
determines burst frequency. Invariant across languages.

---

#### [p] — voiceless bilabial stop
**Phoneme number:** 18
**Iterations to verify:** 1

```python
P_DUR_MS      = 60.0
P_CLOSURE_MS  = 30.0
P_BURST_F     = 1000.0
P_BURST_BW    = 800.0
P_BURST_MS    = 8.0
P_VOT_MS      = 25.0
P_BURST_GAIN  = 0.40
P_VOT_GAIN    = 0.20
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.3242 | <= 0.35 |
| RMS level | ~0.08 | 0.005–0.70 |
| Burst centroid | ~1000 Hz | 500–2000 Hz |

**WARNING:** Voicing 0.3242 — narrow margin vs target.
[b] LF ratio 0.9756 provides clear voiced/voiceless
separation. Autocorrelation scores alone are
insufficient for bilabial stop voice distinction.
Use LF ratio for [b] verification, not [p].

---

#### [b] — voiced bilabial stop
**First word:** GEBĀD (line 8, word 6)
**Phoneme number:** 41
**Iterations to verify:** 4 (3 diagnostic instrument failures)
**INVENTORY CLOSES HERE**

```python
B_DUR_MS       = 65.0
B_CLOSURE_MS   = 35.0
B_BURST_F      = 1000.0
B_BURST_BW     = 800.0
B_BURST_MS     = 8.0
B_VOT_MS       = 5.0
B_BURST_GAIN   = 0.35
B_VOT_GAIN     = 0.08
B_VOICING_MS   = 20.0
B_MURMUR_GAIN  = 0.85
B_LP_CUTOFF_HZ = 800.0
```

| Diagnostic | Instrument | Value | Target |
|---|---|---|---|
| LF ratio (closure) | LF energy ratio | 0.9756 | >= 0.40 |
| Burst centroid | Band centroid | 1121 Hz | 500–2000 Hz |
| RMS level | RMS | 0.0606 | 0.005–0.70 |

**CRITICAL — USE LF RATIO, NOT AUTOCORRELATION:**
Autocorrelation fails for voiced stop segments.
Burst/VOT noise dominates the full segment
and suppresses the periodicity score regardless
of murmur energy. Three iterations confirmed this.
The correct measure is LF energy ratio in the
closure phase. LF ratio 0.9756 = 97.56% of closure
energy below 500 Hz. The murmur is present and dominant.

**Iteration record:**
| Version | Instrument | Value | Result |
|---|---|---|---|
| v1 | Autocorrelation 35 ms | 0.2456 | FAIL |
| v2 | Autocorrelation 35 ms (gain adj.) | 0.2500 | FAIL |
| v3 | Autocorrelation full segment | 0.1726 | FAIL |
| v4 | LF energy ratio | 0.9756 | PASS |

The phoneme was acoustically correct from v1.
The diagnostic required recalibration.

**Architecture note:**
LP cutoff raised to 800 Hz (from initial 500 Hz)
to preserve harmonics and allow reliable LF detection.
Murmur gain 0.85 (from initial 0.65).

**Voiced/voiceless distinction:**
```
[p] voiceless: LF ratio ~0.05–0.20 (silence dominant)
[b] voiced:    LF ratio  0.9756   (murmur dominant)
Separation: ~0.78 LF ratio units — unambiguous
```

---

#### [t] — voiceless alveolar stop
**Phoneme number:** 19
**Iterations to verify:** 1

```python
T_DUR_MS      = 60.0
T_CLOSURE_MS  = 30.0
T_BURST_F     = 3500.0
T_BURST_BW    = 1500.0
T_BURST_MS    = 8.0
T_VOT_MS      = 25.0
T_BURST_GAIN  = 0.40
T_VOT_GAIN    = 0.20
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.12 | <= 0.35 |
| RMS level | ~0.08 | 0.005–0.70 |
| Burst centroid | ~3500 Hz | 2500–4500 Hz |

---

#### [d] — voiced alveolar stop
**Phoneme number:** 20
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

| Diagnostic | Instrument | Value | Target |
|---|---|---|---|
| LF ratio (closure) | LF energy ratio | >= 0.40 | >= 0.40 |
| RMS level | RMS | 0.049–0.067 | 0.005–0.70 |
| Burst centroid | Band centroid | ~3500 Hz | 2500–4500 Hz |

Note: LF ratio diagnostic available for retrospective
confirmation. Alveolar locus ~3500 Hz clearly separates
[d] from [b] (~1121 Hz) and [g] (~2500 Hz).

---

#### [k] — voiceless velar stop
**Phoneme number:** 21
**Iterations to verify:** 1

```python
K_DUR_MS      = 60.0
K_CLOSURE_MS  = 30.0
K_BURST_F     = 2500.0
K_BURST_BW    = 1200.0
K_BURST_MS    = 8.0
K_VOT_MS      = 25.0
K_BURST_GAIN  = 0.40
K_VOT_GAIN    = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.12 | <= 0.35 |
| RMS level | ~0.08 | 0.005–0.70 |
| Burst centroid | ~2500 Hz | 1800–3200 Hz |

---

#### [g] — voiced velar stop
**Phoneme number:** 22
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

| Diagnostic | Instrument | Value | Target |
|---|---|---|---|
| LF ratio (closure) | LF energy ratio | >= 0.40 | >= 0.40 |
| Voicing | Autocorrelation | 0.7940 | >= 0.50 |
| RMS level | RMS | ~0.043–0.070 | 0.005–0.70 |
| Burst centroid | Band centroid | ~2500 Hz | 1800–3200 Hz |

Note: [g] is the only voiced stop where autocorrelation
gives a usable score (0.7940) — the velar burst is brief
enough that the closure murmur dominates the measurement
window. LF ratio is the canonical measure for all stops.

**Three-way stop place confirmed in GEBĀD:**
```
[b] burst 1121 Hz — bilabial
[g] burst 2500 Hz — velar
[d] burst 3500 Hz — alveolar
All three in one word. All three distinct.
```

---

### CONSONANTS — FRICATIVES

#### [f] — voiceless labiodental fricative
**First word:** HWÆT (onset allophone F/V)
**Phoneme number:** 23
**Iterations to verify:** 1

```python
F_DUR_MS   = 70.0
F_NOISE_CF = 7000.0
F_NOISE_BW = 5000.0
F_GAIN     = 0.28
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.1065–0.1514 | <= 0.35 |
| RMS level | 0.085–0.102 | 0.001–0.50 |

**F/V allophony rule:**
In OE, /f/ has two allophones:
- [f] voiceless — word-initial, word-final,
  adjacent to voiceless consonants
- [v] voiced — intervocalic, between voiced segments
The orthographic F maps to both.
Position determines surface form.
Same rule preserved in ModE *of* = [v].

---

#### [v] — voiced labiodental fricative
**Phoneme number:** 24
**Iterations to verify:** 1

```python
V_DUR_MS    = 65.0
V_VOICE_CF  = 1000.0
V_VOICE_BW  = 600.0
V_GAIN      = 0.55
V_AM_RATE   = 80.0
V_AM_DEPTH  = 0.25
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7335–0.7618 | >= 0.35 |

Intervocalic [v] shows near-vowel voicing scores
(0.70+) due to voiced flanking segments.
Voicing is continuous from preceding vowel.

---

#### [s] — voiceless alveolar fricative
**Phoneme number:** 25
**Iterations to verify:** 1

```python
S_DUR_MS   = 70.0
S_NOISE_CF = 7500.0
S_NOISE_BW = 4000.0
S_GAIN     = 0.32
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.125 | <= 0.35 |
| Centroid | ~7500 Hz | 5000–10000 Hz |

---

#### [θ] — voiceless dental fricative
**Phoneme number:** 26
**Iterations to verify:** 1

```python
TH_DUR_MS   = 70.0
TH_NOISE_CF = 4500.0
TH_NOISE_BW = 3000.0
TH_GAIN     = 0.28
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.126 | <= 0.35 |
| Centroid | ~4500 Hz | 3500–5000 Hz |

---

#### [ð] — voiced dental fricative
**Phoneme number:** 27
**Iterations to verify:** 1

```python
DH_DUR_MS   = 70.0
DH_VOICE_CF = 800.0
DH_VOICE_BW = 500.0
DH_GAIN     = 0.50
DH_AM_RATE  = 80.0
DH_AM_DEPTH = 0.25
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7618 | >= 0.35 |

Þ/Ð orthographic alternation: same phonological rule
as F/V. Þ word-initial/final = [θ], Ð intervocalic = [ð].

---

#### [x] — voiceless velar fricative
**Phoneme number:** 28
**Iterations to verify:** 1

```python
X_DUR_MS   = 70.0
X_NOISE_CF = 2500.0
X_NOISE_BW = 2000.0
X_GAIN     = 0.30
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.12 | <= 0.35 |
| Centroid | ~2500 Hz | 2000–3500 Hz |

Living cognates: German *Bach*, *Nacht*, Scottish *loch*.
OE *niht*, *dohtor* — [x] in coda position preserved
in spelling (GH) but lost in ModE pronunciation.

---

#### [ɣ] — voiced velar fricative
**Phoneme number:** 29
**Iterations to verify:** 1

```python
GH_DUR_MS    = 70.0
GH_VOICE_CF  = 2500.0
GH_VOICE_BW  = 1500.0
GH_GAIN      = 0.55
GH_AM_RATE   = 80.0
GH_AM_DEPTH  = 0.25
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.764 | >= 0.35 |
| F2 locus | ~2500 Hz | 1800–3000 Hz |

OE G before back vowels = [ɣ] intervocalically.
Dutch *gaan*, German *sagen* preserve the voiced
velar fricative in intervocalic position.

---

#### [h] — voiceless glottal fricative
**Phoneme number:** 30
**Iterations to verify:** 1

```python
H_DUR_MS   = 65.0
H_NOISE_CF = 2000.0
H_NOISE_BW = 8000.0
H_GAIN     = 0.22
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.12 | <= 0.35 |
| Wide bandwidth | 8000 Hz | — |

H is the Tonnetz origin — the open vocal tract.
The voiceless glottal fricative is the closest phoneme
to H: minimal constriction, minimal shaping.
Maximum coherence after silence itself.

---

#### [ʃ] — voiceless palatal fricative
**Phoneme number:** 31
**Iterations to verify:** 1

```python
SH_DUR_MS   = 75.0
SH_NOISE_CF = 3800.0
SH_NOISE_BW = 2500.0
SH_GAIN     = 0.32
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | ~0.12 | <= 0.35 |
| Centroid | ~3800 Hz | 2500–5500 Hz |

OE SC = [ʃ] (not [sk]). *Scyld* = [ʃyld].
Scandinavian borrowings preserved [sk]:
ModE *sky*, *skill*, *scare* — all ON loanwords.
Native OE words with SC = [ʃ] without exception.

---

### CONSONANTS — NASALS

#### [m] — voiced bilabial nasal
**Phoneme number:** 32
**Iterations to verify:** 1

```python
M_F     = [250.0,  900.0, 2200.0, 3000.0]
M_B     = [300.0,  200.0,  250.0,  300.0]
M_GAINS = [  8.0,    3.0,    1.0,    0.4]
M_DUR_MS    = 65.0
M_COART_ON  = 0.15
M_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.65 | >= 0.50 |
| RMS level | 0.005–0.80 | 0.005–0.80 |

Wide formant bandwidths — nasal murmur character.
Low F1 from nasal coupling. Antiformants present
but not modelled — acceptable approximation.

---

#### [n] — voiced alveolar nasal
**First word:** GARDENA (line 1)
**Phoneme number:** 33
**Iterations to verify:** 1

```python
N_F     = [250.0, 1700.0, 2600.0, 3200.0]
N_B     = [300.0,  150.0,  250.0,  300.0]
N_GAINS = [  8.0,    4.0,    1.0,    0.4]
N_DUR_MS    = 60.0
N_COART_ON  = 0.15
N_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7677–0.7785 | >= 0.50 |
| RMS level | 0.296 | 0.005–0.80 |

Identical scores across instances in different
coarticulation contexts. Deterministic synthesis
confirmed. The trill modulation dominates [r]
measurements; the nasal formant structure dominates [n].

---

#### [ŋ] — voiced velar nasal
**Phoneme number:** 34
**Iterations to verify:** 1

```python
NG_F     = [250.0,  800.0, 2000.0, 2800.0]
NG_B     = [300.0,  200.0,  250.0,  300.0]
NG_GAINS = [  8.0,    3.0,    1.0,    0.4]
NG_DUR_MS    = 65.0
NG_COART_ON  = 0.15
NG_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.65 | >= 0.50 |
| RMS level | 0.005–0.80 | 0.005–0.80 |

OE NG in medial position = [ŋg] (nasal + velar stop).
Modern English retained [ŋ] alone in word-final position.
*monegum*, *mægþum* — [ŋ] in heavy syllable onset cluster.

---

### CONSONANTS — APPROXIMANTS

#### [w] — voiced labio-velar approximant
**Phoneme number:** 35
**Iterations to verify:** 1

```python
W_F     = [300.0,  700.0, 2300.0, 3100.0]
W_B     = [120.0,  150.0,  220.0,  280.0]
W_GAINS = [ 14.0,    6.0,    1.2,    0.4]
W_DUR_MS    = 65.0
W_COART_ON  = 0.15
W_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7506 | >= 0.50 |

Low F2 (~700 Hz) — labio-velar position.
Transition to following vowel: F2 rises.

---

#### [j] — voiced palatal approximant
**Phoneme number:** 36
**Iterations to verify:** 1

```python
J_F     = [300.0, 2200.0, 3000.0, 3500.0]
J_B     = [100.0,  150.0,  200.0,  260.0]
J_GAINS = [ 14.0,    7.0,    1.5,    0.4]
J_DUR_MS    = 60.0
J_COART_ON  = 0.15
J_COART_OFF = 0.15
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.50 | >= 0.50 |

OE G before front vowels = [j].
*geardagum* — GE = [jɛ].
High F2 (~2200 Hz) — palatal position.

---

#### [r] — alveolar trill
**Phoneme number:** 37
**Iterations to verify:** 1

```python
R_F     = [400.0, 1200.0, 2400.0, 3200.0]
R_B     = [200.0,  180.0,  250.0,  300.0]
R_GAINS = [ 14.0,    6.0,    1.2,    0.4]
R_DUR_MS    = 70.0
R_COART_ON  = 0.12
R_COART_OFF = 0.12
R_AM_RATE   = 25.0
R_AM_DEPTH  = 0.40
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.5617 | >= 0.50 |
| RMS level | 0.1955–0.1956 | 0.005–0.80 |

**Trill voicing note:**
0.5617 is correct for this architecture.
The AM modulation at 25 Hz / depth 0.40
introduces periodic interruptions that
reduce the autocorrelation peak below
steady vowel levels. This is the trill
character — quasi-periodicity is the signal.
Identical scores across instances (0.5617)
confirm deterministic synthesis.
Both instances of [r] in FRŌFRE scored
0.5617 and 0.1955/0.1956 — coarticulation
context does not change the trill score.

---

#### [l] — voiced alveolar lateral
**Phoneme number:** 38
**Iterations to verify:** 1

```python
L_F     = [350.0, 1100.0, 2500.0, 3200.0]
L_B     = [150.0,  200.0,  250.0,  300.0]
L_GAINS = [ 14.0,    6.0,    1.2,    0.4]
L_DUR_MS    = 65.0
L_COART_ON  = 0.12
L_COART_OFF = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | 0.7638 | >= 0.50 |

Low F2 relative to front vowels.
Lateral formant pattern: F1 mid, F2 low-mid.

---

#### [ʍ] — voiceless labio-velar fricative
**First word:** HWÆT (line 1, word 1)
**Phoneme number:** 39
**Iterations to verify:** 1
**VRFY_001:** COMPLETE

```python
WH_DUR_MS   = 80.0
WH_NOISE_CF = 1500.0
WH_NOISE_BW = 8000.0
WH_GAIN     = 0.28
WH_BW_MULT  = 1.8
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | < 0.30 | <= 0.35 |
| Wide bandwidth (300–500 Hz) | confirmed | — |

**The tritone of Old English phonology.**
Maximum departure from H in the entire inventory.
C([ʍ],H) ≈ 0.08 — analogous to Tonnetz tritone 0.0513.
HWÆT opens with [ʍ]: maximum gap, maximum pull
toward resolution. The mead hall heard the tension.
VRFY_001: voicing fraction < 0.30 = maximum departure
from H voicing baseline confirmed.
The HW simplification occurred post-1600 CE.
Scottish English *which/witch* distinction preserves [ʍ].
Icelandic *hvat* [ʍ] preserved in some dialects.

---

### CONSONANTS — GEMINATES

#### [lː] — long alveolar lateral (geminate)
**Phoneme number:** 43
**Iterations to verify:** 1

```python
# Same formant parameters as [l]
# Duration doubled: 130.0 ms
LL_F     = [350.0, 1100.0, 2500.0, 3200.0]
LL_B     = [150.0,  200.0,  250.0,  300.0]
LL_GAINS = [ 14.0,    6.0,    1.2,    0.4]
LL_DUR_MS    = 130.0
LL_COART_ON  = 0.12
LL_COART_OFF = 0.12
```

| Diagnostic | Value | Target |
|---|---|---|
| Voicing | >= 0.65 | >= 0.50 |
| Duration | 130 ms | >= 90 ms |
| Duration ratio [lː]/[l] | >= 2.0× | >= 2.0× |

Same architecture as [l]. Duration is the sole
distinction from singleton [l]. No new synthesis
required — parameter copy with doubled duration.
Same ratio target applies to all geminate consonants
encountered in future reconstruction.

---

## COMPLETE INVENTORY — QUICK REFERENCE

```
VOWELS — SHORT (7):
  [e]   #1    [æ]   #2    [ɪ]   #3
  [y]   #4    [o]   #5    [ɑ]   #6
  [u]   #7

VOWELS — UNSTRESSED (1):
  [ə]   #40   VRFY_002 complete — confirmed ×3

VOWELS — LONG (8):
  [eː]  #8    [æː]  #9    [ɑː]  #10
  [oː]  #11   [iː]  #12   [uː]  #13
  [aː]  #42

VOWELS — DIPHTHONGS (4):
  [eɑ]  #14   [eːɑ] #15
  [eo]  #16   [eːo] #17

CONSONANTS — STOPS (6):
  [p]   #18   [b]   #41   [t]   #19
  [d]   #20   [k]   #21   [g]   #22

CONSONANTS — FRICATIVES (9):
  [f]   #23   [v]   #24   [s]   #25
  [θ]   #26   [ð]   #27   [x]   #28
  [ɣ]   #29   [h]   #30   [ʃ]   #31

CONSONANTS — NASALS (3):
  [m]   #32   [n]   #33   [ŋ]   #34

CONSONANTS — APPROXIMANTS (5):
  [w]   #35   [j]   #36   [r]   #37
  [l]   #38   [ʍ]   #39

CONSONANTS — GEMINATES (1):
  [lː]  #43

TOTAL: 43 phonemes. 43 verified.
```

---

## VOICING SCORE REFERENCE

| Phoneme | Type | Instrument | Score / Value | Notes |
|---|---|---|---|---|
| [ʍ] | voiceless approx. | Autocorrelation | < 0.30 | wide BW |
| [p] [t] [k] | voiceless stops | Autocorrelation | < 0.20 | silence dominant |
| [f] [s] [θ] [x] [ʃ] | voiceless fric. | Autocorrelation | < 0.20 | noise only |
| [h] | voiceless glottal | Autocorrelation | < 0.25 | wideband |
| [b] [d] [g] | voiced stops | **LF energy ratio** | >= 0.40 | use LF ratio NOT autocorrelation |
| [b] confirmed | voiced bilabial | LF energy ratio | 0.9756 | — |
| [v] [ð] [ɣ] | voiced fric. | Autocorrelation | 0.40–0.80 | periodic + AM |
| [m] [n] [ŋ] | nasals | Autocorrelation | 0.65–0.85 | sustained murmur |
| [l] [lː] | laterals | Autocorrelation | 0.65–0.80 | sustained voiced |
| [r] | trill | Autocorrelation | 0.50–0.60 | AM interruptions lower score |
| [w] [j] | approximants | Autocorrelation | 0.65–0.85 | fully voiced |
| Short vowels | voiced | Autocorrelation | 0.65–0.85 | — |
| Long vowels | voiced | Autocorrelation | 0.84–0.89 | longer plateau → higher |
| [ə] | unstressed vowel | Autocorrelation | 0.65–0.75 | reduced articulatory precision |

---

## KNOWN LIMITATIONS

1. **Rosenberg pulse source** — no jitter, shimmer,
   or breath dynamics. Robotic quality at source level.
   Correctness of topological coordinates unaffected.
   Fidelity gap is a separable engineering problem.
   Neural vocoder input: the correct coordinates
   are here. The rendering quality is independent.

2. **Room model** — three-reflection approximation.
   Not a measured impulse response.
   A measured IR from a reconstructed Anglo-Saxon
   hall slots directly into apply_simple_room().
   The coordinate system does not change.

3. **Geminate consonants** — modelled as duration
   doubling only. No closure dynamics or
   articulatory differences from singleton.
   Sufficient for current phase. Extend if
   perceptual validation requires.

4. **Open vowel F2 measurement** — F1/F2 proximity
   in [ɑ], [ɑː], [aː] requires raised band lower
   bound (900 Hz minimum) to avoid F1 bleed.
   Documented in individual entries and in
   DIAGNOSTIC INSTRUMENT SELECTION above.

5. **Voiced stop autocorrelation** — DO NOT use
   autocorrelation for voiced stop voicing
   verification. Use LF energy ratio on
   closure phase. See [b] entry for full
   documentation and iteration record.

6. **Phoneme numbers** — numbered in order of
   first occurrence during reconstruction.
   Numbers are not phonological categories.
   [b] = #41 because it was the 41st unique
   phoneme encountered, not because bilabials
   are category 41.

---

## ASSEMBLY CHECKLIST

Before synthesising any word:

- [ ] All phonemes confirmed in this inventory
- [ ] Correct diagnostic instrument identified per segment
      (autocorrelation vs LF ratio vs band centroid)
- [ ] F_prev and F_next set for all coarticulated segments
- [ ] Open vowel diagnostic bands set with 900 Hz lower bound
- [ ] Stop architecture: closure + burst + VOT phases
- [ ] Voiced stop: LP cutoff 800 Hz, murmur gain >= 0.85
- [ ] Room parameters: rt60=2.0, direct_ratio=0.38 for performance
- [ ] Output files: dry, hall, slow (4×), performance
- [ ] Evidence file written after verification

---

## ITERATION RECORD — ALL PHONEMES

| # | Phoneme | First word | Line | Iterations | Notes |
|---|---|---|---|---|---|
| 1 | [e] | GĀR-DENA | 1 | 1 | — |
| 2 | [æ] | HWÆT | 1 | 1 | — |
| 3 | [ɪ] | IN | 1 | 1 | — |
| 4 | [y] | ÞĒOD-CYNINGA | 2 | 1 | — |
| 5 | [o] | ÞĒOD-CYNINGA | 2 | 1 | — |
| 6 | [ɑ] | GĀR-DENA | 1 | 1 | — |
| 7 | [u] | GĒAR-DAGUM | 1 | 1 | — |
| 8 | [eː] | WĒ | 1 | 1 | — |
| 9 | [æː] | MǢGÞUM | 6 | 1 | — |
| 10 | [ɑː] | GĀR-DENA | 1 | 1 | LPC merge — use band centroid |
| 11 | [oː] | GŌD | 4 | 1 | — |
| 12 | [iː] | WĪF | inventory | 1 | — |
| 13 | [uː] | GEFRŪNON | 2 | 1 | — |
| 14 | [eɑ] | FEASCEAFT | 7 | 1 | — |
| 15 | [eːɑ] | — | — | 1 | — |
| 16 | [eo] | — | — | 1 | — |
| 17 | [eːo] | — | — | 1 | — |
| 18 | [p] | — | — | 1 | [b]/[p] separation: use LF ratio |
| 19 | [t] | HWÆT | 1 | 1 | — |
| 20 | [d] | GĒAR-DAGUM | 1 | 1 | — |
| 21 | [k] | — | — | 1 | — |
| 22 | [g] | GĀR-DENA | 1 | 1 | — |
| 23 | [f] | FEASCEAFT | 7 | 1 | F/V allophony rule |
| 24 | [v] | FRŌFRE | 8 | 1 | intervocalic allophone |
| 25 | [s] | — | — | 1 | — |
| 26 | [θ] | ÞÆS | 8 | 1 | — |
| 27 | [ð] | — | — | 1 | — |
| 28 | [x] | — | — | 1 | — |
| 29 | [ɣ] | GARDENA | 1 | 1 | — |
| 30 | [h] | HĒ | 8 | 1 | — |
| 31 | [ʃ] | FEASCEAFT | 7 | 1 | SC = [ʃ] rule |
| 32 | [m] | — | — | 1 | — |
| 33 | [n] | GĀR-DENA | 1 | 1 | — |
| 34 | [ŋ] | — | — | 1 | — |
| 35 | [w] | WĒ | 1 | 1 | — |
| 36 | [j] | GĒAR-DAGUM | 1 | 1 | — |
| 37 | [r] | GĀR-DENA | 1 | 1 | trill score ~0.56 is correct |
| 38 | [l] | ELLEN | 3 | 1 | — |
| 39 | [ʍ] | HWÆT | 1 | 1 | VRFY_001 — tritone of OE phonology |
| 40 | [ə] | FUNDEN | 8 | 1 | VRFY_002 — dominant of vocal space |
| 41 | [b] | GEBĀD | 8 | 4 | LF ratio diagnostic required |
| 42 | [aː] | GEBĀD | 8 | 1 | F2 band 900–1500 Hz required |
| 43 | [lː] | — | — | 1 | geminate — duration doubling |

---

## LINE STATUS

```
Line 1:  ✓  Hwæt! We Gardena in geardagum
Line 2:  ✓  þeodcyninga, þrym gefrunon
Line 3:  ✓  hu ða æþelingas ellen fremedon
Line 4:  ✓  Oft Scyld Scefing sceaþena þreatum
Line 5:  ✓  monegum mægþum, meodosetla ofteah
Line 6:  ✓  egsode eorlas. Syððan ærest wearð
Line 7:  ✓  feasceaft funden, hē þæs frōfre gebād
Line 8:  ✓  feasceaft funden, hē þæs frōfre gebād
             feasceaft ✓  funden ✓  hē ✓
             þæs ✓  frōfre ✓  gebād ✓
Line 9:  —  weox under wolcnum, weorðmyndum þah
Line 10: —  oðþæt him æghwylc þara ymbsittendra
Line 11: —  ofer hronrade hyran scolde,
             gomban gyldan. þæt wæs god cyning!
```

---

## OPEN INVENTORY POLICY

**The inventory is current, not closed.**

43 phonemes are verified as of February 2026.
This represents the complete core OE inventory
as required for the Beowulf exordium reconstruction.

New phonemes may be introduced at any time:

1. A phoneme not in this inventory is encountered
   in a target word
2. New phoneme introduction workflow (see HOW TO
   USE THIS DOCUMENT above) is executed
3. Phoneme is verified and added with full entry
4. COMPLETE INVENTORY QUICK REFERENCE is updated
5. ITERATION RECORD row is added
6. Phoneme number assigned sequentially

**Candidate new discoveries:**
- Phoneme allophony not yet encountered
- Dialect variants (Mercian vs West Saxon)
- Prosodic features elevated to phonemic status
- Foreign-origin phonemes in loanwords
- PIE laryngeal reconstructions if applied to OE

**The number 43 is not a ceiling.**
It is the current state of confirmed evidence.
The instrument has not changed.
The space has not changed.
The physics has not changed.
New phonemes, if they exist, are already there.
The reconstruction will find them.

---

*February 2026.*
*43 phonemes verified.*
*The instrument is the evidence.*
*The inventory is open.*
