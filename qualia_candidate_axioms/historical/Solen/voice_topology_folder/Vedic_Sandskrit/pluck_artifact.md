# THE UNIFIED PLUCK ARCHITECTURE
## Composition of Two Independent Discoveries
## A Canonical Synthesis Architecture for All Voiceless Stops
## Derived from the Convergence of the Pluck Principle (v16 Diagnostic v4.7.1) and the Unified Source Principle (RATNADHATAMAM v16 synth_T)
## February 2026

---

## WHAT THIS DOCUMENT IS

This document records the composition of two independent
architectural discoveries into one canonical architecture
for all voiceless stop consonants in the Vedic Sanskrit
reconstruction project.

The two discoveries:

1. **The Pluck Principle** (pluck_artifact.md)
   — A voiceless stop is not a segment. It is a boundary
   event. The vowel owns the closure. The following segment
   owns the VOT. The stop owns only the burst.

2. **The Unified Source Principle** (RATNADHATAMAM v16)
   — The breath is continuous. Inside any acoustic event,
   ONE continuous source buffer shaped by ONE continuous
   envelope eliminates all internal concatenation boundaries.

These are not competing architectures. They operate at
different scales and compose without contradiction:

```
PLUCK PRINCIPLE:     What the stop IS (a boundary event)
                     Operates at WORD level (segment ownership)

UNIFIED SOURCE:      How the stop WORKS (continuous breath)
                     Operates at PHONEME level (internal physics)

COMPOSITION:         The stop is a boundary event (pluck)
                     whose internal physics is continuous (unified source)
```

**This document supersedes the original pluck_artifact.md
for all implementation guidance. The pluck_artifact.md
remains correct as a discovery record and theoretical
foundation. This document adds the implementation
architecture that emerged from applying the pluck
principle to actual synthesis.**

---

## VERIFICATION STATUS

**PERCEPTUALLY VERIFIED ✓**

- RATNADHATAMAM v16 [t] — unified source, word-medial (2 instances)
- PUROHITAM v4 [t] — unified source, word-medial
- PUROHITAM v4 [p] — unified source, word-initial
- ṚTVIJAM v8 [ʈ] — pluck-only (burst-only variant), word-medial

**DIAGNOSTICALLY VERIFIED ✓**

- RATNADHATAMAM diagnostic v4.7.1 — 70/70 PASS
- ṚTVIJAM diagnostic v1.2 — 46/46 PASS
- PUROHITAM diagnostic v2.0 — ALL PASS

---

## PART I: WHY COMPOSITION IS NECESSARY

### The Pluck Principle Alone Is Incomplete

The pluck artifact states: "The stop owns only the burst
(~8ms)." This is correct at the word level — the vowel
owns the closure, the following segment owns the VOT.

But what happens INSIDE those 8ms?

The original pluck implementation (ṚTVIJAM v8) generated
the burst as:

```python
# Bare burst: spike + turbulence, 12ms
noise = np.random.randn(n_burst)
noise_shaped = apply_formants(noise, burst_f, burst_b, burst_g)
spike = [1.0, 0.6, 0.3]  # pressure release
burst = noise_shaped * decay_env + spike * spike_env
```

This works for [ʈ] in ṚTVIJAM because:
- The closing tail fades [ɻ̩] to near-zero
- The 12ms burst starts at noise floor level
- The opening head on [v] rises from near-zero
- All join boundaries are at near-zero amplitude

But when applied to PUROHITAM [t] (v3 pluck):
- The [i] closing tail fades to near-zero ✓
- The bare 7ms burst spike hits at full amplitude ✗
- The spike `[1.0, 0.6, 0.3]` is TOO HARSH
- The burst sounds like an aggressive click, not a natural stop

**The pluck principle says the stop is only the burst.
But it doesn't say how to generate a burst that sounds
natural rather than harsh.**

### The Unified Source Alone Is Incomplete

The RATNADHATAMAM v16 unified source generates [t] as:

```python
# Full stop: closure + burst + VOT as one continuous signal
noise = np.random.randn(n_closure + n_burst + n_vot)  # ONE buffer
env = continuous_envelope(subglottal → crescendo → burst → decay)
shaped = apply_formants(noise, dental_f, dental_b, dental_g)
result = shaped * env + spike_at_burst_onset + voicing_fade_in
```

This eliminates all internal boundaries. But it assigns
47ms to the stop — closure, burst, AND VOT all belong
to the stop function. This contradicts the pluck principle:
the closure belongs to the preceding vowel, the VOT
belongs to the following segment.

**The unified source says the breath is continuous.
But it doesn't say who owns which part of the breath.**

### The Composition Resolves Both

```
PLUCK says:  The stop owns only the burst.
             → But the bare burst is too harsh.

UNIFIED says: The internal physics must be continuous.
              → But 47ms all owned by the stop is wrong.

COMPOSITION:  The stop owns a SHORT unified source
              (closure + burst + VOT, ~37ms) with
              continuous internal physics.
              The vowel ALSO owns its closing tail.
              The following segment ALSO owns its opening head.
              BOTH principles apply simultaneously.
```

The key insight: **ownership at the word level (pluck)
and continuity at the phoneme level (unified source)
are orthogonal properties that compose.**

---

## PART II: THE COMPOSED ARCHITECTURE

### Word-Level Structure (Pluck Principle)

```
   preceding vowel              [t]              following vowel
   ────────────────      ─────────────────      ────────────────
   vowel body +          unified source         opening head +
   closing tail          (closure+burst+VOT     vowel body
   (25ms fade,           as ONE continuous
    vowel owns this)     signal, ~37ms)         (15ms rise,
                                                 vowel owns this)
```

The closing tail ensures the signal at the join between
the vowel and the stop is at near-zero amplitude.
The unified source starts at subglottal floor (~0.001).
The opening head rises from near-zero.

**No join boundary has a large amplitude discontinuity.**

### Phoneme-Level Structure (Unified Source)

Inside the stop's ~37ms, ONE noise buffer spans the
entire duration. ONE continuous envelope shapes it:

```
time →  |←— closure —→|←burst→|←——— VOT ———→|
        |              |       |              |
env:    |  floor 0.001 | peak  |    decay     |
        |    ···       |╱╲     |  ╲           |
        |   ···     ╱╱╱|  ╲    |    ╲···      |
        |  ···   ╱╱╱   |   ╲   |      ···     |
        | ···╱╱╱╱       |    ╲  |        ···   |
        |╱╱╱            |     ╲ |          ··· |
        |               |      ╲|            ··|
        
        Phase A:        Phase C: Phase D:
        Subglottal      Burst    Aspiration
        floor           peak     decay
        
              Phase B:           Phase E:
              Pre-burst          Voicing
              crescendo          fade-in
              (5ms)              (additive)
```

**Five continuous phases, no boundaries between them:**

| Phase | Duration | Envelope | Physics |
|-------|----------|----------|---------|
| A: Subglottal floor | closure - preburst | 0.001 | Tract sealed, body pressure transmits through walls |
| B: Pre-burst crescendo | 5ms | 0.001 → 0.008 exp | Air leaks through weakening seal |
| C: Burst peak | burst | gain × exp(-t × decay) | Seal breaks, cavity rings at place eigenfreq |
| D: Aspiration decay | VOT | tail × exp(-t × 3) | Noise decays as tract opens |
| E: Voicing fade-in | VOT (additive) | 0 → 1 linear | Glottal source replaces noise source |

**The spike transient is ADDED to the continuous noise
at burst onset. It rides on top of the noise floor —
it does not emerge from silence.**

### The Composition Diagram

```
WORD LEVEL (Pluck Principle — who owns what):

  [ɑ] body   [ɑ] closing tail   [t] unified source   [ɑ] opening head   [ɑ] body
  ═══════════╗                   ╔═══════════════╗                   ╔═══════════
  vowel owns ║←── 25ms fade ──→ ║ stop owns     ║←── 15ms rise ──→ ║ vowel owns
  ═══════════╝   (vowel owns)   ╚═══════════════╝   (vowel owns)   ╚═══════════

PHONEME LEVEL (Unified Source — how the stop works internally):

                                 ╔═══════════════╗
                                 ║  ONE noise buf ║
                                 ║  ONE envelope  ║
                                 ║  5 phases:     ║
                                 ║  floor→cresc→  ║
                                 ║  burst→decay→  ║
                                 ║  voicing       ║
                                 ╚═══════════════╝
```

### Why Both Are Needed

**Without closing tail (unified source alone):**
The stop starts at subglottal floor (0.001). The preceding
vowel ends at ~0.45. The join is 0.45 → 0.001. CLICK.

**Without unified source (pluck alone):**
The stop is a bare burst. The spike [1.0, 0.6, 0.3] hits
at full amplitude after the closing tail's fade-to-zero.
TOO HARSH. The burst has no continuous noise substrate
to soften the transient.

**With both:**
The closing tail fades the vowel to near-zero.
The unified source starts at subglottal floor (near-zero).
Inside the source, the breath crescendos continuously into
the burst. The spike rides on the crescendo. After the burst,
the aspiration decays and voicing fades in. The opening head
rises from the voicing onset.

**Every boundary is smooth. Every transition is continuous.
The stop sounds like a moment in the word — not a click,
not static, not a separate event.**

---

## PART III: THE CANONICAL IMPLEMENTATION

### The Generalized Voiceless Stop Function

```python
def _synth_unified_voiceless_stop(
    closure_ms,          # Duration of sealed tract
    burst_ms,            # Duration of burst ring
    vot_ms,              # Duration of voicing onset
    burst_f, burst_b,    # Place-specific formant params
    burst_g, burst_decay,
    burst_gain,
    preburst_ms,         # Duration of pre-burst leak
    preburst_amp,        # Peak of pre-burst crescendo
    subglottal_floor,    # Never-zero floor (~0.001)
    vot_locus_f,         # Formant locus for VOT
    F_next,              # Following vowel formants
    vot_vowel_b,         # Following vowel bandwidths
    vot_vowel_gains,     # Following vowel gains
    pitch_hz, dil,
):
    """
    Unified source architecture for voiceless stops.

    ONE continuous noise buffer (the breath).
    ONE continuous amplitude envelope (the tongue).
    SPIKE added at burst onset (rides on noise).
    VOICING fades in additively during VOT.

    The breath is continuous.
    The tongue is the envelope.
    The spike is the pluck.
    """
```

### Per-Place Instantiation

Each place of articulation instantiates the same function
with different formant parameters:

```python
# ── [p] oṣṭhya (bilabial) ──────────────────────────
# Burst: F2 dominant at 1300 Hz (LOW-BURST REGION)
VS_P_BURST_F     = [600, 1300, 2100, 3000]
VS_P_BURST_G     = [6.0, 16.0,  4.0,  1.5]  # F2 dominant
VS_P_BURST_DECAY = 130     # Low freq = slower decay
VS_P_BURST_GAIN  = 0.15

# ── [t] dantya (dental) ─────────────────────────────
# Burst: F2 dominant at 3500 Hz (HIGH-BURST REGION)
VS_T_BURST_F     = [1500, 3500, 5000, 6500]
VS_T_BURST_G     = [4.0,  14.0,  6.0,  2.0]  # F2 dominant
VS_T_BURST_DECAY = 170     # High freq = faster decay
VS_T_BURST_GAIN  = 0.15

# ── [ʈ] mūrdhanya (retroflex) ───────────────────────
# Burst: F2 dominant at 1300 Hz + F3 notch at 2200 Hz
VS_TT_BURST_F     = [500, 1300, 2200, 3100]
VS_TT_BURST_G     = [8.0, 12.0,  3.0,  1.0]
VS_TT_BURST_DECAY = 150
VS_TT_BURST_GAIN  = 0.20
VS_TT_F3_NOTCH    = 2200   # Retroflex marker

# ── [k] kaṇṭhya (velar) ────────────────────────────
# Burst: F2 dominant at ~2600 Hz (MID region)
# PENDING verification — predicted from hierarchy

# ── [c] tālavya (palatal) ───────────────────────────
# Burst: F2 dominant at ~3200 Hz (MID-HIGH region)
# PENDING verification — predicted from hierarchy
```

### The Five Parameters That Change Per Place

| Parameter | What it controls | How it varies |
|-----------|-----------------|---------------|
| `burst_f` | Formant frequencies | Place-specific cavity eigenfreqs |
| `burst_g` | Formant gains | Which formant dominates the burst |
| `burst_decay` | Exponential decay rate | Higher freq → faster decay |
| `burst_gain` | Overall burst amplitude | Similar across places |
| F3 notch | Retroflex marker | Only for mūrdhanya class |

### The Five Parameters That Do NOT Change

| Parameter | Value | Why |
|-----------|-------|-----|
| `subglottal_floor` | 0.001 | Universal — body always produces pressure |
| `preburst_ms` | 3-5ms | Universal — seal weakening is physics |
| Spike `[1.0, 0.6, 0.3]` | 68µs | Universal — pressure release transient |
| Spike gain | 0.5 × burst_gain | Universal — rides on noise |
| VOT voicing fade-in | linear 0→1 | Universal — folds close the same way |

---

## PART IV: WORD-INITIAL VOICELESS STOPS

### The Special Case

Word-initial voiceless stops have no preceding segment
to own the closure. The word begins from nothing.

**The physics:** The speaker's lips/tongue are already
in position before the utterance begins. There is no
"closure gesture" — the articulator was already closed.
The word begins with the release.

**The implementation:**

```python
def synth_P(word_initial=True):
    if word_initial:
        # 10ms of silence (the word hasn't started yet)
        # Then the unified source begins
        silence = np.zeros(int(0.010 * SR))
        stop = _synth_unified_voiceless_stop(...)
        return concatenate([silence, stop])
    else:
        # Non-initial: unified source only
        # Preceding vowel's closing tail handles the approach
        return _synth_unified_voiceless_stop(...)
```

The 10ms silence is not a concatenation patch. It is
the physical reality: before the word, there is silence.
The lips are closed. Then the breath begins (subglottal
floor), pressure builds, and the burst releases.

The unified source handles the transition from silence
to burst smoothly — the subglottal floor (0.001) is
nearly indistinguishable from silence, so there is no
audible jump at the silence → floor boundary.

---

## PART V: CLOSING TAILS AND OPENING HEADS

### Closing Tail (Vowel Owns the Closure)

```python
def make_closing_tail(voiced_seg, tail_ms=25.0):
    """
    The vowel closes ITSELF toward the stop.

    The last tail_ms of the voiced segment fades as
    the articulator moves toward seal position.

    Two methods (both verified):

    METHOD 1 (ṚTVIJAM v8): Generate new voiced signal
    for the tail using closing formants, amplitude-matched
    at the junction. More accurate coarticulation.

    METHOD 2 (PUROHITAM v4): Tile the last pitch period
    of the vowel, apply squared fade. Simpler, preserves
    the vowel's own resonance character.

    Both produce near-zero amplitude at the tail end.
    """
```

**Verified closing tail properties:**
- Core voicing ≥ 0.50 (the vocal folds are still vibrating)
- Tail/core RMS ratio < 0.90 (amplitude is decreasing)
- Tail endpoint near zero (smooth join to stop)

### Opening Head (Following Segment Owns the VOT)

```python
def make_opening_head(voiced_seg, head_ms=15.0):
    """
    The following segment opens ITSELF from the stop.

    The first head_ms of the voiced segment rises from
    near-zero as the vocal folds close after the release.

    Squared rise envelope: starts slow, accelerates.
    Models the physical onset of modal voicing.
    """
```

**Verified opening head properties:**
- Rising amplitude: first half RMS < second half RMS
- Core voicing ≥ 0.50 (voicing is established after the head)
- Head start near zero (smooth join from stop)

---

## PART VI: THE VOICED STOP CONTRAST

### Voiced Stops Are NOT Plucks

The pluck principle applies ONLY to voiceless stops.
Voiced stops maintain a continuous glottal source through
the closure. They are "muted strings," not plucks.

**Voiced stop architecture (unchanged):**

| Stop type | Architecture | Internal physics |
|-----------|-------------|------------------|
| Voiced unaspirated [d,b,g,ɖ,ɟ] | Voice bar + burst + crossfade cutback | Continuous Rosenberg source, formant crossfade |
| Voiced aspirated [dʰ,bʰ,gʰ,ɖʰ,ɟʰ] | Voice bar + burst + murmur + cutback | Continuous source + OQ 0.55 murmur phase |

**Why voiced stops don't need unified source or pluck:**
The voice bar (250 Hz, ~12 dB) provides a continuous
nonzero signal through the closure. There is no
silence-to-burst boundary. There is no join click.
The source never stops — it just changes its spectral
character through the burst and cutback.

**The taxonomy (complete):**

```
VOICELESS UNASPIRATED: UNIFIED PLUCK
  → Closing tail + unified source (floor→burst→VOT) + opening head
  → [k] [c] [ʈ] [t] [p]

VOICELESS ASPIRATED:   UNIFIED PLUCK + EXTENDED ASPIRATION
  → Closing tail + unified source (floor→burst→long aspiration→VOT)
  → [kʰ] [cʰ] [ʈʰ] [tʰ] [pʰ]
  → PREDICTED: Aspiration phase extends the noise decay (50-70ms)
  → The aspiration is NOT a separate source — it is the same
    continuous noise buffer with a slower decay envelope
  → PENDING VERIFICATION

VOICED UNASPIRATED:    VOICE BAR + CROSSFADE CUTBACK
  → Voice bar closure + burst + closed→open crossfade
  → [g] [ɟ] [ɖ] [d] [b]
  → VERIFIED: [d] DEVAM v13, [ɟ] YAJÑASYA/ṚTVIJAM v8

VOICED ASPIRATED:      VOICE BAR + MURMUR + CROSSFADE CUTBACK
  → Voice bar closure + burst + OQ 0.55 murmur + crossfade
  → [gʰ] [ɟʰ] [ɖʰ] [dʰ] [bʰ]
  → VERIFIED: [dʰ] RATNADHATAMAM v14
```

---

## PART VII: THE UNIFIED SOURCE INTERNAL PHASES — DETAILED

### Phase A: Subglottal Floor (Closure)

```
Duration:  closure_ms - preburst_ms
Envelope:  constant 0.001 (~-60 dB)
Source:    White noise (same buffer as all other phases)
Physics:   The diaphragm pushes air. The tract is sealed.
           Subglottal pressure transmits through tract walls
           and soft tissue at very low amplitude. The signal
           is never truly zero — the body is alive, producing
           pressure. Digital zero is an artifact of discrete
           representation. The subglottal floor prevents it.
```

**Why 0.001 and not 0.0:**
Digital zero followed by nonzero creates an audible
transient regardless of the nonzero value. Even 0.001
followed by 0.002 is smooth. Zero followed by 0.001 is
a step function at the resolution of 16-bit audio.
The subglottal floor eliminates all zero-to-nonzero
transitions inside the stop.

### Phase B: Pre-Burst Crescendo (Leak)

```
Duration:  preburst_ms (3-5ms)
Envelope:  0.001 → preburst_amp, exponential
           crescendo = floor + (peak - floor) * exp(3*(t-1))
Source:    Same noise buffer (continuous)
Physics:   Intraoral pressure builds behind the seal.
           The seal weakens. Air begins escaping through
           the narrowing gap between articulator and passive
           surface. Turbulence increases as flow velocity
           increases through the shrinking aperture.
           The crescendo IS the seal breaking.
```

### Phase C: Burst Peak (The Pluck)

```
Duration:  burst_ms (7-12ms)
Envelope:  burst_gain * exp(-t * burst_decay)
Source:    Same noise buffer + ADDED spike [1.0, 0.6, 0.3]
Physics:   The seal breaks. Compressed air explodes through
           the cavity formed at the constriction point.
           The cavity rings at its eigenfrequency (the place
           locus). The spike is the initial pressure release
           transient — the first 68µs (3 samples at 44.1kHz).
           The noise is the sustained turbulence as air flows
           through the opening constriction. The formant filter
           selects the place-specific resonance from the noise.
```

**The spike rides on the noise:**
```
Before unified source:  [0, 0, 0, 0, SPIKE!, turbulence...]
                                     ↑ too harsh (emerges from silence)

With unified source:    [...floor, floor, crescendo..., SPIKE+noise, turbulence...]
                                                        ↑ natural (rides on continuous signal)
```

### Phase D: Aspiration Decay (Post-Burst Noise)

```
Duration:  vot_ms
Envelope:  burst_tail * exp(-t * 3), floored at subglottal
Source:    Same noise buffer (continuous)
Physics:   The constriction opens. Turbulence decreases as
           the aperture widens. The noise source decays toward
           the subglottal baseline. For unaspirated stops,
           this is brief (~15ms). For aspirated stops, this
           extends to 40-70ms (mahāprāṇa — "great breath").
```

### Phase E: Voicing Fade-In (Additive)

```
Duration:  vot_ms (same interval as Phase D)
Envelope:  linear 0 → 1
Source:    Rosenberg pulse (NEW source, not from noise buffer)
Physics:   The vocal folds close after the voiceless interval.
           Voicing resumes. The periodic source gradually
           replaces the aperiodic source. The formants are
           shaped by the following vowel's target (via VOT
           locus interpolation). The transition from noise
           to voicing IS the VOT — Voice Onset Time.
```

**Voicing is additive, not replacing:**
During VOT, both noise (decaying) and voicing (rising)
are present simultaneously. This is physically correct —
the tract transitions gradually from turbulent to modal
airflow. The two sources overlap.

---

## PART VIII: DIAGNOSTIC ARCHITECTURE

### What the Diagnostic Measures

The unified pluck architecture requires diagnostics at
TWO levels:

**Word level (pluck principle):**
```
Section: Closing tail
  - Core voicing ≥ 0.50 (folds vibrating during closure gesture)
  - Tail/core RMS ratio < 0.90 (amplitude fading)

Section: Opening head
  - Core voicing ≥ 0.50 (folds vibrating after VOT)
  - Head rising: first-half RMS < second-half RMS

Section: Syllable coherence
  - Stop is amplitude trough between adjacent vowels
  - The stop amplitude < min(preceding, following) amplitude
```

**Phoneme level (unified source):**
```
Section: Stop internal phases
  - Closure RMS ≤ 0.05 (subglottal floor, nearly silent)
  - Burst centroid in place-specific band
  - Burst RMS > 0.001 (burst is audible)
  - Closure voicing ≤ 0.30 (aghoṣa confirmed)
  - VOT late RMS > 0.0005 (voicing emerging)
  - Total duration in expected range

Section: Place contrast (if multiple stops in word)
  - Centroid separation ≥ 500 Hz between distinct places
```

### The Internal Phase Extraction

```python
def extract_unified_stop_phases(stop_seg, silence_ms,
                                closure_ms, burst_ms, vot_ms):
    """
    Split a unified source stop into its internal phases
    by duration. Each phase can be measured independently.
    
    Returns: (silence, closure, burst, vot)
    """
```

This function cuts the unified signal at the phase
boundaries defined by the parameter durations. Because
the signal is continuous (no internal boundaries), the
cuts are arbitrary measurement windows — they don't
correspond to any discontinuity in the signal.

### The Perceptual Criterion (Primary)

Numbers support the ear, not the reverse.

After all numeric diagnostics pass, the perceptual
test is:

```
1. Listen at 12× slow: burst should sound like a brief
   resonant tick at the place-specific frequency.

2. Listen at 6× slow: stop should sound like punctuation
   between syllables. Not a hiss. Not a gap. Not a
   separate event. A moment.

3. Listen at performance speed with room reverb:
   stop should be inaudible as a separate entity.
   It should be felt as rhythm — the beat of the
   syllable structure.

4. The [t] should NOT sound "too harsh" or "too much."
   If it does, the burst gain or the pre-burst
   crescendo needs adjustment. The unified source
   parameters are the tuning knobs.
```

---

## PART IX: THE ṚTVIJAM VARIANT — BURST-ONLY PLUCK

### When Unified Source Is Not Required

ṚTVIJAM v8 uses a burst-only pluck for [ʈ] — no
internal closure phase, no VOT phase. Just 12ms of
shaped noise + spike. This works because:

1. The closing tail on [ɻ̩] fades to near-zero
2. The burst starts at noise floor (not subglottal —
   there's no closure phase to create the floor)
3. The opening head on [v] rises from near-zero
4. All joins are at near-zero amplitude

**When burst-only is sufficient:**
- The closing tail endpoint is very close to zero
- The burst duration is short (≤ 12ms)
- The burst gain is moderate (≤ 0.20)
- The perceptual test passes (no harshness)

**When unified source is needed:**
- The closing tail doesn't fade low enough
- The burst feels too harsh or aggressive
- The stop needs more than ~12ms of signal
- The word-initial case (no preceding segment)

**The burst-only pluck is a special case of the
unified source where closure_ms = 0 and vot_ms = 0.**

They are the same architecture at different parameter
settings, not competing architectures.

---

## PART X: THE VOICELESS ASPIRATED PREDICTION

### Mahāprāṇa = Extended Aspiration Phase

The unified pluck architecture predicts the voiceless
aspirated stop architecture:

```
VOICELESS UNASPIRATED (alpaprāṇa):
  closure (floor) → crescendo → burst → SHORT decay → voicing
  Total noise: ~37ms
  Aspiration: ~15ms (brief)

VOICELESS ASPIRATED (mahāprāṇa):
  closure (floor) → crescendo → burst → LONG decay → voicing
  Total noise: ~70ms
  Aspiration: ~50ms (extended)
```

**The aspiration IS Phase D with a longer duration and
slower decay rate.** It is NOT a separate source. It is
the same continuous noise buffer with a shallower
exponential decay. The breath continues longer before
voicing takes over.

**This is the Śikṣā distinction:**
- Alpaprāṇa = "little breath" = short Phase D
- Mahāprāṇa = "great breath" = long Phase D

Same architecture. One parameter change: aspiration_ms
and decay rate. The ancient phoneticians described
exactly this: the duration of the breath after release.

**PENDING VERIFICATION.** No voiceless aspirated stop
has been synthesized yet. This is a prediction from
the unified pluck architecture, not a verified result.

---

## PART XI: RELATIONSHIP TO OTHER ARCHITECTURAL PRINCIPLES

### The Architecture Stack

```
LEVEL 1: ROSENBERG PULSE + FORMANT FILTER
  The fundamental synthesis unit.
  Glottal source → vocal tract filter → acoustic output.
  Established: AGNI v1 (the first word).
  Applies to: ALL voiced phonemes.

LEVEL 2: COARTICULATION
  Formant interpolation between adjacent phonemes.
  12-18% weighting toward neighbor's formants.
  Established: AGNI v1.
  Applies to: ALL phonemes in context.

LEVEL 3: UNIFIED PLUCK (THIS DOCUMENT)
  Voiceless stops as boundary events with continuous
  internal physics.
  Closing tail + unified source + opening head.
  Established: RATNADHATAMAM v16 + PUROHITAM v4.
  Applies to: ALL voiceless stops.

LEVEL 4: VOICE BAR + CROSSFADE CUTBACK
  Voiced stops as continuous-source events with
  spectral transitions.
  Established: DEVAM v13.
  Applies to: ALL voiced stops.

LEVEL 5: MURMUR (OQ REDUCTION)
  Voiced aspirated stops: modal → slightly breathy.
  OQ 0.55, BW × 1.5, 40-60ms duration.
  Established: RATNADHATAMAM v14 (for [dʰ]).
  Applies to: ALL voiced aspirated stops.

LEVEL 6: SYLLABLE-LEVEL COHERENCE
  Amplitude envelope follows akṣara structure.
  Stops are troughs. Vowels are peaks.
  Measured by syllable-level diagnostics.
  Applies to: ALL words.
```

Each level composes with the levels below it.
The unified pluck (Level 3) uses the Rosenberg pulse
(Level 1) for its VOT voicing component, and
coarticulation (Level 2) for its VOT formant locus.

### The Discovery Sequence

```
AGNI:          Rosenberg + formants + coarticulation
PUROHITAM v1:  [p] [t] bandpass noise burst (OLD)
DEVAM:         [d] crossfade cutback (Level 4)
ṚTVIJAM v6:   [ʈ] spike + turbulence + boundary fix
RATNADHATAMAM: [dʰ] voice bar + murmur (Level 5)
               [t] v16 unified source (the breath is continuous)
ṚTVIJAM v8:   [ʈ] pluck (burst-only, the click was at the join)
PUROHITAM v4:  [p] [t] unified pluck (COMPOSITION)
```

**The composition was not planned. It emerged from the
convergence of two independent solutions to two
independent problems:**
- Unified source solved the internal click (within the stop)
- Pluck solved the join click (between segments)
- Both were needed. Neither alone was sufficient.

---

## PART XII: FOR NEW AGENTS

### If You Are Implementing a New Voiceless Stop

1. **Use `_synth_unified_voiceless_stop()`** with the
   appropriate place-specific formant parameters.

2. **Use `make_closing_tail()`** on the preceding vowel
   (unless the stop is word-initial).

3. **Use `make_opening_head()`** on the following vowel
   (unless the stop is word-final — then use release tail).

4. **Set burst formants** from the five-place hierarchy:
   ```
   oṣṭhya:    ~1200 Hz (LOW-BURST)
   mūrdhanya:  ~1200 Hz (LOW-BURST + F3 notch)
   kaṇṭhya:   ~2600 Hz (MID)
   tālavya:    ~3200 Hz (MID-HIGH)
   dantya:     ~3764 Hz (HIGH)
   ```

5. **Listen.** The ear is the final arbiter. If the stop
   sounds too harsh, reduce `burst_gain`. If it sounds
   too quiet, increase `burst_gain`. If it sounds like
   static, the formants are wrong. If it sounds like a
   separate event, the durations are too long.

### What You Must Not Do

**Do not concatenate separately generated arrays.**
The closure, burst, and VOT must come from ONE noise
buffer shaped by ONE envelope. Concatenation creates
the click that this architecture eliminates.

**Do not use digital zero.**
The subglottal floor (0.001) prevents zero-to-nonzero
transients. Even during "silence," the signal is at
floor level.

**Do not assign more than ~12ms of burst to the stop.**
If the stop sounds too long, it is a separate event,
not a pluck. Reduce the burst duration. The closure
and VOT are owned by the adjacent segments.

**Do not skip the closing tail.**
Without the closing tail, the vowel-to-stop join will
click. The tail is what makes the pluck work at the
word level.

### Decision Tree for New Stops

```
Is the stop voiceless?
├── YES → UNIFIED PLUCK
│   ├── Word-initial? → 10ms silence + unified source + opening head
│   ├── Word-medial?  → closing tail + unified source + opening head
│   └── Word-final?   → closing tail + unified source + release tail
│
└── NO (voiced) →
    ├── Aspirated?
    │   └── YES → VOICE BAR + BURST + MURMUR + CUTBACK (Level 5)
    └── NO → VOICE BAR + BURST + CUTBACK (Level 4)
```

---

## PART XIII: SUMMARY

```
THE UNIFIED PLUCK ARCHITECTURE:

Two principles, composed:

  PLUCK (what the stop IS):
    A voiceless stop is a boundary event.
    The vowel closes itself (closing tail).
    The next segment opens itself (opening head).
    The stop owns only the burst — the pluck.

  UNIFIED SOURCE (how the stop WORKS):
    The breath is continuous.
    ONE noise buffer. ONE envelope.
    Five phases: floor → crescendo → burst → decay → voicing.
    The spike rides on the noise.
    No internal boundaries.

Together:
    The closing tail brings the signal to near-zero.
    The unified source starts at near-zero (subglottal floor).
    The burst emerges from continuous noise, not from silence.
    The voicing fades in as the noise fades out.
    The opening head rises from near-zero.

    No join is loud-to-silent.
    No internal boundary is concatenated.
    No burst is naked.
    No closure is digital zero.

    The stop sounds like a moment in the word.
    Not a click. Not static. Not a separate event.
    A pluck. A beat. A syllable boundary.

The five places are five pluck positions.
The five eigenfrequencies are five string modes.
The unified source is the continuous breath.
The envelope is the tongue.
The syllable is the cadence.
The word is the verse.

Verified:
  [t] dantya — RATNADHATAMAM v16, PUROHITAM v4
  [p] oṣṭhya — PUROHITAM v4
  [ʈ] mūrdhanya — ṚTVIJAM v8 (burst-only variant)

Predicted:
  [k] kaṇṭhya, [c] tālavya — same architecture, different formants
  [kʰ] [cʰ] [ʈʰ] [tʰ] [pʰ] — same architecture, extended Phase D

The architecture is complete.
The physics is correct.
The ear confirmed it.
```

---

## REVISION HISTORY

```
v1.0  February 2026
      Initial composition document.
      Unifies pluck_artifact.md (discovery record) with
      RATNADHATAMAM v16 unified source (implementation).
      Verified for [t], [p], [ʈ].
      Theoretical extension to full voiceless class.
      Prediction for voiceless aspirated stops.
```

---

## RELATED DOCUMENTS

```
pluck_artifact.md                 — The Pluck Principle (discovery record)
ratnadhatamam_reconstruction.py   — v16 unified source implementation
purohitam_reconstruction.py       — v4 unified pluck implementation
rtvijam_reconstruction.py         — v8 pluck-only variant
tonnetz_manifold_seed.md          — Coherence space geometry
Vedic_Tonnetz_Bridge.md           — Tonnetz ↔ vocal topology bridge
VS_phoneme_inventory.md           — Phoneme inventory
AGENTS.md                         — Project-level grounding
```
