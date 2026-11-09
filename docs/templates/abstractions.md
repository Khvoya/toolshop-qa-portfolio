# Page, component, and API resource templates

## Page method

```python
@step("<clear UI action>")
def perform_action(self) -> None:
    self.page.get_by_test_id("stable-id").click()
```

A new page inherits `BasePage`, receives `Page` and `Settings`, and uses `navigate("/path")`. Register its fixture in `tests/conftest.py` and export it from the package.

## Component

```python
class RepeatedComponent(BaseComponent):
    def __init__(self, page: Page, entity_id: str) -> None:
        super().__init__(page, page.get_by_test_id(f"entity-{entity_id}"))
```

All locators inside a component start from `self.root`. Return `Locator` explicitly for web-first assertions in specs.

## API resource method

```python
@step("<clear API action>")
def get_entity(self, entity_id: str) -> Entity:
    return self._client.request_model("GET", f"/entities/{entity_id}", model=Entity)
```

Add a Pydantic `Entity` model first. Use `expected_status` for non-200 success, `retry=False` for mutations, and a separate typed method when a negative response body must be modeled.
