# CLAUDE.md

Compact project context for Claude Code. Keep this short and current.

Coding standards and behavioral guidelines live in
@CLAUDE_CODING_RULES.md — they apply to every session and every role.

## What this is
Streamlit dashboard visualizing Germany's public charging infrastructure
(BNetzA Ladesäulenregister + KBA EV stock). Live: https://ladeinfrastruktur-in-deutschland.streamlit.app/

## Stack & tooling
- Python >=3.12, package manager: **uv** (`uv sync`, `uv run …`). Venv: `.venv/`.
- Key deps: streamlit==1.54.0, pandas, geopandas, plotly, folium, pyarrow.

## Run
```bash
uv run streamlit run 01_app/app.py
```

## Layout
- `01_app/app.py` — schlanker Entry-Point, orchestriert nur die Abschnitte.
- `01_app/config.py` — Seiteneinstellung, Farben, Konstanten.
- `01_app/data_loading.py` — Loader (mit `@st.cache_data`).
- `01_app/filters.py` — Seitenleisten-Filter + Anwendung auf die Daten.
- `01_app/sections/` — je ein Modul pro Abschnitt (header, kpis, timeseries,
  analyses, map_view, info).
- `01_app/_data_version.py` — `LAST_UPDATED` stamp; imported by the app so a
  data commit forces a Streamlit Cloud redeploy. Overwritten by the CI workflows.
- `scripts/update_data.py` — downloads BNetzA xlsx, writes the parquet. Shared
  helpers (`add_ags`, `save_output`, paths) are imported by the script below.
- `scripts/update_data_official.py` — alternative source: BNetzA's official daily
  JSON API, same output schema. Run daily by `update_data_api.yml`.
  Explained in `scripts/update_data_official.md`.
- `scripts/update_kba_data.py` — updates the KBA EV-stock parquet.
- `02_data/03_computed_data/combined_ladestation_ladepunkt.parquet` — main data (~7 MB).
- `02_data/03_computed_data/kba_ev_bestand.parquet` — KBA EV stock.
- `02_data/02_meta_data/…/VG250_KRS.shp` — district shapefile for spatial join.

## Data pipeline (GitHub Actions)
- `.github/workflows/update_data_api.yml` — daily (07:20 UTC), official BNetzA
  API, commits the charging parquet + `_data_version.py`.
- `.github/workflows/update_data.yml` — monthly (5th, 06:00 UTC), XLSX fallback,
  commits the same two files.
- `.github/workflows/update_kba_data.yml` — yearly (May 1), commits the KBA parquet.
- Data is committed **into the repo** (read directly by Streamlit Cloud). See the
  README note for the trade-off and possible bucket/DuckDB future steps.

## Conventions
- App reads parquet via paths relative to repo root (cwd), e.g.
  `pd.read_parquet('02_data/03_computed_data/…')`.
- `@st.cache_data(ttl=3600)` on the loaders — refreshes hourly.
- Commit messages / PRs: no AI-attribution lines.

## Work plan

GitHub issues **#18, #27, #22, #20, #21, #23, #24** are the work plan for the
autonomous relay. Work them in exactly this order:

**#18 (pytest setup) → #27 (tests update_data_official) → #22 (tests
_leistungskategorie) → #20 (tests update_kba_data) → #21 (tests filters) →
#23 (smoke test) → #24 (second KPI row)**

Each issue is written to be self-contained. Read the issue in full before
starting it.

Two open issues are deliberately **not** part of the relay and must never be
picked up by a session: **#25** (OBELIS integration) needs a manual ~5 GB
download that a cloud session cannot perform, and **#26** is a decision for the
user, not an implementation task. **#19** waits for the outcome of #26.

Data note: the charging parquet, the KBA parquet and the district shapefile are
committed in the repo, so every issue can be implemented *and* verified in a
cloud session without network access. Tests must stay offline — build API
payloads synthetically instead of calling the BNetzA endpoint.

## Autonomous session protocol (relay of single-purpose sessions)

This repo is worked on autonomously by a relay of Claude Code web sessions,
each with exactly one job:

- **Worker session:** implements exactly one issue and opens its PR, then
  spawns the reviewer.
- **Reviewer session:** reviews that PR, fixes clear findings itself, merges,
  then spawns the next worker.

A fallback routine (2x daily, 06:00/18:00 UTC) restarts the relay if it
stalls (>12h without a commit while issues remain open).

### Rules for every session

1. **Branches:** `agents/integration` is the integration branch (never
   force-push it). Each issue lives on its own feature branch
   `issue-NN-<short-slug>` off the integration branch. When all issues are
   done, the final session proposes a PR from the integration branch to
   `main` for the user to review.
2. **Session start:** fetch + check out the integration branch, read this
   file, `CLAUDE_CODING_RULES.md` and `HANDOVER.md`, then do the one job
   your role defines.
3. **Commit early, push often:** commit and push after every completed unit
   of work. Git history + `HANDOVER.md` are the only handover channel —
   nothing outside pushed commits survives a session.
4. **Keep `HANDOVER.md` current:** update it before ending your session
   (done / in progress / next step / open PR + its state / pitfalls) and
   push it.
5. **90% budget rule:** note the `total_tokens` value at session start. When
   the remaining budget falls below **10% of that starting value**: do not
   start anything new, commit and push the current state, finalize
   `HANDOVER.md`, write an archive snapshot (see "Handover archive"), and
   schedule the successor **as a +5h one-shot trigger instead of an
   immediate spawn** (see step 6), then end the turn.
6. **Spawning the successor:** use the claude-code-remote MCP tools.
   - Normal case (budget fine): `create_session` in the same environment —
     the successor starts immediately.
   - 90% rule hit: `create_trigger` with `run_once_at` = now + 5 hours,
     `create_new_session_on_fire: true`, `initiation: "human_schedule"`.
   - Either way the prompt must be fully standalone — use the templates
     below and fill in issue/PR numbers. Never end your session without
     having spawned or scheduled the successor (unless the relay is
     complete, see step 7).
7. **Completion:** when all issues of the work plan are done, do NOT spawn a
   successor. Update `HANDOVER.md` to state the relay is finished, write a
   final archive snapshot (reason: "all issues done"), and ask the user in
   the session summary whether to open the PR to `main` and disable the
   fallback routine.
8. **Never touch the data files.** `02_data/**` and `01_app/_data_version.py`
   belong to the daily update workflows on `main`. A relay session that
   changes them creates conflicts with a cron job it cannot see.

### Worker session (one issue)

1. Identify the next open issue N from `HANDOVER.md`; read issue N in full.
2. Create `issue-NN-<short-slug>` off the integration branch.
3. Implement the issue following `CLAUDE_CODING_RULES.md`; commit/push per
   unit of work.
4. Open a PR targeting `agents/integration`. The PR body follows the repo
   convention: description with background and links, complexity level,
   priority/urgency.
   Note: `Closes #N` does NOT auto-close issues for PRs into a non-default
   branch — the reviewer closes the issue manually after the merge.
5. Update `HANDOVER.md` (PR number, state: "review pending"), push it to the
   integration branch.
6. Spawn the reviewer session (worker → reviewer template) and end the turn.

### Reviewer session (one PR)

1. Review the full PR diff with fresh eyes. Three questions, in priority
   order:
   1. **Is the code as simple and as short as possible?** Flag
      overcomplication, speculative abstraction, unnecessary
      configurability, dead code, anything where 50 lines would do the job
      of 200.
   2. **Does hand-written code reimplement something an established package
      already provides?** Prefer the package; flag the reinvention.
   3. **Are the rules in `CLAUDE_CODING_RULES.md` followed?** Especially
      "Simplicity First" and "Surgical Changes".
2. Post the findings as a PR review with inline comments (github MCP tools),
   most severe first. If there is nothing to flag, say so explicitly in a
   short review — do not invent findings.
3. **Fix only clear-cut findings yourself** (simplifications, package
   replacements, style/docstring fixes) — commit and push them to the
   feature branch. **Structural or debatable findings are NOT implemented**:
   leave them as PR comments and record them in `HANDOVER.md` so the user or
   a later issue can pick them up.
4. Merge the PR into the integration branch (regular merge, no force-push),
   close issue #N manually with a comment linking the PR, delete the
   feature branch.
5. Update `HANDOVER.md` (issue N done, next issue), write an archive
   snapshot (reason: "issue #N merged").
6. Spawn the next worker session (reviewer → worker template) and end the
   turn — or, if all issues are done, follow "Completion" above.

### Handover archive

Snapshots of `HANDOVER.md` go to `docs/handovers/YYYY-MM-DD_HHMM.md`
(current UTC date/time), prefixed with one line
`# Handover <timestamp> — <reason>`. Write a snapshot:

- after every merge (reviewer, reason: "issue #N merged"),
- whenever the 90% rule triggers (reason: "90% budget reached"),
- at relay completion (reason: "all issues done").

Snapshots are append-only history — never edit or delete old ones. The
current working state always lives in `/HANDOVER.md` at the repo root.

### Fallback sessions

If you were started by the fallback routine: read `HANDOVER.md` and adopt
the role that matches the recorded state — an open PR with review pending
makes you the reviewer; otherwise you are the worker for the next open
issue. Then follow that role's protocol above, including spawning the
successor.

### Prompt templates

Worker → reviewer:

> Continue the autonomous relay on FelixSchramm/charging-infrastructure-in-germany
> as the REVIEWER session. Fetch and check out branch `agents/integration`, read
> CLAUDE.md (section "Autonomous session protocol"), CLAUDE_CODING_RULES.md and
> HANDOVER.md. Review PR #<PR> for issue #<N> following the "Reviewer session"
> protocol: post a PR review (simplicity first, package reuse, coding-rules
> compliance), fix only clear-cut findings yourself, merge, close issue #<N>,
> archive the handover, then spawn the next worker session. Apply the 90% budget
> rule.

Reviewer → worker:

> Continue the autonomous relay on FelixSchramm/charging-infrastructure-in-germany
> as the WORKER session. Fetch and check out branch `agents/integration`, read
> CLAUDE.md (section "Autonomous session protocol"), CLAUDE_CODING_RULES.md and
> HANDOVER.md. Implement issue #<N> on a feature branch following the "Worker
> session" protocol, open the PR against `agents/integration`, update
> HANDOVER.md, then spawn the reviewer session. Apply the 90% budget rule.
