"""
Log DFRobot ICG-20660L to CSV for noise / rock characterization.

Pi (hardware):
  python log_icg20660l.py --out ../../experiments/imu_static.csv --seconds 60 --hz 100
  python log_icg20660l.py --out ../../experiments/imu_rock.csv --seconds 30 --hz 100

Dev / no Pi (synthetic MEMS-like noise + optional rock):
  python log_icg20660l.py --simulate static --out ../../experiments/imu_static.csv --seconds 60 --hz 100
  python log_icg20660l.py --simulate rock --out ../../experiments/imu_rock.csv --seconds 30 --hz 100
"""

from __future__ import annotations

import argparse
import csv
import math
import time
from pathlib import Path

G = 9.80665


def pitch_from_accel_deg(ax_g: float, ay_g: float, az_g: float) -> float:
    # pitch about Y: nose up positive; board X forward, Z up
    return math.degrees(math.atan2(-ax_g, math.sqrt(ay_g * ay_g + az_g * az_g)))


def open_imu(bus: int, addr: int):
    from icg20660l_imu import ICG20660L

    imu = ICG20660L(bus=bus, addr=addr)
    imu.begin()
    return imu


def simulate_sample(t: float, mode: str, rng) -> dict[str, float]:
    # Order-of-magnitude MEMS noise (not a datasheet substitute for real bench data).
    ax = rng.gauss(0.0, 0.002)
    ay = rng.gauss(0.0, 0.002)
    az = 1.0 + rng.gauss(0.0, 0.003)
    gx = rng.gauss(0.0, 0.05)
    gy = rng.gauss(0.0, 0.05)
    gz = rng.gauss(0.0, 0.05)
    if mode == "rock":
        # ~0.4 s period, ~±3° pitch — gate-relevant hand rock
        omega = 2 * math.pi / 0.4
        theta = math.radians(3.0) * math.sin(omega * t)
        thetad = math.degrees(math.radians(3.0) * omega * math.cos(omega * t))
        ax = -math.sin(theta) + rng.gauss(0.0, 0.002)
        az = math.cos(theta) + rng.gauss(0.0, 0.003)
        gy = thetad + rng.gauss(0.0, 0.05)
    return {
        "ax_g": ax,
        "ay_g": ay,
        "az_g": az,
        "gx_dps": gx,
        "gy_dps": gy,
        "gz_dps": gz,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seconds", type=float, default=60.0)
    p.add_argument("--hz", type=float, default=100.0)
    p.add_argument("--bus", type=int, default=1)
    p.add_argument("--addr", type=lambda s: int(s, 0), default=0x69)
    p.add_argument(
        "--simulate",
        choices=("static", "rock"),
        default=None,
        help="Generate synthetic CSV when no I2C hardware is present",
    )
    args = p.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    dt = 1.0 / args.hz
    n = max(1, int(args.seconds * args.hz))

    imu = None
    rng = None
    if args.simulate:
        import random

        rng = random.Random(42 if args.simulate == "static" else 43)
        source = f"simulate:{args.simulate}"
    else:
        imu = open_imu(args.bus, args.addr)
        source = f"i2c:0x{args.addr:02X}"

    fields = [
        "t_s",
        "ax_g",
        "ay_g",
        "az_g",
        "gx_dps",
        "gy_dps",
        "gz_dps",
        "pitch_accel_deg",
        "source",
    ]

    t0 = time.perf_counter()
    with args.out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i in range(n):
            if args.simulate:
                t = i * dt
                s = simulate_sample(t, args.simulate, rng)
            else:
                target = t0 + i * dt
                now = time.perf_counter()
                if now < target:
                    time.sleep(target - now)
                t = time.perf_counter() - t0
                s = imu.read()
            row = {
                "t_s": f"{t:.6f}",
                "ax_g": f"{s['ax_g']:.6f}",
                "ay_g": f"{s['ay_g']:.6f}",
                "az_g": f"{s['az_g']:.6f}",
                "gx_dps": f"{s['gx_dps']:.6f}",
                "gy_dps": f"{s['gy_dps']:.6f}",
                "gz_dps": f"{s['gz_dps']:.6f}",
                "pitch_accel_deg": f"{pitch_from_accel_deg(s['ax_g'], s['ay_g'], s['az_g']):.6f}",
                "source": source,
            }
            w.writerow(row)

    if imu is not None:
        imu.close()

    elapsed = time.perf_counter() - t0
    print(f"wrote {n} samples to {args.out} in {elapsed:.2f}s (~{n / max(elapsed, 1e-9):.1f} Hz wall) [{source}]")


if __name__ == "__main__":
    main()
