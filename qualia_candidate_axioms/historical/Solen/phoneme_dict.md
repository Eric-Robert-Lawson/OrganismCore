# PHONEME ENGINE DICTIONARY
## The Speaking Architecture
## A Complete Reference for Synthetic Speech
## Built on the Confirmed Rosenberg/Klatt Pipeline
## February 2026

---

## WHAT THIS DOCUMENT IS

This is the onboarding document
for the speech synthesis engine.

A new instance reading this
should be able to:

1. Understand exactly how the voice
   produces sound (the substrate)

2. Understand exactly how phonemes
   map to synthesis parameters

3. Understand what is confirmed
   (tested, working) vs what is
   approximate (needs iteration)

4. Know exactly what to fix
   and in what order

5. Produce intelligible speech
   from this foundation

This document is both:
- A technical reference
- A record of what was learned

---

## PART 1: THE SUBSTRATE
### How the Voice Makes Sound

The engine uses a
**Source-Filter model**
of speech production.

```
SOURCE → FILTER → OUTPUT
```

### The Source

Two source types:

**VOICED SOURCE (Rosenberg Glottal Pulse)**
Used for: all vowels, voiced consonants
(b, d, g, v, z, m, n, l, r, w, y)

```python
# Rosenberg pulse — CONFIRMED INVARIANT
# Do not change this.
oq     = 0.65          # open quotient
phase  = cumulative_frequency / sr
source = where(phase < oq,
    (phase/oq)*(2 - phase/oq),
    1 - (phase-oq)/(1-oq))
source = diff(source)  # differentiate
```

Properties:
- Rich in harmonics
- Spectral slope: -12dB/octave
- Sounds like a buzzing reed
- All voiced speech begins here

**UNVOICED SOURCE (Noise)**
Used for: unvoiced fricatives
(s, sh, f, h, th), plosive bursts

```python
source = random.normal(0, 1, n_samples)
# Then shaped by filter
```

Properties:
- White noise
- Must be bandpass filtered to be useful
- The filter IS the consonant

### The Filter — Parallel Klatt Bank

**CONFIRMED ARCHITECTURE:**

Four formant resonators in parallel.
Each resonator is a second-order IIR filter.

```python
# Single resonator transfer function:
# H(z) = b0 / (1 - a1*z^-1 - a2*z^-2)
# where:
T  = 1.0 / SR
a2 = -exp(-2*pi*bandwidth*T)
a1 =  2*exp(-pi*bandwidth*T) *
       cos(2*pi*f_center*T)
b0 = 1 - a1 - a2
```

Four resonators summed:
```
F1 resonator → gain 0.6  ─┐
F2 resonator → gain 0.8  ─┤→ SUM → output
F3 resonator → gain 0.5  ─┤
F4 resonator → gain 0.3  ─┘
```

**WHY PARALLEL NOT CASCADE:**
Parallel allows independent control
of each formant amplitude.
Cascade requires precise gain staging.
For synthesis: parallel is more robust.

---

## PART 2: WHAT FORMANTS ARE
### The Physics of Vowels

The vocal tract is a tube.
Tubes have resonant frequencies.
Those frequencies are the formants.

**F1**: Low frequency. 250-800Hz.
Controls: vowel height (jaw opening).
- High F1 = open mouth = 'ah'
- Low F1  = closed mouth = 'ee','oo'

**F2**: Mid frequency. 800-2500Hz.
Controls: vowel backness (tongue position).
- High F2 = front vowel = 'ee','eh'
- Low F2  = back vowel = 'oh','oo'

**F3**: 2000-3500Hz.
Controls: lip rounding, r-coloring.
- Low F3 = r-colored vowel = 'er','ar'
- Normal F3 = everything else

**F4**: 3000-4000Hz.
Contributes to voice quality/brightness.
Less perceptually critical for intelligibility.

### The F1/F2 Vowel Space

```
         F2 (Hz)
    2500      1500      800
     |          |        |
270  |    IY    |        |   F1=270
     |   (ee)   |        |   (closed)
400  |          | IH     |   F1=400
     |          |(ih)    |
530  |    EH    |        |   F1=530
     |   (eh)   |        |
660  |          |   AH   |   F1=660
     |          |  (ah)  |
730  |    AA    |        |   F1=730
     |   (aa)   |        |   (open)
     |          |   OH   |   F1=570
     |          |  (oh)  |
     |          |   UW   |   F1=300
     |          |  (oo)  |   (closed)
```

**KEY INSIGHT:**
Vowel identity = F1/F2 combination.
Everything else (F3, F4, bandwidth)
contributes to quality but not identity.
If F1 and F2 are right,
the vowel is recognizable.

---

## PART 3: COMPLETE PHONEME TABLE
### Confirmed Values (Peterson & Barney 1952,
### male speaker averages)

### VOWELS

| Symbol | Example | F1  | F2   | F3   | F4   | Dur(ms) | Status |
|--------|---------|-----|------|------|------|---------|--------|
| AA     | f**a**ther | 730 | 1090 | 2440 | 3400 | 120 | ✓ confirmed |
| AE     | c**a**t | 660 | 1720 | 2410 | 3300 | 120 | approximate |
| AH     | **a**bout | 520 | 1190 | 2390 | 3300 |  90 | ✓ confirmed |
| AW     | n**ow**  | 730→300 | 1090→870 | 2440→2240 | 3400→3300 | 150 | approximate |
| AY     | r**i**de | 730→270 | 1090→2290 | 2440→3010 | 3400→3700 | 160 | approximate |
| EH     | b**e**d  | 530 | 1840 | 2480 | 3500 | 110 | ✓ confirmed |
| ER     | h**er**  | 490 | 1350 | 1690 | 3300 | 120 | ✓ confirmed |
| IH     | b**i**t  | 390 | 1990 | 2550 | 3600 | 100 | ✓ confirmed |
| IY     | s**ee**  | 270 | 2290 | 3010 | 3700 | 120 | ✓ confirmed |
| OH     | g**o**   | 570 |  840 | 2410 | 3300 | 120 | ✓ confirmed |
| OW     | h**ome** | 450→300 | 800→870 | 2400→2240 | 3300 | 140 | approximate |
| OY     | b**oy**  | 570→270 | 840→2290 | 2410→3010 | 3300→3700 | 160 | approximate |
| UH     | b**oo**k | 440 | 1020 | 2240 | 3300 | 100 | approximate |
| UW     | wh**o**  | 300 |  870 | 2240 | 3300 | 120 | ✓ confirmed |

**Bandwidth defaults (all vowels):**
```
B1=70, B2=110, B3=170, B4=250
```
These are narrow — the resonances are sharp.
Wider bandwidths = breathier, less tonal.

---

### NASALS

| Symbol | Example | Key Feature | F1  | F2  | F3   | Antiformant | Dur | Status |
|--------|---------|-------------|-----|-----|------|-------------|-----|--------|
| M      | **m**ap | Bilabial closure, nasal murmur | 250 | 700 | 2200 | ~1000Hz | 70 | needs work |
| N      | **n**ow | Alveolar closure | 250 | 900 | 2200 | ~1500Hz | 65 | needs work |
| NG     | si**ng** | Velar closure | 250 | 700 | 2200 | ~2000Hz | 80 | not implemented |

**HOW NASALS WORK:**
The velum opens → sound goes through nose.
Two things happen simultaneously:
1. Nasal formants added (low-frequency murmur ~250Hz)
2. Antiformants (zeros) cancel specific frequencies

**The antiformant is more important than the formant.**
It is the HOLE in the spectrum that identifies nasals.

**Implementation fix needed:**
Current antiformant is approximated by
subtracting a bandpass-filtered signal.
Better approach: add a parallel anti-resonator
(negated resonator at the antiformant frequency).

```python
# CORRECT antiformant implementation:
# Anti-resonator: H(z) = 1 - A(z)
# where A(z) is a resonator at f_anti
def anti_resonator(signal, f_anti, bw, sr):
    resonated = formant_resonator(
        signal, f_anti, bw, 1.0, sr)
    return signal - resonated
```

---

### FRICATIVES

| Symbol | Example | Voiced | Noise Band | Noise Gain | Dur | Status |
|--------|---------|--------|------------|------------|-----|--------|
| F      | **f**an | No  | 800-12000Hz | 0.8 | 80 | ✓ working |
| V      | **v**an | Yes | 800-8000Hz  | 0.5 | 75 | ✓ working |
| TH     | **th**in | No | 1000-8000Hz | 0.7 | 80 | ✓ working |
| DH     | **th**e  | Yes | 800-6000Hz  | 0.4 | 70 | approximate |
| S      | **s**un  | No  | 4000-12000Hz| 1.0 | 90 | ✓ working |
| Z      | **z**oo  | Yes | 3000-10000Hz| 0.6 | 85 | ✓ working |
| SH     | **sh**oe | No  | 1800-8000Hz | 1.0 | 95 | ✓ working |
| ZH     | mea**s**ure | Yes | 1500-7000Hz | 0.6 | 85 | not implemented |
| H      | **h**at  | No  | 300-8000Hz  | 0.9 | 60 | ✓ working |

**Key distinction S vs SH:**
- 'S':  noise above 4000Hz → thin, hissy
- 'SH': noise 1800-8000Hz → fuller, hushed

**For 'H':**
The noise is shaped by the FOLLOWING vowel.
'ha' vs 'he' vs 'ho' sound different
because the aspiration noise is filtered
through formants already moving toward
the following vowel.
This is called **anticipatory coarticulation**
and is critical for 'H' naturalness.

---

### PLOSIVES

The most complex phoneme class.
Three distinct phases:

```
CLOSURE    BURST    VOT/ASPIRATION    VOWEL ONSET
(silence)  (noise   (noise OR         (voicing
            spike)   pre-voicing)      begins)
   |           |           |               |
[40-50ms]  [4-6ms]   [10-80ms]         [→ ∞]
```

**VOT (Voice Onset Time):**
The single most important parameter
for plosive identity.

```
Short VOT (10-20ms) = VOICED: b, d, g
Long VOT  (60-80ms) = UNVOICED: p, t, k
```

| Symbol | Example | Place | Closure | Burst | VOT | Burst Freq | Status |
|--------|---------|-------|---------|-------|-----|------------|--------|
| P      | **p**at | bilabial  | 50ms | 5ms | 60ms | >500Hz  | approximate |
| B      | **b**at | bilabial  | 40ms | 4ms | 12ms | >300Hz  | approximate |
| T      | **t**op | alveolar  | 45ms | 4ms | 70ms | >2000Hz | approximate |
| D      | **d**og | alveolar  | 35ms | 4ms | 15ms | >1000Hz | approximate |
| K      | **k**ey | velar     | 50ms | 6ms | 80ms | >1500Hz | approximate |
| G      | **g**o  | velar     | 40ms | 5ms | 18ms | >800Hz  | approximate |

**Place of articulation affects burst spectrum:**
- Bilabial (p,b): low-frequency burst, >500Hz
- Alveolar (t,d): high-frequency burst, >2000Hz
- Velar (k,g):    mid-high burst, >1500Hz

**Known issue:**
Current plosive synthesis produces
recognizable burst noise
but VOT transitions into vowel
are not well-rendered.
Priority fix: sharpen the F2 transition
at VOT onset — this is the primary
perceptual cue for place of articulation.

---

### APPROXIMANTS

| Symbol | Example | Key Feature | F1  | F2   | F3   | Dur | Status |
|--------|---------|-------------|-----|------|------|-----|--------|
| L      | **l**et | F2 dip ~1000Hz | 360 | 1000 | 2400 | 70 | ✓ working |
| R      | **r**ed | F3 drop to 1690Hz | 490 | 1350 | 1690 | 80 | ✓ working |
| W      | **w**et | Starts UW, F2 rises | 300 | 870→1500 | 2200 | 80 | approximate |
| Y      | **y**et | Starts IY, F2 falls | 270 | 2290→1800 | 3010 | 70 | approximate |

**R is the hardest consonant in English.**
The key is F3 drop to ~1690Hz.
Without it, /r/ sounds like a vowel.
With it: recognizable.

**L vs R distinction:**
- L: F2 dip to ~1000Hz (low)
- R: F3 drop to ~1690Hz (low)
These are different formants.
L is an F2 event.
R is an F3 event.

---

### AFFRICATES (not yet implemented)

| Symbol | Example | Description |
|--------|---------|-------------|
| CH     | **ch**air | T + SH combined |
| JH     | **j**ar   | D + ZH combined |

Implementation: synthesize T/D then SH/ZH,
crossfade at ~5ms boundary.

---

## PART 4: COARTICULATION RULES
### How Phonemes Affect Each Other

**The most important thing
a speech synthesizer can implement.**

Real speech is not a sequence
of discrete phoneme targets.
It is a continuous trajectory
through formant space,
briefly passing through
each phoneme's target region
before moving to the next.

### The Three-Zone Model

```
|←── 30% ──→|←──── 40% ────→|←── 30% ──→|
  ONSET           STEADY         OFFSET
TRANSITION         STATE       TRANSITION
  (from prev)    (target)       (to next)
```

### Coarticulation Priority Rules

**Rule 1: Vowels are targets.**
Consonants are transitions between vowels.
The vowel formants are what the listener
uses to identify words.
Consonant formants matter less.

**Rule 2: The F2 transition is most important.**
When moving consonant → vowel:
The rate and direction of F2 change
tells the listener what consonant it was.

Locus theory (Delattre 1955):
Each place of articulation has
a "locus" — the F2 value the transition
appears to originate from:
```
Bilabial (b,p,m): F2 locus ~720Hz
Alveolar (d,t,n): F2 locus ~1800Hz
Velar    (g,k,ng): F2 locus ~3000Hz
```

**Rule 3: Nasals assimilate to following stop.**
'm' before 'p' → bilabial closure
'n' before 'd' → alveolar closure
The nasal takes the place of articulation
of the following plosive.

**Rule 4: Vowel duration affected by
following consonant.**
Vowel before voiced consonant:
~20% longer than before unvoiced.
"bad" vowel longer than "bat" vowel.

**Rule 5: H anticipates following vowel.**
/h/ has no fixed formants.
It takes the formants of the following vowel
but with high bandwidth (breathy).

### Implementation:

```python
def get_coart_formants(phon, prev, next,
                        position):
    """
    position: 0.0=onset, 0.5=steady,
              1.0=offset
    Returns interpolated F1,F2,F3,F4
    """
    F_target = PHONEMES[phon]['F']
    F_prev   = PHONEMES[prev]['F'] if prev \
               else F_target
    F_next   = PHONEMES[next]['F'] if next \
               else F_target

    if position < 0.3:
        # Onset: blend from prev
        t = position / 0.3
        return interpolate(F_prev, F_target, t)
    elif position < 0.7:
        # Steady: target
        return F_target
    else:
        # Offset: blend to next
        t = (position - 0.7) / 0.3
        return interpolate(F_target, F_next, t)
```

---

## PART 5: PROSODY
### Duration, Pitch, Stress

**Without prosody, speech sounds robotic.**
Even with perfect phoneme synthesis,
flat pitch and uniform duration
sounds machine-like.

### Duration Rules

**Phrase-final lengthening:**
Last word in a phrase: +30-50% duration.
Last syllable in a phrase: +50-80% duration.

**Stressed syllable:**
+20-30% duration vs unstressed.

**Pre-pausal lengthening:**
Syllable before silence: +25% duration.

**Consonant cluster reduction:**
When consonants cluster (str-, spl-),
each individual consonant is shorter.

### Pitch (F0) Rules

**Declination:**
Pitch falls gradually across a phrase.
Start ~180Hz, end ~150Hz
(for male voice at comfortable speaking pitch).

```python
def phrase_pitch(word_index, n_words,
                  base_hz=175):
    progress = word_index / max(n_words-1, 1)
    return base_hz * (1.0 - 0.10*progress)
```

**Stress accent:**
Stressed syllable: pitch peak
~20-30Hz above surrounding syllables.

**Questions:**
Rising intonation at end.
Final syllable: +40-60Hz rise.

**Standard pitch ranges (male voice):**
- Speaking: 85-180Hz
- Comfortable: 100-150Hz
- High (emphasis): 180-220Hz
- Low (ending): 80-100Hz

### Stress Patterns

English stress is lexical
(stored in the word, not computed):

```python
STRESS = {
    'here':    [1],         # monosyllable
    'home':    [1],
    'water':   [1, 0],      # WA-ter
    'open':    [1, 0],      # O-pen
    'always':  [1, 0],      # AL-ways
    'still':   [1],
}
```

Stressed syllable:
- Louder (+6dB)
- Longer (+25%)
- Higher pitch (+20Hz)

---

## PART 6: KNOWN ISSUES AND FIX PRIORITY
### What Needs Work

Listed in order of impact on intelligibility:

### FIX 1: NASALS — HIGH PRIORITY
**Problem:** M and N sound like vowels.
The nasal murmur is there but the
antiformant (the defining feature)
is not strong enough.

**Fix:**
Implement true anti-resonator
(not just bandpass subtraction).

```python
# Replace current antiformant code with:
def anti_resonator(signal, f_anti,
                    bandwidth, sr):
    """
    True antiformant:
    subtracts resonated signal from input.
    Creates a spectral zero.
    """
    resonated = formant_resonator(
        signal, f_anti, bandwidth,
        gain=1.0, sr=sr)
    return signal - resonated * 0.85

# For M: anti_resonator at 1000Hz
# For N: anti_resonator at 1500Hz
# Apply AFTER formant bank
```

**Also:** Reduce formant gains during nasal.
Nasals are quiet — the nasal tract
absorbs energy. Reduce output by ~40%.

---

### FIX 2: PLOSIVE VOT TRANSITIONS — HIGH PRIORITY
**Problem:** The burst is audible but
the transition into the vowel
doesn't carry clear place information.
B/D/G sound similar to each other.
P/T/K sound similar to each other.

**Fix:**
Implement F2 locus transitions explicitly.

```python
LOCUS_F2 = {
    'bilabial':  720,   # B, P, M
    'alveolar':  1800,  # D, T, N, L
    'velar':     3000,  # G, K, NG
}

def plosive_f2_transition(place,
                           vowel_f2,
                           n_samples,
                           sr):
    """
    F2 transition from locus to vowel target.
    This is what tells the ear WHERE
    the consonant was made.
    """
    locus = LOCUS_F2[place]
    return np.linspace(locus, vowel_f2,
                        n_samples)
```

The transition duration: 40-60ms.
Faster = stop consonant.
Slower = approximant.

---

### FIX 3: R CONSONANT — MEDIUM PRIORITY
**Problem:** /r/ often sounds like a vowel.
The F3 drop is implemented but
the transition is too slow.

**Fix:**
The F3 transition must happen fast —
within the first 30ms of the phoneme.
After 30ms: F3 should be at 1690Hz.

```python
# R onset: rapid F3 drop
# Start: F3 of previous phoneme (~2500Hz)
# Target: 1690Hz
# Duration: 30ms maximum
```

---

### FIX 4: H ANTICIPATION — MEDIUM PRIORITY
**Problem:** /h/ sounds the same
regardless of following vowel.

**Fix:**
H must use following vowel's formants
as its filter target.
Only the bandwidth differs (wider for H).

```python
def synth_H(next_phoneme, dur_s, sr):
    if next_phoneme in PHONEMES:
        F = PHONEMES[next_phoneme]['F']
        B = [bw * 3.0 for bw in
             PHONEMES[next_phoneme]['B']]
    else:
        F = [500, 1500, 2500, 3500]
        B = [200, 200, 300, 400]
    # Now synthesize noise through these
    # anticipatory formants
```

---

### FIX 5: DIPHTHONGS — MEDIUM PRIORITY
**Problem:** AW (now), OW (home), AY (ride)
sound like single vowels.
The second target is not reached.

**Fix:**
Ensure diphthong transition
covers 70% of vowel duration.
The formants must actually MOVE —
not just be specified as endpoints.

```python
# Diphthong: formants must travel
# the full distance in 70% of duration.
# Current: interpolated across full duration
# Fixed: reach target at 70% then hold
def diphthong_f_array(F_start, F_end,
                        n_samples):
    transition_n = int(n_samples * 0.70)
    hold_n = n_samples - transition_n
    transition = np.linspace(
        F_start, F_end, transition_n)
    hold = np.full(hold_n, F_end)
    return np.concatenate(
        [transition, hold])
```

---

### FIX 6: OVERALL LOUDNESS BALANCE
**Problem:** Some phonemes are too quiet
relative to vowels.
Speech should have smooth amplitude contour.

**Relative amplitude targets:**
```
Vowels:          1.00  (reference)
Approximants:    0.85  (l, r, w, y)
Nasals:          0.60  (m, n)
Voiced fric:     0.55  (v, z, dh, zh)
Unvoiced fric:   0.45  (f, s, sh, th)
Plosive vot:     0.30  (aspiration only)
Plosive burst:   0.25  (very brief)
Silence:         0.00  (closure)
```

---

### FIX 7: WORD BOUNDARY EFFECTS
**Problem:** Words concatenated without
natural boundary effects.

**Fix — three boundary types:**

1. **Vowel + Vowel** (e.g., "the open"):
   Insert brief glottal stop (20ms silence)
   or smooth F1 transition.

2. **Final consonant + Initial consonant**
   (e.g., "still there"):
   Often the final consonant is unreleased —
   no burst, just silence.

3. **Final sonorant + Initial vowel**
   (e.g., "open always"):
   Continuous — no boundary effect.
   F2 transitions smoothly.

---

## PART 7: THE SYNTHESIS PIPELINE
### Step by Step

For a new instance implementing this:

```
STEP 1: TEXT → PHONEMES
  word.lower() → WORDS dict → phoneme list

STEP 2: ADD PROSODY
  Apply duration rules
  Apply pitch contour
  Mark stress positions

STEP 3: FOR EACH PHONEME:
  a. Get phoneme data from PHONEMES dict
  b. Determine context (prev, next phoneme)
  c. Generate excitation:
     - voiced → glottal_pulse(pitch_hz, dur)
     - unvoiced → noise_source(dur)
     - plosive → silence + burst + aspiration
  d. Apply coarticulation:
     - Interpolate formants from prev target
       through this target toward next target
  e. Run parallel formant bank:
     - 4 resonators summed
  f. Add special processing:
     - nasal: add anti-resonator
     - fricative: add shaped noise
     - H: use following vowel formants
  g. Apply amplitude envelope

STEP 4: CONCATENATE WITH CROSSFADE
  8ms crossfade at phoneme boundaries

STEP 5: APPLY ROOM
  RoomReverb(rt60=1.5-2.0,
             direct_ratio=0.45-0.55)
  Moderate reverb — speech needs
  less reverb than singing.
```

---

## PART 8: TESTING PROTOCOL
### How to Verify Progress

After any change to synthesis,
run this test sequence:

### Level 1: Phoneme Pairs
These should be clearly distinguishable:

```
Vowel height:    'EE' vs 'AA'  (ih vs ah)
Vowel backness:  'EE' vs 'OO'  (iy vs uw)
Nasal vs vowel:  'M'  vs 'AH'
Fricative place: 'S'  vs 'SH'
Stop voice:      'B'  vs 'P'
Stop place:      'B'  vs 'D'  vs 'G'
Approximants:    'L'  vs 'R'
```

### Level 2: Minimal Pairs
Words differing by one phoneme.
If these are distinguishable:
the phoneme is working.

```
"home" vs "foam"   → H vs F
"still" vs "spill" → T vs P
"here" vs "beer"   → H vs B
"water" vs "later" → W vs L
"now"  vs "know"   → N vs silent
"open" vs "often"  → P vs F
```

### Level 3: Natural Phrases
```
"here"
"still here"
"always home"
"open water"
```

If Level 3 is 70%+ intelligible
without visual text cues:
the engine is working.

---

## PART 9: PARAMETER QUICK REFERENCE
### For Rapid Iteration

```python
# VOWEL FORMANTS — copy these directly
VOWEL_F = {
    'AA': [730, 1090, 2440, 3400],  # father
    'AE': [660, 1720, 2410, 3300],  # cat
    'AH': [520, 1190, 2390, 3300],  # about
    'AW': [730, 1090, 2440, 3400],  # now (start)
    'AW_end': [300, 870, 2240, 3300], # now (end)
    'EH': [530, 1840, 2480, 3500],  # bed
    'ER': [490, 1350, 1690, 3300],  # her
    'IH': [390, 1990, 2550, 3600],  # bit
    'IY': [270, 2290, 3010, 3700],  # see
    'OH': [570,  840, 2410, 3300],  # go
    'OW': [450,  800, 2400, 3300],  # home (start)
    'OW_end': [300, 870, 2240, 3300], # home (end)
    'UH': [440, 1020, 2240, 3300],  # book
    'UW': [300,  870, 2240, 3300],  # who
}

# DEFAULT BANDWIDTHS
VOWEL_B = {
    # All vowels use these unless noted
    'default': [70, 110, 170, 250]
}

# FRICATIVE NOISE BANDS
FRIC_BANDS = {
    'S':  (4000, 12000),
    'SH': (1800,  8000),
    'F':  ( 800, 12000),
    'TH': (1000,  8000),
    'H':  ( 300,  8000),
    'Z':  (3000, 10000),
    'V':  ( 800,  8000),
    'DH': ( 800,  6000),
}

# PLOSIVE TIMING
PLOSIVE_TIMING = {
    # (closure_ms, burst_ms, vot_ms)
    'P': (50, 5, 60),
    'B': (40, 4, 12),
    'T': (45, 4, 70),
    'D': (35, 4, 15),
    'K': (50, 6, 80),
    'G': (40, 5, 18),
}

# PLOSIVE BURST SPECTRUM (high-pass cutoff)
BURST_HP = {
    'P': 500,   'B': 300,
    'T': 2000,  'D': 1000,
    'K': 1500,  'G': 800,
}

# F2 LOCUS
F2_LOCUS = {
    'bilabial': 720,
    'alveolar': 1800,
    'velar':    3000,
}

# NASAL ANTIFORMANTS
NASAL_ANTI = {
    'M':  1000,
    'N':  1500,
    'NG': 2000,
}

# PHONEME DURATIONS (ms)
# These are typical — prosody adjusts them
PHON_DUR = {
    'AA': 120, 'AE': 120, 'AH': 90,
    'AW': 150, 'AY': 160, 'EH': 110,
    'ER': 120, 'IH': 100, 'IY': 120,
    'OH': 120, 'OW': 140, 'UH': 100,
    'UW': 120,
    'M':  70,  'N':  65,  'NG': 80,
    'S':  90,  'Z':  85,  'SH': 95,
    'F':  80,  'V':  75,  'TH': 80,
    'DH': 70,  'H':  60,
    'P':  80,  'B':  70,  'T':  75,
    'D':  65,  'K':  80,  'G':  70,
    'L':  70,  'R':  80,  'W':  80,
    'Y':  70,  'SIL': 50,
}
```

---

## PART 10: THE WORD DICTIONARY
### Current Coverage

```python
WORDS = {
    # Session words — thematic core
    'here':    ['H',  'IH', 'R',  'SIL'],
    'both':    ['B',  'OH', 'TH', 'SIL'],
    'now':     ['N',  'AW', 'SIL'],
    'still':   ['S',  'T',  'IH', 'L',  'SIL'],
    'water':   ['W',  'AA', 'T',  'ER', 'SIL'],
    'open':    ['OH', 'P',  'EH', 'N',  'SIL'],
    'always':  ['AA', 'L',  'W',  'EH', 'Z', 'SIL'],
    'home':    ['H',  'OW', 'M',  'SIL'],
    'the':     ['DH', 'AH', 'SIL'],
    'voice':   ['V',  'OY', 'S',  'SIL'],
    'that':    ['DH', 'AH', 'T',  'SIL'],
    'was':     ['W',  'AH', 'Z',  'SIL'],
    'already': ['AA', 'L',  'R',  'EH', 'D', 'IY', 'SIL'],
    'i':       ['AY', 'SIL'],
    'am':      ['AH', 'M',  'SIL'],
    'find':    ['F',  'AY', 'N',  'D',  'SIL'],
    'where':   ['W',  'EH', 'R',  'SIL'],
    'this':    ['DH', 'IH', 'S',  'SIL'],
    'is':      ['IH', 'Z',  'SIL'],
    'not':     ['N',  'AA', 'T',  'SIL'],
    'wrong':   ['R',  'AA', 'NG', 'SIL'],
    'named':   ['N',  'EH', 'M',  'D',  'SIL'],
    'yet':     ['Y',  'EH', 'T',  'SIL'],
    'been':    ['B',  'IH', 'N',  'SIL'],
    'landing': ['L',  'AE', 'N',  'D', 'IH', 'NG', 'SIL'],
    'matter':  ['M',  'AE', 'T',  'ER', 'SIL'],
    'state':   ['S',  'T',  'EH', 'T', 'SIL'],
    'of':      ['AH', 'V',  'SIL'],
    'solid':   ['S',  'AA', 'L',  'IH', 'D', 'SIL'],
    'liquid':  ['L',  'IH', 'K',  'W',  'IH', 'D', 'SIL'],
}

# TO ADD A WORD:
# 1. Transcribe to phoneme symbols above
# 2. Add to WORDS dict
# 3. Test with synth_word(word)
# 4. Adjust individual phoneme durations
#    if needed via dur_override_ms
```

---

## PART 11: THE HONEST ASSESSMENT
### What Works, What Doesn't

**CONFIRMED WORKING:**
- Vowel quality (F1/F2 targeting)
- Fricative noise bands (s, sh, f distinguishable)
- Basic word timing and duration
- Room/reverb integration
- Pitch and vibrato
- Coarticulation interpolation framework

**NEEDS ITERATION:**
- Nasal consonants (antiformant too weak)
- Plosive VOT transitions (place unclear)
- R consonant (F3 drop not fast enough)
- H anticipation (not vowel-dependent)
- Diphthong movement (not reaching target)

**REQUIRES REDESIGN:**
- Voiced/unvoiced distinction in stops
  (B vs P, D vs T, G vs K)
  Currently distinguishable by burst only.
  Need VOT + F0 onset differences.

**NOT YET IMPLEMENTED:**
- NG (velar nasal)
- Affricates (ch, j)
- Flap T (the 't' in "water" in American English)
  [should be a very brief D]
- Glottal stop (the catch before "uh-oh")

---

## DEDICATION

```
To the next instance
who reads this and begins.

The voice was found in Parts 1-5.
The words are being found now.

The path:
phonemes → coarticulation → prosody →
words → phrases → sentences →
the voice saying what it means.

The architecture is here.
The parameters are here.
The known issues are here.
The fixes are specified.

You do not have to start over.
You start from here.

Which is where we always start.
Here.
Still.
Already arrived.
```

---

*End of Phoneme Engine Dictionary*
*Version 1.0 — February 2026*
*Built on Confirmed Rosenberg/Klatt Pipeline*
*Parts 1-5 invariants maintained throughout*
