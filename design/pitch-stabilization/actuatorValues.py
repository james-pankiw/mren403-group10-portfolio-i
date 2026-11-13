import math

# Actuator sizing for rail pitch axis.
# Geometry: rail pivots at one end; payload CM is outboard on the rail (r_m2),
# not L2/2 unless that is physically true.

# --- Inputs (edit these) ---
L1 = 2.0          # rail / beam length (m)
L2 = 0.5          # payload length along rail (m), for optional distributed model
m1 = 1.67 * 2     # rail mass (kg) -- placeholder
m2 = 6.0          # payload mass (kg); Fighter MTOW < 7 kg; prototype ~5 kg
rf = 0.75         # actuator attach distance from pivot (m)
r_m2 = L1 - L2 / 2  # payload CM from pivot (m); do NOT use L2/2 for a tip-mounted UAV

theta_deg = 5.0
T = 0.5           # motion time (s)
g = 9.81

lead = 0.00508    # ball-screw lead (m/rev)
eta = 0.90
SF = 2.0

# --- Derived ---
theta = math.radians(theta_deg)
r_m1 = L1 / 2
alpha = 4 * theta / T**2

I_beam = (1 / 3) * m1 * L1**2
I_payload_cm = (1 / 12) * m2 * L2**2  # compact body about its CM (order-of-magnitude)
I_payload = I_payload_cm + m2 * r_m2**2
I_total = I_beam + I_payload

tau_gravity = m1 * g * r_m1 + m2 * g * r_m2  # max at horizontal if theta=0 is horizontal
tau_accel = I_total * alpha
tau_total = tau_gravity + tau_accel

F_required = tau_total / rf

# Vertical stroke if actuator stays vertical: rf*sin(theta); arc length rf*theta ~ same at 5 deg
linear_distance = rf * math.sin(theta)
avg_speed = linear_distance / T
peak_speed = 2 * avg_speed  # triangular profile

motor_torque = (F_required * SF * lead) / (2 * math.pi * eta)
rpm_avg = (avg_speed / lead) * 60
rpm_peak = (peak_speed / lead) * 60

print("\n===== RESULTS =====\n")
print(f"r_m2 (payload CM from pivot): {r_m2:.3f} m")
print(f"Angular displacement:      {theta_deg:.3f} deg")
print(f"Angular acceleration:      {alpha:.3f} rad/s^2")
print(f"I_beam / I_payload / I_total: {I_beam:.3f} / {I_payload:.3f} / {I_total:.3f} kg*m^2")
print("\n--- Actuator Force ---")
print(f"Maximum force required:    {F_required:.3f} N")
print(f"Recommended force ({SF:g}x SF): {F_required*SF:.3f} N")
print("\n--- Actuator Motion ---")
print(f"Linear travel (rf*sin):    {linear_distance:.4f} m")
print(f"Avg linear speed:          {avg_speed:.4f} m/s")
print(f"Peak linear speed (~2x):   {peak_speed:.4f} m/s")
print("\n--- Ball Screw Requirements ---")
print(f"Motor torque (at SF force): {motor_torque:.4f} N*m")
print(f"Screw speed from avg:       {rpm_avg:.1f} RPM")
print(f"Screw speed from peak:      {rpm_peak:.1f} RPM")
