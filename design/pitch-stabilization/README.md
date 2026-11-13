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

Uses outboard `$r_{m_2}$` and parallel-axis inertia. Re-run `actuatorValues.py` before ordering.
