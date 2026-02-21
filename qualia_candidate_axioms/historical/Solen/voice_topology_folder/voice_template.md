# VOICE TEMPLATE
## How to Speak Using voice_physics_v10
## February 2026

---

## WHAT THIS IS

This file is the speaking template.
It defines how to construct speech using
the synthesis engine.
It is meant to be iterated — as the engine
improves, this template grows in expressive
range.

The diagnostic exists to serve this.
The engine exists to serve this.
This is the top of the stack.

---

## THE INSTRUMENT

```python
from voice_physics_v10 import (
    synth_phrase,
    apply_room,
    write_wav,
    ola_stretch,
    PITCH, DIL, SR, f32,
)
```

One function does all synthesis:

```python
signal = synth_phrase(
    words_phonemes,   # list of (word, [phonemes])
    punctuation='.',  # '.' ',' '?' '!'
    pitch_base=PITCH, # fundamental frequency Hz
    dil=DIL,          # duration scale (default 6)
    sr=SR,            # sample rate (default 44100)
)
```

---

## PHONEME INVENTORY

### Vowels (all working ✓)
```
AA  "f[a]ther"      AE  "c[a]t"
AH  "b[u]t"         AO  "b[ou]ght"
AW  "h[ow]"         AY  "h[igh]"
EH  "b[e]d"         ER  "b[ir]d"
IH  "b[i]t"         IY  "b[ee]t"
OW  "b[oa]t"        OY  "b[oy]"
UH  "b[oo]k"        UW  "b[oo]t"
```

### Consonants — Stops
```
P   "s[p]ot"        B   "[b]ot"
T   "s[t]op"        D   "[d]og"
K   "s[k]y"         G   "[g]o"
```

### Consonants — Fricatives (all working ✓)
```
F   "[f]an"         V   "[v]an"
TH  "[th]in"        DH  "[th]e"
S   "[s]un"         Z   "[z]oo"
SH  "[sh]oe"        ZH  "vi[si]on"
H   "[h]at"
```

### Consonants — Nasals / Approximants
```
M   "[m]an"         N   "[n]ot"
NG  "si[ng]"        L   "[l]eg"
R   "[r]ed"         W   "[w]et"
Y   "[y]es"
```

---

## CONSTRUCTING A PHRASE

Each word is a tuple: `(word_string, [phonemes])`.

```python
phrase = [
    ('the',   ['DH', 'AH']),
    ('voice', ['V', 'OY', 'S']),
    ('was',   ['W', 'AH', 'Z']),
    ('here',  ['H', 'IH', 'R']),
]
```

The word string is used for prosody planning
(stress, duration, rest between words).
The phoneme list is what gets synthesized.

### Punctuation affects prosody

```python
'.'   # declarative — falling pitch, final rest
','   # clause pause — brief rest, pitch held
'?'   # interrogative — rising pitch at end
'!'   # emphatic — louder, slightly faster
```

---

## EXPRESSIVE PARAMETERS

### Pitch
```python
PITCH = 175   # default — mid male voice
              # range: 80 (deep) to 300 (high)
```

### Duration scale
```python
DIL = 6       # default — natural speech rate
              # 3 = fast,  6 = natural, 10 = slow
              # NOTE: phonemes cap at max durations.
              # DIL above 6 has diminishing returns.
              # Use OLA stretch for diagnostic slow.
```

### Room
```python
apply_room(sig, rt60=1.5, dr=0.50)
# rt60: reverb time in seconds
#   0.3 = small dry room
#   0.8 = medium room
#   1.5 = large room / hall
#   2.5 = cathedral

# dr: direct/reverb ratio (0=all reverb, 1=dry)
#   0.3 = distant / submerged
#   0.5 = natural room presence
#   0.7 = close / intimate
#   0.9 = nearly dry
```

---

## SPEAKING PATTERNS

### Statement
```python
def say(text_and_phones, room=True):
    sig = synth_phrase(
        text_and_phones,
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=SR)
    if room:
        sig = apply_room(sig,
                         rt60=0.8, dr=0.60)
    return sig
```

### Question
```python
def ask(text_and_phones, room=True):
    sig = synth_phrase(
        text_and_phones,
        punctuation='?',
        pitch_base=PITCH,
        dil=DIL, sr=SR)
    if room:
        sig = apply_room(sig,
                         rt60=0.8, dr=0.60)
    return sig
```

### Slow / deliberate
```python
def say_slow(text_and_phones,
              factor=2.0, room=True):
    sig = synth_phrase(
        text_and_phones,
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL, sr=SR)
    sig = ola_stretch(sig, factor=factor)
    if room:
        sig = apply_room(sig,
                         rt60=1.0, dr=0.55)
    return sig
```

---

## TEST PHRASES — CURRENT SET

These phrases are chosen to exercise
the full phoneme inventory across natural
contexts. Each covers specific phoneme
classes in combination.

### Group 1 — Fricative-heavy
```python
PHRASES_FRIC = [
    # DH, V, Z, S all in one phrase
    [('the',    ['DH', 'AH']),
     ('oves',   ['AH', 'V', 'Z']),     # "of his"
     ('voice',  ['V', 'OY', 'S']),
     ('fades',  ['F', 'EH', 'D', 'Z'])],

    # H onset, S/Z in middle
    [('he',     ['H', 'IY']),
     ('sees',   ['S', 'IY', 'Z']),
     ('the',    ['DH', 'AH']),
     ('haze',   ['H', 'EH', 'Z'])],

    # TH and DH contrast
    [('this',   ['DH', 'IH', 'S']),
     ('thing',  ['TH', 'IH', 'NG']),
     ('breathes', ['B', 'R', 'IY', 'DH', 'Z'])],
]
```

### Group 2 — Vowel-heavy
```python
PHRASES_VOWEL = [
    # All major vowel classes
    [('i',      ['AY']),
     ('often',  ['AO', 'F', 'AH', 'N']),
     ('hear',   ['H', 'IH', 'R']),
     ('a',      ['AH']),
     ('low',    ['L', 'OW']),
     ('hum',    ['H', 'AH', 'M'])],

    # OY, AW, AY diphthongs
    [('the',    ['DH', 'AH']),
     ('oil',    ['OY', 'L']),
     ('and',    ['AE', 'N', 'D']),
     ('the',    ['DH', 'AH']),
     ('sky',    ['S', 'K', 'AY'])],
]
```

### Group 3 — Natural speech feel
```python
PHRASES_NATURAL = [
    # The original test phrase
    [('the',     ['DH', 'AH']),
     ('voice',   ['V', 'OY', 'S']),
     ('was',     ['W', 'AH', 'Z']),
     ('already', ['AA', 'L', 'R', 'EH', 'D', 'IY']),
     ('here',    ['H', 'IH', 'R'])],

    # New: nasal + stop + fricative
    [('the',     ['DH', 'AH']),
     ('mind',    ['M', 'AY', 'N', 'D']),
     ('moves',   ['M', 'UW', 'V', 'Z']),
     ('slowly',  ['S', 'L', 'OW', 'L', 'IY'])],

    # New: all approximants
    [('where',   ['W', 'EH', 'R']),
     ('will',    ['W', 'IH', 'L']),
     ('we',      ['W', 'IY']),
     ('walk',    ['W', 'AO', 'K'])],

    # New: stops and nasals
    [('nothing', ['N', 'AH', 'TH', 'IH', 'NG']),
     ('begins',  ['B', 'IH', 'G', 'IH', 'N', 'Z']),
     ('without', ['W', 'IH', 'DH', 'AW', 'T']),
     ('an',      ['AE', 'N']),
     ('end',     ['EH', 'N', 'D'])],
]
```

---

## RENDERING A SET OF PHRASES

```python
import os
from voice_physics_v10 import (
    synth_phrase, apply_room,
    write_wav, PITCH, DIL, SR, f32,
)

os.makedirs("output_play", exist_ok=True)

def render_phrase(phrase, name,
                   punct='.', room=True,
                   rt60=1.2, dr=0.55):
    sig = synth_phrase(
        phrase,
        punctuation=punct,
        pitch_base=PITCH,
        dil=DIL, sr=SR)
    if room:
        sig = apply_room(
            f32(sig), rt60=rt60, dr=dr)
    path = f"output_play/{name}.wav"
    write_wav(path, f32(sig), SR)
    words = ' '.join(w for w, _ in phrase)
    dur   = len(sig) / SR
    print(f"  {name}.wav  ({dur:.2f}s)")
    print(f"  \"{words}\"")
    return path
```

---

## ITERATION MODEL

This template grows in two directions:

### 1. Engine improvements
When a phoneme sounds wrong, the diagnostic
identifies the failure. The engine is fixed.
The template does not change — it just works
better.

### 2. Vocabulary / phrase expansion
New phrases are added to the test set.
New speaking patterns (questions, whispers,
emphasis) are added as named functions.
The phoneme dictionary grows.

### What the diagnostic is for
The diagnostic is not the product.
It is the alignment tool.
Run it when something sounds wrong.
The target is: every phrase in this template
sounds like natural speech.

---

## WHAT IS WORKING NOW (February 2026)

```
Vowels:    AA AE AH EH IH IY OY ✓
Fricatives: H S V Z DH ✓ (body)
Continuity: most vowel transitions ✓
            H boundary ✓
            DH boundary ✓
            V boundary ✓

In progress:
  Z voiced character (buzz balance)
  Phrase-initial H/DH onset artifact
  Word-final fricative duration
```

---

## WHAT THIS TEMPLATE IS NOT

Not a dictionary. Not a text-to-speech pipeline.
Not automatic phoneme lookup.

Every phrase is hand-crafted phoneme by phoneme.
This is intentional.
The voice is constructed, not generated.
Each phoneme sequence is a deliberate choice.

The constraint is also the precision.

---

*This template is a living document.*
*It grows with the engine.*
*The engine grows with the ear.*
*The ear is the final arbiter.*
