// Prints the shared CSV produced by 05_ui_prototypes/_shared/prepare_data.py.
// The path is resolved relative to this file, not to the working directory.
import {readFileSync} from "node:fs";

process.stdout.write(readFileSync(new URL("../../../../_shared/data/overview.csv", import.meta.url)));
