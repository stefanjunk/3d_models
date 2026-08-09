---
name: power-transmission-design
description: Use when a commercial FDM design contains gears, racks, belts, pulleys, chains, sprockets, torque transmission, rotational speed, backlash, wear, lubrication, or service-life decisions.
---

# Power Transmission Design

## Core Rule

Do not generate tooth geometry before selecting the transmission architecture
from torque, speed, duty, life, alignment, backlash, noise, lubrication, and
environment. A geometry library does not make a printed transmission suitable.

## Workflow

1. Record torque, speed, duty cycle, life, shock, ratio, center distance,
   alignment, noise, lubrication, temperature, contamination, and failure mode.
2. Run `scripts/screen_transmission.py` for a conservative print-vs-buy screen.
3. Buy belts, chains, and wear-critical mating components as standard parts.
4. Treat only large, low-speed, low-load, limited-duty gears as print
   candidates; require tooth fidelity, backlash, torque, wear, and life tests.
5. Buy small, high-speed, high-load, continuous-duty, precision, or
   safety-relevant gears unless specialist engineering proves otherwise.
6. Use a verified involute generator; never draw approximate teeth manually.

`cq_gears` remains experimental even though its license is permissive. BOSL2
gear output is allowed only from the pinned version and still requires
independent geometry and physical validation.

## Completion Gate

The screen returns architecture guidance only. `PRINT_CANDIDATE_NEEDS_TEST`
blocks commercial release until the declared mechanical tests pass.
