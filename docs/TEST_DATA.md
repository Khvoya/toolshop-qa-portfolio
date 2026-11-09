# Test data and isolation

## Rules

- Generate a unique email and password for every customer with `UserFactory`.
- Build DTOs with factories; create persistent entities through resource clients in `TestDataManager`.
- Use the seeded admin only for cleanup, never as a customer precondition.
- Do not mutate shared customer accounts. Products are read from seeded stock because the customer journey does not administer the catalog.
- Give each test a fresh API request context and browser context. No cookies, storage, carts, or favorites are shared between tests.

## Lifecycle

`TestDataManager` tracks generated users, carts, and favorites. UI-created users/carts must be registered with `track_user`/`track_cart`. Teardown removes favorites, then carts, then users. Delete operations accept `404` because checkout intentionally deletes the cart after payment.

Orders are historical invoices and the upstream API has no delete operation. It also rejects deleting their owners with `409`, so teardown deliberately retains only those users and records the reason in Allure; other cleanup errors still fail. These records do not affect other tests because users and expected totals are unique. Run `uv run python scripts/app.py reset` outside a test run when a completely fresh database is required; this command destroys only this project's application volumes.

## Parallel execution

Use `uv run pytest -n 2`. Unique identities and isolated carts prevent data collisions. Never introduce a global database reset fixture, shared generated account, or assertion over all records in the application. Filter private collections by the current user and use relative invariants for public pagination/search.
