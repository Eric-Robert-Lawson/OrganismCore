# WEARÐ — RECONSTRUCTION EVIDENCE
**Old English:** wearð  
**IPA:** [weɑrθ]  
**Meaning:** became, came to be (past tense of weorþan)  
**Beowulf:** Line 7, word 5 (overall word 30)  
**New phonemes:** none — pure assembly  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  W approximant           ✓ PASS
D2  EA F2 movement          ✓ PASS
D3  EA F1 movement          ✓ PASS
D4  R trill                 ✓ PASS
D5  TH fricative            ✓ PASS
D6  Full word               ✓ PASS
D7  Perceptual              LISTEN
```

Total duration: **270 ms** (11906 samples at 44100 Hz) — diagnostic  
Performance duration: **675 ms** (29766 samples) — 110 Hz, dil 2.5, hall  
Clean first run. Six for six. Zero failures.

---

## VERSION HISTORY

| Version | Change | Result |
|---|---|---|
| v1 | Initial parameters. R_TRILL_DEPTH 0.40 from outset. | ALL PASS |

---

## TRILL DEPTH — ESTABLISHED BASELINE

R_TRILL_DEPTH 0.40 used from the outset.
Voicing result: **0.5923** — identical to
ǢREST v2. This is now the established
trill score at depth 0.40.

| Word | Context | Depth | Voicing | Result |
|---|---|---|---|---|
| GĀR-DENA | various | 0.55 | 0.6818–0.8608 | PASS |
| ǢREST v1 | post-[æː] | 0.55 | 0.4320 | FAIL |
| ǢREST v2 | post-[æː] | 0.40 | 0.5923 | PASS |
| WEARÐ v1 | post-[eɑ] | 0.40 | 0.5923 | PASS |

**Inventory update:**
R_TRILL_DEPTH 0.40 is the verified
value for all subsequent words.
The 0.55 value from early GĀR-DENA
reconstructions produced higher scores
in those contexts but failed in
post-long-vowel context.
0.40 is conservative and reliable.
All future [r] uses: TRILL_DEPTH 0.40.

---

## [eɑ] DIPHTHONG — CROSS-WORD CONSISTENCY

The [eɑ] diphthong has now been
measured in three words:

| Word | F2 onset | F2 offset | F2 delta | F1 delta |
|---|---|---|---|---|
| SCEAÞENA | ~1851 Hz | ~1131 Hz | ~720 Hz ↓ | ~250 Hz ↑ |
| ĒAGE | 1851 Hz | 1115 Hz | 737 Hz ↓ | 281 Hz ↑ |
| WEARÐ | 1849 Hz | 1096 Hz | 753 Hz ↓ | 277 Hz ↑ |

**F2 onset: 1849–1851 Hz across all three.**
Near-identical. Deterministic synthesis
confirmed. The onset formant target
is the same regardless of preceding
consonant — [θ] in SCEAÞENA, [ɣ] in
ĒAGE, [w] in WEARÐ. Coarticulation
at the onset boundary does not
significantly shift the F2 onset
centroid measurement.

**F1 delta: 250–281 Hz rising.**
Consistent jaw-opening trajectory
across all three instances.
The [eɑ] diphthong is phonemically
stable. F1 rises. Jaw opens.
Not [eo].

---

## PHONEME RECORD

### W — voiced labio-velar approximant [w]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7506 | >= 0.50 | PASS |
| RMS level | 0.3226 | 0.005–0.80 | PASS |

Voicing 0.7506 — consistent with
WĒ verification. The [w] is stable.

---

### EA — short front-back diphthong [eɑ]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7624 | >= 0.50 | PASS |
| F2 onset | 1849 Hz | 1500–2200 Hz | PASS |
| F2 offset | 1096 Hz | 800–1400 Hz | PASS |
| F2 delta | 753 Hz ↓ | 400–1000 Hz | PASS |
| F1 delta | 277 Hz ↑ | 100–400 Hz | PASS |

---

### R — alveolar trill [r]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.5923 | >= 0.50 | PASS |
| RMS level | 0.1976 | 0.005–0.80 | PASS |
| TRILL_DEPTH | 0.40 | — | verified |

---

### TH — voiceless dental fricative [θ]

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1402 | <= 0.35 | PASS |
| RMS level | 0.0901 | 0.001–0.50 | PASS |

Known limitation: centroid sits high —
perceptually proximate to [ʃ].
Passes voicing and RMS diagnostics.
Same limitation as PÆÞ, ÞĒOD-CYNINGA.

---

### Full word — D6

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2460 | 0.01–0.90 | PASS |
| Duration (diagnostic) | 270 ms | 220–380 ms | PASS |
| Duration (performance) | 675 ms | — | — |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| W | [w] | 55 ms | voiced labio-velar approximant |
| EA | [eɑ] | 80 ms | short front-back diphthong |
| R | [r] | 65 ms | alveolar trill |
| TH | [θ] | 70 ms | voiceless dental fricative |

Total: 270 ms. Four segments.

**Voicing profile:**

```
[w]   0.7506  voiced   — approximant onset
[eɑ]  0.7624  voiced   — diphthong nucleus
[r]   0.5923  voiced   — trill
[θ]   0.1402  voiceless— dental fricative close
```

Three voiced segments, one voiceless
close. The word is predominantly voiced.
[θ] closes it into silence — the
becoming ends in stillness.

---

## OUTPUT FILES

| File | Parameters | Duration |
|---|---|---|
| `diag_wearth_full.wav` | dry, 145 Hz, dil 1.0 | 270 ms |
| `diag_wearth_hall.wav` | hall RT60=2.0s, 145 Hz, dil 1.0 | 270 ms |
| `diag_wearth_slow.wav` | 4× OLA stretch | ~1080 ms |
| `diag_wearth_perf.wav` | hall RT60=2.0s, 110 Hz, dil 2.5 | 675 ms |

---

## ETYMOLOGICAL NOTE

**wearð — became:**

Past tense of *weorþan* —
to become, to happen, to come to be.
One of the most fundamental verbs
in OE. Used as an auxiliary for
passive constructions and as a
main verb meaning pure becoming.

*Wearð* appears in the most
significant position in line 7:
the verb that closes the clause
*syþðan ǣrest wearð* —
since it first came to be.

**ModE descendants:**

*Weorþan* did not survive as a
main verb into Modern English —
it was displaced by *become*
(from OE *becuman*). But it
survives in:

- **worth** — from OE *weorþ*
  (adjective/noun: value, worthy).
  Same root. The noun form of
  the same word family.

- **-ward / -wards** — direction
  suffixes (toward, backward).
  From OE *-weard* — turned toward,
  becoming. Same root. Movement
  toward a state = becoming.

- **weird** — from OE *wyrd* —
  fate, what becomes. The
  nominalized form of *weorþan*.
  What happens. What comes to be.
  *Wyrd* became *weird* — fate
  became strangeness — because
  fate was considered uncanny.

The verb *wearð* — became —
lives on in English as
*worth*, *weird*, and *-ward*.
Three different words, all
from the same root: becoming.

**The PIE root:**

PGmc *\*werþaną* — to turn,
to become. From PIE *\*wert-* —
to turn. The same root as Latin
*vertere* (to turn), *versus*,
*universe* (turned into one),
*anniversary* (year-turning).

*Wearð* and *anniversary* share
a root. The becoming and the
turning of the year.

---

## LINE 7 — COMPLETE

```
egsode eorlas, syþðan ǣrest wearð
[eɡsode eorlas syθðɑn æːrest weɑrθ]

He terrified warriors, since first
it came to be.
```

| Word | IPA | Status | Iterations |
|---|---|---|---|
| egsode | [eɡsode] | ✓ | 1 |
| eorlas | [eorlas] | ✓ | 1 |
| syþðan | [syθðɑn] | ✓ | 1 |
| ǣrest | [æːrest] | ✓ | 2 |
| wearð | [weɑrθ] | ✓ | 1 |

Line 7: five words. Five verified.
Four first-run passes.
One failure resolved (ǢREST [r] trill depth).

---

## LINES 1–7 STATUS

| Line | Text | Status |
|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | ✓ complete |
| 4 | *þæt wæs gōd cyning* | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | ✓ complete |
| 6 | *mongum mǣgþum meodosetla ofteah* | ✓ complete |
| 7 | *egsode eorlas, syþðan ǣrest wearð* | ✓ complete |
| 8 | *feasceaft funden, hē þæs frōfre gebād* | pending — [b] arrives |

**Seven lines complete.**
**One line remaining.**
**39 phonemes verified.**
**One pending: [b] — line 8 GEBĀD.**

---

*WEARÐ [weɑrθ] verified.*  
*Zero new phonemes. 39 phonemes verified.*  
*Clean first run. Six for six.*  
*R_TRILL_DEPTH 0.40 confirmed as established baseline.*  
*[eɑ] F2 onset 1849 Hz — consistent across SCEAÞENA, ĒAGE, WEARÐ.*  
*Performance: 675 ms, 110 Hz, dil 2.5, hall.*  
*Line 7 complete. Seven of eight lines verified.*  
*Next: line 8 — feasceaft funden, hē þæs frōfre gebād.*  
*[b] arrives in GEBĀD. 40th phoneme. Inventory closes.*
