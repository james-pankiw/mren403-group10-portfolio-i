# Pitch gate

Sensing, forecast, allow/refuse for launch on a pitching boat.

## Sears framing

Thomas Sears’s work on wave-driven boat motion (Queen’s / Marshall lab) sits behind the gate design. Chapter 4 of his thesis gives a short-horizon pitch forecast as a **time-only spectral mixture**. Our sims use that as two cosines fitted to recent pitch, which beats a naive rate-hold over a ~0.3 s rail window.

## Artifacts

| File | Role |
| --- | --- |
| `pitch_sine_sim.py` | Two-cosine forecast vs rate hold |
| `pitch_gate_demo.py` | Interactive boat / scope / arm demo |
| `icg20660l_imu.py` | DFRobot ICG-20660L I2C driver |
| `log_icg20660l.py` | CSV logger (Pi or `--simulate`) |
| `analyze_imu_log.py` | Noise / rate summary |
| `../../experiments/wave-pitch-simulation.md` | Sim write-up |
| `../../experiments/imu-icg20660l-noise.md` | IMU noise note + logs |

## Reference

Sears, T. M. C. (2026). *Spectral Analysis for Robotic Spatiotemporal Mapping* (Ph.D. thesis, Chapter 4). Queen’s University. https://queensu.scholaris.ca/items/ed41fb5e-f0e1-4573-935c-7e94e8f48fed

DFRobot SEN0443 / ICG-20660L: https://wiki.dfrobot.com/sen0443/docs/22509
