# Prototype gripper / carriage — dim sheet

Insitu-style hold / brake / clear for football stand-in on Sasco strut trolleys.
CAD: `gripper-carriage.scad` (parametric; export STL/STEP from OpenSCAD or rebuild in SolidWorks).

Units: mm unless noted. Values are design targets for the prototype — lock with Darcy before cut/print.

## Envelope

| Item | Value | Notes |
| --- | --- | --- |
| Rail / bed | 2× Sasco strut + Atkore trolleys | Stand-in track only |
| Carriage plate | 120 × 80 × 6 | Flat plate on trolley bolt pattern |
| Trolley bolt pattern | 40 × 40 (M5) | Confirm on physical trolley before drill |
| Football stand-in | Ø ~170 (long axis ~280) | Hold at mid-girth; pads soft |
| Prototype payload proxy | ~5 kg bag on carriage for energy tests | Separate from football fixture |

## Arms (Insitu-style)

| Item | Value | Notes |
| --- | --- | --- |
| Arm length (pivot → pad) | 90 | Each side |
| Pivot spacing (transverse) | 70 | Center-to-center |
| Pivot height above plate | 25 | |
| Closed pad gap | 140 | Clamps football midsection |
| Open swing (each arm) | 45° | Clears body after brake hit |
| Pad face | 30 × 20 × 4 elastomer | Replaceable |
| Arm stock | 20 × 6 flat bar (AL or PLA print) | |

## Brake / stop interface

| Item | Value | Notes |
| --- | --- | --- |
| Stop strike height above plate | 40 | Hits arm horns, not football |
| Arm horn / striker offset aft of pivot | 25 | Forward momentum opens jaws |
| Brake face (on rail end) | 30 wide × 50 tall | Shared with Darcy / structure |
| Carriage travel to stop | Full prototype stroke | Energy test uses same stop |

## Mass (estimate)

| Item | Mass |
| --- | --- |
| Plate + hardware | ~0.35 kg |
| Arms + pads | ~0.15 kg |
| Total carriage (empty) | ~0.5 kg |

## Still TBD

- Spring / preload on arms (hold through accel)
- Exact trolley hole survey
- Fighter fuselage pad geometry (full-size later)

## Interface checklist (Darcy)

- [ ] Trolley bolt pattern measured
- [ ] Brake face height / location on rail end
- [ ] Clearance under arms through full stroke
- [ ] No clash with band attach or latch
