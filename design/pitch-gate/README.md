# Pitch gate

Sensing, forecast, allow/refuse for launch on a pitching boat.

## Sears framing

Thomas Sears’s work on wave-driven boat motion (Queen’s / Marshall lab) sits behind the gate design. Chapter 4 of his thesis gives a short-horizon pitch forecast as a **time-only spectral mixture**. Our sims use that as two cosines fitted to recent pitch, which beats a naive rate-hold over a ~0.3 s rail window. Field IMU logs and Sears’s full wave-modelling code are still separate from what we run here.

## Artifacts

- Write-up: `experiments/wave-pitch-simulation.md`
- Code: `code/pitch_sine_sim.py`, `code/pitch_gate_demo.py`
- Figures: `figures/pitch-forecast-v2.1.png`

## Reference

Sears, T. M. C. (2026). *Spectral Analysis for Robotic Spatiotemporal Mapping* (Ph.D. thesis, Chapter 4). Queen’s University. https://queensu.scholaris.ca/items/ed41fb5e-f0e1-4573-935c-7e94e8f48fed
