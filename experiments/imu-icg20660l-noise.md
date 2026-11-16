# ICG-20660L noise / sample-rate note

DFRobot Fermion ICG-20660L (SEN0443) on Raspberry Pi I2C (addr `0x69` default).
Logger: `design/pitch-gate/log_icg20660l.py`. Analyzer: `design/pitch-gate/analyze_imu_log.py`.

## Bring-up

| Item | Value |
| --- | --- |
| Bus | I2C-1; SDA/SCL/3V3/GND |
| WHO_AM_I | `0x91` |
| Accel FS | ±2 g |
| Gyro FS | ±250 dps |
| Target log rate | 100 Hz |

```text
python design/pitch-gate/log_icg20660l.py --out experiments/imu_static.csv --seconds 60 --hz 100
python design/pitch-gate/log_icg20660l.py --out experiments/imu_rock.csv --seconds 30 --hz 100
```

## Logs in this folder

| File | Condition | Source tag |
| --- | --- | --- |
| `imu_static.csv` | 60 s bench-still | `simulate:static` until Pi hardware re-run |
| `imu_rock.csv` | 30 s ~0.4 s period ±3° pitch | `simulate:rock` until Pi hardware re-run |

Synthetic logs use MEMS-like noise so the analysis path is ready. **Replace both CSVs with hardware logs** (`source=i2c:0x69`) before treating numbers as validation evidence.

## Results (current CSVs)

| Metric | Static (60 s) | Rock (30 s) |
| --- | --- | --- |
| Mean sample rate | 100 Hz | 100 Hz |
| Pitch (accel) σ | 0.112° | 2.12° (motion) |
| Gyro Y σ | 0.050 dps | 33.3 dps (motion) |
| Pitch linear drift | ~0.0027 °/min | n/a |

Static pitch σ ≈ 0.11° is well under the sim’s 0.3° IMU noise knob and small vs the 0–10° gate band. Gate margin should stay driven by forecast error / sea model, not this sensor’s static floor — confirm on hardware.

## Gate implication

Order of magnitude: static noise ≪ 1° → keep sim noise ≈ 0.3° as a conservative allowance for vibration once the IMU is on the moving rig. Next: hardware static + rock on the Pi; then wave-pool with the forecast.
