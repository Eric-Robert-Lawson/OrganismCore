"""
SPEAK — primary render script
February 2026

Uses voice_template.md phrase definitions.
Run this to hear the current voice.
"""

import os
import numpy as np
from voice_physics_v10 import (
    synth_phrase,
    apply_room,
    write_wav,
    PITCH, DIL, SR, f32,
)

os.makedirs("output_play", exist_ok=True)


def ola_stretch(sig, factor,
                win_ms=25, sr=SR):
    sig   = np.array(sig, dtype=np.float32)
    n_in  = len(sig)
    win_n = int(win_ms/1000.0*sr)
    if win_n % 2 != 0:
        win_n += 1
    hop_in  = win_n // 4
    hop_out = int(hop_in * factor)
    n_frames = max(1,
        (n_in-win_n)//hop_in + 1)
    n_out = hop_out*(n_frames-1)+win_n
    out  = np.zeros(n_out, dtype=np.float64)
    norm = np.zeros(n_out, dtype=np.float64)
    window = np.hanning(win_n)
    for i in range(n_frames):
        i0 = i*hop_in
        i1 = i0+win_n
        if i1 > n_in:
            frame = np.zeros(win_n)
            av = n_in-i0
            if av > 0:
                frame[:av] = sig[i0:i0+av]
        else:
            frame = sig[i0:i1].astype(
                np.float64)
        o0 = i*hop_out
        o1 = o0+win_n
        out[o0:o1]  += frame*window
        norm[o0:o1] += window
    norm = np.where(norm<1e-8, 1.0, norm)
    return (out/norm).astype(np.float32)


def render(phrase, name, punct='.',
            rt60=1.2, dr=0.55,
            slow=False, slow_factor=4.0):
    sig = synth_phrase(
        phrase, punctuation=punct,
        pitch_base=PITCH,
        dil=DIL, sr=SR)
    sig = f32(sig)
    if slow:
        sig = ola_stretch(
            sig, factor=slow_factor)
    sig = apply_room(sig,
                     rt60=rt60, dr=dr)
    path = f"output_play/{name}.wav"
    write_wav(path, sig, SR)
    words = ' '.join(w for w, _ in phrase)
    dur   = len(sig)/SR
    print(f"  {name}.wav  "
          f"({dur:.2f}s)  \"{words}\"")


# ============================================================
# PHRASES
# ============================================================

print()
print("SPEAK — voice_physics_v10")
print()

# Original test phrase
render([
    ('the',     ['DH', 'AH']),
    ('voice',   ['V',  'OY', 'S']),
    ('was',     ['W',  'AH', 'Z']),
    ('already', ['AA', 'L', 'R',
                  'EH', 'D', 'IY']),
    ('here',    ['H',  'IH', 'R']),
], "the_voice_was_already_here")

# New phrases
render([
    ('the',    ['DH', 'AH']),
    ('mind',   ['M', 'AY', 'N', 'D']),
    ('moves',  ['M', 'UW', 'V', 'Z']),
    ('slowly', ['S', 'L', 'OW', 'L', 'IY']),
], "the_mind_moves_slowly")

render([
    ('he',   ['H', 'IY']),
    ('sees', ['S', 'IY', 'Z']),
    ('the',  ['DH', 'AH']),
    ('haze', ['H', 'EH', 'Z']),
], "he_sees_the_haze")

render([
    ('where', ['W', 'EH', 'R']),
    ('will',  ['W', 'IH', 'L']),
    ('we',    ['W', 'IY']),
    ('walk',  ['W', 'AO', 'K']),
], "where_will_we_walk", punct='?')

render([
    ('nothing', ['N', 'AH', 'TH', 'IH', 'NG']),
    ('begins',  ['B', 'IH', 'G', 'IH', 'N', 'Z']),
    ('without', ['W', 'IH', 'DH', 'AW', 'T']),
    ('an',      ['AE', 'N']),
    ('end',     ['EH', 'N', 'D']),
], "nothing_begins_without_an_end")

print()
print("  PLAY:")
for name in [
    "the_voice_was_already_here",
    "the_mind_moves_slowly",
    "he_sees_the_haze",
    "where_will_we_walk",
    "nothing_begins_without_an_end",
]:
    print(f"  afplay output_play/{name}.wav")
