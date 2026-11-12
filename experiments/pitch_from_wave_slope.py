"""Pitch amplitude from wave height, period, and boat length.

Math: docs/portfolio/preliminary-simulations/pitch-from-wave-slope.md
Each row is its own assumed sea. Heights are not a measured lake state.

Run from the repo root:
    python docs/portfolio/preliminary-simulations/pitch_from_wave_slope.py
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

G = 9.81
BOAT_LENGTH_M = 7.0
HORIZONS_S = (0.3, 0.5)
SAMPLE_DT_S = 0.01

# name, crest-to-trough height m, period s
SEAS = (
    ("Small wind wave", 0.3, 3.0),
    ("Moderate wind wave", 0.5, 4.0),
    ("Short chop", 0.5, 1.0),
)

OUT_DIR = Path(__file__).resolve().parent


def wavelength_m(period_s: float) -> float:
    return G * period_s * period_s / (2.0 * math.pi)


def pitch_amplitude_rad(height_m: float, period_s: float, boat_length_m: float = BOAT_LENGTH_M) -> float:
    """(H / Lb) * |sin(pi Lb / L)|. See the markdown note."""
    length = wavelength_m(period_s)
    return (height_m / boat_length_m) * abs(math.sin(math.pi * boat_length_m / length))


def pitch_deg(t: float, amplitude_deg: float, period_s: float) -> float:
    return amplitude_deg * math.cos(2.0 * math.pi * t / period_s)


def constant_rate_error_deg(amplitude_deg: float, period_s: float, horizon_s: float) -> tuple[float, float]:
    """Release at a crest. Rate is ~0, so the rate model stays at +amplitude."""
    truth = pitch_deg(horizon_s, amplitude_deg, period_s)
    predicted = amplitude_deg
    return truth, predicted - truth


def main() -> None:
    lines = [
        f"Boat length {BOAT_LENGTH_M:.1f} m. Deep water. Head seas. Each row is a separate assumed sea.",
        f"{'sea':<22} {'H m':>6} {'T s':>6} {'L m':>8} {'pitch deg':>10} "
        f"{'truth 0.3':>10} {'err 0.3':>8} {'truth 0.5':>10} {'err 0.5':>8}",
    ]
    rows = []
    for name, height, period in SEAS:
        wave_l = wavelength_m(period)
        amp = math.degrees(pitch_amplitude_rad(height, period))
        truth_03, err_03 = constant_rate_error_deg(amp, period, HORIZONS_S[0])
        truth_05, err_05 = constant_rate_error_deg(amp, period, HORIZONS_S[1])
        rows.append((name, height, period, wave_l, amp))
        lines.append(
            f"{name:<22} {height:6.2f} {period:6.1f} {wave_l:8.2f} {amp:10.2f} "
            f"{truth_03:10.2f} {err_03:8.2f} {truth_05:10.2f} {err_05:8.2f}"
        )
    lines.append("")
    lines.append("truth 0.3 / truth 0.5: pitch degrees after a release at the crest.")
    lines.append("err: constant-rate prediction minus truth. The rate model holds the crest angle.")
    text = "\n".join(lines) + "\n"
    results_path = OUT_DIR / "results.txt"
    results_path.write_text(text, encoding="utf-8")
    print(text, end="")
    print(f"wrote {results_path}")

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharey=False)
    for ax, (name, height, period, wave_l, amp) in zip(axes, rows):
        t_end = 2.0 * period
        n = int(t_end / SAMPLE_DT_S)
        times = [i * SAMPLE_DT_S for i in range(n + 1)]
        values = [pitch_deg(t, amp, period) for t in times]
        ax.plot(times, values, color="black", linewidth=1.3)
        ax.axhline(amp, color="0.6", linewidth=0.6, linestyle=":")
        ax.axhline(-amp, color="0.6", linewidth=0.6, linestyle=":")
        ax.axvline(0.0, color="0.35", linewidth=0.8, linestyle="--")
        for horizon in HORIZONS_S:
            ax.plot(horizon, pitch_deg(horizon, amp, period), "k.", markersize=6)
        ax.set_title(f"{name}\nH={height:.1f} m, T={period:.0f} s, L={wave_l:.1f} m\npitch ±{amp:.1f}°")
        ax.set_xlabel("time from crest (s)")
        ax.grid(True, linewidth=0.4, alpha=0.5)
    axes[0].set_ylabel("pitch (deg)")
    fig.suptitle(f"Head-sea pitch on a {BOAT_LENGTH_M:.0f} m boat  |  dashed line is a crest release")
    fig.tight_layout()
    figure_path = OUT_DIR / "pitch-from-wave-slope.png"
    fig.savefig(figure_path, dpi=140)
    print(f"wrote {figure_path}")


if __name__ == "__main__":
    main()
