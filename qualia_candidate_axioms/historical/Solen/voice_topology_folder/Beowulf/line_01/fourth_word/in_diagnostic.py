============================================================
IN DIAGNOSTIC v2
Old English [ɪn]
Beowulf line 1, word 4
============================================================

  in_reconstruction.py: OK

────────────────────────────────────────────────────────────
DIAGNOSTIC 1 — I VOWEL [ɪ]

  Near-close near-front lax vowel.
  F1 centroid (200–700 Hz):
    target 280–480 Hz
    (floor 280: sub-F1 harmonics
     at 290 Hz pull centroid down)
  F2 centroid (1400–2200 Hz):
    target 1600–2000 Hz

    [PASS] voicing (body): 0.6699  target [0.6500–1.0000]  ██████████████████████████
    [PASS] RMS level: 0.3041  target [0.0100–5.0000]  ████████████
    [PASS] F1 centroid (307 Hz): 307.1 Hz  target [280.0–480.0]  
    [PASS] F2 centroid (1774 Hz): 1773.7 Hz  target [1600.0–2000.0]  
  diag_i_vowel_slow.wav
  PASSED

────────────────────────────────────────────────────────────
DIAGNOSTIC 2 — N NASAL [n]

    [PASS] voicing: 0.7666  target [0.6000–1.0000]  ██████████████████████████████
    [PASS] RMS (nasal murmur): 0.1935  target [0.0050–0.2500]  ███████
    [PASS] antiformant ratio (800/1200 Hz): 0.0996  target [0.0000–1.0000]  ███
  diag_n_final_slow.wav
  PASSED

────────────────────────────────────────────────────────────
DIAGNOSTIC 3 — FULL WORD [ɪn]

    [PASS] RMS level: 0.2778  target [0.0100–0.9000]  ███████████
    [PASS] duration (120 ms): 120.0 ms  target [80.0–180.0]  
    [PASS] I zone voicing: 0.7812  target [0.6500–1.0000]  ███████████████████████████████
    [PASS] N zone voicing: 0.7666  target [0.5500–1.0000]  ██████████████████████████████
  5291 samples (120 ms)
  diag_in_full.wav
  diag_in_hall.wav
  diag_in_slow.wav
  PASSED

────────────────────────────────────────────────────────────
DIAGNOSTIC 4 — PERCEPTUAL

  afplay output_play/diag_i_vowel_slow.wav
  afplay output_play/diag_n_final_slow.wav
  afplay output_play/diag_in_slow.wav
  afplay output_play/diag_in_hall.wav

  LISTEN FOR:
  I: short, high, front — 'bit' quality
    NOT 'see' (too high)
    NOT 'bet' (too open)
  N: nasal murmur fading to silence
  Full: two events, 120 ms total

============================================================
SUMMARY

  D1 I vowel              ✓ PASS
  D2 N nasal              ✓ PASS
  D3 Full word            ✓ PASS
  D4 Perceptual           LISTEN

  ALL NUMERIC CHECKS PASSED

  IN [ɪn] verified.
  Next word: GĒAR-DAGUM
  Beowulf line 1, word 5.

============================================================
