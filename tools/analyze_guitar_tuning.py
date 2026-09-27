"""Find and measure every open string in a guitar-tuning recording.

Method (built from what the first batch taught us):
1. Pluck onsets from positive spectral flux.
2. At each pluck, compare the spectrum just before and just after: partials that
   newly appear belong to the string just plucked, even when its fundamental
   hides under another string's harmonic.
3. The plucked string's f0 is the frequency whose harmonic series best explains
   the newly appeared partials.
4. Plucks with the same f0 are merged into one string, which is then measured
   two ways over long windows once it has settled: its fundamental (the batch
   convention) and its overtones (partial n / n), so disagreement is visible.

Usage: python analyze_guitar_tuning.py recording.wav

Reliability (validated 2026-09-26 on the batch-1 tunings 5 and 7, whose strings
were established by independent forensic review): it recovered most strings,
including masked ones, but it can report a string an octave high when its 2nd
harmonic dominates, it missed one string, and speech before the plucks shows up
as spurious one-pluck "strings". Treat its output as a lead, not a result, and
confirm every string with band-limited tracking at the pluck times.
"""

import math
import sys
import wave

import numpy as np

SR_EXPECTED = 48000
FMIN, FMAX = 50.0, 450.0


def load(path):
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    return sr, x


def cents(a, b):
    return 1200 * math.log2(a / b)


def spectrum(x, sr, pad=16):
    n = len(x)
    nfft = 1 << (int(math.ceil(math.log2(n))) + int(math.log2(pad)))
    s = np.abs(np.fft.rfft(x * np.hanning(n), nfft))
    return s, np.fft.rfftfreq(nfft, 1 / sr)


def peak_near(spec, freqs, f, tol_cents):
    """Interpolated peak (freq, dB) within +/- tol_cents of f."""
    lo, hi = f * 2 ** (-tol_cents / 1200), f * 2 ** (tol_cents / 1200)
    idx = np.where((freqs >= lo) & (freqs <= hi))[0]
    if len(idx) < 3:
        return None
    i = idx[np.argmax(spec[idx])]
    if i <= 0 or i >= len(spec) - 1:
        return None
    a, b, g = (np.log(spec[j] + 1e-12) for j in (i - 1, i, i + 1))
    d = 0.5 * (a - g) / (a - 2 * b + g) if (a - 2 * b + g) != 0 else 0.0
    return (i + d) * (freqs[1] - freqs[0]), 20 * np.log10(spec[i] + 1e-12)


def onsets(x, sr):
    """Pluck onsets: strong positive spectral flux in the guitar band (70-3000 Hz)."""
    n, hop = 4096, 512
    win = np.hanning(n)
    freqs = np.fft.rfftfreq(n, 1 / sr)
    band = (freqs >= 70) & (freqs <= 3000)
    frames = range(0, len(x) - n, hop)
    mags = np.array([np.abs(np.fft.rfft(x[i:i + n] * win))[band] for i in frames])
    logm = np.log1p(mags * 10)
    flux = np.maximum(logm[1:] - logm[:-1], 0).sum(axis=1)
    flux = np.convolve(flux, np.ones(3) / 3, mode="same")
    peaks = [k for k in range(1, len(flux) - 1) if flux[k] >= flux[k - 1] and flux[k] >= flux[k + 1]]
    strong = np.percentile(flux[peaks], 95) if peaks else 0
    thresh = max(np.median(flux) + 6 * np.median(np.abs(flux - np.median(flux))), 0.25 * strong)
    times, last = [], -1.0
    for k in peaks:
        t = (k + 1) * hop / sr
        if flux[k] > thresh and t - last > 0.3:
            times.append((t, float(flux[k])))
            last = t
    return times


def risen_partials(x, sr, t):
    """Peaks (Hz, rise dB, post level dB) that appear at a pluck."""
    pre = x[max(0, int((t - 0.45) * sr)):int((t - 0.03) * sr)]
    post = x[int((t + 0.06) * sr):int((t + 0.48) * sr)]
    if len(pre) < 2000 or len(post) < 2000:
        return []
    m = min(len(pre), len(post))
    s0, f = spectrum(pre[-m:], sr, pad=8)
    s1, _ = spectrum(post[:m], sr, pad=8)
    d0, d1 = 20 * np.log10(s0 + 1e-9), 20 * np.log10(s1 + 1e-9)
    top = d1.max()
    out = []
    band = (f > FMIN * 0.95) & (f < 2600)
    for i in np.where(band)[0][1:-1]:
        if d1[i] >= d1[i - 1] and d1[i] > d1[i + 1] and d1[i] > top - 40 and d1[i] - d0[i] > 10:
            out.append((f[i], d1[i] - d0[i], d1[i]))
    return out


def best_f0(peaks):
    """f0 in [FMIN, FMAX] whose harmonic series best explains the risen peaks.

    Each candidate is scored by the rise of the harmonics it explains, scaled by
    the fraction of its expected harmonics (k <= 8, below 2600 Hz) that actually
    rose. That fraction is what stops sub-octave candidates, whose extra
    harmonics are missing, from winning. The fundamental or 2nd harmonic must
    itself have risen.
    """
    if not peaks:
        return None, 0
    best, best_score = None, 0.0
    for fp, _, _ in peaks:
        for n in range(1, 7):
            f0 = fp / n
            if not FMIN <= f0 <= FMAX:
                continue
            expected = [k for k in range(1, 9) if k * f0 <= 2600]
            hit = {}
            for gp, grise, _ in peaks:
                k = round(gp / f0)
                if k in expected and abs(cents(gp, k * f0)) < 25:
                    hit[k] = max(hit.get(k, 0), grise)
            if 1 not in hit and 2 not in hit:
                continue
            score = sum(r / math.sqrt(k) for k, r in hit.items()) * (len(hit) / len(expected))
            if score > best_score:
                best, best_score = f0, score
    return best, best_score


def measure(x, sr, f0, starts):
    """Settled fundamental and overtone estimates, 0.5-3.5 s after each pluck.

    Windows are fixed rather than cut at the next onset: other strings plucked in
    between add their own peaks, but the searches are narrow bands around n*f0.
    """
    dur = len(x) / sr
    for _ in range(2):  # refine f0 once from the first pass
        fund, over = [], []
        for a in starts:
            a, b = a + 0.5, min(dur, a + 3.5)
            if b - a < 1.0:
                continue
            s, f = spectrum(x[int(a * sr):int(b * sr)], sr, pad=32)
            p = peak_near(s, f, f0, 30)
            if p:
                fund.append(p[0])
            for n in range(2, 7):
                q = peak_near(s, f, n * f0, 20)
                if q:
                    over.append(q[0] / n)
        if fund:
            f0 = float(np.median(fund))
    fund_f = float(np.median(fund)) if fund else None
    over_f = float(np.median(over)) if over else None
    return fund_f, over_f, len(fund)


def main():
    sr, x = load(sys.argv[1])
    print(f"{len(x) / sr:.2f} s at {sr} Hz")
    ons = onsets(x, sr)
    print(f"\n{len(ons)} onsets: " + ", ".join(f"{t:.2f}" for t, _ in ons))

    print("\nPer-pluck string detection (partials that newly appear):")
    plucks = []
    for t, flux in ons:
        pk = risen_partials(x, sr, t)
        f0, score = best_f0(pk)
        if f0:
            plucks.append((t, f0, score, len(pk)))
            print(f"  {t:6.2f} s  f0 ~ {f0:8.2f} Hz  (score {score:6.1f}, {len(pk)} risen partials)")
        else:
            print(f"  {t:6.2f} s  (no pitched partials appeared)")

    # Group plucks into strings: same f0 within 25 cents.
    strings = []
    for t, f0, score, _ in sorted(plucks, key=lambda p: -p[2]):
        if score < 8:
            continue
        for s in strings:
            if abs(cents(f0, s["f0"])) < 30:
                s["times"].append(t)
                break
        else:
            strings.append({"f0": f0, "times": [t]})
    strings.sort(key=lambda s: s["f0"])

    print("\nStrings (settled measurements):")
    for s in strings:
        starts = sorted(s["times"])
        fund, over, n = measure(x, sr, s["f0"], starts)
        gap = cents(over, fund) if fund and over else float("nan")
        fund_s = f"{fund:8.3f}" if fund else "    n/a "
        over_s = f"{over:8.3f}" if over else "    n/a "
        print(f"  f0 ~ {s['f0']:7.2f}  plucked at {', '.join(f'{t:.2f}' for t in starts):<22}"
              f" fundamental {fund_s} Hz   overtones/n {over_s} Hz   gap {gap:+5.1f} c  ({n} windows)")


if __name__ == "__main__":
    main()
