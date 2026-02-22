# ÐĀ — RECONSTRUCTION EVIDENCE
**Old English:** ðā  
**IPA:** [ðɑː]  
**Meaning:** then, at that time / those (demonstrative pronoun)  
**Source:** Beowulf, line 3, word 2 (overall word 10)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v3  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  Ð fricative   ✓ PASS
D2  Ā long vowel  ✓ PASS
D3  Full word     ✓ PASS
D4  Perceptual    LISTEN
```

Total duration: **220 ms** (9702 samples at 44100 Hz)  
Three reconstruction versions to resolve
voiced fricative synthesis.  
Clean pass on v3.

---

## VERSION HISTORY

| Recon version | Change |
|---|---|
| v1 | Initial parameters. D1 FAIL: voicing 0.1642, centroid 4090 Hz. |
| v2 | Raised DH_VOICE_GAIN 0.45→0.80, lowered DH_NOISE_GAIN 0.22→0.12, lowered DH_NOISE_CF 3800→3000, narrowed BW 2500→1800, added mid-band voiced component 200–1500 Hz. D1 FAIL: voicing 0.1911. Centroid correct at 3116 Hz. Voicing still insufficient. |
| v3 | Root cause found: rosenberg_pulse uses np.diff — differencing suppresses low-frequency fundamental. LP filter at 800 Hz passed harmonics but autocorrelation could not find 145 Hz peak through differentiated signal. Fix: new rosenberg_pulse_raw() — undifferenced Rosenberg pulse with strong fundamental at 145 Hz. LP cutoff raised 800→1200 Hz. Mid-band component removed — redundant. D1 PASS: voicing 0.7883. |

| Diag version | Change |
|---|---|
| v1 | Single diagnostic version. No changes required — failures resolved in reconstruction. |

---

## PHONEME RECORD

### Ð → [ð] — voiced dental fricative
New phoneme. The voiced counterpart of [θ].
Same place of articulation — tongue tip
at upper teeth — opposite voicing.

This is the *th* in Modern English
*the*, *this*, *that*, *there*, *them*,
*they*, *though*, *then*.

Old English [ð] survived into Modern
English essentially unchanged in these
high-frequency function words. It is
one of the few Old English sounds that
did not shift, weaken, or disappear
over 1300 years. When you say "the"
you are producing the same sound that
an Anglo-Saxon poet produced.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be > 0.40) | 0.7883 | 0.40–1.0 | PASS |
| RMS level | 0.2931 | 0.005–0.80 | PASS |
| Frication centroid (400–8000 Hz) | 1846 Hz | 800–4000 Hz | PASS |

**Parameters (v3):**
- Noise CF: 3000 Hz, BW: 1800 Hz
- Noise gain: 0.12
- Voice gain: 0.80
- Voice source: undifferenced Rosenberg pulse
- LP cutoff: 1200 Hz
- Duration: 70 ms

**The undifferenced pulse discovery:**

This word required three reconstruction
versions because of a non-obvious
interaction between the Rosenberg pulse
generator and the voicing measurement.

The standard rosenberg_pulse() function
applies np.diff to the raw glottal pulse.
This differentiation operation is correct
for vowel synthesis — it produces the
natural spectral tilt of the voice source
(6 dB/octave roll-off). But differentiation
suppresses the low-frequency fundamental.
The 145 Hz fundamental is weak after
differencing.

The autocorrelation voicing measurement
looks for periodicity in the 80–400 Hz
range. With a weak 145 Hz component,
the autocorrelation peak was marginal
(0.19) even with high voice gain.

The fix: rosenberg_pulse_raw() returns
the undifferenced pulse — the raw
glottal waveform before differentiation.
This has a strong 145 Hz fundamental.
Low-pass filtered to 1200 Hz, it
produces a voicing bar with a clear
periodic structure that the autocorrelation
finds immediately (0.79).

This is the correct synthesis approach
for voiced fricatives: the voicing bar
in natural [ð] is produced by periodic
glottal pulses, not by filtered
differentiated pulses.

rosenberg_pulse_raw() is now a permanent
addition to the synthesis toolkit for
use in all voiced fricatives: [ð], [v],
[ɣ], [z] (if present in the corpus).

**[θ] vs [ð] contrast — confirmed by measurement:**

| Phoneme | Voicing score | Centroid | Type |
|---|---|---|---|
| [θ] | 0.1187–0.1461 | 4100–4340 Hz | voiceless |
| [ð] | 0.7883 | 1846 Hz | voiced |

Voicing scores are completely non-overlapping.
The distinction is unambiguous in measurement.

Centroid difference: [θ] at ~4200 Hz,
[ð] at ~1846 Hz — a difference of ~2350 Hz.
This is expected. The voicing source
concentrates energy in the low-frequency
harmonics (145, 290, 435 Hz etc.) and
the LP-filtered voicing bar dominates
the spectral centroid measurement,
pulling it far below the dental
frication noise centroid.

The [ð] centroid is lower than [x]
(~2750 Hz) and [θ] (~4200 Hz) — not
because the place is more posterior
(it is not — [ð] is dental, [x] is
velar) but because the voicing energy
dominates the centroid calculation.
This is a measurement artifact of
centroid-based place identification
when voicing is present.

**Implication for future voiced fricatives:**
Centroid alone is not a reliable place
indicator for voiced fricatives.
The voicing score is the primary
diagnostic. The centroid confirms
that voicing energy is present and
pulling the spectrum low.

---

### Ā — long open back [ɑː]
Third instance. Previously verified
in GĀR-DENA (D2) and GĀR-DENA compound.
Parameters identical throughout.
Word-final position here — longer
decay envelope (fade from 85% of segment).

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7998 | 0.65–1.0 | PASS |
| Duration | 150 ms | 120–200 ms | PASS |
| F1+F2 centroid (600–1400 Hz) | 852 Hz | 750–1050 Hz | PASS |

**Cross-instance [ɑː] consistency:**

| Word | F1+F2 centroid | Duration |
|---|---|---|
| GĀR-DENA | ~850 Hz | 150 ms |
| ÐĀ | 852 Hz | 150 ms |

Effectively identical. The [ɑː] phoneme
is fully stable and reproducible.

---

### Full word — D3

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2775 | 0.01–0.90 | PASS |
| Duration | 220 ms | 150–400 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| Ð | [ð] | 70 ms | voiced dental fricative |
| Ā | [ɑː] | 150 ms | long vowel word-final |

The long vowel at 150 ms is more than
twice the duration of the fricative at
70 ms. The word is vowel-dominant in
duration — the [ɑː] carries most of
the acoustic energy and duration.

---

## SYNTHESIS ARCHITECTURE UPDATE

This word adds rosenberg_pulse_raw()
to the permanent toolkit:

```
rosenberg_pulse()     — differenced
                        for vowels
                        6 dB/octave tilt
                        weak fundamental

rosenberg_pulse_raw() — undifferenced
                        for voiced fricatives
                        strong fundamental
                        flat spectrum before LP
```

All future voiced fricatives ([v], [ɣ], [z])
will use rosenberg_pulse_raw() for the
voicing bar component.

---

## PHONETIC AND HISTORICAL NOTE

**The [θ]/[ð] distinction in Old English**

Old English used two letters for the
dental fricatives:
- **þ** (thorn): used for both [θ] and [ð]
  in early manuscripts
- **ð** (eth): used specifically for [ð]
  in later manuscripts, though usage
  was inconsistent

The distinction between voiced and
voiceless dental fricatives was
phonemic in Old English — minimal
pairs existed. The two sounds were
not interchangeable.

In Modern English both [θ] and [ð]
survive but their distribution has
become largely predictable:
- [θ] in content words: *think*, *thin*,
  *thick*, *three*, *through*
- [ð] in function words: *the*, *this*,
  *that*, *them*, *there*, *though*

This distribution was not as fixed
in Old English — voicing was more
phonemically contrastive.

**ðā specifically:**
This word functions as both a temporal
adverb (*then*, *at that time*) and a
demonstrative pronoun (*those*). In line 3
of Beowulf it is the temporal adverb:
*hu ðā æþelingas* — *how then those
princes*. The [ðɑː] pronunciation is
identical in both uses.

The Modern English descendant is
ambiguous: *the* (definite article,
from OE *þe*) and the archaic *thaw*
(process, unrelated) — *ðā* as a
temporal adverb became *then* through
a different sound change pathway.

---

## VOICED FRICATIVE INVENTORY — INITIATED

| Phoneme | Place | Status |
|---|---|---|
| [ð] | dental | ✓ verified here |
| [v] | labiodental | pending |
| [ɣ] | velar | pending |
| [z] | alveolar | rare in OE |

First voiced fricative verified.
Synthesis pattern established for all
subsequent voiced fricatives:
frication noise + rosenberg_pulse_raw()
low-pass filtered.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `tha_dry.wav` | Full word, no reverb, 145 Hz |
| `tha_hall.wav` | Full word, hall reverb RT60=2.0s |
| `tha_slow.wav` | Full word, 4× time-stretched |
| `tha_performance.wav` | 110 Hz pitch, dil=2.5, hall |
| `tha_dh_isolated.wav` | [ð] fricative only, 4× slow |

---

## NEW PHONEMES ADDED THIS WORD

| Phoneme | Description | Key parameter |
|---|---|---|
| [ð] | voiced dental fricative | voicing 0.79, centroid 1846 Hz — use rosenberg_pulse_raw() for voicing bar |

---

## CUMULATIVE LINE STATUS

| Line | Words | Status |
|---|---|---|
| 1: *Hwæt wē Gār-Dena in gēar-dagum* | 5 | ✓ complete |
| 2: *Þēod-cyninga, þrym gefrūnon* | 3 | ✓ complete |
| 3: *hu ðā æþelingas ellen fremedon* | hu ✓  ðā ✓ | in progress |

---

## PHONEME INVENTORY
*All verified phonemes as of this word:*

| Phoneme | Description | First word | Instances |
|---|---|---|---|
| [ʍ] | voiceless labio-velar fricative | HWÆT | 1 |
| [æ] | open front unrounded | HWÆT | 1 |
| [t] | voiceless alveolar stop | HWÆT | 1 |
| [w] | voiced labio-velar approximant | WĒ | 1 |
| [eː] | long close-mid front | WĒ | 3 |
| [ɡ] | voiced velar stop | GĀR-DENA | 4 |
| [ɑː] | long open back | GĀR-DENA | 3 |
| [r] | alveolar trill | GĀR-DENA | 4 |
| [d] | voiced alveolar stop | GĀR-DENA | 3 |
| [e] | short close-mid front | GĀR-DENA | 2 |
| [n] | voiced alveolar nasal | GĀR-DENA | 7 |
| [ɑ] | short open back | GĀR-DENA | 5 |
| [ɪ] | short near-close front | IN | 2 |
| [u] | short close back rounded | GĒAR-DAGUM | 2 |
| [m] | voiced bilabial nasal | GĒAR-DAGUM | 2 |
| [θ] | voiceless dental fricative | ÞĒOD-CYNINGA | 3 |
| [o] | short close-mid back rounded | ÞĒOD-CYNINGA | 2 |
| [k] | voiceless velar stop | ÞĒOD-CYNINGA | 1 |
| [y] | short close front rounded | ÞĒOD-CYNINGA | 2 |
| [ŋ] | voiced velar nasal | ÞĒOD-CYNINGA | 1 |
| [j] | palatal approximant | GEFRŪNON | 1 |
| [f] | voiceless labiodental fricative | GEFRŪNON | 1 |
| [uː] | long close back rounded | GEFRŪNON | 1 |
| [x] | voiceless velar fricative | HU | 1 |
| [ð] | voiced dental fricative | ÐĀ | 1 |

**25 distinct phonemes verified.**

---

*ÐĀ [ðɑː] verified.*  
*Next: ÆÞELINGAS [æθeliŋɡɑs] — line 3, word 3.*
