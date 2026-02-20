# TRANSITION TIMING AND VOICED SIBILANT CONTRAST
## A Reasoning Artifact on Coarticulation Speed,
## Dilation Scaling, and Z/S Perceptual Blur
## February 2026

---

## THE OBSERVATIONS

Phrase heard: "the voice was always here."
Phrase produced by synthesis:
"Yea Voisss wazs already (brief 'teh' sound) here"

Four specific perceptual events:

```
1. "Voisss"   — S and Z blurred into one long sibilant
2. "wazs"     — Z had a sibilant tail into the next vowel
3. "voi-ce"   — OY→S sounded like two syllables
4. "teh here" — IY→H produced an audible intermediate vowel
```

These are precise observations.
Each maps to a specific mechanism.

---

## PART 1: THREE OF FOUR ARE THE SAME PROBLEM

Events 2, 3, and 4 share one root cause:

**Coarticulation transition time
scales with dilation.**

It should not.

### What is happening:

In `build_trajectories`, the transition
zone (onset/offset) is computed as:

```python
n_on  = int(cf * n_s)   # cf = coart_frac
n_off = int(cf * n_s)
```

`n_s` is the phoneme duration in samples.
`n_s = dur_ms / 1000 * sr`
`dur_ms = PHON_DUR_BASE[ph] * DUR_SCALE[stress] * dil`

So at DIL=6.0:
```
PHON_DUR_BASE['S']  = 100ms
DUR_SCALE[stress=2] = 1.40
dur_ms = 100 * 1.40 * 6.0 = 840ms

n_s    = 840ms * 44100 = 37044 samples
cf(S)  = 0.10
n_on   = int(0.10 * 37044) = 3704 samples
       = 84ms of transition zone
```

At normal speech (DIL=1.0):
```
dur_ms = 100 * 1.40 * 1.0 = 140ms
n_s    = 6174 samples
n_on   = int(0.10 * 6174) = 617 samples
       = 14ms of transition zone
```

The transition zone is 84ms at DIL=6.
It should be ~14ms regardless of DIL.
At 6× dilation, transitions are 6× too long.
The intermediate formant position
is audible for 84ms instead of 14ms.
That is a long time.
The ear hears it as a separate event.

### Specific events explained:

**"voi-ce" (OY → S):**
OY is a diphthong ending near IY position.
IY has F2=2290Hz, tongue high and front.
S has its resonator at 8800Hz.
The transition zone from IY toward S
is ~80ms at DIL=6.
During that 80ms the tract is at
an intermediate position —
somewhere between IY and S.
IY-ish tract + S-onset frication
= sounds like a palatal consonant,
like "y" or an extra syllable.
The ear parses it as "voi-ce" not "vois."

**"wazs" (Z → W):**
Z has a bypass release envelope of 8ms.
That is fixed — not dilation-scaled.
But the TRACT is still moving
during n_off = 0.15 * n_s of Z.
At DIL=6, n_off(Z) ≈ 0.15 * 760ms
= 114ms of Z's tract moving toward W.
During those 114ms, Z bypass is fading.
But the tract is still in a configuration
that resonates fricative-adjacent.
The residual frication + slow tract
= sounds like an extra "s" at the end.

**"teh here" (IY → H):**
IY ends 'already' (final phoneme: IY).
H begins 'here'.
IY tract: F1=270Hz, F2=2290Hz.
H tract: takes target from next vowel IH.
IH target: F1=390Hz, F2=1990Hz.
The rest between words is:
`base_rest_ms * bond * dil`
`= 85 * 0.60 * 6 = 306ms`

During the rest, the tract continues
whatever trajectory it was on.
It does not reset.
After IY, the tract is moving
through EH territory (F1~530, F2~1840)
on its way toward IH.
The H source activates on a
mid-front tract position.
H through mid-front formants
= something like "heh" or "teh."
The ear hears it as an extra syllable
before "here."

---

## PART 2: THE FIX FOR TRANSITIONS

The coarticulation fraction `cf`
should produce a transition that is
**fixed in absolute milliseconds**,
not proportional to phoneme duration.

```
TARGET TRANSITION TIMES (absolute):

Approximants (L, R, W, Y):  25-35ms
Nasals (M, N, NG):           20-30ms
Fricatives (S, Z, SH, etc):  12-18ms
Stops (P, B, T, D, K, G):   8-15ms
Vowels:                      20-30ms
H:                           10-15ms
DH:                          20-28ms
```

These are the times the ear needs
to perceive a smooth transition.
Not so short that transitions pop.
Not so long that they become audible
as separate phonetic events.

At DIL=6, these times should be the same.
The phoneme BODY extends with dilation.
The transition boundaries do not.

Implementation:

```python
# In ph_spec_prosody:
# Compute absolute transition samples
# from milliseconds, not from cf*n_s

TRANS_MS = {
    'H':   12, 'DH':  22,
    'L':   28, 'R':   28,
    'W':   28, 'Y':   28,
    'P':   10, 'B':   10,
    'T':   10, 'D':   10,
    'K':   12, 'G':   12,
    'S':   14, 'Z':   16,
    'SH':  16, 'ZH':  16,
    'M':   24, 'N':   24,
    'NG':  24,
}
DEFAULT_TRANS_MS = 22  # vowels

def trans_samples(ph, sr):
    ms = TRANS_MS.get(ph, DEFAULT_TRANS_MS)
    return int(ms / 1000.0 * sr)
```

Then in `build_trajectories`:

```python
# Instead of:
n_on  = int(cf * n_s)
n_off = int(cf * n_s)

# Use:
n_on  = min(trans_samples(ph, sr),
            n_s // 3)
n_off = min(trans_samples(ph, sr),
            n_s // 3)
n_mid = n_s - n_on - n_off
```

The phoneme body (n_mid) grows with DIL.
The transition zones stay fixed.
The intermediate positions are
no longer audible as separate events.

---

## PART 3: THE BYPASS RELEASE ALSO NEEDS FIXING

The bypass envelope in `make_sibilance_bypass`
has a fixed 8ms release:

```python
rel = int(0.008*sr)   # 8ms — fixed
```

This is correct — it does not scale with DIL.
But it creates a mismatch:

At DIL=6, the Z phoneme body is ~760ms.
The bypass release is 8ms.
But the TRACT is still moving for
~114ms after the bypass ends (n_off zone).

The bypass ends cleanly in 8ms.
But the tract is still radiating
a Z-adjacent configuration for 114ms.

Fix: The bypass release should extend
to cover the full n_off zone.
When the next phoneme is a voiced non-fricative,
the bypass fades over the entire
transition zone, not just 8ms.

```python
# Context-aware bypass release:
# If next_ph is a vowel or approximant,
# fade bypass over full n_off samples.
# If next_ph is another fricative,
# keep brief 8ms release
# (the sibilances connect).
```

---

## PART 4: THE Z/S BLUR

The first observation: "Voisss."
S and Z blurred into one long sibilant.
This is a different problem from transition timing.

### What is happening:

'voice' → V OY **S**
'was'   → W AH **Z**

S ends 'voice'. Z ends 'was'.
Adjacent across a word boundary.

S is unvoiced sibilant. Bypass at 8800Hz.
Z is voiced sibilant. Bypass at 8000Hz.

The difference:
  S: sibilance only. No voice.
  Z: sibilance PLUS voiced buzz underneath.

In the synthesis:
  S bypass is correct — resonator at 8800Hz.
  Z bypass is correct — resonator at 8000Hz.
  But Z's voiced component (tract)
  is at `VOICED_TRACT_FRACTION = 0.75`
  of `voiced_full`.

The problem:
  The `voiced_full` signal during Z
  is generated continuously across
  the entire phrase.
  At the S → Z boundary
  (word boundary: 'voice' | 'was')
  there is a syntactic rest:
  `base_rest_ms * bond * dil`
  `= 85 * 0.65 * 6 = 331ms`

  During the rest, no voiced source.
  The voiced component of Z
  starts only after the rest.
  But 331ms is long.
  And the bypass is running
  for the full Z duration before
  and after the rest.

  No — wait. Let me re-read.

  The rest comes AFTER the last phoneme
  of the word ('voice' ends with S).
  Then the rest. Then 'was' begins.
  'was' = W AH Z.
  The Z is at the END of 'was',
  not adjacent to S directly.

  The phrase is:
  V OY S [rest] W AH Z [rest] AA L R EH D IY

  S and Z are NOT adjacent.
  There is W AH between them.

  So "Voisss" is not S+Z blurring
  across a word boundary.

  It is something else.

  Re-reading: "the voice was always here."
  The actual phrase: V OY S | W AH Z | AA L W EH Z

  There are TWO Z phonemes:
    Z in 'was': W AH **Z**
    Z in 'always': AA L W EH **Z**

  And 'always' also ends in Z.

  But 'voice' ends in S.
  'was' ends in Z.
  'always' ends in Z.

  S → [rest] → W → AH → Z → [rest] → AA → L → W → EH → Z

  The "Voisss" sound is likely:
  The S of 'voice' is too long.
  At DIL=6, S duration:
  `PHON_DUR_BASE['S'] * DUR_SCALE[stress=2] * 6`
  `= 100 * 1.40 * 6 = 840ms`

  840ms of S.
  That is nearly a full second of sibilance.
  At normal speech it would be 140ms.
  The ear hears 840ms of S as "sss."

  The VOICED component of Z in 'was'
  is being masked by:
  1. The 840ms S that just finished
  2. The rest between 'voice' and 'was'
  3. The W onset of 'was'

  By the time Z arrives, the ear
  has been hearing sibilance for
  so long that the Z also sounds
  like just more sibilance.

  The Z voice component needs to be
  more prominent relative to its sibilance.
  And the S duration is simply too long.

### The fix for S duration:

Fricative durations should scale with DIL
but with a cap.
A 840ms S is not a slow S.
It is a broken S.
There is a perceptual maximum duration
for any fricative above which it sounds
unnatural — like a steam leak.

```python
# In plan_prosody:
# Cap fricative durations

FRIC_MAX_MS = {
    'S':  180, 'Z':  180,
    'SH': 200, 'ZH': 200,
    'F':  160, 'V':  160,
    'TH': 170, 'DH': 170,
}

# After computing dur_ms:
if ph in FRIC_MAX_MS:
    dur_ms = min(dur_ms,
                 FRIC_MAX_MS[ph])
```

### The fix for Z voiced contrast:

Z's voice component needs to be
clearly distinct from S.
Currently:
  Z bypass: resonator at 8000Hz, gain calibrated
  Z voice: voiced_full * 0.75 through tract

The gap between S (no voice) and Z (some voice)
is the perceptual Z/S contrast.
To make that gap larger:

1. Increase Z's voiced tract fraction: 0.75 → 0.85
2. Raise Z's VOICED_TRACT_FRACTION specifically
   (not all voiced fricatives — just Z)
3. Ensure that at the S→Z boundary,
   the voiced component of Z starts
   at full strength, not faded in.

```python
# Z-specific voiced fraction
Z_VOICED_TRACT = 0.88
# (vs global VOICED_TRACT_FRACTION = 0.75)
```

---

## PART 5: THE REST SCALING PROBLEM

From Part 3 analysis, the rest between words
is also scaling with DIL:

```python
rest_ms = base_rest_ms * bond * dil
        = 85 * 0.65 * 6.0
        = 331ms
```

A 331ms rest between 'voice' and 'was' is long.
At normal speech it would be 55ms.
The rest IS part of the meaning.
But 331ms is so long that:
  - The tract resets during the rest
  - The H onset of 'here' picks up
    at an arbitrary position
  - The intermediate position sounds
    like "teh"

Rests should also have a cap.
A long rest is a pause — semantically meaningful.
But during a slow/dilated delivery,
the rests should be proportionally shorter.

```python
REST_MAX_MS = 280.0  # never longer than this
rest_ms = min(
    base_rest_ms * bond * dil,
    REST_MAX_MS
)
```

---

## PART 6: THE TRACT RESET DURING RESTS

Related to Part 5.

During a rest (`breath_rest`),
the tract is not running.
The source is silence (or breath noise).
The formant trajectories are not computed.

When the next phoneme begins,
`build_trajectories` picks up from
the LAST computed position of the
previous phoneme.

This is correct for short rests.
For rests of 300ms, the physical
vocal tract would have moved
toward a neutral position.
The synthesis does not do this.
It picks up exactly where it left off.

If the last phoneme before the rest
was IY (high front, F2=2290Hz),
and the next phoneme after the rest
is H-IH (mid-front),
the tract starts H from IY position.
That is a long way to travel.
The H onset sounds like a transition
from IY toward IH — which sounds like
a vowel. "teh."

Fix: During rests longer than ~100ms,
gradually move the tract toward a
neutral schwa position (F1≈500, F2≈1500).
When the next phoneme begins,
coarticulate from near-neutral
rather than from the previous extreme.

```python
# Neutral position for inter-word reset
NEUTRAL_F = [500, 1500, 2500, 3500]
NEUTRAL_B = [120, 150,  250,  350]

# During long rests, blend F_current
# toward NEUTRAL_F over the rest duration.
# The longer the rest, the more
# the tract approaches neutral.
```

---

## PART 7: SUMMARY OF FIXES

Four perceptual events.
Four root causes.
Three fixes address them all.

```
EVENT                  ROOT CAUSE            FIX
─────────────────────────────────────────────────────
"Voisss"               S duration 840ms      Cap fricative dur
                       Z voicing buried      Z_VOICED_TRACT=0.88

"wazs"                 Bypass release vs     Context-aware
                       slow tract n_off      bypass release

"voi-ce"               Transition 80ms       Fixed-ms transitions
                       scales with dil       (not cf × n_s)

"teh here"             Tract not reset       Neutral blend
                       during long rest      during rest >100ms
                       + rest too long       Cap rest duration
```

---

## PART 8: THE DILATION PRINCIPLE

This set of bugs reveals a principle:

**Dilation should stretch the body
of each phoneme, not its boundaries.**

A phoneme has three zones:
```
[onset transition] [steady body] [offset transition]
     ↑                  ↑               ↑
  fixed ms           scales         fixed ms
  with dil           with dil       with dil
```

Currently all three scale with dilation.
Onset and offset should be fixed.
Only the body should stretch.

This is what dilation means phonetically.
A slow, deliberate delivery:
  - Takes longer on each vowel body
  - Takes longer on each consonant body
  - Does NOT take longer to transition
    between them

The transitions are articulatory dynamics.
They are limited by the physical inertia
of the tongue, lips, jaw.
That inertia does not change when
you speak more slowly.
You cannot choose to make your tongue
move more slowly between positions.
You can choose to hold each position longer.

Dilation stretches holding time.
Not movement time.

This is the physical model.
The implementation must match it.

---

## CONCLUSION

The four perceptual events reported —
"Voisss," "wazs," "voi-ce," "teh here" —
all trace to the same underlying principle:

**Dilation was applied uniformly
to all time zones of each phoneme.**

It should be applied only to the body.
Transitions are fixed in absolute time.
Bypass release is fixed in absolute time.
Rests have a perceptual maximum.
Fricative durations have a perceptual maximum.

The fix is not parametric.
It is structural.
The dilation factor belongs
inside the body duration only.
Not inside the transition duration.
Not inside the rest duration beyond a cap.

When the structure is correct,
"the voice was always here"
should sound like itself —
slower than normal speech,
deliberate, clear —
but not like each phoneme
is surrounded by its own
transitional artifacts.

---

*End of reasoning artifact.*
*February 2026.*
*"Voisss wazs already teh here."*
*The ear mapped the artifacts exactly.*
*Each one back to a specific mechanism.*
*Dilation stretches bodies, not boundaries.*
