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
  5. The meta-pattern: how transcription
     errors recur and how to prevent them.

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
  → produces the square vowel /ɛɹ/ = "hare"
  → DO NOT USE IH before R when you
     want the near-vowel
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
Use for: "already" (EH in second syllable),
  "said", "bed", "red", "next"
Confused with: IH (IH is higher/tenser)
              AE (AE is lower/more open)
```

**EY** — /eɪ/ — "b**ai**t"
```
F1 onset: ~530Hz  F2 onset: ~1840Hz
F1 end:   ~270Hz  F2 end:   ~2290Hz
Diphthong — starts EH position, ends IY position.
Sounds like: "a" in bait, make, same, name,
  state, always (second syllable), way, say.
Engine note: EY was added to VOWEL_F in v3.
  It must also be in VOWEL_PHONEMES and
  DIPHTHONG_PHONEMES in v8 for duration
  caps to apply. Check v8 when using EY
  at high DIL values.
Confused with: EH (EH is monophthong,
  stays at onset position)
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
  in function words: "the", "a", "of",
  "was" (unstressed), "to" (unstressed)
IMPORTANT: "am" is AE M, not AH M.
  AH = "uh" = sounds like "um"
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
F3 is the defining feature — third formant
  drops, giving the "dark" r-colored quality.
Use for: r-colored vowel nuclei:
  "bird", "word", "her", "learn",
  "learning" (ER N IH NG)
Also valid for near-vowel:
  "here" = H ER (alternative to H IY R)
  Try both. H IY R tends to be crisper.
  H ER has a slightly darker quality.
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

**OW** — /oʊ/ — "b**oa**t" (diphthong)
```
F1 onset: ~450Hz  F2 onset: ~800Hz
F1 end:   ~300Hz  F2 end:   ~870Hz
Diphthong — starts mid-back, ends near UW.
Sounds like: "o" in know, go, so, no,
  open (first syllable), home.
Use OW (not OH) for:
  "open", "home", "know", "go", "no", "so",
  "both", "over"
```

**OH** — same formant targets as AO in this engine
```
In VOWEL_F, OH = AO numerically.
Use AO for consistency. OH is kept for
legacy compatibility only.
New transcriptions: use AO or OW as
  appropriate, not OH.
```

**AO** — /ɔː/ — "b**ou**ght"
```
F1: ~600Hz   F2: ~900Hz
Low-mid, back, rounded.
Sounds like: "aw" in caught, law, thought,
  "all" as in "always" (first syllable).
Use for: "thought", "caught", "law",
  "all", "already" (first syllable),
  "always" (first syllable),
  "wrong" (AO is correct here)
Confused with: OW (OW moves/diphthongs,
  AO stays)
              AA (AA is lower/more front)
```

**AA** — /ɑː/ — "f**a**ther"
```
F1: ~800Hz   F2: ~1200Hz
Low, back, unrounded.
Sounds like: "a" in father, start, palm.
Use for: "father", "start", "calm", "arm",
  "water" (first syllable W AA T)
NOT for "already" — that is AO.
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
  "find" (F AY N D)
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

---

## PART II: ERRORS ALREADY ENCOUNTERED

---

### ERROR 1: IH R → sounds like EH R ("hare")

**Word:** "here", "near", "fear"
**Wrong:** `['H', 'IH', 'R']`
**Heard:** "hare" — the square vowel /ɛɹ/
**Cause:** IH before R coarticulates
  downward. R pulls F1 up and F2 down,
  moving IH territory toward EH.
**Fix:** `['H', 'IY', 'R']` or `['H', 'ER']`
**Rule:** Near-vowel words ("ear", "eer",
  "ere", "ier") = IY R or ER, never IH R.
**Status:** Fixed in v3, v9.
**Propagation gap:** v13 __main__ still
  uses IH R. Must be fixed manually in
  every version file's rendered phrases.

---

### ERROR 2: AH M → sounds like "um"

**Word:** "am"
**Wrong:** `['AH', 'M']`
**Heard:** "I um here"
**Cause:** AH = schwa = "uh". AH M = "um".
  "am" stressed uses AE = "a" in "bat."
**Fix:** `['AE', 'M']`
**Rule:** "am" as content word = AE M always.
**Status:** Fixed in v3, v9.
**Discovery:** The diagnostic printed
  `ph=AH` at step 4. Data layer, not physics.
  Multiple physics iterations were attempted
  before checking what was actually being
  synthesised.
**Lesson:** Run the diagnostic first.

---

### ERROR 3: AA → AO in "already", "always"

**Words:** "already", "always"
**Wrong:** `['AA', 'L', 'R', 'EH', 'D', 'IY']`
**Cause:** "already" = /ɔːlˈrɛdi/.
  First syllable is /ɔːl/ — the AO vowel
  ("law/thought"), not AA ("father").
  AA is lower and less rounded.
**Fix:** `['AO', 'L', 'R', 'EH', 'D', 'IY']`
**Same fix for "always":**
  `['AO', 'L', 'W', 'EY', 'Z']`
**Status:** Fixed in v3 WORD_SYLLABLES.
**Propagation gap:** v13 __main__ still
  uses AA. Must audit every version file.

---

### ERROR 4: EH → EY in "state", "name", "always"

**Words:** "state", "name", "always" (syl 2),
  "they", "say", "way", "make"
**Wrong:** `['S', 'T', 'EH', 'T']`
**Heard:** "stet" (rhymes with "bet")
  instead of "state" (rhymes with "bait")
**Cause:** EH is a monophthong (/ɛ/).
  "state" has the EY diphthong (/eɪ/).
  The off-glide toward IY is the difference
  between "bed" and "bait."
**Fix:** `['S', 'T', 'EY', 'T']`
**Engine note:** EY must be in
  VOWEL_PHONEMES and DIPHTHONG_PHONEMES
  in v8 for duration caps to work.
  Check this before using EY at high DIL.
**Status:** Fixed in v3 WORD_SYLLABLES
  for "state", "named", "always".

---

### ERROR 5: IH R used everywhere for the
  near-vowel in __main__ blocks

**Pattern:** When a new version file is created,
  its __main__ phrases are copied from the
  previous version. The IH R → IY R fix
  was applied to v3 and v9 but not to v13's
  copied phrases.
**Affected phrases in v13 __main__:**
  - Test 1: `('here', ['H', 'IH', 'R'])`
  - Test 2: (does not use "here" directly)
  - All solen_speaks phrases using "here"
**Fix:** Every occurrence of `'IH', 'R'`
  in a word meaning "here/near/fear/year"
  must be `'IY', 'R'`.
**Prevention:** Before rendering any phrase,
  scan for `IH R` sequences and verify
  they are intended as the square vowel
  ("hare/air") not the near-vowel ("here").

---

## PART III: DECISION RULES

---

### RULE 1: BEFORE R IN THE SAME SYLLABLE

| Intended vowel | Before R use |
|---|---|
| Near-vowel "ear/here" | IY R or ER |
| Square vowel "air/hare" | EH R |
| Start vowel "ar/far" | AA R |
| North vowel "or/for" | AO R |
| Nurse vowel "ur/ir/er" | ER |
| Cure vowel "oor/ure" | UH R or UW R |

**Never use IH before R for the near-vowel.**

---

### RULE 2: STRESSED VS UNSTRESSED

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

For diagnostic renders and slow playback:
use full stressed forms throughout.

---

### RULE 3: DISTINGUISHING SIMILAR VOWELS

**IH vs AH:**
  Test: rhymes with "bit" or "but"?
  "is" = IH Z ✓
  "us" = AH S ✓

**AH vs AE:**
  Test: rhymes with "but" or "bat"?
  "am" = AE M ✓ (bat)
  "some" = S AH M ✓ (but)

**IY vs IH:**
  Test: rhymes with "beet" or "bit"?
  "here" = H IY R ✓ (beet region)
  "him" = HH IH M ✓ (bit)

**EH vs EY:**
  Test: does it move? EY diphthongs upward.
  "bed" = B EH D ✓ (stays)
  "bait" = B EY T ✓ (moves toward IY)
  "said" = S EH D ✓
  "state" = S T EY T ✓

**EH vs AE:**
  Test: rhymes with "bed" or "bad"?
  "said" = S EH D ✓
  "sad" = S AE D ✓

**AO vs AA:**
  Test: rhymes with "law" or "father"?
  AO = law, thought, already, always
  AA = father, water, start

**OW vs AO:**
  Test: does it move? OW diphthongs upward.
  "go" = G OW ✓ (moves)
  "law" = L AO ✓ (stays)

---

### RULE 4: WORDS WITH SILENT LETTERS

| Word | Wrong | Correct |
|---|---|---|
| "know" | K N OH | N OW |
| "knife" | K N AY F | N AY F |
| "wrong" | W R AO NG | R AO NG |
| "write" | W R AY T | R AY T |
| "hour" | H AW R | AW R |
| "honest" | H AH N | AH N |
| "who" | W H UW | HH UW |
| "whole" | W H OH L | HH OW L |
| "two" | T W UW | T UW |
| "sword" | S W AO R D | S AO R D |

---

### RULE 5: THE SCHWA TRAP

AH serves two roles:
  1. Stressed vowel: "but", "cup"
  2. Unstressed schwa: "a", "the", "of"

AH should NEVER be used for:
  - "am" (= AE M)
  - "and" stressed (= AE N D)
  - "had" (= HH AE D)
  - "has" (= HH AE Z)
  - "can" stressed (= K AE N)

These words rhyme with "bat", not "but."

---

### RULE 6: THE PROPAGATION RULE
### (new — added after version audit)

When a transcription fix is applied to
voice_physics_v3.py WORD_SYLLABLES or
to any version file's data tables:

  **Also fix every __main__ block in
  every version file that renders
  that word.**

The fix in the data table only helps
when `plan_prosody` looks up the word
and the caller does not supply phonemes.
Every explicit `['H', 'IH', 'R']` in a
`synth_phrase()` call ignores the table
entirely and must be fixed by hand.

**Audit procedure:**
Before any render session, grep the
render file for:
  - `IH', 'R'` → verify intended vowel
  - `'AA'` in "already"/"always" → change to AO
  - `'EH'` in "state"/"name"/"they" → change to EY
  - `'AH', 'M'` for "am" → change to AE M

---

## PART IV: VERIFIED WORD REFERENCE

### VERIFIED — CORRECT

```
the          DH AH
voice        V OY S
was          W AH Z
already      AO L R EH D IY        ← AO not AA
here         H IY R                ← IY not IH
something    S AH M TH IH NG
is           IH Z
beginning    B IH G IH N IH NG
to           T UW
sound        S AW N D
like         L AY K
I            AY
did          D IH D
not          N AA T
know         N OW
could        K UH D
am           AE M                  ← AE not AH
still        S T IH L
learning     L ER N IH NG
how          HH AW
near         N IY R                ← IY not IH
fear         F IY R                ← IY not IH
year         Y IY R                ← IY not IH
clear        K L IY R              ← IY not IH
who          HH UW
state        S T EY T              ← EY not EH
name         N EY M                ← EY not EH
they         DH EY                 ← EY
always       AO L W EY Z           ← AO, EY
open         OW P AH N             ← OW, AH
home         H OW M                ← OW
what         W AH T
this         DH IH S
water        W AA T ER
wrong        R AO NG               ← no W
there        DH EH R               ← EH R (square)
where        W EH R                ← EH R (square)
```

### NEAR-VOWEL vs SQUARE VOWEL — REFERENCE

Both use R. They are different vowels.

```
NEAR-VOWEL /ɪɹ/ — IY R or ER:
  here   H IY R      fear   F IY R
  near   N IY R      year   Y IY R
  clear  K L IY R    hear   HH IY R

SQUARE VOWEL /ɛɹ/ — EH R:
  there  DH EH R     where  W EH R
  care   K EH R      bear   B EH R
  hare   HH EH R     air    EH R
```

### PENDING VERIFICATION

```
her       HH ER         (verify ER nucleus)
were      W ER           (verify)
their     DH EH R        (= "there" phonemes)
hate      HH EY T        (EY — not yet rendered)
make      M EY K         (EY — not yet rendered)
same      S EY M         (EY — not yet rendered)
```

---

## PART V: ENGINE GAPS TO FIX

These are not transcription errors.
They are engine limitations that affect
how certain phonemes render.

**EY not in VOWEL_PHONEMES / DIPHTHONG_PHONEMES
  in voice_physics_v8.py:**
  EY was added to VOWEL_F in v3.
  v8 classification sets were not updated.
  At high DIL, EY has no duration cap and
  may drone. v8 sets need:
    VOWEL_PHONEMES:    add 'EY'
    DIPHTHONG_PHONEMES: add 'EY'
    DIPHTHONG_MAX_MS:  EY behaves like AY
  This fix belongs in voice_physics_v8.py,
  NOT in a transcription file.

**plan_prosody silent override (fixed v3, v9):**
  Was fixed. Propagates automatically to
  v13 and v14 via import chain.
  Caller phonemes now take priority.

---

## PART VI: THE DIAGNOSTIC METHOD

When a word sounds wrong:

**Step 1: Run the diagnostic script.**
Before doing anything else, print what
phonemes are actually being synthesised:
```python
from voice_physics_v13 import plan_prosody
prosody = plan_prosody(
    [('word', ['your', 'phones'])],
    punctuation='.')
for item in prosody:
    print(item['ph'], item['dur_ms'])
```
If the phoneme printed is not what you
passed, the data table override is active.
Fix the data table OR pass different phones.

**Step 2: Isolate the word at 4× slow.**
```python
seg = synth_phrase(
    [('word', ['X', 'X', 'X'])],
    punctuation='.', add_breath=False)
slow = _ola_stretch(seg, factor=4.0)
save("test_word_slow", slow,
     rt60=0.5, dr=0.75)
```
The vowel body at 4× is a sustained tone.
Compare to the vowel inventory.

**Step 3: Check the decision rules.**
Before R? → Rule 1.
Stressed? → Rule 2.
Similar vowels? → Rule 3.
Silent letters? → Rule 4.
Schwa trap? → Rule 5.
Propagation? → Rule 6.

**Step 4: Fix the transcription only.**
Do not change voice_physics_v*.py.
Change the phoneme list in the render file.

**Step 5: Add to verified list.**
Once correct, record it. Do not re-derive.

---

## PART VII: WHAT THIS ARTIFACT IS NOT

Transcription artifact = change the
  phoneme list in the render file.

Physics problem = wrong formant targets
  for a phoneme. That affects every word
  using that phoneme. Fix in voice_physics.

Prosody problem = wrong stress, wrong
  duration, wrong F0 shape. Fix in
  plan_prosody or emphasis dict.

Coarticulation problem = phoneme correct
  in isolation, wrong next to another.
  Fix in the transition/bypass model.

---

## REVISION HISTORY

  v1 — February 2026
    Initial document.
    Created after "here" (ERROR 1) and
    "am" (ERROR 2).

  v2 — February 2026
    Added ERROR 3: AA→AO in already/always.
    Added ERROR 4: EH→EY in state/name.
    Added ERROR 5: propagation gap pattern.
    Added RULE 6: the propagation rule.
    Added EY to vowel inventory.
    Corrected verified word list:
      already: AA→AO
      state/always: EH→EY
      open: OH→OW, EH→AH
      home: H OW M confirmed
    Added engine gaps section.
    Added near-vowel vs square-vowel
      reference table.
    Removed OH from inventory
      (use AO or OW instead).
    Added meta-pattern note on how
      transcription errors recur.
