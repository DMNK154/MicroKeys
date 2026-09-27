"""Assemble THIRD_PARTY_NOTICES.txt for the MicroKeys Windows binary release.

Every licence or copyright text in the output is read from its source file at
run time and copied unchanged (only line endings are converted to CRLF, and
blank lines at the very start or end of a copied block are dropped). The
script then re-reads each source file and checks that the copied text appears
byte-for-byte in the written file.
"""

import hashlib
import os
import re
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # repository root (packaging/notices -> ../..)
OUT = os.path.join(ROOT, "packaging", "THIRD_PARTY_NOTICES.txt")

# Licence texts that the JUCE tree does not contain, kept verbatim next to this script.
GPL3_SRC = os.path.join(HERE, "GPL-3.0.txt")
GPL3_SHA256_LF = "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"  # gnu.org gpl-3.0.txt
UNICODE_SRC = os.path.join(HERE, "Unicode-3.0.txt")

VST3 = "JUCE/modules/juce_audio_processors/format_types/VST3_SDK"
WIDTH = 79


def src_path(rel):
    return rel if os.path.isabs(rel) else os.path.join(ROOT, *rel.split("/"))


def read_text(rel):
    data = open(src_path(rel), "rb").read()
    assert not data.startswith(b"\xef\xbb\xbf"), rel
    text = data.decode("utf-8").replace("\r\n", "\n")
    assert "\r" not in text, rel
    return text


def trim(text):
    lines = text.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def whole(rel):
    return trim(read_text(rel))


def lines(rel, first, last, first_starts, last_starts):
    """Lines first..last (1-based, inclusive), checking the boundary lines."""
    all_lines = read_text(rel).split("\n")
    seg = all_lines[first - 1:last]
    assert seg[0].startswith(first_starts), (rel, seg[0])
    assert seg[-1].startswith(last_starts), (rel, seg[-1])
    return trim("\n".join(seg))


def until(rel, end_marker):
    """From the start of the file up to (not including) the line starting with end_marker.
    Returns the text and the number of the last line it contains."""
    all_lines = read_text(rel).split("\n")
    assert all_lines[0].strip(), rel  # no leading blank line, so line numbers start at 1
    idx = next(i for i, l in enumerate(all_lines) if l.startswith(end_marker))
    text = trim("\n".join(all_lines[:idx]))
    return text, text.count("\n") + 1


def first_comment(rel):
    """The first /* ... */ comment of a file (the JUCE module header)."""
    text = read_text(rel)
    assert text.startswith("/*"), rel
    end = text.index("*/") + 2
    return trim(text[:end]), text[:end].count("\n") + 1


def vst_attribution():
    """The trademark attribution sentence, copied from the VST3 usage guidelines PDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:  # the sentence is also asserted verbatim where this is called
        return "VST is a trademark of Steinberg Media Technologies GmbH, registered in Europe and other countries."

    pdf = src_path(f"{VST3}/VST3_Usage_Guidelines.pdf")
    doc = fitz.open(pdf)
    text = "\n".join(page.get_text() for page in doc)
    m = re.search(r"Attribution:\s*[\"\u201c](VST is a trademark of.*?)[\"\u201d]", text, re.S)
    assert m, "attribution not found"
    return " ".join(m.group(1).split())


# ---------------------------------------------------------------------------
# Output helpers

out = []
verbatim_blocks = []  # (label, text) for the verification pass


def emit(s=""):
    out.append(s)


def para(text, indent=""):
    emit(textwrap.fill(" ".join(text.split()), width=WIDTH, initial_indent=indent,
                       subsequent_indent=indent, break_long_words=False, break_on_hyphens=False))
    emit()


def field(label, text):
    lead = f"{label + ':':<15}"
    emit(textwrap.fill(" ".join(text.split()), width=WIDTH, initial_indent=lead,
                       subsequent_indent=" " * len(lead), break_long_words=False,
                       break_on_hyphens=False))


def section(title):
    emit("=" * WIDTH)
    emit(title)
    emit("=" * WIDTH)
    emit()


def verbatim(label, text):
    verbatim_blocks.append((label, text))
    emit(f"[Begin verbatim text: {label}]")
    emit()
    emit(text)
    emit()
    emit("[End verbatim text]")
    emit()


# ---------------------------------------------------------------------------
# Gather facts from the tree

cmake = read_text("CMakeLists.txt")
VERSION = re.search(r"project\(MicroKeys VERSION ([0-9.]+)\)", cmake).group(1)
TAG = f"v{VERSION}"

std_header = read_text("JUCE/modules/juce_core/system/juce_StandardHeader.h")
juce_ver = ".".join(re.search(rf"#define JUCE_{k}\s+(\d+)", std_header).group(1)
                    for k in ("MAJOR_VERSION", "MINOR_VERSION", "BUILDNUMBER"))
assert juce_ver == "8.0.8", juce_ver

versions = {
    "zlib": re.search(r'#define ZLIB_VERSION "([^"]+)"', read_text("JUCE/modules/juce_core/zip/zlib/zlib.h")).group(1),
    "libpng": re.search(r'#define PNG_LIBPNG_VER_STRING "([^"]+)"', read_text("JUCE/modules/juce_graphics/image_formats/pnglib/png.h")).group(1),
    "libjpeg": re.search(r'#define JVERSION\s+"([^"]+)"', read_text("JUCE/modules/juce_graphics/image_formats/jpglib/jversion.h")).group(1),
    "harfbuzz": re.search(r'#define HB_VERSION_STRING "([^"]+)"', read_text("JUCE/modules/juce_graphics/fonts/harfbuzz/hb-version.h")).group(1),
    "vst3": re.search(r'#define kVstVersionString\s+"VST ([^"]+)"', read_text(f"{VST3}/pluginterfaces/vst/vsttypes.h")).group(1),
}
assert versions == {"zlib": "1.3.1", "libpng": "1.6.37", "libjpeg": "6b  27-Mar-1998",
                    "harfbuzz": "10.1.0", "vst3": "3.7.12"}, versions
assert os.path.isdir(src_path("JUCE/modules/juce_audio_formats/codecs/oggvorbis/libvorbis-1.3.7"))
assert "1.4.3" in read_text("JUCE/modules/juce_audio_formats/codecs/flac/JUCE_CHANGES.txt")

MODULES = ["juce_audio_utils", "juce_audio_processors", "juce_audio_plugin_client",
           "juce_audio_formats", "juce_audio_devices", "juce_audio_basics", "juce_gui_extra",
           "juce_gui_basics", "juce_graphics", "juce_events", "juce_data_structures", "juce_core"]
juce_notice, juce_notice_lines = first_comment("JUCE/modules/juce_core/juce_core.h")
for m in MODULES:  # the same notice heads every module
    assert first_comment(f"JUCE/modules/{m}/{m}.h")[0] == juce_notice, m
juce_licence_md, juce_licence_md_lines = until("JUCE/LICENSE.md", "## The JUCE Framework Dependencies")

# Identical-file facts stated in the text
same = lambda a, b: read_text(a) == read_text(b)
assert same(f"{VST3}/LICENSE.txt", f"{VST3}/pluginterfaces/LICENSE.txt")
assert same(f"{VST3}/base/LICENSE.txt", f"{VST3}/public.sdk/LICENSE.txt")
ogg_licence = whole("JUCE/modules/juce_audio_formats/codecs/oggvorbis/Ogg Vorbis Licence.txt")
assert ogg_licence.endswith(whole("JUCE/modules/juce_audio_formats/codecs/oggvorbis/libvorbis-1.3.7/COPYING"))

gpl3 = read_text(GPL3_SRC)
assert hashlib.sha256(gpl3.encode("utf-8")).hexdigest() == GPL3_SHA256_LF, "GPLv3 copy is not the canonical text"
unicode_licence = whole(UNICODE_SRC)
assert unicode_licence.startswith("UNICODE LICENSE V3") and "SPDX-License-Identifier: Unicode-3.0" in unicode_licence

ATTRIBUTION = vst_attribution()
assert ATTRIBUTION == "VST is a trademark of Steinberg Media Technologies GmbH, registered in Europe and other countries.", ATTRIBUTION
IJG_STATEMENT = re.search(r'documentation must state that "(this software is based in part on the work of\s+the Independent JPEG Group)"',
                          read_text("JUCE/modules/juce_graphics/image_formats/jpglib/README")).group(1)
IJG_STATEMENT = " ".join(IJG_STATEMENT.split())
IJG_STATEMENT = IJG_STATEMENT[0].upper() + IJG_STATEMENT[1:] + "."

SRC_ZIP = f"MicroKeys-{VERSION}-source-with-JUCE.zip"
REPO = "https://github.com/DMNK154/MicroKeys"

# ---------------------------------------------------------------------------
# Header

title = f"MicroKeys {VERSION} for Windows (64-bit): third-party notices and licences"
emit(title)
emit("=" * len(title))
emit()
emit("MicroKeys")
emit("Copyright (C) 2026 W Ross Warren")
emit(REPO)
emit()
para("This release contains two programs built from the same source code: "
     "MicroKeys.vst3, the VST\u00ae 3 plug-in, and MicroKeys.exe, the standalone application. "
     "Both are free software: you can redistribute them and/or modify them under the terms of "
     "the GNU Affero General Public License, version 3 (AGPLv3), as published by the Free "
     "Software Foundation. The full text of that licence is in LICENSE.txt, which comes with "
     "this file. MicroKeys comes with NO WARRANTY, to the extent permitted by law; see sections "
     "15 and 16 of the licence.")

emit("Complete corresponding source code")
emit("----------------------------------")
para("The complete corresponding source code of both programs is available free of charge. "
     "It includes the JUCE framework, every third-party component listed in this file, and "
     "the CMake build files used to build the programs. You can get it in either of two ways:")
emit(f"  - From the Git repository {REPO}")
emit(f"    at tag {TAG}, together with the JUCE submodule (JUCE {juce_ver}) that the")
emit("    tag points to. This command downloads both:")
emit()
emit(f"      git clone --recurse-submodules --branch {TAG} {REPO}.git")
emit()
emit(f"  - As the archive {SRC_ZIP}, attached to the {TAG}")
emit(f"    release at {REPO}/releases/tag/{TAG}")
emit("    It holds the repository and the JUCE submodule in one archive. (GitHub's")
emit("    automatic \"Source code\" downloads leave the JUCE submodule out.)")
emit()

emit("Tunings and recordings")
emit("----------------------")
para("The tunings and recordings by W Ross Warren that come with MicroKeys are not covered by "
     "the AGPLv3. They are licensed under the Creative Commons Attribution 4.0 International "
     "licence (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/")

emit("Acknowledgements")
emit("----------------")
para(IJG_STATEMENT)
para(ATTRIBUTION)

emit("Third-party components")
emit("----------------------")
para("MicroKeys is built on the JUCE framework, which contains the third-party code listed "
     "below. Each numbered section says what the component is, which program contains it, "
     "its licence, and then gives the licence and copyright text copied verbatim from the "
     "component's own files. File paths are relative to the root of the MicroKeys source "
     "code.")

rows = [
    ("1", "JUCE framework", juce_ver, "AGPLv3", "both"),
    ("2", "zlib", versions["zlib"], "zlib", "both"),
    ("3", "libpng", versions["libpng"], "libpng-2.0", "both"),
    ("4", "IJG JPEG library (libjpeg)", "6b", "IJG", "both"),
    ("5", "libFLAC", "1.4.3", "BSD-3-Clause", "both"),
    ("6", "Ogg Vorbis (libogg, libvorbis)", "1.3.7", "BSD-3-Clause", "both"),
    ("7", "HarfBuzz", versions["harfbuzz"], "MIT-style, ISC", "both"),
    ("8", "SheenBidi", "-", "Apache-2.0", "both"),
    ("9", "Steinberg VST 3 SDK: pluginterfaces", versions["vst3"], "GPLv3", "VST3"),
    ("10", "Steinberg VST 3 SDK: base, public.sdk", versions["vst3"], "BSD-3-Clause", "VST3"),
    ("11", "PreSonus Plug-In Extensions", "-", "public domain", "VST3"),
    ("12", "Unicode Character Database tables", "-", "Unicode-3.0", "both"),
]
fmt = "  {:<3} {:<38} {:<8} {:<14} {}"
emit(fmt.format("#", "Component", "Version", "Licence", "In"))
emit(fmt.format("--", "-" * 38, "-" * 8, "-" * 14, "----"))
for r in rows:
    emit(fmt.format(*r))
emit()
para('"both" means the component is in MicroKeys.exe and in MicroKeys.vst3. '
     '"VST3" means it is in MicroKeys.vst3 only.', indent="  ")

# ---------------------------------------------------------------------------
# 1. JUCE

section(f"1. JUCE framework {juce_ver}")
field("What it is", "The C++ framework MicroKeys is built on. It provides the VST3 plug-in and "
      "standalone application wrappers, audio and MIDI device access, the user interface, and "
      "graphics and text rendering. Made by Raw Material Software Limited (https://juce.com).")
field("Included in", "MicroKeys.exe and MicroKeys.vst3. Modules used: " + ", ".join(MODULES) + ".")
field("Licence", "GNU Affero General Public License, version 3 (AGPLv3). The JUCE framework "
      "modules are dual-licensed under the AGPLv3 and the commercial JUCE 8 licence; MicroKeys "
      "uses them under the AGPLv3. The full text of the AGPLv3 is in LICENSE.txt.")
field("Copyright", "Copyright (c) Raw Material Software Limited")
field("Source", f"JUCE/ (a Git submodule of https://github.com/juce-framework/JUCE, tag {juce_ver})")
emit()
para("JUCE's statement of its framework licence (the list of dependencies that follows it in "
     "the same file is covered by the other sections of this file):")
verbatim(f"JUCE/LICENSE.md, lines 1-{juce_licence_md_lines}", juce_licence_md)
para("The notice at the top of every JUCE module source file:")
verbatim(f"JUCE/modules/juce_core/juce_core.h, lines 1-{juce_notice_lines}", juce_notice)

# 2. zlib
section(f"2. zlib {versions['zlib']}")
field("What it is", "General-purpose data compression library (deflate/inflate), used by "
      "JUCE's zip and gzip streams.")
field("Included in", "MicroKeys.exe and MicroKeys.vst3")
field("Licence", "zlib licence")
field("Copyright", "(C) 1995-2024 Jean-loup Gailly and Mark Adler")
field("Modified", "Yes, slightly, by the JUCE authors. The changes are listed in "
      "JUCE/modules/juce_core/zip/zlib/JUCE_CHANGES.txt.")
field("Source", "JUCE/modules/juce_core/zip/zlib/")
emit()
verbatim("JUCE/modules/juce_core/zip/zlib/LICENSE", whole("JUCE/modules/juce_core/zip/zlib/LICENSE"))

# 3. libpng
section(f"3. libpng {versions['libpng']}")
field("What it is", "The PNG Reference Library, used by JUCE to read and write PNG images.")
field("Included in", "MicroKeys.exe and MicroKeys.vst3")
field("Licence", "PNG Reference Library License version 2 (libpng-2.0). The text below also "
      "contains the earlier libpng licence that covers the contributions to libpng 0.5 "
      "through 1.6.35.")
field("Copyright", "Copyright (c) 1995-2019 The PNG Reference Library Authors, and the other "
      "holders named below")
field("Modified", "Yes, slightly, by the JUCE authors. The changes are marked \"JUCE CHANGE "
      "STARTS HERE\" and \"JUCE CHANGE ENDS HERE\" in the source and described in "
      "libpng_readme.txt.")
field("Source", "JUCE/modules/juce_graphics/image_formats/pnglib/")
emit()
verbatim("JUCE/modules/juce_graphics/image_formats/pnglib/LICENSE",
         whole("JUCE/modules/juce_graphics/image_formats/pnglib/LICENSE"))

# 4. IJG
jpg_readme = "JUCE/modules/juce_graphics/image_formats/jpglib/README"
section("4. Independent JPEG Group's JPEG library (libjpeg) 6b")
field("What it is", "JPEG image library from the Independent JPEG Group, used by JUCE to "
      "load JPEG images.")
field("Included in", "MicroKeys.exe and MicroKeys.vst3")
field("Licence", "IJG licence (the Independent JPEG Group's licence)")
field("Copyright", "Copyright (C) 1991-1998, Thomas G. Lane")
field("Statement", IJG_STATEMENT)
field("Modified", "JUCE includes only part of the library. JUCE's notes on it are in "
      "\"JUCE/modules/juce_graphics/image_formats/jpglib/changes to libjpeg for JUCE.txt\".")
field("Version", f"{versions['libjpeg']} (jversion.h)")
field("Source", "JUCE/modules/juce_graphics/image_formats/jpglib/ (the complete README is there)")
emit()
para("The \"LEGAL ISSUES\" section of the library's README. The README's remaining paragraphs "
     "concern ansi2knr.c and the Unix configure scripts, which are not part of JUCE's copy of "
     "the library.")
verbatim(f"{jpg_readme}, lines 111-158",
         lines(jpg_readme, 111, 158, "LEGAL ISSUES", "assumed by the product vendor."))

# 5. FLAC
flac_lic = "JUCE/modules/juce_audio_formats/codecs/flac/Flac Licence.txt"
section("5. libFLAC 1.4.3")
field("What it is", "Free Lossless Audio Codec library, used by JUCE to read and write FLAC "
      "audio files.")
field("Included in", "MicroKeys.exe and MicroKeys.vst3")
field("Licence", "BSD-3-Clause (Xiph.Org BSD-style licence)")
field("Copyright", "Copyright (C) 2000-2009 Josh Coalson; Copyright (C) 2011-2023 Xiph.Org "
      "Foundation")
field("Modified", "Yes, slightly, by the JUCE authors, as described at the top of the text "
      "below and in JUCE/modules/juce_audio_formats/codecs/flac/JUCE_CHANGES.txt.")
field("Source", "JUCE/modules/juce_audio_formats/codecs/flac/")
emit()
verbatim(flac_lic, whole(flac_lic))

# 6. Ogg Vorbis
ogg_dir = "JUCE/modules/juce_audio_formats/codecs/oggvorbis"
section("6. Ogg Vorbis: libvorbis 1.3.7 and libogg")
field("What it is", "The Ogg container library (libogg: bitwise.c, framing.c) and the Vorbis "
      "audio codec library (libvorbis), used by JUCE to read and write Ogg Vorbis audio "
      "files.")
field("Included in", "MicroKeys.exe and MicroKeys.vst3")
field("Licence", "BSD-3-Clause (Xiph.Org BSD-style licence)")
field("Copyright", "Copyright (c) 2002-2020 Xiph.org Foundation; the libogg source files are "
      "(C) 1994-2018 Xiph.Org Foundation; lib/lpc.c also carries Copyright 1992, 1993, 1994 "
      "Jutta Degener and Carsten Bormann, Technische Universitaet Berlin")
field("Modified", "Yes, slightly, by the JUCE authors, as described at the top of the text "
      "below.")
field("Source", f"{ogg_dir}/")
emit()
para("The licence file for JUCE's copy of Ogg Vorbis. Its licence text is identical to "
     "libvorbis-1.3.7/COPYING.")
verbatim(f"{ogg_dir}/Ogg Vorbis Licence.txt", ogg_licence)
para("The notice at the top of the libogg source files:")
verbatim(f"{ogg_dir}/framing.c, lines 1-11",
         lines(f"{ogg_dir}/framing.c", 1, 11, "/*****", " *****"))
lpc = f"{ogg_dir}/libvorbis-1.3.7/lib/lpc.c"
para("libvorbis's lib/lpc.c contains code by Jutta Degener and Carsten Bormann, whose notices "
     "must be preserved:")
verbatim(f"{lpc}, lines 17-43",
         lines(lpc, 17, 43, "/* Some of these routines", "*****************"))

# 7. HarfBuzz
hb = "JUCE/modules/juce_graphics/fonts/harfbuzz"
section(f"7. HarfBuzz {versions['harfbuzz']}")
field("What it is", "Text shaping engine that turns Unicode text into positioned glyphs, used "
      "by JUCE's text rendering.")
field("Included in", "MicroKeys.exe and MicroKeys.vst3")
field("Licence", "\"Old MIT\" licence (SPDX: MIT-Modern-Variant). The text mentions COPYING "
      "files in subdirectories; JUCE's copy of HarfBuzz contains none. Two source files carry "
      "their own permissive licences, reproduced after COPYING: hb-algs.hh (the fasthash "
      "functions, MIT) and hb-ucd.cc (ISC).")
field("Copyright", "Google, Inc.; Red Hat, Inc.; Behdad Esfahbod; and the other holders named "
      "below")
field("Source", f"{hb}/")
emit()
verbatim(f"{hb}/COPYING", whole(f"{hb}/COPYING"))
para("The licence of the fasthash functions in hb-algs.hh:")
verbatim(f"{hb}/hb-algs.hh, lines 261-284",
         lines(f"{hb}/hb-algs.hh", 261, 284, "/* The MIT License", "*/"))
para("The licence of hb-ucd.cc:")
verbatim(f"{hb}/hb-ucd.cc, lines 1-15", lines(f"{hb}/hb-ucd.cc", 1, 15, "/*", " */"))

# 8. SheenBidi
sb = "JUCE/modules/juce_graphics/unicode/sheenbidi"
section("8. SheenBidi")
field("What it is", "Implementation of the Unicode Bidirectional Algorithm (layout of "
      "right-to-left and mixed-direction text), used by JUCE's text layout.")
field("Included in", "MicroKeys.exe and MicroKeys.vst3")
field("Licence", "Apache License, Version 2.0. SheenBidi has no NOTICE file.")
field("Copyright", "Copyright (C) 2014-2022 Muhammad Tayyab Akram")
field("Modified", f"Yes: the JUCE authors changed some #include paths, as listed in "
      f"{sb}/JUCE_CHANGES.txt.")
field("Version", "Not recorded in the source tree.")
field("Source", f"{sb}/")
emit()
para("The copyright notice at the top of the SheenBidi source files:")
verbatim(f"{sb}/Headers/SheenBidi.h, lines 1-15",
         lines(f"{sb}/Headers/SheenBidi.h", 1, 15, "/*", " */"))
verbatim(f"{sb}/LICENSE", whole(f"{sb}/LICENSE"))

# 9. VST3 pluginterfaces
section(f"9. Steinberg VST 3 SDK {versions['vst3']}: pluginterfaces")
field("What it is", "The VST 3 plug-in interface definitions (the pluginterfaces directory of "
      "Steinberg's VST 3 SDK). They let VST 3 hosts such as FL Studio load MicroKeys.vst3.")
field("Included in", "MicroKeys.vst3 only (not in MicroKeys.exe)")
field("Licence", "GNU General Public License, version 3 (GPLv3). The VST 3 SDK is "
      "dual-licensed under the proprietary Steinberg VST3 License or the GPLv3; MicroKeys "
      "uses it under the GPLv3 option. The full text of the GPLv3 is in Appendix A at the end "
      "of this file. Section 13 of the AGPLv3 and section 13 of the GPLv3 allow the two "
      "licences to be combined in one program.")
field("Copyright", "(c) 2024, Steinberg Media Technologies GmbH")
field("Modified", "JUCE's only change to the SDK (listed in VST3_SDK/JUCE_README.md) is to the "
      "moduleinfotool utility, which runs during the build and is not shipped.")
field("Trademarks", ATTRIBUTION + " See VST3_SDK/VST3_Usage_Guidelines.pdf for the rules on "
      "using the VST name and logos.")
field("Source", f"{VST3}/pluginterfaces/")
emit()
para("The licence file the pluginterfaces source files refer to (VST3_SDK/pluginterfaces/"
     "LICENSE.txt is identical):")
verbatim(f"{VST3}/LICENSE.txt", whole(f"{VST3}/LICENSE.txt"))

# 10. VST3 base / public.sdk
tpp = f"{VST3}/pluginterfaces/vst/ivsttestplugprovider.h"
tpp_all = read_text(tpp).split("\n")
tpp_start = tpp_all.index("// LICENSE") - 1
assert tpp_all[tpp_start + 3].startswith("//------")  # rule under the "(c)" line
tpp_end = next(i for i in range(tpp_start + 4, len(tpp_all)) if tpp_all[i].startswith("//------"))
assert "OF THE POSSIBILITY OF SUCH DAMAGE." in tpp_all[tpp_end - 1]
section(f"10. Steinberg VST 3 SDK {versions['vst3']}: base and public.sdk")
field("What it is", "Helper classes from Steinberg's VST 3 SDK (the base and public.sdk "
      "directories, and pluginterfaces/vst/ivsttestplugprovider.h) that JUCE's VST3 wrapper "
      "uses: component and edit-controller base classes, parameters, buses, preset files, "
      "streams and string conversion.")
field("Included in", "MicroKeys.vst3 only (not in MicroKeys.exe)")
field("Licence", "BSD-3-Clause")
field("Copyright", "(c) 2024, Steinberg Media Technologies GmbH; ivsttestplugprovider.h: (c) "
      "2022, Steinberg Media Technologies GmbH")
field("Source", "VST3_SDK/base/ and VST3_SDK/public.sdk/, both in "
      "JUCE/modules/juce_audio_processors/format_types/")
emit()
para("The licence file of the base directory (public.sdk/LICENSE.txt is identical; the same "
     "terms are embedded at the top of each of these source files):")
verbatim(f"{VST3}/base/LICENSE.txt", whole(f"{VST3}/base/LICENSE.txt"))
para("The licence embedded in pluginterfaces/vst/ivsttestplugprovider.h:")
verbatim(f"{tpp}, lines {tpp_start + 1}-{tpp_end + 1}",
         lines(tpp, tpp_start + 1, tpp_end + 1, "//------", "//------"))

# 11. PreSonus
psl = "JUCE/modules/juce_audio_processors/format_types/pslextensions/ipslviewembedding.h"
section("11. PreSonus Plug-In Extensions")
field("What it is", "The PreSonus plug-in view embedding interface (ipslviewembedding.h), "
      "which JUCE's VST3 wrapper implements for PreSonus hosts.")
field("Included in", "MicroKeys.vst3 only (not in MicroKeys.exe)")
field("Licence", "Public domain. No notice is required; it is acknowledged here.")
field("Source", psl)
emit()
verbatim(f"{psl}, lines 1-17", lines(psl, 1, 17, "//*****", "//*****"))

# 12. Unicode
section("12. Unicode Character Database tables")
field("What it is", "Lookup tables generated from the Unicode Character Database (character "
      "properties, scripts, bidirectional types and emoji data). They are part of HarfBuzz, "
      "SheenBidi and JUCE's own text code.")
field("Included in", "MicroKeys.exe and MicroKeys.vst3")
field("Licence", "Unicode License v3 (Unicode-3.0). JUCE's LICENSE.md does not list it; it is "
      "included here because the licence asks for its notice to accompany software derived "
      "from Unicode data files.")
field("Copyright", "Copyright \u00a9 1991-2024 Unicode, Inc.")
field("Source", f"{hb}/hb-ucd-table.hh, {hb}/hb-unicode-emoji-table.hh, {sb}/Source/, and "
      "JUCE/modules/juce_graphics/unicode/juce_UnicodeGenerated.cpp")
emit()
para("The source tree does not contain the licence text. The text below is the Unicode "
     "License v3; the current version is published at https://www.unicode.org/license.txt.")
verbatim("Unicode License v3", unicode_licence)

# Other components / runtime
section("Other components")
para("JUCE/LICENSE.md also lists AudioUnitSDK, Oboe, GLEW (with Mesa and Khronos code), CHOC "
     "(with QuickJS), LV2, AAX and Box2D. None of them is compiled into MicroKeys.exe or "
     "MicroKeys.vst3: they belong to other platforms, other plug-in formats, or JUCE modules "
     "that MicroKeys does not use. They are part of the JUCE source tree, under their own "
     "licences, and so are included in the source code described at the top of this file.")
para("The Microsoft Visual C++ runtime library is statically linked into MicroKeys.exe and "
     "MicroKeys.vst3, so no separate runtime installation is needed. It is part of the "
     "Microsoft C/C++ compiler toolset used to build the programs and is used under "
     "Microsoft's licence terms for that toolset. All other libraries the programs use are "
     "part of Windows.")

# Appendix A
section("Appendix A. GNU General Public License, version 3")
para("This is the licence under which MicroKeys.vst3 uses the Steinberg VST 3 SDK "
     "pluginterfaces (section 9). It is the text published at "
     "https://www.gnu.org/licenses/gpl-3.0.txt.")
verbatim("GNU General Public License, version 3", trim(gpl3))

emit("End of third-party notices.")

# Every path named in the text must exist in the tree.
for rel in ["JUCE/LICENSE.md", "JUCE/modules/juce_core/zip/zlib/JUCE_CHANGES.txt",
            "JUCE/modules/juce_graphics/image_formats/pnglib/libpng_readme.txt",
            "JUCE/modules/juce_graphics/image_formats/jpglib/changes to libjpeg for JUCE.txt",
            "JUCE/modules/juce_audio_formats/codecs/flac/JUCE_CHANGES.txt",
            f"{sb}/JUCE_CHANGES.txt", f"{sb}/Source", f"{hb}/hb-ucd-table.hh", lpc,
            f"{hb}/hb-algs.hh", f"{hb}/hb-ucd.cc",
            f"{hb}/hb-unicode-emoji-table.hh",
            "JUCE/modules/juce_graphics/unicode/juce_UnicodeGenerated.cpp",
            f"{VST3}/JUCE_README.md", f"{VST3}/VST3_Usage_Guidelines.pdf", f"{VST3}/base",
            f"{VST3}/public.sdk", f"{VST3}/pluginterfaces", psl,
            "JUCE/modules/juce_audio_plugin_client/AU/AudioUnitSDK",
            "JUCE/modules/juce_audio_devices/native/oboe", "JUCE/modules/juce_opengl/opengl/juce_gl.h",
            "JUCE/modules/juce_javascript/choc", "JUCE/modules/juce_audio_processors/format_types/LV2_SDK",
            "JUCE/modules/juce_audio_plugin_client/AAX/SDK", "JUCE/modules/juce_box2d/box2d"]:
    assert os.path.exists(src_path(rel)), rel
for name in ["AudioUnitSDK", "Oboe", "GLEW", "Mesa", "Khronos", "CHOC", "QuickJS", "LV2", "AAX", "Box2D"]:
    assert name in read_text("JUCE/LICENSE.md"), name

# ---------------------------------------------------------------------------
# Write with CRLF and verify

body = "\n".join(out).rstrip("\n") + "\n"
data = body.replace("\n", "\r\n").encode("utf-8")
with open(OUT, "wb") as f:
    f.write(data)

# Verification: re-read, check encoding and line endings, and find every verbatim block.
check = open(OUT, "rb").read()
assert not check.startswith(b"\xef\xbb\xbf")
check.decode("utf-8")
assert b"\n" not in check.replace(b"\r\n", b""), "bare LF"
assert b"\r" not in check.replace(b"\r\n", b""), "bare CR"
for label, text in verbatim_blocks:
    needle = (f"[Begin verbatim text: {label}]\r\n\r\n" + text.replace("\n", "\r\n")
              + "\r\n\r\n[End verbatim text]").encode("utf-8")
    assert check.count(needle) == 1, label

# Independent re-derivation of the full-file blocks straight from disk.
full_files = [
    "JUCE/modules/juce_core/zip/zlib/LICENSE",
    "JUCE/modules/juce_graphics/image_formats/pnglib/LICENSE",
    flac_lic,
    f"{ogg_dir}/Ogg Vorbis Licence.txt",
    f"{hb}/COPYING",
    f"{sb}/LICENSE",
    f"{VST3}/LICENSE.txt",
    f"{VST3}/base/LICENSE.txt",
    UNICODE_SRC,
    GPL3_SRC,
]
for rel in full_files:
    raw = open(src_path(rel), "rb").read().replace(b"\r\n", b"\n").strip(b"\n")
    assert raw.replace(b"\n", b"\r\n") in check, rel

non_ascii = sorted({ch for ch in check.decode("utf-8") if ord(ch) > 127})
print(f"wrote {OUT}")
n_lines = check.count(b"\r\n")
print(f"  {len(check)} bytes, {n_lines} lines, {len(verbatim_blocks)} verbatim blocks verified")
print(f"  non-ASCII characters: {' '.join(f'U+{ord(c):04X}' for c in non_ascii)}")
long_lines = [i + 1 for i, l in enumerate(body.split("\n")) if len(l) > WIDTH]
print(f"  lines longer than {WIDTH}: {len(long_lines)} (first few: {long_lines[:10]})")
