# EVIDENCE — YAJÑASYA
## Vedic Sanskrit Reconstruction Project
## Rigveda 1.1.1 — Word 4
**February 2026**

---

## WORD

**yajñasya** — of the sacrifice
Rigveda 1.1.1, word 4.
Genitive singular of *yajña* — sacrifice,
the act of offering, the ritual that
constitutes the relationship between
the human and the divine.

The word that tells what kind of priest
Agni is. Not merely a household fire.
The priest of the sacrifice itself.

---

## IPA TRANSCRIPTION

```
[jɑɟɲɑsjɑ]
```

**Segment sequence:**

```
J1  [j]   voiced palatal approximant   — tālavya antastha
A1  [ɑ]   short open central           — kaṇṭhya (verified AGNI)
JJ  [ɟ]   voiced palatal stop          — tālavya row 3
NY  [ɲ]   voiced palatal nasal         — tālavya row 5
A2  [ɑ]   short open central           — kaṇṭhya (verified AGNI)
S   [s]   voiceless dental sibilant    — dantya
J2  [j]   voiced palatal approximant   — tālavya antastha
A3  [ɑ]   short open central           — kaṇṭhya (verified AGNI)
```

**Syllable structure:**

```
YAJ — ÑA — SYA
[jɑɟ] — [ɲɑ] — [sjɑ]
```

---

## PHONEMES VERIFIED IN THIS WORD

| Phoneme | IPA | Devanāgarī | Śikṣā | Status |
|---|---|---|---|---|
| palatal approximant | [j] | य | tālavya antastha | **VERIFIED** |
| voiced palatal stop | [ɟ] | ज | tālavya row 3 | **VERIFIED** |
| voiced palatal nasal | [ɲ] | ञ | tālavya row 5 | **VERIFIED** |
| voiceless dental sibilant | [s] | स | dantya | **VERIFIED** |

Previously verified phonemes also present:
[ɑ] ×3 — AGNI.

---

## ŚIKṢĀ CLASSIFICATION

All four new phonemes are tālavya or dantya.

**Tālavya** — palatal — tongue body raised
to the hard palate. The Pāṇinīya Śikṣā
places three of the four new phonemes
here: ya (approximant), ja/jna (stop and
nasal). The tālavya sector of the VS
inventory is now substantially mapped.

**[j] antastha** — semivowel class.
Pāṇinīya Śikṣā: *ya ra la va* — the four
antastha, the sounds that stand between
(the consonants and the vowels). The
tongue approaches the palate. It does
not contact it. The antastha is defined
by approach without closure. This is
the Śikṣā description of what acoustic
phonetics calls an approximant. The two
descriptions are the same fact.

**[ɟ] tālavya row 3** — voiced unaspirated
palatal stop. The tongue body contacts
the hard palate. Full closure. Voiced
murmur during closure. Palatal burst at
release. This word contains the first
verification of the palatal stop locus:
3223 Hz.

**[ɲ] tālavya row 5** — palatal nasal.
Same place of articulation as [ɟ]. The
distinction is the velum: for [ɟ] it is
closed, for [ɲ] it is open. The
transition [ɟ]→[ɲ] in this word is the
same constriction held while the velum
opens. No F2 movement. No burst
transition. Only the nasal coupling
appearing. This is the most physically
intimate stop-to-nasal transition in the
VS inventory — both are tālavya. The
tongue barely moves.

**[s] dantya** — voiceless dental sibilant.
The turbulent jet directed against the
upper teeth. Dantya class: tongue tip to
upper teeth. The same place that produces
the dental stop [t] at burst locus 3764 Hz
produces the sibilant [s] at CF 7586 Hz.
The sibilant is higher because the
constriction is narrower and the
turbulence is finer. The cavity-to-frequency
relationship is the same physics. Different
degree of constriction — same place —
different frequency consequence.

---

## VERIFIED ACOUSTIC VALUES

### [j] — voiced palatal approximant

```
Śikṣā:           tālavya antastha
Voicing:          0.5659  (target >= 0.50)
F2 centroid:      2027.6 Hz  (target 1800–2400)
F3 centroid:      2699.8 Hz  (target 2500–3100)
Amplitude dips:   0  (target = 0)
Duration:         55 ms
```

**Synthesis parameters (locked):**
```python
VS_J_F         = [280.0, 2100.0, 2800.0, 3300.0]
VS_J_B         = [100.0,  200.0,  300.0,  350.0]
VS_J_GAINS     = [ 10.0,    6.0,    1.5,    0.5]
VS_J_DUR_MS    = 55.0
VS_J_COART_ON  = 0.18
VS_J_COART_OFF = 0.18
```

**Key diagnostic — D4 (the approximant criterion):**

The dip count of 0 is the defining result.
This is the acoustic realisation of the
Śikṣā antastha description: the tongue
approaches — it does not contact.

The dip detector requires a pitch-period-aware
smoothing kernel. At 120 Hz, one Rosenberg
period = 8.33 ms. The v1 detector used a 5 ms
kernel — shorter than one period — and detected
inter-pulse Rosenberg valleys as articulatory
dips. The [j] failed D4 in v1 with count = 4.

The v2 detector uses a 22.5 ms kernel (2.7×
pitch period). At this scale, Rosenberg
inter-pulse valleys are invisible. Only
articulatory-scale events survive. The [j]
produces 0 dips. The [ɾ] tap produces 2 dips
(as in PUROHITAM). The separation is clean.

**This is a calibration result, not a synthesis
fix.** The [j] was acoustically correct from the
first run. The detector was miscalibrated for
the VS pitch register. The v2 kernel is the
correct instrument for VS at 120 Hz.

The kernel constant is now computed from
physics:
```
DIP_SMOOTH_MS = (1000 / pitch_hz) × 2.7
```
It will scale correctly if the pitch register
changes.

---

### [ɟ] — voiced palatal stop

```
Śikṣā:           tālavya row 3
LF ratio:         0.9816  (target >= 0.40)
Burst centroid:   3223 Hz  (target 2800–4000)
Duration:         ~50 ms
```

**Synthesis parameters (locked):**
```python
VS_JJ_CLOSURE_MS  = 30.0
VS_JJ_BURST_F     = 3200.0
VS_JJ_BURST_BW    = 1500.0
VS_JJ_BURST_MS    = 9.0
VS_JJ_VOT_MS      = 10.0
VS_JJ_MURMUR_GAIN = 0.70
VS_JJ_BURST_GAIN  = 0.32
```

**Key diagnostic — D8 (burst hierarchy):**

The four-point hierarchy is now confirmed
from VS-internal measurements only:

```
[p] oṣṭhya    1204 Hz  (PUROHITAM)
[g] kaṇṭhya   2594 Hz  (ṚG / AGNI)
[ɟ] tālavya   3223 Hz  (this word)
[t] dantya    3764 Hz  (PUROHITAM)

oṣṭhya < kaṇṭhya < tālavya < dantya
```

Margin from [g]: +629 Hz.
Margin from [t]: −541 Hz.
The palatal stop is positioned cleanly
between the two adjacent verified stops.

This ordering is the acoustic expression of
the Śikṣā place ordering. The ancient
phoneticians ordered the places by tongue
position — front to back, or equivalently,
by the size of the anterior cavity. The
burst hierarchy orders them by the same
quantity. The Śikṣā taxonomy and the
spectrograph are the same map.

**Pending: mūrdhanya retroflex burst ~1300 Hz.**
This will slot below [p] oṣṭhya 1204 Hz —
counter-intuitive but physically correct.
The tongue curl creates a large sublingual
cavity anterior to the constriction.
Five-point hierarchy when ṚTVIJAM is reached.

---

### [ɲ] — voiced palatal nasal

```
Śikṣā:           tālavya row 5
Voicing:          0.6351  (target >= 0.50)
F2 centroid:      1980.1 Hz  (target 1800–2400)
F2 above [n]:     +1080 Hz  (target >= 500)
Antiresonance:    0.1963  (target < 0.60)
Anti band:        900–1500 Hz  (palatal zero)
Duration:         65 ms
```

**Synthesis parameters (locked):**
```python
VS_NY_F        = [250.0, 2000.0, 2800.0, 3300.0]
VS_NY_B        = [120.0,  180.0,  250.0,  300.0]
VS_NY_GAINS    = [  8.0,    4.0,    1.2,    0.4]
VS_NY_DUR_MS   = 65.0
VS_NY_ANTI_F   = 1200.0
VS_NY_ANTI_BW  = 250.0
```

**Key diagnostic — D13 (nasal zero ordering):**

Three-nasal antiresonance hierarchy now
confirmed from VS-internal measurements:

```
[m] oṣṭhya   ~800 Hz   ratio 0.0046  (PUROHITAM)
[n] dantya   ~800 Hz   ratio 0.0018  (AGNI)
[ɲ] tālavya  ~1200 Hz  ratio 0.1963  (this word)
```

The physical basis: the nasal side branch
(from the velum to the place of articulation)
acts as a Helmholtz-type resonator. Shorter
branch → higher resonant frequency → higher
antiresonance frequency in the output.

For [m] and [n], the nasal side branches are
long (labial and dental — far from the
velum). Their zeros cluster near 800 Hz.

For [ɲ], the palatal constriction is close to
the velum — the nasal side branch is short.
The zero is higher: ~1200 Hz. The palatal nasal
is distinctly brighter than [m] and [n]. This is
the Śikṣā ordering oṣṭhya < dantya < tālavya
expressed as an antiresonance ordering.

**Pending: [ɳ] retroflex ~1000 Hz, [ŋ] velar ~2000 Hz.**
When verified, the full five-nasal zero hierarchy
will confirm the complete Śikṣā ordering
acoustically, root to crown.

---

### [s] — voiceless dental sibilant

```
Śikṣā:           dantya
Voicing:          0.1085  (target <= 0.30)
Noise CF:         7586.4 Hz  (target 5000–11000)
Above [t] burst:  +3822 Hz  (target >= 500)
Duration:         80 ms
```

**Synthesis parameters (locked):**
```python
VS_S_NOISE_CF  = 7500.0
VS_S_NOISE_BW  = 3000.0
VS_S_GAIN      = 0.22
VS_S_DUR_MS    = 80.0
```

**Key diagnostic — D17 (sibilant hierarchy):**

[s] is the highest-frequency phoneme
verified in the VS inventory. CF 7586 Hz.
It sits 3822 Hz above the [t] burst (3764 Hz) —
the same dantya constriction, narrower, higher.

The three-sibilant hierarchy is partially
established:
```
[ʂ] mūrdhanya  ~2800 Hz  (PENDING)
[ɕ] tālavya    ~4500 Hz  (PENDING)
[s] dantya      7586 Hz  (VERIFIED)
```

The sibilant hierarchy mirrors the stop burst
hierarchy: smaller anterior cavity = higher
frequency. The retroflex sibilant will be
lowest (large sublingual cavity), the dental
sibilant is highest (no anterior cavity beyond
the teeth), the palatal sibilant sits between.
Same physics. Different degree of constriction.

---

## THE [ɟ]→[ɲ] TRANSITION

The transition from voiced palatal stop to
voiced palatal nasal within this word is
acoustically unique in the VS inventory.

Both phonemes are tālavya. The tongue body
is at the hard palate for both. The F2 locus
does not move. The burst of [ɟ] releases into
[ɲ] without a formant jump.

What changes across the boundary is exactly
one thing: the velum opens. The oral stop
releases, and as it does, the nasal coupling
activates. The nasal antiresonance appears.
The formant pattern shifts from oral-stop
quality to nasal quality. But the F2 trajectory
is continuous. The tongue is in the same room.

This is what the Śikṣā means by placing [ɟ]
and [ɲ] in the same row: they share a place.
The acoustic evidence is the continuous F2
across the stop-to-nasal transition.

The [ɟ]→[ɲ] transition in YAJÑASYA is the
first time the VS reconstruction has produced
a stop-to-homorganic-nasal sequence. It
confirms that the place framework is working:
phonemes at the same Śikṣā place produce
continuous F2 trajectories across their
boundaries. This is coarticulation as evidence
of phonological structure.

---

## THE DIAGNOSTIC CALIBRATION DISCOVERY

This word produced an important
methodological result independent of the
phoneme verification.

The dip detector for the approximant criterion
must use a smoothing kernel scaled to the
pitch period of the synthesis. At 120 Hz
(VS recitation register), the Rosenberg glottal
pulse period is 8.33 ms. A smoothing kernel
shorter than this period will detect
inter-pulse amplitude valleys as articulatory
dips. The v1 kernel (5 ms) was shorter than
one pitch period and produced a false count
of 4 dips for [j].

The correct kernel spans at least 2.5–3× the
pitch period. For VS at 120 Hz, this is
approximately 22 ms. At this scale:

- Rosenberg inter-pulse valleys: invisible
- Tap [ɾ] articulatory dip: still visible
  (the physical contact is longer than the
  pitch period, so it survives the longer kernel)
- Approximant [j]: zero dips
  (no articulatory closure at any scale)

The dip count = 0 for [j] and dip count = 2
for [ɾ] at the 22 ms scale constitutes a
clean binary separation of the approximant
and tap classes.

The kernel constant is now physics-derived:
```
smooth_ms = (1000 / pitch_hz) × 2.7
```
This will scale automatically to any pitch
register used in future VS synthesis.

---

## DIAGNOSTIC RESULTS — FULL RECORD

| Check | Value | Target | Result |
|---|---|---|---|
| D1  [j] voicing | 0.5659 | >= 0.50 | PASS |
| D2  [j] F2 centroid | 2027.6 Hz | 1800–2400 Hz | PASS |
| D3  [j] F3 centroid | 2699.8 Hz | 2500–3100 Hz | PASS |
| D4  [j] dip count | 0 | = 0 | PASS |
| D5  [j] Śikṣā confirmation | — | D1–D4 | PASS |
| D6  [ɟ] LF ratio | 0.9816 | >= 0.40 | PASS |
| D7  [ɟ] burst centroid | 3223.1 Hz | 2800–4000 Hz | PASS |
| D8  [ɟ] burst hierarchy | +629 / −541 Hz | in range | PASS |
| D9  [ɟ] Śikṣā confirmation | — | D6–D8 | PASS |
| D10 [ɲ] voicing | 0.6351 | >= 0.50 | PASS |
| D11 [ɲ] F2 centroid | 1980.1 Hz | 1800–2400 Hz | PASS |
| D12 [ɲ] antiresonance | 0.1963 | < 0.60 | PASS |
| D13 [ɲ] nasal zero order | 0.1963 in 900–1500 Hz | in palatal band | PASS |
| D14 [ɲ] Śikṣā confirmation | — | D10–D13 | PASS |
| D15 [s] voicing | 0.1085 | <= 0.30 | PASS |
| D16 [s] noise CF | 7586.4 Hz | 5000–11000 Hz | PASS |
| D17 [s] sibilant hierarchy | +3822 Hz above [t] | >= 500 Hz | PASS |
| D18 [s] Śikṣā confirmation | — | D15–D17 | PASS |
| D19 Full word RMS | 0.3021 | 0.01–0.90 | PASS |
| D19 Full word duration | 468.9 ms | 400–750 ms | PASS |
| D20 Perceptual | — | LISTEN | — |

**Diagnostic script:** `yajnasya_diagnostic.py v2`
**All 19 numeric checks: PASS**

---

## SYNTHESIS PARAMETERS — PERFORMANCE

```
pitch_hz:     120.0
dil:          1.0  (diagnostic)
rt60:         1.5  (temple courtyard)
direct_ratio: 0.55
SR:           44100 Hz
```

---

## OUTPUT FILES

```
yajnasya_dry.wav          — direct signal
yajnasya_hall.wav         — temple courtyard
yajnasya_slow.wav         — 4× OLA stretch
yajnasya_j_iso.wav        — [j] isolated
yajnasya_jj_iso.wav       — [ɟ] isolated
yajnasya_ny_iso.wav       — [ɲ] isolated
yajnasya_s_iso.wav        — [s] isolated
(slow versions of each isolated phoneme)
```

---

## CUMULATIVE INVENTORY STATE

### Verified phonemes after YAJÑASYA: 19

```
Word        Phonemes added
ṚG          [ɻ̩]  [g]
AGNI        [a]  [n]  [i]
ĪḶE         [iː] [ɭ]  [eː]
PUROHITAM   [p]  [u]  [ɾ]  [oː]  [h]  [t]  [m]
YAJÑASYA    [j]  [ɟ]  [ɲ]  [s]
```

### Tālavya row — current state

```
[c]   voiceless palatal stop        PENDING
[cʰ]  voiceless palatal aspirated   PENDING
[ɟ]   voiced palatal stop           VERIFIED  (this word)
[ɟʰ]  voiced palatal aspirated      PENDING
[ɲ]   voiced palatal nasal          VERIFIED  (this word)
[j]   palatal approximant (antastha) VERIFIED  (this word)
[ɕ]   palatal sibilant              PENDING
```

Three of seven tālavya phonemes confirmed.
The voiced column is mapped.
Voiceless unaspirated [c] and the aspirated
pair [cʰ][ɟʰ] remain.

### Four-point burst hierarchy — confirmed

```
oṣṭhya  [p]  1204 Hz  (PUROHITAM)
kaṇṭhya [g]  2594 Hz  (ṚG / AGNI)
tālavya [ɟ]  3223 Hz  (this word)
dantya  [t]  3764 Hz  (PUROHITAM)
```

Pending: mūrdhanya [ɖ/ʈ] ~1300 Hz.
Will slot below oṣṭhya when ṚTVIJAM verified.

### Three-nasal antiresonance — confirmed

```
oṣṭhya  [m]  ~800 Hz   ratio 0.0046  (PUROHITAM)
dantya  [n]  ~800 Hz   ratio 0.0018  (AGNI)
tālavya [ɲ]  ~1200 Hz  ratio 0.1963  (this word)
```

Pending: mūrdhanya [ɳ] ~1000 Hz, kaṇṭhya [ŋ] ~2000 Hz.

### Sibilant hierarchy — partial

```
mūrdhanya [ʂ]  ~2800 Hz  PENDING
tālavya   [ɕ]  ~4500 Hz  PENDING
dantya    [s]   7586 Hz  VERIFIED (this word)
```

---

## NEXT WORD

**DEVAM** — [devɑm] — the divine,
the god, the shining one.
Rigveda 1.1.1, word 5.
*yajñasya devam* — the divine of the sacrifice.

New phoneme: **[d]** — voiced dental stop.
Row 3 of the dental column.
The voiced partner of [t] (verified PUROHITAM).
LF ratio diagnostic. Dental burst ~3764 Hz locus.
Voiced closure + dental burst + short VOT.

Previously verified in DEVAM:
  [eː] — ĪḶE
  [m]  — PUROHITAM
  [a]  — AGNI

One new phoneme only.

---

*February 2026.*
*Of the sacrifice.*
*The tālavya row is opening.*
*The sibilant space has its anchor.*
*19 phonemes.*
*The instrument holds.*
