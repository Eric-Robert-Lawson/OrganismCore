# GŌD — RECONSTRUCTION EVIDENCE
**Old English:** gōd  
**IPA:** [ɡoːd]  
**Meaning:** good  
**Source:** Beowulf, line 4, word 3 (overall word 16)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  G stop           ✓ PASS
D2  Ō long vowel     ✓ PASS
D3  D stop           ✓ PASS
D4  Long/short ratio ✓ PASS
D5  Full word        ✓ PASS
D6  Perceptual       LISTEN
```

Total duration: **295 ms** (13009 samples at 44100 Hz)  
Clean first run. Five for five.  
One new phoneme: [oː].

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All five numeric checks passed on first run. |

---

## PHONEME RECORD

### G — voiced velar stop [ɡ]
Sixth instance. GĀR-DENA, GĒAR-DAGUM,
GEFRŪNON, ÆÞELINGAS, FREMEDON,
now GŌD. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1205 | 0.01–0.90 | PASS |
| Duration | 75 ms | 50–120 ms | PASS |

---

### Ō — long close-mid back rounded [oː]
**New phoneme.**  
Long counterpart of short [o].
First new phoneme since ÐĀ (word 10).
Five consecutive assembly words ended.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.8666 | 0.60–1.0 | PASS |
| Duration | 150 ms | 120–200 ms | PASS |
| F2 centroid (500–1000 Hz) | 701 Hz | 550–850 Hz | PASS |

**Voicing 0.8666 — highest in the
vowel inventory.**
Long vowels have more sustained
periodic energy in the autocorrelation
window than short vowels. The longer
steady-state plateau gives the
autocorrelation more cycles to work
with. This is consistent with all
previous long vowel instances —
[ɑː], [eː], [uː] all showed voicing
scores above 0.85.

**Parameters:**
- F1: 430 Hz — close-mid height
- F2: 700 Hz — back position
- F3: 2400 Hz
- F4: 3200 Hz
- Duration: 150 ms
- No offglide — pure monophthong

**[oː] is a pure monophthong.**
Modern English *go*, *no*, *so* have
diphthongized to [oʊ] in most accents —
the vowel starts at [o] and glides
toward [ʊ]. Old English [oː] does not
do this. The tongue position and lip
rounding are held steady throughout.
The vowel starts and ends at the same
formant values. This is a feature
shared with many modern languages —
German *so* [zoː], Italian *no* [nɔ] —
but lost in most English dialects.

**[oː] vs [o] — length ratio (D4):**

| Segment | Duration | Ratio |
|---|---|---|
| [o] short target | 65 ms | 1.00× |
| [oː] long measured | 150 ms | 2.31× |

Target ratio: ≥ 1.70×.  
Measured: 2.31×. Clean.

The same duration ratio mechanism
that distinguishes geminate [lː] from
singleton [l] applies here. Old English
vowel length is phonemically contrastive:

| Word | IPA | Meaning |
|---|---|---|
| *god* | [ɡod] | God (the deity) |
| *gōd* | [ɡoːd] | good (the adjective) |

One short vowel vs one long vowel —
different words, different meanings.
Duration is the only acoustic distinction.
The formant targets are identical.
This minimal pair appears in Beowulf
itself — the poem refers to both
*god* (God) and *gōd* (good). The
synthesis must distinguish them or
the poem is incomprehensible.
D4 confirms the distinction is present
and measurable.

**Long vowel inventory — updated:**

| Phoneme | Duration | First word |
|---|---|---|
| [eː] | 120 ms | WĒ |
| [ɑː] | 150 ms | GĀR-DENA |
| [uː] | 130 ms | GEFRŪNON |
| [oː] | 150 ms | GŌD |

All long vowels 120–150 ms.
All short vowels 55–65 ms.
Ratio consistently 2.0–2.5× across
all long/short pairs.
The length system is fully consistent.

**[oː] in the heroic vocabulary:**

This phoneme appears in the most
frequent and significant words of
Beowulf's heroic register:

| Word | IPA | Meaning | Approx. count |
|---|---|---|---|
| *gōd* | [ɡoːd] | good | ~30 |
| *mōd* | [moːd] | spirit, courage | ~40 |
| *dōm* | [doːm] | glory, judgment | ~20 |
| *blōd* | [bloːd] | blood | ~15 |
| *fōt* | [foːt] | foot | ~5 |
| *bōt* | [boːt] | remedy, cure | ~5 |

Estimated 150+ instances of [oː]
across the full poem. The parameters
established here serve all of them.

---

### D — voiced alveolar stop [d]
Fifth instance. GĀR-DENA (×3),
FREMEDON, now GŌD. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.1231 | 0.01–0.90 | PASS |
| Duration | 70 ms | 50–120 ms | PASS |

---

### Full word — D5

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2787 | 0.01–0.90 | PASS |
| Duration | 295 ms | 200–450 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| G | [ɡ] | 75 ms | voiced stop |
| Ō | [oː] | 150 ms | long vowel |
| D | [d] | 70 ms | voiced stop |

Total: 295 ms. Three segments.
The long vowel at 150 ms accounts
for 51% of the total word duration.
This is the acoustic signature of
a long-vowel word — the vowel
dominates the temporal profile.
Compare to GĀR [ɡɑːr] where [ɑː]
similarly dominates at 150 ms of
~295 ms total. Long vowel words
are acoustically front-heavy in
terms of energy and duration.

---

## MINIMAL PAIR NOTE

**[ɡod] vs [ɡoːd] — god vs gōd:**

This is one of the most important
minimal pairs in Beowulf. The poem
refers to the Christian God (*god*)
and uses the adjective *gōd* (good)
constantly. In recitation, a listener
distinguishes them solely by the
duration of the medial vowel.

The synthesis engine now produces
both correctly:
- [ɡod]: 65 ms vowel — *God*
- [ɡoːd]: 150 ms vowel — *good*

The ratio 2.31× is well above the
perceptual threshold for length
distinction (~1.5×). A listener
would not confuse these two words.

---

## MORPHOLOGICAL NOTE

*gōd* — adjective, strong declension.
Meaning: good, virtuous, capable,
effective. A term of general positive
evaluation — good in quality, good
in character, good in performance.

In the context of *þæt wæs gōd cyning*
(that was a good king), *gōd* is the
predicate adjective modifying *cyning*.
The statement is the poem's verdict
on Scyld Scefing and, by extension,
on all the great kings described in
the opening lines.

*Gōd* → Modern English *good*.
The vowel has shortened and slightly
lowered ([oː] → [ʊ]). The consonants
are unchanged. The meaning is
unchanged. The word has been in
continuous use for over 1300 years.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `god_dry.wav` | Full word, no reverb, 145 Hz |
| `god_hall.wav` | Full word, hall reverb RT60=2.0s |
| `god_slow.wav` | Full word, 4× time-stretched |
| `god_performance.wav` | 110 Hz pitch, dil=2.5, hall |
| `god_oo_long.wav` | [oː] isolated, 4× slow |
| `god_o_short.wav` | [o] short reference, 4× slow |

---

## NEW PHONEMES ADDED THIS WORD

| Phoneme | Description | Key parameter |
|---|---|---|
| [oː] | long close-mid back rounded | 150 ms duration — ratio 2.31× short [o] |

**29 phonemes verified.**

---

## CUMULATIVE LINE STATUS

| Line | Text | Status |
|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | ✓ complete |
| 4 | *þæt wæs gōd cyning* | þæt ✓  wæs ✓  gōd ✓ — one word remaining |

---

## PHONEME INVENTORY
*All verified phonemes — 29 total:*

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

**29 verified.**  
**Remaining gaps: [p], [b], [iː], [æː],**  
**[eo], [eːo], [ɣ].**

---

*GŌD [ɡoːd] verified.*  
*Next: CYNING [kyniŋɡ] — line 4, word 4.*  
*Final word of line 4. Zero new phonemes.*  
*Line 4 completion one word away.*
