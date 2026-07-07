# Ausführplan: Offizielle BNetzA-Tages-API anbinden

> **Status (2026-06-26):** Anfrage-Mail an `ladesaeulenregister@bnetza.de` ist
> raus (OpenAPI-Spec + Endpoint-URL der öffentlichen, **tagesaktuellen**
> REST-Schnittstelle JSON/XML). Dieser Plan wird ausgeführt, **sobald die
> Antwort mit Spezifikation/Zugangsdaten vorliegt.** Bis dahin bleibt der
> bestehende `services2`-ArcGIS-Snapshot (Stand monatlich, ~Wochen Verzug) bzw.
> die XLSX-Pipeline aktiv.

---

## 0. Warum überhaupt
- Genutzter Endpoint `services2.arcgis.com/.../Ladesaeulen_in_Deutschland/
  FeatureServer/0` ist ein **monatlicher Snapshot** (Layer `Ladesäulenregister_042026`,
  „Stand: 04.2026", `lastEditDate` 2026-05-08) → hinkt der Realität hinterher.
- Ziel: die **offizielle, einmal täglich aktualisierte** öffentliche
  REST-Schnittstelle der BNetzA als Datenquelle. Endpoint/Spec kommt per Mail.

## 1. Was wir behalten (unverändert, schon getestet)
Das Ziel-Schema und die nachgelagerte Logik bleiben **gleich** — nur die
*Quelle* (Fetch + Normalisierung) wird getauscht:
- `scripts/update_data.py`: `transform()`, `add_ags()`, `_to_float()`,
  Konstanten `OUT_PATH`, `VERSION_PATH`, `SHAPEFILE`.
- Ziel-Parquet `02_data/03_computed_data/combined_ladestation_ladepunkt.parquet`
  mit den 22 Spalten (siehe `plans/2026-06-25_api-anbindung.md`, Abschnitt 2).
- Validierungs-Guards: Pflicht-Spalten-Check, `MIN_RECORDS`-Schwelle,
  globales `try/except` → `sys.exit(1)`.
- `data_loading.load_data()` (Dashboard) bleibt komplett unberührt.

## 2. Offene Punkte, die die Spec klären MUSS (Checkliste beim Antwort-Eingang)
Vor der Implementierung aus der Mail/OpenAPI-Spec festhalten:
1. **Endpoint-URL** der öffentlichen Tages-Schnittstelle.
2. **Auth:** Token nötig? Wenn ja — Header (`Authorization: Bearer …` /
   `X-API-Key`) oder Query-Param? Wie wird er beantragt/rotiert?
3. **Format:** JSON oder XML (oder beides)? → bestimmt Parser.
4. **Pagination:** Offset/Limit, Seiten-Token, Cursor — oder ein Voll-Dump?
   Maximale Seitengröße? Rate-Limits.
5. **Datensatz-Granularität & Feldnamen:** pro **Station** mit `Stecker1..6`
   (wie ArcGIS → Wide→Long-Melt bleibt) **oder** bereits pro **Ladepunkt**
   (dann entfällt der Melt, `normalize` baut die Station-Spalten direkt)?
6. **Datums-Format:** Epoch-ms (wie ArcGIS) vs. ISO-String → `to_datetime`-Aufruf.
7. **Datenstand-Feld:** Liefert die API ein „Stand"/Aktualisierungsdatum?
   → für `_data_version.py` statt `date.today()`.
8. **Nutzungsbedingungen:** Lizenz, Pflicht-Quellenangabe, erlaubte Frequenz.

## 3. Code-Struktur
Minimaler Eingriff, an `update_data_api.py` angelehnt. Neue Datei:
```text
scripts/update_data_official.py   # Fetch+normalize gegen die offizielle API
```
- Importiert `transform`, `add_ags`, `OUT_PATH`, `VERSION_PATH` aus
  `update_data` (gleiches Muster wie `update_data_api.py`).
- **Token** (falls nötig) ausschließlich aus Umgebungsvariable:
  `TOKEN = os.environ["BNETZA_API_TOKEN"]` — **nie** committen. In GitHub
  Actions als Repository-Secret hinterlegen.
- Aufbau analog `update_data_api.py`:
  - `fetch_all()` — paginierter Abruf gemäß Spec, Retry/Backoff, sammelt Records.
    Bei XML: `xml.etree`/`lxml` statt `r.json()`.
  - `normalize(df)` — neues `RENAME`-Mapping (API-Feldnamen → erwartete
    Spaltennamen), Datums-Konvertierung passend zum Format.
  - Wenn Quelle bereits **Ladepunkt-granular**: `transform()` ggf. anpassen
    oder einen schlanken `build_target(df)` schreiben, der die 22 Spalten
    direkt erzeugt (Melt überspringen). Sonst `transform()` unverändert.
  - `main()` — `fetch_all` → `normalize` → (`transform`/`build_target`) →
    `add_ags` → `to_parquet` → `_data_version.py` (Stand aus API, sonst heute).

## 4. Validierung / Robustheit (zwingend, wie bisher)
- Pflicht-Spalten nach Fetch prüfen; Abbruch bei `< MIN_RECORDS` (~50.000)
  → schützt die gute Datei vor Teil-/Leer-Antworten.
- Plausi-Diff gegen die aktuelle Parquet: Stations-/Ladepunkt-Zahl,
  `max(Inbetriebnahmedatum)` sollte **neuer** sein als der ArcGIS-Snapshot.
- Globales `try/except` → `sys.exit(1)`, damit kein kaputtes Parquet committed
  wird (CI-Step rot).

## 5. CI / Workflow
- `.github/workflows/update_data_api.yml` (täglicher Cron existiert bereits)
  auf das neue Skript umstellen: `uv run python scripts/update_data_official.py`.
- Falls Token: im Job per `env: BNETZA_API_TOKEN: ${{ secrets.BNETZA_API_TOKEN }}`.
- **Jetzt ist täglicher Cron sinnvoll** (Quelle ist tagesaktuell).
- `update_data.py` (XLSX, monatlich) als Fallback behalten, bis die offizielle
  API über mehrere Läufe verifiziert ist. Danach `services2`-Skript
  (`update_data_api.py`) entfernen oder als Backup belassen.

## 6. Test & Rollout
1. Lokal: aktuelle Parquet + `_data_version.py` sichern (`/tmp`).
2. `uv run python scripts/update_data_official.py` — Logs/Recordzahl prüfen.
3. Schema-Diff: Spalten (Menge **und** Reihenfolge) == Referenz, dtypes,
   NaN-Quote der Schlüsselspalten == 0.
4. `PYTHONPATH=01_app uv run python -c "from data_loading import load_data; …"`
   → `Jahr`/`Leistungskategorie` plausibel, keine Fehler.
5. Erst dann committen/Workflow scharf schalten. PR ohne AI-Attribution.

## 7. Zu treffende Entscheidungen (nach Spec)
- [ ] Quelle Ladepunkt- oder Stations-granular → Melt behalten oder entfernen.
- [ ] `services2`-Skript & XLSX-Pipeline: behalten / abschalten / löschen.
- [ ] Cron-Frequenz endgültig (täglich, sobald Tages-API steht).
- [ ] `ladepunkt_id`: laufende Nummer beibehalten oder stabile
      `ladestation_id`-`slot`-Kombi (offene Frage aus voriger Diskussion).
