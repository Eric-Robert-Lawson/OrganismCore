# ELLEN — RECONSTRUCTION EVIDENCE
**Old English:** ellen  
**IPA:** [ellen]  
**Meaning:** courage, strength, zeal, vigorous effort in battle  
**Source:** Beowulf, line 3, word 4 (overall word 12)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  E1 vowel        ✓ PASS
D2  LL geminate     ✓ PASS
D3  E2 vowel        ✓ PASS
D4  N nasal         ✓ PASS
D5  Geminate ratio  ✓ PASS
D6  Full word       ✓ PASS
D7  Perceptual      LISTEN
```

Total duration: **315 ms** (13891 samples at 44100 Hz)  
Clean first run. Six for six.  
Geminate ratio exactly 2.00×.  
First geminate consonant verified.

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All six numeric checks passed on first run. |

---

## PHONEME RECORD

### E1 — short close-mid front [e]
Fourth instance. GĀR-DENA, GEFRŪNON,
ÆÞELINGAS, now ELLEN (×2). Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7097 | 0.50–1.0 | PASS |
| F2 centroid (1600–2600 Hz) | 2066 Hz | 1800–2400 Hz | PASS |

**Pronunciation note:**
[e] is the vowel in Modern English
*bed*, *get*, *set* — short mid front.
It is NOT the vowel in *bead*, *eel*,
*see* — those are [iː], long close front.
The distinction matters for *ellen*:
the word sounds like **eh·lll·eh·n**,
not **eel·l·ea·n**.

---

### LL — geminate lateral [lː]
**First geminate consonant verified.**

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.8441 | 0.55–1.0 | PASS |
| F1 centroid (150–500 Hz) | 202 Hz | 150–450 Hz | PASS |
| F3 centroid (2000–3000 Hz) | 2492 Hz | 2000–2800 Hz | PASS |
| Duration | 130 ms | 110–160 ms | PASS |

**Geminate ratio (D5):**

| Segment | Duration | Samples |
|---|---|---|
| [l] singleton | 65 ms | 2866 |
| [lː] geminate | 130 ms | 5733 |
| **Ratio** | **2.00×** | — |

Target: 1.70–2.50×. Measured: 2.00×.
Exactly double. Clean.

**What a geminate is:**

A geminate is a phonemically long
consonant. It is not two consonants.
It is one consonant held for
approximately twice the duration
of its singleton counterpart.

For [lː] specifically:
- Tongue tip contacts alveolar ridge
- Air flows around sides — same as [l]
- Lateral antiformant present — same as [l]
- F1, F2, F3 targets identical to [l]
- The articulation is continuous —
  no release, no re-closure, no gap
- Only duration distinguishes [lː] from [l]

The synthesis implementation:
- onset transition: 20 ms (same as singleton)
- plateau: 90 ms (vs 25 ms singleton)
- offset transition: 20 ms (same as singleton)
- total: 130 ms vs 65 ms singleton

The extra 65 ms is entirely in the plateau.
The transitions are the same absolute
duration — the tongue moves to and from
the alveolar ridge at the same speed.
Only the hold time changes.

**Why geminates matter phonemically:**

Old English geminate consonants were
phonemically contrastive — minimal pairs
existed where the only distinction was
consonant length:

| Word | IPA | Meaning |
|---|---|---|
| *calan* | [kɑlɑn] | to be cold |
| *callan* | [kɑlːɑn] | to call |
| *sittan* | [sittɑn] | to sit |
| *witan* | [witɑn] | to know |

A listener could not recover the meaning
without the length distinction.
The geminate is not an orthographic
convention — it is a phonemic reality.

**Geminates in Modern English:**

Modern English has lost phonemic geminate
consonants. The double letters in Modern
English spelling (*sitting*, *running*,
*better*) are orthographic, not phonemic.
A Modern English speaker does not hold
the *t* in *sitting* longer than the *t*
in *siting*. An Old English speaker did.

This is why *ellen* sounds unfamiliar
even to a native English speaker —
the phonemic length distinction on the
consonant does not exist in the modern
perceptual system. The ear hears it as
"a long l" without assigning phonemic
weight to the duration.

**Italian comparison:**
The closest modern analogue is Italian,
which preserves phonemic geminates:
*bello* [bɛlːo] vs *pelo* [pelo],
*anno* [anːo] vs *ano* [ano].
The geminate mechanism in *ellen* is
acoustically identical to Italian
geminate consonants.

---

### E2 — short close-mid front [e]
Second instance within this word.
Identical parameters to E1.
Coarticulation target from [l] formants.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7096 | 0.50–1.0 | PASS |
| F2 centroid (1600–2600 Hz) | 2067 Hz | 1800–2400 Hz | PASS |

E1 and E2 are effectively identical:
F2 2066 Hz vs 2067 Hz. The vowel
is stable across both positions
in this word.

---

### N — voiced alveolar nasal [n]
Word-final instance. Longer decay
envelope. Ninth verified instance.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7812 | 0.60–1.0 | PASS |
| RMS (nasal murmur) | 0.2299 | 0.005–0.25 | PASS |

---

### Full word — D6

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.3058 | 0.01–0.90 | PASS |
| Duration | 315 ms | 250–500 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| E | [e] | 60 ms | short vowel |
| LL | [lː] | 130 ms | geminate lateral |
| E | [e] | 60 ms | short vowel |
| N | [n] | 65 ms | nasal word-final |

Total: 315 ms.

The geminate at 130 ms is the longest
single segment in the word — longer than
either vowel, longer than the nasal.
It accounts for 41% of the total word
duration. This is the acoustic signature
of a geminate word: the consonant
dominates the temporal profile.

By comparison, in a hypothetical
singleton *elen* [elen], the [l]
would be 65 ms — 24% of total duration.
The geminate doubles that proportion.

---

## GEMINATE FRAMEWORK — ESTABLISHED

This word establishes the geminate
synthesis and verification framework
for all future geminate consonants.

**Rule:** geminate duration = 2.0× singleton.
**Test:** D5 geminate ratio check, target 1.7–2.5×.
**Implementation:** geminate=True flag in
synth_L() and all future consonant
synthesizers. Extra duration in plateau
only — transitions unchanged.

**Geminates expected in remaining words:**

| Word | Geminate |
|---|---|
| ELLEN | [lː] ✓ verified |
| Future words | [tː], [nː], [sː] etc. |

The framework is now documented and
tested. Future geminates require only
the geminate=True flag — no new
synthesis architecture needed.

---

## MORPHOLOGICAL NOTE

*ellen* — neuter a-stem noun.

The semantic field of *ellen* is
specifically heroic courage — not
passive bravery but active, vigorous,
physically demanding valor in combat.
It is the courage that makes a warrior
*do* something difficult, not merely
endure something.

Compounds with *ellen*:
- *ellenrōf* — famous for courage
- *ellenweorc* — deed of courage,
  heroic work
- *ellenþrист* — bold in courage
- *ellenmǣrþ* — glory won by courage

*Ellen* appears approximately 28 times
in Beowulf. It is one of the core
vocabulary items of the heroic register.

Modern English cognate: none surviving
as a common word. The name *Ellen*
comes through a separate Latin/Greek
pathway (Helena) and is unrelated.

Gothic cognate: *aljan* — zeal, effort.
The Proto-Germanic root *\*alja-*
means something like vigorous effort
or excess of energy.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `ellen_dry.wav` | Full word, no reverb, 145 Hz |
| `ellen_hall.wav` | Full word, hall reverb RT60=2.0s |
| `ellen_slow.wav` | Full word, 4× time-stretched |
| `ellen_performance.wav` | 110 Hz pitch, dil=2.5, hall |
| `ellen_ll_geminate.wav` | [lː] geminate only, 4× slow |
| `ellen_l_singleton.wav` | [l] singleton only, 4× slow |

---

## NEW PHENOMENA ADDED THIS WORD

| Phenomenon | Description | Key parameter |
|---|---|---|
| Geminate [lː] | Phonemically long lateral | ratio 2.00× — 130 ms vs 65 ms singleton |

No new phonemes. First geminate verified.

---

## CUMULATIVE LINE STATUS

| Line | Words | Status |
|---|---|---|
| 1: *Hwæt wē Gār-Dena in gēar-dagum* | 5 | ✓ complete |
| 2: *Þēod-cyninga, þrym gefrūnon* | 3 | ✓ complete |
| 3: *hu ðā æþelingas ellen fremedon* | hu ✓  ðā ✓  æþelingas ✓  ellen ✓ | one word remaining |

---

## PHONEME INVENTORY
*All verified phonemes as of this word:*

| Phoneme | Description | First word | Instances |
|---|---|---|---|
| [ʍ] | voiceless labio-velar fricative | HWÆT | 1 |
| [æ] | open front unrounded | HWÆT | 3 |
| [t] | voiceless alveolar stop | HWÆT | 1 |
| [w] | voiced labio-velar approximant | WĒ | 1 |
| [eː] | long close-mid front | WĒ | 3 |
| [ɡ] | voiced velar stop | GĀR-DENA | 5 |
| [ɑː] | long open back | GĀR-DENA | 3 |
| [r] | alveolar trill | GĀR-DENA | 4 |
| [d] | voiced alveolar stop | GĀR-DENA | 3 |
| [e] | short close-mid front | GĀR-DENA | 5 |
| [n] | voiced alveolar nasal | GĀR-DENA | 9 |
| [ɑ] | short open back | GĀR-DENA | 6 |
| [ɪ] | short near-close front | IN | 3 |
| [u] | short close back rounded | GĒAR-DAGUM | 2 |
| [m] | voiced bilabial nasal | GĒAR-DAGUM | 2 |
| [θ] | voiceless dental fricative | ÞĒOD-CYNINGA | 4 |
| [o] | short close-mid back rounded | ÞĒOD-CYNINGA | 2 |
| [k] | voiceless velar stop | ÞĒOD-CYNINGA | 1 |
| [y] | short close front rounded | ÞĒOD-CYNINGA | 2 |
| [ŋ] | voiced velar nasal | ÞĒOD-CYNINGA | 2 |
| [j] | palatal approximant | GEFRŪNON | 1 |
| [f] | voiceless labiodental fricative | GEFRŪNON | 1 |
| [uː] | long close back rounded | GEFRŪNON | 1 |
| [x] | voiceless velar fricative | HU | 1 |
| [ð] | voiced dental fricative | ÐĀ | 1 |
| [l] | voiced alveolar lateral | ÆÞELINGAS | 3 |
| [lː] | geminate lateral | ELLEN | 1 |
| [s] | voiceless alveolar fricative | ÆÞELINGAS | 1 |

**28 distinct phonemes and phenomena verified.**

---

*ELLEN [ellen] verified.*  
*Geminate consonant framework established.*  
*Next: FREMEDON [fremedon] — line 3, word 5.*  
*Final word of line 3.*  
*Zero new phonemes.*
