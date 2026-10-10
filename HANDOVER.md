# HANDOVER

Living handover document for the autonomous session chain
(see CLAUDE.md, section "Autonomous session protocol").
Update after every completed unit of work and before every handover.

**Last updated:** 2026-10-10 (worker session for #32 finished)
**Chain status:** running

## Done

- (nothing yet — branch `agents/ui-prototypes` created on 2026-10-10 from
  `agents/integration` + `main`, work plan switched to the UI issues, hourly
  fallback routine created, see `plans/2026-10-10_ui-relay.md`)

## In progress

- Issue **#32**: PR **#44** (`issue-32-shared-data-prep` -> `agents/ui-prototypes`),
  state: **review pending**. Reference KPIs verified against pandas logic
  (documented in the PR). Reviewer: merge, close #32 manually, then next is #30.

## Next step

- Review and merge PR #44 (issue #32), then start issue **#30**.

## Open questions / decisions taken

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
