"""Build the Scala-archive submission files for guitar-tuning batch 1.

Single source of truth for the seven idealized tunings (the same values the
MicroKeys .mkscale files use). For each tuning this writes a .scl file:

- the scale proper is the octave-reduced set of open-string pitches with the
  lowest string as 1/1 and 2/1 as the period (the archive's dominant convention);
  strings in the same pitch class but an imperfect octave apart stay as separate
  degrees;
- comment lines record the full open-string voicing (un-reduced cents above the
  lowest string, Hz, exact ratio where pure) so nothing is lost by reduction.

Tunings marked "hold" (string set not yet confirmed by the player) are written to
a separate folder so they are not attached by mistake.

Every string frequency is cross-checked against the matching .mkscale file, and
output filenames are checked against the local archive copy.

Usage:  python make_scala_batch1.py [--name "Full Name"] [--prefix surname_]
"""

import argparse
import json
import math
import os
import re
from fractions import Fraction

SCALES_DIR = os.environ.get(
    "MICROKEYS_SCALES_DIR",
    os.path.join(os.path.expanduser("~"), "OneDrive", "Documents", "MicroKeys Scales"))
OUT_DIR = os.path.join(SCALES_DIR, "Scala Submission - Batch 1")
HOLD_DIR = os.path.join(OUT_DIR, "On hold - confirm strings")
BATCH_DIRS = {1: OUT_DIR, 2: os.path.join(SCALES_DIR, "Scala Submission - Batch 2")}
YEAR = "2026"
SIGNATURE = "! Open-string guitar tuning, lowest string = 1/1"

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

PYTH_DIM8 = Fraction(2**20, 3**12)  # octave minus a Pythagorean comma

# Each string: (midi key in MicroKeys, Hz, exact ratio to the lowest string or None, note)
# Ordered low to high. Hz values are exactly those used to build the .mkscale files.
TUNINGS = [
    {
        "num": 1,
        "mkscale": "Guitar-CGCGCD-Just.mkscale",
        "desc": "By-ear CGCGCD (open Csus2) guitar tuning idealized to 3-limit JI",
        "strings": [
            (36, 63.55, Fraction(1), ""),
            (43, 63.55 * 3 / 2, Fraction(3, 2), ""),
            (48, 63.55 * 2, Fraction(2), ""),
            (55, 63.55 * 3, Fraction(3), ""),
            (60, 63.55 * 4, Fraction(4), ""),
            (62, 63.55 * 9 / 2, Fraction(9, 2), ""),
        ],
        "notes": [
            "The open strings are harmonics 2:3:4:6:8:9 of the pitch an octave below the 1/1.",
            "Idealized from a recording; the other measured strings were within 4.1 cents of these",
            "values. String 3 was uncertain: its fundamental read +5 cents, its overtones about +13.",
        ],
    },
    {
        "num": 2,
        "mkscale": "Guitar-PythComma-Just.mkscale",
        "desc": "By-ear guitar tuning idealized to 3-limit JI: 1/1 4/3 27/16, and 2/1 3/1 4/1 "
                "less a Pythagorean comma",
        "strings": [
            (42, 89.89, Fraction(1), ""),
            (47, 89.89 * 4 / 3, Fraction(4, 3), ""),
            (51, 89.89 * 27 / 16, Fraction(27, 16), ""),
            (53, 89.89 * float(PYTH_DIM8), PYTH_DIM8, ""),
            (60, 89.89 * float(PYTH_DIM8 * Fraction(3, 2)), PYTH_DIM8 * Fraction(3, 2), ""),
            (65, 89.89 * float(PYTH_DIM8 * 2), PYTH_DIM8 * 2, ""),
        ],
        "notes": [
            "Lower strings 1/1 4/3 27/16 lie at 0, -1 and +3 pure fifths from the lowest string;",
            "upper strings are 2/1 3/1 4/1 each lowered by a Pythagorean comma (-12, -11, -12 fifths).",
            "Idealized from a recording: the measured lower strings were within 2.8 cents of these",
            "values; the upper strings measured 24.0, 13.0 and 17.7 cents below 2/1, 3/1 and 4/1,",
            "i.e. -0.6, +10.4 and +5.7 cents from the comma-lowered values used here.",
        ],
    },
    {
        "num": 3,
        "mkscale": "Guitar-ByEar3.mkscale",
        "desc": "By-ear guitar tuning with one pure 5/4 (5/2 between strings 6 and 3)",
        "strings": [
            (38, 75.50, Fraction(1), ""),
            (45, 112.40, None, ""),
            (51, 155.41, None, ""),
            (54, 75.50 * 5 / 2, Fraction(5, 2), ""),
            (60, 266.05, None, ""),
            (62, 296.74, None, ""),
        ],
        "notes": [
            "Measured from a recording; only the 5/2 was idealized (measured -2.3 cents from pure",
            "on its beating fundamental, about +3 cents on its overtones).",
            "Strings 6 and 1 are 30.4 cents short of a double octave.",
        ],
    },
    {
        "num": 4,
        "mkscale": "Guitar-ByEar4.mkscale",
        "desc": "By-ear guitar tuning: 1/1 4/3 5/3 plus 4/3 and 5/3 each 10.8 c higher, and 2/1 less 7.5 c",
        "strings": [
            (41, 89.41, Fraction(1), ""),
            (47, 119.96, None, ""),
            (50, 89.41 * 5 / 3, Fraction(5, 3), ""),
            (53, 178.05, None, ""),
            (58, 89.41 * 8 / 3, Fraction(8, 3), ""),
            (62, 119.96 * 5 / 2, None, "pure 5/2 above string 5"),
        ],
        "labels": {47: "A#2"},
        "notes": [
            "Measured from a recording; 5/3, 8/3 and the 5/2 were idealized (measured +1.2, +3.1",
            "and -3.3 cents from pure). As a result string 5 to string 2 is an octave 10.8 cents",
            "narrow and string 4 to string 1 one 10.8 cents wide (measured -7.7 and +6.3 cents).",
        ],
    },
    {
        "num": 5,
        "rebuild_mkscale": True,
        "mkscale": "Guitar-ByEar5.mkscale",
        "desc": "By-ear guitar tuning: 3/2, plus 3/2 raised 9.8 c, 4/3 raised 5.0 c, and 2/1 less 2.3 c and 5.3 c",
        "strings": [
            (41, 89.47, Fraction(1), ""),
            (46, 119.64, None, ""),
            (48, 89.47 * 3 / 2, Fraction(3, 2), ""),
            (53, 178.70, None, ""),
            (61, 269.94, None, "masked"),
            (65, 356.78, None, ""),
        ],
        "notes": [
            "Measured from a recording; only the 3/2 was idealized (measured +1.1 cents from pure).",
            "String 2 hides among the lower strings' harmonics and was found by comparing the",
            "spectrum before and after each pluck. It is about an octave above string 4; its",
            "fundamental reads about 5 cents above its overtones, so its pitch is less certain.",
            "The 1197.68-cent degree is 2.3 cents narrow of 2/1, close to the measurement uncertainty.",
        ],
    },
    {
        "num": 6,
        "rebuild_mkscale": True,
        "mkscale": "Guitar-ByEar6.mkscale",
        "desc": "By-ear guitar tuning: major third 396.8 c, fifths 696.6 c and 710.3 c, "
                "octave 4.9 c and double octave 14.6 c wide",
        "strings": [
            (41, 89.37, Fraction(1), "ringing, not plucked"),
            (45, 112.39, None, ""),
            (48, 133.64, None, ""),
            (53, 179.25, None, "brief initial mode 178.5 Hz"),
            (61, 269.41, None, "masked"),
            (66, 360.50, None, ""),
        ],
        "notes": [
            "Measured from a recording; nothing was idealized. String 3's settled pitch is used;",
            "its 178.5 Hz initial mode dies within about a second.",
            "String 2 hides among the lower strings' harmonics and was found by comparing the",
            "spectrum before and after each pluck. It is about an octave above string 4; its",
            "fundamental reads about 9 cents above its overtones, so its pitch is less certain.",
        ],
    },
    {
        "num": 7,
        "rebuild_mkscale": True,
        "mkscale": "Guitar-ByEar7.mkscale",
        "desc": "By-ear guitar tuning: fifths 711.6 c and 720.3 c, octave 18.4 c and double octave "
                "25.3 c wide, 3/2 and 8/3 above string 4",
        "strings": [
            (37, 68.00, Fraction(1), "slack; held within about 3 cents"),
            (44, 102.57, None, ""),
            (49, 137.45, None, ""),
            (56, 137.45 * 3 / 2, None, "masked; pure 3/2 above string 4"),
            (61, 276.00, None, "masked; beside string 4's 2nd harmonic"),
            (66, 137.45 * 8 / 3, None, "pure 8/3 above string 4"),
        ],
        "notes": [
            "Measured from a recording; the 3/2 and 8/3 above string 4 were idealized (measured",
            "+1.0 and +1.3 cents from pure). String 3 to 2 is 6.9 cents wide of 4/3 (kept).",
            "Strings 3 and 2 hide among the other strings' harmonics and were found by comparing",
            "the spectrum before and after each pluck; string 2 was resolved from string 4's 2nd",
            "harmonic only in long analysis windows.",
        ],
    },
    {
        "num": 8,
        "batch": 2,
        "rebuild_mkscale": True,
        "mkscale": "Guitar-ByEar8.mkscale",
        "desc": "By-ear CGCGCD guitar tuning: pure 3/2, and 2/1 3/1 4/1 9/2 off by -4.7, -8.1, +5.6, +2.6 c",
        "strings": [
            (36, 63.61, Fraction(1), ""),
            (43, 63.61 * 3 / 2, Fraction(3, 2), ""),
            (48, 126.877, None, ""),
            (55, 189.94, None, "three modes, 188.6/189.4/190.35 Hz"),
            (60, 255.27, None, ""),
            (62, 286.67, None, ""),
        ],
        "notes": [
            "Measured from a recording with each string plucked alone; only the 3/2 was idealized",
            "(measured -2.0 cents from pure). Same CGCGCD shape as guitar1, but not idealized to JI.",
            "String 3 rings in three close modes; their settled centre is used (about +/-5 cents).",
            "String 5 is the centre of a close doublet (95.27/95.35 Hz); strings 2 and 1 read about",
            "4 cents above their own overtone series.",
        ],
    },]


def cents(ratio):
    return 1200 * math.log2(ratio)


def std_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def octave_reduce_fraction(fr):
    while fr >= 2:
        fr /= 2
    while fr < 1:
        fr *= 2
    return fr


def load_mkscale(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return {int(n): float(c) for n, c in re.findall(r'note="(\d+)" cents="([-\d.]+)"', text)}


def build_degrees(tuning):
    """Octave-reduced degrees (excluding 1/1) as (cents, text) sorted ascending."""
    root_hz = tuning["strings"][0][1]
    degrees = []
    for _, hz, exact, _ in tuning["strings"][1:]:
        if exact is not None:
            fr = octave_reduce_fraction(exact)
            if fr == 1:
                continue  # a pure octave of the root is the root itself
            c = cents(float(fr))
            text = f"{fr.numerator}/{fr.denominator}"
        else:
            c = cents(hz / root_hz) % 1200.0
            text = f"{c:.5f}"
        if any(abs(c - d[0]) < 1e-6 for d in degrees):
            continue  # exact duplicate pitch class
        degrees.append((c, text))
    degrees.sort()
    degrees.append((1200.0, "2/1"))
    return degrees


def string_lines(tuning):
    root_hz = tuning["strings"][0][1]
    n = len(tuning["strings"])
    full_set = n == 6
    lines = []
    for i, (midi, hz, exact, note) in enumerate(tuning["strings"]):
        # guitar convention (string 1 = highest) only when all six strings are known
        who = f"string {n - i}" if full_set else f"pitch {i + 1}"
        c = cents(hz / root_hz)
        ratio = f"{exact.numerator}/{exact.denominator}" if exact is not None else "-"
        label = tuning.get("labels", {}).get(midi, NOTE_NAMES[midi % 12] + str(midi // 12 - 1))
        extra = f"  ({note})" if note else ""
        lines.append(f"!   {who}: {hz:9.3f} Hz  {c:9.3f} c  {ratio:>16}  ~{label}{extra}")
    return lines


def description(tuning, author):
    d = tuning["desc"]
    if author:
        first = d.split()[0]
        if not first.isupper():  # keep acronyms such as CGCGCD
            d = d[0].lower() + d[1:]
        d = f"{author}, {d}"
    return f"{d}, 1/1={tuning['strings'][0][1]:.2f} Hz"


def write_scl(tuning, prefix, author):
    fname = f"{prefix}guitar{tuning['num']}.scl"
    desc = description(tuning, author)
    degrees = build_degrees(tuning)
    root_hz = tuning["strings"][0][1]
    n = len(tuning["strings"])

    out = [f"! {fname}", "!", desc, f" {len(degrees)}", "!"]
    out += [f" {text}" for _, text in degrees]
    out += [
        "!",
        f"{SIGNATURE} = {root_hz:.3f} Hz.",
        "! The scale above is the octave-reduced set of the open strings listed below.",
        "! ~names are approximate 12-TET (A=440) note names.",
        "! Open strings, low to high (cents above the lowest string, not reduced):"
        if n == 6 else "! Recorded open strings, low to high (cents above the lowest, not reduced):",
    ]
    out += string_lines(tuning)
    out += [f"! {note}" for note in tuning["notes"]]
    out += [f"! Tuned by ear and recorded in {YEAR}."]

    folder = HOLD_DIR if tuning.get("hold") else BATCH_DIRS[tuning.get("batch", 1)]
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, fname), "w", encoding="ascii", newline="\r\n") as f:
        f.write("\n".join(out) + "\n")
    return folder, fname, desc, degrees


def mkscale_table(strings):
    """Cents offset for all 128 keys: each key follows the nearest string of its pitch
    class; pitch classes with no string sit at the lowest string's offset."""
    offsets = {midi: cents(hz / std_hz(midi)) for midi, hz, _, _ in strings}
    keys = [midi for midi, _, _, _ in strings]
    table = {}
    for n in range(128):
        same = [m for m in keys if m % 12 == n % 12]
        table[n] = offsets[min(same, key=lambda m: abs(m - n))] if same else offsets[keys[0]]
    return table


def write_mkscale(tuning):
    """Rebuild a tuning's .mkscale from its strings, backing up the original once."""
    path = os.path.join(SCALES_DIR, tuning["mkscale"])
    table = mkscale_table(tuning["strings"])
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<MicroKeysScale>"]
    lines += [f'  <Key note="{n}" cents="{table[n]:.4f}"/>' for n in range(128)]
    lines.append("</MicroKeysScale>")
    new_text = "\n".join(lines) + "\n"

    old_text = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old_text == new_text:
        return "unchanged"
    if old_text is not None:
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mkscale_backup")
        os.makedirs(backup_dir, exist_ok=True)
        backup = os.path.join(backup_dir, tuning["mkscale"].replace(".mkscale", ".original.mkscale"))
        if not os.path.exists(backup):
            with open(backup, "w", encoding="utf-8") as f:
                f.write(old_text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)
    return "rebuilt"


def cross_check(tuning):
    """Every string's Hz must match the .mkscale key it came from."""
    table = load_mkscale(os.path.join(SCALES_DIR, tuning["mkscale"]))
    worst = 0.0
    for midi, hz, _, _ in tuning["strings"]:
        mk_hz = std_hz(midi) * 2 ** (table[midi] / 1200)
        err = abs(cents(mk_hz / hz))
        worst = max(worst, err)
        assert err < 0.001, f"tuning {tuning['num']} key {midi}: mkscale {mk_hz:.4f} vs {hz:.4f}"
    return worst


def remove_stale(written):
    """Delete generated guitarN.scl files from earlier runs (other prefix or folder)."""
    for folder in (*BATCH_DIRS.values(), HOLD_DIR):
        if not os.path.isdir(folder):
            continue
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            if not re.search(r"guitar\d\.scl$", name) or path in written:
                continue
            with open(path, "r", encoding="ascii", errors="replace") as f:
                ours = SIGNATURE in f.read()
            if ours:
                os.remove(path)
                print(f"removed stale {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="", help="author credit for description lines")
    ap.add_argument("--prefix", default="", help="filename prefix, e.g. surname_")
    args = ap.parse_args()

    manifest, written = [], set()
    for t in TUNINGS:
        if t.get("rebuild_mkscale"):
            print(f"{t['mkscale']}: {write_mkscale(t)}")
        worst = cross_check(t)
        folder, fname, desc, degrees = write_scl(t, args.prefix, args.name)
        written.add(os.path.join(folder, fname))
        collision = os.path.exists(os.path.join(SCALES_DIR, fname))
        manifest.append({
            "num": t["num"], "batch": t.get("batch", 1), "file": fname, "hold": bool(t.get("hold")),
            "mkscale": t["mkscale"],
            "description": desc, "root_hz": t["strings"][0][1],
            "degrees": [{"cents": c, "text": text} for c, text in degrees],
            "strings": [{"midi": m, "hz": hz, "cents_above_root": cents(hz / t["strings"][0][1]),
                         "exact_ratio": f"{e.numerator}/{e.denominator}" if e is not None else None,
                         "note": note} for m, hz, e, note in t["strings"]],
        })
        where = "HOLD " if t.get("hold") else "READY"
        print(f"[{where}] {fname:<18} {len(degrees)} degrees  mkscale worst {worst:.6f} c"
              f"  archive name collision: {'YES' if collision else 'no'}  desc {len(desc)} chars")
        print(f"   {desc}")
    remove_stale(written)

    manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scala_batch1_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    print(f"\nManifest: {manifest_path}")


if __name__ == "__main__":
    main()
