# Wave / pitch simulation documentation

MREN 403 Group 10 · James Pankiw · Portfolio I  
Purpose: document the synthetic sea → pitch → forecast → gate work done before hardware IMU logs exist.

**Claim level:** These runs are **engineering simulations** for algorithm and band design. They are **not** Zodiac or Lake Ontario measurements.

---

## Traceability

| Artifact | Path (this portfolio tree) | Role |
| --- | --- | --- |
| Pitch from rigid-hull wave slope | `experiments/pitch_from_wave_slope.py` | Amplitude model for assumed seas |
| Slope note + table | `experiments/pitch-from-wave-slope.md` | Derivation and assumptions |
| Slope figure | `figures/pitch-from-wave-slope.png` | One-sea pitch traces |
| Slope results | `experiments/results.txt` | Printed amplitudes / rate-hold errors |
| Pitch gate sim v2.1 | `code/pitch_sine_sim.py` | Two-cosine forecast scored vs rate hold |
| Forecast figure v2.1 | `figures/pitch-forecast-v2.1.png` | Trace + false-allow / missed-window bars |
| Interactive demo | `code/pitch_gate_demo.py` | Boat + scope + arm → allow → pause |
| Theory source | Sears (2026) Ch. 4 — time-only spectral mixture (two cosines) | Forecast form |
| Boat length | Zodiac PRO 7 sheet → 6.90 m (`references/pro-7.md`) | Hull length in sim |

Run from the **git repo root** (scripts still live there / are mirrored under `code/` and `experiments/`):

```text
python docs/portfolio/preliminary-simulations/pitch_from_wave_slope.py
python software/pitch_sine_sim.py
python software/pitch_gate_demo.py
```

Or from copies in this tree:

```text
python portfolio/experiments/pitch_from_wave_slope.py
python portfolio/code/pitch_sine_sim.py
python portfolio/code/pitch_gate_demo.py
```

Demo needs a display / Tk (`python3-tk` on Linux). Sim plots use Agg and write PNGs.

---

## 1. Pitch from wave slope (2026-10-03)

### Idea

In head seas, treat the boat as a **rigid length** $L_b$. Pitch amplitude for one deep-water sine wave of crest-to-trough height $H$ and period $T$:

$$
L = \frac{g T^2}{2\pi}, \qquad
\theta_{\max} = \frac{H}{L_b}\left|\sin\left(\frac{\pi L_b}{L}\right)\right|.
$$

Each table row is its **own** assumed sea (not three waves added). Heights/periods are assumptions, not a buoy record.

### Assumed seas used later by the gate sim

| Name | $H$ (m) | $T$ (s) | Pitch amplitude (7 m / 6.90 m hull) |
| --- | --- | --- | --- |
| Short chop | 0.50 | 1.0 | ~±4.09° |
| Small wind wave | 0.30 | 3.0 | ~±2.46° |
| Moderate wind wave | 0.50 | 4.0 | ~±3.16° (slope study only) |

**Why constant-rate fails:** at a crest, holding the crest angle while the wave continues produces large error on short periods (e.g. 1 s chop: rate-hold errors of several degrees by 0.3–0.5 s). That motivates a short-horizon forecast.

### Limitations

- Deep-water dispersion only; no diffraction, surge, or boat dynamics.
- 1 s wavelength ≪ hull → formula is a bound; a 7 m boat does not follow chop like a small craft.
- Replacing overall length 6.90 m with hull length 5.97 m would cut chop pitch; we keep overall length and note the sensitivity in `references/pro-7.md`.

---

## 2. Pitch gate simulation v2.1 (`pitch_sine_sim.py`)

### Gate definition

| Parameter | Value | Notes |
| --- | --- | --- |
| Launch elevation band | 0–10° | Set angle 5° at band centre |
| Margin | 1.5° | Allow only if forecast stays inside band by this margin |
| Prior | 6.0 s | Fit window |
| Horizon | $2 \times 2\,\mathrm{m} / 15\,\mathrm{m/s} \approx 0.27\,\mathrm{s}$ | Rail time; Sears-feasible ~0.5 s covers this |
| IMU noise | 0.3° | Additive on samples the gate sees |
| Predictor | Two cosines; frequencies from spectrum | Sears Ch. 4 time-only form |
| Baseline | Hold last pitch rate | Comparison for false allows |
| Seed | 403 | Reproducible synthetic sea |

### Synthetic truth (harder than the model)

- 1 s chop and 3 s wind wave from the slope table, each **spread** over nearby periods with random phases (amplitude drifts).
- Extra **6 s swell** the two-cosine fit is **not** given.
- Launch elevation = hull pitch + 5° set angle.

### Cases scored (60 s of release times)

1. Forecast only (rail fixed to hull)  
2. Forecast + 1.5° margin  
3. Slow stabilization (actuator removes most motion slower than 2 s; **20% residual assumed**)  
4. Slow stabilization + margin  

**Metrics**

- **False allow:** gate allowed; true elevation left 0–10° during the horizon.  
- **Missed window:** gate refused; true elevation stayed in band.

Re-run the script for the current numeric table; paste the printed false-allow / missed percentages into the portfolio when submitting so figures and text match.

### What this informs for the final design

- Margin and prior length are design knobs, not decoration.
- Stabilization helps but does not replace the gate (chop is left for the forecast in this model).
- Rate hold is an insufficient safety baseline near crests.
- Hardware must still beat this on a **measured** pitch log (wave pool / rocking rig).

---

## 3. Interactive demo (`pitch_gate_demo.py`)

Same sea, noise, and gate as the sim family. Dashboard: wind readout (assumed OK), heading, pitch, scope of recorded pitch + forecast + rate hold, arm button. When the gate allows after arm, the demo launches briefly then **pauses** and can show true pitch through the window.

**Use:** explain the gate to supervisors and teammates; not a validation pass by itself.

---

## 4. Path to hardware validation (pitch gate)

| Step | Status |
| --- | --- |
| Slope amplitudes | Done (assumed seas) |
| Synthetic forecast vs rate hold | Done (v2.1) |
| Demo for communication | Done |
| IMU log on bench / Pi | Next |
| Wave pool / rocking rig score | Validation plan, subsystem 5 |
| Sears wave-modelling code | Pending his supervisors; do not treat as in hand |

---

## Reflection

Early work replaced hand-waved ±10° travel with a **documented amplitude model**, then a **scored predictor**. Remaining honesty: seas and the 20% stabilizer residual are assumptions; 0–10° and 15 m/s still need Fighter-facing justification; only a real pitch log closes the loop.
