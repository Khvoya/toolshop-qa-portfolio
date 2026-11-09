# UI spec template

```python
import allure
import pytest
from playwright.sync_api import expect

from toolshop.models import Product
from toolshop.ui import HomePage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.title("UI: <observable behavior>")
def test_<behavior>(home_page: HomePage, product: Product) -> None:
    with allure.step("Arrange: <API-backed state>"):
        home_page.open()
    with allure.step("Act: <page/component action>"):
        home_page.search(product.name)
    with allure.step("Assert: <web-first observable result>"):
        expect(home_page.product_card(product).root).to_be_visible()
```

Use `registered_user`, `page_with_cart`, or another existing fixture for state that is not the behavior under test.
