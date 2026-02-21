# PHONETIC TRANSCRIPTION GUIDE
## A Reasoning Artifact on the Gap Between
## English Spelling and ARPAbet Input
## February 2026

---

## WHAT THIS ARTIFACT IS FOR

The engine takes ARPAbet phoneme symbols.
English spelling does not map to those symbols
in any consistent way.

Every word you give to synth_phrase() must
be manually transcribed into ARPAbet.
If the transcription is wrong, the physics
is correct but the word is wrong.
The physics cannot fix a transcription error.
Only this document can.

This artifact records:
  1. The complete vowel inventory with
     listening tests and formant values.
  2. The complete consonant inventory with
     notes on the most error-prone symbols.
  3. The systematic transcription errors
     that have already been encountered.
  4. Rules for choosing between similar
     vowels and consonants.
  5. The v16 syllabified input format and
     when to use it.
  6. A growing word reference for words
     that have been transcribed and verified.

---

## PART I: THE VOWEL INVENTORY

Each entry has:
  - ARPAbet symbol
  - IPA equivalent
  - Keyword (the classic "test word")
  - Formant targets in this engine
  - What it sounds like in isolation
  - Tonnetz distance from H origin
  - Common confusion with other symbols

The Tonnetz distance is the measurable
departure from H baseline required to
produce this vowel. Larger distance =
tract must move further = longer ghost
between syllables when this vowel is
the nucleus.

---

### MONOPHTHONGS — FRONT

**IY** — /iː/ — "b**ee**t"
```
F1: ~300Hz   F2: ~2300Hz
High, front, tense.
Sounds like: "ee" in meet, feet, beat.
Tonnetz: (3, -2) — maximum front departure.
  Distance from H: 3.61. One of the two
  farthest vowels from baseline.
Before R: produces the near-vowel /ɪɹ/
  → use for "here", "near", "fear", "year"
  → NOT IH before R
Confused with: IH (too similar in
  spelling, very different in sound)
```

**IH** — /ɪ/ — "b**i**t"
```
F1: ~420Hz   F2: ~2050Hz
High, front, lax.
Sounds like: "i" in bit, sit, fill, him.
Tonnetz: (2, -1) — front, slightly high.
  Distance from H: 2.24.
Before R: coarticulates DOWN toward EH
  → produces "hare" not "here"
  → DO NOT USE IH before R in the same
     syllable when you want the near-vowel
Use for: "is", "it", "this", "with",
  "still", "did", "him", "beginning"
  (all syllables of "beginning")
Confused with: IY (tenser, higher)
              AH (lower, more central)
```

**EH** — /ɛ/ — "b**e**d"
```
F1: ~600Hz   F2: ~1750Hz
Mid, front, lax.
Sounds like: "e" in bed, red, said, head.
Tonnetz: (1, 0) — one step front of H.
  Distance from H: 1.00.
Before R: produces the square vowel /ɛɹ/
  → use for "there", "where", "care",
    "hare", "air", "bear"
  → this is the vowel you heard when
    IH R went wrong
Use for: "already" (EH in second syllable),
  "said", "bed", "red", "next"
Confused with: IH (IH is higher/tenser)
              AE (AE is lower/more open)
```

**AE** — /æ/ — "b**a**t"
```
F1: ~800Hz   F2: ~1800Hz
Low, front, lax.
Sounds like: "a" in bat, cat, had, man.
Noticeably open — jaw is low.
Tonnetz: (1, 1) — front and open.
  Distance from H: 1.41.
Use for: "am", "and", "that", "have",
  "can", "back"
Confused with: EH (EH is higher, less open)
              AH (AH is more central)
```

---

### MONOPHTHONGS — CENTRAL

**AH** — /ʌ/ — "b**u**t"
```
F1: ~700Hz   F2: ~1220Hz
Mid, central, lax.
Sounds like: "u" in but, cup, love, some.
Also used for unstressed "uh" — the schwa
  in function words: "the", "a", "of"
Tonnetz: (0, 1) — one step open from H.
  Distance from H: 1.00. Nearest vowel
  to baseline. The schwa is almost home.
Use for: "but", "cup", "something",
  "was" (unstressed), "the" (unstressed)
IMPORTANT: "am" is AE M, not AH M
  "am" stressed = /æm/ — the AE vowel
  "am" unstressed → AH M is acceptable
  but AE M is always correct
  → "I um here" happened because
    "am" was transcribed AH M
    AH = "uh" schwa = sounds like "um"
    AE = "a" in "bat" = sounds like "am"
Confused with: AE (AE is more front/open)
              AA (AA is lower/back)
```

**ER** — /ɜːɹ/ — "b**ir**d"
```
F1: ~490Hz   F2: ~1350Hz   F3: ~1700Hz
Mid-central, r-colored.
Sounds like: "er" in bird, word, her,
  learn, turn.
Tonnetz: (0, -1) — one step high from H.
  Distance from H: 1.00.
F3 suppression is the defining feature —
  the third formant drops, giving the
  "dark" r-colored quality.
  The 2D Tonnetz grid does not capture
  the F3 axis. ER is acoustically unique
  even at close distance.
Use for: r-colored vowels in the nucleus:
  "bird", "word", "her", "learn",
  "learning" (ER N IH NG)
Also works as nucleus for "here", "near":
  ('here', ['H', 'ER'])  — valid alternative
  to IY R. Slightly different quality.
  Try both. Use whichever sounds right.
Confused with: R (R is a consonant,
  ER is a vowel nucleus)
```

---

### MONOPHTHONGS — BACK

**UW** — /uː/ — "b**oo**t"
```
F1: ~310Hz   F2: ~870Hz
High, back, tense, rounded.
Sounds like: "oo" in boot, food, who, two.
Tonnetz: (-3, -2) — maximum back departure.
  Distance from H: 3.61. The mirror of IY
  across the origin. Both are equidistant
  from H. IY is far front-high. UW is
  far back-high. The ghost between them
  is the longest possible traversal.
Use for: "to", "who", "do", "you",
  "new", "through"
Confused with: UH (UH is lax, less back)
```

**UH** — /ʊ/ — "b**oo**k"
```
F1: ~450Hz   F2: ~1030Hz
High, back, lax.
Sounds like: "oo" in book, could, would,
  put, good.
Tonnetz: (-2, -1) — back and slightly high.
  Distance from H: 2.24.
Use for: "could", "would", "should",
  "good", "put", "full"
Confused with: UW (UW is tenser, darker)
```

**OH** — /oʊ/ (nucleus) — "b**oa**t"
```
F1: ~500Hz   F2: ~1000Hz
Mid, back.
Sounds like: "o" in know, go, so, no.
Tonnetz: (-2, 0) — two steps back from H.
  Distance from H: 2.00.
Note: in this engine OH is the mid-back
  vowel. Some words spelled "o" use AO
  (see below). When in doubt:
  "know", "go", "no", "so" → OH
  "thought", "caught", "law" → AO
```

**AO** — /ɔː/ — "b**ou**ght"
```
F1: ~600Hz   F2: ~900Hz
Low-mid, back, rounded.
Sounds like: "aw" in caught, law, thought.
Tonnetz: (-1, 1) — back and open.
  Distance from H: 1.41.
Use for: "thought", "caught", "law",
  "all", "also", "call"
Confused with: OH (OH is higher/more back)
              AA (AA is lower/more front)
```

**AA** — /ɑː/ — "f**a**ther"
```
F1: ~800Hz   F2: ~1200Hz
Low, back, unrounded.
Sounds like: "a" in father, start, palm.
Tonnetz: (-1, 2) — back and very open.
  Distance from H: 2.24.
Use for: "already" (AA first syllable),
  "father", "start", "calm", "arm"
Confused with: AE (AE is more front)
              AH (AH is more central/higher)
```

---

### DIPHTHONGS

Diphthongs begin at an onset position
and glide toward an endpoint.
The onset position is used for Tonnetz
distance calculation (ghost duration).

**AY** — /aɪ/ — "h**igh**"
```
Onset: low-central (~AE/AA region)
  Tonnetz onset: (1, 1)
Ends:  high-front (~IH/IY region)
Sounds like: "i" in high, my, time, like.
Use for: "I", "my", "time", "like", "high"
```

**AW** — /aʊ/ — "h**ow**"
```
Onset: low-central (~AA region)
  Tonnetz onset: (-1, 2)
Ends:  high-back (~UH/UW region)
Sounds like: "ow" in how, now, sound,
  out, down.
Use for: "how", "sound", "out", "down",
  "now"
```

**OY** — /ɔɪ/ — "b**oy**"
```
Onset: low-back (~AO region)
  Tonnetz onset: (-1, 1)
Ends:  high-front (~IH/IY region)
Sounds like: "oy" in boy, voice, join.
Use for: "voice" (V OY S), "boy", "join"
```

**OW** — /oʊ/ — "b**oa**t" (diphthong form)
```
Onset: mid-back (~OH region)
Ends:  high-back (~UH region)
Some engines use OH for this.
Use OH unless OW is specifically in
VOWEL_PHONEMES for this engine.
```

**EY** — /eɪ/ — "b**ai**t"
```
Onset: mid-front (~EH region)
  Tonnetz onset: (2, -1)
Ends:  high-front (~IH/IY region)
Sounds like: "a" in bait, make, same,
  name, take, hate.
Use for: "make", "same", "hate",
  "they", "say", "way", "day"
```

---

## PART II: THE CONSONANT INVENTORY

Consonants are paths through constriction
space. Every consonant departs from H
baseline, applies a constriction, and
returns toward the following vowel.

Only the most error-prone consonants are
documented here. The others are consistent.

---

### THE DH / TH PAIR

These are the same articulation —
tongue to upper teeth or ridge —
with one difference: glottis state.

**DH** — /ð/ — voiced dental fricative
```
"the", "this", "that", "there", "them"
"then", "they", "though", "with"

DH = dental contact × voiced glottis.
The voicing is secondary.
The dental friction is identity.
Too much voicing = DH sounds like a vowel.
v9 fix: DH_VOICED_FRACTION = 0.30.
DH max duration: 75ms.

DO NOT confuse with D:
  DH: tongue to teeth, friction audible
  D:  tongue to ridge, complete stop
  "the" = DH AH
  "day" = D EY
```

**TH** — /θ/ — unvoiced dental fricative
```
"think", "through", "three", "teeth"
"both", "something", "with"
  (final TH)

TH = dental contact × open glottis.
Breathy, not voiced.
No formant resonance — pure friction.
```

---

### THE H FAMILY

H is not a consonant among others.
H is the baseline state of the voice.
See h_ghost_topology.md for full theory.

**H** / **HH** — voiceless glottal
```
"here", "have", "home", "how"

In this engine: use HH for the ARPAbet
  symbol before vowels.
H is an alias that also works.

CRITICAL INSIGHT (v16):
  H is the Tonnetz origin. The baseline.
  H before a vowel = the vowel in approach,
  before full formant commitment.
  NOT a separate event prepended to the
  vowel. The onset of the vowel itself.

  v11 fix: H filters through following
  vowel's formants. This is why.

VOWEL-INITIAL WORDS:
  "event", "already", "I", "am", "always"
  All begin with unwritten H.
  v16 models this automatically.
  DO NOT add explicit HH before vowel-initial
  words in v16. The engine inserts the
  voiced H onset.

  In v15 and earlier:
  If "event" sounded clipped at the start,
  you could add explicit ['HH','IH','V'...]
  In v16: ['IH','V','EH','N','T'] is correct.
  The engine handles the onset.
```

---

### THE SOFT G / HARD G RULE

This is the most common consonant
transcription error.

**G** — /ɡ/ — velar stop (hard G)
```
Before A, O, U → hard G
  "garden" = G AA R D AH N
  "go"     = G OH
  "gun"    = G AH N
  "good"   = G UH D

Also word-initial before consonants:
  "green"  = G R IY N
  "grass"  = G R AE S
```

**JH** — /dʒ/ — voiced palatal affricate (soft G)
```
Before E, I, Y → soft G → JH
  "gin"     = JH IH N
  "begin"   = B IH JH IH N
  "general" = JH EH N ER AH L
  "ginger"  = JH IH N JH ER

Also spelled J:
  "judge"  = JH AH JH
  "just"   = JH AH S T
  "join"   = JH OY N

Also word-final -ge, -dge:
  "age"    = EY JH
  "large"  = L AA R JH
  "bridge" = B R IH JH

CH = /tʃ/ — unvoiced palatal affricate
  Same place, unvoiced:
  "church"  = CH ER CH
  "nature"  = N EY CH ER
  "much"    = M AH CH
  "which"   = W IH CH
  "beach"   = B IY CH

RULE:
  English letter G before E, I, Y → JH
  English letter G before A, O, U → G
  English letter J             → JH
  English letters -dge, -ge    → JH
  English letters -ch, tch     → CH
```

---

### NASALS

All nasals share the same voicing and
broad formant shape. Identity is place.

```
M  — bilabial:  lip closure
     "my", "am", "some", "him"
     Tonnetz: (0, 0) — near H origin

N  — alveolar:  tongue tip to ridge
     "no", "in", "and", "then"
     Tonnetz: (1, 0) — one step front

NG — velar:     back tongue to velum
     "ring", "beginning", "something"
     Tonnetz: (-2, 0) — two steps back
     NOTE: NG is never word-initial.
     "ng" in "sing" → NG
     "ng" in "finger" → NG G (two phones)
     "ng" in "singer" → NG (no G)
```

---

### APPROXIMANTS

```
L  — lateral alveolar
     "like", "already", "still", "learning"
     Tongue tip to ridge, air flows laterally.
     Before R in same syllable: L transitions
     into R without a clean boundary.
     Treat as separate phonemes.

R  — rhotic approximant
     "here", "there", "already", "learning"
     Retroflex or bunched — the F3 drops.
     Tonnetz: (0, -1) — shares ER topology.
     R as onset: before vowel (rhotic)
     R as coda:  after vowel (r-coloring)
     See RULE 1 for pre-R vowel choices.

W  — labio-velar approximant
     "was", "water", "with", "always"
     Lip rounding + back tongue raising.
     Tonnetz: (-1, -1) — between bilabial
     and velar.

Y  — palatal approximant
     "year", "you", "yes", "beyond"
     Tongue body toward palate.
     Tonnetz: (2, -1) — shares IY topology.
     NOT the vowel IY — Y is an onset
     consonant only.
     "year"  = Y IY R
     "you"   = Y UW
     "yes"   = Y EH S
```

---

## PART III: ERRORS ALREADY ENCOUNTERED

Record every transcription error the moment
it is identified. This section grows as the
engine is used.

---

### ERROR 1: IH R → sounds like EH R

**Word:** "here", "near", "fear"
**Wrong:** `['H', 'IH', 'R']`
**Heard:** "hare" — the EH vowel in "hare"
**Cause:** IH before R coarticulates
  downward toward EH space.
  The R pulls the first formant up and
  the second formant down, moving
  IH (F1~420, F2~2050) toward
  EH (F1~600, F2~1750) territory.
**Fix:** Use IY before R for the near-vowel.
  `['H', 'IY', 'R']`
  Or use ER as the nucleus:
  `['H', 'ER']`
**Rule:** For words where the vowel in
  the spelling is "ear", "eer", "ere",
  "ier" — use IY R or ER, never IH R.

---

### ERROR 2: AH M → sounds like "um"

**Word:** "am"
**Wrong:** `['AH', 'M']`
**Heard:** "I um here" instead of "I am here"
**Cause:** AH is the vowel in "but", "cup",
  "love". It is also the unstressed schwa —
  the "uh" sound. "um" is exactly AH M.
  The stressed English word "am" uses
  the AE vowel — the "a" in "bat."
**Fix:** `['AE', 'M']` for stressed "am"
  `['AH', 'M']` is acceptable only for
  very fast unstressed "am" in running
  speech — "I'm" reductions.
**Rule:** "am" as a content word = AE M.
  "am" as a function word reduced = AH M.
  When in doubt: AE M.

---

### ERROR 3: G before E/I → sounds like stop not affricate

**Word:** "beginning", "gin", "general"
**Wrong:** `['B','IH','G','IH','N','IH','NG']`
**Heard:** hard velar stop where affricate
  belongs — "be-GOIN-ing" not "beginning"
**Cause:** English G before E, I, Y is
  pronounced /dʒ/ (JH), not /ɡ/ (G).
  The soft G rule. G is the spelling.
  JH is the sound.
**Fix:** `['B','IH','JH','IH','N','IH','NG']`
**Rule:** See PART II soft G / hard G rule.
  When in doubt about G: what vowel follows?
  E, I, Y → JH. A, O, U → G.

---

### ERROR 4: Explicit HH before vowel-initial words in v16

**Context:** v16 only
**Wrong:** `('event', ['HH','IH','V','EH','N','T'])`
**Problem:** v16 inserts the voiced H onset
  automatically for vowel-initial words.
  An explicit HH will produce a doubled
  onset — a voiced H followed by another
  voiced H approximation.
**Fix:** `('event', ['IH','V','EH','N','T'])`
  Let v16 handle the unwritten H.
**Rule:** In v16+, do not add HH before
  vowel-initial words unless the explicit
  aspirated H is desired (as in "have",
  "here" — words where H is written and
  stressed). In those cases HH is correct.

---

## PART IV: DECISION RULES

When the right vowel is not obvious,
apply these rules in order.

---

### RULE 1: BEFORE R IN THE SAME SYLLABLE

R in the same syllable colors the
preceding vowel. The vowel target shifts.

| Intended vowel | Before R use |
|---|---|
| Near-vowel "ear" | IY R or ER |
| Square vowel "air" | EH R |
| Start vowel "ar" | AA R |
| North vowel "or" | AO R |
| Nurse vowel "ur/ir/er" | ER |
| Cure vowel "oor/ure" | UH R or UW R |

**Never use IH before R for the near-vowel.**

The syllabified format helps here:
  "here"  = ['H', 'IY', 'R']
            one syllable — IY and R are
            in the same syllable. IY R.
  "carry" = [['K','AE','R'],['IY']]
            two syllables — R is coda of
            first, not coloring the IY.

---

### RULE 2: STRESSED VS UNSTRESSED

English reduces unstressed vowels toward
schwa (AH). The same spelling sounds
different stressed vs unstressed.

| Word | Stressed | Unstressed |
|---|---|---|
| "am" | AE M | AH M |
| "the" | DH IY | DH AH |
| "a" | EY | AH |
| "of" | AH V | AH V |
| "and" | AE N D | AH N |
| "to" | T UW | T AH |
| "was" | W AA Z | W AH Z |
| "can" | K AE N | K AH N |
| "him" | HH IH M | IH M |
| "her" | HH ER | ER |
| "are" | AA R | ER |

For content words (nouns, verbs,
adjectives, adverbs): use the full
stressed form.
For function words (articles,
prepositions, auxiliaries) in running
speech: AH reduction is natural.
For diagnostic renders and slow playback:
use full stressed forms throughout so
individual phoneme quality is audible.

---

### RULE 3: DISTINGUISHING SIMILAR VOWELS

When two vowels sound similar and you are
not sure which is correct:

**IH vs AH:**
  IH = "bit" — front of mouth
  AH = "but" — center of mouth
  Tonnetz: IH is (2,-1), AH is (0,1).
  They are in different quadrants.
  Test: does it rhyme with "bit" or "but"?
  "is" = IH Z ✓
  "us" = AH S ✓
  "his" = HH IH Z ✓
  "bus" = B AH S ✓

**AH vs AE:**
  AH = "but" — mouth not very open
  AE = "bat" — mouth more open, jaw lower
  Tonnetz: AH is (0,1), AE is (1,1).
  Same openness axis, AE is more front.
  Test: does it rhyme with "but" or "bat"?
  "am" = AE M ✓ (bat, not but)
  "and" = AE N D ✓
  "some" = S AH M ✓ (but, not bat)

**IY vs IH:**
  IY = "beet" — tense, long
  IH = "bit" — lax, short
  Tonnetz: IY is (3,-2), IH is (2,-1).
  IY is further from H in both axes.
  Test: does it rhyme with "beet" or "bit"?
  "he" = HH IY ✓
  "him" = HH IH M ✓
  "already" (final syllable) = IY ✓
  "beginning" (all syllables) = IH ✓

**EH vs AE:**
  EH = "bed" — mid front
  AE = "bad" — low front
  Tonnetz: EH is (1,0), AE is (1,1).
  Same front axis, AE is more open.
  Test: does it rhyme with "bed" or "bad"?
  "said" = S EH D ✓
  "sad" = S AE D ✓

**OH vs AO:**
  OH = "boat/know" — mid back, moves
  AO = "bought/law" — low-mid back, stays
  Tonnetz: OH is (-2,0), AO is (-1,1).
  Test: does it rhyme with "know" or "law"?
  "go" = G OH ✓
  "law" = L AO ✓

**AA vs AH:**
  AA = "father" — back and low, jaw fully
    dropped, tongue retracted
  AH = "but" — central, not as open
  Tonnetz: AA is (-1,2), AH is (0,1).
  AA is further back and more open.
  Test: "palm" vs "pun" — which is closer?
  "arm" = AA R M ✓ (palm, not pun)
  "already" = AA L R EH D IY ✓ (first syl)

---

### RULE 4: WORDS WITH SILENT LETTERS
### OR MISLEADING SPELLING

English spelling is not phonetic.
These words are consistently transcribed
wrong based on spelling.

| Word | Wrong assumption | Correct |
|---|---|---|
| "know" | K N OH | N OH |
| "knife" | K N AY F | N AY F |
| "wrong" | W R AO NG | R AO NG |
| "write" | W R AY T | R AY T |
| "hour" | H AW R | AW R |
| "honest" | H AH N | AH N |
| "who" | W H UW | HH UW |
| "whole" | W H OH L | HH OH L |
| "one" | W AH N | W AH N ✓ (W is correct) |
| "once" | W AH N S | W AH N S ✓ |
| "two" | T W UW | T UW |
| "sword" | S W AO R D | S AO R D |
| "gin" | G IH N | JH IH N |
| "begin" | B IH G IH N | B IH JH IH N |
| "general" | G EH N ER AH L | JH EH N ER AH L |
| "age" | EY G | EY JH |
| "judge" | JH AH D JH | JH AH JH (coda JH) |
| "church" | CH ER T CH | CH ER CH |
| "nature" | N EY T UW R | N EY CH ER |
| "gesture" | G EH S T UW R | JH EH S CH ER |
| "schedule" | S K EH D | S K EH JH UH L |
|            | (AmE) | (AmE) |

---

### RULE 5: THE SCHWA TRAP

AH serves two roles:
  1. The stressed vowel in "but", "cup"
  2. The unstressed schwa in "a", "the",
     "of", "was", "to", "from"

This is correct — both are AH.
But AH should NEVER be used for:
  - "am" (= AE M)
  - "and" stressed (= AE N D)
  - "had" (= HH AE D)
  - "has" (= HH AE Z)
  - "can" stressed (= K AE N)
  - "back" (= B AE K)
  - "that" (= DH AE T)

These words have the AE vowel —
they rhyme with "bat", not "but."
The spelling "a" does not mean AH.

**The trap in reverse:** Do not use AE
for genuine schwa words. "about", "above",
"ago" all begin with AH, not AE.
AH = "uh". AE = "a" in "bat". They are
different phonemes at different places
in the mouth.

---

### RULE 6: THE SYLLABIFIED FORMAT (v16+)

From v16, synth_phrase() accepts nested
phoneme lists that encode syllable
boundaries explicitly.

**When to use flat format:**
  Single-syllable words.
  Words you have not yet syllabified.
  Quick tests where ghost precision
  does not matter.

```python
('voice', ['V', 'OY', 'S'])        # flat
('here',  ['H', 'IY', 'R'])        # flat
```

**When to use syllabified format:**
  Multisyllabic words where you want
  correct inter-syllable ghosts.
  Words where the stress placement
  matters perceptually.
  Any word in the canonical phrase that
  will be listened to carefully.

```python
('already',  [['AO', 'L'],         # syl 1
              ['R',  'EH'],         # syl 2 — STRESSED
              ['D',  'IY']])        # syl 3

('beginning',[['B',  'IH'],        # syl 1
              ['JH', 'IH'],        # syl 2 — STRESSED
              ['N',  'IH', 'NG']]) # syl 3

('something',[['S',  'AH', 'M'],   # syl 1 — STRESSED
              ['TH', 'IH', 'NG']]) # syl 2

('learning', [['L',  'ER'],        # syl 1 — STRESSED
              ['N',  'IH', 'NG']]) # syl 2
```

**Syllabification rule:**
  Each syllable has exactly one vowel
  (or one diphthong) as its nucleus.
  Onset consonants attach to the FOLLOWING
  vowel — they are the beginning of that
  vowel's approach from H.
  Coda consonants attach to the PRECEDING
  vowel — they are the return toward H
  from that vowel.

  "already": AO L | R EH | D IY
    Syl 1: AO L — the L closes the first syl
    Syl 2: R EH — the R opens the second
    Syl 3: D IY — the D opens the third
    The ghost at boundary 1 (AO→R):
      tract moves from AA region through H
      toward alveolar/rhotic position.
    The ghost at boundary 2 (EH→D):
      tract moves from EH region through H
      toward alveolar stop position.

  "beginning": B IH | JH IH | N IH NG
    Syl 1: B IH — bilabial stop to IH
    Syl 2: JH IH — affricate to IH (STRESSED)
    Syl 3: N IH NG — alveolar nasal to IH
             + velar nasal close

**Backward compatibility:**
  Flat lists still work in v16.
  The engine uses WORD_SYLLABLES lookup
  if available, else treats as one syllable.
  For multisyllabic words not in
  WORD_SYLLABLES: provide nested lists
  to get correct ghost placement.

---

## PART V: VERIFIED WORD REFERENCE

Words that have been transcribed, rendered,
and confirmed to sound correct.
Add to this list every time a word is
verified. Never re-derive a verified word.

For multisyllabic words, the syllabified
form is now the preferred reference.
The flat form is included for v15
compatibility.

---

### VERIFIED — CORRECT

```
the         DH AH
            syllabified: ['DH','AH'] (1 syl)

voice       V OY S
            syllabified: [['V','OY'],['S']]
            (V and OY are onset+nucleus of
            syl 1; S is coda closing to H)

was         W AH Z
            syllabified: ['W','AH','Z'] (1 syl)

already     AA L R EH D IY
            syllabified: [['AO','L'],
                          ['R','EH'],
                          ['D','IY']]
            NOTE: first syl uses AO not AA —
            in this engine AO better matches
            the rounded "aw" onset of "already"
            than the fully open AA.
            Verify perceptually.

here        H IY R
            syllabified: ['H','IY','R'] (1 syl)
            near-vowel fix: IY not IH before R

something   S AH M TH IH NG
            syllabified: [['S','AH','M'],
                          ['TH','IH','NG']]

is          IH Z
            syllabified: ['IH','Z'] (1 syl)

beginning   B IH JH IH N IH NG
            syllabified: [['B','IH'],
                          ['JH','IH'],
                          ['N','IH','NG']]
            NOTE: G→JH soft G fix.
            v15+ required.

to          T UW
            syllabified: ['T','UW'] (1 syl)

sound       S AW N D
            syllabified: ['S','AW','N','D'] (1 syl)

like        L AY K
            syllabified: ['L','AY','K'] (1 syl)

I           AY
            syllabified: ['AY'] (1 syl)
            v16: voiced H onset automatic

did         D IH D
            syllabified: ['D','IH','D'] (1 syl)

not         N AH T
            syllabified: ['N','AH','T'] (1 syl)

know        N OH
            syllabified: ['N','OH'] (1 syl)
            silent K — never K N

could       K UH D
            syllabified: ['K','UH','D'] (1 syl)

am          AE M
            syllabified: ['AE','M'] (1 syl)
            NOT AH M — schwa trap

still       S T IH L
            syllabified: ['S','T','IH','L'] (1 syl)

learning    L ER N IH NG
            syllabified: [['L','ER'],
                          ['N','IH','NG']]
            ER nucleus — verified

how         H AW
            syllabified: ['H','AW'] (1 syl)

near        N IY R
            syllabified: ['N','IY','R'] (1 syl)
            near-vowel fix

fear        F IY R
            syllabified: ['F','IY','R'] (1 syl)
            near-vowel fix

year        Y IY R
            syllabified: ['Y','IY','R'] (1 syl)
            near-vowel fix

clear       K L IY R
            syllabified: ['K','L','IY','R'] (1 syl)
            near-vowel fix

who         HH UW
            syllabified: ['HH','UW'] (1 syl)

what        W AH T
            syllabified: ['W','AH','T'] (1 syl)

this        DH IH S
            syllabified: ['DH','IH','S'] (1 syl)

judge       JH AH JH
            syllabified: ['JH','AH','JH'] (1 syl)
            v15+ required

gin         JH IH N
            syllabified: ['JH','IH','N'] (1 syl)
            v15+ required

church      CH ER CH
            syllabified: ['CH','ER','CH'] (1 syl)
            v15+ required

much        M AH CH
            syllabified: ['M','AH','CH'] (1 syl)
            v15+ required

each        IY CH
            syllabified: ['IY','CH'] (1 syl)
            v15+ required
            v16: voiced H onset automatic

age         EY JH
            syllabified: ['EY','JH'] (1 syl)
            v15+ required

event       IH V EH N T
            syllabified: [['IH','V'],
                          ['EH','N','T']]
            v16: voiced H onset automatic
            do NOT prefix with HH

evening     IY V IH N IH NG
            syllabified: [['IY','V'],
                          ['IH','N'],
                          ['IH','NG']]
            v16: voiced H onset automatic

water       W AO T ER
            syllabified: [['W','AO'],
                          ['T','ER']]
```

---

### PENDING VERIFICATION

Words used but not yet confirmed
to sound correct in v16.

```
already (first syl): AO or AA?
  Current: AO L (rounded onset)
  Alternative: AA L (fully open)
  Verify: does "already" sound natural?
  The ghost between AO-L and R-EH
  will be audible in v16 slow render.

her        HH ER
  vs:      HH IH R
  ER is likely correct. Verify.

were       W ER
  vs:      W IH R
  W ER is correct. Verify in sentence.

there      DH EH R
  Square vowel. Not yet verified.

where      W EH R
  Same as "there". Not verified.

they       DH EY
  EY diphthong. Not verified.

their      DH EH R
  Same phonemes as "there". Not verified.

nature     N EY CH ER
  v15+ required for CH. Not verified.

water      W AO T ER
  See verified list — added as pending
  formal verification.
```

---

### KNOWN PROBLEM WORDS

Words where the correct transcription
is uncertain or the engine has a known
limitation.

```
"the" before vowels:
  "the event" — does DH AH produce a
  clean transition into IH V in v16?
  Or should it be DH IY before vowels?
  Standard English: "the" before vowels
  often reduces to /ðɪ/ (DH IH) in
  careful speech.
  Current: DH AH throughout.
  Consider: DH IH before vowel-initial words
  for careful register.

"a" before vowels:
  "a event" → colloquially "an event"
  "an" = AE N before vowels.
  "a" = AH
  Use "an" with its transcription when
  the following word is vowel-initial.

"her" at phrase end:
  "I saw her" — final ER often reduced
  further. Can be just ER with no HH.
  Verify perceptually.

Words ending in "-tion", "-sion":
  "nation"  = N EY SH AH N
              [['N','EY'],['SH','AH','N']]
  "vision"  = V IH ZH AH N
              [['V','IH'],['ZH','AH','N']]
  "station" = S T EY SH AH N
  The SH (or ZH for -sion) nucleus is
  the syllable boundary point.
  Not yet verified.

Words ending in "-ture":
  "nature"  = N EY CH ER
  "feature" = F IY CH ER
  "culture" = K AH L CH ER
  v15+ required. Not yet verified.
```

---

## PART VI: THE DIAGNOSTIC METHOD

When a word sounds wrong, do this:

**Step 1: Isolate the word.**
Render it alone at 4× slow with v16:

```python
from voice_physics_v16 import (
    synth_phrase, save, _ola_stretch,
    recalibrate_gains_v8, SR, PITCH,
    ARC_NORMAL
)

recalibrate_gains_v8(sr=SR)

seg_slow = _ola_stretch(
    synth_phrase(
        [('word', ['X', 'X', 'X'])],
        punctuation='.',
        add_breath=False,
        add_ghost=False),
    factor=4.0)
save("test_word_slow", seg_slow,
     rt60=0.6, dr=0.72)
```

Use `add_ghost=False` for phoneme
diagnosis. The ghost is correct behavior —
turn it off to hear bare phonemes.

**Step 2: Identify which phoneme is wrong.**
At 4× slow, each phoneme is 4× longer.
The vowel body — the steady-state middle —
is audible as a distinct sustained tone.
Compare it to the vowel inventory above.

**Step 3: Check the decision rules.**
Before R?        → Rule 1.
Stressed?        → Rule 2.
Similar vowels?  → Rule 3.
Silent letters?  → Rule 4.
Schwa trap?      → Rule 5.
Soft/hard G?     → Part II consonants.

**Step 4: Fix the transcription only.**
Do not change voice_physics_v*.py.
Change the phoneme list in the calling
script.

**Step 5: Add to the verified word list.**
Once the word sounds correct, record it
in Part V with the syllabified form.
Do not re-derive a verified word.

**Step 6: Ghost diagnosis (v16 only).**
If the word sounds correct in isolation
but wrong in a phrase, the issue may be
the ghost between syllables.

```python
# Test with and without ghost
seg_no_ghost = synth_phrase(
    [('word', ['X', 'X', 'X'])],
    add_ghost=False)
seg_ghost = synth_phrase(
    [('word', ['X', 'X', 'X'])],
    add_ghost=True)
```

If `no_ghost` sounds correct but `ghost`
sounds wrong: the syllable boundaries
in the nested format are wrong. Check
the syllabification.

If both sound wrong: the phonemes are
wrong. Go back to Step 2.

---

## PART VII: WHAT THIS ARTIFACT IS NOT

This artifact covers transcription choices —
which ARPAbet symbol to give the engine.

It does not cover:

  Physics problems:
    If the engine's formant targets for a
    phoneme are wrong, the phoneme will
    sound wrong for every word that uses it.
    That is a voice_physics_v*.py problem.

  Prosody problems:
    If a word sounds robotic or has wrong
    stress, that is a plan_prosody() or
    emphasis dict problem.

  Ghost problems:
    If the syllable seams are audible as
    clicks or artifacts, that is a v16
    ghost filter or amplitude calibration
    problem. Adjust GHOST_PROFILES in
    tonnetz_engine.py.

  Coarticulation problems:
    If a phoneme sounds right in isolation
    but wrong next to another phoneme,
    that is a physics problem — the
    transition zone or bypass model.

The boundary is:
  Transcription artifact = change the
    phoneme list or syllabification.
  Everything else = change the physics,
    prosody, or ghost parameters.

---

## REVISION HISTORY

  v1 — February 2026
    Initial document.
    Created after "here" sounded like
    "hare" (ERROR 1) and "am" sounded
    like "um" (ERROR 2).
    Near-vowel rule established.
    Schwa trap rule established.
    Verified word list seeded from
    all phrases rendered to date.

  v2 — February 2026
    CONSONANT INVENTORY added (Part II).
    Documents DH/TH pair, H family,
    soft G / hard G rule, nasals,
    approximants.
    H ghost topology incorporated:
    H is the Tonnetz origin. Vowel-initial
    words begin with voiced H automatically
    in v16. Do not add explicit HH.
    ERROR 3 added: G before E/I → JH.
    ERROR 4 added: explicit HH before
    vowel-initial words in v16.
    RULE 6 added: syllabified format
    documentation and examples.
    Tonnetz distances added to all vowel
    entries — the measurable departure
    from H baseline.
    Verified word list updated with
    syllabified forms for all multisyllabic
    words. Affricate words added (v15+).
    Vowel-initial words flagged for v16
    automatic H onset.
    DIAGNOSTIC METHOD updated with v16
    add_ghost=False flag and Step 6
    ghost diagnosis.
    PENDING VERIFICATION updated:
    "already" first syllable AO vs AA
    flagged for perceptual check.
    "-tion", "-ture", "-sion" words
    added to known problem list.
````{"repoID":0,"ref":"","type":"repo-instructions","url":"/Eric-Robert-Lawson/OrganismCore/blob/refs/heads/main/.github/copilot-instructions.md"}
