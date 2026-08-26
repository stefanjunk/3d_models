/*
FDM Mechanical Sample Library
Portable OpenSCAD mechanism primitives and sample assemblies.
Units: millimetres. Designed around 0.4 mm nozzle / 0.2 mm layers.
License: MIT for code; generated geometry CC0-1.0.
*/

$fn = is_undef($fn) ? 48 : $fn;

// ---------- General helpers ----------
module rounded_box(size=[20,10,3], r=2, center=false) {
    sx=size[0]; sy=size[1]; sz=size[2];
    rr=min(r,min(sx,sy)/2-0.01);
    translate(center ? [-sx/2,-sy/2,-sz/2] : [0,0,0])
        hull()
            for (x=[rr,sx-rr], y=[rr,sy-rr])
                translate([x,y,0]) cylinder(r=rr,h=sz);
}

module rounded_plate_c(size=[20,10,3], r=2) {
    translate([-size[0]/2,-size[1]/2,0]) rounded_box(size=size,r=r);
}

module ring_z(od=10,id=5,h=5) {
    difference() {
        cylinder(d=od,h=h);
        translate([0,0,-0.1]) cylinder(d=id,h=h+0.2);
    }
}

module cylinder_x(d=4,l=10,center=true,fn=32) {
    rotate([0,90,0]) cylinder(d=d,h=l,center=center,$fn=fn);
}
module cylinder_y(d=4,l=10,center=true,fn=32) {
    rotate([90,0,0]) cylinder(d=d,h=l,center=center,$fn=fn);
}

module hex_prism(flat=5.5,h=3,center=false) {
    cylinder(r=flat/sqrt(3),h=h,center=center,$fn=6);
}

module pin_z(d=4,l=16,head_d=7,head_h=1.5,tip=0.7) {
    union() {
        cylinder(d=head_d,h=head_h);
        translate([0,0,head_h]) cylinder(d=d,h=max(0.1,l-head_h-tip));
        translate([0,0,l-tip]) cylinder(d1=d,d2=max(0.5,d-2*tip),h=tip);
    }
}

module beam2d(p1=[0,0],p2=[10,0],w=1.2) {
    hull() {
        translate(p1) circle(d=w,$fn=24);
        translate(p2) circle(d=w,$fn=24);
    }
}

module polyline_prism(points=[[0,0],[10,0]],w=1.2,h=2) {
    linear_extrude(height=h)
        union()
            for (i=[0:len(points)-2])
                beam2d(points[i],points[i+1],w);
}

module prism_x(poly=[[0,0],[1,0],[1,1],[0,1]],length=10) {
    n=len(poly);
    pts=concat(
        [for(p=poly) [0,p[0],p[1]]],
        [for(p=poly) [length,p[0],p[1]]]
    );
    f0=[for(i=[0:n-1]) n-1-i];
    f1=[for(i=[0:n-1]) n+i];
    fs=[for(i=[0:n-1]) [i,(i+1)%n,n+(i+1)%n,n+i]];
    polyhedron(points=pts,faces=concat([f0],[f1],fs),convexity=10);
}

module dovetail_x(length=40,w_bottom=12,w_top=8,h=5) {
    prism_x([[-w_bottom/2,0],[w_bottom/2,0],[w_top/2,h],[-w_top/2,h]],length);
}

module mushroom_rail_x(length=40,stem_w=6,head_w=12,stem_h=3,head_h=3,chamfer=1.5) {
    union() {
        translate([0,-stem_w/2,0]) cube([length,stem_w,stem_h+0.05]);
        prism_x([
            [-head_w/2+chamfer,stem_h],
            [ head_w/2-chamfer,stem_h],
            [ head_w/2,stem_h+chamfer],
            [ head_w/2,stem_h+head_h],
            [-head_w/2,stem_h+head_h],
            [-head_w/2,stem_h+chamfer]
        ],length);
    }
}

module simple_gear(teeth=16,module_size=1.5,thickness=5,bore=4,hub_d=0,hub_h=0) {
    root_r=max(module_size*teeth/2-1.25*module_size,2);
    outer_r=module_size*teeth/2+module_size;
    root_w=2*PI*root_r/teeth*0.58;
    tip_w=2*PI*outer_r/teeth*0.28;
    difference() {
        union() {
            cylinder(r=root_r,h=thickness);
            for(i=[0:teeth-1])
                rotate([0,0,i*360/teeth])
                    linear_extrude(height=thickness)
                        polygon([
                            [root_r-0.25,-root_w/2],
                            [outer_r,-tip_w/2],
                            [outer_r, tip_w/2],
                            [root_r-0.25, root_w/2]
                        ]);
            if(hub_d>0 && hub_h>0)
                translate([0,0,thickness]) cylinder(d=hub_d,h=hub_h);
        }
        translate([0,0,-0.1]) cylinder(d=bore,h=thickness+hub_h+0.2);
    }
}

module rack_bar(teeth=18,module_size=1.5,width=8,base_h=4,tooth_h=1.5) {
    pitch=PI*module_size;
    length=teeth*pitch;
    union() {
        cube([length,width,base_h]);
        for(i=[0:teeth-1])
            translate([i*pitch,width/2,base_h-0.18])
                rotate([90,0,0])
                    linear_extrude(height=width,center=true)
                        polygon([
                            [0,0],
                            [pitch*0.23,tooth_h],
                            [pitch*0.57,tooth_h],
                            [pitch*0.80,0]
                        ]);
    }
}

module external_thread(d=16,pitch=3,length=16,depth=1.1,bore=0) {
    core_d=d-2*depth;
    difference() {
        union() {
            cylinder(d=core_d,h=length);
            linear_extrude(
                height=length,
                twist=360*length/pitch,
                slices=max(32,ceil(length/pitch*20)),
                convexity=12
            )
                translate([core_d/2-0.02,0])
                    polygon([
                        [0,-pitch*0.22],
                        [depth,-pitch*0.10],
                        [depth, pitch*0.10],
                        [0, pitch*0.22]
                    ]);
        }
        if(bore>0) translate([0,0,-0.1]) cylinder(d=bore,h=length+0.2);
    }
}

module thread_nut(d=16,pitch=3,length=8,depth=1.1,clearance=0.3,flat=24) {
    difference() {
        hex_prism(flat=flat,h=length);
        translate([0,0,-0.1])
            external_thread(d=d+2*clearance,pitch=pitch,length=length+0.2,depth=depth,bore=0);
    }
}

module color_a() { color([0.15,0.48,0.85]) children(); }
module color_b() { color([0.95,0.48,0.12]) children(); }
module color_c() { color([0.20,0.72,0.46]) children(); }
module color_d() { color([0.68,0.30,0.78]) children(); }
module color_hw(){ color([0.32,0.34,0.38]) children(); }

// ---------- 01: Removable pin hinge, offset planar leaves ----------
module pin_hinge_leaf(side=1,pin_d=4,clearance=0.25,leaf_l=28,leaf_w=18,leaf_t=3,knuckle_h=6,wall=2.2) {
    hole=pin_d+2*clearance;
    od=hole+2*wall;
    union() {
        translate([side*(od/2+leaf_l/2-wall*0.7),0,0])
            rounded_plate_c([leaf_l,leaf_w,leaf_t],2.2);
        ring_z(od=od,id=hole,h=knuckle_h);
        if(side>0)
            translate([od/2-wall*0.8,-wall/2,0]) cube([leaf_l*0.18+wall,wall,knuckle_h]);
        else
            translate([-od/2-leaf_l*0.18-wall+wall*0.8,-wall/2,0]) cube([leaf_l*0.18+wall,wall,knuckle_h]);
    }
}
module sample_pin_hinge(view="plate",clearance=0.25,pin_d=4,leaf_l=28) {
    h=6; ac=max(0.2,clearance);
    if(view=="assembly") {
        color_a() pin_hinge_leaf(1,pin_d,clearance,leaf_l);
        color_b() translate([0,0,h+ac]) rotate([0,0,145]) pin_hinge_leaf(-1,pin_d,clearance,leaf_l);
        color_hw() translate([0,0,-0.5]) pin_z(pin_d,2*h+ac+2,head_d=pin_d+3);
    } else {
        color_a() translate([20,18,0]) pin_hinge_leaf(1,pin_d,clearance,leaf_l);
        color_b() translate([20+2*leaf_l+24,18,0]) pin_hinge_leaf(-1,pin_d,clearance,leaf_l);
        color_hw() translate([20+2*leaf_l+48,18,0]) pin_z(pin_d,2*h+ac+2,head_d=pin_d+3);
    }
}

// ---------- 02: Print-in-place planar pivot ----------
module pip_outer_pivot(clearance=0.25,core_d=8,h=6,wall=2.2,leaf_l=28,leaf_w=16) {
    od=core_d+2*clearance+2*wall;
    gap_w=3.2+2*clearance;
    union() {
        difference() {
            ring_z(od=od,id=core_d+2*clearance,h=h);
            translate([0,-gap_w/2,-0.1]) cube([od, gap_w,h+0.2]);
        }
        translate([-od/2-leaf_l+wall*0.8,-leaf_w/2,0]) rounded_box([leaf_l,leaf_w,3],2);
    }
}
module pip_inner_pivot(core_d=8,h=6,arm_w=3,leaf_l=28,leaf_w=16) {
    union() {
        cylinder(d=core_d,h=h);
        translate([0,-arm_w/2,0]) cube([core_d/2+leaf_l,arm_w,3]);
        translate([core_d/2+leaf_l/2,-leaf_w/2,0]) rounded_box([leaf_l,leaf_w,3],2);
    }
}
module sample_pip_pivot(view="plate",clearance=0.25,core_d=8) {
    if(view=="assembly") {
        color_a() pip_outer_pivot(clearance,core_d);
        color_b() rotate([0,0,32]) pip_inner_pivot(core_d);
    } else {
        translate([42,26,0]) {
            color_a() pip_outer_pivot(clearance,core_d);
            color_b() pip_inner_pivot(core_d);
        }
    }
}

// ---------- 03: Thin-section flexure hinge ----------
module sample_flexure_hinge(view="plate",beam_t=0.8,beam_w=12,gap=8,plate=[28,24,3]) {
    module body() {
        union() {
            translate([-gap/2-plate[0],-plate[1]/2,0]) rounded_box(plate,2.5);
            translate([ gap/2,-plate[1]/2,0]) rounded_box(plate,2.5);
            translate([-gap/2-2,-beam_w/2,(plate[2]-beam_t)/2]) cube([gap+4,beam_w,beam_t]);
            translate([-gap/2-4,-beam_w/2,0]) cube([4,beam_w,plate[2]]);
            translate([ gap/2,-beam_w/2,0]) cube([4,beam_w,plate[2]]);
        }
    }
    color_a() translate(view=="assembly"?[0,0,0]:[36,20,0]) body();
}

// ---------- 04: Serpentine living hinge ----------
module serpentine_bridge(gap=22,beam_w=1.2,h=2.4,yoff=0,amp=4) {
    pts=[[-gap/2, yoff],[-gap/3,yoff+amp],[-gap/6,yoff-amp],[0,yoff+amp],[gap/6,yoff-amp],[gap/3,yoff+amp],[gap/2,yoff]];
    polyline_prism(pts,beam_w,h);
}
module sample_serpentine_hinge(view="plate",beam_w=1.2,gap=22,plate=[26,28,2.4]) {
    module body() union() {
        translate([-gap/2-plate[0],-plate[1]/2,0]) rounded_box(plate,2.5);
        translate([ gap/2,-plate[1]/2,0]) rounded_box(plate,2.5);
        serpentine_bridge(gap,beam_w,plate[2],-5,4);
        serpentine_bridge(gap,beam_w,plate[2], 5,4);
    }
    color_a() translate(view=="assembly"?[0,0,0]:[38,22,0]) body();
}

// ---------- 05: Snap-assembled universal joint ----------
module universal_cross(pin_d=4,span=22,center=6) {
    union() {
        translate([-center/2,-center/2,0]) cube([center,center,pin_d]);
        translate([0,0,pin_d/2]) cylinder_x(pin_d,span,true,12);
        translate([0,0,pin_d/2]) cylinder_y(pin_d,span,true,12);
    }
}
module universal_yoke(axis="y",pin_d=4,clearance=0.3,span=22,arm_l=24,arm_t=5) {
    hole=pin_d+2*clearance;
    if(axis=="y") {
        difference() {
            union() {
                translate([-arm_l,-span/2-arm_t/2,0]) cube([arm_l,arm_t,9]);
                translate([-arm_l, span/2-arm_t/2,0]) cube([arm_l,arm_t,9]);
                translate([-arm_l-7,-span/2-arm_t/2,0]) cube([8,span+arm_t,4]);
            }
            for(y=[-span/2,span/2]) {
                translate([0,y,pin_d/2+1]) cylinder_y(hole,arm_t+0.4,true,18);
                translate([-hole*0.28,y-arm_t/2-0.2,pin_d/2+1]) cube([hole*0.56,arm_t+0.4,9]);
            }
        }
    } else rotate([0,0,90]) universal_yoke("y",pin_d,clearance,span,arm_l,arm_t);
}
module sample_universal_joint(view="plate",clearance=0.3,pin_d=4) {
    if(view=="assembly") {
        color_a() universal_yoke("y",pin_d,clearance);
        color_b() universal_yoke("x",pin_d,clearance);
        color_c() translate([0,0,1]) universal_cross(pin_d);
    } else {
        color_a() translate([34,25,0]) universal_yoke("y",pin_d,clearance);
        color_b() translate([82,25,0]) universal_yoke("y",pin_d,clearance);
        color_c() translate([58,58,0]) universal_cross(pin_d);
    }
}

// ---------- 06: Pinned two-axis gimbal ----------
module square_frame(outer=42,inner=30,h=4,r=2) {
    difference() {
        rounded_plate_c([outer,outer,h],r);
        translate([0,0,-0.1]) rounded_plate_c([inner,inner,h+0.2],max(0.6,r-0.6));
    }
}
module gimbal_outer(pin_d=4,clearance=0.25,outer=44,inner=32) {
    hole=pin_d+2*clearance;
    difference() {
        union() {
            square_frame(outer,inner,4,3);
            for(x=[-outer/2+4,outer/2-4]) translate([x,0,5]) cube([8,10,10],center=true);
        }
        for(x=[-outer/2+4,outer/2-4]) translate([x,0,4.5]) cylinder_x(hole,10.5,true,18);
    }
}
module gimbal_inner(pin_d=4,clearance=0.25,outer=30,inner=20) {
    hole=pin_d+2*clearance;
    difference() {
        union() {
            square_frame(outer,inner,4,2.5);
            for(x=[-outer/2-3,outer/2+3]) translate([x,0,4.5]) cylinder_x(pin_d+3,6,true,18);
            for(y=[-outer/2+3,outer/2-3]) translate([0,y,5.5]) cube([10,7,11],center=true);
        }
        for(y=[-outer/2+3,outer/2-3]) translate([0,y,5]) cylinder_y(hole,8,true,18);
    }
}
module gimbal_platform(pin_d=4,outer=18) {
    union() {
        rounded_plate_c([outer,outer,4],3);
        translate([0,0,5]) cylinder_y(pin_d,outer+8,true,18);
    }
}
module gimbal_pin(pin_d=4,l=54) { pin_z(pin_d,l,head_d=pin_d+3,head_h=1.2,tip=0.8); }
module sample_gimbal_joint(view="plate",clearance=0.25,pin_d=4) {
    if(view=="assembly") {
        color_a() gimbal_outer(pin_d,clearance);
        color_b() rotate([12,0,0]) gimbal_inner(pin_d,clearance);
        color_c() rotate([12,0,16]) gimbal_platform(pin_d);
        color_hw() rotate([0,90,0]) translate([0,0,-27]) gimbal_pin(pin_d,54);
        color_hw() rotate([90,0,0]) translate([0,0,-19]) gimbal_pin(pin_d,38);
    } else {
        color_a() translate([30,30,2]) gimbal_outer(pin_d,clearance);
        color_b() translate([84,28,0]) gimbal_inner(pin_d,clearance);
        color_c() translate([84,66,0]) gimbal_platform(pin_d);
        color_hw() translate([16,70,0]) gimbal_pin(pin_d,54);
        color_hw() translate([28,70,0]) gimbal_pin(pin_d,38);
    }
}

// ---------- 07: XY compliant stage ----------
module sample_xy_flexure_stage(view="plate",beam_w=1.0,beam_l=17,frame=52,platform=18,h=3) {
    module body() union() {
        difference() {
            rounded_plate_c([frame,frame,h],3);
            translate([0,0,-0.1]) rounded_plate_c([frame-10,frame-10,h+0.2],2);
        }
        rounded_plate_c([platform,platform,h],2.5);
        // Four folded beams, two per axis.
        polyline_prism([[-platform/2, -6],[-platform/2-beam_l/2,-6],[-platform/2-beam_l/2,-16],[-frame/2+5,-16]],beam_w,h);
        polyline_prism([[-platform/2,  6],[-platform/2-beam_l/2, 6],[-platform/2-beam_l/2, 16],[-frame/2+5, 16]],beam_w,h);
        polyline_prism([[ platform/2, -6],[ platform/2+beam_l/2,-6],[ platform/2+beam_l/2,-16],[ frame/2-5,-16]],beam_w,h);
        polyline_prism([[ platform/2,  6],[ platform/2+beam_l/2, 6],[ platform/2+beam_l/2, 16],[ frame/2-5, 16]],beam_w,h);
        polyline_prism([[-6,-platform/2],[-6,-platform/2-beam_l/2],[-16,-platform/2-beam_l/2],[-16,-frame/2+5]],beam_w,h);
        polyline_prism([[ 6,-platform/2],[ 6,-platform/2-beam_l/2],[ 16,-platform/2-beam_l/2],[ 16,-frame/2+5]],beam_w,h);
        polyline_prism([[-6, platform/2],[-6, platform/2+beam_l/2],[-16, platform/2+beam_l/2],[-16, frame/2-5]],beam_w,h);
        polyline_prism([[ 6, platform/2],[ 6, platform/2+beam_l/2],[ 16, platform/2+beam_l/2],[ 16, frame/2-5]],beam_w,h);
    }
    color_a() translate(view=="assembly"?[0,0,0]:[32,32,0]) body();
}

// ---------- 08: Slotted snap ball joint ----------
module ball_stud(ball_d=14,stem_d=6,stem_h=10,base=[24,20,3]) {
    union() {
        rounded_plate_c(base,2.5);
        cylinder(d1=stem_d+4,d2=stem_d,h=4);
        translate([0,0,3.8]) cylinder(d=stem_d,h=stem_h);
        translate([0,0,3.8+stem_h]) sphere(d=ball_d);
    }
}
module snap_ball_socket(ball_d=14,clearance=0.35,wall=2.2,opening_ratio=0.78,base=[26,22,3]) {
    inner=ball_d+2*clearance;
    outer=inner+2*wall;
    ri=inner/2; ro=outer/2;
    cz=base[2]+ro-wall*0.72;
    zopen=cz+ri*sqrt(max(0.01,1-opening_ratio*opening_ratio));
    union() {
        rounded_plate_c(base,2.5);
        difference() {
            intersection() {
                translate([0,0,cz]) difference() { sphere(d=outer); sphere(d=inner); }
                translate([-outer,-outer,base[2]-0.25]) cube([2*outer,2*outer,zopen-base[2]+0.25]);
            }
            for(a=[0:90:270])
                rotate([0,0,a])
                    translate([-0.65,-outer,cz-0.2]) cube([1.3,2*outer,zopen-cz+1.2]);
        }
    }
}
module sample_snap_ball_joint(view="plate",ball_d=14,clearance=0.35) {
    if(view=="assembly") {
        color_a() snap_ball_socket(ball_d,clearance);
        color_b() translate([0,0,3]) rotate([18,0,12]) ball_stud(ball_d);
    } else {
        color_a() translate([28,24,0]) snap_ball_socket(ball_d,clearance);
        color_b() translate([72,24,0]) ball_stud(ball_d);
    }
}

// ---------- 09: Split clamp ball joint ----------
module clamp_socket_half(ball_d=16,clearance=0.25,wall=4,half=1,bolt_d=3.4,nut_flat=5.7) {
    sx=ball_d+2*wall+14; sy=ball_d+2*wall; sz=ball_d/2+wall;
    difference() {
        translate([-sx/2,-sy/2,0]) rounded_box([sx,sy,sz],3);
        translate([0,0,ball_d/2+wall*0.45]) sphere(d=ball_d+2*clearance);
        translate([0,0,-0.1]) cylinder(d=ball_d*0.45,h=sz+0.2);
        for(x=[-sx/2+5,sx/2-5]) {
            translate([x,0,-0.1]) cylinder(d=bolt_d,h=sz+0.2,$fn=24);
            if(half<0) translate([x,0,sz-2.4]) hex_prism(nut_flat,2.6);
        }
    }
}
module sample_clamp_ball_joint(view="plate",ball_d=16,clearance=0.25,bolt_d=3.4,nut_flat=5.7) {
    if(view=="assembly") {
        color_a() clamp_socket_half(ball_d,clearance,4,1,bolt_d,nut_flat);
        color_b() translate([0,0,ball_d+8]) rotate([180,0,0]) clamp_socket_half(ball_d,clearance,4,-1,bolt_d,nut_flat);
        color_c() translate([0,0,4]) ball_stud(ball_d,6,12,[26,20,3]);
    } else {
        color_a() translate([28,24,0]) clamp_socket_half(ball_d,clearance,4,1,bolt_d,nut_flat);
        color_b() translate([72,24,0]) clamp_socket_half(ball_d,clearance,4,-1,bolt_d,nut_flat);
        color_c() translate([50,62,0]) ball_stud(ball_d,6,10,[24,18,3]);
    }
}

// ---------- 10: Press-fit dowel connector ----------
module pressfit_male(pin_d=8,pin_h=14,plate=[28,24,4]) {
    union() {
        rounded_plate_c(plate,2.5);
        translate([0,0,plate[2]]) cylinder(d1=pin_d+1.2,d2=pin_d,h=1.2);
        translate([0,0,plate[2]+1.2]) cylinder(d=pin_d,h=pin_h-2.2);
        translate([0,0,plate[2]+pin_h-1]) cylinder(d1=pin_d,d2=pin_d-1.5,h=1);
    }
}
module pressfit_female(pin_d=8,gap=0,depth=14,plate=[28,24,18]) {
    difference() {
        rounded_plate_c(plate,2.5);
        translate([0,0,plate[2]-depth]) cylinder(d=pin_d+2*gap,h=depth+0.1);
        translate([0,0,plate[2]-1.2]) cylinder(d1=pin_d+2*gap,d2=pin_d+2*gap+2,h=1.3);
    }
}
module sample_pressfit_dowel(view="plate",pin_d=8,gap=0) {
    if(view=="assembly") {
        color_a() pressfit_female(pin_d,gap);
        color_b() translate([0,0,20]) rotate([180,0,0]) pressfit_male(pin_d);
    } else {
        color_a() translate([26,22,0]) pressfit_female(pin_d,gap);
        color_b() translate([66,22,0]) pressfit_male(pin_d);
    }
}

// ---------- 11: Keyed plug/socket ----------
module keyed_plug(body=[26,22,4],plug=[12,10,13],key=[2.2,2.0]) {
    union() {
        rounded_plate_c(body,2.5);
        translate([-plug[0]/2,-plug[1]/2,body[2]]) cube(plug);
        translate([plug[0]/2-0.1,-key[0]/2,body[2]+2]) cube([key[1],key[0],plug[2]-3]);
        translate([-plug[0]/2-0.8,-plug[1]/2-0.8,body[2]])
            difference(){cube([plug[0]+1.6,plug[1]+1.6,1.2]); translate([0,0,0]) cube([0,0,0]);}
    }
}
module keyed_socket(clearance=0.25,body=[30,26,18],plug=[12,10,13],key=[2.2,2.0]) {
    difference() {
        rounded_plate_c(body,2.5);
        translate([-plug[0]/2-clearance,-plug[1]/2-clearance,body[2]-plug[2]-0.1])
            cube([plug[0]+2*clearance,plug[1]+2*clearance,plug[2]+0.2]);
        translate([plug[0]/2-clearance,-key[0]/2-clearance,body[2]-plug[2]+1.8])
            cube([key[1]+2*clearance,key[0]+2*clearance,plug[2]-2]);
        translate([-plug[0]/2-clearance-0.8,-plug[1]/2-clearance-0.8,body[2]-1.3])
            cube([plug[0]+2*clearance+1.6,plug[1]+2*clearance+1.6,1.4]);
    }
}
module sample_keyed_plug_socket(view="plate",clearance=0.25) {
    if(view=="assembly") {
        color_a() keyed_socket(clearance);
        color_b() translate([0,0,18]) rotate([180,0,0]) keyed_plug();
    } else {
        color_a() translate([28,24,0]) keyed_socket(clearance);
        color_b() translate([68,24,0]) keyed_plug();
    }
}

// ---------- 12: One-way barbed connector ----------
module barb_pin(pin_d=7,length=20,barb_h=1.0,barbs=3,base=[25,22,4]) {
    union() {
        rounded_plate_c(base,2.5);
        translate([0,0,base[2]]) cylinder(d=pin_d,h=length);
        for(i=[0:barbs-1])
            translate([0,0,base[2]+5+i*4]) cylinder(d1=pin_d+2*barb_h,d2=pin_d,h=2.5);
        translate([0,0,base[2]+length]) cylinder(d1=pin_d,d2=pin_d-2,h=1.5);
    }
}
module barb_socket(pin_d=7,clearance=0.25,depth=20,wall=5,slots=4) {
    od=pin_d+2*wall;
    difference() {
        union() {
            rounded_plate_c([30,26,4],2.5);
            translate([0,0,4]) cylinder(d=od,h=depth+2);
        }
        translate([0,0,3.9]) cylinder(d=pin_d+2*clearance,h=depth+2.2);
        for(a=[0:360/slots:359]) rotate([0,0,a]) translate([-0.55,0,10]) cube([1.1,od,depth+10]);
    }
}
module sample_barbed_connector(view="plate",clearance=0.25,pin_d=7,barb_h=1.0) {
    if(view=="assembly") {
        color_a() barb_socket(pin_d,clearance);
        color_b() translate([0,0,29]) rotate([180,0,0]) barb_pin(pin_d,20,barb_h);
    } else {
        color_a() translate([28,24,0]) barb_socket(pin_d,clearance);
        color_b() translate([66,24,0]) barb_pin(pin_d,20,barb_h);
    }
}

// ---------- 13: Dovetail joiner ----------
module dovetail_male(length=42,w_bottom=13,w_top=9,h=5,base_w=24,base_h=3) {
    union() {
        translate([0,-base_w/2,0]) cube([length,base_w,base_h]);
        translate([0,0,base_h]) dovetail_x(length,w_bottom,w_top,h);
    }
}
module dovetail_female(length=42,w_bottom=13,w_top=9,h=5,clearance=0.25,base_w=25,base_h=10) {
    difference() {
        translate([0,-base_w/2,0]) cube([length,base_w,base_h]);
        translate([-0.1,0,base_h-h-0.1])
            dovetail_x(length+0.2,w_bottom+2*clearance,w_top+2*clearance,h+0.2);
    }
}
module sample_dovetail_joiner(view="plate",clearance=0.2,length=42) {
    if(view=="assembly") {
        color_a() dovetail_female(length=length,clearance=clearance);
        color_b() translate([length*0.35,0,7]) dovetail_male(length=length);
    } else {
        color_a() translate([8,20,0]) dovetail_female(length=length,clearance=clearance);
        color_b() translate([8,55,0]) dovetail_male(length=length);
    }
}

// ---------- 14: Tongue-and-groove with transverse wedge ----------
module wedge_key(length=24,w0=7,w1=5,h=6) {
    prism_x([[-w0/2,0],[w0/2,0],[w1/2,h],[-w1/2,h]],length);
}
module tongue_part(clearance=0.25,length=34) {
    union() {
        translate([0,-13,0]) cube([length,26,4]);
        translate([4,-6,4]) cube([length-8,12,7]);
        translate([length*0.58,-8,7]) cube([7,16,6]);
    }
}
module groove_part(clearance=0.25,length=34) {
    difference() {
        translate([0,-15,0]) cube([length,30,15]);
        translate([3.8,-6-clearance,7.8]) cube([length-7.6,12+2*clearance,7.3]);
        translate([length*0.58-clearance,-9,6.8]) cube([7+2*clearance,18,8.4]);
    }
}
module sample_wedge_lock_joint(view="plate",clearance=0.25) {
    if(view=="assembly") {
        color_a() groove_part(clearance);
        color_b() translate([0,0,4]) tongue_part(clearance);
        color_c() translate([19,-12,8]) rotate([0,0,90]) wedge_key(24,7,5,6);
    } else {
        color_a() translate([10,24,0]) groove_part(clearance);
        color_b() translate([58,24,0]) tongue_part(clearance);
        color_c() translate([36,60,0]) wedge_key(24,7,5,6);
    }
}

// ---------- 15: Screw boss with captured hex nut ----------
module nuttrap_base(screw_d=3.4,nut_flat=5.7,nut_h=2.5,boss_d=12,boss_h=10) {
    difference() {
        union() {
            rounded_plate_c([30,26,4],3);
            cylinder(d=boss_d,h=4+boss_h);
        }
        translate([0,0,-0.1]) cylinder(d=screw_d,h=4+boss_h+0.2,$fn=24);
        translate([0,0,4+boss_h-nut_h]) hex_prism(nut_flat,nut_h+0.2);
        translate([0,-nut_flat/2,4+boss_h-nut_h]) cube([boss_d,nut_flat,nut_h+0.3]);
    }
}
module screw_lid(screw_d=3.4,head_d=6.5) {
    difference() {
        rounded_plate_c([30,26,4],3);
        translate([0,0,-0.1]) cylinder(d=screw_d,h=4.2,$fn=24);
        translate([0,0,2.2]) cylinder(d=head_d,h=2,$fn=24);
    }
}
module sample_nuttrap_screw(view="plate",screw_d=3.4,nut_flat=5.7,nut_h=2.5,head_d=6.5) {
    if(view=="assembly") {
        color_a() nuttrap_base(screw_d,nut_flat,nut_h);
        color_b() translate([0,0,14.5]) screw_lid(screw_d,head_d);
    } else {
        color_a() translate([28,22,0]) nuttrap_base(screw_d,nut_flat,nut_h);
        color_b() translate([68,22,0]) screw_lid(screw_d,head_d);
    }
}

// ---------- 16: Heat-set insert coupon ----------
module insert_base(pilot_d=4.1,insert_depth=6,boss_d=13) {
    difference() {
        union() {
            rounded_plate_c([30,26,4],3);
            cylinder(d=boss_d,h=12);
        }
        translate([0,0,12-insert_depth]) cylinder(d=pilot_d,h=insert_depth+0.2,$fn=32);
        translate([0,0,-0.1]) cylinder(d=max(1.8,pilot_d-1.4),h=12-insert_depth+0.2,$fn=24);
        translate([0,0,10.8]) cylinder(d1=pilot_d+1.0,d2=pilot_d,h=1.3,$fn=32);
    }
}
module insert_lid(screw_clear=3.4,head_d=6.5) {
    difference() {
        rounded_plate_c([30,26,4],3);
        translate([0,0,-0.1]) cylinder(d=screw_clear,h=4.2,$fn=24);
        translate([0,0,2.1]) cylinder(d=head_d,h=2.1,$fn=24);
    }
}
module sample_heatset_insert(view="plate",pilot_d=4.1,screw_clear=3.4,head_d=6.5,insert_depth=6) {
    if(view=="assembly") {
        color_a() insert_base(pilot_d,insert_depth);
        color_b() translate([0,0,12.5]) insert_lid(screw_clear,head_d);
    } else {
        color_a() translate([28,22,0]) insert_base(pilot_d,insert_depth);
        color_b() translate([68,22,0]) insert_lid(screw_clear,head_d);
    }
}

// ---------- 17: Coarse printed thread pair ----------
module threaded_bolt(d=16,pitch=3,length=16,depth=1.1,head_flat=24) {
    union() {
        hex_prism(head_flat,5);
        translate([0,0,5]) external_thread(d,pitch,length,depth);
        translate([0,0,5+length]) cylinder(d1=d-2*depth,d2=d-2*depth-1,h=1);
    }
}
module sample_printed_thread(view="plate",d=16,pitch=3,clearance=0.3,length=16) {
    depth=max(0.8,pitch*0.36); flat=d+8;
    if(view=="assembly") {
        color_a() thread_nut(d,pitch,9,depth,clearance,flat);
        color_b() translate([0,0,-8]) threaded_bolt(d,pitch,length,depth,flat);
    } else {
        color_a() translate([28,24,0]) thread_nut(d,pitch,9,depth,clearance,flat);
        color_b() translate([70,24,0]) threaded_bolt(d,pitch,length,depth,flat);
    }
}

// ---------- 18: Cantilever snap latch ----------
module snap_male(beam_t=1.2,clearance=0.25,beam_l=24,beam_w=10,hook=2.0) {
    union() {
        rounded_plate_c([28,24,4],3);
        translate([-beam_w/2,8,4]) cube([beam_w,beam_l,beam_t]);
        translate([-beam_w/2,8+beam_l-hook,4+beam_t])
            prism_x([[-beam_w/2,0],[beam_w/2,0],[beam_w/2,hook],[-beam_w/2,hook]],beam_w);
        translate([-beam_w/2,8+beam_l-hook,4]) cube([beam_w,hook,beam_t+hook]);
    }
}
module snap_female(beam_w=10,hook=2,clearance=0.25) {
    difference() {
        rounded_plate_c([32,28,8],3);
        translate([-beam_w/2-clearance,-14,-0.1]) cube([beam_w+2*clearance,20,8.2]);
        translate([-beam_w/2-clearance-hook,-2,4]) cube([beam_w+2*clearance+2*hook,8,4.2]);
    }
}
module sample_cantilever_snap(view="plate",beam_t=1.2,clearance=0.25,hook=2.0) {
    if(view=="assembly") {
        color_a() snap_female(10,hook,clearance);
        color_b() translate([0,-35,0]) snap_male(beam_t,clearance,24,10,hook);
    } else {
        color_a() translate([28,24,0]) snap_female(10,hook,clearance);
        color_b() translate([70,24,0]) snap_male(beam_t,clearance,24,10,hook);
    }
}

// ---------- 19: Rotating hook latch ----------
module hook_base(pin_d=4,clearance=0.25) {
    hole=pin_d+2*clearance;
    union() {
        rounded_plate_c([34,28,4],3);
        translate([0,0,4]) ring_z(od=hole+5,id=hole,h=6);
    }
}
module hook_lever(pin_d=4,clearance=0.25,arm=34,hook_depth=6) {
    hole=pin_d+2*clearance;
    union() {
        ring_z(od=hole+5,id=hole,h=5);
        translate([0,-4,0]) cube([arm,8,5]);
        translate([arm-4,-4,0]) cube([5,8,10]);
        translate([arm-10,-4,7]) cube([10,8,3]);
        translate([-12,-6,0]) rounded_box([14,12,5],3);
    }
}
module hook_catch() {
    union() {
        rounded_plate_c([24,24,4],3);
        translate([-8,-7,4]) cube([16,14,9]);
        translate([-10,-9,9]) cube([20,18,4]);
    }
}
module sample_hook_latch(view="plate",pin_d=4,clearance=0.25,arm=34) {
    if(view=="assembly") {
        color_a() hook_base(pin_d,clearance);
        color_b() translate([0,0,4.3]) rotate([0,0,18]) hook_lever(pin_d,clearance,arm);
        color_c() translate([arm+5,0,0]) hook_catch();
        color_hw() translate([0,0,-0.4]) pin_z(pin_d,17,head_d=pin_d+3);
    } else {
        color_a() translate([24,22,0]) hook_base(pin_d,clearance);
        color_b() translate([63,22,0]) hook_lever(pin_d,clearance,arm);
        color_c() translate([32,60,0]) hook_catch();
        color_hw() translate([58,60,0]) pin_z(pin_d,17,head_d=pin_d+3);
    }
}

// ---------- 20: Bayonet quarter-turn connection ----------
module bayonet_plug(core_d=18,lug_w=5,lug_h=3,stem_h=18,clearance=0.25) {
    union() {
        rounded_plate_c([32,28,4],3);
        translate([0,0,4]) cylinder(d=core_d,h=stem_h);
        for(a=[0,180]) rotate([0,0,a]) translate([core_d/2-0.2,-lug_w/2,4+stem_h-5]) cube([lug_h+1,lug_w,4]);
        translate([0,0,4+stem_h]) cylinder(d1=core_d,d2=core_d-2,h=1.2);
    }
}
module bayonet_socket(core_d=18,lug_w=5,lug_h=3,stem_h=18,clearance=0.25,wall=4) {
    id=core_d+2*clearance; od=id+2*wall;
    difference() {
        union() {
            rounded_plate_c([36,32,4],3);
            translate([0,0,4]) cylinder(d=od,h=stem_h+3);
        }
        translate([0,0,3.9]) cylinder(d=id,h=stem_h+3.2);
        for(a=[0,180]) rotate([0,0,a]) {
            translate([id/2-0.2,-lug_w/2-clearance,4+stem_h-7]) cube([wall+lug_h+1,lug_w+2*clearance,10]);
            translate([-lug_w/2-clearance,id/2-0.2,4+stem_h-7]) cube([lug_w+2*clearance,wall+lug_h+1,4+2*clearance]);
        }
    }
}
module sample_bayonet(view="plate",core_d=18,clearance=0.25,lug_w=5) {
    if(view=="assembly") {
        color_a() bayonet_socket(core_d,lug_w,3,18,clearance);
        color_b() translate([0,0,8]) rotate([0,0,35]) bayonet_plug(core_d,lug_w,3,18,clearance);
    } else {
        color_a() translate([28,24,0]) bayonet_socket(core_d,lug_w,3,18,clearance);
        color_b() translate([74,24,0]) bayonet_plug(core_d,lug_w,3,18,clearance);
    }
}

// ---------- 21: Sliding bolt latch ----------
module slide_bolt_base(clearance=0.25,bolt_w=10,bolt_h=5,travel=28) {
    union() {
        rounded_plate_c([58,26,4],3);
        for(y=[-bolt_w/2-clearance-2,bolt_w/2+clearance])
            translate([-travel/2-8,y,4]) cube([travel+16,2,bolt_h+3]);
        for(x=[-travel/2-8,travel/2+5])
            translate([x,-bolt_w/2-clearance-2,4+bolt_h]) cube([5,bolt_w+2*clearance+4,2]);
    }
}
module slide_bolt(clearance=0.25,bolt_w=10,bolt_h=5,length=46) {
    union() {
        translate([-length/2,-bolt_w/2,0]) rounded_box([length,bolt_w,bolt_h],1.5);
        translate([-4,-bolt_w/2-8,bolt_h-0.1]) rounded_box([8,bolt_w+16,4],2);
        translate([length/2-1.5,-bolt_w/2+1,1]) cube([4,bolt_w-2,bolt_h-2]);
    }
}
module bolt_keep(bolt_w=10,bolt_h=5,clearance=0.25) {
    difference() {
        rounded_plate_c([24,26,12],3);
        translate([-12,-bolt_w/2-clearance,4]) cube([24,bolt_w+2*clearance,bolt_h+2*clearance]);
    }
}
module sample_slide_bolt(view="plate",clearance=0.25,bolt_w=10,bolt_h=5) {
    if(view=="assembly") {
        color_a() slide_bolt_base(clearance,bolt_w,bolt_h);
        color_b() translate([-6,0,5]) slide_bolt(clearance,bolt_w,bolt_h);
        color_c() translate([45,0,0]) bolt_keep(bolt_w,bolt_h,clearance);
    } else {
        color_a() translate([38,20,0]) slide_bolt_base(clearance,bolt_w,bolt_h);
        color_b() translate([38,55,0]) slide_bolt(clearance,bolt_w,bolt_h);
        color_c() translate([88,25,0]) bolt_keep(bolt_w,bolt_h,clearance);
    }
}

// ---------- 22: Dovetail linear rail ----------
module sample_dovetail_rail(view="plate",clearance=0.3,length=70,carriage_l=26) {
    module rail() union() {
        translate([0,-11,0]) cube([length,22,3]);
        translate([0,0,3]) dovetail_x(length,14,9,5);
        translate([0,-11,3]) cube([2,22,4]);
        translate([length-2,-11,3]) cube([2,22,4]);
    }
    module carriage() difference() {
        translate([0,-13,0]) rounded_box([carriage_l,26,11],2.5);
        translate([-0.1,0,2.8]) dovetail_x(carriage_l+0.2,14+2*clearance,9+2*clearance,5.4);
        translate([-0.1,-9,0]) cube([carriage_l+0.2,18,3.1]);
    }
    if(view=="assembly") {
        color_a() rail();
        color_b() translate([22,0,0]) carriage();
    } else {
        color_a() translate([8,18,0]) rail();
        color_b() translate([30,55,0]) carriage();
    }
}

// ---------- 23: Mushroom/T linear rail ----------
module sample_t_rail(view="plate",clearance=0.3,length=70,carriage_l=26) {
    module rail() union() {
        translate([0,-12,0]) cube([length,24,3]);
        translate([0,0,3]) mushroom_rail_x(length,6,14,3,3,1.5);
    }
    module carriage() difference() {
        translate([0,-15,0]) rounded_box([carriage_l,30,13],2.5);
        translate([-0.1,0,2.8]) mushroom_rail_x(carriage_l+0.2,6+2*clearance,14+2*clearance,3.2,3.2,1.5);
        translate([-0.1,-4,0]) cube([carriage_l+0.2,8,3.2]);
    }
    if(view=="assembly") {
        color_a() rail();
        color_b() translate([25,0,0]) carriage();
    } else {
        color_a() translate([8,18,0]) rail();
        color_b() translate([30,58,0]) carriage();
    }
}

// ---------- 24: Compliant-preload box slider ----------
module preload_rail(length=70,w=14,h=10) {
    union() {
        translate([0,-w/2,0]) cube([length,w,h]);
        translate([0,-w/2-3,0]) cube([length,w+6,3]);
    }
}
module preload_carriage(clearance=0.3,rail_w=14,rail_h=10,length=30,beam_t=1.0) {
    outer_w=rail_w+2*clearance+8;
    difference() {
        union() {
            translate([0,-outer_w/2,0]) rounded_box([length,outer_w,rail_h+7],2.5);
            // two spring pads attached from roof
            for(x=[7,length-7])
                translate([x-3,-rail_w/2+1,rail_h+1]) cube([6,rail_w-2,beam_t]);
        }
        translate([-0.1,-rail_w/2-clearance,2.9]) cube([length+0.2,rail_w+2*clearance,rail_h+clearance+0.2]);
        // release slots isolate the spring beams
        for(x=[7,length-7]) {
            translate([x-4,-rail_w/2+0.5,rail_h+1+beam_t]) cube([8,rail_w-1,5]);
            translate([x-4,-rail_w/2+0.5,rail_h-1]) cube([1.2,rail_w-1,4]);
            translate([x+2.8,-rail_w/2+0.5,rail_h-1]) cube([1.2,rail_w-1,4]);
        }
    }
}
module sample_preload_slider(view="plate",clearance=0.3,beam_t=1.0) {
    if(view=="assembly") {
        color_a() preload_rail();
        color_b() translate([22,0,0]) preload_carriage(clearance,14,10,30,beam_t);
    } else {
        color_a() translate([8,20,0]) preload_rail();
        color_b() translate([32,58,0]) preload_carriage(clearance,14,10,30,beam_t);
    }
}

// ---------- 25: Rack and pinion drive ----------
module rack_base(teeth=16,module_size=1.5,width=8) {
    rack_bar(teeth,module_size,width,4,module_size);
}
module pinion_with_handle(teeth=16,module_size=1.5,thickness=6,bore=4) {
    union() {
        simple_gear(teeth,module_size,thickness,bore,hub_d=bore+5,hub_h=3);
        translate([0,0,thickness+3]) rounded_plate_c([18,6,4],2);
    }
}
module rack_axle(pin_d=4,l=18) { pin_z(pin_d,l,head_d=pin_d+3); }
module sample_rack_pinion(view="plate",teeth=16,module_size=1.5,clearance=0.25) {
    pin_d=4; rack_len=teeth*PI*module_size;
    if(view=="assembly") {
        color_a() rack_base(teeth,module_size,10);
        color_b() translate([rack_len/2, -module_size*teeth/2-1,4]) pinion_with_handle(teeth,module_size,6,pin_d+2*clearance);
        color_hw() translate([rack_len/2,-module_size*teeth/2-1,0]) rack_axle(pin_d,18);
    } else {
        color_a() translate([8,18,0]) rack_base(teeth,module_size,10);
        color_b() translate([rack_len+28,28,0]) pinion_with_handle(teeth,module_size,6,pin_d+2*clearance);
        color_hw() translate([rack_len+50,28,0]) rack_axle(pin_d,18);
    }
}

// ---------- 26: Spur gear pair on a pin base ----------
module gear_base(center_distance=34,pin_d=4,pin_h=12) {
    union() {
        rounded_plate_c([center_distance+28,30,4],3);
        for(x=[-center_distance/2,center_distance/2]) translate([x,0,4]) cylinder(d=pin_d,h=pin_h);
    }
}
module sample_spur_gears(view="plate",teeth_a=14,teeth_b=22,module_size=1.5,clearance=0.25) {
    cd=module_size*(teeth_a+teeth_b)/2;
    pin_d=4; bore=pin_d+2*clearance;
    if(view=="assembly") {
        color_a() gear_base(cd,pin_d,11);
        color_b() translate([-cd/2,0,4.3]) simple_gear(teeth_a,module_size,6,bore,hub_d=9,hub_h=2);
        color_c() translate([ cd/2,0,4.3]) simple_gear(teeth_b,module_size,6,bore,hub_d=9,hub_h=2);
    } else {
        color_a() translate([40,22,0]) gear_base(cd,pin_d,11);
        color_b() translate([22,72,0]) simple_gear(teeth_a,module_size,6,bore,hub_d=9,hub_h=2);
        color_c() translate([76,72,0]) simple_gear(teeth_b,module_size,6,bore,hub_d=9,hub_h=2);
    }
}

// ---------- 27: Rotary detent indexer ----------
module detent_disk(notches=12,d=40,h=5,bore=4.5,notch_d=4) {
    difference() {
        cylinder(d=d,h=h);
        translate([0,0,-0.1]) cylinder(d=bore,h=h+0.2);
        for(a=[0:360/notches:359]) rotate([0,0,a]) translate([d/2,0,-0.1]) cylinder(d=notch_d,h=h+0.2,$fn=24);
    }
}
module detent_base(disk_d=40,pin_d=4,beam_t=1.2,notch_d=4) {
    union() {
        rounded_plate_c([disk_d+34,disk_d+18,4],3);
        cylinder(d=pin_d,h=11);
        translate([disk_d/2-2,-3,4]) cube([18,6,beam_t]);
        translate([disk_d/2+13,-4,4]) cube([5,8,6]);
        translate([disk_d/2-4,-4,4+beam_t]) cylinder(d=notch_d*0.78,h=4,$fn=24);
    }
}
module sample_detent_indexer(view="plate",notches=12,beam_t=1.2,clearance=0.25) {
    d=40; pin=4; bore=pin+2*clearance;
    if(view=="assembly") {
        color_a() detent_base(d,pin,beam_t);
        color_b() translate([0,0,4.4]) detent_disk(notches,d,5,bore,4);
    } else {
        color_a() translate([42,28,0]) detent_base(d,pin,beam_t);
        color_b() translate([42,76,0]) detent_disk(notches,d,5,bore,4);
    }
}

// ---------- 28: Two-piece shaft coupler ----------
module coupler_half(bore_d=6,clearance=0.2,length=32,outer_w=24,outer_h=12,screw_d=3.4,nut_flat=5.7,nut_side=false) {
    difference() {
        translate([-length/2,-outer_w/2,0]) rounded_box([length,outer_w,outer_h],3);
        translate([0,0,outer_h]) cylinder_x(bore_d+2*clearance,length+0.2,true,32);
        translate([0,0,outer_h-0.01]) cube([length+0.2,outer_w+0.2,outer_h],center=true);
        for(x=[-length/2+6,length/2-6]) {
            translate([x,0,-0.1]) cylinder(d=screw_d,h=outer_h+0.2,$fn=24);
            if(nut_side) translate([x,0,outer_h-2.6]) hex_prism(nut_flat,2.8);
        }
    }
}
module test_shaft(d=6,length=24) { cylinder(d=d,h=length,$fn=32); }
module sample_shaft_coupler(view="plate",bore_d=6,clearance=0.2,screw_d=3.4,nut_flat=5.7) {
    if(view=="assembly") {
        color_a() coupler_half(bore_d,clearance,32,24,12,screw_d,nut_flat,false);
        color_b() translate([0,0,24]) rotate([180,0,0]) coupler_half(bore_d,clearance,32,24,12,screw_d,nut_flat,true);
        color_c() translate([-18,0,12]) rotate([0,90,0]) test_shaft(bore_d,36);
        color_d() translate([18,0,12]) rotate([0,-90,0]) test_shaft(bore_d,36);
    } else {
        color_a() translate([28,22,0]) coupler_half(bore_d,clearance,32,24,12,screw_d,nut_flat,false);
        color_b() translate([70,22,0]) coupler_half(bore_d,clearance,32,24,12,screw_d,nut_flat,true);
        color_c() translate([24,60,0]) test_shaft(bore_d,24);
        color_d() translate([40,60,0]) test_shaft(bore_d,24);
    }
}

// ---------- 29: Reusable cable snap clip ----------
module cable_clip(cable_d=6,clearance=0.3,wall=2.0,base=[28,20,3],opening=3.5) {
    id=cable_d+2*clearance; od=id+2*wall;
    clip_w=10;
    opening_eff=max(opening,cable_d*0.45);
    cz=base[2]+od/2-wall*0.55;
    union() {
        rounded_plate_c(base,2.5);
        translate([0,0,cz])
            difference() {
                cylinder_y(od,clip_w,true,48);
                cylinder_y(id,clip_w+0.2,true,48);
                translate([-opening_eff/2,-clip_w,0]) cube([opening_eff,2*clip_w,od]);
            }
        // reinforced feet keep the ring connected to the mounting plate
        for(x=[-od*0.30,od*0.30])
            translate([x-1.2,-clip_w/2,base[2]-0.2]) cube([2.4,clip_w,wall+0.8]);
    }
}
module sample_cable_clip(view="plate",cable_d=6,clearance=0.3,wall=2.0) {
    color_a() translate(view=="assembly"?[0,0,0]:[28,22,0]) cable_clip(cable_d,clearance,wall);
}

// ---------- 30: Pulley block ----------
module pulley_wheel(rope_d=3,outer_d=28,width=8,bore=4.5) {
    difference() {
        union() {
            cylinder(d=outer_d-2,h=width);
            translate([0,0,width/2]) rotate_extrude($fn=48)
                translate([outer_d/2-1,0]) circle(d=rope_d+1,$fn=24);
        }
        translate([0,0,-0.1]) cylinder(d=bore,h=width+0.2,$fn=32);
    }
}
module pulley_bracket(outer_d=28,width=8,pin_d=4,clearance=0.25) {
    gap=width+2*clearance;
    hole=pin_d+2*clearance;
    difference() {
        union() {
            rounded_plate_c([outer_d+16,24,4],3);
            for(y=[-gap/2-3,gap/2]) translate([-outer_d/2-3,y,4]) cube([outer_d+6,3,outer_d/2+8]);
            translate([-8,-gap/2-3,outer_d/2+8]) cube([16,gap+6,5]);
        }
        translate([0,0,4+outer_d/2]) cylinder_y(hole,gap+8,true,24);
        translate([0,0,outer_d/2+8]) cylinder(d=6,h=6,$fn=24);
    }
}
module sample_pulley_block(view="plate",rope_d=3,outer_d=28,pin_d=4,clearance=0.25) {
    width=8;
    if(view=="assembly") {
        color_a() pulley_bracket(outer_d,width,pin_d,clearance);
        color_b() translate([0,0,4+outer_d/2-width/2]) rotate([90,0,0]) pulley_wheel(rope_d,outer_d,width,pin_d+2*clearance);
        color_hw() translate([0,-(width+2*clearance+8)/2,4+outer_d/2]) rotate([90,0,0]) pin_z(pin_d,width+2*clearance+8,head_d=pin_d+3);
    } else {
        wheel_x=outer_d+50;
        pin_x=wheel_x+outer_d/2+12;
        color_a() translate([34,24,0]) pulley_bracket(outer_d,width,pin_d,clearance);
        color_b() translate([wheel_x,24,0]) pulley_wheel(rope_d,outer_d,width,pin_d+2*clearance);
        color_hw() translate([pin_x,24,0]) pin_z(pin_d,width+2*clearance+8,head_d=pin_d+3);
    }
}

// ---------- 31: Radial O-ring shaft gland ----------
module nominal_oring(oring_id=10,oring_cs=2) {
    rotate_extrude($fn=64)
        translate([oring_id/2+oring_cs/2,0]) circle(d=oring_cs,$fn=24);
}
module radial_gland_body(shaft_d=3,oring_id=3,oring_cs=1.5,radial_squeeze=0.12,clearance=0.2,land_l=10,lead_in=1.2,grease_reservoir=1.2,wall=3) {
    bore=shaft_d+2*clearance;
    pocket_d=shaft_d+2*oring_cs*(1-radial_squeeze);
    boss_d=pocket_d+2*wall;
    seat_d=boss_d-1.4;
    pocket_h=oring_cs*1.15;
    pocket_z=4+land_l-pocket_h;
    difference() {
        union() {
            rounded_plate_c([34,30,4],3);
            translate([0,0,3.9]) cylinder(d=boss_d,h=land_l+0.1);
        }
        translate([0,0,-0.1]) cylinder(d=bore,h=4+land_l+0.3);
        translate([0,0,-0.1]) cylinder(d1=bore+2*lead_in,d2=bore,h=lead_in+0.2);
        translate([0,0,pocket_z]) cylinder(d=pocket_d,h=pocket_h+0.2);
        translate([0,0,pocket_z-grease_reservoir])
            cylinder(d=pocket_d+0.8,h=grease_reservoir+0.2);
        translate([0,0,4+land_l-1.3]) cylinder(d=seat_d,h=1.5);
    }
}
module radial_gland_retainer(shaft_d=3,oring_cs=1.5,radial_squeeze=0.12,clearance=0.2,wall=3) {
    pocket_d=shaft_d+2*oring_cs*(1-radial_squeeze);
    boss_d=pocket_d+2*wall;
    difference() {
        union() {
            cylinder(d=boss_d+2,h=1.4);
            translate([0,0,1.35]) cylinder(d=boss_d-1.8,h=1.1);
        }
        translate([0,0,-0.1]) cylinder(d=shaft_d+2*clearance,h=2.7);
    }
}
module sample_radial_shaft_gland(view="plate",shaft_d=3,oring_id=3,oring_cs=1.5,radial_squeeze=0.12,clearance=0.2,land_l=10,lead_in=1.2,grease_reservoir=1.2,wall=3) {
    assert(shaft_d>0 && oring_id>0 && oring_cs>=1,"shaft and O-ring dimensions must be positive");
    assert(radial_squeeze>=0.05 && radial_squeeze<=0.30,"radial_squeeze must be 0.05..0.30");
    assert(clearance>=0.1 && clearance<=0.6,"clearance must be 0.1..0.6 mm per side");
    assert(land_l>oring_cs*2+grease_reservoir+1,"land_l is too short for gland and reservoir");
    assert(lead_in>=0.4 && wall>=2,"lead-in and wall are below the FDM baseline");
    assert(abs(oring_id-shaft_d)<=oring_cs*0.6,"nominal O-ring ID is incompatible with the shaft coupon");
    pocket_d=shaft_d+2*oring_cs*(1-radial_squeeze); boss_d=pocket_d+2*wall;
    pocket_z=4+land_l-oring_cs*1.15;
    if(view=="assembly") {
        color_a() radial_gland_body(shaft_d,oring_id,oring_cs,radial_squeeze,clearance,land_l,lead_in,grease_reservoir,wall);
        color_b() translate([0,0,4+land_l-1.3]) radial_gland_retainer(shaft_d,oring_cs,radial_squeeze,clearance,wall);
        color_c() translate([0,0,pocket_z+oring_cs*0.58]) nominal_oring(oring_id,oring_cs);
        color_hw() translate([0,0,-2]) pin_z(shaft_d,25,head_d=shaft_d+3);
    } else {
        color_a() translate([28,24,0]) radial_gland_body(shaft_d,oring_id,oring_cs,radial_squeeze,clearance,land_l,lead_in,grease_reservoir,wall);
        color_b() translate([58,24,0]) radial_gland_retainer(shaft_d,oring_cs,radial_squeeze,clearance,wall);
        color_hw() translate([78,24,0]) pin_z(shaft_d,25,head_d=shaft_d+3);
    }
}

// ---------- 32: O-ring-preloaded ramped bayonet ----------
module ramped_bayonet_plug(core_d=24,running_clearance=0.3,lug_w=6,oring_id=21,oring_cs=2,radial_squeeze=0.15,stem_h=20) {
    groove_depth=max(0.7,oring_cs*(1-radial_squeeze)-running_clearance);
    difference() {
        union() {
            cylinder(d=core_d+10,h=4);
            translate([0,0,4]) cylinder(d=core_d,h=stem_h);
            for(a=[0,180])
                rotate([0,0,a]) translate([core_d/2-0.2,-lug_w/2,4+stem_h-5])
                    cube([4,lug_w,3.2]);
            translate([0,0,4+stem_h]) cylinder(d1=core_d,d2=core_d-2,h=1.2);
        }
        translate([0,0,8]) rotate_extrude($fn=48)
            translate([core_d/2-groove_depth,0]) square([groove_depth+0.2,oring_cs*1.15]);
    }
}
module ramped_bayonet_channel(id=24.6,wall=4,lug_w=6,running_clearance=0.3,z0=16,ramp_h=0.8,turn_deg=42) {
    // Axial entry plus a swept rising channel; short overhangs remain printable.
    translate([id/2-0.2,-lug_w/2-running_clearance,z0])
        cube([wall+5,lug_w+2*running_clearance,11]);
    hull() {
        translate([id/2-0.2,-lug_w/2-running_clearance,z0])
            cube([wall+5,lug_w+2*running_clearance,3.4+2*running_clearance]);
        rotate([0,0,turn_deg]) translate([id/2-0.2,-lug_w/2-running_clearance,z0+ramp_h])
            cube([wall+5,lug_w+2*running_clearance,3.4+2*running_clearance]);
    }
}
module ramped_bayonet_socket(core_d=24,running_clearance=0.3,lug_w=6,ramp_h=0.8,turn_deg=42,stem_h=20,wall=4,hard_stop=1.5) {
    id=core_d+2*running_clearance; od=id+2*wall; z0=4+stem_h-8;
    union() {
        difference() {
            union() {
                rounded_plate_c([44,40,4],3);
                translate([0,0,4]) cylinder(d=od,h=stem_h+3);
            }
            translate([0,0,3.9]) cylinder(d=id,h=stem_h+3.3);
            for(a=[0,180]) rotate([0,0,a])
                ramped_bayonet_channel(id,wall,lug_w,running_clearance,z0,ramp_h,turn_deg);
        }
        // Positive terminal lands provide a repeatable rotational hard stop.
        for(a=[0,180]) rotate([0,0,a+turn_deg])
            translate([id/2-0.8,lug_w/2+running_clearance-hard_stop-0.4,z0+ramp_h-0.2])
                cube([wall+1.6,hard_stop+0.8,3.8+2*running_clearance]);
    }
}
module sample_ramped_bayonet(view="plate",core_d=24,running_clearance=0.3,lug_w=6,ramp_h=0.8,turn_deg=42,oring_id=21,oring_cs=2,radial_squeeze=0.15,hard_stop=1.5) {
    groove_depth=oring_cs*(1-radial_squeeze)-running_clearance;
    assert(core_d>=16 && lug_w>=4,"core or lug dimensions are below the FDM baseline");
    assert(running_clearance>=0.2 && running_clearance<=0.7,"running_clearance must be 0.2..0.7 mm per side");
    assert(radial_squeeze>=0.05 && radial_squeeze<=0.30,"radial_squeeze must be 0.05..0.30");
    assert(groove_depth>=0.7,"O-ring groove would be too shallow");
    assert(ramp_h>=0.3 && ramp_h<=2.0 && turn_deg>=25 && turn_deg<=70,"ramp travel is outside the sample range");
    assert(hard_stop>=0.8 && hard_stop<=lug_w/2,"hard_stop is outside the printable range");
    assert(oring_id>0 && oring_cs>=1,"O-ring dimensions must be positive");
    if(view=="assembly") {
        color_a() ramped_bayonet_socket(core_d,running_clearance,lug_w,ramp_h,turn_deg,20,4,hard_stop);
        color_b() translate([0,0,7]) rotate([0,0,35])
            ramped_bayonet_plug(core_d,running_clearance,lug_w,oring_id,oring_cs,radial_squeeze);
        color_c() translate([0,0,7+8+oring_cs*0.58]) nominal_oring(oring_id,oring_cs);
    } else {
        color_a() translate([30,28,0]) ramped_bayonet_socket(core_d,running_clearance,lug_w,ramp_h,turn_deg,20,4,hard_stop);
        color_b() translate([78,28,0]) ramped_bayonet_plug(core_d,running_clearance,lug_w,oring_id,oring_cs,radial_squeeze);
    }
}

// ---------- 33: Compact asymmetric micro-shaft coupler ----------
module micro_coupler_body(input_d=3,output_d=4,input_clearance=0.15,output_clearance=0.18,length=18,outer_d=12,fastener=2.4,axial_stop=0.8) {
    difference() {
        cylinder(d=outer_d,h=length);
        translate([0,0,-0.1]) cylinder(d=input_d+2*input_clearance,h=length/2-axial_stop/2+0.1);
        translate([0,0,length/2+axial_stop/2]) cylinder(d=output_d+2*output_clearance,h=length/2-axial_stop/2+0.2);
        translate([0,-0.55,-0.1]) cube([outer_d/2+1,1.1,length+0.2]);
        for(z=[length*0.25,length*0.75])
            translate([outer_d*0.29,0,z]) cylinder_y(fastener,outer_d+2,true,24);
    }
}
module shaft_gauge(d=3,h=24) { pin_z(d,h,head_d=d+3,head_h=1.5,tip=0.5); }
module sample_micro_shaft_coupler(view="plate",input_d=3,output_d=4,input_clearance=0.15,output_clearance=0.18,length=18,outer_d=12,fastener=2.4,axial_stop=0.8) {
    assert(input_d>0 && output_d>0 && length>=14,"shaft diameters and length must be positive");
    assert(input_clearance>=0.1 && input_clearance<=0.5,"input_clearance must be 0.1..0.5 mm per side");
    assert(output_clearance>=0.1 && output_clearance<=0.5,"output_clearance must be 0.1..0.5 mm per side");
    assert(outer_d>=max(input_d,output_d)+5,"outer_d leaves insufficient clamp wall");
    assert(fastener>=1.8 && fastener<=3.2,"fastener clearance is outside the M2/M2.5 sample range");
    assert(axial_stop>=0.4 && axial_stop<=2,"axial_stop must be 0.4..2 mm");
    if(view=="assembly") {
        color_a() translate([0,0,20]) micro_coupler_body(input_d,output_d,input_clearance,output_clearance,length,outer_d,fastener,axial_stop);
        color_c() shaft_gauge(input_d,29);
        color_d() translate([0,0,20+length-1]) shaft_gauge(output_d,29);
    } else {
        color_a() translate([28,24,0]) micro_coupler_body(input_d,output_d,input_clearance,output_clearance,length,outer_d,fastener,axial_stop);
        color_c() translate([50,24,0]) shaft_gauge(input_d,24);
        color_d() translate([68,24,0]) shaft_gauge(output_d,24);
    }
}

// ---------- 34: Crank pin to slotted rocker oscillator ----------
module oscillator_base(pivot_offset=18,post_d=4,base_t=4) {
    difference() {
        rounded_plate_c([pivot_offset+54,46,base_t],3);
        translate([0,17,-0.1]) cylinder(d=5,h=base_t+0.2,$fn=24);
    }
    for(x=[-pivot_offset/2,pivot_offset/2])
        translate([x,0,base_t]) cylinder(d=post_d,h=9,$fn=32);
}
module oscillator_crank(crank_r=6,post_d=4,pin_d=4,plate_t=3) {
    difference() {
        union() {
            cylinder(d=2*(crank_r+5),h=plate_t);
            translate([crank_r,0,plate_t-0.1]) cylinder(d=pin_d,h=6,$fn=32);
            translate([crank_r,0,plate_t+5.7]) cylinder(d=pin_d+2.4,h=1.3,$fn=32);
        }
        translate([0,0,-0.1]) cylinder(d=post_d+0.5,h=plate_t+0.2,$fn=32);
    }
}
module oscillator_rocker(crank_r=6,pivot_offset=18,slot_w=5.8,post_d=4,rocker_r=24,plate_t=3) {
    difference() {
        linear_extrude(height=plate_t)
            hull() {
                circle(r=7,$fn=32);
                translate([-pivot_offset,0]) circle(r=slot_w/2+3,$fn=32);
                translate([rocker_r,0]) circle(r=6,$fn=32);
            }
        translate([0,0,-0.1]) cylinder(d=post_d+0.5,h=plate_t+0.2,$fn=32);
        hull() {
            translate([-pivot_offset-crank_r-2,0,-0.1]) cylinder(d=slot_w,h=plate_t+0.2,$fn=32);
            translate([-pivot_offset+crank_r+2,0,-0.1]) cylinder(d=slot_w,h=plate_t+0.2,$fn=32);
        }
        translate([rocker_r,0,-0.1]) cylinder(d=3.2,h=plate_t+0.2,$fn=24);
    }
}
module sample_crank_rocker(view="plate",crank_r=6,pivot_offset=18,slot_w=5.8,pin_d=4,rocker_r=24,plate_t=3) {
    assert(crank_r>=2 && pivot_offset>crank_r+8,"crank radius and pivot offset are incompatible");
    assert(slot_w>=pin_d+0.8,"slot_w needs at least 0.4 mm radial pin clearance");
    assert(rocker_r>=pivot_offset && plate_t>=2.4,"rocker radius or plate thickness is below the sample range");
    if(view=="assembly") {
        color_a() oscillator_base(pivot_offset,4,4);
        color_b() translate([-pivot_offset/2,0,4.3]) oscillator_crank(crank_r,4,pin_d,plate_t);
        color_c() translate([pivot_offset/2,0,4+plate_t+0.7]) oscillator_rocker(crank_r,pivot_offset,slot_w,4,rocker_r,plate_t);
    } else {
        color_a() translate([40,28,0]) oscillator_base(pivot_offset,4,4);
        color_b() translate([92,20,0]) oscillator_crank(crank_r,4,pin_d,plate_t);
        color_c() translate([95,80,0]) oscillator_rocker(crank_r,pivot_offset,slot_w,4,rocker_r,plate_t);
    }
}

// ---------- 35: Dual O-ring friction piston ----------
module annular_groove_z(body_d=16,depth=1,width=1.8,z=2) {
    translate([0,0,z]) rotate_extrude($fn=48)
        translate([body_d/2-depth,0]) square([depth+0.15,width]);
}
module friction_piston_body(bore_d=20,travel=24,lead_in=1.2,wall=3) {
    od=bore_d+2*wall; h=travel+16;
    difference() {
        union() {
            rounded_plate_c([od+16,od+12,4],3);
            translate([0,0,3.9]) cylinder(d=od,h=h+0.1);
        }
        translate([0,0,7]) cylinder(d=bore_d,h=h+0.3);
        translate([0,0,4+h-lead_in]) cylinder(d1=bore_d,d2=bore_d+2*lead_in,h=lead_in+0.2);
        translate([0,0,4+h-1.5]) cylinder(d=od-1.4,h=1.7);
    }
}
module friction_piston(bore_d=20,travel=24,oring_id=17.5,oring_cs=1.5,groove_depth=1.08,groove_spacing=4.4,clearance=0.2,anti_loss_stop=4.5) {
    head_d=bore_d-2*clearance; stem_d=max(5,bore_d-3);
    head_h=max(11,2.2+groove_spacing+oring_cs*1.2+1); total=travel+18;
    difference() {
        union() {
            cylinder(d=head_d,h=head_h);
            translate([0,0,head_h-0.1]) cylinder(d=stem_d,h=total-head_h+0.1);
            translate([0,0,total]) cylinder(d=stem_d+2*anti_loss_stop,h=4);
        }
        annular_groove_z(head_d,groove_depth,oring_cs*1.2,2.2);
        annular_groove_z(head_d,groove_depth,oring_cs*1.2,2.2+groove_spacing);
    }
}
module friction_piston_retainer(bore_d=20,wall=3,clearance=0.2) {
    od=bore_d+2*wall; stem_d=max(5,bore_d-3);
    difference() {
        union() {
            cylinder(d=od+2,h=1.5);
            translate([0,0,1.45]) cylinder(d=od-1.8,h=1.2);
        }
        translate([0,0,-0.1]) cylinder(d=stem_d+2*clearance,h=2.9);
    }
}
module sample_friction_piston(view="plate",bore_d=20,travel=24,oring_id=17.5,oring_cs=1.5,groove_depth=1.08,groove_spacing=4.4,lead_in=1.2,anti_loss_stop=4.5,clearance=0.2) {
    body_h=travel+16;
    head_d=bore_d-2*clearance; groove_root_d=head_d-2*groove_depth;
    assert(bore_d>=10 && travel>=12,"bore and travel are below the sample range");
    assert(oring_id>0 && oring_cs>=1,"O-ring dimensions must be positive");
    assert(abs(oring_id-groove_root_d)<=oring_cs*0.7,"nominal O-ring ID is incompatible with the piston groove");
    assert(groove_depth>=oring_cs*0.5 && groove_depth<=oring_cs*0.9,"groove_depth must be 50..90% of O-ring cross-section");
    assert(groove_spacing>=oring_cs*2 && lead_in>=0.5,"groove spacing or lead-in is too small");
    assert(anti_loss_stop>=2.5 && clearance>=0.15 && clearance<=0.6,"retention or piston clearance is outside the sample range");
    if(view=="assembly") {
        color_a() friction_piston_body(bore_d,travel,lead_in,3);
        color_b() translate([0,0,8]) friction_piston(bore_d,travel,oring_id,oring_cs,groove_depth,groove_spacing,clearance,anti_loss_stop);
        color_c() translate([0,0,8+2.2+oring_cs*0.6]) nominal_oring(oring_id,oring_cs);
        color_c() translate([0,0,8+2.2+groove_spacing+oring_cs*0.6]) nominal_oring(oring_id,oring_cs);
        color_c() translate([0,0,4+body_h-1.5]) friction_piston_retainer(bore_d,3,clearance);
    } else {
        color_a() translate([30,28,0]) friction_piston_body(bore_d,travel,lead_in,3);
        color_b() translate([80,28,0]) friction_piston(bore_d,travel,oring_id,oring_cs,groove_depth,groove_spacing,clearance,anti_loss_stop);
        color_c() translate([118,28,0]) friction_piston_retainer(bore_d,3,clearance);
    }
}

// ---------- 36: Captive serviceable hinge pin ----------
module captive_hinge_pin(pin_d=4,grip_l=16,head_d=7) {
    groove_d=max(1,pin_d-1.0); groove_z=grip_l-1.8;
    difference() {
        pin_z(pin_d,grip_l+1.5,head_d=head_d,head_h=1.5,tip=0.5);
        translate([0,0,groove_z]) rotate_extrude($fn=32)
            translate([groove_d/2,0]) square([(pin_d-groove_d)/2+0.2,0.9]);
    }
}
module captive_pin_clip(pin_d=4,retainer_clearance=0.25,t=1.2) {
    id=max(1,pin_d-1.0)+2*retainer_clearance; od=id+3.2;
    difference() {
        ring_z(od,id,t);
        translate([0,-od/4,-0.1]) cube([od,od/2,t+0.2]);
    }
}
module sample_captive_hinge_pin(view="plate",pin_d=4,bearing_clearance=0.25,head_d=7,retainer_clearance=0.25,grip_l=13,leaf_l=28) {
    sep=6+2*bearing_clearance;
    assert(pin_d>=2 && pin_d<=8,"pin_d is outside the sample range");
    assert(bearing_clearance>=0.15 && bearing_clearance<=0.6,"bearing_clearance must be 0.15..0.6 mm per side");
    assert(retainer_clearance>=0.15 && retainer_clearance<=0.6,"retainer_clearance must be 0.15..0.6 mm per side");
    assert(head_d>=pin_d+2 && grip_l>=10,"head diameter or grip length is too small");
    if(view=="assembly") {
        color_a() translate([0,0,0]) pin_hinge_leaf(-1,pin_d,bearing_clearance,leaf_l,18,3,6,2.2);
        color_b() translate([0,0,sep]) pin_hinge_leaf(1,pin_d,bearing_clearance,leaf_l,18,3,6,2.2);
        color_hw() translate([0,0,-1]) captive_hinge_pin(pin_d,grip_l,head_d);
        color_c() translate([0,0,grip_l-0.8]) captive_pin_clip(pin_d,retainer_clearance,1.2);
    } else {
        color_a() translate([36,20,0]) pin_hinge_leaf(-1,pin_d,bearing_clearance,leaf_l,18,3,6,2.2);
        color_b() translate([36,50,0]) pin_hinge_leaf(1,pin_d,bearing_clearance,leaf_l,18,3,6,2.2);
        color_hw() translate([72,20,0]) captive_hinge_pin(pin_d,grip_l,head_d);
        color_c() translate([92,20,0]) captive_pin_clip(pin_d,retainer_clearance,1.2);
    }
}

// ---------- 37: Compression cable gland ----------
module cable_gland_body(cable_d=4,seal_clearance=0.3,thread_d=16,pitch=2.5,strain_relief=12,wall=3) {
    depth=max(0.8,pitch*0.36);
    difference() {
        union() {
            translate([strain_relief/2,0,0]) rounded_plate_c([34+strain_relief,30,wall],3);
            translate([0,0,wall-0.1]) external_thread(thread_d,pitch,12,depth,0);
        }
        translate([0,0,-0.1]) cylinder(d=cable_d+2*seal_clearance,h=wall+12.2);
        // Two tie passages keep cable strain out of the sealing insert.
        for(x=[17+strain_relief*0.30,17+strain_relief*0.70])
            translate([x-1.2,-5,-0.1]) cube([2.4,10,wall+0.2]);
    }
}
module cable_gland_seal(cable_d=4,seal_clearance=0.3,thread_d=16,compression_l=4.5) {
    difference() {
        ring_z(thread_d-3,cable_d+2*seal_clearance,compression_l);
        translate([0,-0.6,-0.1]) cube([thread_d/2+1,1.2,compression_l+0.2]);
    }
}
module cable_gland_nut(cable_d=4,seal_clearance=0.3,thread_d=16,pitch=2.5,compression_l=4.5,thread_clearance=0.3) {
    depth=max(0.8,pitch*0.36);
    nut_l=max(9,compression_l+4);
    thread_nut(d=thread_d,pitch=pitch,length=nut_l,depth=depth,clearance=thread_clearance,flat=thread_d+8);
}
module sample_cable_gland(view="plate",cable_d=4,seal_clearance=0.3,compression_l=4.5,thread_d=16,pitch=2.5,strain_relief=12,wall=3) {
    seal_od=thread_d-3; seal_id=cable_d+2*seal_clearance;
    assert(cable_d>=1.5 && seal_clearance>=0.2 && seal_clearance<=0.8,"cable or seal clearance is outside the sample range");
    assert(compression_l>=3 && compression_l<=8,"compression_l must be 3..8 mm");
    assert(seal_od-seal_id>=3.2,"sealing insert leaves insufficient radial material");
    assert(thread_d>=12 && pitch>=2.5 && pitch<=5,"thread dimensions are outside the validated coarse-thread family");
    assert(strain_relief>=8 && wall>=2.4,"strain-relief length or wall is below the FDM baseline");
    seal_x=62+strain_relief; nut_x=seal_x+thread_d+16;
    if(view=="assembly") {
        color_a() cable_gland_body(cable_d,seal_clearance,thread_d,pitch,strain_relief,wall);
        color_c() translate([0,0,wall+8]) cable_gland_seal(cable_d,seal_clearance,thread_d,compression_l);
        color_b() translate([0,0,wall+9]) cable_gland_nut(cable_d,seal_clearance,thread_d,pitch,compression_l,0.3);
    } else {
        color_a() translate([28,24,0]) cable_gland_body(cable_d,seal_clearance,thread_d,pitch,strain_relief,wall);
        color_c() translate([seal_x,24,0]) cable_gland_seal(cable_d,seal_clearance,thread_d,compression_l);
        color_b() translate([nut_x,24,0]) cable_gland_nut(cable_d,seal_clearance,thread_d,pitch,compression_l,0.3);
    }
}

// ---------- 38: Cylindrical cell cradle ----------
module cylindrical_cell_cradle(cell_d=10.5,cell_l=44.5,count=1,cell_gap=2,clearance=0.35,strap_w=6,contact_keepout=5,wall=2) {
    id=cell_d+2*clearance; od=id+2*wall;
    total_w=count*od+(count-1)*cell_gap+8;
    base_l=cell_l+10; base_t=3; support_l=cell_l-2*contact_keepout;
    difference() {
        union() {
            rounded_plate_c([base_l,total_w,base_t],3);
            for(i=[0:count-1]) {
                yc=(i-(count-1)/2)*(od+cell_gap);
                cz=base_t+od/2-wall*0.55;
                translate([0,yc,cz])
                    difference() {
                        cylinder_x(od,support_l,true,48);
                        cylinder_x(id,support_l+0.4,true,48);
                        translate([-support_l/2-2,-od/2-1,id*0.35]) cube([support_l+4,od+2,od]);
                    }
                for(x=[-support_l/2+2,support_l/2-4])
                    translate([x,yc-od*0.30,base_t-0.2]) cube([2.4,od*0.60,wall+0.8]);
            }
        }
        for(x=[-support_l/4-strap_w/2,support_l/4-strap_w/2])
            translate([x,-total_w/2-0.1,-0.1]) cube([strap_w,total_w+0.2,base_t+0.2]);
    }
}
module cell_diameter_gauge(cell_d=10.5,h=20) { cylinder(d=cell_d,h=h,$fn=48); }
module sample_cell_cradle(view="plate",cell_d=10.5,cell_l=44.5,count=1,cell_gap=2,clearance=0.35,strap_w=6,contact_keepout=5) {
    assert(cell_d>=8 && cell_l>=30 && count>=1 && count<=4,"cell dimensions or count are outside the sample range");
    assert(clearance>=0.25 && clearance<=0.8 && cell_gap>=1,"clearance or cell gap is outside the sample range");
    assert(strap_w>=4 && strap_w<=12,"strap_w must be 4..12 mm");
    assert(contact_keepout>=3 && contact_keepout<cell_l/3,"contact_keepout is incompatible with cell length");
    if(view=="assembly") {
        color_a() cylindrical_cell_cradle(cell_d,cell_l,count,cell_gap,clearance,strap_w,contact_keepout,2);
        for(i=[0:count-1]) {
            od=cell_d+2*clearance+4; yc=(i-(count-1)/2)*(od+cell_gap);
            color_hw() translate([0,yc,3+cell_d/2]) cylinder_x(cell_d,cell_l,true,48);
        }
    } else {
        color_a() translate([cell_l/2+10,32,0]) cylindrical_cell_cradle(cell_d,cell_l,count,cell_gap,clearance,strap_w,contact_keepout,2);
        color_hw() translate([cell_l+28,32,0]) cell_diameter_gauge(cell_d,20);
    }
}

// ---------- 39: Sealed magnetic actuator pocket ----------
module magnetic_actuator_body(wall_t=2,magnet_d=6,magnet_l=3,switch_keepout=[18,6,6],travel=20,retention=1.2,clearance=0.35) {
    total_h=6+wall_t; slider_w=16; rail_l=travel+24; base_l=max(56,rail_l+8);
    difference() {
        union() {
            rounded_plate_c([base_l,32,total_h],3);
            for(y=[-slider_w/2-clearance-2,slider_w/2+clearance])
                translate([-rail_l/2,y,total_h-0.1]) cube([rail_l,2,3.2]);
            for(x=[-rail_l/2,rail_l/2-retention])
                translate([x,-slider_w/2-clearance-2,total_h-0.1])
                    cube([retention,slider_w+2*clearance+4,3.2]);
        }
        translate([-switch_keepout[0]/2,-switch_keepout[1]/2,-0.1])
            rounded_box([switch_keepout[0],switch_keepout[1],switch_keepout[2]+0.2],1.2);
    }
}
module magnetic_actuator_slider(magnet_d=6,magnet_l=3,clearance=0.35) {
    difference() {
        rounded_plate_c([24,16,4],2.5);
        translate([0,0,4-magnet_l]) cylinder(d=magnet_d+2*clearance,h=magnet_l+0.2,$fn=32);
    }
}
module sample_magnetic_actuator(view="plate",wall_t=2,magnet_d=6,magnet_l=3,switch_keepout=[18,6,6],travel=20,retention=1.2,clearance=0.35) {
    assert(wall_t>=1 && wall_t<=6,"wall_t is outside the sample range");
    assert(magnet_d>=3 && magnet_l>=1,"magnet dimensions must be positive");
    assert(len(switch_keepout)==3 && min(switch_keepout)>0,"switch_keepout must be [length,width,height]");
    assert(travel>=8 && travel<=40,"travel must be 8..40 mm");
    assert(retention>=0.8 && retention<=2.5 && clearance>=0.25,"retention or clearance is below the FDM baseline");
    if(view=="assembly") {
        color_a() magnetic_actuator_body(wall_t,magnet_d,magnet_l,switch_keepout,travel,retention,clearance);
        color_b() translate([0,0,6+wall_t+0.4]) magnetic_actuator_slider(magnet_d,magnet_l,clearance);
    } else {
        color_a() translate([34,24,0]) magnetic_actuator_body(wall_t,magnet_d,magnet_l,switch_keepout,travel,retention,clearance);
        color_b() translate([82,24,0]) magnetic_actuator_slider(magnet_d,magnet_l,clearance);
    }
}
