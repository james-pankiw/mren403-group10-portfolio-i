"""Live pitch-gate demo for the bench computer.

Same sea as software/pitch_sine_sim.py: seed 403, the spread 1 s chop and 3 s
wind wave, the 6 s swell the fit is not given, and 0.3° of IMU noise. The rail
is fixed. Launch elevation is hull pitch plus the 5° set angle.

The window is a dashboard. Wind is assumed OK and is not part of the gate.
A two-cosine forecast must stay 1.5° inside the 0–10° band for the next 0.5 s.
After an allow, the aircraft moves for 0.3 s. The clock then stops at 0.5 s
and the scope shows the noise-free pitch over that window.

Run on the Pi desktop, from the repo root:

    python3 software/pitch_gate_demo.py

Space bar does the same thing as the button. The window needs a display. If it
fails to open, install the Tk binding: sudo apt install python3-tk. SSH with no
desktop will not open the window.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pitch_sine_sim import (  # noqa: E402
    BAND,
    BOAT_LENGTH_M,
    IMU_NOISE_DEG,
    MARGIN_DEG,
    PRIOR_S,
    SAMPLE_DT_S,
    SEED,
    SET_ANGLE_DEG,
    STEP_S,
    constant_rate,
    dominant_frequencies,
    fit_cosines,
    in_band,
    launch_trace,
    predict,
    wave_components,
    wavelength_m,
)

HEADING_DEG = 0.0
LAUNCH_S = 0.5
FLIGHT_S = 0.3
EXIT_SPEED_MS = 15.0
NAVY = "#002452"
IMU_COLOR = "#d7ff6a"
FORECAST_COLOR = "#5ec8ff"
FORECAST_OK = "#8dff9a"
RATE_COLOR = "#b7b7b7"
TRUTH_COLOR = "#ffffff"

# Bow is +x. Overall length matches the PRO 7, 6.90 m.
HULL = np.array(
    [
        [-3.45, 0.08],
        [-3.25, -0.22],
        [-2.4, -0.42],
        [2.5, -0.42],
        [3.40, -0.12],
        [3.45, 0.10],
        [2.15, 0.30],
        [-1.6, 0.34],
        [-3.20, 0.20],
    ]
)
CONSOLE = np.array([[-0.55, 0.32], [0.35, 0.32], [0.35, 0.78], [-0.55, 0.78]])
RAIL_START = np.array([-1.15, 0.36])
RAIL_M = 2.0
# How far the aircraft travels during the 0.3 s it is on the move.
FLIGHT_RUN_M = EXIT_SPEED_MS * FLIGHT_S
# Wave height on the drawing only. The hull stays at its true proportions.
WAVE_Y_SCALE = 0.5


def wind_speed_ms(time_s: float) -> float:
    """Displayed only. Wind is assumed OK and does not arm or block a launch."""
    return 4.2 + 0.5 * math.sin(2.0 * math.pi * time_s / 13.0)


def visual_waves(parts: list[tuple[float, float, float]]) -> list[tuple[float, float, float, float]]:
    """Surface sines whose rigid-hull pitch matches the pitch-sim components.

    Each entry is (amplitude m, wavenumber, angular frequency, phase rad).
    η = a sin(kx − ωt − phase) puts the bow up when that component's cosine is +1.
    """
    waves = []
    for amp_deg, period, phase in parts:
        length = wavelength_m(period)
        sine = math.sin(math.pi * BOAT_LENGTH_M / length)
        if abs(sine) < 1e-6:
            continue
        height = math.radians(amp_deg) * BOAT_LENGTH_M / abs(sine)
        waves.append((height / 2.0, 2.0 * math.pi / length, 2.0 * math.pi / period, phase))
    return waves


def eta(x: np.ndarray, time_s: float, waves: list[tuple[float, float, float, float]]) -> np.ndarray:
    level = np.zeros_like(x, dtype=float)
    for amplitude, wavenumber, omega, phase in waves:
        level = level + amplitude * np.sin(wavenumber * x - omega * time_s - phase)
    return level


def rotate(points: np.ndarray, angle_deg: float, origin: np.ndarray) -> np.ndarray:
    """Positive angle raises the bow (+x) — bow up is positive pitch."""
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    shifted = points - origin
    rotated = np.column_stack(
        [
            cos_a * shifted[:, 0] - sin_a * shifted[:, 1],
            sin_a * shifted[:, 0] + cos_a * shifted[:, 1],
        ]
    )
    return rotated + origin


class PitchRig:
    """Fixed-rail sea, IMU buffer, and the pitch-sim gate."""

    def __init__(self) -> None:
        rng = np.random.default_rng(SEED)
        self.parts = wave_components(rng)
        self.waves = visual_waves(self.parts)
        self.rng = rng
        n_prior = int(round(PRIOR_S / SAMPLE_DT_S))
        indices = np.arange(-n_prior, 1)
        self.times = indices * SAMPLE_DT_S
        self.truth = launch_trace(self.times, self.parts, False)
        self.measured = self.truth + rng.normal(0.0, IMU_NOISE_DEG, size=indices.shape)
        self.state = "disarmed"
        self.forecast = np.array([])
        self.rate = np.array([])
        self.future_t = np.array([])
        self.fit_t = np.array([])
        self.fit_y = np.array([])
        self.release_t: float | None = None
        self.release_forecast = np.array([])
        self.release_future_t = np.array([])
        self.release_rate = np.array([])
        self.release_fit_t = np.array([])
        self.release_fit_y = np.array([])

    def now(self) -> float:
        return float(self.times[-1])

    def advance(self) -> None:
        n_step = int(round(STEP_S / SAMPLE_DT_S))
        cursor = int(round(self.now() / SAMPLE_DT_S))
        new_t = (np.arange(cursor + 1, cursor + n_step + 1)) * SAMPLE_DT_S
        new_truth = launch_trace(new_t, self.parts, False)
        self.times = np.concatenate([self.times, new_t])
        self.truth = np.concatenate([self.truth, new_truth])
        self.measured = np.concatenate(
            [self.measured, new_truth + self.rng.normal(0.0, IMU_NOISE_DEG, size=new_t.shape)]
        )
        keep = int(round((PRIOR_S + 2.0) / SAMPLE_DT_S))
        if self.times.size > keep + 400:
            self.times = self.times[-keep:]
            self.truth = self.truth[-keep:]
            self.measured = self.measured[-keep:]

    def evaluate(self) -> bool:
        """Fit the gate on the last 6 s. True when the forecast stays inside the margin."""
        n_prior = int(round(PRIOR_S / SAMPLE_DT_S))
        n_horizon = int(round(LAUNCH_S / SAMPLE_DT_S))
        past_t = self.times[-n_prior - 1 :]
        past_y = self.measured[-n_prior - 1 :]
        self.future_t = self.now() + np.arange(n_horizon + 1) * SAMPLE_DT_S
        frequencies = dominant_frequencies(past_t, past_y)
        coef = fit_cosines(past_t, past_y, frequencies)
        self.forecast = predict(self.future_t, frequencies, coef)
        self.rate = constant_rate(past_t, past_y, self.future_t)
        self.fit_t = np.concatenate([past_t, self.future_t[1:]])
        self.fit_y = predict(self.fit_t, frequencies, coef)
        return in_band(self.forecast, MARGIN_DEG)

    def hull_pitch_deg(self) -> float:
        return float(self.truth[-1] - SET_ANGLE_DEG)

    def launch_elapsed(self) -> float:
        if self.release_t is None:
            return 0.0
        return self.now() - self.release_t

    def aircraft_along(self) -> float:
        """Tail position along the rail. Motion lasts FLIGHT_S, then the aircraft holds."""
        if self.release_t is None or self.state not in ("launching", "paused"):
            return 0.15
        frac = min(1.0, max(0.0, self.launch_elapsed() / FLIGHT_S))
        return 0.15 + frac * (FLIGHT_RUN_M - 0.15)

    def truth_in_launch(self) -> tuple[np.ndarray, np.ndarray]:
        """Noise-free elevation from the allow through the 0.5 s window."""
        if self.release_t is None:
            return np.array([]), np.array([])
        end = min(self.now(), self.release_t + LAUNCH_S)
        mask = (self.times >= self.release_t) & (self.times <= end + 1e-9)
        return self.times[mask], self.truth[mask]

    def begin_launch(self) -> None:
        self.state = "launching"
        self.release_t = self.now()
        self.release_forecast = self.forecast.copy()
        self.release_future_t = self.future_t.copy()
        self.release_rate = self.rate.copy()
        self.release_fit_t = self.fit_t.copy()
        self.release_fit_y = self.fit_y.copy()

    def step_armed(self) -> None:
        """Advance one tick. An allow starts a 0.3 s flight and a stop at 0.5 s."""
        if self.state == "paused":
            return
        self.advance()
        if self.state == "launching":
            if self.now() >= self.release_t + LAUNCH_S - 0.5 * SAMPLE_DT_S:
                self.state = "paused"
            return
        pitch_ok = self.evaluate()
        if self.state == "armed" and pitch_ok:
            self.begin_launch()


def hold_reason(pitch_ok: bool) -> str:
    if pitch_ok:
        return "window open"
    return "holding for pitch"


def uav_polygon(along_rail_m: float) -> np.ndarray:
    """Side silhouette in hull axes. `along_rail_m` is where the tail sits on the rail line."""
    angle = math.radians(SET_ANGLE_DEG)
    direction = np.array([math.cos(angle), math.sin(angle)])
    normal = np.array([-math.sin(angle), math.cos(angle)])
    tail = RAIL_START + direction * along_rail_m
    nose = tail + direction * 1.7
    return np.vstack(
        [
            nose,
            nose - direction * 0.40 + normal * 0.16,
            tail + direction * 0.25 + normal * 0.10,
            tail + normal * 0.12,
            tail - direction * 0.22 + normal * 0.46,
            tail + normal * 0.02,
            tail - normal * 0.10,
            nose - direction * 0.25 - normal * 0.08,
        ]
    )


def hold_start_time(min_hold_s: float = 2.5) -> float:
    """Sim time where a refuse lasts at least min_hold_s, so Arm does not fire at once."""
    scout = PitchRig()
    refused_from = None
    while scout.now() < 80.0:
        scout.advance()
        if scout.evaluate():
            refused_from = None
        elif refused_from is None:
            refused_from = scout.now()
        elif scout.now() - refused_from >= min_hold_s:
            return refused_from
    return 0.0


def park_at_hold(rig: PitchRig | None = None) -> PitchRig:
    """Leave the rig at the start of that refuse, with 6 s of IMU history behind it."""
    target = hold_start_time()
    rig = PitchRig() if rig is None else rig
    while rig.now() < target - 1e-9:
        rig.advance()
    rig.evaluate()
    return rig


def first_launch_time(max_s: float = 90.0) -> float | None:
    """Arm during a refuse. Return the sim time of the pause, if any."""
    rig = park_at_hold()
    rig.state = "armed"
    steps = int(round(max_s / STEP_S))
    for _ in range(steps):
        rig.step_armed()
        if rig.state == "paused":
            return rig.now()
    return None


def build_figure(rig: PitchRig):
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Button

    plt.rcParams.update({"font.size": 11, "font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(12.8, 7.2), facecolor="#eef2f6")
    fig.canvas.manager.set_window_title("Pitch gate demo — MREN 403")

    header = fig.add_axes([0.0, 0.90, 1.0, 0.10])
    header.set_xlim(0, 1)
    header.set_ylim(0, 1)
    header.set_axis_off()
    header.add_patch(plt.Rectangle((0, 0), 1, 1, color=NAVY, transform=header.transAxes, zorder=0))

    ax_btn = fig.add_axes([0.018, 0.922, 0.12, 0.056])
    button = Button(ax_btn, "Arm launch", color="#c5962c", hovercolor="#e0b84a")
    button.label.set_color(NAVY)
    button.label.set_fontweight("bold")

    labels = {}
    fields = (
        ("wind", 0.20, "Wind"),
        ("heading", 0.36, "Heading"),
        ("direction", 0.54, "Wind gate"),
        ("pitch", 0.72, "Pitch"),
        ("state", 0.88, "Gate"),
    )
    for key, x, name in fields:
        header.text(x, 0.68, name, color="#9eb0c8", fontsize=9, ha="center", va="center", transform=header.transAxes)
        labels[key] = header.text(
            x, 0.32, "—", color="white", fontsize=14, fontweight="bold", ha="center", va="center", transform=header.transAxes
        )

    boat = fig.add_axes([0.04, 0.40, 0.92, 0.46])
    scope = fig.add_axes([0.07, 0.08, 0.88, 0.28])
    scope.set_facecolor("#12171c")
    for spine in scope.spines.values():
        spine.set_color("#3d4a58")
    scope.tick_params(colors="#1a2330")
    scope.grid(True, color="#2a3542", linewidth=0.6)
    scope.axhspan(BAND[0], BAND[1], color="#163226", zorder=0)
    scope.axhline(BAND[0] + MARGIN_DEG, color="#8fd18a", linewidth=0.8, linestyle="--")
    scope.axhline(BAND[1] - MARGIN_DEG, color="#8fd18a", linewidth=0.8, linestyle="--")
    scope.axvspan(0.0, LAUNCH_S, color="#1a3044", zorder=0)
    scope.axvline(0.0, color="#f2f2f2", linewidth=0.8)
    imu_line, = scope.plot([], [], color=IMU_COLOR, linewidth=1.4, label="recorded")
    forecast_line, = scope.plot([], [], color=FORECAST_COLOR, linewidth=2.2, label="predicted")
    rate_line, = scope.plot([], [], color=RATE_COLOR, linewidth=1.2, linestyle="--", label="hold last rate")
    truth_line, = scope.plot([], [], color=TRUTH_COLOR, linewidth=2.4, label="true pitch")
    scope.set_xlim(-PRIOR_S, LAUNCH_S + 0.15)
    scope.set_ylim(-4.0, 16.0)
    scope.set_xticks([-6, -4, -2, 0, LAUNCH_S])
    scope.set_xticklabels(["−6 s", "−4", "−2", "now", f"{LAUNCH_S:.1f} s"])
    scope.set_ylabel("launch elevation (deg)", color="#1a2330")
    scope.text(0.01, 0.06, "dashed lines: 1.5° margin inside 0–10°", transform=scope.transAxes, color="#8fd18a", fontsize=8)
    scope.legend(
        loc="upper left",
        fontsize=8,
        frameon=True,
        facecolor="#1b222a",
        edgecolor="#3d4a58",
        labelcolor="#e8eef4",
    )
    note = scope.text(
        0.99,
        0.95,
        "",
        transform=scope.transAxes,
        ha="right",
        va="top",
        color="white",
        fontsize=11,
        fontweight="bold",
    )
    fig.text(
        0.04,
        0.015,
        "Synthetic head seas, fixed rail, 0.3° IMU noise. Same model as pitch_sine_sim.py. Not a hull log. Wind is assumed OK and is not a gate.",
        color="#3d4a5c",
        fontsize=8,
    )

    demo = {
        "fig": fig,
        "button": button,
        "labels": labels,
        "boat": boat,
        "scope_lines": (imu_line, forecast_line, rate_line, truth_line),
        "note": note,
        "rig": rig,
    }

    def paint() -> None:
        now = rig.now()
        pitch_ok = bool(rig.forecast.size) and in_band(rig.forecast, MARGIN_DEG)
        labels["wind"].set_text(f"{wind_speed_ms(now):.1f} m/s")
        labels["heading"].set_text(f"{HEADING_DEG:03.0f}°")
        labels["direction"].set_text("assumed OK")
        labels["direction"].set_color("#8dff9a")
        if rig.state == "paused":
            labels["pitch"].set_text(f"true {rig.truth[-1]:+.1f}°")
            labels["state"].set_text("TRUE PITCH")
            labels["state"].set_color("#ffffff")
        else:
            labels["pitch"].set_text(f"{rig.measured[-1]:+.1f}°")
            if rig.state == "launching":
                labels["state"].set_text("LAUNCH")
                labels["state"].set_color("#8dff9a")
            elif rig.state == "armed":
                labels["state"].set_text("ARMED")
                labels["state"].set_color("#f0d78c")
            else:
                labels["state"].set_text("DISARMED")
                labels["state"].set_color("#d5dde6")

        _draw_boat(boat, rig)
        if rig.state == "armed":
            boat.text(
                0.02,
                0.95,
                "ARMED — " + hold_reason(pitch_ok),
                transform=boat.transAxes,
                ha="left",
                va="top",
                fontsize=13,
                fontweight="bold",
                color="#8a6a12",
            )
        elif rig.state == "launching":
            boat.text(
                0.02,
                0.95,
                f"LAUNCHING — aircraft moves for {FLIGHT_S:.1f} s",
                transform=boat.transAxes,
                ha="left",
                va="top",
                fontsize=14,
                fontweight="bold",
                color="#0d6b2c",
            )
        elif rig.state == "paused":
            boat.text(
                0.02,
                0.95,
                f"TRUE PITCH {rig.truth[-1]:+.1f}° at {LAUNCH_S:.1f} s",
                transform=boat.transAxes,
                ha="left",
                va="top",
                fontsize=14,
                fontweight="bold",
                color="#0d6b2c",
            )

        rel_past = rig.times - now
        visible = rel_past >= -PRIOR_S
        imu_line.set_data(rel_past[visible], rig.measured[visible])
        _, _, _, truth_line = demo["scope_lines"]
        if rig.release_t is not None:
            forecast_line.set_data(rig.release_fit_t - now, rig.release_fit_y)
            rate_line.set_data(rig.release_future_t - now, rig.release_rate)
            forecast_line.set_color(FORECAST_OK)
            forecast_line.set_linewidth(2.4)
            truth_t, truth_y = rig.truth_in_launch()
            truth_line.set_data(truth_t - now, truth_y)
            low, high = float(np.min(rig.release_forecast)), float(np.max(rig.release_forecast))
            true_now = float(truth_y[-1]) if truth_y.size else float(rig.truth[-1])
            if rig.state == "paused":
                note.set_text(f"true pitch {true_now:+.1f}°   forecast {low:.1f}° to {high:.1f}°")
                note.set_color(TRUTH_COLOR)
            else:
                note.set_text(f"launching   forecast {low:.1f}° to {high:.1f}° over {LAUNCH_S:.1f} s")
                note.set_color(FORECAST_OK)
        elif rig.forecast.size:
            truth_line.set_data([], [])
            forecast_line.set_data(rig.fit_t - now, rig.fit_y)
            rate_line.set_data(rig.future_t - now, rig.rate)
            forecast_line.set_color(FORECAST_OK if pitch_ok else FORECAST_COLOR)
            forecast_line.set_linewidth(2.2)
            low, high = float(np.min(rig.forecast)), float(np.max(rig.forecast))
            word = "inside margin" if pitch_ok else "outside margin"
            note.set_text(f"{word}   {low:.1f}° to {high:.1f}°   over {LAUNCH_S:.1f} s")
            note.set_color(FORECAST_OK if pitch_ok else "white")

    def on_button(_event) -> None:
        if rig.state == "paused":
            rig.state = "disarmed"
            rig.release_t = None
            button.label.set_text("Arm launch")
            button.ax.set_facecolor("#c5962c")
            demo["anim"].event_source.start()
        elif rig.state == "disarmed":
            rig.state = "armed"
            button.label.set_text("Armed")
            button.ax.set_facecolor("#e7c56a")
        fig.canvas.draw_idle()

    def on_key(event) -> None:
        if event.key == " ":
            on_button(None)

    button.on_clicked(on_button)
    fig.canvas.mpl_connect("key_press_event", on_key)
    demo["paint"] = paint
    return demo


def _draw_boat(ax, rig: PitchRig) -> None:
    import matplotlib.pyplot as plt

    ax.cla()
    ax.set_facecolor("#d7e7f2")
    now = rig.now()
    xs = np.linspace(-4.0, 8.0, 500)
    ys = eta(xs, now, rig.waves) * WAVE_Y_SCALE
    ax.fill_between(xs, ys, -6.0, color="#2f6f93", zorder=1)
    ax.plot(xs, ys, color="#d5e8f2", linewidth=1.0, zorder=2)

    heave = float(eta(np.array([0.0]), now, rig.waves)[0]) * WAVE_Y_SCALE
    origin = np.array([0.0, heave - 0.05])
    pitch = rig.hull_pitch_deg()
    hull = rotate(HULL + origin, pitch, origin)
    console = rotate(CONSOLE + origin, pitch, origin)
    ax.fill(hull[:, 0], hull[:, 1], color=NAVY, zorder=3)
    ax.fill(console[:, 0], console[:, 1], color="#4d6278", zorder=4)

    angle = math.radians(SET_ANGLE_DEG)
    direction = np.array([math.cos(angle), math.sin(angle)])
    rail_body = np.vstack([RAIL_START, RAIL_START + direction * RAIL_M]) + origin
    rail = rotate(rail_body, pitch, origin)
    ax.plot(rail[:, 0], rail[:, 1], color="#c5962c", linewidth=4, solid_capstyle="round", zorder=5)

    along = rig.aircraft_along()
    craft = rotate(uav_polygon(along) + origin, pitch, origin)
    ax.fill(craft[:, 0], craft[:, 1], color="#b90e31", zorder=6)
    ax.plot(
        np.r_[craft[:, 0], craft[0, 0]],
        np.r_[craft[:, 1], craft[0, 1]],
        color="#3a0610",
        linewidth=0.9,
        zorder=7,
    )

    if rig.state in ("launching", "paused") and along > RAIL_M:
        path_body = np.vstack(
            [RAIL_START + direction * RAIL_M, RAIL_START + direction * along]
        ) + origin
        path = rotate(path_body, pitch, origin)
        ax.annotate(
            "",
            xy=path[1],
            xytext=path[0],
            arrowprops={"arrowstyle": "-|>", "color": "#0d6b2c", "lw": 1.6, "mutation_scale": 14},
            zorder=5,
        )

    ax.set_xlim(-4.0, 8.0)
    ax.set_ylim(-3.4, 4.8)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Head seas, bow to the right. Hull pitch follows the wave model.", loc="left", color="#3d4a5c", fontsize=10)
    plt.setp(ax.title, fontweight="regular")


def run_snapshot(path: Path, max_s: float = 90.0) -> float:
    import matplotlib

    matplotlib.use("Agg")
    rig = park_at_hold()
    rig.state = "armed"
    while rig.state != "paused" and rig.now() < max_s:
        rig.step_armed()
    if rig.state != "paused":
        raise RuntimeError(f"no safe window within {max_s:.0f} s")
    demo = build_figure(rig)
    demo["button"].label.set_text("Resume")
    demo["paint"]()
    demo["fig"].savefig(path, dpi=100)
    return rig.now()


def main() -> None:
    import matplotlib

    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    rig = park_at_hold()
    demo = build_figure(rig)

    def update(_frame) -> None:
        if rig.state != "paused":
            rig.step_armed()
        if rig.state == "paused" and demo["button"].label.get_text() != "Resume":
            demo["button"].label.set_text("Resume")
            demo["button"].ax.set_facecolor("#8dff9a")
            demo["anim"].event_source.stop()
            print(
                f"stopped at t={rig.now():.2f} s  true pitch {float(rig.truth[-1]):+.1f}°  "
                f"forecast {float(np.min(rig.release_forecast)):.1f}° to {float(np.max(rig.release_forecast)):.1f}°"
            )
        demo["paint"]()

    demo["paint"]()
    demo["anim"] = FuncAnimation(demo["fig"], update, interval=50, blit=False, cache_frame_data=False)
    try:
        demo["fig"].canvas.manager.window.state("zoomed")
    except Exception:
        pass
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--snapshot":
        out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).with_name("pitch_gate_demo_launch.png")
        launched = run_snapshot(out)
        print(f"LAUNCH at t={launched:.2f} s")
        print(f"wrote {out}")
    else:
        main()
