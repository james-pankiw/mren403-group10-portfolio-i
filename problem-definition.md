# Problem definition

MREN 403 Group 10 · James Pankiw (portfolio write-up) · 2026-11-12  
Sources: client brief; proposal feedback (2026-10-27); supervisor meetings 2026-09-23, 2026-10-08, 2026-10-29, 2026-11-12; `references/fighter-hand-throw.md`; `references/ficheProduit-PRO 7.pdf`.

## Client and need

|              |                                                                                                 |
| ------------ | ----------------------------------------------------------------------------------------------- |
| **Client**   | Ingenuity Labs (Prof. Greeff, Prof. Gammell), with Coast Guard use case                         |
| **Need**     | Safe and reliable launch to test search-and-rescue algorithms over water using a fixed-wing UAV |
| **Aircraft** | MakeFlyEasy Fighter                                                                             |
| **Boat**     | Zodiac Nautic PRO 7                                                                             |

Hand launches are inconsistent even on land, and a failed launch is costly. Launching from a small RHIB adds deck pitch/roll and harsher weather. The client needs launches that are **safe and consistent** enough that algorithm testing over water is practical.

## Problem statement

> Design a system to semi-autonomously launch the MakeFlyEasy Fighter from a Zodiac Nautic PRO 7, safely and consistently, despite boat motion and marine weather.

**Semi-autonomous** here means: a person arms the system; the system decides whether a launch window is safe and when to release.

## Problem Factors

| Factor                           | Effect                                                             |
| -------------------------------- | ------------------------------------------------------------------ |
| Boat pitch during a short launch | Exit elevation changes while the aircraft is still on the launcher |
| Inconsistent hand-throw          | Not repeatable for SAR algorithm trials                            |
| Cost of a bad launch             | Airframe, payload, and test day lost                               |
| Marine environment               | Spray, corrosion, vibration, maintenance access                    |
| Full throttle before release     | Latch must hold thrust                                             |
| Deck space / PRO 7 layout        | Rail and mount must fit without modifying the hull                 |

## Scope

| In scope                                                                     | Out of scope (this course)                                   |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Full-size **design** for the Fighter on the PRO 7 (CAD, drawings, BOM, cost) | Building the full-size Fighter launcher inside the $500 fund |
| Scaled **prototype** to validate design decisions within $500                | Guaranteed Zodiac / open-water trial                         |
| Pitch sensing, prediction, and launch allow/refuse                           | Learned model as the thing that arms the latch               |
| One pitch axis for rail elevation (design + later prototype)                 | Two-axis gimbal or “launch in any sea” as the success test   |
| Carriage / gripper / energy delivery / trigger on the prototype              |                                                              |

## Design vs prototype

|          | Full-size design          | Scaled prototype                 |
| -------- | ------------------------- | -------------------------------- |
| Aircraft | MakeFlyEasy Fighter       | ~5 kg mass / football stand-in ( |
| Rails    | Sized for Fighter + PRO 7 | 2× Sasco strut + trolleys        |
| Proof    | Analysis, CAD             | Noted in subsystem-validation.md |
| Boat     | PRO 7 interface designed  | Bench / wave-pool stand-in       |

## Operating assumptions

| Item                    | Working value                                         | Status                                                    |
| ----------------------- | ----------------------------------------------------- | --------------------------------------------------------- |
| Launch elevation band   | 0–10° (set angle ~5° ±5°)                             | Working design band; justify vs Fighter launch attitude   |
| Pitch forecast horizon  | ≥ rail time (~0.27–0.5 s)                             | From rail length ÷ exit speed assumption                  |
| Head into waves         | Pitch is the primary gate axis                        | Meeting / Sears framing                                   |
| Wind vs heading         | ±30° allow band                                       | Team proposed limit; not a measurement                    |
| Full throttle at launch | Required                                              | Supervisor constraint 2026-10-08                          |
| Assumed seas (sim)      | H = 0.3–0.5 m; T = 1–4 s (and 6 s swell in hard case) | Synthetic; pending boat dynamics model/real imu data logs |

## Stakeholders

| Stakeholder | Care-about |
| --- | --- |
| Coast Guard / boat crew | Safe launch; no hull damage; clear procedures |
| SAR algorithm users | Repeatable launches so flight tests are usable |
| Course supervisors | Bench-validated prototype; buildable full-size design; justified parameters and edge cases |
| Team | $500, time to PDR/CDR, clear ownership |

## Reflection

Project Proposal feedback noted that the problem was stated as an immediate solution without clearly defining the problem to be solved in this project. This is an updated draft clearly stating the problem, stakeholders, and constraints.
