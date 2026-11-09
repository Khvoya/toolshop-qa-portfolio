# Architecture

## Layers

1. **Specs** (`tests/`) describe a business rule with Allure steps and assertions.
2. **Fixtures** (`tests/conftest.py`) compose settings, Playwright, API sessions, browser state, data lifecycle, and pages.
3. **Pages/components** (`src/toolshop/ui/`) own browser interactions and locators.
4. **Resource clients** (`src/toolshop/api/resources.py`) own endpoint semantics and expected statuses.
5. **Transport** (`src/toolshop/api/client.py`) owns headers, authentication, redacted diagnostics, retries, status checks, and JSON decoding.
6. **Models/factories** provide typed contracts and unique input data.
7. **Data manager** tracks resources and cleans them in reverse dependency order.

Specs should depend on pages/resources, not transport. Pages may expose locators for web-first assertions; they should not hide business expected values.

## Choosing a test level

- Use **API** for status, validation, response contracts, isolated business rules, and data setup.
- Use **UI** for rendering, interaction, navigation, client validation, and browser-visible state.
- Use **E2E** only for critical journeys that cross at least two layers and need independent verification.
- Use **self** for deterministic tests of this framework's own helpers.

Do not repeat the same assertion at all levels. For example, API tests verify the product contract; UI tests verify that this data is rendered; E2E verifies purchase persistence.

## Settings

`Settings` uses the `TOOLSHOP_` environment prefix and `.env`. UI/API base URLs, timeouts, retry policy, and admin cleanup credentials are centralized. Do not call environment APIs elsewhere.

## Browser authentication

API login creates a bearer token. `authenticated_page` installs it as `auth-token` before the first application navigation. `page_with_cart` also installs the API-created `cart_id` in session storage. Login UI is exercised only in authentication and E2E specs.

## Retry policy

Transport retries only idempotent methods by default and only on `429`, `5xx`, or Playwright network errors. Mutating requests opt out. The helper uses exponential backoff with jitter. Pytest assertion failures are never retried by transport. CI may rerun a failed test once so both attempts and diagnostics remain visible in Allure.

## Diagnostics

Allure receives structured steps and redacted API bodies. Failed browser tests add screenshot, video, trace, URL, and console/page errors. Passing tests discard video and tracing data to limit storage.
