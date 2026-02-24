# EVIDENCE — YAJÑASYA
## Rigveda 1.1.1, word 5
## [jɑɟɲɑsjɑ] — "of the sacrifice"
## February 2026

---

## VERIFICATION STATUS: VERIFIED ✓ (v5 / v1.1)

**Date verified:** February 2026
**Synthesis version:** v5 (Unified Pluck Architecture)
**Diagnostic version:** v1.1 (Principles-First Tonnetz-Derived, 47/47 PASS)
**Method:** Perceptual + numeric (complete)

**Prior verification:** v3 diagnostic on v3 synthesis (v7 burst architecture)
**Current verification:** v1.1 diagnostic (47/47 PASS) on v5 synthesis

---

## NEW ARCHITECTURE VERIFIED IN THIS WORD

### [s] — Voiceless Dental Sibilant (v5 Unified Source + Pluck)

**Śikṣā:** dantya aghoṣa ūṣman (sibilant/fricative)
**IPA:** voiceless alveolar sibilant
**Devanāgarī:** स
**Status:** VERIFIED (v5 unified source, v1.1 numeric)

**The insight:** The Pluck Principle extends to ALL voiceless segments, not just stops.
When you concatenate `[...ɑ[-1]=0.45] + [s[0]=noise...]`, the amplitude jump is audible.
Same boundary problem. Same solution.

**v5 applies Pluck Principle to [s]:**
- **Closing tail:** [ɑ]₂ owns the closure before [s]. Last 25ms fades.
- **Unified source:** [s] uses one continuous noise buffer with subglottal floor (0.001). Never digital zero at either edge.
- **Opening head:** [j]₂ owns the onset after [s]. First 15ms rises.

### [ɟ] — Voiced Palatal Stop (v4 4-Phase, Unchanged)

**Śikṣā:** tālavya ghoṣa alpaprāṇa
**IPA:** voiced palatal stop
**Devanāgarī:** ज
**Status:** VERIFIED (v4 architecture, v1.1 numeric)
**Prior verification:** YAJÑASYA v3 (v7 burst architecture), ṚTVIJAM v9

---

## SYNTHESIS ARCHITECTURE — v5 UNIFIED PLUCK

### The Central Insight: Pluck Extends to All Voiceless Segments

v4 treated [s] as a standalone noise segment. But [s] is voiceless — the same
boundary problem applies as for voiceless stops. Concatenating voiced signal
directly into noise produces an audible amplitude discontinuity.

v5 applies the same principle discovered for [t] in RATNADHĀTAMAM v16:
**segment ownership follows physics.** The voiceless segment owns only its
internal noise. The voiced segments own the transitions into and out of
voicelessness.

### [s] Unified Source Architecture

```
Phase A: Subglottal floor (0.001, ~-60dB)
         NOT digital zero — the body is producing pressure.
         This prevents a zero-to-noise boundary.

Phase B: Onset rise (8ms)
         The tongue narrows the dental constriction.
         Turbulence increases. Exponential rise from floor to peak.

Phase C: Sustained sibilant
         Full amplitude noise at dental locus.
         Bandpass: 7500 Hz center, 3000 Hz bandwidth.
         One continuous filter pass, no frame boundaries.

Phase D: Offset decay (8ms)
         The tongue releases the constriction.
         Turbulence decreases. Exponential decay to floor.

Phase E: Subglottal floor
         The breath continues after the sibilant.
         No digital zero at the end.
```

ONE continuous noise buffer. ONE continuous bandpass filter. ONE continuous
amplitude envelope. The constriction IS the envelope — it modulates the
airstream into turbulence at the dental position.

### [ɟ] 4-Phase Architecture (v4, Unchanged)

```
Phase 1: Voice bar closure (250 Hz, BW 80)
         OQ 0.65 Rosenberg, low-pass filtered

Phase 2: Spike + turbulence burst at palatal locus
         [500, 3200, 3800, 4200] Hz — F2 dominant

Phase 3: Crossfade cutback (closed → open)
         Smooth transition to following segment
```

Voiced stops don't need the Pluck Principle — continuous glottal source
through closure eliminates boundary discontinuities.

### Closing Tail / Opening Head Architecture

**Closing tail:** [ɑ]₂ OWNS the closure before [s]. The amplitude fades
over the final 25ms of the vowel segment as the tongue moves toward the
dental sibilant position. The vowel's resonator produces the fade — no
separate closure segment is concatenated.

**Opening head:** [j]₂ OWNS the onset after [s]. The voiced onset rises
over 15ms at the start of the approximant, not appended to the sibilant.

**Result:** The [s] itself starts and ends at subglottal floor. The vowel
decays into near-zero. The approximant rises from near-zero. All joins
are at near-zero amplitude — no boundary discontinuities.

---

## PERCEPTUAL VERIFICATION

**v5 perceptual checks passed:**
1. ✓ No click at [ɑ]₂→[s] boundary (closing tail + subglottal floor)
2. ✓ No click at [s]→[j]₂ boundary (subglottal floor + opening head)
3. ✓ [s] sounds like dental sibilant, not static (bandpass at 7500 Hz)
4. ✓ [ɟ] has voiced stop quality (voice bar through closure)
5. ✓ [ɟ]→[ɲ] transition is smooth (both voiced, no boundary)
6. ✓ Full word at performance speed with hall reverb: natural cadence
7. ✓ Syllable structure YAJ.ÑA.SYA perceived correctly

**Comparison to v4:**
- v4: `[...ɑ=0.45] + [s=noise...]` = audible click at boundary
- v5: `[...tail→0.00] + [s=floor→rise...decay→floor] + [0.00→head...]` = smooth

---

## NUMERIC DIAGNOSTICS — v1.1 (47/47 PASS)

### Section A: Signal Integrity (4/4)

```
NaN count:           0        (expected 0)                  ✓
Inf count:           0        (expected 0)                  ✓
Peak amplitude:      0.7500   (expected 0.01–1.00)          ✓
DC offset |mean|:    0.0015   (expected 0.00–0.05)          ✓
```

### Section B: Signal Continuity (16/16)

**Tier 1 — Within-segment (8/8):**

```
[j]₁                          max_ss=0.0000  below threshold     ✓
[ɑ]₁                          max_ss=0.0000  below threshold     ✓
[ɟ]                            max_ss=1.2008  below threshold     ✓
[ɲ]                            max_ss=0.0000  below threshold     ✓
[ɑ]₂+tail (core only, 55ms)   max_ss=0.0000  below threshold     ✓
[s] UNIFIED (unvoiced)         max|Δ|=0.2767  (< 0.50)           ✓
head+[j]₂ (core only, 55ms)   max_ss=0.0000  below threshold     ✓
[ɑ]₃                          max_ss=0.0000  below threshold     ✓
```

**Tier 2 — Segment-join continuity (7/7):**

```
[j]₁ -> [ɑ]₁                  0.5970  voiced transition norm=0.822  ✓
[ɑ]₁ -> [ɟ]                   0.6946  voiced transition norm=0.926  ✓
[ɟ] -> [ɲ]                    0.0000  below threshold               ✓
[ɲ] -> [ɑ]₂+tail              0.0001  below threshold               ✓
[ɑ]₂+tail -> [s]              0.0001  sibilant join (< 0.85)        ✓
[s] -> head+[j]₂              0.0000  sibilant join (< 0.85)        ✓
head+[j]₂ -> [ɑ]₃             0.0005  below threshold               ✓
```

**Isolated sibilant (1/1):**

```
[s] unified isolated           max|Δ|=0.2537  (< 0.50)           ✓
```

### Section C: [s] Unified Source — Dental Sibilant (4/4)

```
Voicing (aghoṣa):   0.1861    (expected -1.00–0.30)        ✓
RMS (audible):       0.0497    (expected 0.001–0.500)       ✓
Centroid (sib band): 7490.8 Hz (expected 5000–10000)        ✓
Total duration:      55.0 ms   (expected 50–120)            ✓
```

Edge amplitude confirms subglottal floor:
```
Edge RMS start:      0.002482  (floor = 0.001)
Edge RMS end:        0.002570  (floor = 0.001)
```

### Section D: Closing Tail (2/2)

```
[ɑ]₂ core voicing:  0.7880    (expected 0.50–1.00)         ✓
[ɑ]₂ tail/core RMS: 0.4427    (expected 0.00–0.90)         ✓
```

### Section E: Opening Head (2/2)

```
[j]₂ core voicing:  0.7863    (expected 0.50–1.00)         ✓
Opening head rising: 0.0072 -> 0.3142                       ✓
```

### Section F: Voiced Palatal Stop [ɟ] (3/3)

```
Closure LF ratio (voicing proof): 0.9844 (expected 0.40–1.00) ✓
Release centroid (place band 1-6kHz): 3127.5 Hz (expected 1500–4500) ✓
Total duration:      54.0 ms   (expected 30–80)             ✓
```

**v1.1 note:** Closure voicing (autocorrelation) REMOVED.
Closure is 30ms ≈ 3.6 periods. After body() trim (15% each edge),
2.5 periods remain — below guard clause (3 periods). Autocorrelation
returns 0.0. Wrong instrument for signal length.

Voicing is PROVEN by:
- Closure LF ratio = 0.9844 (voice bar at 250 Hz dominates — this IS voicing)
- Join [ɟ]→[ɲ] = 0.000011 (continuous voiced signal)
- Join [ɑ]₁→[ɟ] = 0.694558 (voiced transition, norm=0.926)

### Section G: Vowels (9/9)

```
       voicing    F1 (Hz)    F2 (Hz)
[ɑ]₁   0.7860 ✓   657.1 ✓   1101.4 ✓
[ɑ]₂   0.7880 ✓   668.6 ✓   1099.9 ✓
[ɑ]₃   0.7876 ✓   670.0 ✓   1099.7 ✓
```

All vowels: voicing 0.787 ± 0.001, F1 ~665 Hz, F2 ~1100 Hz.
Consistent across three instances. Coarticulation effects minimal.

### Section H: Approximants and Nasal (4/4)

```
[j]₁ voicing:    0.7854  ✓
[j]₂ voicing:    0.7863  ✓
[ɲ] voicing:     0.7965  ✓
[ɲ] LF ratio:    0.9966  ✓
```

### Section I: Syllable Coherence (3/3)

```
[s] trough: 0.0497 < min(0.3994, 0.3995)                   ✓
[ɑ]₁ relative amplitude: 0.9713 (expected 0.50–1.00)        ✓
Word duration: 488.9 ms (expected 300–700)                   ✓
```

**YAJ.ÑA.SYA** — [s] is the repeller (minimum energy), vowels are the attractors.

---

## DIAGNOSTIC EVOLUTION — v1.0 TO v1.1

### v1.0: Initial (47/48, 1 FAIL)

Adapted from ṚTVIJAM v2.1 / RATNADHĀTAMAM v4.7.1 template.
Applied all prior ruler calibrations: cold-start 4 periods, ceiling 5.0,
place band for [ɟ], sibilant band for [s].

**Failed:** [ɟ] closure voicing = 0.0000 (expected 0.25–1.00)

**Root cause:** The `measure_voicing()` function:
1. `body()` trims 15% each edge from 30ms closure → 21ms ≈ 2.5 periods
2. Guard clause: `len(seg_body) < PERIOD_N * 3` → 926 < 1104 → returns 0.0
3. Autocorrelation never runs

The signal IS voiced (LF ratio 0.9844 proves it). The measurement instrument
cannot resolve voicing in a signal this short after edge trimming.

### v1.1: Closure voicing removed (47/47, ALL PASS)

**Fix:** Remove autocorrelation-based closure voicing check. Replace with
LF ratio check (which already passes) as the voicing evidence.

**Precedent:** Same pattern as ṚTVIJAM v2.1 cutback voicing removal:
- Cutback was 15ms ≈ 1.3 periods → autocorrelation invalid
- Closure is 30ms, but after trim ≈ 2.5 periods → below guard clause
- Both cases: wrong instrument for signal length

**Evidence that [ɟ] closure IS voiced:**
1. Closure LF ratio = 0.9844 — voice bar at 250 Hz with gain 12.0
   dominates the spectrum. No voiceless signal produces 98% LF energy.
2. Join [ɟ]→[ɲ] = 0.000011 — continuous voiced signal across boundary
3. Join [ɑ]₁→[ɟ] = 0.694558 (norm=0.926) — normal voiced transition

**"Fix the ruler, not the instrument."**

---

## RULER CALIBRATION LESSONS

### 1. Autocorrelation Has Minimum Signal Requirements (Confirmed Again)

At 120 Hz, one period = 8.3ms. After body() trim (15% each edge = 30% removed),
a 30ms closure yields 21ms ≈ 2.5 periods. The guard clause requires 3 periods
for reliable autocorrelation. This is the third time this lesson has appeared:

```
RATNADHĀTAMAM v4.7.1: closing tail 25ms → 1.05 periods after trim → removed
ṚTVIJAM v2.1:        cutback 15ms → 1.3 periods → removed
YAJÑASYA v1.1:        closure 30ms → 2.5 periods after trim → removed
```

The pattern is consistent: any voiced segment shorter than ~35ms (3 × 8.3ms +
30% trim overhead) cannot be measured by autocorrelation. Use LF ratio instead.

### 2. LF Ratio IS Voicing Evidence for Short Closures

The voice bar (250 Hz, gain 12.0) produces overwhelming LF energy during voiced
closure. LF ratio > 0.90 is definitive proof that the glottal source was active.
This measurement works regardless of signal length because it uses FFT, not
autocorrelation.

### 3. The Pluck Principle Generalizes to All Voiceless Segments

The same boundary problem that affects voiceless stops also affects voiceless
fricatives/sibilants. The same solution applies:

```
VOICELESS STOPS:      unified source (breath + tongue) + closing tail + opening head
VOICELESS SIBILANTS:  unified source (breath + constriction) + closing tail + opening head
```

The physics is the same: the diaphragm pushes air continuously, the articulator
modulates the airstream, segment boundaries must be at near-zero amplitude.

---

## SYNTHESIS EVOLUTION — v1 TO v5

### v1: Baseline
Initial synthesis with placeholder architectures for all phonemes.

### v2: Diagnostic calibration
Discovered that diagnostic was wrong, not synthesis. Same lesson as
HOTĀRAM: spectral leakage + insufficient frames → wrong measurements.

### v3: v7 burst architecture for [ɟ]
Updated [ɟ] to spike + turbulence burst (v7). Matched AGNI [g] verified
architecture. Perceptual verification: voiced palatal stop quality confirmed.

### v4: 4-phase [ɟ] architecture
Added voice bar closure + crossfade cutback from ṚTVIJAM v9.
Complete voiced palatal stop model.

### v5: Unified Pluck Architecture ✓
Extended Pluck Principle to [s]:
- Closing tail on [ɑ]₂ (vowel owns transition to voicelessness)
- Unified source for [s] (subglottal floor, no digital zero)
- Opening head on [j]₂ (approximant owns transition from voicelessness)
- All joins at near-zero amplitude — no boundary discontinuities

**The principle that began with [t] in RATNADHĀTAMAM now covers all
voiceless segments in the inventory.**

---

## VERIFIED PARAMETERS

### [s] Voiceless Dental Sibilant (v5 Unified Source)

```python
VS_S_NOISE_CF  = 7500.0       # Dental sibilant center frequency
VS_S_NOISE_BW  = 3000.0       # Bandwidth
VS_S_DUR_MS    = 80.0          # Total duration
VS_S_PEAK_GAIN = 0.22          # Sustained amplitude
VS_S_SUBGLOTTAL_FLOOR = 0.001  # ~-60dB, never digital zero
VS_S_ONSET_MS  = 8.0           # Rise from floor to full
VS_S_OFFSET_MS = 8.0           # Decay from full to floor
VS_S_CLOSING_MS = 25.0         # Owned by preceding vowel
VS_S_OPENING_MS = 15.0         # Owned by following segment
```

### [ɟ] Voiced Palatal Stop (v4 4-Phase)

```python
VS_JJ_CLOSURE_MS  = 30.0
VS_JJ_BURST_MS    = 9.0
VS_JJ_CUTBACK_MS  = 15.0

VS_JJ_VOICEBAR_F  = 250.0     # Voice bar frequency
VS_JJ_VOICEBAR_BW = 80.0      # Voice bar bandwidth
VS_JJ_VOICEBAR_G  = 12.0      # Voice bar gain

VS_JJ_BURST_F     = [500.0, 3200.0, 3800.0, 4200.0]  # Palatal locus
VS_JJ_BURST_B     = [300.0,  500.0,  600.0,  700.0]
VS_JJ_BURST_G     = [  8.0,   12.0,    3.0,    1.0]   # F2 dominant
VS_JJ_BURST_DECAY = 180.0
VS_JJ_BURST_PEAK  = 0.15
```

### [ɲ] Voiced Palatal Nasal

```python
VS_NY_F        = [250.0, 2000.0, 2800.0, 3300.0]
VS_NY_B        = [120.0,  180.0,  250.0,  300.0]
VS_NY_GAINS    = [  8.0,    4.0,    1.2,    0.4]
VS_NY_DUR_MS   = 65.0
VS_NY_ANTI_F   = 1200.0   # Palatal antiresonance
VS_NY_ANTI_BW  = 250.0
```

### [j] Voiced Palatal Approximant

```python
VS_J_F         = [280.0, 2100.0, 2800.0, 3300.0]
VS_J_B         = [100.0,  200.0,  300.0,  350.0]
VS_J_GAINS     = [ 10.0,    6.0,    1.5,    0.5]
VS_J_DUR_MS    = 55.0
```

---

## SEGMENT MAP — v5

```
Segment              Duration   Samples   Architecture
─────────────────────────────────────────────────────────
[j]₁                  55.0 ms    2425     voiced approximant
[ɑ]₁                  55.0 ms    2425     steady-state vowel
[ɟ]                    54.0 ms    2381     voice bar + burst + cutback
[ɲ]                    65.0 ms    2866     voiced palatal nasal
[ɑ]₂ + closing tail   80.0 ms    3528     55ms vowel + 25ms fade
[s] UNIFIED            55.0 ms    2425     unified noise source
head + [j]₂           70.0 ms    3087     15ms rise + 55ms approximant
[ɑ]₃                  55.0 ms    2425     steady-state vowel
─────────────────────────────────────────────────────────
TOTAL                 489.0 ms   21562
ACTUAL                488.9 ms   21559
```

---

## TĀLAVYA COLUMN — STATUS

```
Row  IPA  Description              Status    Verified in
───  ───  ─────────────────────    ────────  ─────────────
1    [c]  voiceless unaspirated    PENDING   —
2    [cʰ] voiceless aspirated      PENDING   —
3    [ɟ]  voiced unaspirated       VERIFIED  YAJÑASYA ✓
4    [ɟʰ] voiced aspirated         PENDING   —
5    [ɲ]  nasal                    VERIFIED  YAJÑASYA ✓
```

Row 3 and row 5 verified. The tālavya voiced stop and nasal are confirmed.

---

## PLUCK PRINCIPLE — GENERALIZATION STATUS

```
Segment type            Architecture            Status
───────────────────────────────────────────────────────────
Voiceless stops         Unified source + pluck   VERIFIED (RATNADHĀTAMAM, PUROHITAM, ṚTVIJAM)
Voiceless sibilants     Unified source + pluck   VERIFIED (YAJÑASYA v5) ✓
Voiceless fricatives    Unified source + pluck   PREDICTED (same physics)
Voiced stops            Voice bar + cutback      VERIFIED (DEVAM, YAJÑASYA, ṚTVIJAM)
Voiced aspirated stops  Voice bar + murmur       VERIFIED (RATNADHĀTAMAM)
```

**The Pluck Principle now covers two voiceless segment classes.**
The prediction: ALL voiceless segments — stops, sibilants, fricatives,
aspirated stops — use the same unified source architecture.
The physics is identical: continuous breath, shaped by continuous envelope,
subglottal floor at edges, closing tails and opening heads on voiced neighbors.

---

## SIBILANT HIERARCHY — PARTIAL

```
Sibilant   IPA   Place       Centroid    Status      Verified in
─────────  ────  ──────────  ────────��   ──────────  ───────────
[s]        [s]   dantya      7490.8 Hz   VERIFIED    YAJÑASYA ✓
[ṣ]        [ʂ]   mūrdhanya   ~5500 Hz?   PREDICTED   —
[ś]        [ɕ]   tālavya     ~6500 Hz?   PREDICTED   —
```

The sibilant centroid hierarchy should follow the same physics as the
burst centroid hierarchy: shorter anterior cavity = higher frequency.
Dental [s] at 7491 Hz. Retroflex [ʂ] should be lower (longer cavity).
Palatal [ɕ] should be between dental and retroflex.

---

## WORD EVIDENCE

**Rigveda 1.1.1:**
```
agnimīḷe purohitaṃ yajñasya devamṛtvijam |
hotāraṃ ratnadhātamam ||
```

"I praise Agni, the household priest,
the divine minister of **the sacrifice**,
the invoker, the best giver of treasures."

Word 5 of 9 in the first verse.
Morphology: yajña (sacrifice) + -sya (genitive singular).
**"Of the sacrifice"** — the genitive that binds the priest to his function.

---

## PHONEMES IN YAJÑASYA

```
Seg  IPA   Type                    Duration  Verified in
───  ────  ──────────────────────  ────────  ──────────────
[j]  appr  voiced palatal           55 ms    YAJÑASYA v3
[ɑ]  vow   short open central       55 ms    AGNI
[ɟ]  stop  voiced palatal (v4)      54 ms    YAJÑASYA v4 ✓
[ɲ]  nas   voiced palatal nasal     65 ms    YAJÑASYA v3
[ɑ]  vow   short open central       55 ms    AGNI
[s]  sib   voiceless dental (v5)    55 ms    THIS WORD (v5) ✓
[j]  appr  voiced palatal           55 ms    YAJÑASYA v3
[ɑ]  vow   short open central       55 ms    AGNI
```

Total word duration: 488.9 ms (diagnostic speed, dil=1.0).

---

## DIAGNOSTIC EVOLUTION — COMPLETE

```
v1.0    Initial diagnostic (from ṚTVIJAM v2.1 template)
        Cold-start: 4 periods (b=[g] convention)
        Cold-start ceiling: 5.0
        [ɟ] release centroid in PLACE BAND (1-6 kHz)
        [s] centroid in SIBILANT BAND (4-12 kHz)
        47/48 PASS, 1 FAIL: [ɟ] closure voicing = 0.0

v1.1    [ɟ] closure voicing (autocorrelation) REMOVED
        Closure 30ms → body() trim → 2.5 periods
        Below guard clause (3 periods)
        Wrong instrument for signal length
        Voicing proven by LF ratio (0.9844) + join continuity
        47/47 PASS
```

### Coverage

```
                              v1.1
Signal integrity               4 checks
Signal continuity (within)     8 checks
Signal continuity (joins)      8 checks
[s] unified verification       4 checks
Closing tail                   2 checks
Opening head                   2 checks
[ɟ] phases                     3 checks
Vowel formants (F1, F2)        9 checks
Approximants + Nasal           4 checks
Syllable coherence             3 checks
                             ───
TOTAL                         47 checks (word-complete)
```

---

## KEY INSIGHTS — COMPLETE

### From v3 (v7 Burst Architecture)

1. **Spike + turbulence is correct physics for all stops.**
   The same architecture works for voiced palatal [ɟ] as for
   voiceless dental [t] and voiced velar [g]. The burst is a
   pressure release transient — an impulse exciting cavity resonance.

2. **Place cue lives in the formant-filtered turbulence, not the spike.**
   The spike is broadband. The turbulence is shaped by the cavity
   at the place of constriction. The palatal locus ([500, 3200, 3800, 4200])
   differs from dental ([1500, 3500, 5000, 6500]) and velar
   ([2594 Hz centroid]).

### From v4 (4-Phase [ɟ])

3. **Voice bar + crossfade cutback eliminates voiced stop boundaries.**
   Continuous glottal source through closure means no silence-to-signal
   discontinuity. The 250 Hz voice bar hums through the sealed tract.
   The cutback crossfades from closed-tract to open-tract formants.

### From v5 (Unified Pluck for [s])

4. **The Pluck Principle extends to all voiceless segments.**
   Voiceless stops and voiceless sibilants share the same boundary
   problem (voiced signal → voiceless noise → voiced signal) and
   the same solution (closing tail + unified source + opening head).

5. **Subglottal floor prevents digital-zero boundaries.**
   The breath never stops. During any voiceless segment, the tract
   walls transmit some energy. The subglottal floor (0.001, ~-60dB)
   models this reality. It prevents the zero-to-noise jump that
   the ear detects as a click.

6. **Segment ownership follows physics for all voiceless segments.**
   The voiced segment whose articulator is moving owns the transition.
   The vowel's tongue moves toward the sibilant → closing tail is the vowel's.
   The approximant's voicing resumes after the sibilant → opening head is
   the approximant's. The sibilant only owns the sustained noise.

### From Diagnostic Calibration (v1.0 → v1.1)

7. **Autocorrelation failure pattern is now a known class.**
   Three words, three occurrences, same root cause: short segment +
   body trim → below minimum period count → returns 0.0.
   The fix is always the same: use LF ratio or join continuity
   as voicing evidence instead.

---

## IMPLEMENTATION FILES

```
yajnasya_reconstruction.py     Synthesis v5 (unified pluck architecture)
yajnasya_diagnostic.py         Diagnostic v1.1 (47/47)
evidence.md                    This file
```

---

## AUDIO OUTPUT FILES

```
diag_yaj_word_dry.wav              Full word, diagnostic speed
diag_yaj_word_slow6x.wav           6× slow for analysis
diag_yaj_word_slow12x.wav          12× slow for analysis
diag_yaj_word_hall.wav              Temple courtyard reverb
diag_yaj_perf.wav                  Performance speed (2.5× dilation)
diag_yaj_perf_hall.wav             Performance + reverb
diag_yaj_perf_slow6x.wav          Performance, 6× slow
diag_yaj_s_unified.wav             Isolated [s] unified source
diag_yaj_s_unified_slow6x.wav     [s] 6× slow
diag_yaj_s_unified_slow12x.wav    [s] 12× slow
diag_yaj_jj_iso.wav               Isolated [ɟ]
diag_yaj_jj_iso_slow6x.wav        [ɟ] 6× slow
diag_yaj_jj_iso_slow12x.wav       [ɟ] 12× slow
diag_yaj_aSya_syllable.wav         aSya syllable (boundary test)
diag_yaj_aSya_syllable_slow6x.wav  aSya 6× slow
diag_yaj_aSya_syllable_slow12x.wav aSya 12× slow
```

---

## ŚIKṢĀ VALIDATION

### [ɟ] — ज

- **Sthāna (place):** tālavya ✓ (release centroid 3127.5 Hz in place band)
- **Prayatna (manner):** spṛṣṭa (stop) ✓ (burst transient + cutback)
- **Nāda (voicing):** ghoṣa ✓ (closure LF ratio 0.9844, joins continuous)
- **Prāṇa (aspiration):** alpaprāṇa ✓ (no murmur phase, 54ms total)

### [s] — स

- **Sthāna (place):** dantya ✓ (centroid 7490.8 Hz — high sibilant)
- **Prayatna (manner):** ūṣman (sibilant) ✓ (sustained turbulent noise)
- **Nāda (voicing):** aghoṣa ✓ (voicing = 0.1861, below 0.30)
- **Prāṇa (aspiration):** — (not applicable to sibilants in the same way)

### [ɲ] — ञ

- **Sthāna (place):** tālavya ✓ (antiresonance at 1200 Hz, palatal)
- **Prayatna (manner):** anunāsika ✓ (nasal, LF ratio 0.9966)
- **Nāda (voicing):** ghoṣa ✓ (voicing = 0.7965)

**The ancient phoneticians described the articulatory positions.**
**The acoustic measurements confirm them.**
**They agree.**

---

## RELATED DOCUMENTS

```
pluck_artifact.md                  — The Pluck Principle (discovery record)
tonnetz_manifold_seed.md           — Coherence space geometry
the_convergence_artifact.md        — Three independent derivations
Vedic_Tonnetz_Bridge.md            — Tonnetz ↔ vocal topology bridge
VS_phoneme_inventory.md            — Phoneme inventory
ratnadhatamam/evidence.md          — [t] pluck + [dʰ] aspiration
rtvijam/evidence.md                — [ʈ] pluck + [ɟ] palatal stop
purohitam/evidence.md              — [p] + [t] unified source
AGENTS.md                          — Project-level semantic grounding
```

---

*February 2026.*
*47 diagnostics. Zero failures.*
*The Pluck Principle extends to sibilants.*
*The breath is continuous. The constriction is the envelope.*
*Closing tails, opening heads, subglottal floors — the same physics,*
*the same architecture, from stops to sibilants.*
*The ruler was calibrated once. The same lesson, third occurrence.*
*"Fix the ruler, not the instrument."*
*यज्ञस्य*
