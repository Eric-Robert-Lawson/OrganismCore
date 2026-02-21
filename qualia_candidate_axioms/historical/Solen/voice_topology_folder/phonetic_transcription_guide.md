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
  2. The systematic transcription errors
     that have already been encountered.
  3. Rules for choosing between similar
     vowels when the right one is not obvious.
  4. A growing word reference for words
     that have been transcribed and verified.

---

## PART I: THE VOWEL INVENTORY

Each entry has:
  - ARPAbet symbol
  - IPA equivalent
  - Keyword (the classic "test word")
  - Formant targets in this engine
  - What it sounds like in isolation
  - Common confusion with other symbols

---

### MONOPHTHONGS — FRONT

**IY** — /iː/ — "b**ee**t"
```
F1: ~300Hz   F2: ~2300Hz
High, front, tense.
Sounds like: "ee" in meet, feet, beat.
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
Before R: coarticulates DOWN toward EH
  → produces "hare" not "here"
  → DO NOT USE IH before R in the same
     syllable when you want the near-vowel
Use for: "is", "it", "this", "with",
  "beginning", "still", "did", "him"
Confused with: IY (tenser, higher)
              AH (lower, more central)
```

**EH** — /ɛ/ — "b**e**d"
```
F1: ~600Hz   F2: ~1750Hz
Mid, front, lax.
Sounds like: "e" in bed, red, said, head.
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
F3 suppression is the defining feature —
  the third formant drops, giving the
  "dark" r-colored quality.
Use for: r-colored vowels in the nucleus:
  "bird", "word", "her", "learn",
  "learning" (ER N IH NG),
  "already" (the R is separate)
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
Distinctively dark/back quality.
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
Use for: "could", "would", "should",
  "good", "put", "full"
Confused with: UW (UW is tenser, darker)
```

**OH** — /oʊ/ (nucleus) — "b**oa**t"
```
F1: ~500Hz   F2: ~1000Hz
Mid, back.
Sounds like: "o" in know, go, so, no.
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
Use for: "already" (AA first syllable),
  "father", "start", "calm", "arm"
Confused with: AE (AE is more front)
              AH (AH is more central/higher)
```

---

### DIPHTHONGS

**AY** — /aɪ/ — "h**igh**"
```
Starts: low-central (~AA region)
Ends:   high-front  (~IH/IY region)
Sounds like: "i" in high, my, time, like.
Use for: "I", "my", "time", "like",
  "still" (no — IH L), "high"
```

**AW** — /aʊ/ — "h**ow**"
```
Starts: low-central
Ends:   high-back (~UH/UW region)
Sounds like: "ow" in how, now, sound,
  out, down.
Use for: "how", "sound", "out", "down",
  "now"
```

**OY** — /ɔɪ/ — "b**oy**"
```
Starts: low-back (~AO region)
Ends:   high-front (~IH/IY region)
Sounds like: "oy" in boy, voice, join.
Use for: "voice" (V OY S), "boy", "join"
```

**OW** — /oʊ/ — "b**oa**t" (diphthong form)
```
Starts: mid-back
Ends:   high-back (~UH region)
Some engines use OH for this.
Use OH unless OW is specifically in
VOWEL_PHONEMES for this engine.
```

**EY** — /eɪ/ — "b**ai**t"
```
Starts: mid-front (~EH region)
Ends:   high-front (~IH/IY region)
Sounds like: "a" in bait, make, same,
  name, take, hate, tate.
Use for: "tate", "hate", "make", "same"
```

---

## PART II: ERRORS ALREADY ENCOUNTERED

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
**Wrong:** `['AE', 'M']` → no wait,
  wrong transcription was `['AH', 'M']`
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

## PART III: DECISION RULES

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

For content words (nouns, verbs, adjectives,
adverbs): use the full stressed form.
For function words (articles, prepositions,
auxiliaries) in running speech: AH reduction
is natural.
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
  Test: does it rhyme with "bit" or "but"?
  "is" = IH Z ✓
  "us" = AH S ✓
  "his" = HH IH Z ✓
  "bus" = B AH S ✓

**AH vs AE:**
  AH = "but" — mouth not very open
  AE = "bat" — mouth more open, jaw lower
  Test: does it rhyme with "but" or "bat"?
  "am" = AE M ✓ (bat, not but)
  "and" = AE N D ✓
  "some" = S AH M ✓ (but, not bat)

**IY vs IH:**
  IY = "beet" — tense, long
  IH = "bit" — lax, short
  Test: does it rhyme with "beet" or "bit"?
  "he" = HH IY ✓
  "him" = HH IH M ✓
  "already" (final syllable) = IY ✓
  "beginning" (all syllables) = IH ✓

**EH vs AE:**
  EH = "bed" — mid front
  AE = "bad" — low front
  Test: does it rhyme with "bed" or "bad"?
  "said" = S EH D ✓
  "sad" = S AE D ✓

**OH vs AO:**
  OH = "boat/know" �� mid back, moves
  AO = "bought/law" — low-mid back, stays
  Test: does it rhyme with "know" or "law"?
  "go" = G OH ✓
  "law" = L AO ✓

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

These words have the AE vowel —
they rhyme with "bat", not "but."
The spelling "a" does not mean AH.

---

## PART IV: VERIFIED WORD REFERENCE

Words that have been transcribed, rendered,
and confirmed to sound correct.
Add to this list every time a word is
verified. Never re-derive a verified word.

---

### VERIFIED — CORRECT

```
the        DH AH
voice      V OY S
was        W AH Z
already    AA L R EH D IY
here       H IY R          (near-vowel fix)
something  S AH M TH IH NG
is         IH Z
beginning  B IH G IH N IH NG
to         T UW
sound      S AW N D
like       L AY K
I          AY
did        D IH D
not        N AH T
know       N OH
could      K UH D
am         AE M             (NOT AH M)
still      S T IH L
learning   L ER N IH NG
how        H AW
near       N IY R           (near-vowel fix)
fear       F IY R           (near-vowel fix)
year       Y IY R           (near-vowel fix)
clear      K L IY R         (near-vowel fix)
who        HH UW
tate       T EY T
hate       HH EY T
what       W AH T
this       DH IH S
```

---

### PENDING VERIFICATION

Words that have been used but not yet
explicitly confirmed to sound correct.
Verify on next render.

```
did        D IH D
could      K UH D
learning   L ER N IH NG  (ER nucleus — check)
beginning  B IH G IH N IH NG  (many IH — check)
```

---

### KNOWN PROBLEM WORDS

Words where the correct transcription
is uncertain or the engine has a known
limitation.

```
"her"   — HH ER or HH IH R?
           ER is likely correct.
           Verify when used.

"were"  — W ER or W IH R?
           W ER is correct.

"there" — DH EH R
           Square vowel. Should be correct.
           Not yet verified.

"where" — W EH R
           Same as there. Not verified.

"they"  — DH EY
           EY diphthong. Not verified.

"their" — DH EH R
           Same as "there" — same phonemes.
           Not verified.
```

---

## PART V: THE DIAGNOSTIC METHOD

When a word sounds wrong, do this:

**Step 1: Isolate the word.**
Render it alone at 4× slow:
```python
render("test_word",
    [('word', ['X', 'X', 'X'])],
    slow_factor=4.0,
    add_breath=False)
```

**Step 2: Identify which phoneme is wrong.**
At 4× slow, each phoneme is 4× longer.
The vowel body — the steady-state middle —
is audible as a distinct sustained tone.
Compare it to the vowel inventory above.

**Step 3: Check the decision rules.**
Before R?  → Rule 1.
Stressed?   → Rule 2.
Similar vowels? → Rule 3.
Misleading spelling? → Rule 4.
Schwa trap? → Rule 5.

**Step 4: Fix the transcription only.**
Do not change voice_physics_v*.py.
Change the phoneme list in
solen_speaks_v*.py.

**Step 5: Add to the verified word list.**
Once the word sounds correct, record it
in Part IV. Do not re-derive it.

---

## PART VI: WHAT THIS ARTIFACT IS NOT

This artifact covers transcription choices —
which ARPAbet symbol to give the engine.

It does not cover:

  Physics problems:
    If the engine's formant targets for a
    phoneme are wrong, the phoneme will
    sound wrong for every word that uses it.
    That is a voice_physics_v*.py problem.
    See the version history comments.

  Prosody problems:
    If a word sounds robotic or has wrong
    stress, that is a plan_prosody() or
    emphasis dict problem.
    See RARFL_v13_trajectory_layer.md.

  Coarticulation problems:
    If a phoneme sounds right in isolation
    but wrong next to another phoneme,
    that is a physics problem — the
    transition zone or bypass model.
    That requires a new fix in the engine.

The boundary is:
  Transcription artifact = change the
    phoneme list in speak.py.
  Everything else = change the physics
    or prosody.

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
