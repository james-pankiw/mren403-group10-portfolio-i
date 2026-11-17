"""Summarize an ICG-20660L CSV log: rate, noise, drift."""
import csv
import math
import statistics
import sys

def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / max(1, len(xs)))

def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: analyze_imu_log.py <csv>\n")
        return 2
    path = argv[1]
    sys.stdout.write("reading %s ...\n" % path)
    sys.stdout.flush()
    t = []
    pitch = []
    gy = []
    source = ""
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for r in reader:
            t.append(float(r["t_s"]))
            pitch.append(float(r["pitch_accel_deg"]))
            gy.append(float(r["gy_dps"]))
            if not source:
                source = r.get("source", "")
    if len(t) < 2:
        sys.stderr.write("need >=2 samples\n")
        return 1
    dt = [t[i + 1] - t[i] for i in range(len(t) - 1)]
    hz = 1.0 / statistics.mean(dt)
    p_mean = statistics.mean(pitch)
    pitch0 = [x - p_mean for x in pitch]
    gy_mean = statistics.mean(gy)
    gy0 = [x - gy_mean for x in gy]
    t_mean = statistics.mean(t)
    num = sum((t[i] - t_mean) * (pitch[i] - p_mean) for i in range(len(t)))
    den = sum((ti - t_mean) ** 2 for ti in t)
    drift = num / den if den else 0.0
    print("file: %s" % path)
    print("source: %s" % source)
    print("samples: %d  duration: %.2f s  mean rate: %.1f Hz" % (len(t), t[-1] - t[0], hz))
    print("pitch_accel: mean=%.4f deg  sigma=%.4f deg  rms_ac=%.4f deg" % (p_mean, statistics.pstdev(pitch), rms(pitch0)))
    print("gyro_y: mean=%.4f dps  sigma=%.4f dps  rms_ac=%.4f dps" % (gy_mean, statistics.pstdev(gy), rms(gy0)))
    print("pitch linear drift ~= %.5f deg/s (%.3f deg/min)" % (drift, drift * 60))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
