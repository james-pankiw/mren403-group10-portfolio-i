# Preliminary simulations — pitch from wave slope

2026-10-03. This note is the amplitude model used until a pitch log exists. The forecast script `code/pitch_sine_sim.py` uses the 1 s and 3 s rows from the table below.

Script: `pitch_from_wave_slope.py` in this folder. Figure: `figures/pitch-from-wave-slope.png`. Printed table: `results.txt`.

## What is assumed

- Boat length $L_b = 7\,\mathrm{m}$. The selected boat is the Zodiac Nautic PRO 7, overall length 6.90 m (`references/pro-7.md`). Seven metres is inside the sheet’s ±3% tolerance, so this table is unchanged.
- Deep water. Wavelength from the period only.
- Head seas. The boat is a rigid length, so pitch is the bow-to-stern slope of one sine wave.
- Each row is its own assumed sea, not three waves added together.
- Heights and periods are assumptions, not a Kingston buoy record and not Sears’ IMU.

## Wavelength

$$
L = \frac{g T^2}{2\pi}, \qquad g = 9.81\,\mathrm{m/s^2}.
$$

## Pitch amplitude

Surface of one component, crest-to-trough height $H$:

$$
\eta = \frac{H}{2}\sin(kx), \qquad k = \frac{2\pi}{L}.
$$

Pitch of a rigid boat is the elevation difference from stern to bow, divided by length. With the bow at $x + L_b/2$ and the stern at $x - L_b/2$,

$$
\theta(t) = \frac{H}{L_b}\sin\left(\frac{\pi L_b}{L}\right)\cos(\omega t).
$$

The amplitude saved by the script is

$$
\theta_{\max} = \frac{H}{L_b}\left|\sin\left(\frac{\pi L_b}{L}\right)\right|
$$

in radians, then converted to degrees.

Long-wave check: if $L \gg L_b$, $\sin(\pi L_b/L) \approx \pi L_b/L$, so $\theta_{\max} \approx \pi H / L$. That is the maximum slope of the wave. A short wave, $L \ll L_b$, gives a smaller pitch than that slope because the hull spans more than one wave. A 1 s wave is about 1.6 m long, so this formula is only a bound for the Coast Guard boat. The Otter is about 2 m and can follow that chop; a 7 m boat does not.

## Assumed seas

| Name | $H$ (m) | $T$ (s) | Role |
| --- | --- | --- | --- |
| Small wind wave | 0.3 | 3 | Plausible short lake wave |
| Moderate wind wave | 0.5 | 4 | Longer than the 1 s Otter peak |
| Short chop | 0.5 | 1 | Same order as the Sears station-keeping peak; hull is longer than the wave |

Exact wavelength, pitch amplitude, and the crest errors at 0.3 s and 0.5 s are written by the script to `results.txt` each run. Do not copy the old ±8° or ±10° figures forward. Actuator travel waits on a measured pitch log.

## Run on 2026-10-03

Boat length 7.0 m. Release is at a crest, so a constant-rate model holds that crest angle. Error is that hold minus the true pitch.

| Sea | $H$ (m) | $T$ (s) | $L$ (m) | Pitch amplitude | Pitch at +0.3 s | Rate error at 0.3 s | Pitch at +0.5 s | Rate error at 0.5 s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Small wind wave | 0.30 | 3 | 14.05 | ±2.46° | +1.99° | 0.47° | +1.23° | 1.23° |
| Moderate wind wave | 0.50 | 4 | 24.98 | ±3.16° | +2.81° | 0.34° | +2.23° | 0.92° |
| Short chop | 0.50 | 1 | 1.56 | ±4.09° | −1.26° | 5.35° | −4.09° | 8.17° |
