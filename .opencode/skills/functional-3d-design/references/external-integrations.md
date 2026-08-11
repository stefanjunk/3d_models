# Optional external skills, MCPs, and references

The core package does not require network access. Add integrations only when they solve a clear gap, and review permissions because CAD MCPs commonly expose local Python or shell execution.

List the manifest with:

```bash
python scripts/external_integrations.py list
```

## Recommended optional skills

### CadQuery LLM skill

Repository: `jmwright/cadquery-llm-skill`

Use for B-Rep mindset, workplanes, selectors, patterns, examples, and local documentation guidance.

### text-to-cad skill collection

Repository: `earthtojake/text-to-cad`

Relevant skills include CAD/STEP-first workflows, off-the-shelf part search, and safe slicer/G-code generation.

Do not copy the whole repository into every project. Pull only the skills needed and preserve licenses.

## Recommended MCPs

### CadQuery contrib MCP

Repository path: `CadQuery/cadquery-contrib/mcp-server`

Use for executing CadQuery scripts, rendering views, inspecting geometric properties, and exporting formats.

### build123d MCP

Useful when build123d/bd_warehouse introspection and labeled rendering are central.

### FreeCAD MCP

Use for interactive FreeCAD document control and experimental FEM automation. Restrict code-execution permissions and require human review of loads, constraints, contacts, and material models.

### Blender MCP

Use for organic mesh editing, remesh, booleans, and renders. Restrict file and Python execution to the project workspace.

### OCP viewer MCP

Useful for rendering/visual feedback for CadQuery/build123d without using Blender for precision geometry.

## OpenCode references

The package includes `config-examples/opencode.references.jsonc`, which can expose upstream repositories as read-only reference material. References are preferable to copying large documentation trees and can be searched by agents through their resolved local cache.

## Integration security checklist

- Pin a release or commit where reproducibility matters.
- Read license and dependency files.
- Start read-only; enable write/execute tools only per task.
- Deny external-directory access unless required.
- Never grant an MCP automatic printer-start permissions.
- Store generated files under the project, not arbitrary home/system paths.
- Log tool versions in the validation report.
