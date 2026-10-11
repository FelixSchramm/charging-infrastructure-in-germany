// Evidence only reads files inside sources/, so the shared CSVs are copied there.
import { copyFileSync } from "node:fs";
import { join } from "node:path";

const from = join(import.meta.dirname, "..", "..", "_shared", "data");
const to = join(import.meta.dirname, "sources", "shared");
for (const file of ["overview.csv", "meta.csv"]) {
  copyFileSync(join(from, file), join(to, file));
}
