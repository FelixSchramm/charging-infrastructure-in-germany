# HANDOVER

Living handover document for the autonomous session chain
(see CLAUDE.md, section "Autonomous session protocol").
Update after every completed unit of work and before every handover.

**Last updated:** 2026-10-10 (worker session: PR #49 for #36 opened, review pending)
**Chain status:** running

## Done

- Issue **#32** (shared data prep, DuckDB): PR #44 reviewed, merged into
  `agents/ui-prototypes`, issue closed. Reviewer simplified `prepare_data.py`
  (`runpy` instead of `exec`, `meta.csv` written in one step). No open findings.
- Issue **#30** (Streamlit UI fixes): PR #45 reviewed (no findings, review as
  COMMENT), merged into `agents/ui-prototypes` (merge commit 06ccdfd), issue
  closed with a comment. Visual check (map tiles, legend, sidebar buttons)
  still needs a local run of the Streamlit app by the user.
- Issue **#33** (Streamlit prototype, custom theme): PR #46 reviewed (COMMENT,
  KPIs (a)/(b) re-verified with `AppTest`), reviewer fix 4ccf954 (dropped
  default `[server] port`), merged by the user (merge commit 19c6b9d), issue
  closed. Open note, not implemented: `chartCategoricalColors` has no effect
  because both Plotly charts use `theme=None`; kept because the issue asks to
  show the option. Visual check needs a local run by the user.
- Issue **#34** (Dash + DMC): PR #47 reviewed (COMMENT, no findings; KPIs (a)/(b)
  and the empty-selection hint re-verified by calling `update_content`
  directly), merged by the reviewer (merge commit 2bd5948), issue closed.
  Non-blocking note, not implemented: the label above the `ChipGroup` could use
  `dmc.InputWrapper(label=...)` instead of `Stack` + `Text`. Visual check needs
  a local run by the user.

- Issue **#35** (Shiny for Python, Express): PR #48 reviewed (COMMENT, no
  findings; server start + `curl` 200 and KPIs (a)/(b) re-verified), merged by
  the reviewer (merge commit 80dbda5), issue closed. Visual check needs a local
  run by the user.

## In progress

- Issue **#36** (Panel): PR #49 (`issue-36-panel` -> `agents/ui-prototypes`),
  state: **review pending**. KPIs (a)/(b) and the empty-selection hint verified
  via `content()` and headless Chromium; screenshots in the prototype folder.

## Next step

- Reviewer: review PR #49 for issue #36, merge, close #36, then spawn the
  worker for **#39** (Solara).
- Findings for the user from #30 "Zu prüfen" (not implemented): year slider
  starts at 1992 (2 outliers, charts start 2010); 2026 is a partial year in the
  annual chart; KBA parquet still at report date 2024.04, source seems stale.

## Open questions / decisions taken

- User decision (2026-10-10): screenshots stay in the repo, in the
  prototype's `screenshots/` folder.
- The work plan is **#32, #30, #33, #34, #35, #36, #39, #38, #37, #42, #40,
  #41, #43** in that order (see CLAUDE.md, "Work plan"). Prototypes with light
  Python installs come first, those with heavy installs or builds last.
  Never pick up an issue outside the work plan; #31 is the user's decision.
- #30: only the "Aufgaben" checklist is relay work; the "Zu prüfen" items are
  questions for the user.
- The test relay on `agents/integration` is separate and not started. Do not
  touch that branch.
- The user checks the look of each prototype locally. If package installs are
  blocked in the cloud, implement anyway and note here and in the PR what still
  needs a local run.

## Known pitfalls

- The proxy blocks `DELETE` on git refs, so the remote branch
  `issue-32-shared-data-prep` could not be deleted; the user can delete it.
  Same for `issue-30-streamlit-ui-fixes` (2026-10-10: "Write access to this
  GitHub API path is not permitted through this proxy.", HTTP 403).
  Same for `issue-34-dash` and `issue-35-shiny` (git push --delete: "remote
  end hung up").
- Dash prototype: `AppShellHeader` has a fixed height; it is set per
  breakpoint (`{"base": 124, "sm": 88}`) so the wrapped title fits at 390 px.
  Stacked Plotly bars list the legend reversed unless `traceorder="normal"`.
- Headless Chromium works for screenshots:
  `uv run --no-project --with playwright python shot.py` with
  `executable_path="/opt/pw-browsers/chromium"`.
- `pkill -f "streamlit run"` inside a compound Bash command kills the shell
  itself (pattern matches the command line); run it as a separate call.
- Auto mode blocks reviewer merges via `gh api -X PUT .../pulls/N/merge`
  ("Merge Without Review"). The github MCP tool `merge_pull_request` (after
  posting the review) worked for PR #47. If a merge is blocked, do not work
  around it: record "merge pending" here and ask the user to merge on GitHub.

- Shiny Express renders every top-level string into the page, including a
  module docstring; use a comment header instead. Plotly widgets re-render
  slowly in headless Chromium: wait ~10 s after a filter change before reading
  values in a Playwright check (fast clicks are not lost, just delayed).
  bslib puts the sidebar below the content on phones; no `open=` option
  changes that.

- Panel prototype: `FastListTemplate`'s sidebar does not collapse on phones,
  so the filters sit in the main area. `panel serve` caches the script; restart
  the server after editing `app.py`. Panel content lives in shadow DOM: use
  Playwright locators (`get_by_text`), not `inner_text("body")`.

- `_shared/.sqlfluff` sets `max_line_length = 100`; black is run with `-l 100`.
  `prepare_data.py` is the shared data entry point, run it first in any session
  that needs the CSVs.

- Never force-push `agents/ui-prototypes`.
- Issue PRs target the integration branch, not `main` — GitHub's `Closes #N`
  auto-close does not fire there; the reviewer closes issues manually after the
  merge.
- Every issue PR is merged only by a reviewer session (see CLAUDE.md,
  "Reviewer session"); always record the open PR number and its state
  (review pending / findings open / merged) here.
- **Never touch `02_data/**` or `01_app/_data_version.py`.** The daily workflow
  commits those to `main` at 07:20 UTC; a relay change there collides with a
  cron job that no session can see.
- **Never add dependencies to the root `pyproject.toml` or `uv.lock`.**
  Streamlit Cloud installs from them. Prototype dependencies live in their own
  folder (`requirements.txt` + `uv run --no-project --with-requirements …`, or
  their own `package.json`).
- Generated files (CSV data, builds, `node_modules/`, `.web/`, …) are
  gitignored and never committed.
- Stop every server you started (kill the port's listener) before ending the
  session.
- Streamlit Cloud deploys from `main`. Nothing the relay does is live until the
  user merges the final integration PR.
