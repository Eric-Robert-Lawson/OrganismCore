#!/usr/bin/env python3
"""
RATNADHĀTAMAM — Vedic Sanskrit Reconstruction
Rigveda 1.1.1 — Word 9

First word containing voiced aspirated stop [dʰ]
Critical validation of 4-way voicing/aspiration contrast

IPA: [rɑtnɑdʰaːtɑmɑm]
Devanāgarī: रत्नधातमम्

February 2026
"""

import numpy as np
from scipy import signal
import scipy.io.wavfile as wav

# ══════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════

SR = 44100
DTYPE = np.float32

NEUTRAL_ALVEOLAR_F3_HZ = 2700.0

# ── ŚIKṢĀ REFERENCES ──────────────────────────────────
DANTYA_BURST_LO_HZ = 3000.0
DANTYA_BURST_HI_HZ = 4500.0

# ── VS-INTERNAL VERIFIED REFERENCES ───────────────────
# From previous verified words
VS_T_BURST_HZ = 3764.0      # PUROHITAM
VS_D_BURST_HZ = 3500.0      # DEVAM
VS_N_F2_HZ = 900.0          # AGNI
VS_M_F2_HZ = 552.0          # PUROHITAM
VS_A_F1_HZ = 631.0          # AGNI
VS_A_F2_HZ = 1106.0         # AGNI

# ══════════════════════════════════════════════════════
# PHONEME PARAMETERS
# ══════════════════════════════════════════════════════

# [r] — alveolar trill (from OE, but single-tap variant for Vedic)
VS_R_F = [300.0, 1900.0, 2700.0, 3300.0]
VS_R_B = [120.0, 200.0, 250.0, 300.0]
VS_R_GAINS = [12.0, 6.0, 1.5, 0.4]
VS_R_DUR_MS = 30.0
VS_R_DIP_DEPTH = 0.35
VS_R_DIP_WIDTH = 0.40

# [ɑ] — short open central (AGNI verified)
VS_A_F = [700.0, 1100.0, 2550.0, 3400.0]
VS_A_B = [130.0, 160.0, 220.0, 280.0]
VS_A_GAINS = [16.0, 6.0, 1.5, 0.5]
VS_A_DUR_MS = 55.0
VS_A_COART_ON = 0.12
VS_A_COART_OFF = 0.12

# [t] — voiceless dental stop (PUROHITAM verified)
VS_T_CLOSURE_MS = 25.0
VS_T_BURST_F = 3500.0
VS_T_BURST_BW = 1500.0
VS_T_BURST_MS = 7.0
VS_T_VOT_MS = 15.0
VS_T_BURST_GAIN = 0.38

# [n] — dental nasal (AGNI verified)
VS_N_F = [250.0, 900.0, 2000.0, 3000.0]
VS_N_B = [100.0, 200.0, 300.0, 350.0]
VS_N_GAINS = [8.0, 2.5, 0.5, 0.2]
VS_N_DUR_MS = 60.0
VS_N_ANTI_F = 800.0
VS_N_ANTI_BW = 200.0
VS_N_COART_ON = 0.15
VS_N_COART_OFF = 0.15

# [dʰ] — VOICED DENTAL ASPIRATED STOP (NEW)
# Critical finding: Aspiration = breathy murmur (NOT voiceless gap)
# Based on Hindi/Marathi phonetics literature
VS_DH_CLOSURE_MS = 28.0         # Voiced closure (same as [d])
VS_DH_BURST_F = 3500.0          # Dental burst (same as [d], [t])
VS_DH_BURST_BW = 1500.0
VS_DH_BURST_MS = 8.0
VS_DH_BURST_GAIN = 0.28

# ASPIRATION = BREATHY MURMUR (30-60 ms typical)
VS_DH_MURMUR_MS = 45.0          # Target: 45 ms (middle of Hindi range)
VS_DH_MURMUR_TILT = 1.8         # Spectral tilt (attenuate higher harmonics)
VS_DH_MURMUR_NOISE = 0.25       # Turbulent noise mixing (leaky glottis)
VS_DH_MURMUR_H1H2_TARGET = 13.0 # Target H1-H2 = 13 dB
VS_DH_MURMUR_BW_MULT = 1.8      # Widen formant bandwidths (turbulence)

VS_DH_CLOSURE_VOICING = 0.70    # Voiced during closure

# [aː] — long open central (NEW)
VS_AA_F = [700.0, 1100.0, 2550.0, 3400.0]
VS_AA_B = [130.0, 160.0, 220.0, 280.0]
VS_AA_GAINS = [16.0, 6.0, 1.5, 0.5]
VS_AA_DUR_MS = 110.0            # Long: 2× short [ɑ]
VS_AA_COART_ON = 0.10
VS_AA_COART_OFF = 0.10

# [m] — bilabial nasal (PUROHITAM verified)
VS_M_F = [250.0, 900.0, 2200.0, 3000.0]
VS_M_B = [100.0, 200.0, 300.0, 350.0]
VS_M_GAINS = [8.0, 2.5, 0.5, 0.2]
VS_M_DUR_MS = 60.0
VS_M_ANTI_F = 800.0
VS_M_ANTI_BW = 200.0
VS_M_COART_ON = 0.15
VS_M_COART_OFF = 0.15

PITCH_HZ = 120.0
DIL = 1.0

# ══════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def rms(sig):
    return np.sqrt(np.mean(sig**2))

def write_wav(path, sig, sr=SR):
    sig_norm = sig / (np.max(np.abs(sig)) + 1e-10)
    sig_int = (sig_norm * 32767 * 0.95).astype(np.int16)
    wav.write(path, sr, sig_int)
    print(f"Wrote {path}")

def safe_bp(lo, hi, sr=SR):
    nyq = sr / 2.0
    lo = max(20.0, min(lo, nyq - 100))
    hi = min(hi, nyq - 100)
    if hi <= lo:
        hi = lo + 100
    sos = signal.butter(4, [lo, hi], btype='band', output='sos', fs=sr)
    return sos

def safe_lp(fc, sr=SR):
    nyq = sr / 2.0
    fc = min(fc, nyq - 100)
    sos = signal.butter(4, fc, btype='low', output='sos', fs=sr)
    return sos

def safe_hp(fc, sr=SR):
    fc = max(20.0, fc)
    sos = signal.butter(4, fc, btype='high', output='sos', fs=sr)
    return sos

def ola_stretch(sig, factor=4.0, sr=SR):
    """Time-stretch via overlap-add"""
    hop_in = int(sr * 0.010)  # 10ms
    hop_out = int(hop_in * factor)
    win_len = hop_in * 4
    window = np.hanning(win_len)
    
    out_len = int(len(sig) * factor)
    output = np.zeros(out_len, dtype=DTYPE)
    
    for i in range(0, len(sig) - win_len, hop_in):
        frame = sig[i:i+win_len] * window
        out_pos = int(i * factor)
        if out_pos + win_len <= out_len:
            output[out_pos:out_pos+win_len] += frame
    
    return output

def rosenberg_pulse(n_samples, pitch_hz, tilt=0.8, sr=SR):
    """
    Glottal pulse train (Rosenberg model)
    tilt: 0.8 = modal voice, 1.8 = breathy voice
    """
    output = np.zeros(n_samples, dtype=DTYPE)
    period_samples = int(sr / pitch_hz)
    
    for i in range(0, n_samples, period_samples):
        if i + period_samples > n_samples:
            break
        
        # Rising phase (40% of period)
        rise_samples = int(period_samples * 0.4)
        rise = np.linspace(0, 1, rise_samples)
        
        # Falling phase (60% of period)
        fall_samples = period_samples - rise_samples
        # Apply tilt (higher tilt = faster decay = weaker harmonics)
        fall = np.exp(-tilt * np.linspace(0, 5, fall_samples))
        
        pulse = np.concatenate([rise, fall])
        output[i:i+len(pulse)] = pulse
    
    return output

def apply_formants(src, freqs, bws, gains, sr=SR):
    """Apply formant resonances"""
    output = src.copy()
    for F, BW, G in zip(freqs, bws, gains):
        if F > 0 and BW > 0:
            # Resonator as bandpass filter
            sos = safe_bp(F - BW, F + BW, sr)
            filtered = signal.sosfilt(sos, output)
            output += filtered * (G / 10.0)
    return output

def iir_notch(sig, fc, bw=200.0, sr=SR):
    """IIR notch filter (for nasal antiresonance)"""
    Q = fc / bw
    b, a = signal.iirnotch(fc / (sr/2), Q)
    return signal.filtfilt(b, a, sig)

# ══════════════════════════════════════════════════════
# PHONEME SYNTHESIS FUNCTIONS
# ══════════════════════════════════════════════════════

def synth_R(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """Alveolar tap [ɾ]"""
    dur_ms = VS_R_DUR_MS * dil
    n_samples = int(dur_ms / 1000.0 * SR)
    
    # Voiced source with single dip (tap = single contact)
    source = rosenberg_pulse(n_samples, pitch_hz, tilt=0.8)
    
    # Apply amplitude dip in middle
    dip_start = int(n_samples * (0.5 - VS_R_DIP_WIDTH/2))
    dip_end = int(n_samples * (0.5 + VS_R_DIP_WIDTH/2))
    envelope = np.ones(n_samples)
    envelope[dip_start:dip_end] *= VS_R_DIP_DEPTH
    source *= envelope
    
    # Apply formants
    output = apply_formants(source, VS_R_F, VS_R_B, VS_R_GAINS)
    
    return output

def synth_A(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """Short open central vowel [ɑ]"""
    dur_ms = VS_A_DUR_MS * dil
    n_samples = int(dur_ms / 1000.0 * SR)
    
    # Modal voice
    source = rosenberg_pulse(n_samples, pitch_hz, tilt=0.8)
    
    # Apply formants
    output = apply_formants(source, VS_A_F, VS_A_B, VS_A_GAINS)
    
    # Coarticulation (if context provided)
    if F_prev is not None:
        on_samples = int(n_samples * VS_A_COART_ON)
        for i in range(on_samples):
            alpha = i / on_samples
            F_interp = [F_prev[j] * (1-alpha) + VS_A_F[j] * alpha for j in range(4)]
            frame = rosenberg_pulse(1, pitch_hz, tilt=0.8)
            output[i] = apply_formants(frame, F_interp, VS_A_B, VS_A_GAINS)[0]
    
    return output

def synth_T(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """Voiceless dental stop [t]"""
    closure_samples = int(VS_T_CLOSURE_MS / 1000.0 * SR)
    burst_samples = int(VS_T_BURST_MS / 1000.0 * SR)
    vot_samples = int(VS_T_VOT_MS / 1000.0 * SR)
    
    # Closure: silence
    closure = np.zeros(closure_samples, dtype=DTYPE)
    
    # Burst: dental transient
    burst_noise = np.random.randn(burst_samples).astype(DTYPE)
    sos = safe_bp(VS_T_BURST_F - VS_T_BURST_BW/2, 
                  VS_T_BURST_F + VS_T_BURST_BW/2)
    burst = signal.sosfilt(sos, burst_noise) * VS_T_BURST_GAIN
    
    # VOT: aspiration noise (voiceless H through next vowel formants)
    if F_next is not None:
        vot_noise = np.random.randn(vot_samples).astype(DTYPE) * 0.15
        vot = apply_formants(vot_noise, F_next, VS_A_B, [g*0.3 for g in VS_A_GAINS])
    else:
        vot = np.zeros(vot_samples, dtype=DTYPE)
    
    return np.concatenate([closure, burst, vot])

def synth_N(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """Dental nasal [n]"""
    dur_ms = VS_N_DUR_MS * dil
    n_samples = int(dur_ms / 1000.0 * SR)
    
    # Voiced source
    source = rosenberg_pulse(n_samples, pitch_hz, tilt=0.8)
    
    # Apply formants
    output = apply_formants(source, VS_N_F, VS_N_B, VS_N_GAINS)
    
    # Apply nasal antiresonance (zero at ~800 Hz)
    output = iir_notch(output, VS_N_ANTI_F, VS_N_ANTI_BW)
    
    return output

def synth_DH(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """
    Voiced dental aspirated stop [dʰ]
    
    CRITICAL: Aspiration = breathy murmur (NOT voiceless gap)
    
    Phase 1: VOICED CLOSURE (like [d])
    Phase 2: BURST (like [d])
    Phase 3: BREATHY MURMUR (30-60 ms, continuous voicing)
    Phase 4: Transition to modal voice
    """
    closure_samples = int(VS_DH_CLOSURE_MS / 1000.0 * SR)
    burst_samples = int(VS_DH_BURST_MS / 1000.0 * SR)
    murmur_samples = int(VS_DH_MURMUR_MS * dil / 1000.0 * SR)
    
    # Phase 1: VOICED CLOSURE
    closure_source = rosenberg_pulse(closure_samples, pitch_hz, tilt=0.8)
    # Only pharyngeal resonance (oral cavity closed)
    sos_lp = safe_lp(500)
    closure = signal.sosfilt(sos_lp, closure_source) * VS_DH_CLOSURE_VOICING
    
    # Phase 2: BURST (dental transient)
    burst_noise = np.random.randn(burst_samples).astype(DTYPE)
    sos_burst = safe_bp(VS_DH_BURST_F - VS_DH_BURST_BW/2,
                        VS_DH_BURST_F + VS_DH_BURST_BW/2)
    burst = signal.sosfilt(sos_burst, burst_noise) * VS_DH_BURST_GAIN
    
    # Phase 3: BREATHY MURMUR (KEY ASPIRATION PHASE)
    # Breathy voice = weak periodic + turbulent noise
    murmur_periodic = rosenberg_pulse(murmur_samples, pitch_hz, 
                                      tilt=VS_DH_MURMUR_TILT)
    murmur_noise = np.random.randn(murmur_samples).astype(DTYPE) * VS_DH_MURMUR_NOISE
    murmur_source = murmur_periodic + murmur_noise
    
    # Filter through NEXT vowel formants (approaching vowel)
    # BUT with wider bandwidths (turbulence broadens formants)
    if F_next is not None:
        murmur_bws = [bw * VS_DH_MURMUR_BW_MULT for bw in VS_A_B]
        murmur = apply_formants(murmur_source, F_next, murmur_bws, VS_A_GAINS)
    else:
        # Fallback: Use [ɑ] formants
        murmur_bws = [bw * VS_DH_MURMUR_BW_MULT for bw in VS_A_B]
        murmur = apply_formants(murmur_source, VS_A_F, murmur_bws, VS_A_GAINS)
    
    # Concatenate phases
    output = np.concatenate([closure, burst, murmur])
    
    return output

def synth_AA(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """Long open central vowel [aː]"""
    dur_ms = VS_AA_DUR_MS * dil
    n_samples = int(dur_ms / 1000.0 * SR)
    
    # Modal voice
    source = rosenberg_pulse(n_samples, pitch_hz, tilt=0.8)
    
    # Apply formants
    output = apply_formants(source, VS_AA_F, VS_AA_B, VS_AA_GAINS)
    
    return output

def synth_M(F_prev=None, F_next=None, pitch_hz=PITCH_HZ, dil=DIL):
    """Bilabial nasal [m]"""
    dur_ms = VS_M_DUR_MS * dil
    n_samples = int(dur_ms / 1000.0 * SR)
    
    # Voiced source
    source = rosenberg_pulse(n_samples, pitch_hz, tilt=0.8)
    
    # Apply formants
    output = apply_formants(source, VS_M_F, VS_M_B, VS_M_GAINS)
    
    # Apply nasal antiresonance
    output = iir_notch(output, VS_M_ANTI_F, VS_M_ANTI_BW)
    
    return output

# ══════════════════════════════════════════════════════
# ROOM SIMULATION
# ══════════════════════════════════════════════════════

def apply_simple_room(sig, rt60=1.5, sr=SR):
    """Simple Schroeder reverb"""
    comb_delays = [int(sr * d) for d in [0.0297, 0.0371, 0.0411, 0.0437]]
    allpass_delays = [int(sr * d) for d in [0.005, 0.0017]]
    
    decay = 0.001 ** (1.0 / (rt60 * sr))
    
    # Comb filters
    output = sig.copy()
    for delay in comb_delays:
        buffer = np.zeros(delay)
        comb_out = np.zeros(len(sig), dtype=DTYPE)
        for i in range(len(sig)):
            comb_out[i] = sig[i] + buffer[0] * decay
            buffer = np.roll(buffer, 1)
            buffer[0] = comb_out[i]
        output += comb_out * 0.25
    
    # Allpass filters
    for delay in allpass_delays:
        buffer = np.zeros(delay)
        allpass_out = np.zeros(len(output), dtype=DTYPE)
        for i in range(len(output)):
            delayed = buffer[0]
            buffer = np.roll(buffer, 1)
            buffer[0] = output[i] + delayed * 0.5
            allpass_out[i] = delayed - output[i] * 0.5
        output = allpass_out
    
    return output

# ══════════════════════════════════════════════════════
# WORD SYNTHESIS
# ══════════════════════════════════════════════════════

def synth_ratnadhatamam(pitch_hz=PITCH_HZ, dil=DIL, rt60=1.5):
    """
    Synthesize: ratnadhātamam [rɑtnɑdʰaːtɑmɑm]
    
    Syllable structure:
    RAT — NA — DHĀ — TA — MAM
    [rɑt] [nɑ] [dʰaː] [tɑ] [mɑm]
    """
    
    print("Synthesizing RATNADHĀTAMAM...")
    print("  [r] [ɑ] [t] [n] [ɑ] [dʰ] [aː] [t] [ɑ] [m] [ɑ] [m]")
    
    # Syllable 1: RAT [rɑt]
    r1 = synth_R(F_next=VS_A_F, pitch_hz=pitch_hz, dil=dil)
    a1 = synth_A(F_prev=VS_R_F, F_next=VS_T_BURST_F, pitch_hz=pitch_hz, dil=dil)
    t1 = synth_T(F_prev=VS_A_F, F_next=VS_N_F, pitch_hz=pitch_hz, dil=dil)
    
    # Syllable 2: NA [nɑ]
    n1 = synth_N(F_prev=VS_T_BURST_F, F_next=VS_A_F, pitch_hz=pitch_hz, dil=dil)
    a2 = synth_A(F_prev=VS_N_F, F_next=VS_DH_BURST_F, pitch_hz=pitch_hz, dil=dil)
    
    # Syllable 3: DHĀ [dʰaː] ← CRITICAL SYLLABLE
    dh = synth_DH(F_prev=VS_A_F, F_next=VS_AA_F, pitch_hz=pitch_hz, dil=dil)
    aa = synth_AA(F_prev=VS_DH_BURST_F, F_next=VS_T_BURST_F, pitch_hz=pitch_hz, dil=dil)
    
    # Syllable 4: TA [tɑ]
    t2 = synth_T(F_prev=VS_AA_F, F_next=VS_A_F, pitch_hz=pitch_hz, dil=dil)
    a3 = synth_A(F_prev=VS_T_BURST_F, F_next=VS_M_F, pitch_hz=pitch_hz, dil=dil)
    
    # Syllable 5: MAM [mɑm]
    m1 = synth_M(F_prev=VS_A_F, F_next=VS_A_F, pitch_hz=pitch_hz, dil=dil)
    a4 = synth_A(F_prev=VS_M_F, F_next=VS_M_F, pitch_hz=pitch_hz, dil=dil)
    m2 = synth_M(F_prev=VS_A_F, F_next=None, pitch_hz=pitch_hz, dil=dil)
    
    # Concatenate all phonemes
    word = np.concatenate([r1, a1, t1, n1, a2, dh, aa, t2, a3, m1, a4, m2])
    
    # Normalize
    word = word / (np.max(np.abs(word)) + 1e-10) * 0.8
    
    print(f"  Duration: {len(word)/SR:.2f}s")
    print(f"  RMS: {rms(word):.4f}")
    
    return word.astype(DTYPE)

# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("RATNADHĀTAMAM RECONSTRUCTION")
    print("Vedic Sanskrit — Rigveda 1.1.1, Word 9")
    print("=" * 60)
    print()
    
    # Synthesize at performance tempo
    word_perf = synth_ratnadhatamam(pitch_hz=PITCH_HZ, dil=2.5, rt60=1.5)
    
    # Synthesize dry (no reverb)
    word_dry = synth_ratnadhatamam(pitch_hz=PITCH_HZ, dil=1.0, rt60=0.0)
    
    # Synthesize with hall reverb
    word_hall = apply_simple_room(word_dry, rt60=2.0)
    
    # Synthesize 4× slow (for diagnostic clarity)
    word_slow = ola_stretch(word_dry, factor=4.0)
    
    # Write outputs
    write_wav("ratnadhatamam_performance.wav", word_perf)
    write_wav("ratnadhatamam_dry.wav", word_dry)
    write_wav("ratnadhatamam_hall.wav", word_hall)
    write_wav("ratnadhatamam_slow.wav", word_slow)
    
    print()
    print("=" * 60)
    print("SYNTHESIS COMPLETE")
    print("=" * 60)
    print()
    print("Next: Run ratnadhatamam_diagnostic.py")
