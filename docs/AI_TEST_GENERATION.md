# AI test generation playbook

## Required context

Before writing a test, inspect:

1. The nearest existing spec in the same suite.
2. `tests/conftest.py` for reusable fixtures.
3. Existing resource clients/models for API scenarios.
4. Existing pages/components for UI scenarios.
5. `docs/TEST_DATA.md` for lifecycle constraints.

Use templates in `docs/templates/` as structural references, not as code to copy blindly.

## Generation algorithm

1. State the single business behavior and choose the lowest sufficient test level.
2. Identify existing fixtures that satisfy Arrange. Add factory/resource/data-manager support only if missing.
3. Keep endpoint paths in resource clients and selectors in pages/components.
4. Add or reuse Pydantic models for every API response used by the test.
5. Write an Allure title and explicit Arrange/Act/Assert steps. Resource and page methods already contribute nested steps.
6. Assert observable behavior and persisted state. Avoid visibility-only assertions for mutating operations.
7. Track all generated resources for cleanup. Never use another test's data or a global reset.
8. Add `smoke` only for a critical fast path and `negative` for rejection/validation behavior.
9. Update abstractions and documentation if the generated test introduces a reusable concept.

## Prohibited shortcuts

- No `time.sleep`, fixed browser sleeps, raw API paths in specs, or selectors in specs.
- No unvalidated `dict` response assertions when a model exists or is needed.
- No test order dependencies, shared mutable accounts, or broad `try/except` around assertions.
- No unconditional retries, local pytest reruns, skips for stable application behavior, or suppressing mypy errors.
- No upstream source changes in `.runtime/` and no committing `.env`, artifacts, or generated reports.

## Definition of done

The new spec is independent under `-n 2`, cleanup succeeds on repeat runs, static gates pass, collection is warning-free, and the relevant real suite passes against the local application. If the application cannot be started, report the test as implemented but unverified.
