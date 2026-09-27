# MicroKeys

<img src="docs/vst-compatible-logo.png" alt="VST Compatible. VST is a registered trademark of Steinberg Media Technologies GmbH" width="120" align="right">

A microtonal instrument plugin (VST® 3 and standalone) that lets you tune every key of a MIDI keyboard individually, the way you would retune the strings of a guitar. It was built to play by-ear open guitar tunings on a keyboard. This repository includes those tunings, the recordings they were measured from, the scripts that turn the measurements into scale files, and a first-pass analyzer for new recordings.

## Download

**Windows 10/11 (64-bit):** get the installer from the [latest release](https://github.com/DMNK154/MicroKeys/releases/latest). Download `MicroKeys-…-Windows-Setup.exe` and double-click it. It installs the VST3 plugin, the standalone app and the tunings. If Windows says "Windows protected your PC", click **More info**, then **Run anyway** (the installer isn't signed with a paid certificate). A portable zip is there too, for installing by hand.

There is no macOS or Linux download: MicroKeys has only been built and tested on Windows so far.

## Features

- **Per-key tuning.** Select a key by playing or clicking it, then drag the cents slider (±200 cents, 0.001-cent steps). The pitch updates while the note is sounding, so you can tune by ear like turning a tuning peg. The slider widens automatically for keys tuned further out.
- **Exact frequencies.** A row of 12 boxes shows one octave of keys in Hz to three decimals. Pick the octave (C0 to C8) from the Octave menu or step through with the < and > buttons beside it; it also follows the last key you played. Type a frequency between 1 Hz and 20 kHz and press Enter.
- **Tune all octaves.** With the toggle on (the default), retuning one key retunes the same key in every other octave, like a string. Turn it off to tune single keys. **Reset key** returns a key to standard tuning; **Reset all** returns every key to standard tuning and sets Keys per octave back to 12.
- **Keys per octave.** The Keys per octave menu, beside the selected key's frequency, says how many keys it takes to reach the octave: 12 (normal), or 5, 7, 19, 22, 24 (quarter tones) or 31. Changing it retunes nothing; it only tells Tune all octaves which keys are octaves of each other. With 24, retuning C4 also puts C6 at exactly twice its frequency and C2 at exactly half, and leaves C5 alone. When it isn't 12 and Tune all octaves is on, the keys a change will reach are tinted orange on the keyboard. The Hz boxes still show 12 piano keys at a time, and the slider and cents readout still measure each key from its standard piano pitch, so in a 24-key layout many keys read several hundred cents: type their Hz in the boxes, then fine-tune with the slider.
- **Scale files.** Save and load complete tunings as `.mkscale` files. A file also remembers Keys per octave when it isn't 12.
- **Scala import.** Load a Scala `.scl` scale with up to 1024 notes per period, including non-octave periods. Its 1/1 goes on the selected key at that key's current frequency, and each following degree goes on the next key up, black and white keys alike, so a 7-note scale repeats every 7 keys. The import retunes all 128 keys. If the scale repeats at an exact octave (2/1) and has 5, 7, 12, 19, 22, 24 or 31 notes, Keys per octave is set to match; the import message mentions it when the setting changes. Step-by-step instructions are in [Importing Scala scales](#importing-scala-scales).
- **Scale name display.** The current scale's name is shown, with "(edited)" once you change a key. The tuning, the name and the Keys per octave setting are saved with your DAW project.
- **Sound.** A 16-voice FM electric-piano voice with Gain, Brightness, Attack, Decay, Sustain and Release controls.

## Using the tunings

Click **Load scale...** in the plugin and browse to a `.mkscale` or `.scl` file. The dialog opens in your `Documents\MicroKeys Scales` folder, which the plugin creates the first time you click Save or Load. If your Documents folder is synced by OneDrive, it is `OneDrive\Documents\MicroKeys Scales`. Copy the files there to keep them at hand.

For the guitar tunings, load the `.mkscale` files, which put each string on its own key at its exact frequency. The `.scl` versions are for Scala and other Scala-compatible instruments; loaded into MicroKeys they place the scale degrees on consecutive keys instead.

To play a Scala scale, see [Importing Scala scales](#importing-scala-scales) below.

`.mkscale` files are plain XML: one `<Key note="0-127" cents="..."/>` element per retuned MIDI key, giving that key's offset in cents from standard 12-TET tuning at A440. Keys that are not listed play at standard pitch. The plugin leaves out keys at 0 cents when it saves; the files in this repository list all 128. A file saved with Keys per octave other than 12 records it on the root element, for example `<MicroKeysScale keysPerOctave="24">`. Files without it, including every file in this repository, are 12 keys per octave. Older versions of MicroKeys ignore the attribute and load the same pitches.

## Importing Scala scales

MicroKeys reads Scala `.scl` files, the standard format for microtonal scales. That includes nearly every scale in the [Scala scale archive](https://www.huygens-fokker.org/docs/scales.zip) and any `.scl` file you write yourself.

Importing replaces the tuning of every key, with no undo, and so does **Reset all**. If you've tuned keys you want to keep, click **Save scale...** first.

### Quick start

1. **Pick the root key.** Play or click the key where the scale's 1/1 should go. The window shows it as "Key: C4" and outlines its Hz box in orange.
   - The root is simply the last key selected. While the window is open, every note MicroKeys receives selects its key, including notes your DAW plays back, and typing a Hz value into a box selects that key too. Stop playback before importing.
   - When MicroKeys first opens, A4 is selected, so that is the root until you pick another key.
   - MicroKeys calls middle C (MIDI note 60) C4. FL Studio's piano roll calls the same key C5.
2. **Set the root's pitch.** The 1/1 takes the root key's current frequency, even one left over from a tuning or scale you loaded earlier.
   - For the key's standard piano pitch (for example 261.626 Hz on C4, or 440 Hz on A4), click **Reset all** first. The key you picked stays selected. Only the root keeps that pitch: every other key, A4 included, moves to the scale.
   - For any other pitch, type it into the root key's Hz box and press Enter, for example 256 on C4.
3. **Import the file.** Click **Load scale...** and choose the `.scl` file. The dialog lists `.mkscale` and `.scl` files together. To try it out, open the **Examples** folder and choose `ptolemy_intense_diatonic.scl`.
4. **Check the summary.** A message shows the scale's description and where it landed, for example: "7 notes per period (1200.00 cents), root 1/1 on C4 at 261.626 Hz." The file name appears as the scale name at the top right.
5. **Play it.** Start on the root and go up one key at a time, black and white alike: each key plays the next degree. A 7-note scale on C4 reaches its octave at G4, not C5, so the white keys alone won't play it.

### How the scale is laid out

- **One degree per key, in order,** on consecutive keys. So a 7-note scale repeats every 7 keys, and a 19-note scale every 19 keys. For example, Ptolemy's intense diatonic on C4 plays:

  | C4 | C#4 | D4 | D#4 | E4 | F4 | F#4 | G4 |
  |---|---|---|---|---|---|---|---|
  | 1/1 | 9/8 | 5/4 | 4/3 | 3/2 | 5/3 | 15/8 | 2/1 |

- **All 128 MIDI keys (0 to 127) are retuned,** above and below the root.
  - The on-screen keyboard covers A0 to C8 (MIDI 21 to 108); scroll with the arrow at its left end to reach its lowest keys. The Hz boxes reach C0 to B8. Play the keys outside those ranges from a MIDI keyboard or the piano roll.
- **Large scales cover fewer octaves.** 128 keys hold 128 / N periods of an N-note scale: about 4 octaves of 31-EDO, or 2.4 of 53-EDO. With the root on A4 at 440 Hz, 53-EDO runs from about 178 Hz to 940 Hz. Pick a higher root key for more low notes, or a lower one for more high notes.
- **The period can be any interval above 1/1.** The scale repeats at the file's last pitch, so non-octave scales such as Bohlen-Pierce (3/1) work too.
- **Pitches** can be cents or ratios.
  - A cents value must contain a decimal point (`700.0` or `701.955`). A plain `700` is read as the ratio 700/1.
  - Ratios are written like `3/2`, or as a whole number such as `2` for 2/1.
  - A scale can have up to 1024 notes per period. Lines starting with `!` are comments.
- **Keys per octave follows the scale when it can.** It is set to match when the scale repeats at an exact 2/1 and has 5, 7, 12, 19, 22, 24 or 31 notes. The summary mentions it when the setting changes. That way **Tune all octaves** keeps treating the right keys as octaves.
  - For these scales other than 12 notes, the root and its octaves are tinted orange after the import (with **Tune all octaves** on, the default).
  - For any other scale, such as 17-, 41- or 53-EDO or Bohlen-Pierce, Keys per octave keeps its previous value, which may be left over from an earlier scale. **Tune all octaves** always copies at exact 2/1 octaves, never at the scale's own period, so it would retune the wrong keys. Turn it off before adjusting single keys.
- **The on-screen keys keep their piano colours and note names,** whatever the scale.

### Putting a set pitch on a different key

A `.kbm` keyboard mapping can put a reference pitch on a key other than the 1/1, for example 1/1 on C4 with A4 = 440 Hz. MicroKeys doesn't read `.kbm` files, but you can get the same result by working out the root's pitch first:

1. Find the degree that will land on the reference key.
2. Divide the reference pitch by that degree's ratio (for a degree in cents, divide by 2^(cents/1200)).
3. Type the result into the root key's Hz box, then import.

For example, the 12-note just intonation in **Examples** puts 5/3 on A4 when its root is C4, so type 440 ÷ 5/3 = 264 into C4. Count keys, not note names: in the 7-note Ptolemy scale on C4, A4 is 9 keys up and plays 5/2 (5/4 one period up), so you would type 176.

### After importing

- **Adjust any key** by ear with the slider, or type its Hz. The scale name then shows "(edited)".
  - The slider and cents readout measure each key from its standard piano pitch, not from the 1/1. With Ptolemy on C4 at 261.626 Hz, the 9/8 on C#4 reads +103.91 cents, and keys far from the root can read thousands.
  - For big changes, type the Hz, then fine-tune with the slider.
  - For the same reason, **Reset key** returns a key to its piano pitch, not its scale pitch.
- **Save your version** with **Save scale...** as a `.mkscale` file. MicroKeys never changes the `.scl` file.
- **The tuning is saved with your DAW project,** and the standalone app keeps it when you close it, so you don't need to import again.

### Not supported

- **Keyboard mapping (`.kbm`) files.** MicroKeys always maps the scale straight up and down the keyboard, one degree per key, so it can't put a 7-note scale on the white keys only.
- **MTS-ESP** (as master or client), **MIDI Tuning Standard** messages and **AnaMark `.tun`** files. The tuning changes only MicroKeys' own sound.
- **Exporting** `.scl`, `.kbm` or `.tun` files.
- **Per-channel tuning and pitch bend.** Each MIDI note number has one pitch on every channel, so a multichannel controller layout (a Lumatone, for example) plays the same pitch for a note number on every channel. Pitch bend is ignored, so MPE bends do nothing.

### Scales to try

- **`Examples`** (installed in `Documents\MicroKeys Scales\Examples`; `tunings/examples/` in this repository):
  - Ptolemy's intense diatonic (7 notes)
  - 12-note 5-limit just intonation
  - quarter-comma meantone

  Put the 12-note ones on a C key so the scale lines up with the piano layout.
- **`Scala files`** (installed in `Documents\MicroKeys Scales\Scala files`; `scala/` in this repository): this project's by-ear guitar tunings as Scala scales of 3 to 11 notes, so they spread across many octaves of keys.
  - To play a guitar tuning with each string on its own key, load its `.mkscale` file instead (see [Using the tunings](#using-the-tunings)).
  - To hear a `.scl` version at the guitar's pitch, type the 1/1 frequency from its description (for example 63.55 Hz for `guitar1.scl`) into the root key's Hz box before importing.
- **The [Scala scale archive](https://www.huygens-fokker.org/docs/scales.zip)** from the Huygens-Fokker Foundation. The link downloads a zip of thousands of `.scl` files. Right-click the downloaded zip, choose **Extract All...**, and extract it into your `Documents\MicroKeys Scales` folder (the scales land in an `scl` subfolder).
- **Your own scales:** the [`.scl` format description](https://www.huygens-fokker.org/scala/scl_format.html) explains how to write one.

### If something goes wrong

- **The root landed on the wrong key, or at the wrong pitch.** Click **Reset all**, click the key you want, then import again. Without **Reset all**, the root keeps whatever pitch the last scale gave that key.
- **"Could not read any data from: ..."** The file is probably stored only in OneDrive's cloud. Right-click it in File Explorer and choose **Always keep on this device**.
- **"Invalid note count", "Could not parse pitch line" and similar messages.** MicroKeys couldn't read the file as a Scala scale.
  - Those two messages quote the line MicroKeys stopped at.
  - MicroKeys takes 1 to 1024 notes per period, so "Invalid note count" also appears for a scale outside that range.
- **"The interval of repetition must be ascending."** The file's last pitch is 1/1 or lower, so there is nothing to repeat the scale at. Two files in the Scala archive, `chimes.scl` and `harmf16.scl`, are like this.
- **Keys far from the root are inaudible or sound harsh.** A scale with few notes per period, or a wide period, spreads across many octaves of the 128 keys. Keys far from the root can end up above or below the range of hearing.

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

VST is a trademark of Steinberg Media Technologies GmbH, registered in Europe and other countries.
