# Subsystem validation plan

MREN 403 Group 10 · Portfolio I · Updated after supervisor meeting 2026-11-12  
Detailed ownership: `decisions/group-leads.md`

## Rule

Design the full-size Fighter launcher. Use the $500 prototype to **pass/fail design decisions**. A prototype pass is **not** a Zodiac trial and **not** proof of full exit speed / launch energy.

## Prototype baseline

| Item                    | Choice                                   |
| ----------------------- | ---------------------------------------- |
| Rails                   | 2× Sasco / Atkore strut                  |
| Carriage                | Atkore strut trolleys                    |
| Force-delivery mass     | ~5 kg bean bag                           |
| Fuselage stand-in       | Football (or similar)                    |
| Launch computer (first) | Raspberry Pi (command → release latency) |
| Motion proxy            | Small wave pool                          |

Strut + trolleys are a cheap prototype bed. They do **not** validate final rail material or the final carriage bearing choice.

## Subsystems

| ID  | Subsystem          | Lead           | Prototype test                                       | Pass                                                                                          | Locks in final design                                       |
| --- | ------------------ | -------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| A   | Rail / structure   | Darcy          | Launch on strut bed; watch frame/rail stability      | Structure stays stable under launch loads (no collapse, excessive flex, or loss of alignment) | Mechanical layout / bracing / load path                     |
| B   | Carriage + gripper | Darcy + James  | Football hold / release at brake                     | Hold through accel; arms clear                                                                | Linkage, pads, clearances                                   |
| C   | Launch energy      | Ahrvin         | Bands launch ~5 kg to stop                           | Repeatable; brake absorbs                                                                     | Band sizing method; brake energy                            |
| D   | Launch trigger     | James + Ahrvin | Pi latency; arm/safe                                 | Latency ≪ window; no disarm release                                                           | Time from command to launch                                 |
| E   | Pitch gate         | James          | IMU + forecast on wave pool                          | Fewer false allows than rate hold                                                             | Predictor, margin (imu noise), sample rate                  |
| F   | Pitch control      | Jamison        | Actuator holds 0–10° on moving base                  | Elevation in band; error logged                                                               | Actuator force/speed; mount                                 |
| G   | Boat mount         | Jamison (CAD)  | **Not prototype-tested**                             | —                                                                                             | Full-size PRO 7 interface stays design/CAD only             |
| H   | Environment        | James          | Opportunistic check in wave pool once the rig is wet | Electronics still run after pool use                                                          | Prototype waterproofing style; feeds final marine packaging |

**Build order:** A → C → D → B → E → F. H is incidental to the wave-pool run, not a separate campaign. G is design-only.

## A. Rail / structure

|                         |                                                                                                       |
| ----------------------- | ----------------------------------------------------------------------------------------------------- |
| **Lead**                | Darcy                                                                                                 |
| **Full-size job**       | Straight, stiff rail/frame that fits the PRO 7 and takes launch and brake loads                       |
| **Prototype hardware**  | Sasco strut + trolleys                                                                                |
| **What we test**        | Mechanical stability of the structure during launch (deflection, shake, alignment under ~5 kg launch) |
| **What we do not test** | Final rail material; suitability of strut or trolleys for the Fighter launcher                        |
| **Pass**                | Frame/rail holds alignment through launch and brake; no structural failure or unsafe motion           |
| **Informs**             | Bracing, span, mount stiffness, and load path in full-size CAD                                        |
| **Edge cases**          | Weak-axis flex; shake at brake; mount looseness                                                       |

## B. Carriage + gripper

|                         |                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------- |
| **Lead**                | Darcy, James                                                                    |
| **Full-size job**       | Hold the Fighter; release cleanly at stroke end without wing or fuselage damage |
| **Prototype hardware**  | Carriage on prototype trolleys; football (or similar) as fuselage stand-in      |
| **What we test**        | Hold through acceleration; release at the brake stop; arms clear the body       |
| **What we do not test** | Final trolley/bearing hardware; Fighter airframe strength                       |
| **Pass**                | Stand-in stays seated until stop; arms swing clear;                             |
| **Informs**             | Linkage geometry, pad locations, brake placement                                |
| **Edge cases**          | Soft body shifts in the jaws; arms fail to clear at speed; bind on the stop     |

## C. Launch energy

|                         |                                                                                                                        |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Lead**                | Ahrvin                                                                                                                 |
| **Full-size job**       | Store and deliver launch energy; aircraft at full throttle before release                                              |
| **Prototype hardware**  | Scaled elastic/bands; ~5 kg bean bag on the carriage                                                                   |
| **What we test**        | Force delivery to the carriage; repeatable travel to the brake; brake absorbs the stop                                 |
| **What we do not test** | Fighter exit speed or full-size launch energy                                                                          |
| **Pass**                | Mass reaches the stop repeatably; structure and brake survive; energy delivery is consistent enough to size the method |
| **Informs**             | Band sizing method; brake energy capacity; loads into the structure (feeds A and B)                                    |
| **Edge cases**          | Partial band failure; overspeed into the stop                                                                          |

*Mass justification for ~5 kg is still an open write-up (supervisor ask 2026-11-12).*

## D. Launch trigger

|                        |                                                                                |
| ---------------------- | ------------------------------------------------------------------------------ |
| **Lead**               | James (firmware / Pi), Ahrvin (latch hardware)                                 |
| **Full-size job**      | Release only when armed and the gate allows; hold against full-throttle thrust |
| **Prototype hardware** | Raspberry Pi command path; latch/release on the prototype                      |
| **What we test**       | Command → launch latency and jitter; arm / disarm / abort                      |
| **Pass**               | Latency known and small vs ~0.3–0.5 s window; no release when disarmed         |
| **Informs**            | Interlock logic; latch rating; wave prediction horizon                         |
| **Edge cases**         | Latency the safe pitch window; release on glitch                               |

## E. Pitch gate

|                         |                                                                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Lead**                | James                                                                                                                           |
| **Full-size job**       | Log pitch; forecast; allow launch only inside a safe window                                                                     |
| **Prototype / sim**     | Two-cosine forecast; rocking rig (manual input) or small wave pool                                                              |
| **Sim evidence so far** | `code/pitch_sine_sim.py`, `code/pitch_gate_demo.py` — see [wave-pitch-simulation.md](../experiments/wave-pitch-simulation.md) |
| **What we test**        | False allows; gated launch into C/D hardware on real motion                                                                     |
| **Pass**                | Refuse on bad fit / dropout, later testing with wavepool launch                                                                 |
| **Informs**             | Predictor, prior length, margin inside 0–10°, sample rate                                                                       |
| **Edge cases**          | Crest / high rate; unmodelled swell; IMU gap                                                                                    |

## F. Pitch control

|                         |                                                                                                                  |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Lead**                | Jamison                                                                                                          |
| **Full-size job**       | Hold rail elevation in the launch band during the launch window                                                  |
| **Prototype hardware**  | Front-rail linear actuator on a moving base (after A–E are stable)                                               |
| **What we test**        | Hold a set elevation while the base pitches; log angle error vs time                                             |
| **What we do not test** | Full marine weather envelope on day one; final actuator brand until force/speed are sized                        |
| **Pass**                | Elevation stays inside 0–10° for the window; error logged                                                        |
| **Informs**             | Required angular rate / travel (Δθ, time); actuator force and speed; mount stiffness; CAD of the pitch axis      |
| **Edge cases**          | Crest rates that saturate the actuator; hold error outside the band; coupling into structure vibration (dampers) |
| **Status**              | Later than gate + carriage                                                                                       |

## G. Boat mount — not tested on the prototype

Full-size PRO 7 mount is **design/CAD only** (Jamison). No prototype boat-mount validation this term.

## H. Environment

When the rig goes in the wave pool, we waterproof the prototype electronics with a chosen style (enclosure / sealing approach TBD) and treat that pool day as a transient check: gear still runs wet. Final marine packaging and sea-spray maintenance stay on the full-size design record.
