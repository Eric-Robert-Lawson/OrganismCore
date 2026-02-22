# MǢGÞUM — RECONSTRUCTION EVIDENCE
**Old English:** mǣgþum  
**IPA:** [mæːɣθum]  
**Meaning:** kinship groups, tribes, peoples (dative plural)  
**Source:** Beowulf, line 6, word 2 (overall word 23)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  M nasal             ✓ PASS
D2  AE_LONG vowel       ✓ PASS
D3  GH fricative        ✓ PASS
D4  TH fricative        ✓ PASS
D5  U vowel             ✓ PASS
D6  M nasal final       ✓ PASS
D7  GH/X distinction    ✓ PASS
D8  AEL/AE length       ✓ PASS
D9  Full word           ✓ PASS
D10 Perceptual          LISTEN
```

Total duration: **430 ms** (18961 samples at 44100 Hz)  
Clean first run. Nine for nine.  
Two new phonemes: [æː] and [ɣ].

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All nine numeric checks passed on first run. |

---

## ITERATION ANALYSIS

Both new phonemes passed on first attempt.

**[ɣ] synthesis strategy:**

Applied the lesson learned from [v]
in SCEFING. [v] required three
iterations — the noise-mixing strategy
failed twice before switching to pure
voiced source with AM modulation.

For [ɣ], the pure voiced source
strategy was used from the start.
No noise component. Rosenberg pulse
filtered through velar constriction
band formants. AM modulation at 80 Hz.
Result: voicing 0.7607. First run.

The [v]/[f] experience was directly
transferable: voiced fricatives in
OE are primarily voiced sounds —
the frication is secondary. The
voicing is the phonemically
relevant feature. Synthesis must
prioritise the periodic source.

---

## PHONEME RECORD

### M — voiced bilabial nasal [m]
Word-initial. Consistent with all
previous [m] instances.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7751 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2122 | 0.005–0.25 | PASS |

---

### AE_LONG — long open front unrounded [æː]
**New phoneme. 33rd verified.**

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.8634 | 0.50–1.0 | PASS |
| F2 centroid (1200–2200 Hz) | 1663 Hz | 1400–2000 Hz | PASS |
| Duration | 100 ms | 85–130 ms | PASS |

**D8 — [æː] vs [æ] length distinction:**

| Measure | Value | Target | Result |
|---|---|---|---|
| [æː] duration | 100 ms | 85–130 ms | PASS |
| Length ratio [æː]/[æ] | 2.00× | 1.7–3.0× | PASS |

**[æ] cross-instance comparison:**

| Sound | Duration | F2 | Quality |
|---|---|---|---|
| [æ] short — HWÆT | ~50 ms | ~1700 Hz | open front |
| [æː] long — MǢGÞUM | 100 ms | 1663 Hz | open front |

F2 values nearly identical: 1663 Hz
vs ~1700 Hz. The quality is the same.
The duration is exactly double.
This is the correct relationship
for a vowel length distinction in OE.

**Vowel length in Old English:**

OE distinguishes short and long
vowels phonemically. The distinction
is quantity, not quality. Every
short vowel has a long counterpart:

| Short | Long | Distinction |
|---|---|---|
| [æ] | [æː] | duration ×2 |
| [e] | [eː] | duration ×2 |
| [ɑ] | [ɑː] | duration ×2 |
| [o] | [oː] | duration ×2 |
| [u] | [uː] | duration ×2 |
| [ɪ] | [iː] | duration ×2 |
| [y] | [yː] | duration ×2 |

In poetry the distinction is
metrically significant — long
vowels carry heavy syllables,
short vowels light syllables.
The alliterative metre of Beowulf
depends on this distinction being
real and consistent. Every long
vowel in the poem is genuinely
longer than its short counterpart.

**[æː] frequency in Old English:**

| OE word | IPA | Modern English |
|---|---|---|
| *mǣg* | [mæːɣ] | kinsman (obs.) |
| *dǣd* | [dæːd] | deed |
| *sǣ* | [sæː] | sea |
| *hǣl* | [hæːl] | hale, health |
| *wǣpn* | [wæːpn] | weapon |
| *slǣpan* | [slæːpɑn] | sleep |
| *lǣdan* | [læːdɑn] | lead (verb) |
| *clǣne* | [klæːne] | clean |

The [æː] parameters verified here
apply to all of these and hundreds
of other OE words. The long front
open vowel is one of the most
productive vowels in the language.

---

### GH — voiced velar fricative [ɣ]
**New phoneme. 34th verified.**

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be high) | 0.7607 | 0.35–1.0 | PASS |
| RMS level | 0.2205 | 0.005–0.80 | PASS |

**D7 — [ɣ] vs [x] distinction:**

| Phoneme | Voicing | Verified in |
|---|---|---|
| [x] voiceless velar fricative | ~0.10 | HU |
| [ɣ] voiced velar fricative | 0.7607 | MǢGÞUM |

Separation: 0.6607 voicing units.
The velar fricative pair is now
complete. Same place, same manner,
opposite laryngeal setting.

**[ɣ] synthesis parameters:**

- F1: 500 Hz, BW 400 Hz
- F2: 1500 Hz, BW 500 Hz
- F3: 2800 Hz, BW 600 Hz
- AM rate: 80 Hz
- AM depth: 0.25
- No noise component
- Pure Rosenberg pulse source

Broad bandwidth formants model
the distributed velar constriction.
The tongue dorsum raised toward
the velum creates a wide resonance
cavity with no sharp formant peaks
— hence large bandwidths relative
to vowels.

**[ɣ] distribution in Old English:**

OE /g/ has three allophones
depending on phonological context:

| Context | Realisation | Example |
|---|---|---|
| Word-initial before back vowels | [ɡ] stop | *god* [ɡod] |
| Word-initial before front vowels | [j] approximant | *geong* [joŋɡ] |
| Intervocalic / between voiced segs | [ɣ] fricative | *mǣgþum* [mæːɣθum] |

The same letter *g* represents three
different sounds. Context determines
which. This is why OE /g/ looks
deceptively simple in the manuscript
but requires three separate synthesis
paths in the reconstruction.

**OE words with intervocalic [ɣ]:**

| OE word | IPA | Meaning |
|---|---|---|
| *mǣg* | [mæːɣ] | kinsman |
| *dragan* | [draɣɑn] | to draw/drag |
| *boga* | [boɣɑ] | bow (weapon) |
| *maga* | [mɑɣɑ] | stomach |
| *lagu* | [lɑɣu] | law, water |
| *saga* | [sɑɣɑ] | saying, tale |
| *folgian* | [folɣiɑn] | to follow |

Modern English *drag*, *bow*, *follow*
all descend from OE words where [ɣ]
was intervocalic. The [ɣ] was either
lost or vocalised in Middle English —
it does not survive in any standard
Modern English dialect, though it
persists in some Scottish English
pronunciations.

**The voiced velar fricative pair —
complete:**

| Phoneme | Description | Voicing | First word |
|---|---|---|---|
| [x] | voiceless velar fricative | ~0.10 | HU |
| [ɣ] | voiced velar fricative | 0.7607 | MǢGÞUM |

Both velars verified. The velar
fricative inventory is complete.

---

### TH — voiceless dental fricative [θ]
Eighth instance. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1481 | 0.0–0.35 | PASS |
| RMS level | 0.0991 | 0.001–0.50 | PASS |

---

### U — short close back rounded [u]
Fully stable. Consistent across
all instances.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6675 | 0.50–1.0 | PASS |
| F2 centroid (500–1200 Hz) | 738 Hz | 550–1100 Hz | PASS |

---

### M — voiced bilabial nasal [m] final
Identical to initial instance.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7751 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2122 | 0.005–0.25 | PASS |

---

### Full word — D9

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2688 | 0.01–0.90 | PASS |
| Duration | 430 ms | 380–650 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| M | [m] | 65 ms | voiced bilabial nasal |
| Ǣ | [æː] | 100 ms | long open front unrounded |
| G | [ɣ] | 70 ms | voiced velar fricative |
| Þ | [θ] | 75 ms | voiceless dental fricative |
| U | [u] | 55 ms | short close back rounded |
| M | [m] | 65 ms | voiced bilabial nasal |

Total: 430 ms. Six segments.
The [æː] at 100 ms is the longest
single segment in this word — as
expected for a long vowel. It is
twice the duration of [u] at 55 ms.
The two fricatives [ɣ] and [θ]
are adjacent — voiced into voiceless.
The transition is abrupt: vocal fold
vibration stops at the [ɣ]/[θ]
boundary.

---

## ETYMOLOGICAL NOTE

**mǣgþ — kinship group:**

*mǣgþ* is a feminine noun meaning
a kinship group, tribe, clan, nation,
or people related by blood. It derives
from *mǣg* (kinsman, male relative)
with the collective suffix *-þ*.

Related words:
- *mǣg* — kinsman, male relative
- *māge* — female relative, kinswoman
- *mǣgsibb* — kinship, relationship
- *mǣgwlite* — family resemblance

The concept of *mǣgþ* is central to
the social world of Beowulf. Loyalty,
obligation, feud, and honour all
operate through kinship structures.
Scyld's power extended across many
such groups — *mongum mǣgþum* —
many tribes, many kinship networks.

**Modern English reflexes:**

*mǣg* → ModE *may* (auxiliary verb
meaning to have power or ability —
originally: to be strong, to be able,
as a kinsman gives strength).

The [ɣ] in *mǣg* [mæːɣ] was lost
in ME — *may* has no consonant
where OE had [ɣ]. This is one of
the most common fates of OE [ɣ]:
silent loss between vowels, leaving
only the surrounding vowels.

---

## VOICED FRICATIVE INVENTORY — COMPLETE

With [ɣ] verified, all voiced
fricatives in the OE inventory
are now confirmed:

| Phoneme | Place | Voicing | Verified |
|---|---|---|---|
| [v] | labiodental | 0.7618 | SCEFING |
| [ð] | dental | 0.65+ | ÐĀ |
| [ɣ] | velar | 0.7607 | MǢGÞUM |

The voiceless counterparts:

| Phoneme | Place | Voicing | Verified |
|---|---|---|---|
| [f] | labiodental | ~0.00 | GEFRŪNON |
| [θ] | dental | ~0.10 | ÞĒOD-CYNINGA |
| [x] | velar | ~0.10 | HU |

Three voiced/voiceless fricative
pairs. All six verified. The fricative
inventory of Old English is complete.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `maegthum_dry.wav` | Full word, no reverb, 145 Hz |
| `maegthum_hall.wav` | Full word, hall reverb RT60=2.0s |
| `maegthum_slow.wav` | Full word, 4× time-stretched |
| `maegthum_gh_only.wav` | [ɣ] isolated, 4× slow |
| `maegthum_ael_only.wav` | [æː] isolated, 4× slow |

---

## NEW PHONEMES ADDED THIS WORD

| Phoneme | Description | Key parameter | Iterations |
|---|---|---|---|
| [æː] | long open front unrounded | duration 100 ms — ratio 2.00× vs [æ] | 1 |
| [ɣ] | voiced velar fricative | voicing 0.7607 — pure voiced source, AM 80 Hz | 1 |

**34 phonemes verified.**

---

## CUMULATIVE LINE STATUS

| Line | Text | Words | Status |
|---|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | 1–5 | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | 6–8 | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | 9–13 | ✓ complete |
| 4 | *þæt wæs gōd cyning* | 14–17 | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | 18–21 | ✓ complete |
| 6 | *mongum mǣgþum meodosetla ofteah* | 22–25 | mongum ✓  mǣgþum ✓ — in progress |

---

## PHONEME INVENTORY
*All verified phonemes — 34 total:*

| Phoneme | Description | First word |
|---|---|---|
| [ʍ] | voiceless labio-velar fricative | HWÆT |
| [æ] | open front unrounded | HWÆT |
| [t] | voiceless alveolar stop | HWÆT |
| [w] | voiced labio-velar approximant | WĒ |
| [eː] | long close-mid front | WĒ |
| [ɡ] | voiced velar stop | GĀR-DENA |
| [ɑː] | long open back | GĀR-DENA |
| [r] | alveolar trill | GĀR-DENA |
| [d] | voiced alveolar stop | GĀR-DENA |
| [e] | short close-mid front | GĀR-DENA |
| [n] | voiced alveolar nasal | GĀR-DENA |
| [ɑ] | short open back | GĀR-DENA |
| [ɪ] | short near-close front | IN |
| [u] | short close back rounded | GĒAR-DAGUM |
| [m] | voiced bilabial nasal | GĒAR-DAGUM |
| [θ] | voiceless dental fricative | ÞĒOD-CYNINGA |
| [o] | short close-mid back rounded | ÞĒOD-CYNINGA |
| [k] | voiceless velar stop | ÞĒOD-CYNINGA |
| [y] | short close front rounded | ÞĒOD-CYNINGA |
| [ŋ] | voiced velar nasal | ÞĒOD-CYNINGA |
| [j] | palatal approximant | GEFRŪNON |
| [f] | voiceless labiodental fricative | GEFRŪNON |
| [uː] | long close back rounded | GEFRŪNON |
| [x] | voiceless velar fricative | HU |
| [ð] | voiced dental fricative | ÐĀ |
| [l] | voiced alveolar lateral | ÆÞELINGAS |
| [s] | voiceless alveolar fricative | ÆÞELINGAS |
| [lː] | geminate lateral | ELLEN |
| [oː] | long close-mid back rounded | GŌD |
| [ʃ] | voiceless postalveolar fricative | SCYLD |
| [v] | voiced labiodental fricative | SCEFING |
| [eɑ] | short front-back diphthong | SCEAÞENA |
| [æː] | long open front unrounded | MǢGÞUM |
| [ɣ] | voiced velar fricative | MǢGÞUM |

**34 verified.**  
**Remaining gaps: [p], [b], [iː],**  
**[eːɑ], [eo], [eːo].**  
**6 phonemes remaining.**

---

*MǢGÞUM [mæːɣθum] verified.*  
*[æː] and [ɣ] added.*  
*Fricative inventory complete — all 6 fricative pairs verified.*  
*Next: MEODOSETLA [meodosetlɑ] — line 6, word 3.*  
*NEW PHONEME: [eo] short front-mid diphthong.*
