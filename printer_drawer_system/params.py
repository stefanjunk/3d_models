"""Shared parameters for the modular 3D-printer drawer system."""

wall_t = 3.0        # wall thickness (mm)
shelf_t = 3.0       # horizontal divider thickness
clearance = 0.35    # sliding clearance per side

frame_iw = 120.0    # frame interior width
frame_id = 150.0    # frame interior depth

# Slot heights (interior, clear opening)
slot_h_std  = 30.0  # standard slot: nozzles, screws
slot_h_tall = 48.0  # tall slot: screwdrivers, pliers

# Slot layout bottom→top: [tall, std, std, std]
SLOTS = [slot_h_tall, slot_h_std, slot_h_std, slot_h_std]

frame_ih = sum(SLOTS) + (len(SLOTS) - 1) * shelf_t   # 138+9 = 147 mm
frame_ow = frame_iw + 2 * wall_t                       # 126 mm
frame_oh = frame_ih + 2 * wall_t                       # 153 mm
frame_od = frame_id + wall_t                           # 153 mm (back wall only, front open)

# Drawer body (the part that slides inside the slot)
drawer_w  = frame_iw - 2 * clearance
drawer_d  = frame_id - clearance - 2.0  # short enough to close fully
drawer_wt = 2.0     # drawer wall thickness
handle_h  = 14.0    # front-panel handle protrusion height
handle_w  = 50.0    # handle width
handle_d  = 10.0    # handle depth
fp_thick  = 4.0     # front-panel thickness (visible face)
