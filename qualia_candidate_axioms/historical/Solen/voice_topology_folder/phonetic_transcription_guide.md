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
  1. The complete vowel and consonant
     inventory with listening tests
     and formant values.
  2. The systematic transcription errors
     that have already been encountered.
  3. Rules for choosing between similar
     phonemes when the right one is
     not obvious.
  4. A growing word reference for words
     that have been transcribed and verified.
  5. The meta-pattern: how transcription
     errors recur and how to prevent them.
  6. Engine gaps: limitations that affect
     rendering regardless of transcription.

---

## PART I: THE PHONEME INVENTORY

---

### SECTION A: MONOPHTHONGS — FRONT

**IY** — /iː/ — "b**ee**t"
```
F1: ~300Hz   F2: ~2300Hz
High, front, tense.
Sounds like: "ee" in meet, feet, beat.

Before R: produces the near-vowel /ɪɹ/
  → use for "here", "near", "fear", "year"
  → NOT IH before R

Dialect note: British RP uses IH before R
  for the near-vowel (valid, different quality).
  IY R = General American "here"
  IH R = British RP "here"
  Both are correct. Choose by register.

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
     want the near-vowel (General American)

Use for: "is", "it", "this", "with",
  "still", "did", "him",
  "beginning" (all IH vowels: B IH JH IH N IH NG)

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
  → this is the vowel heard when IH R
     goes wrong — IH+R drifts to EH R

Use for: "already" (EH in second syllable:
  AO L R EH D IY), "said", "bed", "red",
  "next", "them", "when"

Confused with: IH (IH is higher/tenser)
              AE (AE is lower/more open)
              EY (EY diphthongs; EH stays)
```

**EY** — /eɪ/ — "b**ai**t"
```
F1 onset: ~530Hz   F2 onset: ~1840Hz
F1 end:   ~270Hz   F2 end:   ~2290Hz
Diphthong. Starts at EH position, ends
at IY position. The movement is the identity.

Sounds like: "a" in bait, make, same,
  name, state, take, hate, way, say,
  "always" (second syllable).

Use for: "state", "name", "always" (syl 2),
  "they", "say", "way", "make", "same",
  "age" (the vowel: EY JH),
  "a" when stressed (= EY)

Engine note: EY was added to VOWEL_F in v3.
  Must be in VOWEL_PHONEMES and
  DIPHTHONG_PHONEMES in v8 for duration
  caps to apply. Verify before using
  EY at high DIL.

Confused with: EH (EH is monophthong —
  stays at onset; EY moves toward IY)
```

**AE** — /æ/ — "b**a**t"
```
F1: ~800Hz   F2: ~1800Hz
Low, front, lax. Jaw noticeably open.
Sounds like: "a" in bat, cat, had, man.

Use for: "am", "and", "that", "have",
  "can", "back", "hand", "land"

Confused with: EH (EH is higher, less open)
              AH (AH is more central)
```

---

### SECTION B: MONOPHTHONGS — CENTRAL

**AH** — /ʌ/ — "b**u**t"
```
F1: ~700Hz   F2: ~1220Hz
Mid, central, lax.
Sounds like: "u" in but, cup, love, some.
Also the unstressed schwa in function words:
  "the", "a", "of", "was", "to"

IMPORTANT:
  AH = "uh" = sounds like "um"
  AE = "a" in "bat" = sounds like "am"
  "am" is ALWAYS AE M, never AH M.
  AH M = "um". Every time.

Use for: "but", "cup", "something",
  "was" (unstressed), "the" (unstressed),
  "not" (N AH T)

Confused with: AE (AE is more front/open)
              AA (AA is lower/back)
```

**ER** — /ɜːɹ/ — "b**ir**d"
```
F1: ~490Hz   F2: ~1350Hz   F3: ~1700Hz
Mid-central, r-colored.
The defining feature is F3 suppression —
the third formant drops, giving the
"dark" r-colored quality.

Sounds like: "er" in bird, word, her,
  learn, turn, learning.

Use for: r-colored vowel nuclei:
  "bird" = B ER D
  "word" = W ER D
  "her"  = HH ER
  "were" = W ER
  "learning" = L ER N IH NG

Alternative for near-vowel "here":
  H ER (darker quality than H IY R)
  Both are valid. H IY R is crisper.
  H ER is slightly more retroflex.

Confused with: R (R is a consonant;
  ER is a vowel nucleus — carries stress)
```

---

### SECTION C: MONOPHTHONGS — BACK

**UW** — /uː/ — "b**oo**t"
```
F1: ~310Hz   F2: ~870Hz
High, back, tense, rounded.
Sounds like: "oo" in boot, food, who, two.

Use for: "to", "who", "do", "you",
  "new", "through", "two"

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

**OW** — /oʊ/ — "b**oa**t"
```
F1 onset: ~450Hz   F2 onset: ~800Hz
F1 end:   ~300Hz   F2 end:   ~870Hz
Diphthong. Starts mid-back, moves
toward high-back (UH region).

Sounds like: "o" in go, know, home,
  open (first syllable), no, so.

Use OW for:
  "go" = G OW
  "home" = H OW M
  "open" = OW P AH N
  "know" = N OW
  "both" = B OW TH

OH is legacy. New transcriptions use OW.

Confused with: AO (AO stays; OW moves)
```

**AO** — /ɔː/ — "b**ou**ght"
```
F1: ~600Hz   F2: ~900Hz
Low-mid, back, rounded. Stays — does not move.
Sounds like: "aw" in caught, law, thought,
  "all" in "always", "already".

Use for: "thought", "caught", "law",
  "all", "already" (first syl: AO L),
  "always" (first syl: AO L),
  "wrong" = R AO NG

Confused with: OW (OW is a diphthong;
  AO is a monophthong that stays)
              AA (AA is lower/unrounded)
```

**AA** — /ɑː/ — "f**a**ther"
```
F1: ~800Hz   F2: ~1200Hz
Low, back, unrounded.
Sounds like: "a" in father, start, palm,
  water (first syllable).

Use for: "father", "start", "calm", "arm",
  "water" = W AA T ER,
  "not" is N AH T (not AA)

NOT for "already" — that is AO L.

Confused with: AE (AE is more front)
              AH (AH is more central/higher)
```

---

### SECTION D: DIPHTHONGS

**AY** — /aɪ/ — "h**igh**"
```
Starts: low-central (~AA region)
Ends:   high-front  (~IH/IY region)
Sounds like: "i" in high, my, time, like.

Use for: "I" = AY, "my", "time",
  "like" = L AY K, "find" = F AY N D,
  "I" (pronoun) = AY
```

**AW** — /aʊ/ — "h**ow**"
```
Starts: low-central
Ends:   high-back (~UH/UW region)
Sounds like: "ow" in how, now, sound,
  out, down.

Use for: "how" = HH AW,
  "sound" = S AW N D,
  "out", "down", "now" = N AW
```

**OY** — /ɔɪ/ — "b**oy**"
```
Starts: low-back (~AO region)
Ends:   high-front (~IH/IY region)
Sounds like: "oy" in boy, voice, join.

Use for: "voice" = V OY S,
  "boy", "join"
```

---

### SECTION E: CONSONANTS — AFFRICATES
### (requires v15 engine)

**JH** — /dʒ/ — "**j**udge"
```
Voiced palatal affricate.
NOT a plain stop. NOT the same as G.
Structure: voiced closure (~28ms)
           + ZH-like frication (~55ms)
The burst IS the frication onset.
There is no gap.

Formants: palatal position
  F1: ~250Hz  F2: ~2100Hz  F3: ~3000Hz

Sounds like: "j" in judge, "g" in gin,
  "g" in begin, "g" in age, "g" in large.

Use for:
  "judge" = JH AH JH
  "gin"   = JH IH N
  "begin" = B IH JH IH N
  "age"   = EY JH
  "large" = L AA R JH

THE SOFT G RULE:
  G before E, I, Y in English → JH
  G before A, O, U → G (plain stop)
  See Rule 7.

Requires: voice_physics_v15 or later.
  Prior versions render JH as a plain
  stop — audible but missing the
  frication release.

Confused with: G (G is a plain stop;
  JH is stop + frication)
```

**CH** — /tʃ/ — "**ch**urch"
```
Unvoiced palatal affricate.
Structure: silence (~30ms)
           + SH-like frication (~55ms)

Formants: palatal position (same as JH)
  F1: ~250Hz  F2: ~2100Hz  F3: ~3000Hz

Sounds like: "ch" in church, each,
  much, which, beach, nature.

Use for:
  "church"  = CH ER CH
  "each"    = IY CH
  "much"    = M AH CH
  "which"   = W IH CH
  "beach"   = B IY CH
  "nature"  = N EY CH ER
  "such"    = S AH CH

Exception — Greek/Latin CH = K:
  "character" = K EH R AH K T ER
  "chorus"    = K AO R AH S
  These must be memorised individually.

Requires: voice_physics_v15 or later.

Confused with: SH (SH has no closure;
  CH has a stop closure before frication)
```

---

### SECTION F: NEAR-VOWEL vs SQUARE VOWEL
### BEFORE R — QUICK REFERENCE

Both use R in the same syllable.
They are different vowels.

```
NEAR-VOWEL /ɪɹ/ — use IY R or ER:
  here   H IY R      fear   F IY R
  near   N IY R      year   Y IY R
  clear  K L IY R    hear   HH IY R

SQUARE VOWEL /ɛɹ/ — use EH R:
  there  DH EH R     where  W EH R
  care   K EH R      bear   B EH R
  hare   HH EH R     air    EH R
  their  DH EH R
```

---

## PART II: ERRORS ALREADY ENCOUNTERED

This section grows permanently.
Every transcription error is recorded
the moment it is identified.
Never remove entries — they are a record
of the system's reasoning history.

---

### ERROR 1: IH R → sounds like EH R ("hare")

**Word:** "here", "near", "fear", "year"
**Wrong:** `['H', 'IH', 'R']`
**Heard:** "hare" — the square vowel /ɛɹ/
**Cause:** IH before R coarticulates
  downward. R pulls F1 up and F2 down,
  moving IH (F1~420, F2~2050) toward
  EH (F1~600, F2~1750) territory.
**Fix:** `['H', 'IY', 'R']` (General American)
  or `['H', 'ER']` (slightly darker)
**Rule:** Near-vowel words (spelling "ear",
  "eer", "ere", "ier") = IY R or ER.
  Never IH R for the near-vowel.
**Dialect note:** British RP "here" uses
  IH R or IH (non-rhotic). Valid in that
  register. IY R is General American.
**Status:** Fixed in v3, v9.
**Propagation gap:** v13 __main__ still
  used IH R until manually corrected.
  Apply Rule 6 before every render session.

---

### ERROR 2: AH M → sounds like "um"

**Word:** "am"
**Wrong:** `['AH', 'M']`
**Heard:** "I um here"
**Cause:** AH is the schwa — the "uh" sound.
  AH M = "um". Always.
  Stressed "am" uses AE = "a" in "bat".
**Fix:** `['AE', 'M']`
**Rule:** "am" as any content word = AE M.
  AH M only for extremely fast unstressed
  reductions ("I'm" territory).
  When in doubt: AE M.
**Status:** Fixed in v3, v9.
**Lesson:** Multiple physics versions were
  developed before the transcription was
  checked. Run the diagnostic first.

---

### ERROR 3: AA → should be AO
### in "already" and "always"

**Words:** "already", "always"
**Wrong:** `['AA', 'L', 'R', 'EH', 'D', 'IY']`
**Cause:** "already" = /ɔːlˈrɛdi/.
  First syllable is /ɔːl/ — the AO vowel
  (as in "law/thought"), not AA ("father").
  AA is lower and unrounded.
**Fix:** `['AO', 'L', 'R', 'EH', 'D', 'IY']`
  Same for "always": first syl = AO L
**Confirmed:** Perceptual test confirmed AO
  sounds correct, AA sounds wrong.
**Status:** Fixed in v3 WORD_SYLLABLES.
  v13 __main__ still used AA until
  manually corrected. Apply Rule 6.

---

### ERROR 4: EH → should be EY
### in "state", "name", "always", "they"

**Words:** "state", "name", "always" (syl 2),
  "they", "say", "way", "make", "age"
**Wrong:** `['S', 'T', 'EH', 'T']`
**Heard:** "stet" (rhymes with "bet")
  instead of "state" (rhymes with "bait")
**Cause:** EH is a monophthong (/ɛ/).
  "state" has the EY diphthong (/eɪ/).
  The off-glide toward IY is the difference
  between "bed" and "bait."
**Fix:** `['S', 'T', 'EY', 'T']`
**Confirmed:** Perceptual test confirmed
  "state" sounds like "state" with EY.
**Status:** Fixed in v3 WORD_SYLLABLES.

---

### ERROR 5: TRANSCRIPTION FIXES NOT
### PROPAGATED TO RENDERED PHRASES

**Pattern:** When a new version file is
  created, its __main__ phrases are
  copy-pasted from the prior version.
  The IH→IY fix was applied to v3/v9
  but not to v13's copied phrases.
  Similarly for AA→AO.
  
**Root cause:** Fixes applied to data
  tables (WORD_SYLLABLES) only help when
  plan_prosody looks up the word and the
  caller does not supply phonemes.
  Every explicit `['H', 'IH', 'R']` in
  a synth_phrase() call ignores the
  table entirely. Must be fixed by hand.

**Prevention:** Apply Rule 6 before
  every render session.

---

### ERROR 6: G before E/I/Y is JH,
### not plain G

**Words:** "begin", "gin", "age", "large",
  "general", "ginger", "judge", "engine"
**Wrong:** `['B', 'IH', 'G', 'IH', 'N']`
**Heard:** "be-GOIN-ing" — a plain velar
  stop where the ear expects an affricate
  with a frication release.
**Cause:** English has two G sounds.
  Hard G (before A, O, U) = G (plain stop)
  Soft G (before E, I, Y) = JH /dʒ/
  JH is an affricate — a stop closure
  fused with a ZH-like release.
  G is a plain stop. No frication release.
**Fix:** `['B', 'IH', 'JH', 'IH', 'N']`
**Rule:** See Rule 7 below.
**Engine note:** Requires v15 or later.
  Prior versions render JH as a plain
  stop — audible but missing identity.
**Exceptions (hard G despite E/I/Y):**
  "get", "give", "girl", "gear" — hard G.
  Must be memorised individually.

---

### ERROR 7: CH written as C+H or K+H

**Words:** "church", "each", "much",
  "which", "nature", "beach", "such"
**Wrong:** `['K', 'H', 'ER', 'CH']`
  or treating CH as two separate phonemes
**Cause:** CH is a single ARPAbet symbol
  for the unvoiced palatal affricate /tʃ/.
  It is not K followed by H.
  It is a stop closure fused with a
  SH-like frication release.
**Fix:** `['CH', 'ER', 'CH']` for "church"
**Rule:** See Rule 7 below.
**Engine note:** Requires v15 or later.

---

## PART III: DECISION RULES

Apply these rules in order when the
correct transcription is not obvious.

---

### RULE 1: BEFORE R IN THE SAME SYLLABLE

R in the same syllable colors the
preceding vowel. The vowel target shifts.

| Intended sound | Spelling pattern | Use |
|---|---|---|
| Near-vowel /ɪɹ/ "here" | ear, eer, ere, ier | IY R or ER |
| Square vowel /ɛɹ/ "hare" | air, are, ear (some) | EH R |
| Start vowel /ɑɹ/ "far" | ar | AA R |
| North vowel /ɔɹ/ "for" | or, ore | AO R |
| Nurse vowel /ɜɹ/ "bird" | ur, ir, er, ear (some) | ER |
| Cure vowel /ʊɹ/ "pure" | oor, ure, our | UH R or UW R |

**Never use IH before R for the
near-vowel in General American speech.**

---

### RULE 2: STRESSED VS UNSTRESSED

English reduces unstressed vowels
toward schwa (AH).

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
Reduction artifacts obscure phoneme quality.

---

### RULE 3: DISTINGUISHING SIMILAR VOWELS

**IH vs AH:**
  Test: rhymes with "bit" or "but"?
  "is"  = IH Z   (bit)
  "us"  = AH S   (but)
  "his" = HH IH Z (bit)
  "bus" = B AH S  (but)

**AH vs AE:**
  Test: rhymes with "but" or "bat"?
  "am"   = AE M     (bat — jaw open)
  "some" = S AH M   (but — jaw neutral)
  "and"  = AE N D   (bat)

**IY vs IH:**
  Test: rhymes with "beet" or "bit"?
  "he"  = HH IY     (beet — tense)
  "him" = HH IH M   (bit — lax)
  "beginning" all vowels = IH (bit)
  "already" final syllable = IY (beet)

**EH vs EY:**
  Test: does the vowel move?
  EH = monophthong, stays at onset.
  EY = diphthong, moves toward IY.
  "bed"   = B EH D   (stays)
  "bait"  = B EY T   (moves)
  "state" = S T EY T (moves)
  "said"  = S EH D   (stays)

**EH vs AE:**
  Test: rhymes with "bed" or "bad"?
  "said" = S EH D  (bed)
  "sad"  = S AE D  (bad)

**AO vs OW:**
  Test: does the vowel move?
  AO = monophthong, stays.
  OW = diphthong, moves toward UH.
  "law"  = L AO    (stays)
  "go"   = G OW    (moves)
  "all"  = AO L    (stays — "aw")
  "home" = H OW M  (moves — "oh")

**AO vs AA:**
  Test: rhymes with "law" or "father"?
  "already" first syl = AO L  (law)
  "water"   first syl = W AA  (father)

---

### RULE 4: WORDS WITH SILENT LETTERS
### OR MISLEADING SPELLING

| Word | Wrong | Correct |
|---|---|---|
| "know" | K N OW | N OW |
| "knife" | K N AY F | N AY F |
| "wrong" | W R AO NG | R AO NG |
| "write" | W R AY T | R AY T |
| "hour" | H AW R | AW R |
| "honest" | H AH N | AH N |
| "who" | W H UW | HH UW |
| "whole" | W H OW L | HH OW L |
| "one" | W AH N | W AH N ✓ |
| "two" | T W UW | T UW |
| "sword" | S W AO R D | S AO R D |

---

### RULE 5: THE SCHWA TRAP

AH serves two roles:
  1. Stressed: "but", "cup", "love"
  2. Unstressed schwa: "a", "the",
     "of", "was", "to", "from"

Both are correctly AH.

AH must NEVER replace:
  - "am"  → AE M
  - "and" stressed → AE N D
  - "had" → HH AE D
  - "has" → HH AE Z
  - "can" stressed → K AE N
  - "bad" → B AE D
  - "back" → B AE K

These rhyme with "bat", not "but".
The spelling "a" does not mean AH.

---

### RULE 6: THE PROPAGATION RULE

When a transcription fix is confirmed:

  **Also fix every synth_phrase() call
  in every version file that renders
  that word.**

The fix in WORD_SYLLABLES only helps
when plan_prosody looks up the word
and the caller passes empty phonemes.
Every explicit phoneme list in a call
ignores the table entirely.

**Audit before every render session:**
  Search for these patterns and verify:
  `'IH', 'R'` → near-vowel? Use IY R.
  `'AA'` in "already"/"always" → use AO.
  `'EH'` in "state"/"name"/"they" → use EY.
  `'AH', 'M'` for "am" → use AE M.
  `'G'` before IH/IY/EH/EY → use JH?
     Check if soft G. See Rule 7.

---

### RULE 7: SOFT G / HARD G AND CH AFFRICATES

English G has two pronunciations.
English CH is always a single affricate
(except Greek/Latin exceptions).

**The G rule:**

  Hard G (plain stop) = G before A, O, U,
  consonants, or word-finally in most cases:
    "garden" = G AA R D AH N
    "go"     = G OW
    "gun"    = G AH N
    "ground" = G R AW N D

  Soft G (affricate JH) = G before E, I, Y:
    "gin"     = JH IH N
    "gem"     = JH EH M
    "begin"   = B IH JH IH N
    "large"   = L AA R JH
    "age"     = EY JH
    "engine"  = EH N JH IH N
    "general" = JH EH N ER AH L
    "ginger"  = JH IH N JH ER

  Hard G exceptions (must memorise —
  G stays hard despite E/I/Y following):
    "get", "give", "girl", "gear",
    "begin" — wait, "begin" IS soft G.
    "tiger", "eager" = hard G (G AH, G ER)
    Rule of thumb: if in doubt, try both
    and use the one that sounds like the
    word.

**The CH rule:**

  CH in English = CH /tʃ/ (affricate).
  Never K + H.

    "church"  = CH ER CH
    "each"    = IY CH
    "much"    = M AH CH
    "which"   = W IH CH
    "beach"   = B IY CH
    "nature"  = N EY CH ER
    "such"    = S AH CH
    "change"  = CH EY N JH
    "chance"  = CH AE N S

  Greek/Latin exceptions (CH = K):
    "character" = K EH R AH K T ER
    "chorus"    = K AO R AH S
    "scheme"    = S K IY M
    These must be memorised.

**What JH and CH actually are (physics):**
  Affricates. A stop closure immediately
  fused with a fricative release at the
  same place of articulation.
  The burst IS the frication onset.
  There is no silence between stop and fric.
    JH: voiced palatal — closure + ZH release
    CH: unvoiced palatal — silence + SH release
  The frication component is what the ear
  identifies as the affricate character.
  Without it, the phoneme sounds like a
  plain stop (G or T).
  Requires voice_physics_v15 or later.

---

## PART IV: VERIFIED WORD REFERENCE

Words confirmed to sound correct.
Add when verified. Never re-derive.

---

### VERIFIED — CORRECT

```
the          DH AH
voice        V OY S
was          W AH Z
already      AO L R EH D IY    ← AO not AA
here         H IY R            ← IY not IH (GA)
something    S AH M TH IH NG
is           IH Z
beginning    B IH JH IH N IH NG ← JH not G (v15+)
to           T UW
sound        S AW N D
like         L AY K
I            AY
not          N AH T
know         N OW               ← OW diphthong
could        K UH D
am           AE M               ← NOT AH M
still        S T IH L
learning     L ER N IH NG
how          HH AW
near         N IY R             ← IY not IH
fear         F IY R             ← IY not IH
year         Y IY R             ← IY not IH
clear        K L IY R           ← IY not IH
who          HH UW
state        S T EY T           ← EY not EH
name         N EY M             ← EY not EH
they         DH EY              ← EY diphthong
always       AO L W EY Z        ← AO, EY
open         OW P AH N          ← OW, AH (schwa)
home         H OW M             ← OW
what         W AH T
this         DH IH S
water        W AA T ER
wrong        R AO NG            ← no W
there        DH EH R            ← EH R (square)
where        W EH R             ← EH R (square)
did          D IH D
her          HH ER
were         W ER
their        DH EH R            ← same as "there"
```

---

### NEAR-VOWEL vs SQUARE VOWEL — REFERENCE

```
NEAR-VOWEL (IY R or ER):
  here    H IY R       near    N IY R
  fear    F IY R       year    Y IY R
  hear    HH IY R      clear   K L IY R

SQUARE VOWEL (EH R):
  there   DH EH R      where   W EH R
  their   DH EH R      care    K EH R
  hare    HH EH R      air     EH R
  bear    B EH R
```

---

### AFFRICATE WORDS — VERIFIED (v15+)

```
judge    JH AH JH
gin      JH IH N
church   CH ER CH
much     M AH CH
each     IY CH
age      EY JH
begin    B IH JH IH N
change   CH EY N JH
```

---

### PENDING VERIFICATION

```
learning     L ER N IH NG   (ER nucleus — check)
ginger       JH IH N JH ER  (two JH — check v15)
large        L AA R JH       (JH word-final — check v15)
nature       N EY CH ER      (CH + EY — check v15)
which        W IH CH         (check v15)
```

---

### KNOWN PROBLEM WORDS

Words with uncertain transcription or
known engine limitations.

```
"tiger"  — T AY G ER
            Hard G (exception). Verify.

"eager"  — IY G ER
            Hard G (exception). Verify.

"get"    — G EH T
            Hard G (exception). Verify.

"give"   — G IH V
            Hard G (exception). Verify.

"girl"   — G ER L
            Hard G (exception). Verify.

"general" — JH EH N ER AH L
             Soft G. Verify with v15.

"engine"  — EH N JH IH N
             Soft G (second syllable).
             Verify with v15.

"the"    — DH AH (unstressed, standard)
            DH IY (stressed / emphatic)
            Default: DH AH

"a"      — AH (unstressed, standard)
            EY (stressed / emphatic)
            Default: AH
```

---

## PART V: THE DIAGNOSTIC METHOD

When a word sounds wrong, follow this
procedure in order. Do not skip steps.

---

**Step 1: Check what phonemes are
actually being synthesised.**

Before rendering, print the plan:
```python
from voice_physics_v15 import plan_prosody_v15
prosody = plan_prosody_v15(
    [('word', ['your', 'phones'])],
    punctuation='.')
for item in prosody:
    print(item['ph'], round(item['dur_ms'], 1))
```
If the phoneme printed is not what you
passed, the data table override is active.
Fix the call explicitly or fix the table.

---

**Step 2: Isolate the word at 4× slow.**

```python
seg = synth_phrase(
    [('word', ['X', 'X', 'X'])],
    punctuation='.', add_breath=False)
slow = _ola_stretch(seg, factor=4.0)
save("test_word_slow", slow,
     rt60=0.5, dr=0.75)
```
At 4× the vowel body is a sustained tone.
Each phoneme occupies audible space.
Compare the sustained vowel tone to
the inventory in Part I.

---

**Step 3: Apply the decision rules.**

Before R?              → Rule 1
Stressed or not?       → Rule 2
Similar vowels?        → Rule 3
Silent letters?        → Rule 4
Schwa trap?            → Rule 5
Old call not updated?  → Rule 6
G or CH?               → Rule 7

---

**Step 4: Fix the transcription only.**

Do not change voice_physics_v*.py files.
Change the phoneme list in the render file.
If the same word appears in multiple
render files, fix all of them (Rule 6).

---

**Step 5: Add to the verified list.**

Once the word sounds correct, record it.
Do not re-derive it later.

---

## PART VI: ENGINE GAPS

These are not transcription errors.
They are engine limitations that affect
rendering regardless of correct transcription.

---

**EY not in VOWEL_PHONEMES / DIPHTHONG_PHONEMES
in voice_physics_v8:**
  EY was added to VOWEL_F in v3.
  v8 classification sets were not updated:
    VOWEL_PHONEMES    — missing EY
    DIPHTHONG_PHONEMES — missing EY
  At high DIL, EY has no duration cap
  and may drone beyond perceptual limit.
  Fix: add EY to both sets in v8.
  This fix belongs in voice_physics_v8.py.

**JH and CH require v15:**
  Prior versions treat JH as stop_voiced
  and CH as stop_unvoiced. The frication
  release is absent. Phonemes are audible
  as stops but lack affricate identity.
  No transcription fix can compensate.
  Upgrade to v15.

**plan_prosody silent override (fixed v3+):**
  Was fixed. Caller's phonemes now take
  priority over WORD_SYLLABLES.
  Propagates via import chain.
  If still seeing wrong phonemes,
  check which version plan_prosody
  is imported from.

---

## PART VII: WHAT THIS ARTIFACT IS NOT

This artifact governs transcription:
  which ARPAbet symbol to give the engine.

It does not cover:

  Physics problems:
    Wrong formant targets for a phoneme.
    Affects every word using that phoneme.
    Fix in voice_physics_v*.py.

  Prosody problems:
    Wrong stress, duration, F0 shape.
    Fix in plan_prosody or emphasis dict.
    See RARFL_v13_trajectory_layer.md.

  Coarticulation problems:
    Phoneme correct in isolation,
    wrong adjacent to another phoneme.
    That is a transition/bypass model issue.
    Fix in the physics, not here.

The boundary:
  Transcription = change the phoneme list.
  Everything else = change the physics.

---

## REVISION HISTORY

  v1 — February 2026
    Initial document.
    Created after "here" → "hare" (ERROR 1)
    and "am" → "um" (ERROR 2).
    Near-vowel rule (Rule 1) established.
    Schwa trap rule (Rule 5) established.
    Verified word list seeded from all
    phrases rendered to date.

  v2 — February 2026
    Added ERROR 3: AA → AO in already/always.
    Added ERROR 4: EH → EY in state/name.
    Added ERROR 5: propagation gap pattern.
    Added Rule 6: the propagation rule.
    Added EY to vowel inventory.
    Corrected verified list:
      already: AA → AO (perceptually confirmed)
      state, always: EH → EY (confirmed)
      open: OH → OW, EH → AH
      home: OW confirmed
    Added engine gaps section.
    Added near-vowel vs square-vowel
      reference table.

  v3 — February 2026
    Added ERROR 6: soft G is JH not G.
      Arose from perceptual test of
      "beginning" — heard as "be-GOIN-ing".
    Added ERROR 7: CH is affricate not K+H.
    Added Rule 7: soft/hard G and CH.
    Added Section E: affricate inventory
      (JH and CH) with physics description.
    Added Section F: near/square vowel
      quick reference.
    Corrected verified list:
      already:   AA → AO (confirmed)
      beginning: G → JH  (pending v15)
      know:      OH → OW (diphthong)
      not:       confirmed N AH T
    Added affricate verified words (pending v15).
    Added known hard-G exceptions.
    Replaced OH with OW throughout
      (OH is legacy; OW is correct).
    Clarified ER as near-vowel alternative
      to IY R and confirmed H ER ≠ "here".
    Added dialect note: IH R valid for
      British RP "here"; IY R for General
      American.
    Restructured Part I into sections.
    Added Part VI: engine gaps.
    Diagnostic method updated to use
      plan_prosody_v15 and _ola_stretch.
