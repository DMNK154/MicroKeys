# MicroKeys

A microtonal instrument plugin (VST3 and standalone) that lets you tune every key of a MIDI keyboard individually, the way you would retune the strings of a guitar. It was built to play by-ear open guitar tunings on a keyboard. This repository includes those tunings, the recordings they were measured from, the scripts that turn the measurements into scale files, and a first-pass analyzer for new recordings.

## Download

**Windows 10/11 (64-bit):** get the installer from the [latest release](https://github.com/DMNK154/MicroKeys/releases/latest). Download `MicroKeys-…-Windows-Setup.exe` and double-click it. It installs the VST3 plugin, the standalone app and the tunings. If Windows says "Windows protected your PC", click **More info**, then **Run anyway** (the installer isn't signed with a paid certificate). A portable zip is there too, for installing by hand.

There is no macOS or Linux download: MicroKeys has only been built and tested on Windows so far.

## Features

- **Per-key tuning.** Select a key by playing or clicking it, then drag the cents slider (±200 cents, 0.001-cent steps). The pitch updates while the note is sounding, so you can tune by ear like turning a tuning peg. The slider widens automatically for keys tuned further out.
- **Exact frequencies.** A row of 12 boxes shows one octave of keys in Hz to three decimals. Pick the octave (C0 to C8) from the Octave menu; it also follows the last key you played. Type a frequency between 1 Hz and 20 kHz and press Enter.
- **Tune all octaves.** With the toggle on (the default), retuning one key retunes every key of that pitch class, like a string. Turn it off to tune single keys. **Reset key** and **Reset all** return keys to standard tuning.
- **Scale files.** Save and load complete tunings as `.mkscale` files.
- **Scala import.** Load a Scala `.scl` scale with up to 1024 notes per period, including non-octave periods. Its 1/1 goes on the selected key at that key's current frequency, and each following degree goes on the next key up, black and white keys alike, so a 7-note scale repeats every 7 keys. The import retunes all 128 keys.
- **Scale name display.** The current scale's name is shown, with "(edited)" once you change a key. The tuning and the name are saved with your DAW project.
- **Sound.** A 16-voice FM electric-piano voice with Gain, Brightness, Attack, Decay, Sustain and Release controls.

## Using the tunings

Click **Load scale...** in the plugin and browse to a `.mkscale` or `.scl` file. The dialog opens in your `Documents\MicroKeys Scales` folder, which the plugin creates the first time you click Save or Load. If your Documents folder is synced by OneDrive, it is `OneDrive\Documents\MicroKeys Scales`. Copy the files there to keep them at hand.

For the guitar tunings, load the `.mkscale` files, which put each string on its own key at its exact frequency. The `.scl` versions are for Scala and other Scala-compatible instruments; loaded into MicroKeys they place the scale degrees on consecutive keys instead.

`.mkscale` files are plain XML: one `<Key note="0-127" cents="..."/>` element per retuned MIDI key, giving that key's offset in cents from standard 12-TET tuning at A440. Keys that are not listed play at standard pitch. The plugin leaves out keys at 0 cents when it saves; the files in this repository list all 128.

## The tunings

All tunings except the standard scales in `tunings/examples/` are by W Ross Warren. The guitar tunings were tuned by ear on a standard (12-TET fretted) guitar, recorded, and measured from the recordings by spectral analysis.

The by-ear files (`Guitar-ByEar3` to `Guitar-ByEar8`) keep the strings as played, and set an interval to a pure ratio only where the measurement was within about 3.3 cents of it and the ear was plausibly aiming at it. The two `-Just` files go further: every string of tunings 1 and 2 is set to 3-limit just intonation, which moves some strings by up to about 5 cents (tuning 1) and 10.4 cents (tuning 2). In the 12-note scale, fretted notes are idealized to exact 12-TET steps above their open string, because that is what a fretted guitar produces.

### `tunings/full-tuning-1/`

| File | What it is |
|---|---|
| `Full Tuning #1.mkscale` | `Guitar-12Note-Ideal.mkscale` (below) with the black keys set by hand: C# and D# about 61 cents above C4 and D4, G# and A# about 95.5 cents above G3 and A3, and F# 1.3 cents above string 1, fret 4. Each black key has one setting for every octave. |
| `Full Tuning #1 (idealized).mkscale` | Each black-key pair locked exactly together (every change is under 0.2 cents). |
| `Full Tuning #1 (idealized, frets).mkscale` | F#, G# and A# set to the exact 12-TET first-position frets on this tuning (string 1 fret 4; string 3 frets 1 and 3). |

### `tunings/guitar/`

Each file puts the open strings on their keys at the measured or idealized frequencies. Keys of the same pitch class follow the nearest string, and the remaining keys sit at 12-TET steps from the lowest string, like frets.

| File | Tuning |
|---|---|
| `Guitar-CGCGCD.mkscale` | Tuning 1 as measured: CGCGCD, about a quarter-tone flat of A440. |
| `Guitar-CGCGCD-Just.mkscale` | Tuning 1 in 3-limit just intonation: 1/1, 3/2, 2/1, 3/1, 4/1, 9/2 above 63.55 Hz. |
| `Guitar-PythComma-Just.mkscale` | Tuning 2: lower strings 1/1, 4/3, 27/16; upper strings 2/1, 3/1, 4/1 each lowered by a Pythagorean comma. |
| `Guitar-ByEar3.mkscale` | Tuning 3: kept as played apart from one pure 5/2 between strings 6 and 3. |
| `Guitar-ByEar4.mkscale` | Tuning 4: 1/1, 4/3, 5/3, plus 4/3 and 5/3 each 10.8 cents higher, and an octave 7.5 cents narrow (the 5/3, the 8/3 and a 5/2 above string 5 are idealized). |
| `Guitar-ByEar5.mkscale` | Tuning 5: a pure 3/2 and a second fifth 9.8 cents wider, a slightly wide fourth, and narrowed octaves. |
| `Guitar-ByEar6.mkscale` | Tuning 6: a 396.8-cent major third, fifths of 696.6 and 710.3 cents, and wide octaves (nothing idealized). |
| `Guitar-ByEar7.mkscale` | Tuning 7: fifths of 711.6 and 720.3 cents, wide octaves, and a pure 3/2 and 8/3 above string 4. |
| `Guitar-ByEar8.mkscale` | Tuning 8: CGCGCD retuned by ear; only the 3/2 between strings 6 and 5 is idealized. |
| `Guitar-12Note.mkscale` | The 12-note scale as played: the six CGCGCD open strings plus fretted notes a whole tone above most of them (and a minor third above the top string). |
| `Guitar-12Note-Ideal.mkscale` | The same 12 notes with every fretted note at an exact 12-TET step above its open string. |

### `scala/`

The guitar tunings as Scala `.scl` files, for use in Scala or any Scala-compatible instrument. They carry the same values as the `.mkscale` files: `guitar1.scl` is `Guitar-CGCGCD-Just` and `guitar9.scl` is `Guitar-12Note-Ideal`. Full Tuning #1 has no `.scl` version.

- `batch-1/guitar1.scl` to `guitar7.scl`: tunings 1 to 7, each as the octave-reduced set of its open strings with the lowest string as 1/1. The comment lines in each file list every open string unreduced, with its frequency.
- `batch-2/guitar8.scl`: tuning 8.
- `batch-2/guitar9.scl`: the idealized 12-note scale as 12 fixed pitches, not octave-reduced, with the top note as the last degree (so it acts as the period, 2910 cents).

### `tunings/examples/`

Three standard reference scales for trying the Scala import: Ptolemy's intense diatonic, 12-note 5-limit just intonation, and quarter-comma meantone.

### `recordings/`

The recordings the tunings were measured from.

| Recording | Tuning |
|---|---|
| `tuning1-cgcgcd.m4a` | Tuning 1 |
| `tuning2-pythagorean-comma.m4a` | Tuning 2 |
| `tuning3.m4a` to `tuning7.m4a` | Tunings 3 to 7 |
| `tuning8-cgcgcd.m4a` | Tuning 8 (each string plucked on its own) |
| `12-note-scale.m4a` | The 12-note scale |

## Building

MicroKeys uses [JUCE 8](https://juce.com/) (included as a git submodule) and CMake. It has been built and tested on Windows with FL Studio.

Requirements: Visual Studio 2022 or the Visual Studio 2022 Build Tools with the "Desktop development with C++" workload, CMake 3.22 or newer, and git.

```bash
git clone --recursive https://github.com/DMNK154/MicroKeys.git
cd MicroKeys
cmake -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release --target MicroKeys_VST3 MicroKeys_Standalone
```

The results are in `build/MicroKeys_artefacts/Release/`:

- `VST3/MicroKeys.vst3`: copy this folder to `C:\Program Files\Common Files\VST3\`, then rescan plugins in your DAW. In FL Studio that is Options > Manage plugins > Find installed plugins.
- `Standalone/MicroKeys.exe`: runs without a DAW. Set the audio and MIDI devices under Options.

If you already cloned without `--recursive`, run `git submodule update --init` before building.

Keep the source folder on a short path. JUCE's build tools can fail when the path goes past Windows' 260-character limit.

## Tools

Python scripts in `tools/` (Python 3.6 or newer; `analyze_guitar_tuning.py` also needs numpy, and the other two use only the standard library):

- `make_scala_batch1.py`: the source of truth for tunings 1 to 8. It writes `guitar1.scl` to `guitar8.scl` into `Scala Submission - Batch 1` and `Scala Submission - Batch 2` subfolders of your scales folder (copy them to `scala/` yourself), rebuilds the `.mkscale` files for tunings 5 to 8 there, and checks every string's frequency against its `.mkscale`. The `.mkscale` files for tunings 1 to 4 must already be in that folder.
- `make_12note_scale.py`: writes the two 12-note `.mkscale` files and `guitar9.scl` (into the `Scala Submission - Batch 2` subfolder).
- `analyze_guitar_tuning.py`: a first-pass analyzer that finds each pluck in a recording and the string it adds (50 to 450 Hz). It reads mono 16-bit WAV only, so convert a recording first, for example `ffmpeg -i recordings/tuning5.m4a -ac 1 -c:a pcm_s16le tuning5.wav`, then run `python tools/analyze_guitar_tuning.py tuning5.wav`. Treat its output as leads only: on known recordings it sometimes reports a string an octave too high, can miss a string, and mistakes speech for extra strings.

The two `make_` scripts read and write your scales folder. Set the `MICROKEYS_SCALES_DIR` environment variable if yours is somewhere other than `~/OneDrive/Documents/MicroKeys Scales`.

## License

Copyright (C) 2026 W Ross Warren.

The recordings (`recordings/`) and the tunings (`tunings/full-tuning-1/`, `tunings/guitar/` and `scala/`) are licensed under the [Creative Commons Attribution 4.0 International licence (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/): you may use, share and adapt them, including commercially, as long as you credit W Ross Warren.

The MicroKeys software (everything else, including the code in `Source/` and `tools/`) is licensed under the [GNU Affero General Public License v3.0](LICENSE). It is built on the JUCE framework, whose modules are dual-licensed under the AGPLv3 and the commercial JUCE licence. The VST3 build also uses Steinberg's VST3 SDK, which JUCE bundles under GPLv3 or Steinberg's proprietary licence. See `JUCE/LICENSE.md`.
