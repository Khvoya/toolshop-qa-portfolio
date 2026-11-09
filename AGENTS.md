# Agent guide

## Purpose and boundaries

This repository contains independent Python tests for Practice Software Testing Sprint 5. Do not copy, vendor, or commit upstream application source. `.runtime/` is disposable, ignored local infrastructure. Do not edit it to make tests pass.

Read `README.md`, `docs/ARCHITECTURE.md`, `docs/TEST_DATA.md`, and `docs/AI_TEST_GENERATION.md` before generating tests. Use the closest template in `docs/templates/`.

## Architecture rules

- Test specs belong in `tests/api`, `tests/ui`, or `tests/e2e`; helper self-tests belong in `tests/self`.
- Specs contain business steps and meaningful assertions. They must not contain raw endpoint paths, browser storage scripts, CSS/XPath, or cleanup loops.
- Add API endpoints to a resource client in `src/toolshop/api/resources.py`. Validate responses with models from `src/toolshop/models/`.
- Add UI actions to pages and reusable UI elements to components. Components must be scoped to a root locator.
- Use `data-test`, role, or label locators. Dynamic-attribute CSS is acceptable only when the application has no semantic locator.
- Use Playwright `expect` and locator waits. Never add fixed sleeps or arbitrary timeouts.
- Use `@step("Clear action description")` for framework actions and `with allure.step("Arrange/Act/Assert: ...")` in specs.
- Keep credentials in environment settings. Never log tokens, passwords, or real secret values.

## Test data rules

- Prefer unique data through `TestDataManager` and factories. Do not mutate shared seed accounts.
- Use `registered_user`, `product`, `cart`, `page_with_cart`, and page fixtures instead of rebuilding preconditions.
- Track resources created through UI with `track_user` or `track_cart` so teardown can remove them.
- Keep tests independent under `pytest -n 2`. No test may depend on execution order or another test's records.
- Orders have no delete endpoint and their owners cannot be deleted. Cleanup retains only these order-owning users and records the reason; use an explicit local application reset only outside individual tests.

## Implementation workflow

1. Find existing models, resource methods, pages, components, fixtures, and tests before creating new ones.
2. Reuse existing abstractions. Add a missing abstraction rather than placing infrastructure details in a spec.
3. Mark tests with their layer and optionally `smoke` or `negative`. All application tests are regression by default.
4. Give every test an Allure title and descriptive business steps. Assert behavior, not merely visibility, when data or state changes.
5. Update documentation and templates when architecture or commands change.

## Required verification

Run the smallest relevant real suite and all static gates before finishing:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests scripts
uv run pytest --collect-only -q
uv run pytest -m self
uv run pytest -m api       # after API changes
uv run pytest -m ui        # after UI changes
uv run pytest -m e2e       # after journey changes
```

Start the local application with `uv run python scripts/app.py start`. Never report an application test as verified if it was only collected or statically checked. Do not enable retries locally to conceal a failure.
