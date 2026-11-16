"""Summarize an ICG-20660L CSV log: rate, noise, drift."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path


def load(path: Path) -> list[dict[str, float | str]]:
    rows = []
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append(
                {
                    "t_s": float(r["t_s"]),
                    "gy_dps": float(r["gy_dps"]),
                    "pitch_accel_deg": float(r["pitch_accel_deg"]),
                    "source": r.get("source", ""),
                }
            )
    return rows


def rms(xs: list[float]) -> float:
    return math.sqrt(sum(x * x for x in xs) / max(1, len(xs)))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    args = p.parse_args()
    rows = load(args.csv)
    if len(rows) < 2:
        raise SystemExit("need ≥2 samples")

    t = [r["t_s"] for r in rows]
    pitch = [r["pitch_accel_deg"] for r in rows]
    gy = [r["gy_dps"] for r in rows]
    dt = [t[i + 1] - t[i] for i in range(len(t) - 1)]
    hz = 1.0 / statistics.mean(dt)
    pitch0 = [x - statistics.mean(pitch) for x in pitch]
    gy0 = [x - statistics.mean(gy) for x in gy]
    # simple linear drift on pitch (deg/s)
    n = len(t)
    t_mean = statistics.mean(t)
    p_mean = statistics.mean(pitch)
    num = sum((t[i] - t_mean) * (pitch[i] - p_mean) for i in range(n))
    den = sum((t[i] - t_mean) ** 2 for i in range(n))
    drift = num / den if den else 0.0

    print(f"file: {args.csv}")
    print(f"source: {rows[0]['source']}")
    print(f"samples: {n}  duration: {t[-1] - t[0]:.2f} s  mean rate: {hz:.1f} Hz")
    print(f"pitch_accel: mean={p_mean:.4f}°  σ={statistics.pstdev(pitch):.4f}°  rms_ac={rms(pitch0):.4f}°")
    print(f"gyro_y: mean={statistics.mean(gy):.4f} dps  σ={statistics.pstdev(gy):.4f} dps  rms_ac={rms(gy0):.4f} dps")
    print(f"pitch linear drift ≈ {drift:.5f} °/s ({drift * 60:.3f} °/min)")


if __name__ == "__main__":
    main()
