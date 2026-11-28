---
title: Ladeinfrastruktur in Deutschland
toc: false
---

<style>
input {
  accent-color: #00b092;
}
.kpi h2 {
  color: var(--theme-foreground-muted);
}
.kpi .big {
  color: #003247;
}
</style>

```js
const rows = FileAttachment("data/overview.csv").csv({typed: true});
const meta = FileAttachment("data/meta.csv").csv().then((d) => d[0]);
```

```js
const categories = [
  {key: "hpc", label: "HPC-Laden (>= 150 kW)", color: "#00B092"},
  {key: "schnell", label: "Schnellladen (> 22 kW)", color: "#003247"},
  {key: "normal", label: "Normalladen (<= 22 kW)", color: "#D3D3D3"}
];
const states = [...new Set(rows.map((d) => d.bundesland))].sort((a, b) => a.localeCompare(b, "de"));
const fmt = (x, digits = 0) =>
  x.toLocaleString("de-DE", {minimumFractionDigits: digits, maximumFractionDigits: digits});
```

# Ladeinfrastruktur in Deutschland

<p class="muted">Datenstand: BNetzA: ${meta.bnetza_stand} | KBA: ${meta.kba_stand} (Update: ${meta.update})</p>

<div class="grid grid-cols-2">
  <div class="card">${stateInput}</div>
  <div class="card">${typesInput}</div>
</div>

```js
const stateInput = Inputs.select(["Alle Bundesländer", ...states], {label: "Bundesland"});
const state = Generators.input(stateInput);
const typesInput = Inputs.checkbox(categories, {label: "Leistungstyp", value: categories, format: (c) => c.label});
const types = Generators.input(typesInput);
```

```js
// Calculation logic from 05_ui_prototypes/README.md.
const selected = types.map((c) => c.key);
const filtered = state === "Alle Bundesländer" ? rows : rows.filter((d) => d.bundesland === state);
const matching = filtered.filter((d) => selected.some((k) => d[`has_${k}`]));
const kpis = [
  ["Ladestationen", fmt(d3.sum(matching, (d) => d.stationen))],
  ["Ladepunkte", fmt(d3.sum(filtered, (d) => d3.sum(selected, (k) => d[`lp_${k}`])))],
  ["HPC-Ladepunkte", fmt(selected.includes("hpc") ? d3.sum(filtered, (d) => d.lp_hpc) : 0)],
  ["Gesamtleistung", `${fmt(d3.sum(matching, (d) => d.kw) / 1e6, 2)} GW`]
];
const additions = filtered
  .filter((d) => d.jahr >= 2010)
  .flatMap((d) => types.map((c) => ({jahr: d.jahr, label: c.label, lp: d[`lp_${c.key}`]})));
```

```js
function bars(title, width, options) {
  return Plot.plot({
    title,
    width,
    height: 360,
    marginLeft: 60,
    x: {label: null, tickFormat: (y) => (y % (width < 600 ? 4 : 2) ? "" : String(y))},
    y: {label: "Ladepunkte", grid: true, tickFormat: (y) => fmt(y)},
    ...options
  });
}
```

```js
display(
  selected.length === 0
    ? html`<div class="note">Bitte wähle mindestens einen Leistungstyp aus.</div>`
    : html`
      <div class="grid grid-cols-4">
        ${kpis.map(([label, value]) => html`<div class="card kpi"><h2>${label}</h2><span class="big">${value}</span></div>`)}
      </div>
      <div class="grid grid-cols-2">
        <div class="card">${resize((width) => bars("Jährlicher Zubau von Ladepunkten (Gesamt)", width, {
          marks: [Plot.barY(additions, Plot.groupX({y: "sum"}, {x: "jahr", y: "lp", fill: "#003247", tip: true}))]
        }))}</div>
        <div class="card">${resize((width) => bars("Jährlicher Zubau nach Leistungstyp", width, {
          color: {domain: types.map((c) => c.label), range: types.map((c) => c.color), legend: true},
          marks: [Plot.barY(additions, Plot.groupX({y: "sum"}, {x: "jahr", y: "lp", fill: "label", order: types.map((c) => c.label), tip: true}))]
        }))}</div>
      </div>`
);
```
