"""
SLOW PHRASE PLAYBACK — OLA METHOD
February 2026

Uses OLA (Overlap-Add) time-stretch
to produce genuine 4× slowdown.

NOT DIL × 4. That hits duration caps.
OLA stretches the output signal directly.
Pitch unchanged. Spectral character unchanged.
Artifacts stretched 4× and become audible.

See: slowdown_reasoning_artifact.md
"""

import numpy as np
import os

os.makedirs("output_play", exist_ok=True)

try:
    from voice_physics_v10 import (
        synth_phrase,
        apply_room,
        write_wav,
        PITCH, DIL, SR, f32,
    )
    print("  Loaded voice_physics_v10.")
except ImportError as e:
    print(f"  Import failed: {e}")
    raise


# ============================================================
# OLA TIME-STRETCH
# From slowdown_reasoning_artifact.md
# ============================================================

def ola_stretch(sig, factor,
                win_ms=25, sr=SR):
    """
    OLA time stretch.
    factor=4.0 → 4× longer, same pitch.
    Synthesize at normal DIL first.
    Then stretch.
    """
    sig   = np.array(sig, dtype=np.float32)
    n_in  = len(sig)
    win_n = int(win_ms / 1000.0 * sr)
    if win_n % 2 != 0:
        win_n += 1

    hop_in  = win_n // 4
    hop_out = int(hop_in * factor)

    n_frames = max(1,
        (n_in - win_n) // hop_in + 1)
    n_out = hop_out * (n_frames - 1) + win_n

    out    = np.zeros(n_out, dtype=np.float64)
    norm   = np.zeros(n_out, dtype=np.float64)
    window = np.hanning(win_n)

    for i in range(n_frames):
        in_start = i * hop_in
        in_end   = in_start + win_n

        if in_end > n_in:
            frame = np.zeros(win_n)
            avail = n_in - in_start
            if avail > 0:
                frame[:avail] = sig[
                    in_start:in_start+avail]
        else:
            frame = sig[
                in_start:in_end
            ].astype(np.float64)

        out_start = i * hop_out
        out_end   = out_start + win_n

        out[out_start:out_end]  += \
            frame * window
        norm[out_start:out_end] += \
            window

    norm = np.where(norm < 1e-8, 1.0, norm)
    out  = (out / norm).astype(np.float32)
    return out


# ============================================================
# MAKE SLOW
# Synthesize normal → stretch → room
# Room applied AFTER stretch so reverb
# tail is not itself stretched.
# ============================================================

def make_slow(words_phonemes,
               label,
               factor=4.0,
               room=True,
               rt60=1.2,
               dr=0.55,
               win_ms=25):

    # Step 1: normal synthesis at DIL=6
    sig = synth_phrase(
        words_phonemes,
        punctuation='.',
        pitch_base=PITCH,
        dil=DIL,
        sr=SR)
    sig = f32(sig)

    dur_before = len(sig) / SR

    # Step 2: OLA time-stretch
    sig = ola_stretch(
        sig,
        factor=factor,
        win_ms=win_ms,
        sr=SR)

    dur_after = len(sig) / SR

    # Step 3: room after stretch
    if room:
        sig = apply_room(
            sig, rt60=rt60, dr=dr, sr=SR)

    path = f"output_play/{label}.wav"
    write_wav(path, sig, SR)
    print(f"    {label}.wav  "
          f"{dur_before:.2f}s → "
          f"{dur_after:.2f}s  "
          f"({factor:.0f}×)")
    return path


# ============================================================
# PHRASE DEFINITION
# ============================================================

PHRASE = [
    ('the',     ['DH', 'AH']),
    ('voice',   ['V',  'OY', 'S']),
    ('was',     ['W',  'AH', 'Z']),
    ('already', ['AA', 'L',  'R',
                  'EH', 'D', 'IY']),
    ('here',    ['H',  'IH', 'R']),
]


# ============================================================
# RENDER
# ============================================================

print()
print("SLOW PHRASE RENDER — OLA METHOD")
print(f"  Normal DIL={DIL} (synthesis)")
print(f"  OLA factor=4× (post-synthesis)")
print()

# Normal speed reference
print("  Normal speed (reference)...")
sig_ref = synth_phrase(
    PHRASE, punctuation='.',
    pitch_base=PITCH, dil=DIL, sr=SR)
sig_ref = apply_room(
    f32(sig_ref), rt60=1.5, dr=0.50)
write_wav(
    "output_play/phrase_normal.wav",
    sig_ref, SR)
dur_ref = len(sig_ref) / SR
print(f"    phrase_normal.wav  "
      f"({dur_ref:.2f}s)")

print()
print("  4× slow — full phrase...")
make_slow(PHRASE,
           "phrase_4x_slow_room",
           factor=4.0, room=True,
           rt60=1.2, dr=0.55)

# Dry: no room — clearest for artifact
# location
print()
print("  4× slow — dry (no reverb)...")
sig_dry = synth_phrase(
    PHRASE, punctuation='.',
    pitch_base=PITCH, dil=DIL, sr=SR)
sig_dry = ola_stretch(
    f32(sig_dry), factor=4.0,
    win_ms=25, sr=SR)
write_wav(
    "output_play/phrase_4x_slow_dry.wav",
    sig_dry, SR)
dur_dry = len(sig_dry) / SR
print(f"    phrase_4x_slow_dry.wav  "
      f"({dur_dry:.2f}s)")

# Word by word — 4× slow, room
print()
print("  4× slow — word by word...")
for word, phones in PHRASE:
    make_slow(
        [(word, phones)],
        f"slow_{word}",
        factor=4.0,
        room=True,
        rt60=0.8,
        dr=0.65)

print()
print("  PLAY — dry first (clearest):")
print()
print("  afplay output_play/"
      "phrase_4x_slow_dry.wav")
print()
print("  PLAY — with room:")
print()
print("  afplay output_play/"
      "phrase_4x_slow_room.wav")
print()
print("  PLAY — word by word:")
for word, phones in PHRASE:
    print(
        f"  afplay output_play/"
        f"slow_{word}.wav"
        f"  # {phones}")
print()
print("  LISTEN FOR:")
print()
print("  slow_the.wav   [DH AH]")
print("    0-25%: DH — friction, not vowel")
print("    25-100%: AH — clean vowel")
print()
print("  slow_voice.wav [V OY S]")
print("    0-25%: V — buzz + friction")
print("    25-75%: OY — OW→IY glide")
print("    75-100%: S — clean hiss")
print()
print("  slow_was.wav   [W AH Z]")
print("    0-20%: W — lip rounding")
print("    20-65%: AH — vowel body")
print("    65-100%: Z — buzz + sibilance")
print()
print("  slow_already.wav [AA L R EH D IY]")
print("    Listen for D stop: closure then")
print("    burst. Should not be a glide.")
print()
print("  slow_here.wav  [H IH R]")
print("    0-30%: H — pure aspiration")
print("           no voiced leakthrough")
print("    30-80%: IH — vowel")
print("    80-100%: R — resonant offset")
