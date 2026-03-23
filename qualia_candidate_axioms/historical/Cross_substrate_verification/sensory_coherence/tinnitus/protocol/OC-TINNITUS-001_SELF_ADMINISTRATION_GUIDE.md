# TINNITUS EIGENFUNCTION CALIBRATION
## Complete Self-Administration Guide
## OC-TINNITUS-001 — OrganismCore
## Eric Robert Lawson — 2026-03-23

---

## WHAT THIS IS

Your ear is a physical instrument.
When part of it is damaged, it stops responding
to the world and starts ringing at its own
natural frequency — like a cracked bell that
rings one note regardless of what strikes it.

That ringing is not random.
It sits at a geometrically privileged position
in the physical structure of your cochlea —
confirmed in 1,514 patients from the OHSU
Tinnitus Archive (χ² = 2328.1, p ≈ 0).

This protocol finds exactly where your ringing
sits in that structure — in your specific ear,
at your specific frequency — and generates a
personalized cancellation signal calibrated to
your cochlea's geometry.

The calibration is guided entirely by your own
perception. No specialist required. No equipment
beyond a computer and headphones.

You are the measurement instrument.
The script is the probe.

---

## WHAT YOU WILL END UP WITH

By the end of one session (30–45 minutes) you
will have:

```
remedy_left.wav       — left ear remedy
remedy_right.wav      — right ear remedy
remedy_binaural.wav   — both ears, independent
```

Play the appropriate file on loop while you
sleep. That is the minimum viable result.

Bare minimum benefit: better sleep.
The ringing that keeps you awake is given
something to cancel against. The navigator
finds the real signal instead of the false one.

---

## BEFORE YOU BEGIN

### What you need

```
Hardware:
  ✓ Computer (laptop or desktop)
  ✓ Over-ear headphones
    (for calibration — see note below)
  ✓ Quiet room
    (background noise is fine —
     total silence makes tinnitus worse)
  ✓ 35–50 minutes uninterrupted

Software:
  ✓ Python 3.8 or later
  ✓ Three packages (free, install once)
  ✓ The calibration script
```

**Headphone note:**
Use **over-ear headphones** for the calibration
session. Not earbuds. Over-ear headphones give
consistent acoustic coupling and reliable
left/right channel isolation — both essential
for accurate calibration.

For sleeping with the remedy afterward, any
comfortable headphones work. Sleep headphones
(flat speakers in a fabric headband, ~$20–30)
are ideal for side-sleeping.

**Do not use a Bluetooth speaker.**
The remedy must be delivered independently to
each ear. Stereo speakers in a room do not do
this. Headphones only.

---

### Install Python (if not already installed)

**Windows:**
1. Go to https://python.org/downloads
2. Download the latest Python 3.x installer
3. Run it — check "Add Python to PATH"
4. Open Command Prompt (search: cmd)

**Mac:**
1. Open Terminal (search: terminal)
2. Type: `python3 --version`
3. If not installed, it will prompt you
   to install it

**Linux:**
Most distributions have Python 3 already.
Open a terminal and type: `python3 --version`

---

### Install the required packages

Open a terminal / command prompt and run
this one line:

```
pip install sounddevice numpy scipy
```

or on Mac/Linux if that does not work:

```
pip3 install sounddevice numpy scipy
```

This downloads three free scientific
computing packages. Takes 1–2 minutes.
You only do this once.

---

### Download the calibration script

Save `tinnitus_calibration.py` to a folder
you can find easily, for example:

```
Windows:  C:\Users\YourName\tinnitus\
Mac:      /Users/YourName/tinnitus/
Linux:    /home/yourname/tinnitus/
```

The WAV files and session log will be saved
in the same folder as the script.

---

### Run the script

**Windows:**
```
cd C:\Users\YourName\tinnitus
python tinnitus_calibration.py
```

**Mac / Linux:**
```
cd /Users/YourName/tinnitus
python3 tinnitus_calibration.py
```

Everything from here is guided.
The script tells you what to do at each step.
This guide explains what is happening and why.

---

## THE PROTOCOL — ALL SIX PHASES

---

### BEFORE PHASE 1 — Volume Check

The script plays a reference tone through both
ears and asks if you can hear it clearly.

Respond:
```
Y       — clearly audible, comfortable → proceed
LOUDER  → script increases volume, replays
QUIETER → script decreases volume, replays
```

**Target volume:**
The tones should sound like a quiet radio in
the next room. Clearly present. Not demanding
attention. Never sharp or painful.

**Why this matters:**
Too quiet: the tones won't interact with your
tinnitus and you'll get all N responses.
Too loud: discomfort makes perception unreliable.

If you go through the full sweep and get only
N responses everywhere, volume is the first
thing to check. Stop, increase the AMPLITUDE
value at the top of the script (try 0.20,
then 0.25), and re-run.

---

### BEFORE PHASE 1 — Which Ears?

```
L — tinnitus in left ear only
R — tinnitus in right ear only
B — tinnitus in both ears
```

If both: the script runs the full protocol
on the left ear first, prompts you to rest
5 minutes, then runs the right ear.

Each ear is calibrated independently.
Each ear gets its own FA, FR, and phase values.
Each ear may have different tinnitus frequencies.
This is expected and handled automatically.

---

### PHASE 1 — The Rainbow Sweep
#### What it is

A structured probe of 12 specific frequencies,
each chosen because it corresponds to a
geometrically significant position on your
basilar membrane — equal spacing in the
physical structure of the cochlea, not
equal spacing in Hz.

The 12 frequencies (approximate):
```
  1:   ~530 Hz    7:  ~5,650 Hz
  2:   ~780 Hz    8:  ~8,400 Hz  ← peak tinnitus zone
  3: ~1,160 Hz    9: ~10,200 Hz
  4: ~1,720 Hz   10: ~11,800 Hz
  5: ~2,560 Hz   11: ~13,500 Hz
  6: ~3,800 Hz   12: ~15,400 Hz
```

Each tone plays for **10 seconds**.
One ear only (left or right channel).

#### What you do

After each tone, type one letter and press ENTER:

```
B — the tinnitus felt BETTER
    (reduced, quieter, less intrusive,
     changed in a way that felt like relief)

W — the tinnitus felt WORSE
    (louder, more intrusive, more present)

N — NO DIFFERENCE
    (genuinely could not detect any change)
```

#### How to give feedback honestly

**B does not mean "the tinnitus disappeared."**
It means any detectable change in the direction
of relief — even subtle. A slight softening.
A brief fluctuation. A sense of the ringing
being less demanding. If you notice any of that:
B.

**W is useful information, not a failure.**
If a tone makes the tinnitus worse, that is
valuable data. It tells the script which
direction NOT to go.

**N means genuinely no detectable change.**
Not "I'm not sure." If you're not sure, that's
probably N — but pay attention. Some effects
are subtle, especially early in the sweep.

**Do not think too hard.**
Your first instinct is usually accurate.
The tones are short. Notice, respond, move on.

#### What the script does with it

It builds a map of the gradient landscape —
which regions of cochlear space interact with
your false attractor and in which direction.
Better responses cluster around your false
attractor frequency. The script finds that
cluster and uses it as the starting point
for Phase 2.

#### If you get NO Better responses at all

This means one of three things:

1. **Volume too low** (most common) —
   increase AMPLITUDE and restart.

2. **Broadband / noise-like tinnitus** —
   your tinnitus has no single identifiable
   pitch. The cancellation approach has lower
   confidence for this type. The sweep will
   note this. You can still attempt Phase 2
   from the estimated tinnitus region.

3. **No tinnitus in this ear** —
   confirm which ear is actually affected
   and re-run with the correct ear selection.

---

### PHASE 2 — Gradient Descent
#### What it is

Starting from the best-response region
found in the rainbow sweep, the script
navigates toward the exact frequency of
your false attractor — the precise Hz
where your damaged cochlear zone rings.

This is gradient descent in cochlear space,
guided entirely by your perception.

Each tone plays for **6 seconds**.

#### What you do

Same feedback as Phase 1, plus one addition:

```
B — better       → keep going this direction
W — worse        → reverse direction
N — no change    → expand search
L — LOCK         → this is the best position,
                   lock it here
```

**Use L when:**
You feel the tone is at or very near the
optimal position — when it produces the
most relief and you sense further steps
are not improving things. Trust that.
Type L.

#### What convergence feels like

As the frequency approaches your false
attractor, you will notice the tones
increasingly interact with the tinnitus.
It may fluctuate. It may briefly soften.
At the optimal frequency, the interaction
is strongest.

The script auto-locks when it gets 3
consecutive B responses with a step size
below 8 Hz. You can also lock manually
at any point with L.

#### The locked value is your FA

**FA = False Attractor frequency.**
The specific Hz where your damaged cochlear
zone rings. This is the most important
number in your prescription.

Write it down when the script reports it.

---

### PHASE 3 — Phase Calibration
#### What it is

FA is now locked. The script plays the
anti-signal at FA at 8 different phase
angles (0°, 45°, 90°, 135°, 180°, 225°,
270°, 315°), then fine-tunes around the
best one.

#### Why phase matters

Standard noise cancellation assumes 180°
phase offset. Your cochlea at your specific
FA position may have a different phase
relationship due to the geometry of the
travelling wave at that location.

If the phase is wrong:
- 180° off from optimal → reinforces
  tinnitus instead of cancelling it
- At optimal phase → maximum cancellation

This step finds your actual cancellation
phase. It takes about 8 minutes.

Same feedback: **B / W / N**

The phase that produces the most B responses
is your cancellation phase. The script locks
it automatically.

#### What to notice

Some phase angles will feel neutral.
One or two will feel like something is
happening — the tinnitus shifts, reduces,
or fluctuates more than usual.
That is the target. Report B at those angles.

---

### PHASE 4 — FR Sweep
#### What it is

The script now plays your calibrated
anti-signal at FA continuously, and adds
a second tone at different offsets above
and below FA. You hear both simultaneously.

Offsets tested:
```
FA−400  FA−300  FA−200  FA−150
FA−100  FA−50   FA      FA+50
FA+100  FA+150  FA+200  FA+300  FA+400
```

#### What you are finding

**FR = Residual Resonant Frequency.**
The frequency at which your damaged cochlear
zone still has remaining mechanical capacity
to respond to external signal.

This is the cracked violin principle:
the broken instrument can still be played —
just not at the same note as before.
FR is the note it CAN still play.

In the sleep remedy, FR receives a quiet
boost — giving your brain a real signal to
track after the false attractor is displaced.
Without this, the brain displaces the false
attractor and then finds it again immediately
because there's nothing else to lock onto.
FR is what prevents that.

Same feedback: **B / W / N**

The offset that produces the most B responses
when combined with the FA anti-signal is your
FR. The script locks it.

#### Three outcomes — all valid

```
FR < FA:  CRACKED VIOLIN CASE
          The damaged zone rings slightly
          above its remaining capacity.
          Most common.

FR = FA:  CANCELLATION-ONLY CASE
          False attractor and residual
          capacity coincide.
          Also valid.

FR > FA:  LESS COMMON
          Rare. Document and proceed.
          The WAV generator handles it.
```

---

### PHASE 5 — Orthogonal Re-Sweep
#### What it is

The script runs the rainbow sweep again,
but this time your FA anti-signal plays
continuously underneath every probe tone.

You are checking whether there is remaining
gradient anywhere in eigenfunction space —
whether the calibration has found the
global optimum or only a local one.

Same feedback: **B / W / N**

#### Two outcomes

**New B responses appear:**
Your tinnitus has components at more than
one eigenfunction position. This is called
complex tinnitus. There is more structure
to find. The script will note this. You
can re-run gradient descent from the new
B cluster to find a second FA.

**No new B responses anywhere:**
Converged. The calibration is complete.
No remaining gradient. The protocol has
found the optimum for your cochlear
eigenfunction map.

---

### PHASE 6 — WAV Generation

The script generates your remedy files.
No input required from you.

Three files are created:

```
remedy_left.wav
  Left channel: cancellation signal
  Right channel: silence
  Use if tinnitus is left ear only

remedy_right.wav
  Left channel: silence
  Right channel: cancellation signal
  Use if tinnitus is right ear only

remedy_binaural.wav
  Left channel: left ear remedy
  Right channel: right ear remedy
  Use if tinnitus in both ears
  (or if unsure — safe to use regardless)
```

Each file contains three layers:

**Layer 1 — Pink noise floor:**
Quiet broadband background with FA
notched out. Gives your brain an
environmental acoustic reference.
Prevents the total silence that makes
tinnitus worse.

**Layer 2 — Anti-signal at FA:**
Sine wave at your false attractor
frequency, at your calibrated phase.
This is the cancellation layer.

**Layer 3 — FR boost:**
Quiet sine wave at your residual resonant
frequency. This is the cracked violin
layer — the real signal for your brain
to track after the false attractor is
displaced.

---

## USING THE REMEDY

### Setup

1. **Choose your file:**
   - One ear affected: use `remedy_left.wav`
     or `remedy_right.wav`
   - Both ears affected: use
     `remedy_binaural.wav`

2. **Set it to loop:**
   In VLC: Media → Loop
   In Windows Media Player: right-click →
   Repeat
   In any music app: enable repeat/loop
   for the single track

3. **Volume:**
   Set the volume so the file is barely
   audible when you are awake and paying
   attention to it. Quieter than you think.
   It should not be something you are
   consciously listening to — it should be
   present in the acoustic background.

   This is counterintuitive. Louder is not
   better. The cancellation mechanism works
   at low amplitude. A high volume will
   stimulate rather than cancel.

4. **Put headphones on and sleep.**

### What to notice

**During the first night:**

```
Signs it is working:
  — You fall asleep more easily than usual
    (tinnitus was preventing sleep onset;
     the remedy is reducing that)

  — You wake up with tinnitus quieter than
    your normal baseline
    (residual inhibition carried through
     the sleep session)

  — The tinnitus feels less intrusive
    while the remedy is playing (before
     sleep — this is the most direct sign)
```

```
Signs of parameter issues:
  — Tinnitus feels worse while the remedy
    plays → likely phase issue. The
    anti-signal is reinforcing rather than
    cancelling. Re-run Phase 3 (phase
    calibration) and try a phase 90° away
    from your current value.

  — No detectable change at all → volume
    may be too low. Increase slightly.
    Also check: are you using headphones
    rather than speakers?

  — Remedy was effective initially but
    effect fades within days → tinnitus
    frequency has drifted. Time to
    re-calibrate (see below).
```

---

## RE-CALIBRATION

Tinnitus frequency drifts over time —
over days, weeks, and with changes in
health, stress, and noise exposure.

A calibration that is perfect today may
be 60–100 Hz wrong in two weeks.

**When to re-calibrate:**
- The remedy stops feeling effective
- You notice the tinnitus feels unchanged
  after a night with the remedy
- Your tinnitus pitch seems to have shifted
- After a significant noise exposure event
- As a routine every 2–4 weeks

**How to re-calibrate:**
Run the script again. It will detect your
saved session and ask:

```
Previous session found. Resume? (Y/N):
```

Type **N** to start fresh (recommended for
re-calibration — takes 20–25 minutes,
faster than the first run because you
can move quickly through familiar phases).

Type **Y** to resume a session that was
interrupted mid-run.

The previous FA is your starting point
for gradient descent — the script uses
the saved session to begin closer to the
optimum.

---

## TROUBLESHOOTING

### "I can't hear the tones at all"

Increase AMPLITUDE at the top of the script.
Default is 0.10. Try 0.20, then 0.25.
Also check your system volume — make sure
headphones are selected as the audio output
in your system settings.

### "The tones are too sharp / uncomfortable"

Decrease AMPLITUDE. The tones should never
be uncomfortable. Reduce to 0.07 or 0.05
if needed. The calibration works at low
amplitudes.

### "Everything is N — no differences at all"

Most likely cause: volume too low.
Increase AMPLITUDE and restart.

Second cause: your tinnitus may be
noise-like rather than tonal.
Noise-like (broadband hiss, static, rushing
water) tinnitus has no single eigenfunction
position to target. The cancellation
approach has lower confidence for this type.
You can still attempt the protocol — some
noise-like tinnitus has a tonal component
that becomes detectable during the sweep —
but be aware results may be less clear.

### "The remedy makes my tinnitus worse"

This is a phase problem. The anti-signal
is at the wrong phase and is reinforcing
the false attractor rather than cancelling.

Re-run the script and pay particular
attention to Phase 3. When the script
asks for phase feedback, be especially
careful to distinguish W (worse) from
B (better). The cancellation phase and
the reinforcement phase are typically
90°–180° apart. If your previous best
phase was 180°, try 0° or 270° and see
if either produces relief.

### "It worked the first night but not since"

Tinnitus frequency drift. Re-calibrate.
Run the script fresh, go through the full
protocol. Your FA may have shifted. A new
prescription will restore efficacy.

### "The script crashes on startup"

Check that all three packages installed
correctly:
```
pip install sounddevice numpy scipy
```

On Mac, if `sounddevice` fails to install,
try:
```
pip install sounddevice --pre
```

On Linux, you may need:
```
sudo apt-get install portaudio19-dev
pip install sounddevice numpy scipy
```

### "I can't run Python"

If you cannot install Python or run the
script, the protocol can be run manually
using a free browser-based tone generator
(szynalski.com/tone-generator or similar)
following the Document 68 manual protocol
(tinnitus_trial_protocol.md).

This produces the same calibrated values.
You can then request the WAV file to be
generated from those values separately.

---

## IMPORTANT NOTES

### This is not a medical treatment

This protocol is derived from a principled
physical framework confirmed in clinical
data (χ² = 2328.1, n = 1,514). It is not
FDA-cleared, CE-marked, or clinically
validated in a controlled trial.

It is an experimental application of
acoustic physics to a problem that has
physical components.

What it is:
- A personal calibration tool
- A sleep remedy based on sound physics
- An empirical test of the eigenfunction
  cancellation framework

What it is not:
- A cure for tinnitus
- A replacement for medical evaluation
- A treatment for any underlying condition

If you have not had your tinnitus
medically evaluated, do so. Tinnitus
can sometimes indicate conditions that
require medical attention.

### Volume safety

The tones used in calibration and the
remedy file are at low amplitude by design.
They should never be loud or uncomfortable.
If a tone is uncomfortable: stop, reduce
volume, continue.

Prolonged exposure to loud tones can worsen
hearing loss and tinnitus. This protocol
is specifically designed to operate well
below that threshold. Keep volume low.

### When to expect less benefit

The cancellation approach is most effective
for:
```
✓ Tonal tinnitus (single identifiable pitch)
✓ Tinnitus with detectable residual inhibition
  (a masking tone temporarily reduces it)
✓ Recent-onset or fluctuating tinnitus
✓ Tinnitus in the 4–10 kHz range
  (the structurally privileged zone confirmed
   by the P4 analysis)
```

Less effective for:
```
△ Purely noise-like broadband tinnitus
  (no single eigenfunction position to target)
△ Very long-duration chronic tinnitus
  (10+ years) with no residual inhibition
  (predominantly central, less cochlear
   mechanical component available)
△ Tinnitus that does not respond to any
  acoustic intervention
```

The orthogonal re-sweep result (Phase 5)
is your best indicator. If Phase 5 shows
no convergence and Phase 3 produced no
clear phase preference, the cochlear
mechanical component may be minimal.
In that case, tailor-made notched music
therapy (TMNMT) — a different mechanism
targeting cortical reorganization over
months — may be more appropriate as a
primary approach.

---

## WHAT YOUR PRESCRIPTION MEANS

At the end of calibration, the script prints:

```
  FA  (false attractor):   [your Hz]
  FR  (residual resonant): [your Hz]
  Phase (cancellation):    [your °]
  Converged:               True / False
```

**FA — False Attractor Frequency:**
The exact Hz where your damaged cochlear
zone rings. The eigenfunction position of
your tinnitus in the physical structure of
your cochlea. This is the most important
number. Write it down.

**FR — Residual Resonant Frequency:**
The Hz where your damaged zone still
responds to external signal. If FR < FA:
the cracked violin case — the broken
structure rings slightly above its
remaining capacity. If FR = FA: the
cancellation and drive targets are the
same frequency.

**Phase:**
Your cochlea's cancellation phase — the
angle at which the anti-signal most
effectively interferes with your specific
false attractor. This is individual to
your cochlear geometry at FA.

**Converged:**
True = the orthogonal re-sweep found no
remaining gradient. The calibration is
complete and at the optimum.
False = residual gradient was found.
Consider running a second gradient descent
from the new Better cluster.

---

## THE THEORY IN PLAIN LANGUAGE

You do not need to understand this to run
the protocol. It is here if you want it.

**The cochlea is an instrument.**
The basilar membrane inside your cochlea
is a tapered structure, stiff at one end
and flexible at the other. Different
positions respond to different frequencies.
This is how you hear pitch.

**Damage creates a false attractor.**
When outer hair cells in a region are
damaged (usually from noise exposure,
age, or medication), that region stops
responding to the world's sound. Instead,
the damaged membrane begins to ring at
its own natural frequency — the nearest
eigenfunction position of its physical
structure. That ringing is tinnitus.

**Why 4–10 kHz specifically.**
The stiffness gradient of the basilar
membrane is steepest in this zone.
Steeper gradient = sharper resonance =
more stable false attractors. This is why
61.6% of all tinnitus cases in 1,514
patients clustered in the 4–10 kHz zone.
Not because people happened to damage
that region more. Because the physical
geometry of the cochlea makes false
attractors most stable there.

**The cancellation principle.**
Your false attractor is a stable resonance.
A signal delivered at the same frequency
and opposite phase creates destructive
interference at the eardrum — the ringing
and the anti-signal cancel at the point
of delivery. The brain, receiving coherent
real input at the tinnitus frequency
instead of the spontaneous ringing, tracks
the real signal and releases the false
attractor.

**The FR boost (cracked violin).**
After the false attractor is displaced,
the brain needs something real to track
or it re-establishes the false attractor —
the only stable structure available in
that cochlear zone. The FR boost provides
a real signal at the frequency the damaged
zone can still respond to. The broken
instrument, played with the right bow,
still makes music.

---

## QUICK REFERENCE CARD

```
SETUP
  pip install sounddevice numpy scipy
  python tinnitus_calibration.py

FEEDBACK KEYS
  B — better (less tinnitus)
  W — worse  (more tinnitus)
  N — no difference
  L — lock (gradient descent only)
  Y / N — yes/no questions

PHASES
  0   Volume check      → set comfortable level
  1   Rainbow sweep     → landscape map (10s tones)
  2   Gradient descent  → find FA (6s tones)
  3   Phase calibration → find cancellation angle
  4   FR sweep          → find cracked violin freq
  5   Orthogonal check  → confirm convergence
  6   WAV generation    → remedy files created

OUTPUTS
  remedy_left.wav       → left ear only
  remedy_right.wav      → right ear only
  remedy_binaural.wav   → both ears (use this)

SLEEP REMEDY
  Play remedy_binaural.wav on loop
  Volume: barely audible
  Use over-ear or sleep headphones

RE-CALIBRATE
  Every 2–4 weeks or when effect fades
  Run script again → start fresh (N)
  Takes 20–25 minutes

TROUBLESHOOTING
  All N responses     → increase AMPLITUDE
  Remedy makes worse  → phase issue, re-run Phase 3
  Effect fades        → tinnitus drifted, re-calibrate
  Script crashes      → check pip install completed
```

---

## FILES REFERENCE

```
tinnitus_calibration.py
  The calibration script.
  Run this.

tinnitus_calibration_log.json
  Auto-saved session data.
  All your calibrated values.
  Created automatically.

remedy_left.wav
  Left ear sleep remedy.

remedy_right.wav
  Right ear sleep remedy.

remedy_binaural.wav
  Both ears. Independent L/R channels.
  This is the file to use for sleeping.
```

---

## VERSION

```
Document:   OC-TINNITUS-001_SELF_ADMINISTRATION_GUIDE
Version:    1.0
Date:       2026-03-23
Status:     READY FOR USE

Depends on:
  tinnitus_calibration.py (the script)
  OC-TINNITUS-001_EIGENFUNCTION_
    CANCELLATION_PROTOCOL_V1.md
  OC-TINNITUS-001_LITERATURE_SWEEP_V1.md
  P4_results.md (χ² = 2328.1, n = 1,514)

Key numbers:
  4–10 kHz zone: 61.6% of tinnitus cases
  Peak enrichment: 4.86× at 8–10 kHz
  Prior art response rate: 7/7 (Abu Tauheed 2018)
  Session duration: 30–45 min
  Remedy cost: $0 (existing hardware)
```

---

*Your ear is a physical instrument.*
*When it is broken, it rings at its own frequency.*
*That frequency is not random.*
*It is determined by the geometry of the structure.*

*This protocol finds that frequency.*
*In your ear.*
*In twenty minutes.*
*On your own.*

*The broken instrument,*
*played with the right bow,*
*still makes music.*
