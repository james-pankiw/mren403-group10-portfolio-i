# Pitch stabilization

Actuator sizing and trades for the rail elevation axis.

| File | Role |
| --- | --- |
| `actuator_force_requirements.tex` | Force / stroke / motor equations (source) |
| `actuator_part_comparison.tex` | Lead/ball screw and motor trade (source) |
| `UAV_launch_Actuator_values.pdf` | Earlier PDF export of the math |
| `Actuator_Pros_Cons.pdf` | Earlier PDF export of the trade |
| `actuatorValues.py` | Numeric evaluation of the sizing model |

**Note:** An older script used payload inertia about the wrong pivot and `r_m2 = L2/2`. The `.tex` and `actuatorValues.py` here use parallel-axis inertia and an outboard `r_m2`. Re-run the script before ordering parts. Final commercial part selection is still TBD.
