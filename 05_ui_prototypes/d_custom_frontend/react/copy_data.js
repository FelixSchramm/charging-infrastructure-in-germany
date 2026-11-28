// Vite serves public/ as-is, so the shared CSVs are copied there before dev/build.
import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const from = join(import.meta.dirname, "..", "..", "_shared", "data");
const to = join(import.meta.dirname, "public", "data");
mkdirSync(to, { recursive: true });
for (const file of ["overview.csv", "meta.csv"]) {
  copyFileSync(join(from, file), join(to, file));
}
