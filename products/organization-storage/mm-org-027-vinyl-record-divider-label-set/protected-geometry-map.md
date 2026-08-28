# Protected geometry map

- `carrier-contact-faces`: both broad carrier faces remain continuous and smooth in the selected candidate.
- `carrier-perimeter`: rounded plan corners and the full-length top/bottom edges define the sleeve-contact boundary.
- `cap-top-bridge`: the 18 mm region above the U-slot keeps the cap one solid and carries assembly load.
- `slot-lands`: material beside and above every 1.9 mm production slot remains intact.
- `text-band`: engraving stays at least 2 mm above the slot and leaves at least 1.8 mm backing.
- `glyph-pixels`: no normalized batch label may fall below 0.8 mm pixel width.
- `bed-faces`: carrier, caps and coupons retain broad support-free bed faces.
- `nesting-gap`: all selected build objects retain at least 5 mm nominal XY separation.

The windowed carrier cuts only redundant central sheet area, but its added interior edges are not accepted for production until physical snagging, flatness and racking evidence exists.
