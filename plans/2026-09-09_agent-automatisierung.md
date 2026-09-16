# Umsetzungsplan: Agent-Automatisierung für dieses Repo aktivieren

**Ziel:** Den ruhenden Relay-Aufbau aus `agent_architecture/` für dieses Projekt
scharf schalten, sodass eine Kette autonomer Claude-Code-Sessions die offenen
Issues abarbeitet — je eine Session pro Issue, mit Review-Session dazwischen.

**Aufwand:** ~60–90 min Einrichtung, danach läuft der Relay selbst.
**Priorität:** mittel. Nichts davon ist dringend, aber die Vorarbeit (Issues,
Priorisierung) liegt fertig vor.

---

## Ausgangslage

Vorhanden:
- `agent_architecture/` mit Protokoll-Templates, Prompts und Aktivierungs-Checkliste
  (Stand: dormant, nichts läuft von allein)
- Zehn Issues (#18–#27) mit Reihenfolge, jedes für sich lesbar
- Daten liegen im Repo (Parquet + Shapefile) → Sessions können die App und
  später die Tests wirklich ausführen

Fehlt: alles aus der Checkliste ab Schritt 2 (Parameter, Root-Dateien,
Integrationsbranch, Fallback-Routine, Kickoff).

---

## Vorab zu entscheiden

### 1. Welche Issues bekommt der Relay?

Nicht alle offenen Issues sind für eine Cloud-Session machbar:

| Issue | Relay-tauglich | Grund |
|---|---|---|
| #24 KPI-Reihe | ja | reine Code-Änderung, Daten im Repo |
| #18 pytest-Setup | ja | |
| #27, #22, #20, #21, #23 Tests | ja | offline, deterministisch |
| #19 Tests `update_data.py` | erst später | hängt an der Entscheidung in #26 |
| **#25 OBELIS** | **nein** | braucht einen manuellen 5-GB-Download von der Mobilithek; kein stabiler Link, kein Cloud-Zugriff |
| **#26 XLSX-Pipeline** | **nein** | menschliche Entscheidung, kein Implementierungsauftrag |

Vorschlag für `<ISSUE_RANGE>`: **#18, #27, #22, #20, #21, #23, #24** in genau
dieser Reihenfolge. Das ist die Test-Suite plus die KPI-Kacheln — durchgehend
autonom umsetzbar und verifizierbar.

Damit dreht sich die in #18 dokumentierte Reihenfolge für den Relay-Teil um:
#25 (das größere Feature) bleibt Handarbeit und läuft parallel, der Relay
übernimmt den Teil, der ohne dich auskommt.

### 2. Weitere Parameter

- `<OWNER/REPO>`: `FelixSchramm/charging-infrastructure-in-germany`
- `<INTEGRATION_BRANCH>`: `agents/integration`
- `<PROJECT_DESCRIPTION>`: zwei Sätze zum Dashboard, Einstieg `01_app/app.py`,
  Pipeline in `scripts/`
- `<DATA_NOTE>`: Parquet und Shapefile sind eingecheckt, also ist alles lokal
  ausführbar. Kein Netzwerkzugriff auf die BNetzA-API nötig — Tests laufen
  gegen synthetische Payloads.

---

## Schritte

### Schritt 1 — `CLAUDE.md` zusammenführen, nicht überschreiben

Die Checkliste sagt „`CLAUDE.template.md` -> `/CLAUDE.md`". **Das darf hier
nicht wörtlich passieren**: Das bestehende `CLAUDE.md` enthält den kompletten
Projektkontext (Layout, Pipeline, Konventionen), der sonst verloren geht.

Stattdessen:
1. Die hintere Hälfte des heutigen `CLAUDE.md` („AI Coding Instructions" +
   „Behavioral Guidelines") nach `/CLAUDE_CODING_RULES.md` auslagern — die
   Vorlage in `agent_architecture/` ist inhaltlich fast identisch und
   bereits auf den Relay angepasst.
2. In `CLAUDE.md` an ihrer Stelle die Zeile
   `Coding standards ... live in @CLAUDE_CODING_RULES.md` setzen.
3. Die Abschnitte „Work plan" und „Autonomous session protocol" aus
   `CLAUDE.template.md` mit gefüllten Platzhaltern anhängen.

Dabei zwei bestehende Konventionen bewusst auflösen:
- **Branch-Namen:** `CLAUDE.md` verlangt heute Jira-Nummern (`NLL-XXX-…`). Für
  dieses Repo gibt es kein Jira; der Relay braucht `issue-NN-<slug>`. Die
  Jira-Regel für dieses Repo streichen.
- **PR-Beschreibung:** Die Anforderung (Datenquelle, Hintergrund, Komplexität,
  Priorität) bleibt und muss in die Worker-Anweisung, sonst schreiben die
  Sessions PR-Texte, die der Konvention nicht genügen.

→ verifizieren: `CLAUDE.md` enthält weiterhin Layout- und Pipeline-Abschnitt,
`CLAUDE_CODING_RULES.md` existiert, keine Regel steht doppelt.

### Schritt 2 — `HANDOVER.md` und Archivordner anlegen

`HANDOVER.template.md` mit gefüllten Platzhaltern nach `/HANDOVER.md`,
`handovers_README.md` nach `/docs/handovers/README.md`.

Unter „Known pitfalls" projektspezifisch ergänzen:
- Der tägliche Daten-Workflow committet um 07:20 UTC auf `main`
  (Parquet + `_data_version.py`). Der Relay fasst diese Dateien nie an.
- Die App liest Parquet über cwd-relative Pfade → Sessions arbeiten aus dem
  Repo-Root.
- Kein Test-Framework, bis #18 gemergt ist. Bis dahin ist die Verifikation ein
  AppTest-Einzeiler mit `PYTHONPATH=01_app`.

→ verifizieren: Beide Dateien sind gepusht und im Repo sichtbar.

### Schritt 3 — Integrationsbranch anlegen

```bash
git checkout -b agents/integration main && git push -u origin agents/integration
```

→ verifizieren: Branch existiert auf GitHub, `main` ist unverändert.

### Schritt 4 — Test-Workflow als Qualitätsschranke (empfohlen)

Der Relay merged seine PRs selbst. Ohne CI ist die Review-Session die einzige
Kontrolle. Sobald #18 gemergt ist, `.github/workflows/tests.yml` ergänzen
(`uv sync` + `uv run pytest` bei Push/PR), damit jeder Relay-PR eine objektive
Schranke hat statt nur ein Urteil.

Vorher lohnt sich der Workflow nicht — es gibt noch nichts zu laufen.

→ verifizieren: Ein PR gegen `agents/integration` zeigt einen grünen Check.

### Schritt 5 — Fallback-Routine anlegen

Nach `agent_architecture/prompts/fallback_routine.md`: Cron `0 6,18 * * *`,
frische Session je Firing, Prompt mit gefüllten Platzhaltern. Sie startet
nichts, solange der Relay lebt — sie weckt ihn nur, wenn er >12 h steht.

→ verifizieren: Die Routine taucht in der Routinen-Liste auf und ist aktiv.

### Schritt 6 — Relay starten

Neue Cloud-Session auf dem Repo öffnen und den Kickoff-Prompt aus
`prompts/kickoff_worker.md` mit gefüllten Platzhaltern einfügen, erstes Issue
**#18**.

→ verifizieren: Innerhalb der ersten Session entstehen Branch
`issue-18-pytest-setup` und ein PR gegen `agents/integration`.

### Schritt 7 — Abschluss

Wenn alle Issues des Range durch sind: finalen PR `agents/integration` → `main`
prüfen (den reviewst du selbst), Fallback-Routine deaktivieren, optional die
Protokolldateien aus dem Root entfernen.

---

## Risiken für dieses Repo

- **Tägliche Daten-Commits auf `main`.** Der Integrationsbranch driftet jeden
  Tag um einen Daten-Commit. Unkritisch, solange der Relay Parquet und
  `_data_version.py` nicht anfasst; vor dem finalen PR einmal `main` in den
  Integrationsbranch mergen.
- **Streamlit Cloud deployt von `main`.** Solange der Relay nur auf
  `agents/integration` arbeitet, ist die Live-App nicht betroffen. Erst der
  finale Merge ist ein Deploy — entsprechend aufmerksam reviewen.
- **Kein CI bis #18.** Siehe Schritt 4.
- **Review-Session merged ohne menschlichen Blick.** Das ist die Kernannahme
  des Aufbaus. Für die gewählten Issues (Tests + eine UI-Reihe) ist der Schaden
  bei einem Fehlurteil gering, weil `main` unberührt bleibt.

## Definition of Done

- `CLAUDE.md` enthält Projektkontext **und** Relay-Protokoll, ohne dass alter
  Inhalt verloren ging; `CLAUDE_CODING_RULES.md` und `HANDOVER.md` liegen im Root.
- `agents/integration` existiert, Fallback-Routine ist aktiv.
- Die erste Worker-Session hat einen PR gegen den Integrationsbranch geöffnet.
- `main` ist zu diesem Zeitpunkt unverändert.
