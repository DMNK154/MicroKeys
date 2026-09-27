"""Build the 12-note guitar scale from recordings/12-note-scale.m4a.

The player's design: six open strings at nonstandard pitches, plus notes on the
guitar's ordinary 12-TET frets. So a fretted note's intended pitch is exactly
open * 2^(fret/12); the recording's fretted notes came out 3-14 cents sharp of that
(normal fretting sharpness). Outputs:

- Guitar-12Note.mkscale        as played (settled fundamentals, all 12 notes)
- Guitar-12Note-Ideal.mkscale  open strings as played, fretted notes exact 12-TET
- Scala Submission - Batch 2\\guitar9.scl  the ideal 12 pitches, unreduced: lowest
  note = 1/1, top note as the last degree (archive precedent for fixed-pitch
  instruments, e.g. malawi_bangwe1.scl, marimba1.scl)

Values were cross-checked by independent re-measurement (2026-09-26).
MicroKeys files put each note on its natural key; other keys follow the nearest
note of their pitch class, or the low C's offset (make_scala_batch1.mkscale_table).
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_scala_batch1 import SCALES_DIR, mkscale_table  # noqa: E402

BATCH2_DIR = os.path.join(SCALES_DIR, "Scala Submission - Batch 2")

OPEN = {6: 63.32, 5: 95.19, 4: 126.45, 3: 189.39, 2: 254.50, 1: 285.95}

# (midi key, string, fret, measured Hz), low to high
NOTES = [
    (36, 6, 0, 63.32),
    (38, 6, 2, 71.63),
    (43, 5, 0, 95.19),
    (45, 5, 2, 107.44),
    (48, 4, 0, 126.45),
    (50, 4, 2, 142.78),
    (55, 3, 0, 189.39),
    (57, 3, 2, 212.00),  # weak fundamental; overtones read 213.06
    (60, 2, 0, 254.50),
    (62, 1, 0, 285.95),
    (64, 1, 2, 321.86),
    (65, 1, 3, 340.66),
]
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def ideal_hz(string, fret):
    return OPEN[string] * 2 ** (fret / 12)


def cents(r):
    return 1200 * math.log2(r)


def write_mkscale(path, notes):
    table = mkscale_table([(k, hz, None, "") for k, hz in notes])
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<MicroKeysScale>"]
    lines += [f'  <Key note="{n}" cents="{table[n]:.4f}"/>' for n in range(128)]
    lines.append("</MicroKeysScale>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {path}")


def write_scl(path):
    root = ideal_hz(6, 0)
    fname = os.path.basename(path)
    desc = (f"12-note scale on a CGCGCD guitar: open strings plus 12-TET frets, "
            f"low C to F, 1/1={root:.2f} Hz")
    degrees = [cents(ideal_hz(s, f) / root) for _, s, f, _ in NOTES[1:]]
    out = [f"! {fname}", "!", desc, f" {len(degrees)}", "!"]
    out += [f" {d:.5f}" for d in degrees]
    out += [
        "!",
        "! Twelve fixed pitches, lowest = 1/1, top note as the last degree (not octave-reduced).",
        "! The six open strings are as tuned; fretted notes are exact 12-TET steps above them.",
        "! Notes low to high: string/fret, Hz, cents above 1/1, as played (cents from ideal):",
    ]
    for k, s, f, measured in NOTES:
        ideal = ideal_hz(s, f)
        where = f"string {s} open" if f == 0 else f"string {s} fret {f}"
        dev = cents(measured / ideal)
        played = "" if f == 0 else f"  played {measured:.2f} ({dev:+.1f})"
        out.append(f"!   {where:<16} {ideal:9.3f} Hz  {cents(ideal / root):9.3f} c  "
                   f"~{NAMES[k % 12]}{k // 12 - 1}{played}")
    out += [
        "! Fretted notes were played 3-14 cents sharp of 12-TET (normal fretting sharpness),",
        "! except string 3 fret 2: its weak fundamental read 4.8 cents flat, its overtones 3.9 sharp.",
        "! Tuned by ear and recorded in 2026.",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="ascii", newline="\r\n") as f:
        f.write("\n".join(out) + "\n")
    print(f"Wrote {path}")


def main():
    write_mkscale(os.path.join(SCALES_DIR, "Guitar-12Note.mkscale"),
                  [(k, hz) for k, _, _, hz in NOTES])
    write_mkscale(os.path.join(SCALES_DIR, "Guitar-12Note-Ideal.mkscale"),
                  [(k, ideal_hz(s, f)) for k, s, f, _ in NOTES])
    write_scl(os.path.join(BATCH2_DIR, "guitar9.scl"))


if __name__ == "__main__":
    main()
