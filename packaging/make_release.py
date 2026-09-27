"""Package a MicroKeys Windows release.

Produces, in --out:
  MicroKeys-<ver>-Windows-Setup.exe       Inno Setup installer
  MicroKeys-<ver>-Windows.zip             portable zip
  MicroKeys-<ver>-source-with-JUCE.zip    complete corresponding source
                                           (repository at --ref plus the JUCE
                                           submodule, which GitHub's automatic
                                           source archives leave out)
  SHA256SUMS.txt

Usage (from the repository root, after building the Release targets):
  python packaging/make_release.py --build <build>/MicroKeys_artefacts/Release \
      --out dist --ref v0.1.0
"""

import argparse
import hashlib
import io
import os
import re
import shutil
import subprocess
import tarfile
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISCC_CANDIDATES = [
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "ISCC.exe"),
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
]


def version():
    text = open(os.path.join(REPO, "CMakeLists.txt"), encoding="utf-8").read()
    return re.search(r"project\(MicroKeys VERSION ([0-9.]+)\)", text).group(1)


def stage(build, dest, ver):
    """Lay out exactly what the zip and the installer ship."""
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    shutil.copytree(os.path.join(build, "VST3", "MicroKeys.vst3"), os.path.join(dest, "MicroKeys.vst3"))
    shutil.copy2(os.path.join(build, "Standalone", "MicroKeys.exe"), dest)

    scales = os.path.join(dest, "MicroKeys Scales")
    layout = [
        (os.path.join("tunings", "guitar"), ".mkscale", ""),
        (os.path.join("tunings", "full-tuning-1"), ".mkscale", ""),
        (os.path.join("scala", "batch-1"), ".scl", "Scala files"),
        (os.path.join("scala", "batch-2"), ".scl", "Scala files"),
        (os.path.join("tunings", "examples"), ".scl", "Examples"),
    ]
    for src, ext, sub in layout:
        out = os.path.join(scales, sub)
        os.makedirs(out, exist_ok=True)
        for name in sorted(os.listdir(os.path.join(REPO, src))):
            if name.endswith(ext):
                shutil.copy2(os.path.join(REPO, src, name), out)

    shutil.copy2(os.path.join(REPO, "LICENSE"), os.path.join(dest, "LICENSE.txt"))
    shutil.copy2(os.path.join(REPO, "packaging", "THIRD_PARTY_NOTICES.txt"), dest)
    howto = open(os.path.join(REPO, "packaging", "HOW TO INSTALL.txt"), encoding="utf-8").read()
    with open(os.path.join(dest, "HOW TO INSTALL.txt"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write(howto.replace("@VERSION@", ver))


def zip_dir(src, zip_path):
    root = os.path.basename(src)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for folder, _, files in os.walk(src):
            for name in sorted(files):
                full = os.path.join(folder, name)
                z.write(full, os.path.join(root, os.path.relpath(full, src)))


def source_zip(ref, zip_path, ver):
    """Repository at `ref` plus the JUCE submodule commit it pins, in one zip."""
    prefix = f"MicroKeys-{ver}/"
    juce_sha = subprocess.check_output(["git", "-C", REPO, "rev-parse", f"{ref}:JUCE"], text=True).strip()
    parts = [
        (["git", "-C", REPO, "archive", "--format=tar", f"--prefix={prefix}", ref], None),
        (["git", "-C", os.path.join(REPO, "JUCE"), "archive", "--format=tar", f"--prefix={prefix}JUCE/", juce_sha], juce_sha),
    ]
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for cmd, _ in parts:
            data = subprocess.check_output(cmd)
            with tarfile.open(fileobj=io.BytesIO(data)) as t:
                for member in t.getmembers():
                    if member.isfile():
                        z.writestr(member.name, t.extractfile(member).read())
    return juce_sha


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", required=True, help="<build>/MicroKeys_artefacts/Release")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", default="HEAD", help="git ref for the source archive, e.g. v0.1.0")
    args = ap.parse_args()

    ver = version()
    notices = os.path.join(REPO, "packaging", "THIRD_PARTY_NOTICES.txt")
    if os.path.getsize(notices) < 50_000 or open(notices, encoding="utf-8").read().startswith("PLACEHOLDER"):
        raise SystemExit("packaging/THIRD_PARTY_NOTICES.txt is missing or a placeholder; "
                         "run packaging/notices/make_notices.py first")
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    staged = os.path.join(out, "stage", f"MicroKeys-{ver}-Windows")
    stage(os.path.abspath(args.build), staged, ver)

    portable = os.path.join(out, f"MicroKeys-{ver}-Windows.zip")
    zip_dir(staged, portable)

    iscc = next(p for p in ISCC_CANDIDATES if os.path.exists(p))
    subprocess.check_call([iscc, "/Q", f"/DVersion={ver}", f"/DStageDir={staged}", f"/DOutDir={out}",
                           os.path.join(REPO, "packaging", "windows", "MicroKeys.iss")])
    installer = os.path.join(out, f"MicroKeys-{ver}-Windows-Setup.exe")

    source = os.path.join(out, f"MicroKeys-{ver}-source-with-JUCE.zip")
    juce_sha = source_zip(args.ref, source, ver)

    assets = [installer, portable, source]
    with open(os.path.join(out, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as f:
        for path in assets:
            f.write(f"{sha256(path)}  {os.path.basename(path)}\n")
    for path in assets:
        print(f"{os.path.basename(path):<40} {os.path.getsize(path) / 1e6:8.2f} MB")
    print(f"source: {args.ref} with JUCE {juce_sha[:12]}")


if __name__ == "__main__":
    main()
