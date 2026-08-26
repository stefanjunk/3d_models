---
name: cad-microtask
description: Execute one tightly bounded CAD edit, calculation, parameter sweep, or deterministic validation step. Use when the user asks for a small scoped CAD task whose inputs, allowed files, forbidden decisions, acceptance command, and output format can be stated explicitly.
---

# CAD Microtask

Load `functional-3d-design` before acting.

Treat the user's request as the bounded task. Before editing, state a compact contract containing:

- objective;
- input files and parameters;
- allowed files;
- forbidden decisions;
- acceptance command;
- output format.

Stop and report missing fields when the task cannot be bounded safely. Do not change approved requirements, select unverified safety/load/material assumptions, approve the complete design, or broaden the task.

Make the smallest coherent change, run the stated deterministic acceptance command, and return assumptions, files changed, command result, and unresolved risks.
