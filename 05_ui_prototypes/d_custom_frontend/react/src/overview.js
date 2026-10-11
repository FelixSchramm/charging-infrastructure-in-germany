// Calculation logic from 05_ui_prototypes/README.md ("Rechenlogik").

export const CATEGORIES = [
  { key: "hpc", label: "HPC-Laden (>= 150 kW)", color: "#00B092" },
  { key: "schnell", label: "Schnellladen (> 22 kW)", color: "#003247" },
  { key: "normal", label: "Normalladen (<= 22 kW)", color: "#D3D3D3" },
];

const FIRST_YEAR = 2010;

/**
 * Compute KPIs and yearly additions for one filter selection.
 * @param {object[]} rows - Parsed rows of overview.csv.
 * @param {string|null} state - Selected federal state, null for all.
 * @param {string[]} types - Selected category keys.
 * @returns {object} KPIs, sorted years and points per year and category.
 */
export function computeOverview(rows, state, types) {
  const kpis = { stationen: 0, ladepunkte: 0, hpc: 0, kw: 0 };
  const perYear = new Map();
  for (const row of rows) {
    if (state && row.bundesland !== state) continue;
    // A station counts as soon as one of its charging points matches.
    if (types.some((k) => row[`has_${k}`])) {
      kpis.stationen += row.stationen;
      kpis.kw += row.kw;
    }
    for (const k of types) kpis.ladepunkte += row[`lp_${k}`];
    if (types.includes("hpc")) kpis.hpc += row.lp_hpc;
    if (row.jahr < FIRST_YEAR) continue;
    const year = perYear.get(row.jahr) ?? { hpc: 0, schnell: 0, normal: 0 };
    for (const k of types) year[k] += row[`lp_${k}`];
    perYear.set(row.jahr, year);
  }
  const years = [...perYear.keys()].sort((a, b) => a - b);
  return { kpis, years, perYear: years.map((y) => perYear.get(y)) };
}
