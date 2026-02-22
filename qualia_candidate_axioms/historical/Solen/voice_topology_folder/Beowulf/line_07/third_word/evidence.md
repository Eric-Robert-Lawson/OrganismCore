# SYÞÐAN — RECONSTRUCTION EVIDENCE
**Old English:** syþðan  
**IPA:** [syθðɑn]  
**Meaning:** since, after, when (conjunction/adverb)  
**Source:** Beowulf, line 7, word 3 (overall word 28)  
**Date verified:** February 2026  
**Diagnostic version:** v1  
**Reconstruction version:** v1  

---

## RESULT

```
ALL NUMERIC CHECKS PASSED
D1  S fricative           ✓ PASS
D2  Y vowel               ✓ PASS
D3  TH fricative          ✓ PASS
D4  DH fricative          ✓ PASS
D5  THDH transition       ✓ PASS
D6  A vowel               ✓ PASS
D7  N nasal               ✓ PASS
D8  Full word             ✓ PASS
D9  Perceptual            LISTEN
```

Total duration: **375 ms** (16536 samples at 44100 Hz)  
Clean first run. Eight for eight.  
Zero new phonemes. Pure assembly.

---

## VERSION HISTORY

| Version | Change |
|---|---|
| v1 | Initial parameters. All eight numeric checks passed on first run. |

---

## PHONEME RECORD

### S — voiceless alveolar fricative [s]
Word-initial. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1144 | 0.0–0.35 | PASS |
| Centroid (4000–12000 Hz) | 7646 Hz | 5000–10000 Hz | PASS |

---

### Y — short close front rounded [y]
Post-[s] position.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6680 | 0.50–1.0 | PASS |
| F2 centroid (1000–2000 Hz) | 1418 Hz | 1100–1900 Hz | PASS |

**[y] cross-instance stability:**

| Word | F2 centroid | Context |
|---|---|---|
| ÞĒOD-CYNINGA | ~1418 Hz | medial |
| SYÞÐAN | 1418 Hz | post-[s] |

Identical. The rounded front vowel
is fully stable across contexts.
F2 at 1418 Hz — the acoustic
signature of rounding: same tongue
height as [i] (~2300 Hz F2) but
F2 pulled down ~900 Hz by lip
rounding. The rounding is measurable
and consistent.

---

### TH — voiceless dental fricative [θ]
Pre-[ð] position. First element
of [θð] cluster.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be low) | 0.1212 | 0.0–0.35 | PASS |
| RMS level | 0.0749 | 0.001–0.50 | PASS |

---

### DH — voiced dental fricative [ð]
Post-[θ] position. Second element
of [θð] cluster.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing (must be high) | 0.7618 | 0.35–1.0 | PASS |
| RMS level | 0.2297 | 0.005–0.80 | PASS |

---

### D5 — [θð] voicing transition

| Measure | Value | Result |
|---|---|---|
| [θ] voicing | 0.1212 | voiceless confirmed |
| [ð] voicing | 0.7618 | voiced confirmed |
| Separation | 0.6406 | PASS |

**The [θð] cluster — most minimal
contrast in the inventory:**

The tongue does not move between
[θ] and [ð]. Both are dental
fricatives — tongue tip at upper
teeth, narrow gap, airflow
through the dental aperture.
The only change is laryngeal:
vocal folds inactive during [θ],
vocal folds vibrating during [ð].

This is the minimum possible
phonemic contrast — one binary
feature: [−voice] → [+voice].
No place change. No manner change.
No height change. No backness
change. One switch.

The separation of 0.6406 voicing
units confirms the instrument
captures this contrast cleanly.

**Voiced fricative voicing
scores — full inventory:**

| Phoneme | Voicing | Word |
|---|---|---|
| [ð] | 0.7618 | SYÞÐAN |
| [v] | 0.7618 | SCEFING |
| [ɣ] | 0.7607 | MǢGÞUM |

Remarkable convergence. All three
voiced fricatives produce voicing
scores within 0.0011 of each other.
0.7607 — 0.7618 — 0.7618.

This is not coincidence. It is
a consequence of the synthesis
architecture. All three use the
same strategy: pure Rosenberg
pulse source, AM modulation,
no noise. The AM modulation
parameters differ slightly
between phonemes but the
autocorrelation measure is
primarily sensitive to the
pitch periodicity of the source,
not to the AM depth or rate.
All three use the same source.
All three produce the same
voicing score.

The convergence confirms the
architecture is correct and
consistent. It also reveals
the limitation: the voicing
score does not distinguish
between [ð], [v], and [ɣ].
Place of articulation is encoded
in the formant filters, not in
the voicing measure. The
distinctiveness of these phonemes
is in their spectral shape, not
in their periodicity.

**[θ]/[ð] voiceless/voiced pair —
cross-instance:**

| Phoneme | Voicing | Separation |
|---|---|---|
| [θ] | 0.1212 | — |
| [ð] | 0.7618 | 0.6406 |

Comparable to [x]/[ɣ] separation
of 0.6253. The dental pair is
slightly more separated than
the velar pair. Both are fully
unambiguous.

---

### A — short open back [ɑ]
Post-[ð] position. Fully stable.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.6679 | 0.50–1.0 | PASS |
| F2 centroid (800–1500 Hz) | 1085 Hz | 900–1400 Hz | PASS |

---

### N — voiced alveolar nasal [n]
Word-final. Decay to silence.

| Measure | Value | Target | Result |
|---|---|---|---|
| Voicing | 0.7785 | 0.65–1.0 | PASS |
| RMS (nasal murmur) | 0.2229 | 0.005–0.25 | PASS |

---

### Full word — D8

| Measure | Value | Target | Result |
|---|---|---|---|
| RMS level | 0.2318 | 0.01–0.90 | PASS |
| Duration | 375 ms | 340–560 ms | PASS |

**Segment sequence:**

| Segment | Phoneme | Duration | Type |
|---|---|---|---|
| S | [s] | 65 ms | voiceless alveolar fricative |
| Y | [y] | 55 ms | short close front rounded |
| TH | [θ] | 70 ms | voiceless dental fricative |
| DH | [ð] | 70 ms | voiced dental fricative |
| A | [ɑ] | 55 ms | short open back |
| N | [n] | 60 ms | voiced alveolar nasal |

Total: 375 ms. Six segments.

**Voicing profile:**

```
S    voiceless  0.1144
Y    voiced     0.6680
TH   voiceless  0.1212
DH   voiced     0.7618
A    voiced     0.6679
N    voiced     0.7785
```

Alternating voiceless/voiced pattern
at the word onset: S−Y−TH−DH.
The [θð] cluster sits at the centre —
two fricatives, same place, one
voiceless then one voiced. After
the cluster the word is entirely
voiced to the end: DH−A−N.

---

## INVENTORY AUDIT — HONEST RECORD

An internal check was conducted
before this evidence file was
written. The earlier claim that
the full phoneme inventory would
be complete by lines 9–10 was
reviewed against the actual
text of Beowulf word by word.

**The claim was wrong.**

**Revised first-occurrence map:**

| Phoneme | First occurrence | Line | Word |
|---|---|---|---|
| [b] | *gebād* | 8 | *he þæs frōfre gebād* |
| [iː] | *þrītig* | approx 16 | *þrītig þegna* |
| [eːo] | *þēod* long diphthong | approx 15–20 | multiple candidates |
| [eːɑ] | *ēacen* or similar | approx 20–25 | needs word-by-word scan |
| [p] | *þrēap* or *camp* | approx 25+ | rare in native OE |

**[p] is the problem phoneme.**

[p] is genuinely rare in native
OE vocabulary. It appears mainly
in loanwords (Latin, Norse) and
in specific clusters. A full
word-by-word scan of lines 8–40
is needed to locate its first
occurrence precisely.

**Corrected claim:**

- [b]: line 8 — confirmed
- [iː]: approximately line 16
- [eːo], [eːɑ]: approximately lines 15–25
- [p]: possibly lines 25–40

Full inventory completion: approximately
lines 25–30, not lines 9–10.

The audit found the error.
The error is recorded.
The scan continues word by word
and will reach these phonemes
when the text reaches them.

---

## ETYMOLOGICAL NOTE

**syþðan — since, after:**

One of the most frequent words
in OE poetry. Appears dozens of
times in Beowulf alone. It marks
temporal sequence — the moment
after which a new state of affairs
holds. In poetry it often marks
the decisive event: *syþðan ǣrest
wearð* — since first it came to be.

**Compound etymology:**

*sið* (noun) — journey, time,
occasion. *þan* — instrumental
case suffix, meaning roughly
'by that' or 'from that'.
Literally: *from that journey* —
*from that occasion* — *since that
time*.

The word collapsed through Middle
English:

```
OE  syþþan  [syθθɑn]
ME  siþen   [siθen]
ME  sithen  [siθen]
ModE since  [sɪns]
```

The [y] → [i] shift: OE rounded
front [y] unrounded to [i] in
Middle English — the same change
that affected all OE [y] vowels.
The [θθ] → [θ] → [s] shift:
dental fricative weakened and
eventually merged with [s] in
some dialects. The final [n]
was lost.

ModE *since* retains only the
consonant skeleton of *syþðan* —
[s...ns] from [s...ðɑn]. The
rounded front vowel, the dental
fricatives, the open back vowel —
all gone. The function word
survives; the phonological body
is almost entirely replaced.

---

## OUTPUT FILES

| File | Description |
|---|---|
| `sython_dry.wav` | Full word, no reverb, 145 Hz |
| `sython_hall.wav` | Full word, hall reverb RT60=2.0s |
| `sython_slow.wav` | Full word, 4× time-stretched |
| `sython_thDH_only.wav` | [θð] cluster isolated, 4× slow |

---

## NEW PHONEMES ADDED THIS WORD

None. Pure assembly.

**35 phonemes verified.**

---

## VOICED FRICATIVE CONVERGENCE
*Recorded for the instrument log:*

All three voiced fricatives in the
inventory produce voicing scores
within 0.0011 of each other:

| Phoneme | Voicing | Architecture |
|---|---|---|
| [v] | 0.7618 | Rosenberg + AM |
| [ð] | 0.7618 | Rosenberg + AM |
| [ɣ] | 0.7607 | Rosenberg + AM |

Same source. Same diagnostic.
Same result. The voicing measure
confirms periodicity, not place.
Place is in the filters.
This is correct behaviour.

---

## CUMULATIVE LINE STATUS

| Line | Text | Words | Status |
|---|---|---|---|
| 1 | *Hwæt wē Gār-Dena in gēar-dagum* | 1–5 | ✓ complete |
| 2 | *Þēod-cyninga, þrym gefrūnon* | 6–8 | ✓ complete |
| 3 | *hu ðā æþelingas ellen fremedon* | 9–13 | ��� complete |
| 4 | *þæt wæs gōd cyning* | 14–17 | ✓ complete |
| 5 | *Scyld Scefing sceaþena þreatum* | 18–21 | ✓ complete |
| 6 | *mongum mǣgþum meodosetla ofteah* | 22–25 | ✓ complete |
| 7 | *egsode eorlas, syþðan ǣrest wearð* | 26–30 | egsode ✓  eorlas ✓  syþðan ✓ — two words remaining |

---

*SYÞÐAN [syθðɑn] verified.*  
*[θð] transition confirmed — separation 0.6406.*  
*Most minimal contrast in inventory: same place, voicing only.*  
*Voiced fricative convergence noted: [v]/[ð]/[ɣ] all 0.7607–0.7618.*  
*Inventory completion claim corrected: lines 25–30, not 9–10.*  
*Next: ǢREST [æːrest] — line 7, word 4. Zero new phonemes.*
