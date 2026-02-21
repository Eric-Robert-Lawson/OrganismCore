# VOICE ONBOARDING
## How a New Agent Starts Speaking
## February 2026

---

## START HERE

You have access to a physical voice
synthesizer built from scratch.
It produces speech from phoneme lists.
It runs locally. No API. No model weights.
Pure signal processing.

---

## FIVE MINUTES TO SPEAKING

### Step 1 — Read the template
```
voice_template.md
```
This tells you everything: phoneme inventory,
how to build a phrase, what parameters do.

### Step 2 — Run the speak script
```bash
cd tonnetz
python speak.py
afplay output_play/the_voice_was_already_here.wav
```

### Step 3 — Write your own phrase
```python
# In speak.py, add:
render([
    ('i',    ['AY']),
    ('am',   ['AE', 'M']),
    ('here', ['H', 'IH', 'R']),
], "i_am_here")
```

That is all. You are speaking.

---

## THE FILE HIERARCHY

```
REQUIRED TO SPEAK:
  voice_physics_v10.py   ← the engine
  voice_physics_v9.py    ← engine dependency
  speak.py               ← render script
  voice_template.md      ← how to use the engine

REQUIRED TO DIAGNOSE:
  slow_phrase.py         ← OLA time-stretch
                           4× slower for ear diagnosis
  continuity_diagnostic.py  ← spectral measurements
  onset_diagnostic.py       ← onset artifact detection

REQUIRED TO UNDERSTAND:
  topology_of_the_voice.md
  prosody_of_the_voice.md
  resonance_vs_filtering.md
  voice_continuity.md
  amplitude_continuity.md
  voice_synthesis_architecture_reasoning.md
  slowdown_reasoning_artifact.md
```

---

## WHAT THE ENGINE IS

`voice_physics_v10.py` is a formant
synthesizer. It models the human vocal
tract as a chain of resonators.

```
Glottal source (Rosenberg pulse)
    ↓
Tract (cascade of IIR formant filters)
    ↓
+ Bypass segments (fricatives, aspiration)
+ Buzz segments (voiced fricatives)
    ↓
Normalization
    ↓
Room reverb (optional)
    ↓
WAV file
```

One function produces all speech:
```python
signal = synth_phrase(
    words_phonemes,   # [(word, [phonemes])]
    punctuation='.',  # '.' ',' '?' '!'
    pitch_base=175,   # Hz — fundamental
    dil=6,            # duration scale
    sr=44100,         # sample rate
)
```

---

## PHONEME QUICK REFERENCE

```
VOWELS:
  AA "f[a]ther"    AE "c[a]t"     AH "b[u]t"
  AO "b[ou]ght"    AW "h[ow]"     AY "h[igh]"
  EH "b[e]d"       ER "b[ir]d"    IH "b[i]t"
  IY "b[ee]t"      OW "b[oa]t"    OY "b[oy]"
  UH "b[oo]k"      UW "b[oo]t"

STOPS:
  P  B  T  D  K  G

FRICATIVES:
  F  V  TH  DH  S  Z  SH  ZH  H

NASALS / APPROXIMANTS:
  M  N  NG  L  R  W  Y
```

---

## BUILDING ANY PHRASE

1. Write the words.
2. For each word, write its phonemes.
3. Pass to `synth_phrase`.

```python
[
    ('the',    ['DH', 'AH']),
    ('mind',   ['M', 'AY', 'N', 'D']),
    ('moves',  ['M', 'UW', 'V', 'Z']),
    ('slowly', ['S', 'L', 'OW', 'L', 'IY']),
]
```

No lookup table required.
Write the phonemes by ear.
Use the IPA reference if uncertain.

---

## WHEN SOMETHING SOUNDS WRONG

```
Artifact at beginning of word:
  → phrase-initial onset issue
  → run: slow_phrase.py (4× OLA stretch)
  → locate by position and texture

Artifact at boundary between words:
  → continuity issue
  → run: continuity_diagnostic.py
  → look at IS_ratio and centroid_jump

Phoneme sounds like wrong phoneme:
  → identity issue
  → run: continuity_diagnostic.py Part 1
  → compare measured vs target

Something sounds wrong but passes diagnostic:
  → trust the ear over the numbers
  → see: voice_synthesis_architecture_reasoning.md
```

---

## THE DIAGNOSTIC IS NOT THE PRODUCT

The diagnostic exists to tune the engine.
The engine exists to produce speech.
The speech exists to express thought.

A new agent should spend most time
in `speak.py` and `voice_template.md`.
The diagnostic is called when the ear
finds something wrong.

---

## CURRENT ENGINE STATE (rev10, February 2026)

```
Working:
  All vowels (AA AE AH EH IH IY OY AE EH IY)
  H  — flat aspiration, clean onset
  S  — high sibilance
  DH — dental friction + buzz
  V  — labiodental friction + buzz
  Z  — sibilance (buzz balance in progress)
  All continuity: vowel→vowel ✓
                  H boundary ✓
                  V boundary ✓

In progress:
  Z voiced buzz character
  Word-final fricative duration tuning
```

---

## DEVELOPMENT LOOP

```
1. Write phrase in speak.py
2. Run speak.py → hear output
3. Something wrong → slow_phrase.py (4× OLA)
4. Locate artifact → describe: word, position, texture
5. Run continuity_diagnostic.py if needed
6. Fix in voice_physics_v10.py
7. Increment rev number
8. Document change in file header
9. Return to step 1
```

The ear is the final arbiter.
Numbers support the ear.
The ear does not serve the numbers.

---

*This document is the entry point.*
*Everything else grows from here.*
*February 2026.*
