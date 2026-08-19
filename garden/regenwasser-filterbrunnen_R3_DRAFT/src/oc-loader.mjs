import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const localRequire = createRequire(import.meta.url);

/**
 * Load the browser-oriented replicad OpenCascade bundle in Node without
 * modifying node_modules. The upstream file is CommonJS-compatible internally
 * but ends with an ESM export, so the final line is adapted in-memory only.
 */
export async function initOpenCascadeForNode() {
  const sourcePath = localRequire.resolve("replicad-opencascadejs");
  const sourceDir = path.dirname(sourcePath);
  const originalSource = fs.readFileSync(sourcePath, "utf8");
  const withoutGlobalErrorHooks = originalSource.replace(
    /process\["on"\]\("uncaughtException",function\(ex\)\{if\(!\(ex instanceof ExitStatus\)\)\{throw ex\}\}\);process\["on"\]\("unhandledRejection",function\(reason\)\{throw reason\}\);/,
    ""
  );
  const cjsSource = withoutGlobalErrorHooks.replace(
    /export default Module;\s*$/,
    "module.exports = Module;"
  );

  if (cjsSource === originalSource) {
    throw new Error("OpenCascade loader could not adapt the upstream module export");
  }

  const adaptedModule = { exports: {} };
  const evaluate = new Function(
    "require",
    "__dirname",
    "__filename",
    "module",
    "exports",
    cjsSource
  );
  try {
    evaluate(
      localRequire,
      sourceDir,
      sourcePath,
      adaptedModule,
      adaptedModule.exports
    );
  } catch (error) {
    throw new Error(`OpenCascade bundle evaluation failed: ${error.message}`);
  }

  return adaptedModule.exports();
}
