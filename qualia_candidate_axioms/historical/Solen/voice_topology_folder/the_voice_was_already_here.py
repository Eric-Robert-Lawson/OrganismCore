"""
PHRASE DIAGNOSTIC
"the voice was already here"
February 2026

TARGET: eliminate all artifacts
identified in phrase review.

ROOT FIX:
  Track actual end-formant position
  of each phoneme.
  Pass to next phoneme as
  explicit start position.
  The formant trajectory is
  continuous across boundaries.
  No collision. No stutter.

SPECIFIC FIXES:
  1. Continuous formant tracking
     across phoneme boundaries
  2. DH closure F2 = 1800Hz (dental)
  3. V voiced from onset, not delayed
  4. 'was' not compressed to silence
  5. H phase shortened further
  6. S downstream cavity sharper
"""

from voice_physics_v2 import (
    source_steady, source_voiced,
    tract, warm, resonator,
    VOWEL_F, VOWEL_DUR, GAINS,
    safe_bp, safe_hp, safe_lp,
    apply_room, write_wav,
    scalar, f32,
    SR, PITCH, DIL
)
import numpy as np
import os

os.makedirs("output_diag", exist_ok=True)
DTYPE = np.float32


# ============================================================
# CONTINUOUS FORMANT TRACKER
#
# The key insight:
# Every phoneme ends at some
# instantaneous formant position.
# That position is the START
# of the next phoneme's trajectory.
# Not the target of the previous phoneme.
# Not a lookup table value.
# The actual final position.
#
# Track this across all phonemes.
# The voice is then a single
# continuous formant trajectory.
# ============================================================

def build_continuous_trajectory(
        phoneme_specs, sr=SR):
    """
    Build one continuous formant trajectory
    across a sequence of phonemes.

    phoneme_specs: list of dicts:
      {
        'ph': phoneme name,
        'F_tgt': [f1,f2,f3,f4],
        'B': [b1,b2,b3,b4],
        'n_s': number of samples,
        'coart_frac': float (0.15-0.40),
        'diphthong': bool,
        'F_end': [f1,f2,f3,f4] or None,
        'r_f3': bool,
      }

    Returns:
      F_full: list of 4 arrays,
              total length = sum of n_s
      B_full: list of 4 arrays,
              total length = sum of n_s
      seg_ends: list of sample indices
                where each phoneme ends
    """
    if not phoneme_specs:
        return [np.zeros(1,dtype=DTYPE)]*4, \
               [np.zeros(1,dtype=DTYPE)]*4, \
               []

    n_total = sum(s['n_s']
                  for s in phoneme_specs)
    F_full  = [np.zeros(n_total,dtype=DTYPE)
               for _ in range(4)]
    B_full  = [np.zeros(n_total,dtype=DTYPE)
               for _ in range(4)]
    seg_ends = []

    # Track current formant position
    # Start at first phoneme's target
    F_current = list(
        phoneme_specs[0]['F_tgt'])

    pos = 0
    for si, spec in enumerate(
            phoneme_specs):
        n_s       = spec['n_s']
        F_tgt     = spec['F_tgt']
        B_tgt     = spec['B']
        F_end     = spec.get(
            'F_end', F_tgt)
        is_diph   = spec.get(
            'diphthong', False)
        r_f3      = spec.get('r_f3', False)
        cf        = spec.get(
            'coart_frac', 0.20)

        # Look ahead: where does the
        # NEXT phoneme want to start?
        if si < len(phoneme_specs)-1:
            F_next_tgt = phoneme_specs[
                si+1]['F_tgt']
        else:
            F_next_tgt = F_end \
                         if is_diph \
                         else F_tgt

        n_on  = int(cf * n_s)
        n_off = int(cf * n_s)
        n_mid = n_s - n_on - n_off
        if n_mid < 1:
            n_mid = 1
            n_on  = (n_s-1)//2
            n_off = n_s-1-n_on

        # F_from = where we actually are
        F_from = list(F_current)

        for fi in range(4):
            arr = np.zeros(n_s, dtype=DTYPE)

            # Onset: from actual position
            # to target
            if n_on > 0:
                arr[:n_on] = np.linspace(
                    float(F_from[fi]),
                    float(F_tgt[fi]),
                    n_on, dtype=DTYPE)

            # Mid: target or diphthong
            if n_mid > 0:
                if is_diph:
                    nm = int(n_mid*0.72)
                    nh = n_mid-nm
                    if nm > 0:
                        arr[n_on:
                            n_on+nm] = \
                            np.linspace(
                                float(F_tgt[fi]),
                                float(F_end[fi]),
                                nm, dtype=DTYPE)
                    if nh > 0:
                        arr[n_on+nm:
                            n_on+n_mid] = \
                            float(F_end[fi])
                else:
                    arr[n_on:
                        n_on+n_mid] = \
                        float(F_tgt[fi])

            # Offset: toward next phoneme
            # target
            if n_off > 0:
                f_off_from = (
                    float(F_end[fi])
                    if is_diph
                    else float(F_tgt[fi]))
                arr[n_on+n_mid:] = \
                    np.linspace(
                        f_off_from,
                        float(F_next_tgt[fi]),
                        n_off, dtype=DTYPE)

            # R: fast F3 drop
            if r_f3 and fi == 2:
                nd = min(
                    int(0.030*sr), n_s)
                arr[:nd] = np.linspace(
                    float(F_from[2]),
                    1690.0,
                    nd, dtype=DTYPE)
                arr[nd:] = 1690.0

            F_full[fi][pos:pos+n_s] = arr
            B_full[fi][pos:pos+n_s] = \
                float(B_tgt[fi])

        # Update F_current to actual
        # end position of this phoneme
        for fi in range(4):
            F_current[fi] = float(
                F_full[fi][pos+n_s-1])

        pos += n_s
        seg_ends.append(pos)

    return F_full, B_full, seg_ends


# ============================================================
# SOURCE BUILDER
# Build continuous source array
# matching the formant trajectory.
# ============================================================

def build_source(phoneme_specs,
                  pitch, sr=SR):
    """
    Build continuous source array.
    Each phoneme segment has its
    own source type.
    Crossfades at boundaries prevent
    clicks.
    """
    from scipy.signal import lfilter

    n_total = sum(s['n_s']
                  for s in phoneme_specs)
    source  = np.zeros(n_total, dtype=DTYPE)
    amp_env = np.zeros(n_total, dtype=DTYPE)

    # Pre-generate full voiced + noise
    # arrays to allow crossfades
    voiced_full = source_voiced(
        pitch, n_total, sr=sr)
    noise_full  = source_steady(
        n_total, sr=sr)

    pos = 0
    for spec in phoneme_specs:
        n_s     = spec['n_s']
        stype   = spec.get('source','voiced')
        amp     = spec.get('amp', 1.0)

        s = pos
        e = pos+n_s

        if stype == 'voiced':
            source[s:e] = voiced_full[s:e]
        elif stype == 'noise':
            source[s:e] = noise_full[s:e]
        elif stype == 'h':
            # H: noise → voiced crossfade
            n_h   = int(n_s * 0.20)
            n_x   = min(int(0.018*sr),
                         n_h, n_s-n_h)
            cs    = max(0, n_h-n_x)
            ne    = np.zeros(n_s,dtype=DTYPE)
            ve    = np.zeros(n_s,dtype=DTYPE)
            if cs>0: ne[:cs]=1.0
            if n_x>0:
                fo=f32(np.linspace(1,0,n_x))
                ne[cs:cs+n_x]=fo
                ve[cs:cs+n_x]=1.0-fo
            if cs+n_x<n_s:
                ve[cs+n_x:]=1.0
            source[s:e] = (
                noise_full[s:e]*ne +
                voiced_full[s:e]*ve)
        elif stype == 'stop_unvoiced':
            # Silence + burst + noise→voice
            clos_n  = spec.get('clos_n',0)
            burst_n = spec.get('burst_n',0)
            vot_n   = spec.get('vot_n',0)
            bamp    = spec.get('burst_amp',0.3)
            bhp     = spec.get('burst_hp',2000)
            # Closure: silence
            # Burst: noise spike
            if burst_n > 0:
                bs = clos_n
                be = bs+burst_n
                if be <= n_s:
                    burst = source_steady(
                        burst_n, sr=sr)
                    try:
                        from scipy.signal \
                            import lfilter
                        b,a = safe_hp(
                            bhp, sr)
                        burst = f32(
                            lfilter(b,a,burst))
                    except:
                        pass
                    benv = f32(np.exp(
                        -np.arange(burst_n)/
                        burst_n*20))
                    source[s+bs:s+be] = \
                        burst*benv*bamp
            # VOT: noise→voice
            vot_s = clos_n+burst_n
            vot_e = vot_s+vot_n
            if vot_n > 0 and vot_e <= n_s:
                ne2 = f32(np.linspace(
                    1,0,vot_n))
                ve2 = 1.0-ne2
                source[s+vot_s:s+vot_e] = (
                    noise_full[s+vot_s:
                                s+vot_e]*ne2 +
                    voiced_full[s+vot_s:
                                 s+vot_e]*ve2)
            # Transition: voiced
            tr_s = vot_e
            if tr_s < n_s:
                source[s+tr_s:e] = \
                    voiced_full[s+tr_s:e]

        elif stype == 'stop_voiced':
            clos_n  = spec.get('clos_n',0)
            burst_n = spec.get('burst_n',0)
            vot_n   = spec.get('vot_n',0)
            bamp    = spec.get('burst_amp',0.18)
            bhp     = spec.get('burst_hp',1000)
            # Closure: quiet voiced hum
            if clos_n > 0:
                source[s:s+clos_n] = \
                    voiced_full[s:s+clos_n]*0.06
            if burst_n > 0:
                bs=clos_n; be=bs+burst_n
                if be<=n_s:
                    burst=source_steady(
                        burst_n,sr=sr)
                    try:
                        b,a=safe_hp(bhp,sr)
                        burst=f32(
                            lfilter(b,a,burst))
                    except:
                        pass
                    benv=f32(np.exp(
                        -np.arange(burst_n)/
                        burst_n*20))
                    source[s+bs:s+be]=\
                        burst*benv*bamp
            vot_s=clos_n+burst_n
            vot_e=vot_s+vot_n
            if vot_n>0 and vot_e<=n_s:
                ne2=f32(np.linspace(1,0,vot_n))
                ve2=1.0-ne2
                source[s+vot_s:s+vot_e]=(
                    noise_full[s+vot_s:
                                s+vot_e]*ne2+
                    voiced_full[s+vot_s:
                                 s+vot_e]*ve2)
            tr_s=vot_e
            if tr_s<n_s:
                source[s+tr_s:e]=\
                    voiced_full[s+tr_s:e]

        elif stype == 'fric_v':
            # Voiced fricative:
            # FIX — voiced from start
            # noise band MIXED with voicing
            # not noise then voicing
            bands = spec.get('bands',[])
            n_gain = spec.get('n_gain',0.5)
            fric_n = source_steady(n_s,sr=sr)
            from scipy.signal import lfilter
            for lo,hi,g in bands:
                try:
                    b,a=safe_bp(
                        min(lo,sr*0.47),
                        min(hi,sr*0.48),sr)
                    fric_n+=f32(
                        lfilter(b,a,
                        source_steady(n_s,
                                       sr=sr))
                    )*g
                except:
                    pass
            mx=np.max(np.abs(fric_n))
            if mx>0: fric_n/=mx
            # FIX: voicing present
            # throughout — not delayed
            v_mix = 0.65
            n_mix = 0.35
            source[s:e] = (
                voiced_full[s:e]*v_mix +
                fric_n*n_gain*n_mix)

        elif stype == 'fric_u':
            bands  = spec.get('bands',[])
            d_res  = spec.get('d_res',None)
            d_bw   = spec.get('d_bw', None)
            n_gain = spec.get('n_gain',0.85)
            fric_n = source_steady(n_s,sr=sr)
            from scipy.signal import lfilter
            for lo,hi,g in bands:
                try:
                    b,a=safe_bp(
                        min(lo,sr*0.47),
                        min(hi,sr*0.48),sr)
                    fric_n=f32(
                        lfilter(b,a,fric_n))
                except:
                    pass
            if d_res is not None \
               and d_bw is not None:
                try:
                    lo_=max(100,
                             d_res-d_bw//2)
                    hi_=min(sr*0.48,
                             d_res+d_bw//2)
                    b,a=safe_bp(lo_,hi_,sr)
                    shaped=f32(
                        lfilter(b,a,fric_n))
                    # FIX: downstream
                    # cavity very dominant
                    fric_n=fric_n*0.15+\
                           shaped*0.85
                except:
                    pass
            mx=np.max(np.abs(fric_n))
            if mx>0: fric_n/=mx
            source[s:e]=fric_n*n_gain

        amp_env[s:e] = amp
        pos += n_s

    return f32(source), f32(amp_env)


# ============================================================
# PHONEME SPEC BUILDER
# Maps phoneme names to specs
# including corrected parameters
# ============================================================

def ph_spec(ph, dur_ms,
             pitch=PITCH,
             next_ph=None,
             sr=SR):
    """
    Build a phoneme spec dict
    for the continuous trajectory builder.

    All fixes applied here:
    - DH: dental F2=1800Hz
    - V: voiced from start
    - H: short (20% noise phase)
    - S: sharp downstream cavity
    """
    n_s = max(4, int(dur_ms/1000.0*sr))

    # Lookup formant targets
    def vf(v, wi=1.0):
        d = VOWEL_F.get(v)
        if d: return list(d[0]), list(d[1])
        CONS = {
            'M':([250,700,2200,3300],
                 [60,120,250,350]),
            'N':([250,900,2200,3300],
                 [60,120,250,350]),
            'NG':([250,700,2200,3300],
                  [60,120,250,350]),
            'L':([360,1000,2400,3300],
                 [80,160,220,320]),
            'R':([490,1350,1690,3300],
                 [80,120,180,260]),
            'W':([300,610,2200,3300],
                 [80,90,210,310]),
            'Y':([270,2100,3000,3700],
                 [65,100,160,220]),
            # FIX: DH dental closure
            # F2=1800Hz (front placement)
            'DH':([200,1800,2600,3400],
                  [100,150,250,350]),
            'V':([250,900,2200,3300],
                 [100,130,220,320]),
            'Z':([250,900,2200,3300],
                 [100,130,220,320]),
            'S':([300,1800,2600,3500],
                 [200,200,300,400]),
            'SH':([300,900,2200,3300],
                  [150,150,250,350]),
            'F':([300,900,2200,3300],
                 [200,200,300,400]),
            'TH':([300,900,2200,3300],
                  [200,200,300,400]),
            'H':([500,1500,2500,3500],
                 [200,220,320,420]),
            'P':([300,800,2200,3300],
                 [150,150,250,350]),
            'B':([200,800,2200,3300],
                 [100,120,220,320]),
            'T':([300,1800,2600,3500],
                 [200,200,300,400]),
            'D':([200,900,2200,3300],
                 [100,120,220,320]),
        }
        r = CONS.get(ph,
            ([500,1500,2500,3500],
             [200,200,300,400]))
        return list(r[0]), list(r[1])

    F,B = vf(ph)

    # Next phoneme formants for
    # offset transition target
    F_next = list(VOWEL_F.get(
        next_ph, {None:None}
    )[0]) if next_ph and \
             next_ph in VOWEL_F \
          else F

    base = {
        'ph': ph,
        'F_tgt': F,
        'B': B,
        'n_s': n_s,
        'coart_frac': 0.20,
        'diphthong': False,
        'F_end': None,
        'r_f3': False,
        'source': 'voiced',
        'amp': 1.0,
    }

    # Per-phoneme overrides
    if ph in VOWEL_F:
        vdata = VOWEL_F[ph]
        if len(vdata) > 2:
            base['diphthong'] = True
            base['F_end'] = list(vdata[2])
        base['source'] = 'voiced'
        base['coart_frac'] = 0.20

    elif ph == 'H':
        # FIX: H uses next vowel formants
        # with wide bandwidths
        if next_ph and next_ph in VOWEL_F:
            nv = VOWEL_F[next_ph]
            base['F_tgt'] = list(nv[0])
            base['B'] = [min(float(b)*3.2,
                              560.0)
                         for b in nv[1]]
            if len(nv)>2:
                base['F_end'] = list(nv[2])
        base['source'] = 'h'
        base['coart_frac'] = 0.15

    elif ph == 'DH':
        # FIX: dental — F2=1800Hz
        base['F_tgt'] = [200,1800,2600,3400]
        base['B']     = [100, 150, 250, 350]
        base['source']= 'voiced'
        base['coart_frac'] = 0.30
        base['amp']   = 0.85

    elif ph == 'V':
        # FIX: voiced from start
        base['source'] = 'fric_v'
        base['bands']  = [(200,9000,0.6)]
        base['n_gain'] = 0.28
        base['coart_frac'] = 0.25

    elif ph == 'Z':
        base['source'] = 'fric_v'
        base['bands']  = [(3500,12000,0.8)]
        base['n_gain'] = 0.50
        base['coart_frac'] = 0.25

    elif ph == 'S':
        # FIX: sharper downstream cavity
        base['source'] = 'fric_u'
        base['bands']  = [(4000,14000,1.0)]
        base['d_res']  = 8800
        base['d_bw']   = 800
        base['n_gain'] = 0.90
        base['coart_frac'] = 0.10

    elif ph in ('F','TH'):
        base['source'] = 'fric_u'
        base['bands']  = [(300,9000,0.8)]
        base['d_res']  = None
        base['d_bw']   = None
        base['n_gain'] = 0.35

    elif ph == 'SH':
        base['source'] = 'fric_u'
        base['bands']  = [(1000,8000,1.0)]
        base['d_res']  = 2500
        base['d_bw']   = 700
        base['n_gain'] = 0.78

    elif ph in ('M','N','NG'):
        base['source']     = 'voiced'
        base['coart_frac'] = 0.30

    elif ph in ('L','R','W','Y'):
        base['source']     = 'voiced'
        base['coart_frac'] = 0.38
        if ph == 'R':
            base['r_f3'] = True

    elif ph == 'W':
        base['source']     = 'voiced'
        base['coart_frac'] = 0.38

    elif ph in ('P','K','T'):
        vot = {'P':62,'K':80,'T':70}
        clos= {'P':55,'K':55,'T':50}
        bst = {'P':2, 'K':3, 'T':2}
        bhp = {'P':500,'K':1500,'T':4500}
        bam = {'P':0.28,'K':0.28,'T':0.30}
        f2l = {'P':720,'K':3000,'T':1800}
        base['source']   = 'stop_unvoiced'
        base['clos_n']   = int(
            clos[ph]/1000*sr)
        base['burst_n']  = int(
            bst[ph]/1000*sr)
        base['vot_n']    = int(
            vot[ph]/1000*sr)
        base['burst_hp'] = bhp[ph]
        base['burst_amp']= bam[ph]
        base['F_tgt']    = (
            VOWEL_F.get(next_ph,
            VOWEL_F['AH'])[0]
            if next_ph else
            [500,1500,2500,3500])
        base['B'] = [200,200,300,400]
        base['coart_frac'] = 0.15

    elif ph in ('B','D','G'):
        vot = {'B':14,'D':15,'G':16}
        clos= {'B':45,'D':40,'G':45}
        bst = {'B':2, 'D':2, 'G':2}
        bhp = {'B':300,'D':1200,'G':800}
        bam = {'B':0.16,'D':0.16,'G':0.14}
        base['source']   = 'stop_voiced'
        base['clos_n']   = int(
            clos[ph]/1000*sr)
        base['burst_n']  = int(
            bst[ph]/1000*sr)
        base['vot_n']    = int(
            vot[ph]/1000*sr)
        base['burst_hp'] = bhp[ph]
        base['burst_amp']= bam[ph]
        base['coart_frac'] = 0.15

    return base


# ============================================================
# PHRASE BUILDER
# ============================================================

PHON_DUR_BASE = {
    'AA':140,'AE':130,'AH':100,'AO':130,
    'AW':170,'AY':180,'EH':120,'ER':130,
    'IH':110,'IY':130,'OH':130,'OW':160,
    'OY':180,'UH':110,'UW':130,
    'M':85,'N':80,'NG':90,
    'L':80,'R':90,'W':90,'Y':80,
    'H':70,'DH':80,'V':85,'Z':95,
    'S':100,'SH':105,'F':90,'TH':90,
    'ZH':95,'P':90,'B':80,'T':85,
    'D':75,'K':90,'G':78,
}


def synth_phrase_continuous(
        words_phonemes, pitch=PITCH,
        dil=DIL, sr=SR):
    """
    Synthesize a phrase using the
    continuous formant tracker.

    words_phonemes: list of
      (word, [phoneme list]) tuples

    The entire phrase is ONE
    continuous formant trajectory.
    Word boundaries are marked only
    by amplitude dips — breath rests.
    No filter resets. No gaps.
    """
    from voice_physics_v2 import (
        breath_rest, WORD_WEIGHT
    )

    all_specs  = []
    word_marks = []  # (start_spec_idx,
                     #  word, n_specs)

    for wi, (word, phonemes) in \
            enumerate(words_phonemes):
        start_idx = len(all_specs)
        n_ph      = len(phonemes)

        for i, ph in enumerate(phonemes):
            next_ph = phonemes[i+1] \
                      if i<n_ph-1 \
                      else None
            # Look across word boundary
            if next_ph is None and \
               wi < len(words_phonemes)-1:
                next_word_phs = \
                    words_phonemes[wi+1][1]
                if next_word_phs:
                    next_ph = \
                        next_word_phs[0]

            d_ms = PHON_DUR_BASE.get(
                ph, 80) * dil

            spec = ph_spec(
                ph, d_ms, pitch,
                next_ph, sr)
            all_specs.append(spec)

        word_marks.append((
            start_idx, word,
            len(all_specs)-start_idx))

    if not all_specs:
        return f32(np.zeros(
            int(0.1*sr)))

    # Build continuous trajectory
    F_full, B_full, seg_ends = \
        build_continuous_trajectory(
            all_specs, sr=sr)

    n_total = sum(s['n_s']
                  for s in all_specs)

    # Build continuous source
    source, amp_env = build_source(
        all_specs, pitch, sr=sr)

    # Run through ONE tract
    # Never resets
    out, _ = tract(
        source, F_full, B_full,
        GAINS, states=None, sr=sr)

    # Apply nasal antiformants
    # at appropriate segments
    T = 1.0/sr
    NASAL_AF = {
        'M':(1000,300),
        'N':(1500,350),
        'NG':(2000,400),
    }
    pos = 0
    for spec in all_specs:
        ph  = spec['ph']
        n_s = spec['n_s']
        if ph in NASAL_AF:
            af, abw = NASAL_AF[ph]
            seg = out[pos:pos+n_s].copy()
            anti= np.zeros(n_s,dtype=DTYPE)
            y1=y2=0.0
            for i in range(n_s):
                a2=-np.exp(-2*np.pi*abw*T)
                a1=2*np.exp(-np.pi*abw*T)*\
                    np.cos(2*np.pi*af*T)
                b0=1.0-a1-a2
                y=b0*float(seg[i])+\
                  a1*y1+a2*y2
                y2=y1; y1=y; anti[i]=y
            out[pos:pos+n_s] = \
                seg-f32(anti)*0.50
            out[pos:pos+n_s] *= 0.52
            # Hard gate nasal release
            hg=int(0.012*sr)
            if hg>0 and \
               hg<n_s:
                out[pos+n_s-hg:
                    pos+n_s]=0.0
        pos += n_s

    # Build amplitude envelope
    # Words have natural stress contour
    # Word boundaries: breath amplitude dip
    amp_master = f32(np.ones(n_total))
    pos = 0
    for wi,(start_idx, word, n_specs) \
            in enumerate(word_marks):
        # Word start/end sample positions
        w_start = sum(
            all_specs[j]['n_s']
            for j in range(start_idx))
        w_end   = sum(
            all_specs[j]['n_s']
            for j in range(
                start_idx+n_specs))

        # After each word (except last):
        # brief amplitude dip
        if wi < len(word_marks)-1:
            wt = WORD_WEIGHT.get(
                word.lower(),
                WORD_WEIGHT['default'])
            pause_ms = wt[1]
            dip_n = int(
                pause_ms*dil/1000.0*sr*0.5)
            dip_n = min(dip_n,
                         w_end-w_start)
            if dip_n > 0:
                # Fade out end of word
                amp_master[
                    w_end-dip_n:w_end] *= \
                    f32(np.linspace(
                        1.0, 0.15, dip_n))
                # Fade in start of next word
                next_start = w_end
                if next_start < n_total:
                    fi_n = min(
                        dip_n,
                        n_total-next_start)
                    amp_master[
                        next_start:
                        next_start+fi_n] *= \
                        f32(np.linspace(
                            0.15, 1.0,
                            fi_n))

    # Phrase envelope
    phrase_atk = int(0.025*sr)
    phrase_rel = int(0.060*sr)
    if phrase_atk>0 and \
       phrase_atk<n_total:
        amp_master[:phrase_atk] *= f32(
            np.linspace(0,1,phrase_atk))
    if phrase_rel>0:
        amp_master[-phrase_rel:] *= f32(
            np.linspace(1,0,phrase_rel))

    out = out * amp_master
    mx  = np.max(np.abs(out))
    if mx>0: out/=mx
    return f32(out)


# ============================================================
# DIAGNOSTIC
# ============================================================

if __name__ == "__main__":

    print()
    print("PHRASE DIAGNOSTIC")
    print("'the voice was already here'")
    print("="*60)
    print()

    # The target phrase
    PHRASE = [
        ('the',     ['DH','AH']),
        ('voice',   ['V','OY','S']),
        ('was',     ['W','AH','Z']),
        ('already', ['AA','L','R',
                     'EH','D','IY']),
        ('here',    ['H','IH','R']),
    ]

    # Full phrase
    print("  Synthesizing full phrase...")
    seg = synth_phrase_continuous(
        PHRASE, PITCH, DIL)
    seg = apply_room(seg, rt60=1.5,
                      dr=0.50)
    write_wav(
        "output_diag/"
        "the_voice_was_already_here.wav",
        seg)
    print("  output_diag/"
          "the_voice_was_already_here.wav")

    # Each word isolated for comparison
    print()
    print("  Synthesizing words isolated...")
    for word, phs in PHRASE:
        seg = synth_phrase_continuous(
            [(word, phs)], PITCH, DIL)
        seg = apply_room(
            seg, rt60=1.3, dr=0.55)
        write_wav(
            f"output_diag/word_{word}.wav",
            seg)
        print(f"  word_{word}.wav")

    # Word pairs for boundary check
    print()
    print("  Word pair boundaries...")
    pairs = [
        ('the_voice',
         [('the',['DH','AH']),
          ('voice',['V','OY','S'])]),
        ('voice_was',
         [('voice',['V','OY','S']),
          ('was',['W','AH','Z'])]),
        ('was_already',
         [('was',['W','AH','Z']),
          ('already',['AA','L','R',
                       'EH','D','IY'])]),
        ('already_here',
         [('already',['AA','L','R',
                       'EH','D','IY']),
          ('here',['H','IH','R'])]),
    ]
    for label, wp in pairs:
        seg = synth_phrase_continuous(
            wp, PITCH, DIL)
        seg = apply_room(
            seg, rt60=1.4, dr=0.52)
        write_wav(
            f"output_diag/{label}.wav",
            seg)
        print(f"  {label}.wav")

    print()
    print("="*60)
    print()
    print("  Listen in order:")
    print()
    print("  Full phrase:")
    print("  afplay output_diag/"
          "the_voice_was_already_here.wav")
    print()
    print("  Word pairs (find the"
          " boundary artifacts):")
    for label,_ in pairs:
        print(f"  afplay output_diag/"
              f"{label}.wav")
    print()
    print("  Individual words:")
    for word,_ in PHRASE:
        print(f"  afplay output_diag/"
              f"word_{word}.wav")
    print()
    print("  WHAT TO LISTEN FOR:")
    print()
    print("  'the' — should sound like")
    print("  a soft voiced 'th' into 'uh'")
    print("  NOT like 'w' or 'whuyhe'")
    print()
    print("  'voice' — V should be")
    print("  voiced from the start,")
    print("  not static/F-like")
    print()
    print("  'was' — should be audible,")
    print("  not silent")
    print()
    print("  'already' — no stutters")
    print("  at consonant boundaries")
    print()
    print("  'here' — brief H breath,")
    print("  no long swoop")
    print()
