# ÞREATUM — RECONSTRUCTION EVIDENCE
**Old English:** þreatum  
**IPA:** [θreɑtum]  
**Meaning:** troops, bands, throngs (dative plural)  
**Source:** Beowulf, line 5, word 4 (overall word 21)  
**Line 5 final word.**  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  TH fricative      ✓ PASS
D2  R trill           ✓ PASS
D3  EA diphthong      ✓ PASS
D4  EA F2 movement    ✓ PASS
D5  T stop            ✓ PASS
D6  U vowel           ✓ PASS
D7  M nasal           ✓ PASS
D8  Full word         ✓ PASS
D9  Perceptual        LISTEN
```

Total duration: **410 ms** (18079 samples at 44100 Hz)  
Clean first run. Eight for eight.  
Zero new phonemes. Pure assembly.

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All eight numeric checks passed on first run. |

---

## PHONEME RECORD

### TH — voiceless dental fricative [θ]
Seventh instance. Word-initial here.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1444 | 0.0–0.35 | PASS |
| RMS level | 0.0714 | 0.001–0.50 | PASS |

Word-initial [θ] before [r]. No
preceding vowel — onset from silence.
The fricative ramps up from zero.
Clean voiceless onset confirmed.

---

### R — alveolar trill [r]
Post-fricative position. [θ]→[r]
onset — voiceless fricative into
voiced trill. The voicing onset
of the trill coincides with the
offset of the [θ].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.8608 | 0.45–1.0 | PASS |
| RMS level | 0.2351 | 0.005–0.80 | PASS |

Voicing 0.8608 — highest [r] instance
recorded. The trill modulation
preserves pitch periodicity cleanly.
The AM modulation at 28 Hz produces
2–3 taps across the 70 ms duration.
Audible in 4× slow playback.

---

### EA — short front-back diphthong [eɑ]
Second instance. SCEAÞENA, now ÞREATUM.
Post-trill position — [r]→[eɑ].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7588 | 0.50–1.0 | PASS |
| RMS level | 0.2307 | 0.01–0.90 | PASS |

**D4 — F2 movement trajectory:**

| Measure | Value | Target | Result |
|---|---|---|---|
| F2 onset | 1851 Hz | 1500–2200 Hz | PASS |
| F2 offset | 1131 Hz | 800–1500 Hz | PASS |
| F2 delta | 720 Hz ↓ | 400–1200 Hz | PASS |

**[eɑ] cross-instance stability:**

| Word | F2 onset | F2 offset | Delta |
|---|---|---|---|
| SCEAÞENA | 1851 Hz | 1131 Hz | 720 Hz |
| ÞREATUM | 1851 Hz | 1131 Hz | 720 Hz |

Identical values across both instances.
The diphthong trajectory is deterministic
— no stochastic noise component —
so it produces exactly the same
measurement in every instance.
This is the expected behaviour for
a vowel synthesiser with no random
element. Consistency confirmed.

---

### T — voiceless alveolar stop [t]
Post-diphthong position. [eɑ]→[t].
The stop follows the back [ɑ] offset
of the diphthong — vowel-to-stop
transition.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.2357 | 0.0–0.35 | PASS |
| RMS level | 0.0973 | 0.005–0.80 | PASS |
| Duration | 65 ms | 40–120 ms | PASS |

Voicing 0.2357 — slightly elevated
relative to word-initial [t] instances.
This is expected: the stop closure
follows a voiced vowel and the vocal
fold vibration carries briefly into
the closure phase. Still well within
the voiceless target range.

---

### U — short close back rounded [u]
Post-stop position. [t]→[u].
The vowel follows aspiration of the [t].

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6675 | 0.50–1.0 | PASS |
| F2 centroid (500–1200 Hz) | 738 Hz | 550–1100 Hz | PASS |

F2 738 Hz — consistent with all
previous [u] instances. The back
rounded vowel is stable across
the inventory. F2 below 800 Hz
confirms correct back placement.

---

### M — voiced bilabial nasal [m]
Word-final position. [u]→[m].
The word ends on a nasal — lips
close on the [m], voicing continues
through closure, word ends in
nasal murmur decaying to silence.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7751 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2122 | 0.005–0.25 | PASS |

---

### Full word — D8

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2310 | 0.01–0.90 | PASS |
| Duration | 410 ms | 350–600 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| Þ | [θ] | 75 ms | voiceless dental fricative |
| R | [r] | 70 ms | alveolar trill |
| EA | [eɑ] | 80 ms | short front-back diphthong |
| T | [t] | 65 ms | voiceless alveolar stop |
| U | [u] | 55 ms | short close back rounded |
| M | [m] | 65 ms | voiced bilabial nasal |

Total: 410 ms. Six segments.
The word contains a consonant cluster
at onset [θr] — the only two-consonant
onset cluster verified so far. The
cluster is handled by sequential
segment concatenation with coarticulation
at the boundary: [θ] offset feeds
into [r] onset formants.

---

## ETYMOLOGICAL NOTE

**þrēat → threat:**

OE *þrēat* — a pressing crowd,
a troop, a band, a throng.
The force in the word is literal:
a crowd that presses in on you.

Sound changes to Modern English:
- [θ] → ModE [θ] — unchanged
- [r] → ModE [r] — unchanged
  (though ModE [r] is not a trill)
- [eɑ] → ME [ɛː] → ModE [ɛ]
  (*threat* vowel)
- [t] → ModE [t] — unchanged

The dative plural *þreatum* adds the
*-um* suffix — the instrument of
Scyld's terror was enemy troops.
The singular *þrēat* became Modern
English *threat* through regular
sound change — the pressing crowd
became the pressing danger.

The word also gives:
- *threaten* — to press against
- *throng* — a pressing crowd
  (via different OE forms)

---

## LINE 5 — COMPLETE

```
Scyld Scefing    sceaþena þreatum
[ʃyld  ʃeviŋɡ   ʃeɑθenɑ  θreɑtum]

Scyld Scefing, [terrorised] troops
of enemies
```

**Line 5 word count:** 4 words (18–21)  
**Line 5 new phonemes:** [ʃ], [v], [eɑ]  
**Line 5 pure assembly words:** ÞREATUM  

**Cumulative after line 5:**
- 21 words reconstructed
- 32 phonemes verified
- 5 lines complete

---

## OUTPUT FILES

| File | Description |
|---|---|
| `threatum_dry.wav` | Full word, no reverb, 145 Hz |
| `threatum_hall.wav` | Full word, hall reverb RT60=2.0s |
| `threatum_slow.wav` | Full word, 4× time-stretched |
| `threatum_performance.wav` | 110 Hz pitch, dil=2.5, hall |

---

## NEW PHONEMES ADDED THIS WORD

None. Pure assembly.

**32 phonemes verified.**

---

## CUMULATIVE LINE STATUS

| Line | Text | Words | New phonemes | Status |
|---|---|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | 1–5 | 18 | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | 6–8 | 6 | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | 9–13 | 4 | ✓ complete |
| 4 | *þæt wæs gōd cyning* | 14–17 | 2 | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | 18–21 | 3 | ✓ complete |

---

## PHONEME INVENTORY
*All verified phonemes — 32 total:*

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

**32 verified.**  
**Remaining gaps: [p], [b], [iː],**  
**[æː], [eːɑ], [eo], [eːo], [ɣ].**  
**8 phonemes remaining.**

---

## NEXT: LINE 6

```
mongum mǣgþum meodosetla ofteah
[moŋɡum  mæːɣθum  meodosetlɑ  ofteɑx]
```

**New phonemes in line 6:**

| Word | Phoneme | Description |
|---|---|---|
| MǢGÞUM | [æː] | long open front unrounded |
| MǢGÞUM | [ɣ] | voiced velar fricative |
| MEODOSETLA | [eo] | short front-mid diphthong |

Three new phonemes.  
Line 6 word 1: MONGUM — zero new phonemes.  
Line 6 word 2: MǢGÞUM — [æː] and [ɣ].  
Line 6 word 3: MEODOSETLA — [eo].  
Line 6 word 4: OFTEAH — zero new phonemes.

---

*ÞREATUM [θreɑtum] verified.*  
*Zero new phonemes.*  
*Line 5 complete. 21 words. 32 phonemes.*  
*Next: LINE 6 — mongum mǣgþum meodosetla ofteah.*
