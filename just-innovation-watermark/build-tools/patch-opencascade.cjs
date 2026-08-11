const fs = require("node:fs");
const path = require("node:path");

const packagePath = require.resolve("replicad-opencascadejs/package.json");
const packageJson = JSON.parse(fs.readFileSync(packagePath, "utf8"));

if (packageJson.type !== "module") {
  packageJson.type = "module";
  fs.writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`);
}

const sourcePath = path.join(path.dirname(packagePath), "src", "replicad_single.js");
if (!fs.existsSync(sourcePath)) {
  throw new Error(`OpenCascade runtime not found: ${sourcePath}`);
}
