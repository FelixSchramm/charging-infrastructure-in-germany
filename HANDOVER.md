# HANDOVER

Living handover document for the autonomous session chain
(see CLAUDE.md, section "Autonomous session protocol").
Update after every completed unit of work and before every handover.

**Last updated:** 2026-09-09 (setup session — no issue work started yet)
**Chain status:** not started

## Done

- (nothing yet — protocol files installed on 2026-09-09; the fallback routine
  and the first worker session still have to be started by the user, see
  `plans/2026-09-09_agent-automatisierung.md`, steps 5 and 6)

## In progress

- (nothing)

## Next step

- Start with issue **#18 — test: pytest-Setup und Orchestrierung der Test-Suite**.
  Read the issue in full first. It is the prerequisite for #27, #22, #20, #21
  and #23: without `[tool.pytest.ini_options]` and `pythonpath = ["01_app",
  "scripts"]` none of the test issues can import the modules they test.

## Open questions / decisions taken

- The work plan is **#18, #27, #22, #20, #21, #23, #24** in that order.
  Issues #25 and #26 are deliberately excluded (#25 needs a manual ~5 GB
  download, #26 is a decision for the user); #19 waits for the outcome of #26.
  Never pick up an issue outside the work plan.
- All data files needed for verification are committed in the repo, so every
  issue can be implemented and verified in a cloud session. No step needs a
  local run.
- Once #18 is merged, adding `.github/workflows/tests.yml` (`uv sync` +
  `uv run pytest` on push/PR) is worthwhile: until then the reviewer session is
  the only quality gate the relay has.

## Known pitfalls

- Never force-push `agents/integration`.
- Issue PRs target the integration branch, not `main` — GitHub's `Closes #N`
  auto-close does not fire there; the reviewer closes issues manually after the
  merge.
- Every issue PR is merged only by a reviewer session (see CLAUDE.md,
  "Reviewer session"); always record the open PR number and its state
  (review pending / findings open / merged) here.
- **Never touch `02_data/**` or `01_app/_data_version.py`.** The daily workflow
  commits those to `main` at 07:20 UTC; a relay change there collides with a
  cron job that no session can see.
- The app reads parquet via cwd-relative paths — run everything from the repo
  root, and set `PYTHONPATH=01_app` for AppTest until #18 provides the pytest
  config.
- Streamlit Cloud deploys from `main`. Nothing the relay does is live until the
  user merges the final integration PR.
