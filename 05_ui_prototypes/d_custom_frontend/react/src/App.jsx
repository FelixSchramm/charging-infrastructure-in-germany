import { useEffect, useMemo, useState } from "react";
import { csvParse, autoType } from "d3-dsv";
import BarChart from "./BarChart.jsx";
import { CATEGORIES, computeOverview } from "./overview.js";

const ALL = "Alle Bundesländer";
const number = new Intl.NumberFormat("de-DE");
const gw = new Intl.NumberFormat("de-DE", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/**
 * Load a CSV file copied to public/data/ by copy_data.js.
 * @param {string} name - File name.
 * @param {Function} [row] - Optional row conversion, e.g. autoType.
 * @returns {Promise<object[]>} Parsed rows.
 */
async function loadCsv(name, row) {
  const response = await fetch(`${import.meta.env.BASE_URL}data/${name}`);
  return csvParse(await response.text(), row);
}

/**
 * Build the ECharts option for a bar chart over years.
 * @param {number[]} years - Category axis values.
 * @param {object[]} series - ECharts bar series.
 * @param {boolean} legend - Whether to show the legend.
 * @returns {object} ECharts option.
 */
function chartOption(years, series, legend) {
  return {
    grid: { left: 8, right: 8, top: legend ? 48 : 16, bottom: 8, containLabel: true },
    legend: legend ? { top: 0, left: 0, icon: "roundRect" } : undefined,
    tooltip: { trigger: "axis", valueFormatter: (v) => number.format(v) },
    xAxis: { type: "category", data: years, axisTick: { show: false } },
    yAxis: { type: "value", axisLabel: { formatter: (v) => number.format(v) } },
    series,
  };
}

/**
 * Overview page: header, filters, KPIs and two yearly charts.
 */
export default function App() {
  const [rows, setRows] = useState(null);
  const [meta, setMeta] = useState(null);
  const [state, setState] = useState(ALL);
  const [types, setTypes] = useState(CATEGORIES.map((c) => c.key));

  useEffect(() => {
    // meta.csv stays untyped: autoType would turn the update date into a Date.
    Promise.all([loadCsv("overview.csv", autoType), loadCsv("meta.csv")]).then(([data, m]) => {
      setRows(data);
      setMeta(m[0]);
    });
  }, []);

  const states = useMemo(
    () => (rows ? [...new Set(rows.map((r) => r.bundesland))].sort() : []),
    [rows],
  );

  const result = useMemo(
    () => rows && computeOverview(rows, state === ALL ? null : state, types),
    [rows, state, types],
  );

  const charts = useMemo(() => {
    if (!result) return null;
    const selected = CATEGORIES.filter((c) => types.includes(c.key));
    const total = result.perYear.map((y) => types.reduce((sum, k) => sum + y[k], 0));
    return {
      total: chartOption(
        result.years,
        [{ type: "bar", data: total, itemStyle: { color: "#003247", borderRadius: [4, 4, 0, 0] } }],
        false,
      ),
      byType: chartOption(
        result.years,
        selected.map((c) => ({
          type: "bar",
          name: c.label,
          stack: "total",
          data: result.perYear.map((y) => y[c.key]),
          itemStyle: { color: c.color },
        })),
        true,
      ),
    };
  }, [result, types]);

  function toggleType(key) {
    setTypes((current) =>
      current.includes(key) ? current.filter((k) => k !== key) : [...current, key],
    );
  }

  if (!rows || !meta) return <p className="loading">Daten werden geladen ...</p>;

  const { kpis } = result;
  const cards = [
    ["Ladestationen", number.format(kpis.stationen)],
    ["Ladepunkte", number.format(kpis.ladepunkte)],
    ["HPC-Ladepunkte", number.format(kpis.hpc)],
    ["Gesamtleistung", `${gw.format(kpis.kw / 1e6)} GW`],
  ];

  return (
    <div className="page">
      <header className="header">
        <h1>Ladeinfrastruktur in Deutschland</h1>
        <p className="stand">
          Datenstand: BNetzA: {meta.bnetza_stand} | KBA: {meta.kba_stand} (Update: {meta.update})
        </p>
      </header>

      <section className="filters">
        <label className="field">
          <span>Bundesland</span>
          <select value={state} onChange={(e) => setState(e.target.value)}>
            <option>{ALL}</option>
            {states.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </label>
        <div className="field">
          <span>Leistungstyp</span>
          <div className="chips">
            {CATEGORIES.map((c) => (
              <button
                key={c.key}
                type="button"
                className="chip"
                aria-pressed={types.includes(c.key)}
                onClick={() => toggleType(c.key)}
              >
                <i style={{ background: c.color }} />
                {c.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {types.length === 0 ? (
        <p className="hint">Bitte wähle mindestens einen Leistungstyp aus.</p>
      ) : (
        <>
          <section className="kpis">
            {cards.map(([label, value]) => (
              <div key={label} className="card kpi">
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </section>
          <section className="charts">
            <div className="card">
              <h2>Jährlicher Zubau von Ladepunkten (Gesamt)</h2>
              <BarChart option={charts.total} />
            </div>
            <div className="card">
              <h2>Jährlicher Zubau nach Leistungstyp</h2>
              <BarChart option={charts.byType} />
            </div>
          </section>
        </>
      )}
    </div>
  );
}
