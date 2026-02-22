# EGSODE — RECONSTRUCTION EVIDENCE
**Old English:** egsode  
**IPA:** [eɡsode]  
**Meaning:** terrified, intimidated (past tense 3rd singular of *egsian*)  
**Source:** Beowulf, line 7, word 1 (overall word 26)  
**Date verified:** February 2026  
**Diagnostic version:** v1**  
**Reconstruction version:** v2  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  E vowel initial       ✓ PASS
D2  G stop                ✓ PASS
D3  S fricative           ✓ PASS
D4  GS transition         ✓ PASS
D5  O vowel               ✓ PASS
D6  D stop                ✓ PASS
D7  E vowel final         ✓ PASS
D8  Full word             ✓ PASS
D9  Perceptual            LISTEN
```

Total duration: **360 ms** (15874 samples at 44100 Hz)  
Fixed on second attempt. Eight for eight.  
Zero new phonemes. Pure assembly.

---

## VERSION HISTORY

| Version | Change | D4 result |
|---|---|---|
| v1 | Initial parameters. Murmur gain 0.35, VOT noise gain 0.25 | FAIL — [ɡ] voicing 0.0008 |
| v2 | Murmur gain → 0.65, VOT noise gain → 0.05 | PASS — [ɡ] voicing 0.7940 |

---

## ITERATION RECORD — v1 FAILURE ANALYSIS

**D4 failure data:**

```
v1:
  [ɡ] voicing: 0.0008   ← effectively zero
  [s] voicing: 0.1356
  separation:  -0.1348  ← negative — FAIL
```

**Root cause:**

The v1 [ɡ] synthesiser had three phases:
closure murmur, burst noise, VOT noise.
The autocorrelation voicing measure
samples the middle 50% of the segment.
With murmur gain 0.35 and VOT noise
gain 0.25, the noise components
dominated the energy in the measurement
window. The murmur was physically
present but the autocorrelation found
aperiodic noise, not the pitch period.
Voicing reported as 0.0008.

The [s] voicing at 0.1356 exceeded
the [ɡ] voicing at 0.0008 —
the fricative appeared more voiced
than the stop. Separation was negative.

**This is the same class of failure
as [v] in SCEFING v1 and v2.**

In all three cases: a phoneme that
should be voiced was failing the
voicing diagnostic because noise
components in the synthesiser were
drowning the periodic source in the
autocorrelation measurement window.

The fix in all cases: reduce noise,
increase periodic signal amplitude.
The voicing is not in the noise.
The voicing is in the Rosenberg pulse.

**v2 fix parameters:**

| Parameter | v1 | v2 |
|---|---|---|
| Murmur gain | 0.35 | 0.65 |
| Murmur envelope onset | 0.4 | 0.8 |
| VOT noise gain | 0.25 | 0.05 |

Result: [ɡ] voicing 0.7940.
Separation 0.6644.

---

## PHONEME RECORD

### E — short close-mid front [e] initial
Word-initial. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6695 | 0.50–1.0 | PASS |
| F2 centroid (1500–2500 Hz) | 1875 Hz | 1600–2300 Hz | PASS |

---

### G — voiced velar stop [ɡ]
Post-vowel position. [e]→[ɡ].
Verified with v2 parameters.

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.0726 | 0.005–0.70 | PASS |
| Duration | 70 ms | 40–100 ms | PASS |

**[ɡ] voicing confirmed — v2:**

Murmur gain 0.65. Envelope onset 0.8.
The voiced closure murmur is now
dominant in the measurement window.
Autocorrelation finds the pitch period
at 145 Hz clearly.

---

### S — voiceless alveolar fricative [s]
Post-stop. [ɡ]→[s] cluster.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1296 | 0.0–0.35 | PASS |
| Centroid (4000–12000 Hz) | 7613 Hz | 5000–10000 Hz | PASS |

---

### D4 — [ɡs] voicing transition

| Measure | Value | Result |
|---|---|---|
| [ɡ] voicing | 0.7940 | voiced confirmed |
| [s] voicing | 0.1296 | voiceless confirmed |
| Separation | 0.6644 | PASS |

**[ɡs] — voiced into voiceless:**

The [ɡ] stop is fully voiced during
closure. At the burst, vocal fold
vibration ceases. The [s] that follows
is fully voiceless. The transition is
abrupt — 0.7940 to 0.1296 across the
segment boundary. The voicing contrast
is 0.6644 units — comparable to the
[ɣ]/[x] separation of 0.6253.

The [ɡs] cluster is phonetically
interesting: it requires the larynx
to devoice simultaneously with the
tongue dorsum releasing from the
velar closure and the tongue tip
forming the alveolar groove for [s].
Three articulatory events at near
the same moment. The synthesis
handles these as sequential
concatenated segments — a known
simplification.

---

### O — short close-mid back rounded [o]
Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6691 | 0.50–1.0 | PASS |
| F2 centroid (550–1100 Hz) | 748 Hz | 600–1000 Hz | PASS |

---

### D — voiced alveolar stop [d]
Medial position. [o]→[d]→[e].

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.0678 | 0.005–0.70 | PASS |
| Duration | 60 ms | 30–90 ms | PASS |

---

### E — short close-mid front [e] final
Word-final. Decay to silence.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6695 | 0.50–1.0 | PASS |
| F2 centroid (1500–2500 Hz) | 1875 Hz | 1600–2300 Hz | PASS |

Initial and final [e] instances
produce identical measurements —
deterministic synthesiser, same
parameters, same output.

---

### Full word — D8

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2299 | 0.01–0.90 | PASS |
| Duration | 360 ms | 330–560 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| E | [e] | 55 ms | short close-mid front |
| G | [ɡ] | 70 ms | voiced velar stop |
| S | [s] | 65 ms | voiceless alveolar fricative |
| O | [o] | 55 ms | short close-mid back rounded |
| D | [d] | 60 ms | voiced alveolar stop |
| E | [e] | 55 ms | short close-mid front |

Total: 360 ms. Six segments.

**Voicing profile:**

```
E    voiced    0.6695
G    voiced    0.7940
S    voiceless 0.1296
O    voiced    0.6691
D    voiced    —
E    voiced    0.6695
```

The [s] is the only voiceless segment.
It sits between two voiced stops —
[ɡ] before, [o] after — creating a
brief voiceless island in a largely
voiced word. The contrast is
perceptually sharp: the voiced
murmur of [ɡ] cuts off abruptly
at the [s] onset.

---

## CUMULATIVE VOICED STOP RECORD

With [ɡ] v2 confirmed, all voiced
stop voicing measurements updated:

| Stop | Word | Voicing | Version |
|---|---|---|---|
| [ɡ] | GĀR-DENA | — | pre-diagnostic |
| [d] | GĀR-DENA | — | pre-diagnostic |
| [ɡ] | EGSODE | 0.7940 | v2 |
| [d] | EGSODE | — | stops measured by RMS/duration |

The [ɡ] voicing measurement of 0.7940
is now the reference value for voiced
velar stop closure murmur. Future [ɡ]
instances will use the v2 parameters.

---

## ETYMOLOGICAL NOTE

**egsode — terrified:**

*Egesa* (noun) — terror, dread,
awe. *Egsian* (verb) — to terrify,
to cause dread. *Egsode* — past
tense third singular: he terrified.

The word carries more than military
defeat. *Egesa* is the dread that
precedes and follows violence —
the psychological weight of power.
Scyld did not merely defeat his
enemies. He made them afraid. That
fear was his instrument of control
across many tribes.

**Modern English descendants:**

- *eerie* — via Old Norse *agr*
  (frightening) from the same
  Proto-Germanic root. The sense
  of supernatural dread.

- *ugly* — via Old Norse *uggligr*
  (dreadful, to be dreaded) from
  the same root. Originally: that
  which causes dread, that which
  is frightening. The modern sense
  of physical unattractiveness is
  a narrowing from the original
  sense of causing fear.

The [eɡ] onset of *egsode* —
front vowel followed by voiced
velar stop — is not preserved
in either modern descendant.
Both went through Norse rather
than directly through OE.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `egsode_dry.wav` | Full word, no reverb, 145 Hz, v2 |
| `egsode_hall.wav` | Full word, hall reverb RT60=2.0s, v2 |
| `egsode_slow.wav` | Full word, 4× time-stretched, v2 |
| `egsode_performance.wav` | 110 Hz pitch, dil=2.5, hall, v2 |

---

## NEW PHONEMES ADDED THIS WORD

None. Pure assembly.

**35 phonemes verified.**

---

## LESSON RECORDED

**Voiced stop murmur must dominate
the autocorrelation window.**

This is the third instance of the
same failure class:

| Word | Phoneme | Failure | Fix |
|---|---|---|---|
| SCEFING | [v] | noise masked voicing | pure voiced source |
| EGSODE | [ɡ] | VOT noise masked murmur | murmur gain up, VOT noise down |

Pattern: any synthesised phoneme
that mixes a periodic voiced source
with aperiodic noise risks failing
the autocorrelation voicing diagnostic
if the noise gain is too high relative
to the periodic source.

Rule for all future voiced stops:
murmur gain >= 0.60, VOT noise
gain <= 0.10. The voicing is in
the murmur. The murmur must be heard.

---

## CUMULATIVE LINE STATUS

| Line | Text | Words | Status |
|---|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | 1–5 | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | 6–8 | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | 9–13 | ✓ complete |
| 4 | *þæt wæs gōd cyning* | 14–17 | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | 18–21 | ✓ complete |
| 6 | *mongum mǣgþum meodosetla ofteah* | 22–25 | ✓ complete |
| 7 | *egsode eorlas, syþðan ǣrest wearð* | 26–30 | egsode ✓ — in progress |

---

*EGSODE [eɡsode] verified.*  
*v1 failed D4 — [ɡ] murmur masked by VOT noise.*  
*v2 fixed — murmur gain 0.65, VOT noise 0.05.*  
*[ɡ] voicing 0.7940. Separation 0.6644.*  
*Zero new phonemes. 35 phonemes verified.*  
*Next: EORLAS [eorlas] — line 7, word 2. Zero new phonemes.*
