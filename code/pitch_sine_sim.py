"""Pitch gate v2.1: two-cosine forecast, with and without a margin and slow stabilization.

The forecast is the time-only form of Sears (2026, Chapter 4): two cosines,
amplitudes, frequencies, and phases fit on a few seconds of pitch. Frequencies
are taken from the sample spectrum, not handed to the fit.

The truth trace is synthetic and harder than the model:
  - the 1 s chop and 3 s wind wave from the head-sea pitch table are each spread
    over several nearby periods with random phases, so the amplitude drifts;
  - a 6 s swell is added that the two-cosine fit is not told about;
  - the gate only sees the rail through 0.3° of IMU noise.
Launch elevation is rail pitch plus a 5° set angle, the middle of the 0–10° band.

Four cases are scored:
  - forecast only: the rail is fixed to the hull;
  - forecast + margin: the gate allows only if the prediction stays 1.5° inside the band;
  - slow stabilization: an actuator tilts the rail against motion of 2 s period
    and longer, leaving an assumed 20% of it. The chop is left for the forecast;
  - slow stabilization + margin.
The 20% residual is assumed until the actuator and mount are chosen.

At every release time over 60 s, the gate predicts the launch elevation over the
rail time (2 m at 15 m/s, 0.27 s). It is scored against the true trace:
  - false allow: the gate allowed, the true elevation left the 0–10° band;
  - missed window: the gate refused, the true elevation stayed in the band.

Run from the repo root:
    python software/pitch_sine_sim.py
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

G = 9.81
BOAT_LENGTH_M = 6.90
SET_ANGLE_DEG = 5.0
BAND = (0.0, 10.0)
MARGIN_DEG = 1.5
RAIL_M = 2.0
EXIT_SPEED_MS = 15.0
HORIZON_S = 2.0 * RAIL_M / EXIT_SPEED_MS
PRIOR_S = 6.0
SAMPLE_DT_S = 0.01
IMU_NOISE_DEG = 0.3
RATE_WINDOW_S = 0.1
SCORED_S = 60.0
STEP_S = 0.05
N_TONES = 2
SEED = 403

# name, crest-to-trough height m, period s. Same rows as pitch_from_wave_slope.py.
COMPONENTS = (
    ("Short chop", 0.50, 1.0),
    ("Small wind wave", 0.30, 3.0),
)
SPREAD = 0.08
N_SPREAD = 5
SWELL = ("Swell, not fit", 0.20, 6.0)
SLOW_PERIOD_S = 2.0
STABILIZER_RESIDUAL = 0.20

CASES = (
    ("forecast only", False, 0.0),
    ("forecast + margin", False, MARGIN_DEG),
    ("slow stabilization", True, 0.0),
    ("slow stab. + margin", True, MARGIN_DEG),
)

ROOT = Path(__file__).resolve().parents[1]
OUT_PATHS = (
    Path(__file__).with_name("pitch_sine_sim_v2.1.png"),
    ROOT / "docs" / "portfolio" / "preliminary-simulations" / "pitch-forecast-v2.1.png",
)


def wavelength_m(period_s: float) -> float:
    return G * period_s * period_s / (2.0 * math.pi)


def pitch_amplitude_deg(height_m: float, period_s: float) -> float:
    length = wavelength_m(period_s)
    radians = (height_m / BOAT_LENGTH_M) * abs(math.sin(math.pi * BOAT_LENGTH_M / length))
    return math.degrees(radians)


def wave_components(rng: np.random.Generator) -> list[tuple[float, float, float]]:
    """(amplitude deg, period s, phase rad). Each table row keeps its RMS when spread."""
    parts = []
    offsets = np.linspace(-SPREAD, SPREAD, N_SPREAD)
    weights = np.exp(-0.5 * (offsets / (SPREAD / 2.0)) ** 2)
    weights = weights / np.sqrt(np.sum(weights**2))
    for _, height, period in COMPONENTS:
        amplitude = pitch_amplitude_deg(height, period)
        for offset, weight in zip(offsets, weights):
            parts.append((amplitude * weight, period * (1.0 + offset), rng.uniform(0, 2 * math.pi)))
    _, height, period = SWELL
    parts.append((pitch_amplitude_deg(height, period), period, rng.uniform(0, 2 * math.pi)))
    return parts


def launch_trace(times: np.ndarray, parts: list[tuple[float, float, float]], stabilized: bool) -> np.ndarray:
    total = np.full_like(times, SET_ANGLE_DEG)
    for amplitude, period, phase in parts:
        if stabilized and period >= SLOW_PERIOD_S:
            amplitude = amplitude * STABILIZER_RESIDUAL
        total = total + amplitude * np.cos(2.0 * math.pi * times / period + phase)
    return total


def dominant_frequencies(times: np.ndarray, samples: np.ndarray, n_freq: int = N_TONES) -> tuple[float, ...]:
    """Strongest cycles in the prior window, DC removed."""
    y = samples - np.mean(samples)
    y = y * np.hanning(len(y))
    dt = float(times[1] - times[0])
    spectrum = np.abs(np.fft.rfft(y))
    freqs = np.fft.rfftfreq(len(y), dt)
    spectrum[0] = 0.0
    df = float(freqs[1] - freqs[0])
    found: list[float] = []
    for _ in range(n_freq):
        index = int(np.argmax(spectrum))
        if spectrum[index] <= 0.0:
            break
        if 0 < index < len(spectrum) - 1:
            left, mid, right = spectrum[index - 1], spectrum[index], spectrum[index + 1]
            denom = left - 2.0 * mid + right
            shift = 0.5 * (left - right) / denom if denom != 0.0 else 0.0
        else:
            shift = 0.0
        found.append(float(freqs[index] + shift * df))
        half = max(1, int(0.2 / df))
        spectrum[max(0, index - half) : index + half + 1] = 0.0
    return tuple(sorted(found))


def fit_cosines(times: np.ndarray, samples: np.ndarray, frequencies: tuple[float, ...]) -> np.ndarray:
    """Each frequency gets a sine column and a cosine column, plus a constant."""
    columns = [np.ones_like(times)]
    for frequency in frequencies:
        omega = 2.0 * math.pi * frequency
        columns.append(np.sin(omega * times))
        columns.append(np.cos(omega * times))
    coef, *_ = np.linalg.lstsq(np.column_stack(columns), samples, rcond=None)
    return coef


def predict(t: np.ndarray, frequencies: tuple[float, ...], coef: np.ndarray) -> np.ndarray:
    total = np.full_like(t, coef[0], dtype=float)
    for i, frequency in enumerate(frequencies):
        omega = 2.0 * math.pi * frequency
        total = total + coef[2 * i + 1] * np.sin(omega * t) + coef[2 * i + 2] * np.cos(omega * t)
    return total


def constant_rate(times: np.ndarray, samples: np.ndarray, future: np.ndarray) -> np.ndarray:
    """Rate from a line through the last 0.1 s, so the noise does not set the slope."""
    n = max(2, int(round(RATE_WINDOW_S / SAMPLE_DT_S)) + 1)
    slope, intercept = np.polyfit(times[-n:], samples[-n:], 1)
    return intercept + slope * future


def in_band(values: np.ndarray, margin: float = 0.0) -> bool:
    low, high = BAND
    return bool(np.all((values >= low + margin) & (values <= high - margin)))


def score(times: np.ndarray, truth: np.ndarray, measured: np.ndarray) -> dict:
    """Gate decisions at every release time, with and without the margin."""
    n_prior = int(round(PRIOR_S / SAMPLE_DT_S))
    n_horizon = int(round(HORIZON_S / SAMPLE_DT_S))
    n_step = int(round(STEP_S / SAMPLE_DT_S))
    release_idx = np.arange(n_prior, n_prior + int(round(SCORED_S / SAMPLE_DT_S)) + 1, n_step)

    safe, forecast, rate = [], [], []
    for i in release_idx:
        past_t = times[i - n_prior : i + 1]
        past_y = measured[i - n_prior : i + 1]
        future_t = times[i : i + n_horizon + 1]
        frequencies = dominant_frequencies(past_t, past_y)
        coef = fit_cosines(past_t, past_y, frequencies)
        safe.append(in_band(truth[i : i + n_horizon + 1]))
        forecast.append(predict(future_t, frequencies, coef))
        rate.append(constant_rate(past_t, past_y, future_t))
    return {"release_t": times[release_idx], "safe": np.array(safe), "forecast": forecast, "rate": rate}


def run() -> dict:
    rng = np.random.default_rng(SEED)
    parts = wave_components(rng)
    total_s = PRIOR_S + SCORED_S + HORIZON_S + SAMPLE_DT_S
    times = np.arange(int(round(total_s / SAMPLE_DT_S)) + 1) * SAMPLE_DT_S
    noise = rng.normal(0.0, IMU_NOISE_DEG, size=times.shape)

    traces, scored = {}, {}
    for stabilized in (False, True):
        truth = launch_trace(times, parts, stabilized)
        traces[stabilized] = truth
        scored[stabilized] = score(times, truth, truth + noise)

    print(f"Hull {BOAT_LENGTH_M:.2f} m, rail {RAIL_M:.0f} m at {EXIT_SPEED_MS:.0f} m/s -> horizon {HORIZON_S:.2f} s.")
    print(f"Fit {N_TONES} cosines on {PRIOR_S:.0f} s of pitch with {IMU_NOISE_DEG}° IMU noise. Band {BAND[0]:.0f}–{BAND[1]:.0f}°.")
    print(f"Margin {MARGIN_DEG}°. Stabilizer leaves {100 * STABILIZER_RESIDUAL:.0f}% of motion slower than {SLOW_PERIOD_S:.0f} s (assumed).")
    n = len(scored[False]["release_t"])
    for stabilized in (False, True):
        n_safe = int(np.sum(scored[stabilized]["safe"]))
        label = "stabilized" if stabilized else "fixed rail"
        print(f"{label}: truly safe at {n_safe} of {n} release times ({100 * n_safe / n:.0f}%).")

    print(f"{'case':<22} {'allowed':>8} {'false allow':>13} {'missed':>13}")
    rows = []
    allows = {}
    for name, stabilized, margin in CASES:
        s = scored[stabilized]
        allow = np.array([in_band(p, margin) for p in s["forecast"]])
        allows[name] = allow
        false_allow = int(np.sum(allow & ~s["safe"]))
        missed = int(np.sum(~allow & s["safe"]))
        rows.append((name, false_allow, missed))
        print(f"{name:<22} {int(np.sum(allow)):8d} {false_allow:6d} ({100 * false_allow / n:4.1f}%) {missed:6d} ({100 * missed / n:4.1f}%)")

    rate_allow = np.array([in_band(p) for p in scored[False]["rate"]])
    rate_false = int(np.sum(rate_allow & ~scored[False]["safe"]))
    rate_missed = int(np.sum(~rate_allow & scored[False]["safe"]))
    print(f"{'(hold last rate, fixed)':<22} {int(np.sum(rate_allow)):8d} {rate_false:6d} ({100 * rate_false / n:4.1f}%) {rate_missed:6d} ({100 * rate_missed / n:4.1f}%)")

    return {"times": times, "traces": traces, "rows": rows, "n": n, "release_t": scored[True]["release_t"], "allows": allows}


def plot(result: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 11})
    short_names = {
        "forecast only": "Fixed",
        "forecast + margin": "Fixed\n+ margin",
        "slow stabilization": "Stabilized",
        "slow stab. + margin": "Stabilized\n+ margin",
    }

    shown_s = 10.0
    t_start = PRIOR_S
    t_end = PRIOR_S + shown_s
    times = result["times"]
    visible = (times >= t_start) & (times <= t_end)

    fig, (ax_trace, ax_bar) = plt.subplots(1, 2, figsize=(11.0, 4.2), gridspec_kw={"width_ratios": (1.6, 1.0)})

    ax_trace.axhspan(BAND[0], BAND[1], color="0.9", zorder=0, label="safe band (0–10°)")
    release_t = result["release_t"] - t_start
    allowed = result["allows"]["slow stab. + margin"] & (release_t >= 0.0) & (release_t <= shown_s)
    for t in release_t[allowed]:
        ax_trace.axvspan(t - STEP_S / 2, t + STEP_S / 2, color="#4caf50", alpha=0.3, linewidth=0, zorder=0.5)
    ax_trace.fill_between([], [], color="#4caf50", alpha=0.3, linewidth=0, label="stabilized + margin allows")
    for edge in (BAND[0] + MARGIN_DEG, BAND[1] - MARGIN_DEG):
        ax_trace.axhline(edge, color="0.45", linewidth=0.9, linestyle="--")
    ax_trace.plot([], [], color="0.45", linewidth=0.9, linestyle="--", label=f"{MARGIN_DEG}° margin")
    shown_t = times[visible] - t_start
    ax_trace.plot(shown_t, result["traces"][False][visible], color="black", linewidth=1.3, label="fixed rail")
    ax_trace.plot(shown_t, result["traces"][True][visible], color="C0", linewidth=1.6, label="stabilized rail")
    ax_trace.set_xlim(0.0, shown_s)
    ax_trace.set_xlabel("time (s)")
    ax_trace.set_ylabel("launch elevation (deg)")
    ax_trace.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4, fontsize=9, frameon=False)
    ax_trace.spines[["top", "right"]].set_visible(False)

    names = [short_names[name] for name, _, _ in result["rows"]]
    n = result["n"]
    false_pct = [100 * fa / n for _, fa, _ in result["rows"]]
    missed_pct = [100 * m / n for _, _, m in result["rows"]]
    x = np.arange(len(names))
    width = 0.38
    bars_false = ax_bar.bar(x - width / 2, false_pct, width, color="#d32f2f", label="false allow")
    bars_missed = ax_bar.bar(x + width / 2, missed_pct, width, color="#ffb74d", label="missed window")
    for bars in (bars_false, bars_missed):
        for bar in bars:
            ax_bar.annotate(f"{bar.get_height():.0f}%", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                            ha="center", va="bottom", fontsize=9)
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(names, fontsize=9)
    ax_bar.set_ylabel("% of release times")
    ax_bar.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=9, frameon=False)
    ax_bar.set_ylim(0, max(false_pct + missed_pct) * 1.15 + 1)
    ax_bar.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    for path in OUT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=100)
        print(f"wrote {path}")


def main() -> None:
    plot(run())


if __name__ == "__main__":
    main()
