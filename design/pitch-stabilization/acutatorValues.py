import math

# input values for different mass and rail lengths 

L1 = 2      # Beam length (m)
L2 = 0.5      # Object length (m)

m1 = 1.67 *2    # Beam mass (kg)
m2 = 11      # Object mass (kg)

rf = 0.75      # Actuator attachment location from pivot (m)

theta_deg = 5.0   # Angular travel (degrees)
T = 0.5           # Time to complete motion (s)

g = 9.81

#ball screw avlues and efficiency 
lead = 0.00508      # 0.2 inch lead (m/rev)
eta = 0.90          # ball screw efficiency


# below calculates all required values for actuation 

theta = math.radians(theta_deg)

# Center of mass locations
r_m1 = L1 / 2
r_m2 = L2 / 2   # assumes back of object is and pivot point 

# Angular acceleration
alpha = 4 * theta / T**2

# Moment of inertia
I_beam = (1/3) * m1 * L1**2
I_object = (1/3) * m2 * L2**2

I_total = I_beam + I_object

# Gravity torque (worst case at horizontal)
tau_gravity = m1 * g * r_m1 + m2 * g * r_m2

# Acceleration torque
tau_accel = I_total * alpha

# Total torque
tau_total = tau_gravity + tau_accel

# Required actuator force
F_required = tau_total / rf


# Arc length traveled by attachment point
linear_distance = rf * theta

# Average linear speed
avg_speed = linear_distance / T

# Final angular velocity
omega_final = alpha * T

# safety factor of 2 
SF = 2.0

# Final Mortor Torque 
motor_torque = (F_required*SF * lead) / (2 * math.pi * eta)

rpm = (avg_speed / lead) * 60



# ==========================
# OUTPUT
# ==========================

print("\n===== RESULTS =====\n")

print(f"Angular displacement:      {theta_deg:.3f} deg")
print(f"Angular acceleration:      {alpha:.3f} rad/s^2")


print("\n--- Actuator Force ---")
print(f"Maximum force required:    {F_required:.3f} N")

print("\n--- Actuator Motion ---")
print(f"Linear travel:             {linear_distance:.4f} m")
print(f"Linear Speed:      {avg_speed:.4f} m/s")



print(f"\nRecommended force ({SF}x SF): {F_required*SF:.3f} N")
#motor torque information 
print("\n--- Ball Screw Requirements ---")
print(f"Motor torque: {motor_torque:.4f} N*m")
print(f"Screw speed:  {rpm:.1f} RPM")