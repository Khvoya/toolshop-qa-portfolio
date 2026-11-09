# API spec template

```python
import allure
import pytest

from toolshop.api import ToolshopApi
from toolshop.models import Product

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.title("API: <observable behavior>")
def test_<behavior>(api: ToolshopApi, product: Product) -> None:
    with allure.step("Arrange: <existing fixture or resource precondition>"):
        product_id = product.id
    with allure.step("Act: <typed resource action>"):
        actual = api.products.get(product_id)
    with allure.step("Assert: <business invariant>"):
        assert actual.id == product_id
```

Use `pytest.raises(ApiResponseError)` around a resource method for an unsupported negative variant, or add a typed resource method when the negative response body itself needs validation.
