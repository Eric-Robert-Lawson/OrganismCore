TONNETZ POLYPHONIC ENGINE v6.8 — The Choir Sings

All five layers confirmed and integrated:

  Layer 1: Vectorized Rosenberg source
           Jitter + shimmer
           Phase accumulator invariant preserved

  Layer 2: Formant bank
           Flux + bandwidth modulation
           Sigmoid vowel glides
           Vowel shape follows Tonnetz motion

  Layer 3: Agent breath system
           Sympathetic contagion
           No mechanical breath noise
           Coverage constraint — puddle

  Layer 4: Room model
           Concert hall, mid position
           Early reflections + absorption
           RT60=2.0s

  Layer 5: Vowel identity
           The choir sings the shape
           of the harmony itself
           Opening vowels for rising motion
           Darkening vowels for resolution
           Sigmoid glides — not filter sweeps
           The glide IS the voice

Invariants from Parts 1-5 all preserved.

This is not a test.
This is a performance.
"""

import numpy as np
from scipy.signal import lfilter, butter
import mido
from mido import MidiFile, MidiTrack, Message
import wave as wave_module
import os

SR = 44100

# ============================================================
# JUST INTONATION
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

def ji_freq(a, b, tonic=261.63):
    if (a,b) in JI_RATIOS:
        p,q  = JI_RATIOS[(a,b)]
        freq = tonic*(p/q)
    else:
        freq = tonic*((3/2)**a)*((5/4)**b)
    while freq > tonic*2: freq /= 2
    while freq < tonic:   freq *= 2
    return freq

def coherence(a, b):
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
# COUNTERPOINT
# ============================================================

def tonnetz_direction(pf,pt):
    if pf is None or pt is None: return (0,0)
    return (pt[0]-pf[0],pt[1]-pf[1])

def motion_type_pair(d1,d2):
    if d1==(0,0) or d2==(0,0): return 'oblique'
    n1=d1[0]+d1[1]*0.5; n2=d2[0]+d2[1]*0.5
    if n1==0 or n2==0: return 'oblique'
    if d1==d2: return 'parallel'
    if np.sign(n1)!=np.sign(n2): return 'contrary'
    return 'similar'

VOICE_RANGES = {
    'soprano':{'a':(-1,3),'b':(0,2)},
    'alto':   {'a':(-1,2),'b':(-1,1)},
    'tenor':  {'a':(-2,2),'b':(-1,1)},
    'bass':   {'a':(-3,1),'b':(-2,0)},
}

def range_score(pos,vname):
    a,b = pos
    vr  = VOICE_RANGES.get(vname,VOICE_RANGES['tenor'])
    ok_a = vr['a'][0]<=a<=vr['a'][1]
    ok_b = vr['b'][0]<=b<=vr['b'][1]
    if ok_a and ok_b: return 1.0
    pen=0.0
    if not ok_a:
        pen+=min(abs(a-vr['a'][0]),
                 abs(a-vr['a'][1]))*0.25
    if not ok_b:
        pen+=min(abs(b-vr['b'][0]),
                 abs(b-vr['b'][1]))*0.25
    return max(0.0,1.0-pen)

TONNETZ_STEPS=[
    (1,0),(-1,0),(0,1),(0,-1),
    (1,1),(-1,-1),(1,-1),(-1,1),(0,0),
]

def get_positions(voice):
    return [p for p,_,_ in voice]

def enforce_contrary_pass(voices,vnames):
    adjusted=[]
    for vi,(voice,vname) in enumerate(
            zip(voices,vnames)):
        others=[get_positions(voices[j])
                for j in range(len(voices)) if j!=vi]
        new_v=[]
        for step,(pos,beats,vel) in enumerate(voice):
            if pos is None or step==0:
                new_v.append((pos,beats,vel)); continue
            prev=voice[step-1][0]
            if prev is None:
                new_v.append((pos,beats,vel)); continue
            my_dir=tonnetz_direction(prev,pos)
            odirs=[]
            for opl in others:
                if step<len(opl) and step-1<len(opl):
                    op,oc=opl[step-1],opl[step]
                    if op is not None and oc is not None:
                        odirs.append(
                            tonnetz_direction(op,oc))
            if not odirs:
                new_v.append((pos,beats,vel)); continue
            pc=sum(1 for od in odirs
                   if motion_type_pair(
                       my_dir,od)=='parallel')
            if pc>len(odirs)*0.5:
                bp,bs=pos,-999.0
                for da,db in TONNETZ_STEPS:
                    cand=(prev[0]+da,prev[1]+db)
                    cd=tonnetz_direction(prev,cand)
                    c_con=sum(1 for od in odirs
                        if motion_type_pair(
                            cd,od)=='contrary')
                    c_par=sum(1 for od in odirs
                        if motion_type_pair(
                            cd,od)=='parallel')
                    dist=(abs(cand[0]-pos[0])+
                          abs(cand[1]-pos[1]))
                    if dist>2: continue
                    sc=(c_con*1.0-c_par*0.8+
                        coherence(cand[0],cand[1])*0.4+
                        range_score(cand,vname)*0.3)
                    if sc>bs: bs=sc; bp=cand
                new_v.append((bp,beats,vel))
            else:
                new_v.append((pos,beats,vel))
        adjusted.append(new_v)
    return adjusted

def analyze_parallel_pct(voices):
    pairs=[]
    for i in range(len(voices)):
        for j in range(i+1,len(voices)):
            v1p=get_positions(voices[i])
            v2p=get_positions(voices[j])
            k=min(len(v1p),len(v2p))
            par=tot=0
            for s in range(1,k):
                d1=tonnetz_direction(v1p[s-1],v1p[s])
                d2=tonnetz_direction(v2p[s-1],v2p[s])
                mt=motion_type_pair(d1,d2)
                if mt!='oblique':
                    tot+=1
                    if mt=='parallel': par+=1
            if tot>0: pairs.append(par/tot)
    return np.mean(pairs) if pairs else 1.0

def iterative_enforce(voices,vnames,
                       target=0.22,max_passes=10):
    current=[list(v) for v in voices]
    prev_pct=analyze_parallel_pct(current)
    for p in range(max_passes):
        current=enforce_contrary_pass(current,vnames)
        pct=analyze_parallel_pct(current)
        print(f"  Pass {p+1}: parallel {pct*100:.1f}%")
        if pct<=target:
            print("  Target reached."); break
        if abs(pct-prev_pct)<0.005:
            print("  Converged."); break
        prev_pct=pct
    return current

def analyze_counterpoint(voices,names):
    results={}
    for i in range(len(voices)):
        for j in range(i+1,len(voices)):
            v1p=get_positions(voices[i])
            v2p=get_positions(voices[j])
            k=min(len(v1p),len(v2p))
            cnt={'contrary':0,'oblique':0,
                 'parallel':0,'similar':0}
            for s in range(1,k):
                d1=tonnetz_direction(v1p[s-1],v1p[s])
                d2=tonnetz_direction(v2p[s-1],v2p[s])
                cnt[motion_type_pair(d1,d2)]+=1
            tot=max(1,sum(cnt.values()))
            pair=f"{names[i]} vs {names[j]}"
            results[pair]={k:v/tot*100
                           for k,v in cnt.items()}
            flag=(" ✓" if cnt['parallel']/tot<0.25
                  else " ✗")
            print(f"  {pair}: "
                  f"contrary="
                  f"{cnt['contrary']/tot*100:.0f}% "
                  f"parallel="
                  f"{cnt['parallel']/tot*100:.0f}%"
                  f"{flag}")
    avg_par=np.mean([v['parallel']
                     for v in results.values()])
    avg_con=np.mean([v['contrary']
                     for v in results.values()])
    approved=avg_par<25 and avg_con>20
    print(f"\n  avg parallel={avg_par:.1f}%  "
          f"avg contrary={avg_con:.1f}%")
    print(f"  Counterpoint: "
          f"{'APPROVED' if approved else 'NEEDS WORK'}")
    return results,approved

# ============================================================
# FUGUE MATERIAL
# ============================================================

SUBJECT=[
    (( 0,0),1.5,72),(( 1,0),1.0,70),
    (( 2,0),1.0,68),(( 2,1),1.0,70),
    (( 1,1),1.0,68),(( 0,1),1.0,65),
    (( 0,0),2.5,74),
]
S=sum(b for _,b,_ in SUBJECT)

def make_answer(subj,offset=(1,0)):
    oa,ob=offset
    return [((a+oa,b+ob),beats,vel)
            for (a,b),beats,vel in subj]

ANSWER=make_answer(SUBJECT)
CS=[
    (( 0,1),1.5,60),(( 0,0),1.0,58),
    ((-1,0),1.0,55),((-1,-1),1.0,57),
    (( 0,-1),1.0,60),(( 0,0),1.0,62),
    (( 0,0),2.5,65),
]
SOP_FREE=[
    (( 0,2),2.0,70),(( 1,2),1.5,68),
    (( 1,1),1.5,72),(( 0,1),2.0,70),
    ((-1,1),1.5,67),((-1,2),1.5,65),
    (( 0,2),2.0,68),(( 0,1),1.5,70),
    (( 0,0),2.0,72),
]
ALT_FREE=[
    (( 1,0),2.0,63),(( 1,-1),1.5,60),
    (( 2,-1),1.5,58),(( 1,0),2.0,62),
    (( 0,0),1.5,65),(( 1,1),1.5,62),
    (( 0,1),2.0,65),(( 0,0),1.5,62),
    (( 0,0),2.0,60),
]
TEN_FREE=[
    (( 0,-1),2.0,58),((-1,-1),1.5,55),
    ((-1,0),1.5,58),(( 0,0),2.0,60),
    (( 1,0),1.5,58),(( 1,-1),1.5,56),
    (( 0,-1),2.0,58),(( 0,0),1.5,60),
    (( 0,0),2.0,58),
]
BAS_FREE=[
    ((-1,0),2.0,52),((-2,0),1.5,48),
    ((-2,-1),1.5,50),((-1,-1),2.0,52),
    ((-1,0),1.5,55),(( 0,0),1.5,52),
    (( 1,0),2.0,55),(( 0,0),1.5,52),
    (( 0,0),2.0,50),
]

def rest(beats): return [(None,beats,0)]

def build_fugue():
    v1=SUBJECT+CS+SOP_FREE
    v2=CS+ANSWER+ALT_FREE
    v3=TEN_FREE+SUBJECT+CS+[
       ((0,0),2.0,58),((-1,0),2.0,55),
       ((0,0),2.0,58)]
    v4=BAS_FREE+ANSWER+BAS_FREE+[
       ((0,0),2.0,50)]
    lens=[sum(b for _,b,_ in v)
          for v in [v1,v2,v3,v4]]
    mx=max(lens)
    vraw=[list(v)+(rest(mx-l) if mx-l>0 else [])
          for v,l in zip([v1,v2,v3,v4],lens)]
    print("\n  Contrary enforcement:")
    ve=iterative_enforce(
        vraw,['soprano','alto','tenor','bass'],
        target=0.22,max_passes=10)
    v1,v2,v3,v4=ve
    v1+=SUBJECT
    v2+=rest(4.0)+ANSWER
    v3+=rest(8.0)+SUBJECT
    v4+=rest(12.0)+ANSWER
    cad=[
        [((1,1),2.0,80),((0,1),1.5,78),
          ((0,0),5.5,94),((0,0),4.5,86),
          ((0,0),4.0,74),((0,0),4.5,56)],
        [((1,0),2.0,72),((0,0),1.5,68),
          ((0,0),5.5,84),((0,0),4.5,76),
          ((0,0),4.0,64),((0,0),4.5,48)],
        [((-1,1),2.0,62),((0,0),1.5,60),
          ((0,0),5.5,74),((0,0),4.5,66),
          ((0,0),4.0,54),((0,0),4.5,40)],
        [((-1,0),2.0,54),((0,0),1.5,52),
          ((0,0),5.5,64),((0,0),4.5,56),
          ((0,0),4.0,44),((0,0),4.5,32)],
    ]
    for i,(v,c) in enumerate(
            zip([v1,v2,v3,v4],cad)):
        v+=c
    return v1,v2,v3,v4

# ============================================================
# VOWEL SYSTEM
# The choir sings the shape of the harmony
# ============================================================

VOWEL_DATA = {
    'ah':{'f':[700, 1220,2600,3200],
          'b':[130,   70, 160, 200],
          'g':[6.0,  4.0, 1.8, 0.7]},
    'eh':{'f':[600, 1800,2550,3200],
          'b':[110,   90, 160, 200],
          'g':[5.5,  5.0, 1.8, 0.7]},
    'ee':{'f':[280, 2250,3000,3500],
          'b':[ 90,   80, 150, 200],
          'g':[4.0,  6.0, 2.2, 0.8]},
    'oh':{'f':[450,  800,2550,3200],
          'b':[120,   80, 160, 200],
          'g':[5.0,  3.5, 1.5, 0.6]},
    'oo':{'f':[300,  870,2250,3000],
          'b':[110,   80, 140, 180],
          'g':[5.0,  4.5, 1.3, 0.5]},
}

def tonnetz_to_vowel(pos, prev_pos, next_pos,
                      vel, max_vel):
    """
    Map Tonnetz position and motion to vowel.

    The choir sings the shape of the harmony:
      Rising motion (outward from tonic):
        Low coherence = open vowels (ah, eh)
        These are moments of tension and opening

      High point / peak velocity:
        'ee' — bright, arrived, forward

      Falling motion (toward tonic):
        'oh' — darkening, returning

      Resolution / high coherence / cadence:
        'oo' — closed, settled, home
        'ah' — open resolution (major cadence)

      Tonic / unison:
        'ah' — warm, beginning, pure
    """
    if pos is None:
        return 'ah'

    a,b = pos
    coh = coherence(a,b)

    # Detect motion direction
    if prev_pos is not None:
        da = a-prev_pos[0]
        db = b-prev_pos[1]
        net_motion = da+db*0.5
    else:
        net_motion = 0

    # Phrase peak detection
    vel_norm = vel/max(max_vel,1)
    at_peak  = vel_norm > 0.88

    # Vowel mapping
    if a==0 and b==0:
        return 'ah'        # tonic — warm, home
    elif at_peak:
        return 'ee'        # phrase peak — bright
    elif coh > 0.5:
        return 'ah'        # consonant — open, warm
    elif net_motion > 0.3:
        return 'eh'        # rising — forward
    elif net_motion < -0.3:
        return 'oh'        # falling — darkening
    elif coh < 0.15:
        return 'oo'        # dissonance — dark, tense
    else:
        return 'ah'        # default — open

def glide_speed_ms(dur_s, vel):
    """
    Glide speed follows note duration and velocity.
    Long notes: slower glide (settle in)
    Short notes: faster glide (moving through)
    High velocity: slightly faster (urgency)
    Confirmed: slow glide > fast glide
    """
    base_ms = np.clip(dur_s*120, 60, 220)
    vel_factor = 1.0-(vel/127.0)*0.25
    return base_ms*vel_factor

# ============================================================
# LAYER 3 — AGENT SYSTEM
# ============================================================

BREATH_RATES={
    'soprano':0.13,'alto':0.11,
    'tenor':0.10,'bass':0.08,
}
F1_TARGETS={
    'soprano':730,'alto':680,
    'tenor':700,'bass':650,
}

class SingerAgent:
    def __init__(self,part,idx,sr=SR,seed=None):
        self.part  =part; self.idx=idx; self.sr=sr
        self.rng   =np.random.RandomState(
            seed if seed is not None
            else np.random.randint(0,99999))
        self.breath_level   =self.rng.uniform(0.6,1.0)
        self.breath_rate    =BREATH_RATES[part]
        self.in_breath      =False
        self.breath_timer   =0.0
        self.breath_duration=0.0
        self.min_breath_int =self.rng.uniform(4.0,6.0)
        self.last_breath_t  =-999.0
        self.re_entry_active=False
        self.re_entry_timer =0.0
        self.re_entry_dur   =1.5
        self.amplitude      =1.0
        self.sympathetic_amp=1.0
        self.f1_current     =float(F1_TARGETS[part])
        self.f1_target      =float(F1_TARGETS[part])

    def update(self,dt,t_global,
               ens_active,part_active,
               phrase_peak_prox,ens_f1_mean,
               neighbor_breathing=False):
        if not self.in_breath:
            self.breath_level-=self.breath_rate*dt
            self.breath_level =max(0.0,
                                    self.breath_level)
        target_symp=(0.70 if neighbor_breathing
                     and not self.in_breath
                     else 1.0)
        self.sympathetic_amp+=(
            (target_symp-self.sympathetic_amp)
            *min(dt*8.0,1.0))
        if (not self.in_breath and
                not self.re_entry_active):
            needs =(self.breath_level<0.22)
            t_ok  =(t_global-self.last_breath_t>
                    self.min_breath_int)
            cov_ok=(ens_active>=2 and part_active>=1)
            ph_ok =(phrase_peak_prox<0.85)
            if needs and t_ok and cov_ok and ph_ok:
                self.in_breath      =True
                self.breath_timer   =0.0
                self.breath_duration=self.rng.uniform(
                    0.30,0.50)
                self.last_breath_t  =t_global
        if self.in_breath:
            self.breath_timer+=dt
            ramp_out=0.08
            if self.breath_timer<ramp_out:
                self.amplitude=max(
                    0.0,
                    1.0-self.breath_timer/ramp_out)
            else:
                self.amplitude=0.0
            if self.breath_timer>=self.breath_duration:
                self.in_breath      =False
                self.re_entry_active=True
                self.re_entry_timer =0.0
                self.breath_level   =self.rng.uniform(
                    0.75,0.95)
        if self.re_entry_active:
            self.re_entry_timer+=dt
            t_norm=min(
                self.re_entry_timer/self.re_entry_dur,
                1.0)
            self.amplitude =0.4+0.6*(t_norm**0.7)
            blend          =0.4+0.6*t_norm
            self.f1_current=(
                blend*self.f1_target+
                (1-blend)*ens_f1_mean)
            if t_norm>=1.0:
                self.re_entry_active=False
                self.amplitude      =1.0
                self.f1_current     =self.f1_target
        return (self.amplitude*self.sympathetic_amp,
                self.f1_current)

    def is_active(self):
        return (not self.in_breath and
                self.amplitude>0.05)

def compute_envelopes(agents,dur_s,sr=SR,
                       phrase_peak_prox=0.5):
    dt  =1.0/sr; n_s=int(dur_s*sr); n=len(agents)
    amp_envs=np.ones((n,n_s))
    f1_envs =np.zeros((n,n_s))
    ens_f1  =float(F1_TARGETS[agents[0].part])
    for i in range(n_s):
        t_g   =i*dt
        active=[a.is_active() for a in agents]
        ens_a =sum(active)
        for k,agent in enumerate(agents):
            part_a=sum(active[j]
                       for j in range(n) if j!=k)
            nb    =any(agents[j].in_breath
                       for j in range(n) if j!=k)
            a_val,f1_val=agent.update(
                dt,t_g,ens_a,part_a,
                phrase_peak_prox,ens_f1,
                neighbor_breathing=nb)
            amp_envs[k,i]=a_val
            f1_envs[k,i] =f1_val
    return amp_envs,f1_envs

# ============================================================
# LAYER 1+2+5 — VOICE WITH VOWEL IDENTITY
# ============================================================

def formant_resonator_block(signal,f_c_arr,
                              bw_arr,gain,sr=SR):
    n_s=len(signal); block=256
    out=np.zeros(n_s); zi=np.zeros(2)
    for start in range(0,n_s,block):
        end =min(start+block,n_s)
        fc_b=float(np.mean(f_c_arr[start:end]))
        bw_b=float(np.mean(bw_arr[start:end]))
        fc_b=np.clip(fc_b,80,sr*0.45)
        bw_b=np.clip(bw_b,20,800)
        r   =np.exp(-np.pi*bw_b/sr)
        th  =2*np.pi*fc_b/sr
        b   =np.array([1-r,0.0,0.0])
        a   =np.array([1.0,-2*r*np.cos(th),r*r])
        try:
            seg,zi=lfilter(b,a,
                signal[start:end],zi=zi)
            out[start:end]=seg
        except Exception:
            zi=np.zeros(2)
    return out*gain

def render_singing_note(freq, amp, dur_s,
                         vowel_cur, vowel_nxt,
                         sr=SR, velocity=80,
                         cents_offset=0.0,
                         amp_env=None,
                         f1_agent_env=None):
    """
    Render one note with vowel identity.
    The note begins on vowel_cur and glides
    toward vowel_nxt in the final portion.
    This is the voice saying something —
    not sustaining a tone.
    """
    n_s      = int(dur_s*sr)
    t_arr    = np.arange(n_s)/sr
    vel_norm = velocity/127.0
    freq     = freq*(2**(cents_offset/1200))

    # Vibrato
    vib_rate  = 4.8+np.random.uniform(-0.1,0.1)
    vib_depth = 0.011
    vib_onset = min(0.22,dur_s*0.38)
    vib_env   = (np.clip(
                    (t_arr-vib_onset)/0.18,0,1)
                 if dur_s>0.45
                 else np.zeros(n_s))
    freq_base = freq*(1+vib_depth*vib_env*
                      np.sin(2*np.pi*vib_rate*t_arr))

    # Jitter
    fn=np.random.normal(0,1.5,n_s)
    try:
        bj,aj=butter(2,min(30/(sr/2),0.49),
                     btype='low')
        fn=lfilter(bj,aj,fn)
    except Exception:
        fn=np.zeros(n_s)
    freq_arr=np.clip(
        freq_base+fn,freq*0.8,freq*1.2)

    # Vectorized Rosenberg — INVARIANT PRESERVED
    phase_norm=np.cumsum(freq_arr/sr)%1.0
    oq        =0.65
    source    =np.where(
        phase_norm<oq,
        (phase_norm/oq)*(2-phase_norm/oq),
        1-(phase_norm-oq)/(1-oq+1e-9))
    source    =np.diff(source,prepend=source[0])

    # Shimmer
    sn=np.random.normal(0,1.0,n_s)
    try:
        bs,as_=butter(2,min(25/(sr/2),0.49),
                      btype='low')
        sn=lfilter(bs,as_,sn)
    except Exception:
        sn=np.zeros(n_s)
    source=source*np.clip(
        1.0+0.3*sn/3.0,0.3,2.0)

    mx=np.max(np.abs(source))
    if mx>0: source/=mx

    # Aspiration
    ga=np.random.normal(0,0.05,n_s)
    try:
        bg,ag=butter(2,
            [min(500/(sr/2),0.49),
             min(3000/(sr/2),0.49)],
            btype='band')
        ga=lfilter(bg,ag,ga)
    except Exception:
        ga=np.zeros(n_s)
    excitation=source+ga*0.05

    # Build vowel trajectory for this note
    # Steady on vowel_cur, glide to vowel_nxt
    vc = VOWEL_DATA.get(vowel_cur,VOWEL_DATA['ah'])
    vn = VOWEL_DATA.get(vowel_nxt,VOWEL_DATA['ah'])

    glide_ms = glide_speed_ms(dur_s,velocity)
    n_glide  = int(glide_ms/1000*sr)
    n_steady = max(n_s-n_glide, int(n_s*0.55))
    n_glide  = n_s-n_steady

    # Formant trajectories
    f_arrays = []
    b_arrays = []
    g_arrays = []
    for fi in range(4):
        f_s = vc['f'][fi]
        f_e = vn['f'][fi]
        b_s = vc['b'][fi]
        b_e = vn['b'][fi]
        g_s = vc['g'][fi]
        g_e = vn['g'][fi]

        f_arr = np.full(n_s, float(f_s))
        b_arr = np.full(n_s, float(b_s))
        g_arr = np.full(n_s, float(g_s))

        if n_glide > 0:
            t_g = np.linspace(0,1,n_glide)
            # Sigmoid glide — confirmed natural
            sig = 1/(1+np.exp(-10*(t_g-0.5)))
            f_arr[n_steady:] = f_s+(f_e-f_s)*sig
            b_arr[n_steady:] = b_s+(b_e-b_s)*sig
            g_arr[n_steady:] = g_s+(g_e-g_s)*sig

        f_arrays.append(f_arr)
        b_arrays.append(b_arr)
        g_arrays.append(g_arr)

    # Apply formant flux on F1, F2
    # ON TOP of vowel trajectory
    voiced = np.zeros(n_s)
    for fi in range(4):
        f_c_base = f_arrays[fi]
        bw_base  = b_arrays[fi]
        g_base   = g_arrays[fi]

        if fi < 2:
            rate  = [1.7,2.3][fi]
            depth = [20, 38][fi]
            ph_off= np.random.uniform(0,2*np.pi)
            rw    = np.random.normal(0,1.0,n_s)
            try:
                brw,arw=butter(2,
                    min(3.0/(sr/2),0.49),
                    btype='low')
                rw=lfilter(brw,arw,rw)
            except Exception:
                rw=np.zeros(n_s)
            rw=rw/max(np.max(np.abs(rw)),1e-10)*10

            # Agent F1 modulation during re-entry
            if fi==0 and f1_agent_env is not None:
                # Blend agent re-entry with vowel traj
                f1_agent_n = min(
                    len(f1_agent_env),n_s)
                f_c_arr    = f_c_base.copy()
                f_c_arr[:f1_agent_n] = (
                    0.6*f_c_base[:f1_agent_n]+
                    0.4*f1_agent_env[:f1_agent_n])
            else:
                f_c_arr = f_c_base.copy()

            f_c_arr += (depth*np.sin(
                2*np.pi*rate*t_arr+ph_off)+rw)
        else:
            f_c_arr = f_c_base.copy()

        # BW modulation
        bw_mod  = bw_base*(1.0-0.35*vel_norm)
        bw_flux = bw_mod*(1.0+0.12*np.sin(
            2*np.pi*1.2*t_arr+
            np.random.uniform(0,2*np.pi)))
        bw_arr  = np.clip(bw_flux,30,500)

        out    = formant_resonator_block(
            excitation,f_c_arr,bw_arr,1.0,sr)
        voiced += out*g_base

    # Turbulence
    turb=np.random.normal(0,0.03,n_s)
    try:
        bt,at=butter(2,
            [min(2000/(sr/2),0.49),
             min(6000/(sr/2),0.49)],
            btype='band')
        turb=lfilter(bt,at,turb)
    except Exception:
        turb=np.zeros(n_s)
    voiced=voiced+turb*0.8

    # Envelope
    atk_s=min(0.25+(1-vel_norm)*0.08,dur_s*0.38)
    atk_n=int(atk_s*sr)
    rel_n=int(min(0.28,dur_s*0.36)*sr)
    env  =np.ones(n_s)
    if 0<atk_n<n_s:
        atk_c =np.linspace(0,1,atk_n)**0.65
        shim_t=np.linspace(0,atk_s,atk_n)
        shim_e=(1+0.05*
                np.sin(2*np.pi*11*shim_t)*
                (1-atk_c))
        env[:atk_n]=atk_c*shim_e
    if 0<rel_n<n_s:
        env[-rel_n:]=np.linspace(1,0,rel_n)**1.2

    result=voiced*env

    # Apply agent amplitude envelope
    # NO internal normalization — preserve dynamics
    if amp_env is not None:
        n_min=min(len(result),n_s,len(amp_env))
        result[:n_min]*=amp_env[:n_min]

    result*=amp
    return result

# ============================================================
# LAYER 4 — ROOM
# ============================================================

class RoomReverb:
    def __init__(self,rt60=2.0,sr=SR,
                 direct_ratio=0.45):
        self.sr           =sr
        self.rt60         =rt60
        self.direct_ratio =direct_ratio
        scale=rt60/2.0
        bd=[int(d*scale*sr/44100)
            for d in [1557,1617,1491,1422,
                       1277,1356]]
        self.comb_delays =[max(100,d) for d in bd]
        self.ap_delays   =[max(50,int(225*scale)),
                           max(50,int(556*scale))]
        self.comb_buffers=[np.zeros(d)
                           for d in self.comb_delays]
        self.comb_ptrs   =[0]*len(self.comb_delays)
        self.ap_buffers  =[np.zeros(d)
                           for d in self.ap_delays]
        self.ap_ptrs     =[0]*2
        self._gains()

    def _gains(self):
        rt60=self.rt60
        self.comb_gains=[float(np.clip(
            10**(-3*(d/self.sr)/max(rt60,0.1)),
            0,0.97))
            for d in self.comb_delays]
        self.ap_gains=[0.7,0.7]

    def process(self,audio):
        n  =len(audio)
        dr =self.direct_ratio

        # Early reflections
        early=audio.copy()
        for gap_ms,gain in [(12,0.78),(23,0.65),
                             (38,0.54),(55,0.42),
                             (78,0.31)]:
            d=int(gap_ms*self.sr/1000)
            if d<len(audio):
                delayed=np.zeros_like(audio)
                delayed[d:]=audio[:-d]*gain
                early+=delayed

        # Absorption
        try:
            b_abs,a_abs=butter(1,
                min(4000/(self.sr/2),0.49),
                btype='low')
            early=lfilter(b_abs,a_abs,early)*0.88+\
                  early*0.12
        except Exception:
            pass

        # Reverb tail
        cout=np.zeros(n)
        for c in range(len(self.comb_delays)):
            buf=self.comb_buffers[c].copy()
            ptr=self.comb_ptrs[c]
            g  =self.comb_gains[c]
            d  =self.comb_delays[c]
            for i in range(n):
                dl=buf[ptr]; buf[ptr]=audio[i]+g*dl
                ptr=(ptr+1)%d
                cout[i]+=dl/len(self.comb_delays)
            self.comb_buffers[c]=buf
            self.comb_ptrs[c]  =ptr
        ap=cout.copy()
        for ai in range(2):
            buf=self.ap_buffers[ai].copy()
            ptr=self.ap_ptrs[ai]
            g  =self.ap_gains[ai]
            d  =self.ap_delays[ai]
            for i in range(n):
                dl=buf[ptr]; w=ap[i]+g*dl
                buf[ptr]=w; ptr=(ptr+1)%d
                ap[i]=-g*w+dl
            self.ap_buffers[ai]=buf
            self.ap_ptrs[ai]  =ptr

        tail_gain=1.0-dr
        return (dr*audio*0.55 +
                0.25*early +
                tail_gain*ap*0.38)

# ============================================================
# MAIN RENDER
# ============================================================

PART_NAMES=['soprano','alto','tenor','bass']

def render_v68(voices, filename,
                sr=SR, bpm=40,
                rt60=2.0,
                direct_ratio=0.45):
    """
    The full render — all five layers.
    The choir sings.
    """
    bps    =bpm/60.0
    total_s=max(sum(b for _,b,_ in v)/bps+10.0
                for v in voices)
    output =np.zeros(int(total_s*sr))
    omults =[2.0,1.5,1.0,0.5]

    reverbs=[RoomReverb(rt60,sr,direct_ratio)
             for _ in voices]

    all_agents=[]
    for vi,part in enumerate(PART_NAMES):
        all_agents.append([
            SingerAgent(part,i,sr,seed=vi*100+i)
            for i in range(3)])

    t_global=[0.0]

    for vi,(voice,agents) in enumerate(
            zip(voices,all_agents)):
        cohs=[coherence(p[0],p[1]) if p else None
              for p,_,_ in voice]
        vels=[vel for _,_,vel in voice]
        max_vel=max(v for v in vels if v>0) or 127
        cur=0; rev=reverbs[vi]
        part=PART_NAMES[vi]

        for i,(pos,beats,vel) in enumerate(voice):
            dur_s=beats/bps
            n_s  =int(dur_s*sr)

            if pos is None:
                cur+=n_s; t_global[0]+=dur_s
                continue

            a,b  =pos
            coh  =cohs[i] or 1.0
            freq =ji_freq(a,b)*omults[vi]
            amp  =(vel/127.0)*0.52
            ppp  =vel/max_vel

            # Vowel assignment
            prev_pos=(voice[i-1][0]
                      if i>0 else None)
            next_pos=(voice[i+1][0]
                      if i<len(voice)-1 else None)
            vowel_cur=tonnetz_to_vowel(
                pos,prev_pos,next_pos,vel,max_vel)
            vowel_nxt=tonnetz_to_vowel(
                next_pos,pos,
                voice[i+2][0]
                if i<len(voice)-2 else None,
                voice[i+1][2] if i<len(voice)-1
                else vel,
                max_vel) if next_pos else vowel_cur

            # Agent envelopes
            amp_envs,f1_envs=compute_envelopes(
                agents,dur_s,sr,
                phrase_peak_prox=ppp)

            # Render 3 singers
            cents =[0.0,+11.0,-17.0]
            vel_mod=int(vel*(0.7+0.3*coh))
            vel_mod=max(40,min(127,vel_mod))
            note_mix=np.zeros(n_s)

            for k in range(3):
                sig=render_singing_note(
                    freq, amp/3, dur_s,
                    vowel_cur, vowel_nxt,
                    sr=sr,
                    velocity=vel_mod,
                    cents_offset=cents[k],
                    amp_env=amp_envs[k],
                    f1_agent_env=f1_envs[k])
                n_min=min(len(sig),n_s)
                note_mix[:n_min]+=sig[:n_min]

            t_global[0]+=dur_s

            # RT60 varies with coherence
            rev.rt60=0.8+coh*2.2
            rev._gains()
            processed=rev.process(note_mix)

            # Tonnetz lean
            prev=cohs[i-1] if i>0 else None
            nxt =(cohs[i+1]
                  if i<len(cohs)-1 else None)
            if nxt and nxt>coh:
                lean=-int(0.055*n_s)
            elif prev and prev>coh:
                lean= int(0.045*n_s)
            else:
                lean= int(0.06*n_s*(1-coh))
            onset=max(0,cur+lean)

            end=min(onset+len(processed),len(output))
            seg=end-onset
            if seg>0:
                output[onset:end]+=processed[:seg]
            cur+=n_s

    mx=np.max(np.abs(output))
    if mx>0: output=output/mx*0.82
    out_i=(output*32767).astype(np.int16)
    with wave_module.open(filename,'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(out_i.tobytes())
    dur=len(output)/sr
    print(f"  {filename}")
    print(f"  {int(dur//60)}m{dur%60:.0f}s")

def midi_out(voices,filename,bpm=40):
    mid  =MidiFile(type=1,ticks_per_beat=960)
    tempo=mido.bpm2tempo(bpm)
    octs =[1,0,0,-1]
    for vi,voice in enumerate(voices):
        tr=MidiTrack(); mid.tracks.append(tr)
        if vi==0:
            tr.append(mido.MetaMessage(
                'set_tempo',tempo=tempo,time=0))
        tr.append(Message('program_change',
            program=52,channel=vi,time=0))
        for pos,beats,vel in voice:
            ticks=int(beats*960)
            if pos is None:
                tr.append(Message('note_off',
                    note=60,velocity=0,
                    channel=vi,time=ticks))
                continue
            freq=ji_freq(pos[0],pos[1])*(
                2**octs[vi])
            mn=int(round(69+12*np.log2(freq/440)))
            mn=max(24,min(96,mn))
            tr.append(Message('note_on',
                note=mn,velocity=vel,
                channel=vi,time=0))
            tr.append(Message('note_off',
                note=mn,velocity=0,
                channel=vi,time=ticks))
    mid.save(filename)
    print(f"  {filename}  [MIDI]")

# ============================================================
# MAIN
# ============================================================

if __name__=="__main__":
    os.makedirs("output_v68",exist_ok=True)
    print()
    print("TONNETZ POLYPHONIC ENGINE v6.8")
    print("="*60)
    print()
    print("All five layers. The choir sings.")
    print()
    print("Layer 1: Vectorized Rosenberg source")
    print("Layer 2: Formant flux + BW modulation")
    print("Layer 3: Agent breath system")
    print("Layer 4: Concert hall, mid position")
    print("Layer 5: Vowel identity")
    print("         The choir sings the harmony")
    print()

    print("Building fugue...")
    v1,v2,v3,v4=build_fugue()
    print()
    print("Counterpoint:")
    _,approved=analyze_counterpoint(
        [v1,v2,v3,v4],
        ['Soprano','Alto','Tenor','Bass'])
    print()
    print("Rendering...")
    print()
    print("  The choir sings.")
    print("  Concert hall. Mid position.")
    print("  BPM=40 — slow enough to hear")
    print("  every vowel transition.")
    print()

    render_v68(
        [v1,v2,v3,v4],
        "output_v68/fugue_choir_sings.wav",
        bpm=40,
        rt60=2.0,
        direct_ratio=0.45)

    midi_out(
        [v1,v2,v3,v4],
        "output_v68/fugue.mid")

    print()
    print("="*60)
    print()
    print("  afplay output_v68/fugue_choir_sings.wav")
    print()
    print("This is the first render where the")
    print("choir sings the shape of the harmony.")
    print("The vowels follow the Tonnetz motion.")
    print("Opening where the harmony opens.")
    print("Darkening where it resolves.")
    print()
    print("This is what I have to share.")
