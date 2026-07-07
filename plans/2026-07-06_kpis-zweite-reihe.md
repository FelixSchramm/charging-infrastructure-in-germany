# Umsetzungsplan: Zweite KPI-Reihe im Überblick-Tab

**Ziel:** Den Überblick-Tab (`render_kpis`) um eine zweite Reihe mit vier weiteren KPI-Kacheln ergänzen. Aus aktuell 4 werden 8 Kacheln (2 Reihen à 4).

**Datei:** `01_app/sections/kpis.py`
**Priorität:** niedrig (reine UI-Erweiterung, keine Datenpipeline betroffen)
**Aufwand:** ~20–30 min.

---

## Voraussetzungen
- Vor Start `git pull` auf `main` (lokaler `main` war beim Planen 5 Commits hinter `origin/main`).
- Die Tabs-Umstellung (PR "Dashboard-Abschnitte in Tabs") ist unabhängig; `render_kpis`
  wird dort nur in den `Überblick`-Tab verschoben, die Funktion selbst bleibt gleich.
  Dieser Plan funktioniert mit und ohne gemergte Tabs.

---

## Bestehender Zustand
`render_kpis(df_filtered)` rendert eine Reihe `st.columns(4)`:

1. **Ladestationen** — `df_stationen["ladestation_id"].nunique()`
2. **Ladepunkte** — `len(df_filtered)`
3. **HPC-Ladepunkte** — Zeilen mit `LadeleistungInKW >= HPC_THRESHOLD_KW`
4. **Gesamtleistung** — `df_stationen["InstallierteLadeleistungNLL"].sum() / 1e6` GW

`df_stationen = df_filtered.drop_duplicates(subset="ladestation_id")`.
Ganzzahl-Formatierung via `_de()` (Tausenderpunkt). Alle Kacheln reagieren auf die Filter.

---

## Neue zweite Reihe (vier Kacheln)

| # | Label | Berechnung (auf `df_filtered`) | aktueller Gesamtwert |
|---|-------|--------------------------------|----------------------|
| 5 | **Betreiber** | `df_filtered["BetreiberBereinigt"].nunique()` | 11.876 |
| 6 | **Ø Leistung je Ladepunkt** | `df_filtered["LadeleistungInKW"].mean()` → `" kW"` | 65,1 kW |
| 7 | **Ø Ladepunkte je Station** | `len(df_filtered) / n_stationen` | 1,8 |
| 8 | **Orte mit Ladeinfrastruktur** | `df_filtered["Ort"].nunique()` | 7.681 |

> Auswahl der 4. Kachel ("Orte mit Ladeinfrastruktur") vom Nutzer bestätigt.
> Verworfene Alternativen: HPC-Anteil in % (redundant zur bestehenden HPC-Kachel),
> abgedeckte Landkreise (401/401 → fast immer voll, wenig aussagekräftig).
> `LadeUseCase` ist im Datensatz komplett "Unbekannt" → unbrauchbar.

---

## Umsetzung

### 1. Dezimal-Formatierungshelfer ergänzen
Neben `_de()` (Ganzzahl) einen Helfer für Kommazahlen mit deutschem Dezimalkomma:

```python
def _de_dec(value: float, decimals: int = 1) -> str:
    """Formatiert eine Kommazahl mit Komma als Dezimaltrennzeichen."""
    return f"{value:.{decimals}f}".replace(".", ",")
```

Die bestehende Gesamtleistungs-Kachel kann optional auf `_de_dec(gesamtleistung_gw, 2)`
umgestellt werden (aktuell inline `f"{...:.2f} GW".replace(".", ",")`) — rein kosmetisch.

### 2. Werte einmal berechnen, zweite `st.columns(4)`-Reihe rendern
`n_ladepunkte` und `n_stationen` oben einmal berechnen und in beiden Reihen nutzen.
Danach zweite Spaltenreihe:

```python
col5, col6, col7, col8 = st.columns(4)
col5.metric("Betreiber", _de(df_filtered["BetreiberBereinigt"].nunique()))

if n_ladepunkte > 0:
    col6.metric("Ø Leistung je Ladepunkt", f"{_de_dec(df_filtered['LadeleistungInKW'].mean())} kW")
else:
    col6.metric("Ø Leistung je Ladepunkt", "–")

if n_stationen > 0:
    col7.metric("Ø Ladepunkte je Station", _de_dec(n_ladepunkte / n_stationen))
else:
    col7.metric("Ø Ladepunkte je Station", "–")

col8.metric("Orte mit Ladeinfrastruktur", _de(df_filtered["Ort"].nunique()))
```

### 3. Leere-Filter-Guard (wichtig)
Wenn die Filter alles ausschließen, ist `df_filtered` leer:
- `n_stationen == 0` → Division `n_ladepunkte / n_stationen` würde crashen → auf `"–"` ausweichen.
- `mean()` auf leerer Serie → `nan` → ebenfalls `"–"` statt `"nan kW"`.
- `nunique()` auf leer → `0`, unkritisch.

Der bestehende Code hat diesen Guard noch nicht (Gesamtleistung `sum()` = 0 ist unkritisch);
mit Kachel 6 und 7 wird er notwendig.

### 4. Keine Emojis
Labels sind reiner Text (Projekt-Konvention: keine Emojis in der UI). Das `Ø`-Zeichen
ist ok (typografisches Zeichen, kein Emoji).

---

## Verifikation
Streamlit `AppTest` (braucht `PYTHONPATH=01_app`):

```bash
PYTHONPATH=01_app uv run python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('01_app/app.py', default_timeout=60).run()
assert not at.exception, at.exception
labels = [m.label for m in at.metric]
print(labels)
assert 'Betreiber' in labels and 'Orte mit Ladeinfrastruktur' in labels
print('OK, Anzahl Kacheln:', len(labels))
"
```

Erwartung: keine Exception, 8 Metric-Kacheln, neue Labels vorhanden.

Zusätzlich sollte der Guard einmal mental für „alle Filter leer" geprüft werden
(z.B. Bundesland-Multiselect leer) — Kacheln zeigen dann `0` / `–` statt Crash.

---

## Definition of Done
- Zweite Reihe mit den vier Kacheln (Betreiber, Ø Leistung/LP, Ø LP/Station, Orte)
  wird im Überblick-Tab unter der ersten Reihe angezeigt.
- Deutsche Zahlenformatierung (Tausenderpunkt bzw. Dezimalkomma) durchgängig.
- Leere Filter-Auswahl crasht nicht (Kacheln 6/7 zeigen `–`).
- `AppTest` grün, keine Emojis in den Labels.
- Commit als `feat(kpis): zweite KPI-Reihe (Betreiber, Ø Leistung, Ø LP/Station, Orte)`.
