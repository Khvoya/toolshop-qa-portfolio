# E2E spec template

```python
import allure
import pytest

from toolshop.api import ToolshopApi
from toolshop.models import TestUser

pytestmark = [pytest.mark.e2e, pytest.mark.regression]


@allure.title("E2E: <critical customer journey>")
def test_<journey>(api: ToolshopApi, registered_user: TestUser) -> None:
    with allure.step("Arrange: <API fixture state>"):
        user_id = registered_user.id
    with allure.step("Act: <UI journey through page objects>"):
        ...
    with allure.step("Assert: <independent API verification>"):
        assert user_id
```

A real E2E spec must:

1. Use `pytestmark = [pytest.mark.e2e, pytest.mark.regression]`.
2. Arrange identity/state through API fixtures.
3. Exercise the critical UI journey through pages/components.
4. Verify the resulting persisted state independently through a typed API resource.
5. Filter by the unique generated user/entity rather than assuming a global record count.

Refer to `tests/e2e/test_customer_checkout.py` for the complete canonical pattern. Keep only critical cross-layer journeys in this suite.
