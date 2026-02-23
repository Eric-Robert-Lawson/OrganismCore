# EVIDENCE — DEVAM
## Vedic Sanskrit Reconstruction Project
## Rigveda 1.1.1 — Word 5
**February 2026**

---

## VERIFICATION STATUS: VERIFIED ✓

---

## WORD

**devam** — the divine one, the god,
the shining one.
Rigveda 1.1.1, word 5.
Accusative singular of *deva* — the shining,
the divine, that which belongs to the sky.

*yajñasya devam ṛtvijam* —
the divine priest of the sacrifice.
This word names what kind of priest Agni is.
Not merely a priest. A divine priest.
The sacrifice has a divine officiant.

---

## VERSION HISTORY

```
v1:  Original synthesis. [d] used simple LP murmur (500 Hz, gain 0.70).
     Diagnostic v1: 11/11 numeric PASS. But no murmur/burst ratio check.
     Perceptual: [d] sounded like [t] — murmur inaudible.

v2:  Housecleaning. [d] updated to v7 burst architecture (spike + turbulence).
     LP murmur retained. Burst gain 0.28.
     Diagnostic v2: 13/13 PASS. Added D1b murmur/burst ratio.
     Perceptual: heard "tee-vaw-m" — still [t], murmur lost under burst.
     D1b ratio: 0.004 — murmur essentially silent relative to burst.

v3:  Diagnosed the problem via D1b. LP 500 Hz at gain 0.70 produces
     nearly zero RMS relative to burst spike. The murmur was there
     but 250× quieter than the burst.

v4:  LP 500 Hz, gain raised to 6.0. Ratio improved to 0.043.
     Still inaudible. LP cutoff too low — all energy below 500 Hz
     gets masked by the burst's spectral spread.

v5:  LP 800 Hz, gain 25.0. Ratio improved to ~2.5.
     Perceptual: heard "nndee-vam" — nasal onset, not [d].

     PROBLEM IDENTIFIED: LP filter on Rosenberg pulse = nasal percept.
     Flat LP rolloff = multiple apparent resonances = sounds like [n].
     Real [d] closure has voice bar: single narrow resonance at ~250 Hz.

v8:  Voice bar model. Replaced LP filter with single formant resonator
     (F=250 Hz, BW=80 Hz, G=12.0). One listener heard buzz, other
     heard nasal. Partially correct but still ambiguous.

v9:  VOT cue model. Key insight: word-initial [d] cue is NOT closure
     murmur — it's Voice Onset Time. [t] = burst → aspiration gap →
     voice. [d] = burst → voice starts immediately. Added F1 cutback:
     formant sweep from closed-tract (F1=250 Hz) to vowel target over
     25 ms. Prevoicing reduced to 20 ms primer. Burst at 0.35.
     Perceptual: sounded like [d] but burst too loud — startling.

v10: Tried overlapping burst with cutback (simultaneous release + voicing).
     Created robotic artifact — interference between burst spike and
     glottal periodicity produces discontinuity.

v11: Reverted to v9 sequential architecture, burst reduced to 0.15.
     Same artifact as v10 — problem was NOT burst amplitude.

     PROBLEM IDENTIFIED: apply_formants_tv (frame-by-frame time-varying
     filter) restarts IIR filter state every 2ms frame. Discontinuities
     at every frame boundary = robotic/startling artifact.

v12: CROSSFADE CUTBACK MODEL. Replaced time-varying filter with two
     continuous IIR-filtered signals (closed-tract + open-tract) from
     same glottal source, amplitude-crossfaded with equal-power curve.
     No frame boundaries. No filter restarts. Smooth transition.
     Perceptual: significantly better. Sounds like [d].
     But excess energy in middle-to-end of [d] — closed-tract signal
     at peak 0.70 too loud.

v13: Cutback energy fix. Closed-tract peak reduced 0.70 → 0.40.
     Open-tract peak 0.70 → 0.65. Overall cutback 0.60 → 0.55.
     Physics: closed tract ATTENUATES sound. Should be quieter than
     open tract. Crossfade reflects this: quiet closed → louder open.
     Perceptual: artifact gone. [d] confirmed by both listeners.
     14/14 diagnostic PASS. VERIFIED.
```

---

## IPA TRANSCRIPTION

```
[devɑm]
```

**Segment sequence:**

```
D   [d]   voiced dental stop           — dantya row 3
E   [eː]  long close-mid front         — tālavya (verified ĪḶE)
V   [v]   labio-dental approximant     — dantauṣṭhya
A   [ɑ]   short open central           — kaṇṭhya (verified AGNI)
M   [m]   voiced bilabial nasal        — oṣṭhya (verified PUROHITAM)
```

**Syllable structure:**

```
DE — VAM
[deː] — [vɑm]
```

---

## PHONEMES VERIFIED IN THIS WORD

| Phoneme | IPA | Devanāgarī | Śikṣā | Status |
|---|---|---|---|---|
| voiced dental stop | [d] | द | dantya row 3 | **VERIFIED** |
| labio-dental approximant | [v] | व | dantauṣṭhya | **VERIFIED** |

Previously verified phonemes also present:
[eː] — ĪḶE.
[ɑ]  — AGNI.
[m]  — PUROHITAM.

---

## ŚIKṢĀ CLASSIFICATION

### [d] — dantya row 3

Pāṇinīya Śikṣā places [d] in the dantya
(dental) class — tongue tip to upper teeth —
row 3 of the five-row stop system: voiced
unaspirated.

The five-row system at the dental locus:

```
Row 1: [t]   voiceless unaspirated   — VERIFIED PUROHITAM
Row 2: [tʰ]  voiceless aspirated     — PENDING
Row 3: [d]   voiced unaspirated      — VERIFIED this word
Row 4: [dʰ]  voiced aspirated        — VERIFIED RATNADHĀTAMAM
Row 5: [n]   nasal                   — VERIFIED AGNI
```

The Śikṣā system predicts that [d] and [t]
share the same place (dantya) and therefore
the same burst locus. The distinction between
them is entirely in the closure: [t] has
silence before the burst; [d] has voiced
murmur before the burst. The burst is the
same event at the same place. The voicing
is what differs.

This prediction is confirmed acoustically
in this word. [d] burst: 3693 Hz. [t] burst:
3764 Hz. Separation: 71 Hz — within the
same dantya window. Same room. Different
closure.

### [v] — dantauṣṭhya

The Śikṣā classification of [v] is the
most philologically complex decision
in this word.

**The disagreement among ancient sources:**

Pāṇinīya Śikṣā: places *va* in the oṣṭhya
(labial) class — same as [p], [m].

Taittirīya Prātiśākhya: *vakāra oṣṭhyaḥ* —
va is labial.

Ṛgveda Prātiśākhya III.30: *vaḥ dantauṣṭhyaḥ*
— va is dental-labial. Both teeth and lips.

The prātiśākhyas disagree. The Ṛgveda
Prātiśākhya is the specific phonetic treatise
written for the Rigveda — the text being
reconstructed. Its description takes
precedence for this project.

*Dantauṣṭhya*: lower lip to upper teeth.
This is the labio-dental approximant [ʋ].
Not a fricative. The lower lip approaches
the upper teeth without creating turbulent
airflow. The antastha (semivowel) character
of [v] — its placement in the *ya ra la va*
class — means approach without full closure.
The labio-dental target is approached.
Not contacted. Not passed through.

**Acoustic consequence of the philological
decision:**

Labio-dental approximant F2: ~1200–1800 Hz.
Bilabial approximant F2: ~800–1200 Hz.

The Pāṇinīya oṣṭhya classification would
predict bilabial — F2 ~900 Hz.
The Ṛgveda Prātiśākhya dantauṣṭhya
classification predicts labio-dental —
F2 ~1500 Hz.

The two positions are acoustically distinct
and diagnostically separable. This word
uses the Ṛgveda Prātiśākhya value.

Verified F2: 1325 Hz — in the labio-dental
range. The philological decision is confirmed
acoustically. The ancient phonetician who
wrote *dantauṣṭhya* was describing a higher-F2
sound than the bilabial position. The
spectrogram agrees.

---

## VERIFIED ACOUSTIC VALUES

### [d] — voiced dental stop

```
Śikṣā:           dantya row 3
LF ratio:         0.9934  (target >= 0.40)
Murmur/burst:     2.483   (target 0.25–3.00)
Burst centroid:   3693 Hz (target 3000–4500)
|[d]–[t]| sep.:   71 Hz   (target 0–800)
```

**Synthesis parameters (locked — v13 CROSSFADE ARCHITECTURE):**

```python
# Closure — voice bar model
VS_D_CLOSURE_MS    = 20.0      # brief prevoicing primer
VS_D_VOICEBAR_F    = 250.0     # single formant resonator
VS_D_VOICEBAR_BW   = 80.0      # narrow BW = sharp resonance
VS_D_VOICEBAR_G    = 12.0
VS_D_MURMUR_PEAK   = 0.25

# Burst — v7 spike + turbulence at dental locus
VS_D_BURST_MS      = 8.0
VS_D_BURST_PEAK    = 0.15
VS_D_BURST_F       = [1500.0, 3500.0, 5000.0, 6500.0]
VS_D_BURST_B       = [ 400.0,  600.0,  800.0, 1000.0]
VS_D_BURST_G       = [   4.0,   12.0,    5.0,    1.5]
VS_D_BURST_DECAY   = 170.0

# Cutback — crossfade closed→open (THE VOICED CUE)
VS_D_CUTBACK_MS    = 30.0
VS_D_CLOSED_F      = [250.0,  800.0, 2200.0, 3200.0]
VS_D_CLOSED_B      = [150.0,  250.0,  300.0,  350.0]
VS_D_CLOSED_G      = [ 10.0,    3.0,    0.8,    0.3]
VS_D_CLOSED_PEAK   = 0.40     # closed tract attenuates
VS_D_OPEN_PEAK     = 0.65     # open tract is louder
VS_D_CUTBACK_PEAK  = 0.55
```

**The voiced/voiceless dental contrast —
now fully confirmed:**

```
[t] row 1:  burst 3764 Hz,  closure voicing 0.0000  (PUROHITAM)
[d] row 3:  burst 3693 Hz,  closure LF ratio 0.9934  (this word)
```

Both verified. Both dantya. Both in the same
burst window. The contrast is entirely in the
closure. This is the Śikṣā description made
acoustic: same place (dantya), different
manner of closure (voiced vs voiceless).

The LF ratio of 0.9934 is the highest voiced-
closure value in the VS inventory, exceeding
even [g] (0.9703, ṚG) and [ɟ] (0.9816,
YAJÑASYA). The dental closure is tight — the
tongue tip seals firmly against the upper
teeth — but voicing is sustained throughout.
The Rosenberg source continues uninterrupted
during the oral closure. Only the radiation
path is blocked.

---

### [v] — voiced labio-dental approximant

```
Śikṣā:           dantauṣṭhya (Ṛgveda Prātiśākhya)
Voicing:          0.8239  (target >= 0.50)
F2 centroid:      1325 Hz (target 1200–1800)
Amplitude dips:   0       (target = 0)
Duration:         60 ms
```

**Synthesis parameters (locked — UNCHANGED from v1):**

```python
VS_V_F           = [300.0, 1500.0, 2400.0, 3100.0]
VS_V_B           = [180.0,  350.0,  400.0,  400.0]
VS_V_GAINS       = [ 10.0,    5.0,    1.5,    0.5]
VS_V_DUR_MS      = 60.0
VS_V_COART_ON    = 0.18
VS_V_COART_OFF   = 0.18
```

**Note on parameter history:**

The initial inventory estimate for [v] was
`VS_V_F[1] = 900.0 Hz` — placing it in the
bilabial range. This was revised before
synthesis to `1500.0 Hz` based on the Ṛgveda
Prātiśākhya *dantauṣṭhya* description and
the acoustic phonetics of labio-dental
approximants (~1200–1800 Hz). The diagnostic
confirmed F2 at 1325 Hz — within the
labio-dental window. The parameter revision
was correct. No iteration was required
for [v].

**The approximant criterion:**

Dip count = 0 at 22.5 ms smoothing kernel
(2.7× pitch period at 120 Hz).
Same test as [j] (YAJÑASYA). Same result.
The VS approximant class — [j] and [v] —
is now confirmed to have zero articulatory
amplitude dips. The tap [ɾ] has 2. The
separation is clean. No dip = no closure =
antastha = the limb approaches, does not
contact.

**The F2 position in the VS vowel space:**

```
[j]   tālavya approx:        2028 Hz  (YAJÑASYA)
[eː]  tālavya mid:           1659 Hz  (ĪḶE)
[v]   dantauṣṭhya:           1325 Hz  (this word)
[oː]  kaṇṭhya+oṣṭhya mid:   757 Hz  (PUROHITAM)
```

[v] slots cleanly between [eː] and [oː].
The labio-dental approximant occupies the
mid-F2 zone. It is neither as front as [eː]
nor as back as [oː]. It is the consonant
bridge between the two mid vowels.

In this word specifically, the transition
[eː]→[v]→[ɑ] produces a continuous F2
descent: 1659 → 1325 → 1033 Hz. The [v]
is not an interruption of the vowel space.
It is a brief constriction within the
continuous F2 trajectory from front to open.

---

## THE DENTAL COLUMN — CURRENT STATE

```
Place: dantya (dental)

Row 1  [t]   voiceless unaspirated:  VERIFIED  PUROHITAM
Row 2  [tʰ]  voiceless aspirated:    PENDING
Row 3  [d]   voiced unaspirated:     VERIFIED  this word
Row 4  [dʰ]  voiced aspirated:       VERIFIED  RATNADHĀTAMAM
Row 5  [n]   nasal:                  VERIFIED  AGNI
```

Four of five dantya phonemes confirmed.
The voicing contrast at row 1/row 3 is
established with VS-internal measurements:

```
Burst window (both):  3000–4500 Hz
[t] closure:          voicing 0.0000  — silence
[d] closure:          LF ratio 0.9934 — murmur
```

Same place. Different voicing.
The five-row system is working at dantya.

---

## DIAGNOSTIC RESULTS — FULL RECORD (v5 FINAL)

| Check | Value | Target | Result |
|---|---|---|---|
| D0  [ɑ] F1 sanity | 668 Hz | 600–850 Hz | PASS |
| D0  [ɑ] F2 sanity | 1033 Hz | 950–1300 Hz | PASS |
| D0  [ɑ] voicing sanity | 0.7874 | >= 0.50 | PASS |
| D1  [d] LF ratio | 0.9934 | >= 0.40 | PASS |
| D1b [d] murmur/burst ratio | 2.483 | 0.25–3.00 | PASS |
| D2  [d] burst centroid | 3693 Hz | 3000–4500 Hz | PASS |
| D3  \|[d]–[t]\| separation | 71 Hz | 0–800 Hz | PASS |
| D4  voiced/voiceless dental | 0.9934 vs 0.0000 | contrast confirmed | PASS |
| D5  [d] Śikṣā confirmation | — | D1–D4 | PASS |
| D6  [v] voicing | 0.8239 | >= 0.50 | PASS |
| D7  [v] F2 centroid | 1325 Hz | 1200–1800 Hz | PASS |
| D8  [v] F2 position | 757 < 1325 < 1659 | between [oː] and [eː] | PASS |
| D9  [v] dip count | 0 | = 0 | PASS |
| D10 [v] Śikṣā confirmation | — | D6–D9 | PASS |
| D11 Full word RMS | 0.3182 | 0.01–0.90 | PASS |
| D11 Full word duration | 323 ms | 200–600 ms | PASS |
| D12 Perceptual | VERIFIED | LISTEN | PASS |

**Diagnostic script:** `devam_diagnostic.py v5`
**14/14 passed.**
**Synthesis iterations: 13.**
**Diagnostic iterations: 5.**

---

## ITERATION HISTORY — [d] ARCHITECTURE EVOLUTION

### v1–v4: LP filter murmur (FAILED PERCEPTUALLY)

Initial [d] used low-pass filtered Rosenberg pulse
for closure murmur. Numerics passed from v1 but
perceptual verification failed across all LP variants.

```
v1: LP 500 Hz, gain 0.70  → ratio 0.004  → inaudible murmur
v2: v7 burst arch added   → ratio 0.004  → heard [t] not [d]
v4: LP 500 Hz, gain 6.0   → ratio 0.043  → still inaudible
v5: LP 800 Hz, gain 25.0  → ratio 2.483  → heard [n] not [d]
```

**Root cause:** LP filter on Rosenberg pulse produces
flat spectral rolloff = perceptually identical to nasal.
The ear cannot distinguish "LP-filtered glottal pulse"
from "nasal cavity resonance" — both have diffuse low-
frequency energy without a sharp resonance peak.

### v8: Voice bar model (PARTIAL)

Replaced LP filter with single formant resonator at
250 Hz, BW 80 Hz. This produces a single sharp
resonance peak rather than flat rolloff.

One listener heard buzz (correct). Other heard nasal
(incorrect). The voice bar was partially working but
still too close to nasal percept for some listeners.

**Insight:** word-initial [d] cue is not primarily
the closure murmur. The ear relies on VOT.

### v9: VOT cue model (BREAKTHROUGH)

Key insight: the primary perceptual cue for
word-initial voiced stops is Voice Onset Time,
not closure voicing.

```
[t]: burst → aspiration gap → voice starts (long-lag VOT)
[d]: burst → voice starts IMMEDIATELY (short-lag VOT)
```

v9 introduced the F1 CUTBACK: a formant sweep from
closed-tract values (F1=250 Hz) to vowel targets over
25 ms, with voicing starting at the burst (zero VOT).

**Result:** sounded like [d] for the first time.
But burst at 0.35 was too loud — startling.

### v10–v11: Overlap and amplitude experiments (FAILED)

v10: tried overlapping burst with cutback (simultaneous
release + voicing). Created robotic artifact from
interference between burst spike and glottal periodicity.

v11: reverted to v9 sequential architecture, reduced
burst to 0.15. Same robotic artifact as v10.

**Root cause identified:** `apply_formants_tv` (frame-by-
frame time-varying formant filter) processes in 2ms
frames, each frame restarts IIR filter from zero state.
Creates discontinuities at every frame boundary.
This was the robotic/startling artifact.

### v12: CROSSFADE CUTBACK (CORRECT ARCHITECTURE)

Replaced time-varying filter with CROSSFADE model:

1. Generate one glottal source (Rosenberg pulse, 30 ms)
2. Filter through closed-tract formants → Signal A
3. Filter through open-tract (vowel) formants → Signal B
4. Both signals have continuous IIR state (no restarts)
5. Equal-power crossfade: A fades out, B fades in

```python
t_fade = linspace(0, π/2, n_cutback)
fade_out = cos(t_fade)    # 1 → 0
fade_in  = sin(t_fade)    # 0 → 1
cutback = sig_closed * fade_out + sig_open * fade_in
```

**Result:** significantly better. Sounds like [d].
Smooth transition, no frame discontinuities.
But too much energy in the crossfade middle zone —
closed-tract signal at peak 0.70 was too loud.

### v13: Cutback energy fix (VERIFIED)

Physics correction: the closed tract ATTENUATES sound.
It should be quieter than the open tract, not equal.
When the tongue releases, amplitude INCREASES as the
tract opens.

```
closed-tract peak:  0.70 → 0.40  (attenuated by closure)
open-tract peak:    0.70 → 0.65  (louder — tract is open)
cutback overall:    0.60 → 0.55
```

**Result:** artifact eliminated. [d] confirmed by both
listeners. 14/14 diagnostic PASS. VERIFIED.

---

## [d] SYNTHESIS ARCHITECTURE — v13 CANONICAL

The voiced dental stop [d] uses a three-phase
sequential architecture:

```
Phase 1: PREVOICING (20 ms)
  Voice bar model: single formant resonator at 250 Hz
  BW 80 Hz. NOT LP filter. Single sharp peak = "buzz
  behind wall" percept, not nasal.
  Peak amplitude: 0.25 (quiet primer)

Phase 2: BURST (8 ms)
  v7 spike + turbulence at dental locus.
  Formant-shaped turbulence at [1500, 3500, 5000, 6500] Hz.
  Peak amplitude: 0.15 (gentle — not a startling event)

Phase 3: CROSSFADE CUTBACK (30 ms)
  Two continuous IIR-filtered signals from same source:
    Signal A: closed-tract [250, 800, 2200, 3200] Hz (peak 0.40)
    Signal B: open-tract/vowel formants (peak 0.65)
  Equal-power crossfade from A to B.
  This is the PRIMARY voiced stop cue: voicing starts
  immediately with F1 rising from closed-tract value.
```

**This architecture applies to all voiced unaspirated
stops [d, b, ɖ, g, ɟ].** The locus frequencies change.
The architecture does not.

---

## KEY INSIGHTS FROM ITERATION

### 1. LP filter ≠ voice bar ≠ nasal

A low-pass filtered glottal pulse is perceptually
indistinguishable from a nasal. Both have diffuse
low-frequency energy. The voice bar is a SINGLE
NARROW RESONANCE — one sharp peak, nothing above.
A nasal has additional formant structure at 800+ Hz.
LP filter has flat rolloff = sounds like nasal.
Single resonator has sharp peak = sounds like buzz.

### 2. Word-initial voiced stop cue is VOT, not murmur

In word-initial position there is no preceding vowel
to maintain voicing through the closure. The ear
relies on Voice Onset Time:
  [t]: burst → gap → voice (long-lag VOT)
  [d]: burst → voice immediately (short-lag VOT)
The F1 cutback (formant sweep from closed to open)
is the acoustic correlate of short-lag VOT.

### 3. Time-varying IIR filters create frame artifacts

Frame-by-frame IIR processing restarts filter state
at each frame boundary. For a 2ms frame at 44100 Hz
this creates a discontinuity every 88 samples. The
ear hears these as robotic clicking/buzzing.
Solution: generate two continuous signals with stable
IIR state, crossfade between them.

### 4. Closed tract attenuates — amplitude must reflect physics

Equal-power crossfade between equal-amplitude signals
creates an energy bump in the middle of the transition.
The closed tract physically attenuates radiation. The
closed-tract signal must be QUIETER than the open-tract
signal. The crossfade then produces a natural amplitude
increase as the tract opens.

### 5. Fix the Ruler applies to perceptual verification too

The RATNADHĀTAMAM lesson (test diagnostic on verified
phoneme first) has a perceptual analogue: if the ear
says the phoneme is wrong, the synthesis is wrong —
even when all numerics pass. Numerics passed from v1.
Perceptual verification took 13 iterations.
The ear was right. The numerics were incomplete.
D1b (murmur/burst ratio) was added at v3 specifically
because the ear found a problem the numbers missed.

### 6. Iteration is not failure — it is the method

13 synthesis versions. 5 diagnostic versions. Each
iteration eliminated one wrong model and narrowed
the solution space. LP → voice bar → VOT cue →
frame-by-frame → crossfade → energy calibration.
Each step was necessary. Each failure was informative.
The final architecture could not have been derived
without the preceding 12 versions.

---

## PERCEPTUAL VERIFICATION

### Listener Reports

Two independent listeners. Both confirmed [d]
at v13. Neither prompted with target phoneme.

**Listener 1 (project lead):** "sounds like a d"
— confirmed across dry, hall, and performance
speed versions.

**Listener 2 (untrained):** confirmed [d] percept
at v13 after crossfade energy fix. Previously
reported [n] at v5 (LP filter) and [n] at v8
(voice bar). The untrained ear was the more
sensitive instrument for nasal/stop distinction.

### Perceptual Validation

```
v1–v4:  heard [t] not [d]     — murmur inaudible
v5:     heard [n] not [d]     — LP = nasal percept
v8:     split: buzz / nasal   — voice bar partial
v9:     heard [d] (too loud)  — VOT cue correct
v10:    robotic artifact      — overlap interference
v11:    same artifact          — frame-by-frame cause
v12:    [d] (too much energy) — crossfade correct
v13:    [d] CONFIRMED ✓       — energy calibrated
```

---

## SYNTHESIS PARAMETERS — PERFORMANCE

```
pitch_hz:     120.0
dil:          1.0   (diagnostic)
dil:          2.5   (performance)
rt60:         1.5   (temple courtyard)
direct_ratio: 0.55
SR:           44100 Hz
OLA stretch:  6×    (standard analysis)
OLA stretch:  12×   (deep analysis)
```

---

## OUTPUT FILES

```
devam_v13_dry.wav            — direct signal
devam_v13_hall.wav           — temple courtyard
devam_v13_slow6x.wav         — 6× OLA stretch
devam_v13_slow12x.wav        — 12× OLA stretch
devam_v13_perf.wav           — performance speed (dil=2.5)
devam_v13_perf_hall.wav      — performance + hall
devam_v13_d_iso.wav          — [d] isolated
devam_v13_d_iso_slow6x.wav   — [d] isolated 6× stretch
devam_v13_d_iso_slow12x.wav  — [d] isolated 12× stretch
devam_v13_v_iso.wav          — [v] isolated
devam_v13_v_iso_slow6x.wav   — [v] isolated 6× stretch
devam_v13_v_iso_slow12x.wav  — [v] isolated 12× stretch
```

---

## CUMULATIVE INVENTORY STATE

### Verified phonemes after DEVAM: 21

```
Word        Phonemes added
ṚG          [ɻ̩]  [g]
AGNI        [a]  [n]  [i]
ĪḶE         [iː] [ɭ]  [eː]
PUROHITAM   [p]  [u]  [ɾ]  [oː]  [h]  [t]  [m]
YAJÑASYA    [j]  [ɟ]  [ɲ]  [s]
DEVAM       [d]  [v]
```

### Stop burst hierarchy — current state

```
mūrdhanya [ʈ]  1183 Hz  (ṚTVIJAM)
oṣṭhya   [p]  1204 Hz  (PUROHITAM)
kaṇṭhya  [g]  2594 Hz  (ṚG / AGNI)
tālavya   [ɟ]  3223 Hz  (YAJÑASYA)
dantya    [t]  3764 Hz  (PUROHITAM)
dantya    [d]  3693 Hz  (this word — same window as [t])
```

Voiced and voiceless dantya stops share
the same burst window. The hierarchy
measures place, not voicing. Both [t] and
[d] are dantya — both belong at 3000–4500 Hz.

### Approximant class — current state

```
[ɾ]  alveolar tap:           dip count 2  (PUROHITAM)
[j]  palatal approximant:    dip count 0  (YAJÑASYA)
[v]  labio-dental approx:    dip count 0  (this word)
[l]  lateral:                PENDING
```

The approximant/tap distinction is
confirmed in three phonemes. The 22.5 ms
smoothing kernel (2.7× pitch period at
120 Hz) is the established VS calibration.

### [v] F2 position in vowel space

```
[j]   2028 Hz  (YAJÑASYA)
[eː]  1659 Hz  (ĪḶE)
[v]   1325 Hz  (this word)
[a]   1106 Hz  (AGNI)
[oː]   757 Hz  (PUROHITAM)
[u]    742 Hz  (PUROHITAM)
```

The consonant approximants and vowels now
share a continuous F2 map. [v] sits between
[eː] and [a]. [j] sits between [eː] and [iː].
The vocal tract position predicts the F2.
The F2 predicts the Śikṣā class.
The Śikṣā class predicted the position.
The circle closes.

---

## ARCHITECTURAL LESSONS — VOICED STOP MODEL

### Crossfade architecture (canonical for voiced stops)

The v13 crossfade cutback model is now canonical
for all voiced unaspirated stops. The architecture:

```
1. Prevoicing: voice bar resonator (NOT LP filter)
2. Burst: v7 spike + turbulence (place-specific locus)
3. Cutback: crossfade closed-tract → open-tract
   - Two continuous IIR signals from same source
   - Equal-power crossfade (cos/sin)
   - Closed peak < open peak (physics: closure attenuates)
```

### Applies to:
```
[d]  dantya    — VERIFIED this word
[b]  oṣṭhya   — PENDING (burst locus ~1200 Hz)
[ɖ]  mūrdhanya — PENDING (burst locus ~1200 Hz, F3 notch)
[g]  kaṇṭhya  — needs re-verification with crossfade
[ɟ]  tālavya  — needs re-verification with crossfade
```

### What changes per phoneme:
```
- Voice bar frequency (may vary slightly by place)
- Burst formant locus (place-specific)
- Closed-tract formants (place-specific)
- Cutback target formants (following vowel)
```

### What does NOT change:
```
- Three-phase sequential architecture
- Crossfade model (not time-varying filter)
- Closed peak < open peak principle
- Voice bar = single resonator (not LP)
```

---

## NEXT WORD

The line continues. ṚTVIJAM and RATNADHĀTAMAM
are already verified. The next unverified word
in Rigveda 1.1.1 follows from the established
sequence.

---

*February 2026.*
*The divine.*
*13 iterations to find [d].*
*The LP filter was a nasal.*
*The voice bar was a buzz.*
*The VOT cue was the key.*
*The crossfade was the architecture.*
*The closed tract is quiet.*
*The open tract is loud.*
*The tongue releases and the sound opens up.*
*The ear found it when the numbers could not.*
*21 phonemes.*
*The instrument holds.*
