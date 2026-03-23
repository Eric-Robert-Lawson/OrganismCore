"""
NMR_SAMPLERATE.PY
Sample rate determination for Barker 2021 NMR dataset
OC-OBS-004 — Pre-analysis verification
OrganismCore — Eric Robert Lawson
Run date: 2026-03-23

PURPOSE:
    Determine the true sample rate of the .npy audio files
    by cross-referencing sample counts with annotation timestamps.

    The sample rate is required before any spectral analysis.
    It determines the frequency resolution of the STFT and
    whether the 1-4 kHz soft chirp range is correctly resolved.

USAGE:
    python nmr_samplerate.py --data_dir Naked-mole-rat-voices-1.0
"""

import os
import sys
import argparse
import numpy as np
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, required=True)
    return parser.parse_args()


def read_txt(txt_path):
    """Read annotation file. Returns list of (start, end, label)."""
    annotations = []
    with open(txt_path, "r") as f:
        lines = f.readlines()
    for line in lines[1:]:  # skip header
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            try:
                s = float(parts[0])
                e = float(parts[1])
                cl = parts[2].strip()
                annotations.append((s, e, cl))
            except ValueError:
                continue
    return annotations


def infer_sample_rate(npy_path, txt_path):
    """
    Cross-reference .npy sample count with .txt timestamps
    to infer sample rate.

    Method:
        The last annotation end time approximates the recording
        duration. SR = n_samples / duration.

    Also try: if any softchirp annotations exist, extract that
    segment and compute its expected frequency content as a
    sanity check.
    """
    arr = np.load(npy_path, allow_pickle=False)
    n_samples = arr.shape[0]
    annotations = read_txt(txt_path)

    if not annotations:
        return None

    # Maximum end time in annotations
    max_end = max(e for s, e, cl in annotations)
    min_start = min(s for s, e, cl in annotations)

    # Inferred SR from last annotation
    inferred_sr = n_samples / max_end

    # Candidate sample rates to test
    candidates = [44100, 48000, 96000, 192000, 250000, 300000, 384000]

    # For each candidate, compute implied duration and compare to
    # annotation span
    candidate_results = {}
    for sr in candidates:
        implied_duration = n_samples / sr
        error = abs(implied_duration - max_end)
        candidate_results[sr] = {
            "implied_duration_s": round(implied_duration, 3),
            "annotation_max_end_s": round(max_end, 3),
            "error_s": round(error, 3),
            "match": error < 2.0  # within 2 seconds
        }

    # Count softchirps
    softchirps = [(s, e) for s, e, cl in annotations if cl == "softchirp"]
    noise = [(s, e) for s, e, cl in annotations if cl == "noise"]
    weirdo = [(s, e) for s, e, cl in annotations if cl == "weirdo"]
    downsweep = [(s, e) for s, e, cl in annotations if cl == "downsweep"]

    # Duration of first softchirp
    first_chirp_duration = None
    if softchirps:
        s0, e0 = softchirps[0]
        first_chirp_duration = round(e0 - s0, 6)

    return {
        "file": npy_path.name,
        "n_samples": n_samples,
        "inferred_sr_raw": round(inferred_sr, 1),
        "annotation_max_end_s": round(max_end, 3),
        "annotation_min_start_s": round(min_start, 3),
        "n_softchirps": len(softchirps),
        "n_noise": len(noise),
        "n_weirdo": len(weirdo),
        "n_downsweep": len(downsweep),
        "first_chirp_duration_s": first_chirp_duration,
        "candidate_rates": candidate_results
    }


def main():
    args = parse_args()
    data_dir = Path(args.data_dir)

    # Collect all paired npy/txt files
    pairs = []
    for root, dirs, files in os.walk(data_dir):
        for f in sorted(files):
            if f.endswith(".npy"):
                npy_path = Path(root) / f
                txt_path = npy_path.with_suffix(".txt")
                if txt_path.exists():
                    pairs.append((npy_path, txt_path))

    print()
    print("=" * 60)
    print("  NMR SAMPLE RATE DETERMINATION")
    print("  OC-OBS-004 — Barker 2021 Dataset")
    print("=" * 60)
    print(f"\n  Analysing {len(pairs)} paired recordings\n")

    sep = "─" * 60

    # Run on all files
    all_inferred = []
    all_softchirp_counts = []
    all_noise_counts = []

    for npy_path, txt_path in pairs:
        result = infer_sample_rate(npy_path, txt_path)
        if result is None:
            continue

        all_inferred.append(result["inferred_sr_raw"])
        all_softchirp_counts.append(result["n_softchirps"])
        all_noise_counts.append(result["n_noise"])

    # Summary statistics on inferred SR
    print(sep)
    print("INFERRED SAMPLE RATE ACROSS ALL RECORDINGS")
    print(sep)
    arr = np.array(all_inferred)
    print(f"\n  N recordings analysed:  {len(arr)}")
    print(f"  Mean inferred SR:       {np.mean(arr):.1f} Hz")
    print(f"  Median inferred SR:     {np.median(arr):.1f} Hz")
    print(f"  Std:                    {np.std(arr):.1f} Hz")
    print(f"  Min:                    {np.min(arr):.1f} Hz")
    print(f"  Max:                    {np.max(arr):.1f} Hz")

    # Most likely SR
    candidates = [44100, 48000, 96000, 192000, 250000, 300000, 384000]
    median_sr = np.median(arr)
    closest = min(candidates, key=lambda x: abs(x - median_sr))
    print(f"\n  Closest standard rate:  {closest} Hz")
    print(f"  → LIKELY SAMPLE RATE:   {closest} Hz")

    # Soft chirp corpus summary
    print()
    print(sep)
    print("SOFT CHIRP CORPUS SUMMARY")
    print(sep)
    sc = np.array(all_softchirp_counts)
    print(f"\n  Total softchirps:       {np.sum(sc)}")
    print(f"  Mean per recording:     {np.mean(sc):.1f}")
    print(f"  Median per recording:   {np.median(sc):.1f}")
    print(f"  Max in one recording:   {np.max(sc)}")
    print(f"  Min in one recording:   {np.min(sc)}")
    print(f"  Recordings with 0:      {np.sum(sc == 0)}")

    # Per-recording detail for first 10
    print()
    print(sep)
    print("PER-RECORDING DETAIL (first 10)")
    print(sep)
    counter = 0
    for npy_path, txt_path in pairs:
        if counter >= 10:
            break
        result = infer_sample_rate(npy_path, txt_path)
        if result is None:
            continue
        counter += 1
        print(f"\n  {result['file']}")
        print(f"    N samples:          {result['n_samples']}")
        print(f"    Annot max end (s):  {result['annotation_max_end_s']}")
        print(f"    Inferred SR:        {result['inferred_sr_raw']} Hz")
        print(f"    Softchirps:         {result['n_softchirps']}")
        print(f"    Noise events:       {result['n_noise']}")
        print(f"    Weirdo:             {result['n_weirdo']}")
        print(f"    Downsweep:          {result['n_downsweep']}")
        if result["first_chirp_duration_s"]:
            print(f"    First chirp dur:    {result['first_chirp_duration_s']} s")

        print(f"    Candidate rate check:")
        for sr, res in result["candidate_rates"].items():
            match_str = "← MATCH" if res["match"] else ""
            print(f"      {sr:>7} Hz → "
                  f"duration {res['implied_duration_s']:>8.3f}s "
                  f"(error {res['error_s']:.3f}s) {match_str}")

    # Label distribution across full dataset
    print()
    print(sep)
    print("LABEL DISTRIBUTION ACROSS FULL DATASET")
    print(sep)
    label_counts = {}
    for npy_path, txt_path in pairs:
        annotations = []
        try:
            with open(txt_path, "r") as f:
                lines = f.readlines()
            for line in lines[1:]:
                parts = line.strip().split("\t")
                if len(parts) >= 3:
                    label_counts[parts[2].strip()] = \
                        label_counts.get(parts[2].strip(), 0) + 1
        except Exception:
            continue

    print()
    total_annotations = sum(label_counts.values())
    for label, count in sorted(label_counts.items(),
                                key=lambda x: -x[1]):
        pct = 100 * count / total_annotations
        print(f"    {label:<20} {count:>5}  ({pct:.1f}%)")
    print(f"\n    TOTAL ANNOTATIONS:   {total_annotations}")

    # Longitudinal animal check
    print()
    print(sep)
    print("LONGITUDINAL COVERAGE — SAME ANIMAL ACROSS DATES")
    print(sep)
    from collections import defaultdict
    animal_dates = defaultdict(set)
    animal_colonies = defaultdict(set)
    for npy_path, _ in pairs:
        parts = npy_path.stem.split("_")
        colony = parts[0]
        date = parts[1]
        animal_ids = parts[2:-1]
        for aid in animal_ids:
            animal_dates[aid].add(date)
            animal_colonies[aid].add(colony)

    print()
    multi_date = {a: d for a, d in animal_dates.items() if len(d) > 1}
    print(f"  Animals with recordings on multiple dates: {len(multi_date)}")
    print()
    for animal, dates in sorted(multi_date.items(),
                                  key=lambda x: -len(x[1])):
        colony = list(animal_colonies[animal])[0]
        print(f"    Animal {animal} ({colony}): "
              f"{len(dates)} dates — {', '.join(sorted(dates))}")

    print()
    print("=" * 60)
    print("  END OF SAMPLE RATE REPORT")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
