part="sole"; // [sole,upper_fuzzy,upper_infill]
y0=198;
len=24;
zmax=22;
module clip(){ translate([-90,y0,-3]) cube([180,len,zmax+6]); }
intersection(){
  clip();
  if(part=="sole") import("v6_sole_left.3mf", convexity=20);
  else if(part=="upper_fuzzy") import("v6_1_upper_fuzzy_shell_left.stl", convexity=20);
  else import("v6_1_upper_infill_envelope_left.stl", convexity=20);
}
