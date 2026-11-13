# Subsystem validation plan

MREN 403 Group 10 · Portfolio I · 2026-11-12

**Rule:** Design the full-size Fighter launcher. Use the $500 prototype to pass/fail design decisions. A prototype pass is not a Zodiac trial and not proof of full exit speed or launch energy.

## Prototype baseline

| Item | Choice |
| --- | --- |
| Rails / carriage bed | 2× Sasco strut + trolleys — **prototype stand-in only** (see Darcy, `design/rails-structure/Prototype Rails.docx`) |
| Force-delivery mass | ~5 kg bean bag |
| Fuselage stand-in | Football (or similar) |
| Launch computer (first) | Raspberry Pi (command → release latency) |
| Motion proxy | Small wave pool |

Full-size rail material is a **separate** decision (Darcy currently argues CNC **stainless** in `design/rails-structure/Full Sized Rail.docx`). Strut tests do not select that material.

## Prototype-tested subsystems

| # | Subsystem | Lead | Test | Pass | Informs final design |
| --- | --- | --- | --- | --- | --- |
| 1 | Structure | Darcy | Launch on strut bed; watch stability | No collapse / excessive flex / loss of alignment | Bracing, span, load path in CAD |
| 2 | Carriage & release | Darcy + Ahrvin | Football hold; release at brake | Hold through accel; arms clear | Linkage, pads, brake clearances |
| 3 | Launch energy | Ahrvin | Bands launch ~5 kg to stop | Repeatable delivery; brake absorbs | Band sizing method; brake energy |
| 4 | Trigger & latency | James + Ahrvin | Pi command → release; arm/safe | Latency ≪ window; no disarm release | Pi vs MCU; interlock; latch |
| 5 | Pitch gate | James | IMU + forecast; gated launch on pool | Fewer false allows than rate hold | Predictor, margin, sample rate |
| 6 | Pitch stabilization | Jamison | Actuator holds elevation on moving base | Stays in 0–10°; error logged | Actuator force/speed; mount; CAD |

**Build order:** 1 → 3 → 4 → 2 → 5 → 6.

### 1. Structure

| | |
| --- | --- |
| **What we test** | Mechanical stability during launch on the prototype bed |
| **What we do not test** | Final rail material; keeping strut/trolleys on the Fighter design |
| **Edge cases** | Weak-axis flex; shake at brake; mount looseness |

### 2. Carriage & release

| | |
| --- | --- |
| **What we test** | Hold through acceleration; Insitu-style clear at stop |
| **What we do not test** | Final bearing hardware; Fighter airframe strength |
| **Edge cases** | Soft stand-in shifts; arms fail to clear; bind on stop |

### 3. Launch energy

| | |
| --- | --- |
| **What we test** | Force delivery; repeatable travel to brake |
| **What we do not test** | Fighter exit speed or full launch energy |
| **Edge cases** | Partial band failure; overspeed into stop; abort with energy stored |

### 4. Trigger & latency

| | |
| --- | --- |
| **What we test** | Command→release latency; arm/disarm/abort |
| **Edge cases** | Latency eats the pitch window; glitch release |

### 5. Pitch gate

| | |
| --- | --- |
| **Sim so far** | `code/pitch_sine_sim.py`, `code/pitch_gate_demo.py`; write-up in `experiments/wave-pitch-simulation.md` |
| **Hardware next** | Wave pool / rocking motion; score false allows |
| **Edge cases** | Crest / high rate; bad fit; IMU dropout |

### 6. Pitch stabilization

| | |
| --- | --- |
| **What we test** | Hold set elevation while base pitches |
| **Status** | After 1–5 are stable; date any slip past PDR |
| **Edge cases** | Actuator saturation at crest; error outside 0–10° |

## Not prototype-tested

| Item | Plan |
| --- | --- |
| **Boat mount (PRO 7)** | Full-size CAD / design only (Jamison). No prototype mount validation. |
| **Wet operation** | Waterproof the prototype with a chosen style; treat the wave-pool day as a transient check that gear still runs. Not a separate spray campaign. |

## What a pass does not claim

- Zodiac / PRO 7 trial  
- Fighter exit speed or full launch energy  
- Final rail material from the strut bed  
- Prototype proof of the boat mount  
