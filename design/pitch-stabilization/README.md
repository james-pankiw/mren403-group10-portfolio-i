# Pitch stabilization

Actuator sizing and part selection for the rail elevation axis.

| File | Role |
| --- | --- |
| `actuator_force_requirements.tex` | Force / stroke / motor equations |
| `actuator_part_comparison.tex` | Lead/ball screw and motor trade |
| `actuator_part_selection.tex` | Selected motors, screws, nuts, couplers |
| `actuatorValues.py` | Numeric sizing model |
| `ISV57T-180S_Torque_Speed_Curve.pdf` | Full-scale motor curve |
| `nema-23-stepper-motor-specs.pdf` | Test motor curve |

## Review note

First sizing pass understated actuator force (payload inertia about the wrong pivot / `$r_{m_2}=L_2/2$`). Current `.tex` / `.py` use outboard `$r_{m_2}$` and parallel-axis inertia; part selection was updated against that model. Still open: full-scale peak RPM vs motor max; test motor rated torque is tight vs SF2 (peak torque covers it). Re-run `actuatorValues.py` before ordering.
