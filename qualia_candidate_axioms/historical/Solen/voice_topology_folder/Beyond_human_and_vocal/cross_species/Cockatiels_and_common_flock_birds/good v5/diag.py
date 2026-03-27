import numpy as np
import librosa
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# COCKATIEL CORPUS DIAGNOSTIC
# OC-OBS-005 — OrganismCore — Eric Robert Lawson
# No filters. No gates. No rejection.
# Just measure everything and report what is there.
# ─────────────────────────────────────────────────────────────

CORPUS_DIR   = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "audio_files")
SR           = 44100
HOP_LENGTH   = 32
FRAME_LENGTH = 1024
TOP_DB       = 20
F0_MIN       = 200
F0_MAX       = 4000   # wide open — no assumptions


def diagnose_file(fpath, fname):
    try:
        y, sr = librosa.load(fpath, sr=SR, mono=True)
    except Exception as e:
        print(f"  LOAD ERROR: {e}")
        return

    dur_total = len(y) / sr
    print(f"\n  File: {fname}")
    print(f"  Total duration: {dur_total:.2f}s  "
          f"Sample rate: {sr}Hz")

    # Energy-based segmentation
    intervals = librosa.effects.split(
        y, top_db=TOP_DB,
        frame_length=1024, hop_length=HOP_LENGTH)

    print(f"  Segments found (top_db={TOP_DB}): "
          f"{len(intervals)}")

    for idx, (start, end) in enumerate(intervals[:5]):
        segment = y[start:end]
        dur_ms  = len(segment) / sr * 1000

        print(f"\n    Segment {idx+1}: {dur_ms:.1f}ms")

        # F0 — wide open range, no rejection
        try:
            f0, voiced, _ = librosa.pyin(
                segment,
                fmin=F0_MIN,
                fmax=F0_MAX,
                sr=sr,
                hop_length=HOP_LENGTH,
                frame_length=FRAME_LENGTH)

            if f0 is not None and len(f0) > 0:
                voiced_frac = np.sum(voiced) / len(voiced)
                f0_voiced   = f0[voiced] if np.any(voiced) \
                              else np.array([])

                print(f"      F0 frames total:  {len(f0)}")
                print(f"      Voiced frames:    {np.sum(voiced)}"
                      f"  ({voiced_frac:.2f})")

                if len(f0_voiced) > 0:
                    f0_range = np.max(f0_voiced) - \
                               np.min(f0_voiced)
                    print(f"      F0 min:  {np.min(f0_voiced):.1f}Hz")
                    print(f"      F0 max:  {np.max(f0_voiced):.1f}Hz")
                    print(f"      F0 mean: {np.mean(f0_voiced):.1f}Hz")
                    print(f"      F0 range:{f0_range:.1f}Hz")

                    # ASCII F0 trajectory
                    n_pts = min(20, len(f0_voiced))
                    idx_s = np.linspace(
                        0, len(f0_voiced)-1, n_pts
                    ).astype(int)
                    f0_sub = f0_voiced[idx_s]
                    f0_lo  = np.min(f0_voiced)
                    f0_hi  = np.max(f0_voiced)
                    rng    = f0_hi - f0_lo
                    print(f"      F0 trajectory "
                          f"({f0_lo:.0f}–{f0_hi:.0f}Hz):")
                    for j, v in enumerate(f0_sub):
                        pct = j / (n_pts-1) * 100
                        bar = int((v - f0_lo) /
                                  (rng + 1e-10) * 25)
                        print(f"        t={pct:4.0f}%  "
                              f"{'·'*bar}█"
                              f"  {v:.1f}Hz")
                else:
                    print(f"      No voiced frames detected.")
            else:
                print(f"      pyin returned None.")

        except Exception as e:
            print(f"      F0 ERROR: {e}")

        # RMS
        rms = librosa.feature.rms(
            y=segment,
            frame_length=FRAME_LENGTH,
            hop_length=HOP_LENGTH)[0]
        print(f"      RMS max: {np.max(rms):.5f}  "
              f"mean: {np.mean(rms):.5f}")

    if len(intervals) > 5:
        print(f"\n    ... ({len(intervals)-5} more segments"
              f" not shown)")


def main():
    print("=" * 65)
    print("OC-OBS-005 — CORPUS DIAGNOSTIC")
    print("OrganismCore — Eric Robert Lawson")
    print("No filters. Reporting raw measurements only.")
    print("=" * 65)

    audio_ext = ('.mp3', '.wav', '.flac', '.ogg')
    all_files = sorted([
        f for f in os.listdir(CORPUS_DIR)
        if f.lower().endswith(audio_ext)
    ])

    print(f"\nCorpus: {CORPUS_DIR}")
    print(f"Files:  {len(all_files)}")

    # ── SUMMARY PASS — all segments, all files ────────────
    print(f"\n{'='*65}")
    print("PASS 1 — SEGMENT DURATION DISTRIBUTION")
    print("(across all files, top_db=20)")
    print(f"{'='*65}")

    all_durations   = []
    all_f0_ranges   = []
    all_voiced_frac = []

    for fname in all_files:
        fpath = os.path.join(CORPUS_DIR, fname)
        try:
            y, sr = librosa.load(fpath, sr=SR, mono=True)
        except Exception:
            continue

        intervals = librosa.effects.split(
            y, top_db=TOP_DB,
            frame_length=1024, hop_length=HOP_LENGTH)

        for start, end in intervals:
            segment = y[start:end]
            dur_ms  = len(segment) / sr * 1000
            all_durations.append(dur_ms)

            # Quick F0 check on segments 80-500ms
            if 80 < dur_ms < 500:
                try:
                    f0, voiced, _ = librosa.pyin(
                        segment,
                        fmin=F0_MIN, fmax=F0_MAX,
                        sr=sr,
                        hop_length=HOP_LENGTH,
                        frame_length=FRAME_LENGTH)
                    if f0 is not None and np.any(voiced):
                        vf = np.sum(voiced) / len(voiced)
                        f0v = f0[voiced]
                        all_voiced_frac.append(vf)
                        all_f0_ranges.append(
                            np.max(f0v) - np.min(f0v))
                except Exception:
                    pass

    all_durations = np.array(all_durations)
    print(f"\nAll segment durations (ms):")
    print(f"  Count:       {len(all_durations)}")
    print(f"  Min:         {np.min(all_durations):.1f}")
    print(f"  p5:          {np.percentile(all_durations,5):.1f}")
    print(f"  p25:         {np.percentile(all_durations,25):.1f}")
    print(f"  Median:      {np.median(all_durations):.1f}")
    print(f"  p75:         {np.percentile(all_durations,75):.1f}")
    print(f"  p95:         {np.percentile(all_durations,95):.1f}")
    print(f"  Max:         {np.max(all_durations):.1f}")

    bins = [0,50,100,150,200,250,300,400,500,750,1000,5000]
    print(f"\n  Duration histogram:")
    for i in range(len(bins)-1):
        lo, hi = bins[i], bins[i+1]
        n = np.sum((all_durations >= lo) &
                   (all_durations < hi))
        bar = '█' * min(n, 40)
        print(f"    {lo:>5}–{hi:<5}ms  {n:>4}  {bar}")

    if len(all_voiced_frac) > 0:
        vf = np.array(all_voiced_frac)
        fr = np.array(all_f0_ranges)
        print(f"\nVoiced fraction (segments 80-500ms):")
        print(f"  Count:   {len(vf)}")
        print(f"  Median:  {np.median(vf):.3f}")
        print(f"  Mean:    {np.mean(vf):.3f}")
        print(f"  > 0.4:   {np.sum(vf > 0.4)}")
        print(f"  > 0.6:   {np.sum(vf > 0.6)}")
        print(f"\nF0 range (Hz) in those segments:")
        print(f"  Median:  {np.median(fr):.1f}")
        print(f"  Mean:    {np.mean(fr):.1f}")
        print(f"  > 30Hz:  {np.sum(fr > 30)}")
        print(f"  > 50Hz:  {np.sum(fr > 50)}")
        print(f"  > 100Hz: {np.sum(fr > 100)}")

    # ── DETAIL PASS — first 3 files only ─────────────────
    print(f"\n{'='*65}")
    print("PASS 2 — DETAILED VIEW (first 3 files)")
    print(f"{'='*65}")

    for fname in all_files[:3]:
        fpath = os.path.join(CORPUS_DIR, fname)
        diagnose_file(fpath, fname)

    print(f"\n{'='*65}")
    print("Diagnostic complete.")
    print("Paste full output to determine correct")
    print("geometry extraction parameters.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
