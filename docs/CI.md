# Continuous integration

## Workflow

`.github/workflows/ci.yml` has two job types:

- `quality`: locked dependency install, Ruff formatting/lint, strict mypy, and self-tests.
- `tests`: API/UI/E2E matrix against an independent pinned Docker application on each runner.

Pull requests run only `smoke` tests. Main-branch pushes and `workflow_dispatch` run all application tests. Each runner uses two pytest workers and one diagnostic rerun. Local runs have no pytest rerun flag.

## Artifacts

Each suite uploads `allure-results-<suite>-<run-number>` for 14 days. Failure diagnostics are uploaded separately when present. Application logs are printed on failure. The application is stopped in an `always()` step.

Download a run's artifacts:

```bash
uv run python scripts/gh_ci.py download <run-id>
allure generate artifacts/downloaded/allure-results-<suite>-<run-number> --clean -o artifacts/allure-report
allure open artifacts/allure-report
```

If a suite stores results in a nested directory, point Allure at the directory containing `*-result.json` files.

## GitHub CLI

`scripts/gh_ci.py` wraps non-interactive `gh workflow` and `gh run` commands. Run `gh auth login` first. `dispatch` starts the full workflow, `watch` returns a failing exit status for a failed run, and `download` retrieves artifacts. No GitHub token is stored in project files.

## Failure policy

A rerun is diagnostic, not a quality gate bypass. Investigate the first attempt in Allure and fix product/test defects. Do not increase reruns, skip a stable assertion, or add fixed sleeps to obtain a green workflow.
