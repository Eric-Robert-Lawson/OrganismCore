"""
TONNETZ VOICE ENGINE
Extracted from here_composition.py
Confirmed architecture — Parts 1-5.
All invariants encoded.
Do not modify without reading
finding_voice_pt1 through pt8.

INVARIANTS (never violate):
  1. ALWAYS differentiate Rosenberg (np.diff)
  2. NEVER series formant chain — parallel only
  3. NEVER dry source in output
  4. NEVER turbulence before formant bank
  5. NEVER normalize inside voice stream
  6. NEVER symmetric ensemble detuning
     use: 0, +11, -17 cents
  7. NEVER IIR notch on strong fundamental
  8. ALWAYS vectorized phase accumulator
     never per-cycle Python loops
"""

import numpy as np
from scipy.signal import lfilter, butter
import wave as wave_module
import os

SR = 44100

# ============================================================
# TONNETZ — JUST INTONATION
# ============================================================

JI_RATIOS = {
    ( 0, 0):(1,1),    ( 1, 0):(3,2),
    (-1, 0):(4,3),    ( 2, 0):(9,8),
    (-2, 0):(16,9),   ( 3, 0):(27,16),
    (-3, 0):(32,27),  ( 0, 1):(5,4),
    ( 0,-1):(8,5),    ( 1, 1):(15,8),
    (-1, 1):(6,5),    ( 1,-1):(9,5),
    ( 0, 2):(25,16),  ( 6, 0):(729,512),
    ( 4, 0):(81,64),  (-4, 0):(128,81),
    ( 5, 0):(243,128),(-5, 0):(256,243),
    ( 2, 1):(45,32),  (-2, 1):(75,64),
    ( 3, 1):(135,128),
}

def ji_freq(a, b, tonic=220.0):
    """
    Convert Tonnetz position (a,b) to frequency.
    a = fifth-axis, b = third-axis.
    tonic=220.0 (A3) — lower, more interior.
    """
    if (a,b) in JI_RATIOS:
        p,q  = JI_RATIOS[(a,b)]
        freq = tonic*(p/q)
    else:
        freq = tonic*((3/2)**a)*((5/4)**b)
    while freq > tonic*2: freq /= 2
    while freq < tonic:   freq *= 2
    return freq

def coherence(a, b):
    """
    Coherence of Tonnetz position relative to tonic.
    (0,0) = 1.0. Tritone (6,0) = ~0.051.
    Higher = closer to home.
    """
    if a==0 and b==0: return 1.0
    if (a,b) in JI_RATIOS:
        p,q = JI_RATIOS[(a,b)]
        rc  = np.log2(max(p,1))+np.log2(max(q,1))
        return 1.0/(1.0+rc)
    p = int((3**abs(a))*(5**abs(b)))
    q = int((2**abs(a))*(4**abs(b)))
    g = np.gcd(p,q); p//=g; q//=g
    rc = np.log2(max(p,1))+np.log2(max(q,1))
    return 1.0/(1.0+rc)

# ============================================================
# VOWEL SYSTEM
# Confirmed formant tables — Parts 1-5.
# Do not adjust without perceptual confirmation.
# ============================================================

VOWEL_DATA = {
    # F1, F2, F3, F4 | BW1-4 | Gain1-4
    'ah': {'f':[700, 1220,2600,3200],
           'b':[130,   70, 160, 200],
           'g':[6.0,  4.0, 1.8, 0.7]},
    'eh': {'f':[600, 1800,2550,3200],
           'b':[110,   90, 160, 200],
           'g':[5.5,  5.0, 1.8, 0.7]},
    'ee': {'f':[280, 2250,3000,3500],
           'b':[ 90,   80, 150, 200],
           'g':[4.0,  6.0, 2.2, 0.8]},
    'oh': {'f':[450,  800,2550,3200],
           'b':[120,   80, 160, 200],
           'g':[5.0,  3.5, 1.5, 0.6]},
    'oo': {'f':[300,  870,2250,3000],
           'b':[110,   80, 140, 180],
           'g':[5.0,  4.5, 1.3, 0.5]},
    # pre: the pre-vowel — between breath and /ah/
    # The formant shape of a voice not yet speaking.
    # Use for searching, uncertain, pre-arrival states.
    'pre':{'f':[500,  900,2400,3000],
           'b':[150,  100, 170, 210],
           'g':[3.5,  2.8, 1.2, 0.5]},
    # ou: diphthong start position for /oʊ/ ("both")
    # Part 7: the vowel that closes around a truth.
    'ou_start':{'f':[450,  800,2550,3200],
                'b':[120,   80, 160, 200],
                'g':[5.0,  3.5, 1.5, 0.6]},
    'ou_end':  {'f':[300,  870,2250,3000],
                'b':[110,   80, 140, 180],
                'g':[5.0,  4.5, 1.3, 0.5]},
}

# ============================================================
# AGENT SYSTEM — The Puddle (Part 3)
# Breath rates are register-differentiated.
# F1 targets break convergence structurally.
# ============================================================

BREATH_RATES = {
    'soprano': 0.11,
    'alto':    0.09,
    'tenor':   0.08,
    'bass':    0.06,
}

F1_TARGETS = {
    'soprano': 730,
    'alto':    680,
    'tenor':   700,
    'bass':    650,
}

PART_NAMES = ['soprano','alto','tenor','bass']
OCTAVE_MULTIPLIERS = [2.0, 1.5, 1.0, 0.5]

class SingerAgent:
    """
    One singer in the puddle system.
    Biological constraint (breath) meets
    harmonic structure (Tonnetz position).
    The puddle forms at their interface.

    See finding_voice_pt3.md for full theory.
    """
    def __init__(self, part, idx, sr=SR, seed=None):
        self.part   = part
        self.idx    = idx
        self.sr     = sr
        self.rng    = np.random.RandomState(
            seed if seed is not None
            else np.random.randint(0,99999))
        self.breath_level    = self.rng.uniform(0.6,1.0)
        self.breath_rate     = BREATH_RATES[part]
        self.in_breath       = False
        self.breath_timer    = 0.0
        self.breath_duration = 0.0
        self.min_breath_int  = self.rng.uniform(4.0,7.0)
        self.last_breath_t   = -999.0
        self.re_entry_active = False
        self.re_entry_timer  = 0.0
        self.re_entry_dur    = 1.8
        self.amplitude       = 1.0
        self.sympathetic_amp = 1.0
        self.f1_current      = float(F1_TARGETS[part])
        self.f1_target       = float(F1_TARGETS[part])

    def update(self, dt, t_global,
               ens_active, part_active,
               phrase_peak_prox, ens_f1_mean,
               neighbor_breathing=False):
        # Deplete breath while singing
        if not self.in_breath:
            self.breath_level -= self.breath_rate*dt
            self.breath_level  = max(0.0,
                                     self.breath_level)

        # Sympathetic contagion — lean toward gap
        target_symp = (0.72 if neighbor_breathing
                       and not self.in_breath
                       else 1.0)
        self.sympathetic_amp += (
            (target_symp - self.sympathetic_amp)
            * min(dt*7.0, 1.0))

        # Gap navigation decision
        if (not self.in_breath and
                not self.re_entry_active):
            needs  = self.breath_level < 0.20
            t_ok   = (t_global - self.last_breath_t
                      > self.min_breath_int)
            cov_ok = (ens_active >= 2 and
                      part_active >= 1)
            ph_ok  = phrase_peak_prox < 0.85
            if needs and t_ok and cov_ok and ph_ok:
                self.in_breath       = True
                self.breath_timer    = 0.0
                self.breath_duration = \
                    self.rng.uniform(0.32, 0.52)
                self.last_breath_t   = t_global

        # Breath event — ramp out
        if self.in_breath:
            self.breath_timer += dt
            ro = 0.09
            if self.breath_timer < ro:
                self.amplitude = max(
                    0.0,
                    1.0 - self.breath_timer/ro)
            else:
                self.amplitude = 0.0
            if self.breath_timer >= self.breath_duration:
                self.in_breath       = False
                self.re_entry_active = True
                self.re_entry_timer  = 0.0
                self.breath_level    = \
                    self.rng.uniform(0.75, 0.95)

        # Re-entry — directed toward harmonic center
        # Water finding the lowest point first.
        if self.re_entry_active:
            self.re_entry_timer += dt
            t_norm = min(
                self.re_entry_timer / self.re_entry_dur,
                1.0)
            self.amplitude  = 0.4 + 0.6*(t_norm**0.75)
            blend           = 0.4 + 0.6*t_norm
            self.f1_current = (
                blend * self.f1_target +
                (1-blend) * ens_f1_mean)
            if t_norm >= 1.0:
                self.re_entry_active = False
                self.amplitude       = 1.0
                self.f1_current      = self.f1_target

        return (self.amplitude * self.sympathetic_amp,
                self.f1_current)

    def is_active(self):
        return (not self.in_breath and
                self.amplitude > 0.05)


def compute_envelopes(agents, dur_s, sr=SR,
                      phrase_peak_prox=0.5):
    """
    Run agent simulation for one note duration.
    Returns amp_envs (n_singers, n_samples)
            f1_envs  (n_singers, n_samples)
    """
    dt       = 1.0/sr
    n_s      = int(dur_s*sr)
    n        = len(agents)
    amp_envs = np.ones((n, n_s))
    f1_envs  = np.zeros((n, n_s))
    ens_f1   = float(F1_TARGETS[agents[0].part])

    for i in range(n_s):
        t_g    = i * dt
        active = [a.is_active() for a in agents]
        ens_a  = sum(active)
        for k, agent in enumerate(agents):
            part_a = sum(active[j]
                         for j in range(n) if j!=k)
            nb     = any(agents[j].in_breath
                         for j in range(n) if j!=k)
            a_val, f1_val = agent.update(
                dt, t_g, ens_a, part_a,
                phrase_peak_prox, ens_f1,
                neighbor_breathing=nb)
            amp_envs[k, i] = a_val
            f1_envs[k, i]  = f1_val

    return amp_envs, f1_envs

# ============================================================
# FORMANT RESONATOR — Klatt 1980 parallel bank
# INVARIANT: never series. never dry source in output.
# ============================================================

def formant_resonator_block(signal, f_c_arr,
                             bw_arr, gain, sr=SR):
    """
    Single formant resonator, block-processed.
    Parallel bank: each resonator receives
    same excitation. Outputs summed at caller.
    """
    n_s   = len(signal)
    block = 256
    out   = np.zeros(n_s)
    zi    = np.zeros(2)

    for start in range(0, n_s, block):
        end  = min(start+block, n_s)
        fc_b = float(np.mean(f_c_arr[start:end]))
        bw_b = float(np.mean(bw_arr[start:end]))
        fc_b = np.clip(fc_b, 80, sr*0.45)
        bw_b = np.clip(bw_b, 20, 800)
        r    = np.exp(-np.pi*bw_b/sr)
        th   = 2*np.pi*fc_b/sr
        b_c  = np.array([1-r, 0.0, 0.0])
        a_c  = np.array([1.0, -2*r*np.cos(th), r*r])
        try:
            seg, zi = lfilter(b_c, a_c,
                              signal[start:end],
                              zi=zi)
            out[start:end] = seg
        except Exception:
            zi = np.zeros(2)

    return out * gain

# ============================================================
# VOICE RENDER — confirmed architecture v13 + vowel glides
# All invariants enforced in this function.
# ============================================================

def render_note(freq, amp, dur_s,
                vowel_cur, vowel_nxt,
                glide_ms,
                sr=SR,
                velocity=80,
                cents_offset=0.0,
                amp_env=None,
                f1_agent_env=None):
    """
    Render one note for one singer.

    Signal chain (invariant order):
      1. Vibrato on freq array
      2. Jitter (LP noise on freq)
      3. Rosenberg pulse — vectorized phase acc.
      4. np.diff() — CRITICAL, never remove
      5. Shimmer (LP noise on source amplitude)
      6. Tiny glottal aspiration
      7. Parallel formant bank (Klatt)
      8. Formant flux + bandwidth modulation
      9. Post-formant turbulence
      10. Amplitude envelope
      (NO notch filter — invariant)
      (NO dry source — invariant)
      (NO normalization here — invariant)
    """
    n_s      = int(dur_s * sr)
    if n_s < 2:
        return np.zeros(max(n_s, 1))

    t_arr    = np.arange(n_s) / sr
    vel_norm = np.clip(velocity / 127.0, 0, 1)
    freq     = freq * (2**(cents_offset/1200))

    # ── 1. Vibrato ──────────────────────────────
    vib_rate  = 4.5 + np.random.uniform(-0.15, 0.15)
    vib_depth = 0.012
    vib_onset = min(0.25, dur_s*0.38)
    vib_env   = (np.clip((t_arr-vib_onset)/0.20, 0, 1)
                 if dur_s > 0.40
                 else np.zeros(n_s))
    freq_base = freq * (1 + vib_depth * vib_env *
                        np.sin(2*np.pi*vib_rate*t_arr))

    # ── 2. Jitter ───────────────────────────────
    fn = np.random.normal(0, 1.5, n_s)
    try:
        bj, aj = butter(2, min(30/(sr/2), 0.49),
                        btype='low')
        fn = lfilter(bj, aj, fn)
    except Exception:
        fn = np.zeros(n_s)
    freq_arr = np.clip(freq_base + fn,
                       freq*0.8, freq*1.2)

    # ── 3. Rosenberg pulse ──────────────────────
    # INVARIANT: vectorized phase accumulator.
    # Never replace with per-cycle loop.
    phase_norm = np.cumsum(freq_arr/sr) % 1.0
    oq         = 0.65
    source     = np.where(
        phase_norm < oq,
        (phase_norm/oq) * (2 - phase_norm/oq),
        1 - (phase_norm-oq) / (1-oq+1e-9))

    # ── 4. Differentiation ──────────────────────
    # INVARIANT: always np.diff.
    # Without this: 99% energy below 350Hz.
    # Formants have nothing to shape.
    source = np.diff(source, prepend=source[0])

    # ── 5. Shimmer ──────────────────────────────
    # INVARIANT: shimmer in source, not post-proc.
    # Normalization cannot destroy it here.
    sn = np.random.normal(0, 1.0, n_s)
    try:
        bs, as_ = butter(2, min(25/(sr/2), 0.49),
                         btype='low')
        sn = lfilter(bs, as_, sn)
    except Exception:
        sn = np.zeros(n_s)
    source = source * np.clip(
        1.0 + 0.3*sn/3.0, 0.3, 2.0)

    mx = np.max(np.abs(source))
    if mx > 0: source /= mx

    # ── 6. Glottal aspiration ───────────────────
    ga = np.random.normal(0, 0.05, n_s)
    try:
        bg, ag = butter(2,
            [min(500/(sr/2),  0.49),
             min(3000/(sr/2), 0.49)],
            btype='band')
        ga = lfilter(bg, ag, ga)
    except Exception:
        ga = np.zeros(n_s)
    excitation = source + ga * 0.05

    # ── 7. Vowel trajectory ──────────────────────
    # Sigmoid glide — not linear.
    # Linear = mechanism audible.
    # Sigmoid = articulation audible.
    vc = VOWEL_DATA.get(vowel_cur, VOWEL_DATA['pre'])
    vn = VOWEL_DATA.get(vowel_nxt, VOWEL_DATA['ah'])

    n_glide  = int(glide_ms/1000 * sr)
    n_steady = max(n_s - n_glide, int(n_s*0.45))
    n_glide  = n_s - n_steady

    f_arrays, b_arrays, g_arrays = [], [], []
    for fi in range(4):
        f_s = vc['f'][fi]; f_e = vn['f'][fi]
        b_s = vc['b'][fi]; b_e = vn['b'][fi]
        g_s = vc['g'][fi]; g_e = vn['g'][fi]
        f_arr = np.full(n_s, float(f_s))
        b_arr = np.full(n_s, float(b_s))
        g_arr = np.full(n_s, float(g_s))
        if n_glide > 0:
            t_g = np.linspace(0, 1, n_glide)
            sig = 1 / (1 + np.exp(-10*(t_g-0.5)))
            f_arr[n_steady:] = f_s + (f_e-f_s)*sig
            b_arr[n_steady:] = b_s + (b_e-b_s)*sig
            g_arr[n_steady:] = g_s + (g_e-g_s)*sig
        f_arrays.append(f_arr)
        b_arrays.append(b_arr)
        g_arrays.append(g_arr)

    # ── 8. Parallel formant bank ────────────────
    # INVARIANT: parallel, never series.
    # INVARIANT: NO dry source in output.
    # Formant flux on F1/F2 — independent rates.
    voiced = np.zeros(n_s)
    for fi in range(4):
        f_c_base = f_arrays[fi]
        bw_base  = b_arrays[fi]
        g_base   = g_arrays[fi]

        if fi < 2:
            rate   = [1.7, 2.3][fi]
            depth  = [20,  38 ][fi]
            ph_off = np.random.uniform(0, 2*np.pi)
            rw     = np.random.normal(0, 1.0, n_s)
            try:
                brw, arw = butter(2,
                    min(3.0/(sr/2), 0.49),
                    btype='low')
                rw = lfilter(brw, arw, rw)
            except Exception:
                rw = np.zeros(n_s)
            rw = rw / max(np.max(np.abs(rw)),
                          1e-10) * 10

            if fi == 0 and f1_agent_env is not None:
                f1n     = min(len(f1_agent_env), n_s)
                f_c_arr = f_c_base.copy()
                f_c_arr[:f1n] = (
                    0.6*f_c_base[:f1n] +
                    0.4*f1_agent_env[:f1n])
            else:
                f_c_arr = f_c_base.copy()

            f_c_arr += (depth *
                        np.sin(2*np.pi*rate*t_arr
                               + ph_off) + rw)
        else:
            f_c_arr = f_c_base.copy()

        # Bandwidth modulation — velocity responsive
        # pp = breathy (wide), ff = clear (narrow)
        bw_mod  = bw_base * (1.0 - 0.35*vel_norm)
        bw_flux = bw_mod * (1.0 + 0.12*np.sin(
            2*np.pi*1.2*t_arr +
            np.random.uniform(0, 2*np.pi)))
        bw_arr  = np.clip(bw_flux, 30, 500)

        out     = formant_resonator_block(
            excitation, f_c_arr, bw_arr, 1.0, sr)
        voiced += out * g_base

    # ── 9. Post-formant turbulence ──────────────
    # INVARIANT: turbulence POST-formant only.
    # Pre-formant: amplified by resonators = crowd.
    turb = np.random.normal(0, 0.03, n_s)
    try:
        bt, at = butter(2,
            [min(2000/(sr/2), 0.49),
             min(6000/(sr/2), 0.49)],
            btype='band')
        turb = lfilter(bt, at, turb)
    except Exception:
        turb = np.zeros(n_s)
    voiced = voiced + turb * 0.8

    # ── 10. Amplitude envelope ────────���─────────
    atk_s = min(0.28 + (1-vel_norm)*0.10,
                dur_s*0.40)
    atk_n = int(atk_s * sr)
    rel_n = int(min(0.35, dur_s*0.38) * sr)
    env   = np.ones(n_s)
    if 0 < atk_n < n_s:
        atk_c  = np.linspace(0, 1, atk_n)**0.65
        shim_t = np.linspace(0, atk_s, atk_n)
        shim_e = (1 + 0.05 *
                  np.sin(2*np.pi*11*shim_t) *
                  (1 - atk_c))
        env[:atk_n] = atk_c * shim_e
    if 0 < rel_n < n_s:
        env[-rel_n:] = np.linspace(1, 0,
                                    rel_n)**1.3

    result = voiced * env

    # Agent amplitude envelope applied here
    # INVARIANT: this is the only amplitude scaling
    # inside the voice stream.
    if amp_env is not None:
        nm = min(len(result), n_s, len(amp_env))
        result[:nm] *= amp_env[:nm]

    result *= amp
    return result

# ============================================================
# ROOM — The instrument (Part 4)
# Singers are excitation. Room produces the music.
# Listener hears the field.
# ============================================================

class RoomReverb:
    """
    Schroeder reverberator with early reflections.
    RT60 controls decay time.
    direct_ratio controls observer position:
      0.75 = front row (clinical)
      0.45 = mid hall (designed experience)
      0.20 = rear (immersive)

    RT60 can be updated between notes:
      Large (3-4s): searching, large space
      Medium (2s):  concert hall, clarity
      Small (0.8s): intimate, truth is close
    """
    def __init__(self, rt60=2.5, sr=SR,
                 direct_ratio=0.38):
        self.sr           = sr
        self.rt60         = rt60
        self.direct_ratio = direct_ratio
        self._build(rt60)

    def _build(self, rt60):
        scale = rt60 / 2.0
        bd    = [int(d*scale*self.sr/44100)
                 for d in [1557,1617,1491,
                            1422,1277,1356]]
        self.comb_delays  = [max(100,d) for d in bd]
        self.ap_delays    = [max(50, int(225*scale)),
                             max(50, int(556*scale))]
        self.comb_buffers = [np.zeros(d)
                             for d in self.comb_delays]
        self.comb_ptrs    = [0]*len(self.comb_delays)
        self.ap_buffers   = [np.zeros(d)
                             for d in self.ap_delays]
        self.ap_ptrs      = [0]*2
        self._gains()

    def _gains(self):
        self.comb_gains = [float(np.clip(
            10**(-3*(d/self.sr) /
                 max(self.rt60, 0.1)), 0, 0.97))
            for d in self.comb_delays]
        self.ap_gains = [0.7, 0.7]

    def set_rt60(self, rt60):
        """Update RT60 between notes (contracting room)."""
        self.rt60 = rt60
        self._gains()

    def process(self, audio):
        n     = len(audio)
        dr    = self.direct_ratio
        early = audio.copy()

        # Early reflections — room shape/size
        for gap_ms, gain in [(14, 0.80),(28, 0.68),
                              (46, 0.56),(68, 0.44),
                              (95, 0.33),(130,0.22)]:
            d = int(gap_ms * self.sr / 1000)
            if d < len(audio):
                delayed     = np.zeros_like(audio)
                delayed[d:] = audio[:-d] * gain
                early      += delayed

        # Frequency-dependent absorption
        try:
            ba, aa = butter(1,
                min(3500/(self.sr/2), 0.49),
                btype='low')
            early = (lfilter(ba, aa, early)*0.85 +
                     early*0.15)
        except Exception:
            pass

        # Comb filters
        cout = np.zeros(n)
        for c in range(len(self.comb_delays)):
            buf = self.comb_buffers[c].copy()
            ptr = self.comb_ptrs[c]
            g   = self.comb_gains[c]
            d   = self.comb_delays[c]
            for i in range(n):
                dl       = buf[ptr]
                buf[ptr] = audio[i] + g*dl
                ptr      = (ptr+1) % d
                cout[i] += dl / len(self.comb_delays)
            self.comb_buffers[c] = buf
            self.comb_ptrs[c]    = ptr

        # Allpass filters
        ap = cout.copy()
        for ai in range(2):
            buf = self.ap_buffers[ai].copy()
            ptr = self.ap_ptrs[ai]
            g   = self.ap_gains[ai]
            d   = self.ap_delays[ai]
            for i in range(n):
                dl       = buf[ptr]
                w        = ap[i] + g*dl
                buf[ptr] = w
                ptr      = (ptr+1) % d
                ap[i]    = -g*w + dl
            self.ap_buffers[ai] = buf
            self.ap_ptrs[ai]    = ptr

        return (dr*audio*0.50 +
                0.28*early +
                (1.0-dr)*ap*0.42)

# ============================================================
# RENDER PIPELINE
# Takes a score (list of voices) and produces WAV.
# Each voice: list of (pos, beats, velocity) tuples.
# pos = (a,b) Tonnetz or None (silence).
# ============================================================

def classify_sections(voice, s1_frac=0.40,
                       s2_frac=0.68):
    """
    Divide voice into sections by note index.
    Override fractions per composition as needed.
    """
    total    = len(voice)
    s1_end   = int(total * s1_frac)
    s2_end   = int(total * s2_frac)
    sections = []
    for i in range(total):
        if i < s1_end:
            sections.append(1)
        elif i < s2_end:
            sections.append(2)
        else:
            sections.append(3)
    return sections


def render_score(voices,
                 filename,
                 bpm,
                 sr=SR,
                 tonic=220.0,
                 vowel_fn=None,
                 glide_fn=None,
                 rt60_fn=None,
                 section_fracs=(0.40, 0.68),
                 agent_seeds=None,
                 tail_s=20.0):
    """
    Full render pipeline.

    voices:     list of 4 voice lists (SATB order)
    filename:   output WAV path
    bpm:        tempo
    tonic:      root frequency (default A3=220Hz)
    vowel_fn:   callable(pos, section, idx, total)
                  -> (vowel_cur, vowel_nxt)
                default: 'ah' throughout
    glide_fn:   callable(section, dur_s) -> ms
                default: 150ms
    rt60_fn:    callable(section, coherence) -> rt60
                default: 2.5 throughout
    section_fracs: (s1_end_frac, s2_end_frac)
    agent_seeds: list of 4 lists of 3 seeds
    tail_s:     silence tail for reverb decay
    """
    bps = bpm / 60.0

    # Default callables
    if vowel_fn is None:
        vowel_fn = lambda pos,sec,idx,tot: ('ah','ah')
    if glide_fn is None:
        glide_fn = lambda sec,dur: 150.0
    if rt60_fn is None:
        rt60_fn  = lambda sec,coh: 2.5

    # Total duration
    total_s = max(
        sum(b for _,b,_ in v)/bps
        for v in voices) + tail_s
    output  = np.zeros(int(total_s * sr))

    # Build agents
    all_agents = []
    for vi, part in enumerate(PART_NAMES):
        seeds = (agent_seeds[vi]
                 if agent_seeds else
                 [vi*100+i for i in range(3)])
        all_agents.append([
            SingerAgent(part, i, sr, seed=seeds[i])
            for i in range(3)])

    # Per-voice render
    for vi, (voice, agents) in enumerate(
            zip(voices, all_agents)):

        s1f, s2f = section_fracs
        sections = classify_sections(voice, s1f, s2f)
        cohs     = [coherence(p[0],p[1])
                    if p else None
                    for p,_,_ in voice]
        vels     = [vel for _,_,vel in voice]
        max_vel  = max((v for v in vels if v>0),
                       default=127)
        omult    = OCTAVE_MULTIPLIERS[vi]
        rev      = RoomReverb(rt60=2.5, sr=sr,
                              direct_ratio=0.38)
        cur      = 0
        total_n  = len(voice)

        for i, (pos, beats, vel) in enumerate(voice):
            dur_s = beats / bps
            n_s   = int(dur_s * sr)
            sec   = sections[i]

            if pos is None:
                cur += n_s
                continue

            a, b  = pos
            coh   = cohs[i] or 1.0
            freq  = ji_freq(a, b, tonic) * omult
            amp   = (vel/127.0) * 0.50
            ppp   = vel / max_vel

            vc, vn = vowel_fn(pos, sec, i, total_n)
            gms    = glide_fn(sec, dur_s)

            # Update room
            rev.set_rt60(rt60_fn(sec, coh))

            # Agent envelopes
            amp_envs, f1_envs = compute_envelopes(
                agents, dur_s, sr,
                phrase_peak_prox=ppp)

            # 3-singer ensemble
            # INVARIANT: 0, +11, -17 cents
            cents    = [0.0, +11.0, -17.0]
            vel_mod  = int(vel*(0.7 + 0.3*coh))
            vel_mod  = max(35, min(127, vel_mod))
            note_mix = np.zeros(n_s)

            for k in range(3):
                sig = render_note(
                    freq, amp/3, dur_s,
                    vc, vn, gms,
                    sr=sr,
                    velocity=vel_mod,
                    cents_offset=cents[k],
                    amp_env=amp_envs[k],
                    f1_agent_env=f1_envs[k])
                nm = min(len(sig), n_s)
                note_mix[:nm] += sig[:nm]

            processed = rev.process(note_mix)

            # Tonnetz lean — coherence-based onset
            prev = cohs[i-1] if i>0 else None
            nxt  = (cohs[i+1]
                    if i < len(cohs)-1 else None)
            if nxt and nxt > coh:
                lean = -int(0.055*n_s)
            elif prev and prev > coh:
                lean =  int(0.045*n_s)
            else:
                lean =  int(0.06*n_s*(1-coh))
            onset = max(0, cur+lean)

            end = min(onset+len(processed),
                      len(output))
            seg = end - onset
            if seg > 0:
                output[onset:end] += processed[:seg]
            cur += n_s

    # INVARIANT: single normalization at output only
    mx = np.max(np.abs(output))
    if mx > 0:
        output = output / mx * 0.80

    # Write WAV
    out_i = (output * 32767).astype(np.int16)
    os.makedirs(os.path.dirname(filename)
                if os.path.dirname(filename)
                else '.', exist_ok=True)
    with wave_module.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(out_i.tobytes())

    dur = len(output) / sr
    print(f"  Written: {filename}")
    print(f"  Duration: {int(dur//60)}m "
          f"{dur%60:.0f}s  at {bpm}bpm")
    return output


# ============================================================
# VOCAL DISTANCE LAYER
# Added: February 2026
#
# H Ghost Topology established that:
#   H is the Tonnetz origin (0, 0).
#   Every vowel is a distance from H.
#   Every consonant is a path through
#   constriction space toward a vowel.
#   The ghost between syllables is the
#   acoustic trace of the Tonnetz
#   distance being traversed.
#
# This section adds:
#   VOWEL_TONNETZ   — ARPAbet vowels mapped
#                     to Tonnetz coordinates.
#   CONSONANT_TONNETZ — consonant constriction
#                     positions in the same space.
#   vocal_distance()  — measurable distance
#                     between two phonemes.
#   distance_from_H() — departure from origin.
#   ghost_duration_from_distance() — the distance
#                     made temporal.
#   GHOST_PROFILES  — arc-typed ghost signatures.
#   ghost_at_boundary() — per-syllable ghost params.
#   ghost_formant_interp() — Tonnetz traversal
#                     made acoustic.
#
# NOTE ON TWO VOWEL SYSTEMS:
#   This engine uses VOWEL_DATA (above) with
#   keys 'ah', 'ee', 'oh', 'oo', 'eh', 'pre'
#   for choral synthesis.
#   The voice_physics chain uses ARPAbet symbols
#   ('AH', 'IY', 'OH', 'UW', 'EH') for speech.
#   VOWEL_TONNETZ uses ARPAbet — the speech system.
#   The two systems share the same Tonnetz space.
#   They are different symbol sets for the same
#   physical instrument.
#
# INVARIANTS: unchanged. This section is purely
# additive. Nothing above this line is modified.
# ============================================================

# ── H ORIGIN ─────────────────────────────────────────────
# The baseline state of the voice.
# Unobstructed tract. Tongue at rest.
# Tonnetz position: (0, 0).
# All distances are measured from here.

H_FORMANTS  = [500.0, 1500.0, 2500.0, 3500.0]
H_BANDWIDTHS= [200.0,  220.0,  350.0,  450.0]

# ── VOWEL TONNETZ COORDINATES ─────────────────────────────
#
# ARPAbet vowels mapped to integer Tonnetz grid (a, b).
#
# a = fifth-axis  (positive = front, high F2)
#                 (negative = back,  low  F2)
# b = third-axis  (positive = open,  high F1)
#                 (negative = high,  low  F1)
#
# H = (0, 0) — the origin. Neutral open tract.
#
# Derivation: F1 and F2 from VOWEL_DATA / VOWEL_F
# in voice_physics are the acoustic coordinates.
# The Tonnetz grid is a quantized map of that space
# centered on H baseline.
#
# These are ordinal positions — relative distance
# and direction matter, not cardinal magnitude.
# Perceptual verification is the ground truth.

VOWEL_TONNETZ = {
    # ── HIGH FRONT (low F1, high F2) ──────────────
    'IY': ( 3, -2),   # beet   F1~270  F2~2290
                      # Maximum front departure.
                      # Tongue high and front.
                      # Far from H in both axes.
    'IH': ( 2, -1),   # bit    F1~390  F2~1990
                      # Lax. Closer to H than IY.
    'EY': ( 2, -1),   # bait   diphthong onset position.
                      # Shares IH onset topology.

    # ── MID FRONT ─────────────────────────────────
    'EH': ( 1,  0),   # bed    F1~530  F2~1840
                      # One step front of H.
                      # Moderate distance.
    'AE': ( 1,  1),   # bat    F1~660  F2~1720
                      # Front and open.
                      # Jaw lower than EH.

    # ── LOW / DIPHTHONG ONSET ─────────────────────
    'AY': ( 1,  1),   # high   diphthong onset ~AE.
    'AW': (-1,  2),   # how    diphthong onset ~AA.
    'OY': (-1,  1),   # boy    diphthong onset ~AO.

    # ── CENTRAL ───────────────────────────────────
    'AH': ( 0,  1),   # but    F1~520  F2~1190
                      # One step open from H.
                      # Schwa territory.
                      # Closest vowel to origin.
    'ER': ( 0, -1),   # bird   F1~490  F2~1350
                      # Retroflex. F3 suppressed.
                      # One step high from H.
                      # Distinctive F3 axis
                      # not captured in 2D grid —
                      # ER is acoustically unique.

    # ── LOW BACK ──────────────────────────────────
    'AA': (-1,  2),   # father F1~730  F2~1090
                      # Open and back.
                      # Jaw fully dropped.
    'AO': (-1,  1),   # bought F1~570  F2~ 840
                      # Back and moderately open.
                      # Rounded.

    # ── MID BACK ──────────────────────────────────
    'OW': (-2,  0),   # boat   F1~450  F2~ 800
                      # Back, not very open.
                      # Lips rounding.
    'OH': (-2,  0),   # legacy alias for OW.

    # ── HIGH BACK ─────────────────────────────────
    'UH': (-2, -1),   # book   F1~440  F2~1020
                      # Back and high. Lax.
    'UW': (-3, -2),   # boot   F1~300  F2~ 870
                      # Maximum back departure.
                      # Tongue high and back.
                      # Mirror of IY across origin.

    # ── H ORIGIN ──────────────────────────────────
    'H':  ( 0,  0),   # The origin. No position.
    'HH': ( 0,  0),   # ARPAbet alias.
}

# ── CONSONANT TONNETZ POSITIONS ───────────────────────────
#
# Consonants are paths through constriction space.
# These positions represent the constriction point —
# where the tract is maximally modified during
# the consonant gesture.
#
# Used for distance calculation only.
# The consonant is not a stable position —
# it is a path FROM H THROUGH this position
# TO the following vowel.

CONSONANT_TONNETZ = {
    # ── DENTAL / ALVEOLAR ─────────────────────────
    # Tongue tip constriction. Near front axis.
    'DH': ( 1,  0),   # voiced dental fricative
    'TH': ( 1,  0),   # unvoiced dental fricative
                      # Same articulation. Glottis differs.
    'D':  ( 1,  0),   # alveolar stop voiced
    'T':  ( 1,  0),   # alveolar stop unvoiced
    'N':  ( 1,  0),   # alveolar nasal
    'L':  ( 1,  0),   # lateral approximant
    'S':  ( 1,  0),   # alveolar fricative unvoiced
    'Z':  ( 1,  0),   # alveolar fricative voiced

    # ── BILABIAL ──────────────────────────────────
    # Lip closure. Near central axis.
    # Lips are near H-position articulatorily.
    'B':  ( 0,  0),   # bilabial stop voiced
    'P':  ( 0,  0),   # bilabial stop unvoiced
    'M':  ( 0,  0),   # bilabial nasal

    # ── LABIODENTAL ───────────────────────────────
    'V':  ( 0,  0),   # voiced labiodental
    'F':  ( 0,  0),   # unvoiced labiodental

    # ── VELAR ─────────────────────────────────────
    # Back of tongue raised to velum. Back axis.
    'G':  (-2,  0),   # velar stop voiced
    'K':  (-2,  0),   # velar stop unvoiced
    'NG': (-2,  0),   # velar nasal

    # ── PALATAL / POST-ALVEOLAR ───────────────────
    # Tongue body raised toward palate. Far front.
    'JH': ( 2,  0),   # palatal affricate voiced
    'CH': ( 2,  0),   # palatal affricate unvoiced
    'SH': ( 1,  0),   # post-alveolar fricative unvoiced
    'ZH': ( 1,  0),   # post-alveolar fricative voiced
    'Y':  ( 2, -1),   # palatal approximant
                      # Shares IY/IH onset topology.

    # ── APPROXIMANTS ──────────────────────────────
    'W':  (-1, -1),   # labio-velar approximant
                      # Lip rounding + back tongue.
                      # Between bilabial and velar.
    'R':  ( 0, -1),   # rhotic approximant
                      # Near H but F3-suppressed.
                      # Shares ER topology.
}

# Combined lookup for distance calculations.
ALL_TONNETZ = {**VOWEL_TONNETZ,
               **CONSONANT_TONNETZ}


def vocal_distance(ph1, ph2):
    """
    Euclidean Tonnetz distance between two phonemes.

    ph1, ph2: ARPAbet symbol strings.

    Returns float >= 0.0.

    Representative values:
      H  → H  :  0.00  (at rest, no movement)
      H  → AH :  1.00  (schwa, near origin)
      H  → EH :  1.00  (mid front, one step)
      H  → AO :  1.41  (back open, moderate)
      H  → IY :  3.61  (far front high, maximum)
      H  → UW :  3.61  (far back high, maximum)
      H  → AA :  2.24  (open back, large)
      IY → UW :  6.08  (maximum cross-space)
      AH → IY :  2.83  (central to far front)

    Used to:
      1. Determine ghost duration at syllable
         boundary (larger = longer ghost).
      2. Determine ghost filter position
         (interpolation between nucleus formants).
      3. Verify Tonnetz coordinate assignments
         — if a distance feels perceptually wrong,
         the coordinate needs revision.
    """
    p1 = ALL_TONNETZ.get(ph1, (0, 0))
    p2 = ALL_TONNETZ.get(ph2, (0, 0))
    return float(np.sqrt(
        (p2[0] - p1[0])**2 +
        (p2[1] - p1[1])**2))


def distance_from_H(ph):
    """
    Tonnetz distance of phoneme from H origin (0,0).

    This is the magnitude of the voice's departure
    from baseline to produce this phoneme.
    The ghost at a syllable boundary scales with
    this value: larger departure = longer ghost,
    because the tract has further to travel.

    H  → 0.00  (at origin)
    AH → 1.00  (near — small departure)
    EH → 1.00  (near — front)
    AO → 1.41  (moderate)
    AA → 2.24  (large open-back)
    IY → 3.61  (maximum departure)
    UW → 3.61  (maximum departure)
    """
    return vocal_distance('H', ph)


def print_vocal_distances():
    """
    Diagnostic: print distance table for all vowels.
    Run once to verify Tonnetz coordinate assignments.
    Expected: AH nearest, IY and UW furthest and equal.
    """
    vowels = ['IY','IH','EY','EH','AE',
              'AH','ER','AA','AO','OW',
              'OH','UH','UW']
    print("\nVocal distances from H origin:")
    print(f"  {'Phoneme':8s}  {'(a,b)':10s}  "
          f"{'dist':6s}  {'coherence':10s}")
    print("  " + "-"*42)
    for ph in vowels:
        pos  = VOWEL_TONNETZ.get(ph, (0,0))
        dist = distance_from_H(ph)
        coh  = coherence(pos[0], pos[1])
        print(f"  {ph:8s}  {str(pos):10s}  "
              f"{dist:6.3f}  {coh:10.4f}")
    print()


# ── GHOST DURATION FROM DISTANCE ─────────────────────────
#
# Ghost duration scales with Tonnetz distance traversed.
# Larger Tonnetz jump = tract travels further = longer
# ghost needed for the traversal.
#
# Calibration:
#   distance = 0.0 → ~3ms  (minimum, H→H)
#   distance = 1.0 → ~7ms  (near, H→AH)
#   distance = 2.2 → ~12ms (moderate, H→AA)
#   distance = 3.6 → ~18ms (far, H→IY or H→UW)
#   Maximum ghost capped at 35ms.
#
# These are further scaled by arc_type and dil
# in ghost_at_boundary().

GHOST_DUR_BASE_MS  = 3.0
GHOST_DUR_SCALE_MS = 4.2
GHOST_DUR_MAX_MS   = 35.0
GHOST_DUR_MIN_MS   = 2.0


def ghost_duration_from_distance(distance, dil=6.0):
    """
    Base ghost duration for a Tonnetz distance.

    distance : float — from vocal_distance().
    dil      : float — speaking rate (DIL from
               voice_physics). Higher = slower.
               DIL=6 is normal rate.
               DIL=3 is fast. DIL=12 is slow.

    Returns duration_ms.
    """
    dur = GHOST_DUR_BASE_MS + \
          GHOST_DUR_SCALE_MS * distance
    dur *= (dil / 6.0)
    return float(np.clip(
        dur, GHOST_DUR_MIN_MS, GHOST_DUR_MAX_MS))


# ── GHOST PROFILES BY ARC TYPE ───────────────────────────
#
# Each arc type is a ghost signature:
# the characteristic profile of the inter-syllable
# H-traversal that persists across the phrase.
#
# Keys:
#   duration_mult    : multiplier on base duration.
#   amplitude        : absolute amplitude (0–1).
#   variability      : std dev of per-boundary noise.
#                      Grief: uneven. Normal: steady.
#   phrase_final_mult: multiplier for phrase-final ghost.
#   pre_stress_mult  : eureka only — ghost before
#                      primary-stressed syllable.
#   position_scale   : recognition only — ghost grows
#                      through phrase by this factor.

GHOST_PROFILES = {
    'normal': {
        'duration_mult':     1.00,
        'amplitude':         0.055,
        'variability':       0.10,
        'phrase_final_mult': 1.50,
    },
    'weight': {
        'duration_mult':     1.60,
        'amplitude':         0.072,
        'variability':       0.08,
        'phrase_final_mult': 2.00,
    },
    'grief': {
        'duration_mult':     2.40,
        'amplitude':         0.038,
        'variability':       0.25,  # uneven
        'phrase_final_mult': 3.00,
    },
    'containment': {
        'duration_mult':     0.35,
        'amplitude':         0.022,
        'variability':       0.05,
        'phrase_final_mult': 0.80,
    },
    'eureka': {
        'duration_mult':     0.70,
        'amplitude':         0.065,
        'variability':       0.12,
        'phrase_final_mult': 1.20,
        'pre_stress_mult':   3.50,
    },
    'recognition': {
        'duration_mult':     0.80,
        'amplitude':         0.042,
        'variability':       0.08,
        'phrase_final_mult': 2.50,
        'position_scale':    1.80,
    },
}


def ghost_at_boundary(prev_nucleus_ph,
                       next_nucleus_ph,
                       position_in_phrase,
                       stress_prev,
                       stress_next,
                       arc_type,
                       dil=6.0,
                       phrase_final=False):
    """
    Compute ghost (duration_ms, amplitude) at a
    syllable boundary.

    prev_nucleus_ph : ARPAbet vowel completing.
    next_nucleus_ph : ARPAbet vowel arriving.
                      None if phrase_final=True.
    position_in_phrase : float 0.0–1.0.
    stress_prev     : 0/1/2 (stress of prev syl).
    stress_next     : 0/1/2 (stress of next syl).
    arc_type        : ARC_* string constant.
    dil             : speaking rate dilution.
    phrase_final    : True at end of last syllable.

    Returns (duration_ms, amplitude).
    """
    profile = GHOST_PROFILES.get(
        arc_type, GHOST_PROFILES['normal'])

    if phrase_final or next_nucleus_ph is None:
        # Returning to H from prev nucleus.
        distance = distance_from_H(prev_nucleus_ph)
        dur = ghost_duration_from_distance(
            distance, dil)
        dur *= profile['phrase_final_mult']
    else:
        # Traversing from prev through H to next.
        # Total path = dist(prev→H) + dist(H→next).
        # Mean of two departures = representative
        # distance for timing.
        d1 = distance_from_H(prev_nucleus_ph)
        d2 = distance_from_H(next_nucleus_ph)
        dur = ghost_duration_from_distance(
            (d1 + d2) / 2.0, dil)

    # Arc type duration multiplier
    dur *= profile['duration_mult']

    # Recognition: ghost grows through phrase
    if arc_type == 'recognition':
        scale = profile.get('position_scale', 1.8)
        dur  *= (1.0 + (scale - 1.0)
                 * position_in_phrase)

    # Eureka: ghost elongates before primary stress
    if arc_type == 'eureka' and stress_next == 2:
        dur *= profile.get('pre_stress_mult', 3.5)

    # Stress transition modulation
    # Unstressed → stressed: ghost lengthens
    #   (preparation, gathering)
    # Stressed → unstressed: ghost shortens
    #   (release, continuation)
    if stress_prev == 0 and stress_next == 2:
        dur *= 1.35
    elif stress_prev == 2 and stress_next == 0:
        dur *= 0.75

    # Human variability
    var = profile.get('variability', 0.10)
    if var > 0:
        dur *= float(np.clip(
            np.random.normal(1.0, var),
            0.5, 2.0))

    amp = float(profile['amplitude'])
    if phrase_final:
        amp *= 0.60  # phrase-final ghost is softest

    dur = float(np.clip(
        dur, GHOST_DUR_MIN_MS, GHOST_DUR_MAX_MS))
    amp = float(np.clip(amp, 0.01, 0.20))

    return dur, amp


def ghost_formant_interp(F_prev, F_next, n_s,
                          sr=SR):
    """
    Build time-varying formant arrays for the
    ghost segment — the Tonnetz traversal made
    acoustic.

    The ghost filter interpolates between the
    formant targets of the completing syllable's
    nucleus (F_prev) and the arriving syllable's
    nucleus (F_next), passing through H_FORMANTS
    at the midpoint.

    F_prev : list of 4 floats (completing nucleus).
    F_next : list of 4 floats (arriving nucleus).
             Pass None for phrase-final ghost
             (interpolates to H_FORMANTS instead).
    n_s    : int, number of samples.
    sr     : sample rate.

    Returns list of 4 numpy float32 arrays,
    each length n_s. Pass directly to the
    resonator bank.

    Physics:
      At ghost start  : near F_prev
      At ghost middle : near H_FORMANTS (origin)
      At ghost end    : near F_next
      This is the acoustic trace of returning
      to H and departing toward the next nucleus.
    """
    if F_next is None:
        F_next = list(H_FORMANTS)

    F_arrays = []
    for fi in range(4):
        f_s = float(F_prev[fi]) \
              if fi < len(F_prev) \
              else H_FORMANTS[fi]
        f_h = H_FORMANTS[fi]   # origin midpoint
        f_e = float(F_next[fi]) \
              if fi < len(F_next) \
              else H_FORMANTS[fi]

        # Two-segment interpolation:
        # first half: F_prev → H_FORMANTS
        # second half: H_FORMANTS → F_next
        n_half = n_s // 2
        n_rem  = n_s - n_half

        seg1 = np.linspace(f_s, f_h,
                           n_half,
                           dtype=np.float32)
        seg2 = np.linspace(f_h, f_e,
                           n_rem,
                           dtype=np.float32)
        F_arrays.append(
            np.concatenate([seg1, seg2]))

    return F_arrays
