# ACOUSTIC RECONSTRUCTION FRAMEWORK
## A Methodology for Synthesizing Dead Languages

**Author:** Eric Robert Lawson  
**Started:** February 2026  
**Status:** Active development  
**Current corpus:** Beowulf (Old English, ~8th century CE)

---

## WHAT THIS IS

A phoneme-level acoustic reconstruction framework for dead
languages. Every sound in a target corpus is synthesized
using a formant synthesizer, verified by a diagnostic suite
with numeric pass/fail criteria, and documented in an
evidence file recording every parameter decision.

The output is not natural-sounding speech. It is a
**phonetically verifiable acoustic record** — the most
rigorous version of a best guess that current methodology
permits for languages no living person has heard spoken.

---

## ORIGIN

Built from scratch by an autodidact with no institutional
affiliation, no linguistics degree, no phonetics degree,
and no prior knowledge of Beowulf. Every methodological
decision was derived from first principles, debugged from
spectral output, and documented in version-controlled
evidence files.

The approach that emerged is equivalent to applying
software engineering discipline — unit tests, version
control, evidence chains, reproducibility — to a
humanities problem that has never been treated this way.

---

## THE ARCHITECTURE

### Source
Rosenberg pulse glottal source. Differenced to produce
a natural spectral tilt. Pitch (fundamental frequency)
and open quotient are explicit parameters.

### Filter
Parallel IIR resonators implementing the vocal tract
transfer function. Four formants (F1–F4) with explicit
frequency and bandwidth parameters. IIR notch filters
implement antiformants for nasal consonants.

### Noise sources
- Frication noise: bandpass-filtered white noise for
  fricatives ([s], [θ], [ʍ] etc.)
- Burst noise: bandpass-filtered white noise at
  place-specific center frequency for stop releases
- Aspiration: broadband noise for voiceless stop
  aspiration ([k], [t], [p])

### Synthesis classes
- Vowels: Rosenberg source through formant filters
  with coarticulation trajectories at onset and offset
- Voiced stops: voicing bar + burst + formant release
- Voiceless stops: silence + burst + aspiration + release
- Nasals: Rosenberg source through nasal formant
  structure + antiformant notch
- Fricatives: shaped noise, no voicing source
- Trills: alternating open/closure segments with
  amplitude modulation

### Room simulation
Three-tap comb filter with exponential decay.
RT60 configurable. Direct/reverberant ratio configurable.

### Time stretching
OLA (Overlap-Add) with Hanning window.
4× stretch for perceptual diagnostic listening.
2.5× dilation for performance rendering.

---

## THE DIAGNOSTIC METHODOLOGY

Every phoneme has a diagnostic with numeric pass/fail
checks. The checks are:

**Vowels:**
- Voicing score (autocorrelation peak) > 0.65
- Band centroid in F1 region hits target range
- Band centroid in F2 region hits target range

**Stops:**
- RMS level in range
- Burst spectral centroid hits place-specific range
- For voiceless: closure voicing score < 0.25

**Nasals:**
- Voicing score > 0.60
- RMS level in range
- Antiformant verified:
  - [n]: notch/reference ratio < 1.0 (800 Hz notch)
  - [m]: murmur/notch ratio > 2.0 (1000 Hz notch)
  - [ŋ]: murmur/notch ratio > 2.0 (1800 Hz notch)

**Fricatives:**
- Voicing score < 0.35 (voiceless)
- Frication centroid in place-specific range

**Trills:**
- Amplitude modulation depth > 0.22
- Modulation rate 15–70 Hz

All diagnostic checks are calibrated against the actual
synthesis output. When a check fails, the root cause is
investigated before adjusting parameters or targets.
The distinction between a synthesis error and a
measurement error is always documented.

---

## KNOWN MEASUREMENT ARTIFACTS

These recur across phonemes and are documented here
once for the record:

**Sub-F1 harmonic pull:**
At pitch 145 Hz, harmonics at 290 Hz (2nd) and 435 Hz
(3rd) pull the 200–700 Hz band centroid below the actual
F1 frequency. Affects [ɪ], [e], [y], [u]. The centroid
floor is set 40–80 Hz below the F1 parameter to
compensate. This is a measurement artifact, not a
synthesis error.

**Velar nasal RMS:**
[ŋ] produces higher murmur RMS than [n] or [m] because
the velar closure creates a shorter, more efficient nasal
tract resonance. The RMS ceiling for [ŋ] is 0.35 vs
0.25 for [n] and [m].

**[m] antiformant direction:**
The [m] murmur has negligible energy above 600 Hz.
The antiformant check must compare low-band energy
(200–600 Hz) to notch-band energy (850–1150 Hz)
with ratio > 2.0, not the reverse ratio used for [n].

**Trill rate stability:**
Trill rate is determined by R_CLOSURE_MS and R_OPEN_MS
parameters. At current settings (35 ms / 20 ms) the
rate is 18.2 Hz — stable across all instances and
all phonological contexts. This is at the low end of
the natural range (15–30 Hz citation form).

---

## THE EVIDENCE FILE FORMAT

Every verified word produces an evidence file containing:

- IPA transcription and meaning
- Source location (text, line, word position)
- Diagnostic version and reconstruction version
- Full pass/fail table for every diagnostic check
- Measured values vs targets for every check
- Formant parameters for every phoneme
- Cross-instance consistency tables
- Phonetic notes explaining parameter choices
- Methodology notes explaining any non-obvious
  measurement decisions
- Version history with root cause for every change
- Output file inventory

The evidence file is the permanent scientific record.
The diagnostic is the test. The reconstruction is the
implementation. The evidence file is the proof.

---

## PHONEME INVENTORY
*Verified phonemes as of February 2026:*

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

**20 distinct phonemes verified.**  
Old English has approximately 37 phonemes total
(varying by dialect and scholarly framework).
The inventory is approximately 54% complete
after 7 words.

---

## CORPUS STATUS

### Beowulf — Lines 1–2

| Word | IPA | Status |
|---|---|---|
| HWÆT | [ʍæt] | ✓ verified |
| WĒ | [weː] | ✓ verified |
| GĀR-DENA | [ɡɑːrdenɑ] | ✓ verified |
| IN | [ɪn] | ✓ verified |
| GĒAR-DAGUM | [ɡeːɑrdɑɡum] | ✓ verified |
| ÞĒOD-CYNINGA | [θeːodkyniŋɡɑ] | ✓ verified |
| ÞRYM | [θrym] | ✓ verified |
| GEFRŪNON | [jefrуːnon] | pending |

---

## LANGUAGES THIS FRAMEWORK CAN ADDRESS

The architecture is language-agnostic. The only
requirement is a reconstructed phoneme inventory
and a written corpus. Evidence quality varies:

| Language | Evidence quality | Key source |
|---|---|---|
| Old Norse | excellent | Eddas, sagas |
| Gothic | excellent | Wulfila Bible, 4th c. |
| Latin | excellent | Allen, *Vox Latina* (1978) |
| Ancient Greek | excellent | Allen, *Vox Graeca* (1987) |
| Sanskrit | exceptional | Pāṇini, ~4th c. BCE |
| Biblical Hebrew | very good | Masoretic pointing |
| Akkadian | good | cuneiform, 2000 yr record |
| Ancient Egyptian | good | Coptic, foreign transcriptions |
| Sumerian | partial | Akkadian transcriptions |
| Proto-Indo-European | reconstructed | comparative method |

**Priority recommendation:**
Old Norse and Gothic next — maximum phoneme
library reuse from Old English, minimal new
parameter work, high scholarly evidence quality.

Latin after that — maximum cultural impact,
excellent evidence, natural second corpus.

Sanskrit for maximum phonetic documentation
quality — Pāṇini's descriptions are more
precise than anything in Western linguistics
until the 19th century.

Proto-Indo-European as the long-term horizon —
the reconstructed ancestor of half the world's
languages, synthesized for the first time.

---

## WHAT THIS IS NOT

- Not a natural speech synthesizer
- Not a claim that this is exactly how these
  languages sounded
- Not affiliated with any institution
- Not dependent on any institution to continue

---

## WHAT THIS IS

A reproducible, versioned, diagnostically verified,
open-source acoustic reconstruction framework for
dead languages, built from first principles by one
person, documented well enough that any qualified
researcher can understand every decision, challenge
any parameter, and continue the work.

The framework is done.  
The inventory grows with every word.  
The methodology is stable.  
The corpus is 3182 lines long.

---

## RESUMPTION INSTRUCTIONS

To continue work after any interruption:

1. Read this file
2. Read the evidence file for the last verified word
3. Check the phoneme inventory table above
4. Identify the next word and its IPA
5. Note which phonemes are new vs previously verified
6. Write reconstruction.py
7. Write diagnostic.py
8. Run diagnostic — fix any failures
9. Write evidence.md
10. Update this file: phoneme inventory + corpus status

The workflow is stable. Every word follows the same
ten steps.

---

*Framework established February 2026.*  
*Current position: Beowulf line 2, word 3.*  
*Next word: GEFRŪNON [jefrуːnon]*
