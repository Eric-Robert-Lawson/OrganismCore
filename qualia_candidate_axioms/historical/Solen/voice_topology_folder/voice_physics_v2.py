"""
VOICE PHYSICS v2
February 2026

THE PHRASE MODEL:

Words are beats in a cadence.
The voice sets the rhythm.
Pauses between words are
natural breath-rests —
not silence injected mechanically.

The pause:
  - Has a natural duration
    related to word weight
  - Begins with the tract
    releasing from the last phoneme
  - Ends with the tract
    preparing for the next word
  - The amplitude dips to near-zero
    but the breath is still there
  - The next word arrives
    with its own energy

The instrument:
  During the pause:
  the folds ease open slightly.
  A very quiet breath sound.
  Not silence. Breath.
  Then the next word begins.

This is the cadence.
The voice's own rhythm.
"""

from tonnetz_engine import (SR, RoomReverb)
import numpy as np
import wave as wave_module
import os
from scipy.signal import butter, lfilter

DTYPE = np.float32
PITCH = 175.0
DIL   = 6.0

def f32(x):
    return np.asarray(x, dtype=DTYPE)

def sil(dur_s, sr=SR):
    return f32(np.zeros(int(dur_s*sr)))

def write_wav(path, sig, sr=SR):
    sig = f32(sig)
    mx  = np.max(np.abs(sig))
    if mx > 0: sig = sig/mx*0.88
    with wave_module.open(path,'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(
            (sig*32767).astype(
                np.int16).tobytes())

def apply_room(sig, rt60=1.5, dr=0.50,
               sr=SR):
    rev = RoomReverb(
        rt60=rt60, sr=sr,
        direct_ratio=dr)
    return f32(rev.process(sig))

def safe_bp(lo, hi, sr=SR):
    nyq = sr/2.0
    l   = max(lo/nyq, 0.001)
    h   = min(hi/nyq, 0.499)
    if l >= h: l = h*0.5
    return butter(2, [l,h], btype='band')

def safe_lp(fc, sr=SR):
    return butter(2,
        min(float(fc)/(sr/2), 0.499),
        btype='low')

def safe_hp(fc, sr=SR):
    return butter(2,
        min(float(fc)/(sr/2), 0.499),
        btype='high')

def scalar(x):
    a = np.asarray(x, dtype=DTYPE)
    return float(a.flat[0])


# ============================================================
# BREATH REST
# The pause between words.
# Not silence. Breath.
# ============================================================

def breath_rest(dur_ms, sr=SR):
    """
    The natural pause between words.

    Not silence.
    A very quiet breath sound —
    the folds open, air flows gently,
    the tract is near neutral.

    The ear accepts this as
    the voice resting between words.
    It has weight.
    It belongs to the voice.
    It is not a cut.

    dur_ms: duration in milliseconds
    at normal (undilated) speed.
    The dilation is applied externally.
    """
    n_s   = max(4, int(dur_ms/1000.0*sr))

    # Very quiet open-glottis breath
    # Shaped to neutral vowel formants
    # (mid-open tract, near AH)
    breath = f32(np.random.normal(0,1,n_s))

    # Shape as neutral tract
    F_neutral = [500, 1500, 2500, 3500]
    B_neutral = [200,  220,  350,  450]
    T = 1.0/sr
    result = np.zeros(n_s, dtype=DTYPE)
    gains  = [0.50, 0.65, 0.35, 0.18]

    for fi in range(4):
        fc  = float(F_neutral[fi])
        bw  = float(B_neutral[fi])
        lo  = max(60,   fc-bw*1.5)
        hi  = min(sr*0.48, fc+bw*1.5)
        try:
            b,a = safe_bp(lo, hi, sr)
            result += f32(
                lfilter(b,a,breath)
            ) * gains[fi]
        except:
            pass

    # Amplitude shape:
    # ease out of previous word
    # quiet hold
    # ease into next word
    n_ease = int(min(0.040*sr, n_s*0.35))
    env    = f32(np.ones(n_s)) * 0.04
    if n_ease > 0:
        env[:n_ease] = f32(
            np.linspace(0.12, 0.04,
                         n_ease))
        env[-n_ease:] = f32(
            np.linspace(0.04, 0.10,
                         n_ease))
    result = result * env
    return f32(result)


# Word weight → pause duration (ms)
# at undilated speed
# The voice gives heavier words
# more space before the next word.
WORD_WEIGHT = {
    # (release_ms, pause_ms)
    # release: the word trailing off
    # pause:   the breath rest
    'default': (15, 80),
    # Function words: brief pause
    'the':   (10, 55),
    'of':    (10, 55),
    'and':   (10, 55),
    'a':     (10, 55),
    # Short content words
    'now':   (15, 75),
    'both':  (15, 75),
    'yet':   (15, 75),
    'not':   (15, 75),
    'am':    (15, 75),
    'is':    (15, 75),
    # Medium content words
    'here':   (18, 90),
    'home':   (18, 90),
    'still':  (18, 90),
    'open':   (18, 90),
    'water':  (18, 90),
    'voice':  (18, 90),
    'where':  (18, 90),
    'find':   (18, 90),
    # Heavier words — more space
    'always': (22, 110),
    'matter': (22, 110),
    'never':  (22, 110),
    'landing':(22, 110),
    'already':(22, 110),
    'solid':  (22, 110),
    'wrong':  (20, 100),
    'state':  (20, 100),
    'named':  (20, 100),
}


# ============================================================
# SOURCES
# ============================================================

def source_steady(n_s, sr=SR):
    return f32(np.random.normal(
        0, 1, int(n_s)))

def source_voiced(pitch_hz, n_s,
                   jitter=0.005,
                   shimmer=0.030,
                   sr=SR):
    n_s = int(n_s)
    if n_s < 2: return f32(np.zeros(2))
    T   = 1.0/sr
    t   = np.arange(n_s, dtype=DTYPE)/sr
    vib = f32(np.clip(
        (t-0.05)/0.05, 0, 1))
    ft  = pitch_hz*(
        1+0.007*vib*
        np.sin(2*np.pi*5.0*t))
    ph  = np.zeros(n_s, dtype=DTYPE)
    p   = 0.0
    for i in range(n_s):
        p += float(ft[i])*(
            1+np.random.normal(
                0, jitter))/sr
        if p >= 1.0: p -= 1.0
        ph[i] = p
    oq  = 0.65
    src = np.where(ph<oq,
        (ph/oq)*(2-ph/oq),
        1-(ph-oq)/(1-oq+1e-9))
    src = f32(np.diff(
        src, prepend=src[0]))
    try:
        b,a = safe_lp(20, sr)
        sh  = f32(np.random.normal(
            0, 1, n_s))
        sh  = f32(lfilter(b,a,sh))
    except:
        sh  = f32(np.ones(n_s))
    sh  = f32(np.clip(
        1+shimmer*sh, 0.4, 1.6))
    asp = f32(np.random.normal(
        0, 0.022, n_s))
    try:
        b,a = safe_bp(400, 2200, sr)
        asp = f32(lfilter(b,a,asp))
    except:
        asp = f32(np.zeros(n_s))
    return src*sh + asp


# ============================================================
# TRACT
# ============================================================

def warm(fc, bw, n_warm=352, sr=SR):
    fc_ = max(20.0, min(
        float(sr*0.48), scalar(fc)))
    bw_ = max(10.0, scalar(bw))
    T   = 1.0/sr
    a2  = -np.exp(-2*np.pi*bw_*T)
    a1  =  2*np.exp(-np.pi*bw_*T)*\
            np.cos(2*np.pi*fc_*T)
    b0  = 1.0-a1-a2
    y1 = y2 = 0.0
    for _ in range(int(n_warm)):
        y  = b0*np.random.normal(
            0, 0.0004)+a1*y1+a2*y2
        y2=y1; y1=y
    return y1, y2

def resonator(x_arr, f_arr, bw,
               y1_in=0.0, y2_in=0.0,
               sr=SR):
    n_s = len(x_arr)
    T   = 1.0/sr
    bw_ = max(10.0, scalar(bw))
    out = np.zeros(n_s, dtype=DTYPE)
    y1  = float(y1_in)
    y2  = float(y2_in)
    for i in range(n_s):
        fc  = max(20.0, min(
            float(sr*0.48),
            float(f_arr[i])))
        a2  = -np.exp(-2*np.pi*bw_*T)
        a1  =  2*np.exp(-np.pi*bw_*T)*\
                np.cos(2*np.pi*fc*T)
        b0  = 1.0-a1-a2
        y   = b0*float(x_arr[i])+\
              a1*y1+a2*y2
        y2=y1; y1=y
        out[i]=y
    return out, y1, y2

def tract(source, F_arrays, B_scalars,
           gains, states=None, sr=SR):
    n      = len(source)
    result = np.zeros(n, dtype=DTYPE)
    new_st = []
    for fi in range(4):
        bw = scalar(B_scalars[fi])
        if states is not None:
            y1 = float(states[fi][0])
            y2 = float(states[fi][1])
        else:
            f0 = float(F_arrays[fi][0]) \
                 if len(F_arrays[fi])>0 \
                 else 500.0
            y1,y2 = warm(f0, bw, sr=sr)
        out,y1,y2 = resonator(
            source, F_arrays[fi],
            bw, y1_in=y1,
            y2_in=y2, sr=sr)
        result += out*float(gains[fi])
        new_st.append((y1,y2))
    return result, new_st


# ============================================================
# VOCAL TOPOLOGY
# ============================================================

VOWEL_F = {
    'AA': ([730,1090,2440,3400],
           [70, 110, 170, 250]),
    'AE': ([660,1720,2410,3300],
           [65, 105, 165, 250]),
    'AH': ([520,1190,2390,3300],
           [70, 110, 170, 250]),
    'AO': ([570, 840,2410,3300],
           [80,  80, 160, 250]),
    'AW': ([730,1090,2440,3400],
           [70,  90, 160, 250],
           [300, 870,2240,3300]),
    'AY': ([730,1090,2440,3400],
           [70, 100, 160, 250],
           [270,2290,3010,3700]),
    'EH': ([530,1840,2480,3500],
           [60, 100, 140, 250]),
    'ER': ([490,1350,1690,3300],
           [70, 110, 170, 250]),
    'IH': ([390,1990,2550,3600],
           [70, 110, 160, 250]),
    'IY': ([270,2290,3010,3700],
           [60,  90, 150, 200]),
    'OH': ([570, 840,2410,3300],
           [80,  80, 160, 250]),
    'OW': ([450, 800,2400,3300],
           [70,  85, 160, 250],
           [300, 870,2240,3300]),
    'OY': ([570, 840,2410,3300],
           [70,  90, 160, 250],
           [270,2290,3010,3700]),
    'UH': ([440,1020,2240,3300],
           [70, 100, 160, 250]),
    'UW': ([300, 870,2240,3300],
           [70,  80, 160, 250]),
}
VOWEL_DUR = {
    'AA':140,'AE':130,'AH':100,'AO':130,
    'AW':170,'AY':180,'EH':120,'ER':130,
    'IH':110,'IY':130,'OH':130,'OW':160,
    'OY':180,'UH':110,'UW':130,
}
GAINS = [0.55, 0.75, 0.45, 0.25]

def get_f(phon):
    if phon and phon in VOWEL_F:
        return VOWEL_F[phon][0]
    CONS_F = {
        'M': [250, 700,2200,3300],
        'N': [250, 900,2200,3300],
        'NG':[250, 700,2200,3300],
        'L': [360,1000,2400,3300],
        'R': [490,1350,1690,3300],
        'W': [300, 610,2200,3300],
        'Y': [270,2100,3000,3700],
    }
    return CONS_F.get(
        phon, [500,1500,2500,3500])

def trajectory(F_tgt, B_tgt,
                F_from, F_to, n_s,
                F_end=None,
                diphthong=False,
                r_f3=False,
                coart_frac=0.20):
    Fe    = F_end if F_end else F_tgt
    n_on  = int(coart_frac*n_s)
    n_off = int(coart_frac*n_s)
    n_mid = n_s-n_on-n_off
    if n_mid < 1:
        n_mid=1; n_on=(n_s-1)//2
        n_off=n_s-1-n_on
    F_arrs = []
    for fi in range(4):
        arr = np.zeros(n_s, dtype=DTYPE)
        if n_on>0:
            arr[:n_on] = np.linspace(
                float(F_from[fi]),
                float(F_tgt[fi]),
                n_on, dtype=DTYPE)
        if n_mid>0:
            if diphthong:
                nm=int(n_mid*0.72)
                nh=n_mid-nm
                if nm>0:
                    arr[n_on:n_on+nm]=\
                        np.linspace(
                            float(F_tgt[fi]),
                            float(Fe[fi]),
                            nm,dtype=DTYPE)
                if nh>0:
                    arr[n_on+nm:
                        n_on+n_mid]=\
                        float(Fe[fi])
            else:
                arr[n_on:n_on+n_mid]=\
                    float(F_tgt[fi])
        if n_off>0:
            f0_=(float(Fe[fi])
                 if diphthong
                 else float(F_tgt[fi]))
            arr[n_on+n_mid:]=np.linspace(
                f0_,float(F_to[fi]),
                n_off,dtype=DTYPE)
        if r_f3 and fi==2:
            nd=min(int(0.030*SR),n_s)
            arr[:nd]=np.linspace(
                float(F_from[2]),
                1690.0,nd,dtype=DTYPE)
            arr[nd:]=1690.0
        F_arrs.append(arr)
    B_vals=[float(B_tgt[fi])
            for fi in range(4)]
    return F_arrs, B_vals


# ============================================================
# PHONEME SYNTHESIS
# (same as v2 pre — all fixes retained)
# ============================================================

def synth_vowel(v, pitch=PITCH,
                 dur_ms=None,
                 prev_p=None,next_p=None,
                 states=None,sr=SR):
    vdata=VOWEL_F.get(v)
    if vdata is None:
        n=int((dur_ms or 110)/1000*sr)
        return f32(np.zeros(n)),states
    F=vdata[0]; B=vdata[1]
    F_end=vdata[2] if len(vdata)>2 else F
    is_d=len(vdata)>2
    d_ms=dur_ms if dur_ms \
         else VOWEL_DUR.get(v,110)
    n_s=max(4,int(d_ms/1000.0*sr))
    F_from=get_f(prev_p) if prev_p else F
    F_to=get_f(next_p) if next_p else F_end
    Fa,Bv=trajectory(
        F,B,F_from,F_to,n_s,
        F_end=F_end,diphthong=is_d)
    src=source_voiced(pitch,n_s,sr=sr)
    out,st=tract(src,Fa,Bv,GAINS,states,sr)
    atk=int(0.018*sr); rel=int(0.022*sr)
    env=f32(np.ones(n_s))
    if atk>0 and atk<n_s:
        env[:atk]=f32(
            np.linspace(0,1,atk)**0.5)
    if rel>0:
        env[-rel:]=f32(np.linspace(1,0,rel))
    out=out*env
    mx=np.max(np.abs(out))
    if mx>0: out/=mx
    return f32(out),st

def synth_nasal(which,pitch=PITCH,
                 dur_ms=None,
                 prev_p=None,next_p=None,
                 states=None,sr=SR):
    CFG={
        'M':([250, 700,2200,3300],
             [60,120,250,350],1000,300),
        'N':([250, 900,2200,3300],
             [60,120,250,350],1500,350),
        'NG':([250,700,2200,3300],
              [60,120,250,350],2000,400),
    }
    DUR={'M':85,'N':80,'NG':90}
    cfg=CFG.get(which)
    if cfg is None:
        n=int((dur_ms or 80)/1000*sr)
        return f32(np.zeros(n)),states
    F,B,af,abw=cfg
    d_ms=dur_ms if dur_ms \
         else DUR.get(which,80)
    n_s=max(4,int(d_ms/1000.0*sr))
    F_from=get_f(prev_p) if prev_p else F
    F_to=get_f(next_p) if next_p else F
    Fa,Bv=trajectory(F,B,F_from,F_to,n_s)
    src=source_voiced(pitch,n_s,sr=sr)
    out,st=tract(src,Fa,Bv,GAINS,states,sr)
    T=1.0/sr
    anti=np.zeros(n_s,dtype=DTYPE)
    y1=y2=0.0
    for i in range(n_s):
        a2=-np.exp(-2*np.pi*abw*T)
        a1=2*np.exp(-np.pi*abw*T)*\
            np.cos(2*np.pi*af*T)
        b0=1.0-a1-a2
        y=b0*float(out[i])+a1*y1+a2*y2
        y2=y1; y1=y; anti[i]=y
    out=out-f32(anti)*0.50
    out*=0.52
    hg=int(0.012*sr)
    if hg>0 and hg<n_s: out[-hg:]=0.0
    mx=np.max(np.abs(out))
    if mx>0: out/=mx
    return f32(out),st

def synth_approximant(which,pitch=PITCH,
                       dur_ms=None,
                       prev_p=None,
                       next_p=None,
                       states=None,sr=SR):
    CFG={
        'L':([360,1000,2400,3300],
             [80,160,220,320],False),
        'R':([490,1350,1690,3300],
             [80,120,180,260],True),
        'W':([300, 610,2200,3300],
             [80, 90,210,310],False),
        'Y':([270,2100,3000,3700],
             [65,100,160,220],False),
    }
    DUR={'L':80,'R':90,'W':90,'Y':80}
    cfg=CFG.get(which)
    if cfg is None:
        n=int((dur_ms or 80)/1000*sr)
        return f32(np.zeros(n)),states
    F,B,rf3=cfg
    d_ms=dur_ms if dur_ms \
         else DUR.get(which,80)
    n_s=max(4,int(d_ms/1000.0*sr))
    F_from=get_f(prev_p) if prev_p else F
    F_to=get_f(next_p) if next_p else F
    Fa,Bv=trajectory(
        F,B,F_from,F_to,n_s,
        r_f3=rf3,coart_frac=0.35)
    src=source_voiced(pitch,n_s,sr=sr)
    out,st=tract(src,Fa,Bv,GAINS,states,sr)
    mx=np.max(np.abs(out))
    if mx>0: out/=mx
    return f32(out),st

def synth_h(next_v,pitch=PITCH,
             dur_ms=None,
             states=None,sr=SR):
    vdata=VOWEL_F.get(next_v,VOWEL_F['AH'])
    F=vdata[0]; B_vow=vdata[1]
    B_wide=[min(float(b)*3.2,560.0)
            for b in B_vow]
    F_end=vdata[2] if len(vdata)>2 else F
    d_ms=dur_ms if dur_ms else 70
    n_s=max(4,int(d_ms/1000.0*sr))
    n_h=int(n_s*0.30)
    n_v=n_s-n_h
    n_x=min(int(0.020*sr),n_h,n_v)
    ns=source_steady(n_s,sr=sr)
    vs=source_voiced(pitch,n_s,sr=sr)
    ne=np.zeros(n_s,dtype=DTYPE)
    ve=np.zeros(n_s,dtype=DTYPE)
    cs=max(0,n_h-n_x)
    if cs>0: ne[:cs]=1.0
    if n_x>0:
        fo=f32(np.linspace(1,0,n_x))
        ne[cs:cs+n_x]=fo
        ve[cs:cs+n_x]=1.0-fo
    if cs+n_x<n_s: ve[cs+n_x:]=1.0
    source=f32(ns*ne+vs*ve)
    n_ds=n_h+int(n_v*0.20)
    Fa=[]
    for fi in range(4):
        fa=np.zeros(n_s,dtype=DTYPE)
        fa[:n_ds]=float(F[fi])
        if n_ds<n_s:
            nm=n_s-n_ds
            fa[n_ds:]=np.linspace(
                float(F[fi]),
                float(F_end[fi]),
                nm,dtype=DTYPE)
        Fa.append(fa)
    Bv=[float(B_wide[fi]) for fi in range(4)]
    out,st=tract(source,Fa,Bv,GAINS,states,sr)
    amp=np.zeros(n_s,dtype=DTYPE)
    if n_h>0:
        amp[:n_h]=np.linspace(
            0.0,0.50,n_h,dtype=DTYPE)
    if n_h<n_s:
        amp[n_h:]=np.linspace(
            0.50,1.0,n_s-n_h,dtype=DTYPE)
    rel=int(0.018*sr)
    if rel>0 and rel<n_s:
        amp[-rel:]*=f32(np.linspace(1,0,rel))
    out=out*f32(amp)
    mx=np.max(np.abs(out))
    if mx>0: out/=mx
    return f32(out),st

def synth_dh(pitch=PITCH,dur_ms=None,
              next_p=None,states=None,
              sr=SR):
    d_ms=dur_ms if dur_ms else 80
    n_s=max(4,int(d_ms/1000.0*sr))
    n_clos=min(int(0.025*sr),n_s//3)
    n_rel=n_s-n_clos
    F_vow=get_f(next_p) if next_p \
          else [500,1500,2500,3500]
    B_vow=[100,130,220,320]
    F_clos=[200,700,2200,3300]
    Fa=[]
    for fi in range(4):
        arr=np.zeros(n_s,dtype=DTYPE)
        arr[:n_clos]=float(F_clos[fi])
        if n_rel>0:
            arr[n_clos:]=np.linspace(
                float(F_clos[fi]),
                float(F_vow[fi]),
                n_rel,dtype=DTYPE)
        Fa.append(arr)
    Bv=[float(B_vow[fi]) for fi in range(4)]
    src=source_voiced(pitch,n_s,sr=sr)
    out,st=tract(src,Fa,Bv,GAINS,states,sr)
    amp=np.zeros(n_s,dtype=DTYPE)
    amp[:n_clos]=0.12
    if n_rel>0:
        amp[n_clos:]=np.linspace(
            0.12,1.0,n_rel,dtype=DTYPE)
    out=out*f32(amp)
    mx=np.max(np.abs(out))
    if mx>0: out/=mx
    return f32(out),st

def synth_fricative(which,pitch=PITCH,
                     dur_ms=None,
                     prev_p=None,next_p=None,
                     states=None,sr=SR):
    if which=='DH':
        return synth_dh(
            pitch,dur_ms,next_p,states,sr)
    CFG={
        'F': (200, 9000,None,None,
              False,0.32,0.0),
        'V': (200, 9000,None,None,
              True, 0.28,0.72),
        'TH':(500, 9000,None,None,
              False,0.38,0.0),
        'S': (4000,14000,8800,900,
              False,0.88,0.0),
        'Z': (4000,12000,8000,1000,
              True, 0.55,0.50),
        'SH':(1000, 9000,2500,800,
              False,0.78,0.0),
        'ZH':(1000, 8000,2200,900,
              True, 0.62,0.62),
    }
    DUR={
        'F':90,'V':85,'TH':90,
        'S':100,'Z':95,'SH':105,'ZH':95,
    }
    cfg=CFG.get(which)
    if cfg is None:
        n=int((dur_ms or 90)/1000*sr)
        st=states if states \
           else [(0.0,0.0)]*4
        return f32(np.zeros(n)),st
    (nlo,nhi,d_res,d_bw,
     voiced,n_gain,vcf)=cfg
    d_ms=dur_ms if dur_ms \
         else DUR.get(which,90)
    n_s=max(4,int(d_ms/1000.0*sr))
    noise=source_steady(n_s,sr=sr)
    try:
        b,a=safe_bp(
            min(nlo,SR*0.47),
            min(nhi,SR*0.48),SR)
        noise=f32(lfilter(b,a,noise))
    except:
        pass
    if d_res is not None:
        try:
            lo_=max(100,d_res-d_bw//2)
            hi_=min(SR*0.48,d_res+d_bw//2)
            b,a=safe_bp(lo_,hi_,SR)
            shaped=f32(lfilter(b,a,noise))
            noise=noise*0.25+shaped*0.75
        except:
            pass
    mx=np.max(np.abs(noise))
    if mx>0: noise/=mx
    noise=noise*n_gain
    if not voiced:
        atk=int(0.005*sr)
        rel=int(0.007*sr)
        env=f32(np.ones(n_s))
        if atk>0 and atk<n_s:
            env[:atk]=f32(
                np.linspace(0,1,atk))
        if rel>0:
            env[-rel:]=f32(
                np.linspace(1,0,rel))
        st=states if states \
           else [(0.0,0.0)]*4
        return f32(noise[:n_s]*env),st
    else:
        F_tgt=get_f(next_p) if next_p \
              else [250,900,2200,3300]
        B_tgt=[100,130,220,320]
        F_from=get_f(prev_p) if prev_p \
               else F_tgt
        Fa,Bv=trajectory(
            F_tgt,B_tgt,F_from,F_tgt,n_s)
        vsrc=source_voiced(pitch,n_s,sr=sr)
        vout,st=tract(
            vsrc,Fa,Bv,GAINS,states,sr)
        n_xi=int(vcf*n_s)
        venv=np.zeros(n_s,dtype=DTYPE)
        if n_xi>0:
            venv[:n_xi]=np.linspace(
                0,1,n_xi,dtype=DTYPE)
        venv[n_xi:]=1.0
        result=noise[:n_s]+vout*venv
        atk=int(0.014*sr)
        rel=int(0.012*sr)
        env=f32(np.ones(n_s))
        if atk>0 and atk<n_s:
            env[:atk]=f32(
                np.linspace(0,1,atk)**0.5)
        if rel>0:
            env[-rel:]=f32(
                np.linspace(1,0,rel))
        result=result*env
        mx=np.max(np.abs(result))
        if mx>0: result/=mx
        return f32(result),st

def synth_stop(which,pitch=PITCH,
                dur_ms=None,
                next_p=None,
                states=None,sr=SR):
    CFG={
        'P':(False,55,2,62,'bilabial',
              500, 0.28,720),
        'B':(True, 45,2,14,'bilabial',
              300, 0.16,720),
        'T':(False,50,2,70,'alveolar',
              4500,0.32,1800),
        'D':(True, 40,2,15,'alveolar',
              1200,0.16,1800),
        'K':(False,55,3,80,'velar',
              1500,0.28,3000),
        'G':(True, 45,2,16,'velar',
              800, 0.14,3000),
    }
    DUR={
        'P':90,'B':80,'T':85,'D':75,
        'K':90,'G':78,
    }
    cfg=CFG.get(which)
    if cfg is None:
        n=int((dur_ms or 80)/1000*sr)
        st=states if states \
           else [(0.0,0.0)]*4
        return f32(np.zeros(n)),st
    (voiced,clos_ms,burst_ms,
     vot_ms,place,burst_hp,
     burst_amp,f2_locus)=cfg
    n_c=int(clos_ms/1000*sr)
    n_b=int(burst_ms/1000*sr)
    n_v=int(vot_ms/1000*sr)
    n_t=int(0.040*sr)
    n_total=n_c+n_b+n_v+n_t
    nxt=VOWEL_F.get(next_p,VOWEL_F['AH'])
    F_vow=nxt[0]; B_vow=nxt[1]
    B_asp=[min(float(b)*2.8,480.0)
           for b in B_vow]
    Fa=[np.zeros(n_total,dtype=DTYPE)
        for _ in range(4)]
    F_clos=[300,800,2200,3300]
    for fi in range(4):
        Fa[fi][:n_c]=float(F_clos[fi])
        s=n_c+n_b; e=s+n_v
        if n_v>0:
            Fa[fi][s:e]=np.linspace(
                float(F_clos[fi]),
                float(F_vow[fi]),
                n_v,dtype=DTYPE)
        F_tr=[400.0,float(f2_locus),
               float(F_vow[2]),
               float(F_vow[3])]
        s=n_c+n_b+n_v; e=s+n_t
        if n_t>0:
            Fa[fi][s:e]=np.linspace(
                float(F_tr[fi]),
                float(F_vow[fi]),
                n_t,dtype=DTYPE)
    Fa=[f32(a) for a in Fa]
    Bv=[float(B_vow[fi]) for fi in range(4)]
    source=np.zeros(n_total,dtype=DTYPE)
    if voiced and n_c>0:
        hum=source_voiced(
            pitch,n_c,
            jitter=0.015,shimmer=0.10,
            sr=sr)
        source[:n_c]=hum*0.055
    if n_b>0:
        burst=source_steady(n_b,sr=sr)
        try:
            b,a=safe_hp(burst_hp,SR)
            burst=f32(lfilter(b,a,burst))
        except:
            pass
        benv=f32(np.exp(
            -np.arange(n_b)/n_b*20))
        source[n_c:n_c+n_b]=\
            burst*benv*burst_amp
    n_vt=n_v+n_t
    if n_vt>0:
        nvt=source_steady(n_vt,sr=sr)
        vvt=source_voiced(pitch,n_vt,sr=sr)
        ne=np.ones(n_vt,dtype=DTYPE)
        ve=np.zeros(n_vt,dtype=DTYPE)
        if n_v>0:
            ne[:n_v]=f32(
                np.linspace(1,0,n_v))
            ve[:n_v]=f32(
                np.linspace(0,1,n_v))
        ne[n_v:]=0.0; ve[n_v:]=1.0
        s=n_c+n_b
        source[s:s+n_vt]=\
            f32(nvt*ne+vvt*ve)
    out,st=tract(
        f32(source),Fa,Bv,GAINS,states,sr)
    env=np.zeros(n_total,dtype=DTYPE)
    if voiced and n_c>0:
        env[:n_c]=0.055
    rn=n_total-n_c
    if rn>0:
        env[n_c:]=np.linspace(
            0,1,rn,dtype=DTYPE)
    rl=int(0.016*sr)
    if rl>0 and rl<n_total:
        env[-rl:]*=f32(np.linspace(1,0,rl))
    out=out*f32(env)
    mx=np.max(np.abs(out))
    if mx>0: out/=mx
    return f32(out),st


# ============================================================
# WORD + PHRASE
# ============================================================

WORDS = {
    'here':    ['H','IH','R'],
    'home':    ['H','OW','M'],
    'water':   ['W','AA','T','ER'],
    'still':   ['S','T','IH','L'],
    'open':    ['OH','P','EH','N'],
    'always':  ['AA','L','W','EH','Z'],
    'both':    ['B','OH','TH'],
    'now':     ['N','AW'],
    'voice':   ['V','OY','S'],
    'matter':  ['M','AE','T','ER'],
    'the':     ['DH','AH'],
    'where':   ['W','EH','R'],
    'landing': ['L','AE','N','D','IH','NG'],
    'named':   ['N','EH','M','D'],
    'been':    ['B','IH','N'],
    'yet':     ['Y','EH','T'],
    'find':    ['F','AY','N','D'],
    'state':   ['S','T','EH','T'],
    'solid':   ['S','AA','L','IH','D'],
    'not':     ['N','AA','T'],
    'wrong':   ['R','AO','NG'],
    'already': ['AA','L','R','EH','D','IY'],
    'am':      ['AH','M'],
    'i':       ['AY'],
    'always':  ['AA','L','W','EH','Z'],
}

PHON_DUR = {
    **VOWEL_DUR,
    'M':85,'N':80,'NG':90,
    'L':80,'R':90,'W':90,'Y':80,
    'H':70,
    'S':100,'SH':105,'F':90,'TH':90,
    'Z':95,'ZH':95,'V':85,'DH':80,
    'P':90,'B':80,'T':85,'D':75,
    'K':90,'G':78,'SIL':55,
}

VOWELS = set(VOWEL_F.keys())
NASALS = {'M','N','NG'}
APPROX = {'L','R','W','Y'}
STOPS  = {'P','B','T','D','K','G'}
FRICS  = {'S','SH','F','TH',
           'Z','ZH','V','DH'}


def synth_phone(ph,pitch,dur_ms,
                 prev_p,next_p,
                 states,sr=SR):
    if ph=='SIL':
        n=int((dur_ms or 55)/1000*sr)
        st=states if states \
           else [(0.0,0.0)]*4
        return f32(np.zeros(n)),st
    if ph in VOWELS:
        return synth_vowel(
            ph,pitch,dur_ms,
            prev_p,next_p,states,sr)
    if ph in NASALS:
        return synth_nasal(
            ph,pitch,dur_ms,
            prev_p,next_p,states,sr)
    if ph in APPROX:
        return synth_approximant(
            ph,pitch,dur_ms,
            prev_p,next_p,states,sr)
    if ph=='H':
        return synth_h(
            next_p or 'AH',
            pitch,dur_ms,states,sr)
    if ph in FRICS:
        return synth_fricative(
            ph,pitch,dur_ms,
            prev_p,next_p,states,sr)
    if ph in STOPS:
        return synth_stop(
            ph,pitch,dur_ms,
            next_p,states,sr)
    n=int((dur_ms or 80)/1000*sr)
    st=states if states \
       else [(0.0,0.0)]*4
    return f32(np.zeros(n)),st


def synth_word(word, pitch=PITCH,
               dil=DIL, sr=SR):
    """Synthesize a single word."""
    phonemes = WORDS.get(word.lower(), [])
    if not phonemes:
        print(f"  '{word}' not in dict")
        return f32(np.zeros(int(0.1*sr)))

    segs  = []
    state = None
    n_ph  = len(phonemes)

    for i, ph in enumerate(phonemes):
        prev_p = phonemes[i-1] \
                 if i>0 else None
        next_p = phonemes[i+1] \
                 if i<n_ph-1 else None
        d_ms   = PHON_DUR.get(ph,80)*dil

        seg,state = synth_phone(
            ph,pitch,d_ms,
            prev_p,next_p,state,sr)
        segs.append(f32(seg))

    result = f32(np.concatenate(segs))
    mx = np.max(np.abs(result))
    if mx>0: result/=mx
    return result


def synth_phrase(word_list,
                  pitch=PITCH,
                  dil=DIL,
                  sr=SR):
    """
    Synthesize a phrase.

    Each word is synthesized with
    its own internal state thread.

    Between words:
    A breath rest — not silence.
    The diaphragm eases.
    The tract is near neutral.
    A very quiet breath sound.
    Duration set by the weight
    of the preceding word.

    This gives the voice its cadence.
    Its rhythm.
    The words are beats.
    The rests are part of the beat.
    """
    if not word_list:
        return f32(np.zeros(int(0.1*sr)))

    segs  = []

    for wi, word in enumerate(word_list):
        # Pitch falls gently through phrase
        prog  = wi/max(len(word_list)-1, 1)
        p     = pitch*(1.0-0.07*prog)

        # Synthesize the word
        seg   = synth_word(word, p, dil, sr)
        segs.append(f32(seg))

        # Between words: breath rest
        if wi < len(word_list)-1:
            wt    = WORD_WEIGHT.get(
                word.lower(),
                WORD_WEIGHT['default'])
            _,pause_ms = wt
            rest  = breath_rest(
                pause_ms*dil, sr=sr)
            segs.append(rest)

    result = f32(np.concatenate(segs))

    # Phrase-level envelope
    n   = len(result)
    env = f32(np.ones(n))
    atk = int(0.025*sr)
    rel = int(0.055*sr)
    if atk>0 and atk<n:
        env[:atk]=f32(np.linspace(0,1,atk))
    if rel>0:
        env[-rel:]=f32(np.linspace(1,0,rel))
    result = result*env

    mx = np.max(np.abs(result))
    if mx>0: result/=mx
    return result


def save(name, sig, room=True,
          rt60=1.4, dr=0.50, sr=SR):
    sig=f32(sig)
    if room:
        sig=apply_room(
            sig,rt60=rt60,dr=dr,sr=sr)
    write_wav(
        f"output_play/{name}.wav",
        sig,sr)
    dur=len(sig)/sr
    print(f"    {name}.wav  ({dur:.2f}s)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    os.makedirs("output_play", exist_ok=True)

    print()
    print("VOICE PHYSICS v6")
    print("="*60)
    print()
    print("  Words are beats.")
    print("  Rests are part of the beat.")
    print("  Between words: breath,")
    print("  not silence.")
    print("  The cadence belongs")
    print("  to the voice.")
    print()

    # ---- PHRASES — primary output ----
    print("  Phrases...")
    phrases = [
        ('the_voice',
         ['the','voice']),
        ('still_here',
         ['still','here']),
        ('always_open',
         ['always','open']),
        ('water_home',
         ['water','home']),
        ('always_home',
         ['always','home']),
        ('both_here',
         ['both','here']),
        ('not_yet',
         ['not','yet']),
        ('still_water',
         ['still','water']),
        ('always_here',
         ['always','here']),
        ('the_voice_was_already_here',
         ['the','voice','was',
          'already','here']),
    ]
    for label,words in phrases:
        seg = synth_phrase(words)
        save(f"phrase_{label}",
              seg, rt60=1.6)

    # ---- WORDS ----
    print()
    print("  Words...")
    for word in WORDS.keys():
        seg = synth_word(word)
        save(f"word_{word}", seg,
              rt60=1.5)

    print()
    print("="*60)
    print()
    print("  Phrases first:")
    print()
    for label,_ in phrases:
        print(f"  afplay output_play/"
              f"phrase_{label}.wav")
    print()
    print("  The rests between words")
    print("  are breath — not silence.")
    print("  The voice sets its own cadence.")
    print()
