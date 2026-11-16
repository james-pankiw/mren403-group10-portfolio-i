// Prototype Insitu-style football gripper on strut carriage.
// Dimensions match dims.md (mm). Open in OpenSCAD → export STL, or rebuild in SolidWorks.

$fn = 48;

plate_l = 120;
plate_w = 80;
plate_t = 6;
trolley_pitch = 40;
trolley_hole = 5.2;

pivot_spacing = 70;
pivot_z = 25;
arm_len = 90;
arm_w = 20;
arm_t = 6;
pad_l = 30;
pad_w = 20;
pad_t = 4;
closed_gap = 140;
horn_aft = 25;
horn_h = 15;
open_angle = 0; // set 45 to preview open

module plate() {
  difference() {
    cube([plate_l, plate_w, plate_t], center = true);
    for (x = [-trolley_pitch/2, trolley_pitch/2])
      for (y = [-trolley_pitch/2, trolley_pitch/2])
        translate([x, y, 0])
          cylinder(h = plate_t + 2, d = trolley_hole, center = true);
  }
}

module arm(side = 1) {
  // side: +1 right, -1 left (Y)
  y0 = side * pivot_spacing / 2;
  rotate([0, 0, side * open_angle])
  translate([0, y0, pivot_z]) {
    // pivot boss
    rotate([90, 0, 0])
      cylinder(h = arm_t, d = 12, center = true);
    // arm bar toward football (+X)
    translate([arm_len / 2, 0, 0])
      cube([arm_len, arm_t, arm_w], center = true);
    // pad
    translate([arm_len, 0, 0])
      cube([pad_t, pad_w, pad_l], center = true);
    // aft horn for brake strike
    translate([-horn_aft / 2, 0, arm_w / 2])
      cube([horn_aft, arm_t, horn_h], center = true);
  }
}

module football_proxy() {
  // visual only — long axis along X
  color("orange", 0.35)
    translate([arm_len * 0.55, 0, pivot_z + 10])
      scale([1.4, 0.85, 0.85])
        sphere(d = closed_gap);
}

module assembly() {
  color("silver") plate();
  color("steelblue") arm(+1);
  color("steelblue") arm(-1);
  football_proxy();
  // brake face (rail-end, reference)
  color("crimson", 0.5)
    translate([-plate_l / 2 - 20, 0, 40])
      cube([8, 30, 50], center = true);
}

assembly();
