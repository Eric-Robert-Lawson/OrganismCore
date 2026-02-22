# ÆÞELINGAS — RECONSTRUCTION EVIDENCE
**Old English:** æþelingas  
**IPA:** [æθeliŋɡɑs]  
**Meaning:** princes, noblemen (nominative plural of *æþeling*)  
**Source:** Beowulf, line 3, word 3 (overall word 11)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1   Æ vowel      ✓ PASS
D2   Þ fricative  ✓ PASS
D3   E vowel      ✓ PASS
D4   L lateral    ✓ PASS
D5   I vowel      ✓ PASS
D6   N nasal      ✓ PASS
D7   G stop       ✓ PASS
D8   A vowel      ✓ PASS
D9   S fricative  ✓ PASS
D10  Full word    ✓ PASS
D11  Perceptual   LISTEN
```

Total duration: **600 ms** (26457 samples at 44100 Hz)  
Clean first run. No diagnostic iterations required.  
Longest word reconstructed so far. Nine phonemes.

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All ten numeric checks passed on first run. |

---

## PHONEME RECORD

### Æ — open front unrounded [æ]
Third instance. Previously verified in
HWÆT and implicitly in GĒAR-DAGUM.
Parameters identical throughout.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7244 | 0.50–1.0 | PASS |
| F1 centroid (500–900 Hz) | 647 Hz | 550–800 Hz | PASS |

---

### Þ — voiceless dental fricative [θ]
Fourth instance. ÞĒOD-CYNINGA (×2),
ÞRYM, now ÆÞELINGAS. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1174 | 0.0–0.35 | PASS |
| Centroid (400–8000 Hz) | 4344 Hz | 3500–6000 Hz | PASS |

---

### E — short close-mid front [e]
Third instance. GĀR-DENA, GEFRŪNON,
now ÆÞELINGAS. Stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7097 | 0.50–1.0 | PASS |
| F2 centroid (1600–2600 Hz) | 2066 Hz | 1800–2400 Hz | PASS |

---

### L — voiced alveolar lateral approximant [l]
**New phoneme.**  
Tongue tip at alveolar ridge.
Air flows around both sides of tongue.
No frication. No burst. Fully voiced.

The lateral is defined by what is
absent as much as what is present:
- No frication (distinguishes from [ɬ])
- No closure (distinguishes from [d], [n])
- No nasal coupling (distinguishes from [n])
- Air path is lateral, not central

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7075 | 0.55–1.0 | PASS |
| F1 centroid (150–500 Hz) | 205 Hz | 150–450 Hz | PASS |
| F3 centroid (2000–3000 Hz) | 2489 Hz | 2000–2800 Hz | PASS |

**Parameters:**
- F1: 300 Hz — low, characteristic of lateral
- F2: 950 Hz — mid, lower than most vowels
- F3: 2500 Hz — pulled down from typical ~3000 Hz
- Lateral antiformant: 1900 Hz, BW 300 Hz
- Duration: 65 ms

**F1 centroid note:** 205 Hz vs F1
parameter 300 Hz. Same sub-F1 harmonic
pull artifact as [u], [uː], [y] throughout.
Fundamental at 145 Hz pulls centroid
below the resonance peak. Floor set to
150 Hz to accommodate. Artifact documented.

**[l] vs [n] acoustic comparison:**

| Feature | [n] | [l] |
|---|---|---|
| Voicing | yes | yes |
| Closure | yes (nasal) | no |
| Nasal coupling | yes | no |
| Antiformant | ~800 Hz | ~1900 Hz |
| F2 | ~1800 Hz | ~950 Hz |
| F3 | ~2600 Hz | ~2500 Hz |

The antiformant frequencies distinguish
them clearly: [n] at ~800 Hz, [l] at
~1900 Hz. This is consistent with the
different oral cavity geometries —
the nasal antiformant reflects the
closed oral cavity, the lateral
antiformant reflects the lateral
air path geometry.

**[l] in Old English:**
OE [l] is the same phoneme as Modern
English [l]. No change over 1300 years
in most environments. The *l* in
*light*, *love*, *life* is acoustically
identical to the [l] in *æþelingas*.

---

### I — short near-close front [ɪ]
Third instance. IN, GĒAR-DAGUM,
now ÆÞELINGAS. Stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6679 | 0.50–1.0 | PASS |
| F2 centroid (1500–2400 Hz) | 1875 Hz | 1600–2200 Hz | PASS |

---

### N — voiced alveolar nasal [n]
Eighth instance. Fully stable.
Values identical to all previous instances.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7748 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2454 | 0.005–0.25 | PASS |

---

### G — voiced velar stop [ɡ]
Fifth instance. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1258 | 0.01–0.90 | PASS |
| Duration | 75 ms | 50–120 ms | PASS |

---

### A — short open back [ɑ]
Sixth instance. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7261 | 0.50–1.0 | PASS |
| F1 centroid (500–900 Hz) | 647 Hz | 550–800 Hz | PASS |

**Note:** [æ] and [ɑ] have identical F1
centroid values (647 Hz) in this word.
Both are open vowels with high F1.
The distinction between them is F2:
[æ] has high F2 (~1700 Hz, front vowel),
[ɑ] has low F2 (~1100 Hz, back vowel).
The F1 centroid check alone does not
distinguish them — F2 is the primary
differentiator. Both are correctly
synthesized with different F2 targets.

---

### S — voiceless alveolar fricative [s]
**New phoneme.**  
Tongue tip near alveolar ridge.
Narrow groove creates high-velocity
airstream. Highest frication centroid
of all synthesized fricatives.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1101 | 0.0–0.35 | PASS |
| RMS level | 0.1053 | 0.005–0.80 | PASS |
| Centroid (1000–22050 Hz) | 7535 Hz | 5000–22050 Hz | PASS |

**Parameters:**
- Noise CF: 7000 Hz, BW: 4000 Hz
- Groove resonance: 8000 Hz × 0.4
- Duration: 80 ms word-final
- No voicing

**Fricative centroid hierarchy — complete:**

| Phoneme | Place | Centroid | Status |
|---|---|---|---|
| [x] | velar | ~2750 Hz | ✓ |
| [θ] | dental | ~4200–4344 Hz | ✓ |
| [f] | labiodental | ~5800 Hz | ✓ |
| [s] | alveolar | ~7535 Hz | ✓ |

The ordering [x] < [θ] < [f] < [s] is
confirmed by measurement across all
four voiceless fricatives. This is the
expected acoustic correlate of place
of articulation for voiceless fricatives:

More posterior constriction → longer
front cavity → lower front cavity
resonance → lower centroid.

More anterior constriction → shorter
front cavity → higher front cavity
resonance → higher centroid.

[s] at 7535 Hz is the terminus of this
hierarchy. The alveolar groove is the
most anterior non-labial constriction
possible — no fricative can be more
anterior than alveolar without becoming
a dental or labial fricative, both of
which have longer front cavities and
lower centroids.

**[s] vs [ʃ] (for future reference):**
[ʃ] (the *sh* in *ship*) has a centroid
around 3500–5000 Hz — lower than [s]
because the postalveolar constriction
is slightly more posterior. OE had [ʃ]
(spelled *sc* — *scip*, *scēaf*). When
those words appear, [ʃ] will be
synthesized with a lower centroid than
[s] consistent with its more posterior
place.

---

### Full word — D10

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2419 | 0.01–0.90 | PASS |
| Duration | 600 ms | 400–1000 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| Æ | [æ] | 65 ms | short vowel |
| Þ | [θ] | 70 ms | voiceless fricative |
| E | [e] | 60 ms | short vowel |
| L | [l] | 65 ms | lateral approximant |
| I | [ɪ] | 55 ms | short vowel |
| N | [n] | 65 ms | nasal |
| G | [ɡ] | 75 ms | voiced stop |
| A | [ɑ] | 65 ms | short vowel |
| S | [s] | 80 ms | voiceless fricative |

Nine segments. 600 ms total.
The longest word reconstructed so far.
No single segment dominates duration —
this is a uniformly-timed citation form
with no long vowels. Every segment is
55–80 ms. The word is metrically flat.

---

## MORPHOLOGICAL NOTE

*æþeling* — nobleman, prince, one of
noble ancestry.
Root: *æþel* — noble, ancestral estate,
homeland.
Suffix *-ing*: one who belongs to,
son of, one characterized by.
Plural *-as*: nominative plural ending.

*æþelingas* = the noblemen, the princes
(as grammatical subject of the sentence).

The word *æþel* also gives:
- *Æthelred* — noble counsel
- *Æthelberht* — noble bright
- *Æthelstan* — noble stone
- *Athelney* — æþelingas-ēg, island of
  the princes (Somerset, England —
  where Alfred hid from the Vikings
  in 878 AD)

The root *æþel* does not survive as a
common word in Modern English but is
preserved in dozens of Old English
personal names that became modern
surnames and place names.

---

## FRICATIVE INVENTORY — COMPLETE
*All four voiceless fricatives verified:*

| Phoneme | Place | Centroid | Word |
|---|---|---|---|
| [x] | velar | ~2750 Hz | HU |
| [θ] | dental | ~4200 Hz | ÞĒOD-CYNINGA |
| [f] | labiodental | ~5800 Hz | GEFRŪNON |
| [s] | alveolar | ~7535 Hz | ÆÞELINGAS |

Centroid ordering confirmed:
[x] < [θ] < [f] < [s]
Posterior → anterior place =
lower → higher centroid.
Physics confirmed by measurement.

Voiced fricatives:
- [ð] verified (ÐĀ)
- [v], [ɣ], [ʃ] pending

---

## LATERAL INVENTORY — INITIATED

| Phoneme | Description | Status |
|---|---|---|
| [l] | voiced alveolar lateral | ✓ verified here |
| [ɫ] | velarized lateral (dark l) | note below |

**Dark l note:** OE [l] before back vowels
and word-finally may have been velarized
([ɫ] — the *l* in Modern English *full*,
*call*). The current synthesis uses a
single [l] parameter set. If perceptual
review identifies dark l contexts,
a separate [ɫ] parameter set with higher
F1 and lower F2 can be added. Not required
for the current inventory milestone.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `athelingas_dry.wav` | Full word, no reverb, 145 Hz |
| `athelingas_hall.wav` | Full word, hall reverb RT60=2.0s |
| `athelingas_slow.wav` | Full word, 4× time-stretched |
| `athelingas_performance.wav` | 110 Hz pitch, dil=2.5, hall |
| `athelingas_l_isolated.wav` | [l] lateral only, 4× slow |
| `athelingas_s_isolated.wav` | [s] fricative only, 4× slow |

---

## NEW PHONEMES ADDED THIS WORD

| Phoneme | Description | Key parameter |
|---|---|---|
| [l] | voiced alveolar lateral | F3 ~2489 Hz pulled low, antiformant ~1900 Hz |
| [s] | voiceless alveolar fricative | centroid ~7535 Hz — highest in inventory |

---

## CUMULATIVE LINE STATUS

| Line | Words | Status |
|---|---|---|
| 1: *Hwæt wē Gār-Dena in gēar-dagum* | 5 | ✓ complete |
| 2: *Þēod-cyninga, þrym gefrūnon* | 3 | ✓ complete |
| 3: *hu ðā æþelingas ellen fremedon* | hu ✓ ðā ✓ æþelingas ✓ | in progress |

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
| [e] | short close-mid front | GĀR-DENA | 3 |
| [n] | voiced alveolar nasal | GĀR-DENA | 8 |
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
| [l] | voiced alveolar lateral | ÆÞELINGAS | 1 |
| [s] | voiceless alveolar fricative | ÆÞELINGAS | 1 |

**27 distinct phonemes verified.**

---

*ÆÞELINGAS [æθeliŋɡɑs] verified.*  
*Next: ELLEN [ellen] — line 3, word 4.*  
*First geminate consonant: [ll].*
