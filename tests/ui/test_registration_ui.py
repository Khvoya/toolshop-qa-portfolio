import allure
import pytest

from toolshop.api import ToolshopApi
from toolshop.factories import UserFactory
from toolshop.services import TestDataManager
from toolshop.ui import RegisterPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.title("UI: a new customer can register and then authenticate through API")
@pytest.mark.smoke
def test_customer_registration(
    register_page: RegisterPage, api: ToolshopApi, test_data: TestDataManager
) -> None:
    with allure.step("Arrange: generate a unique registration DTO"):
        new_user = UserFactory.build()
    with allure.step("Act: complete and submit the UI registration form"):
        register_page.open()
        register_page.register(new_user)
    with allure.step("Assert: the new credentials authenticate and return the same identity"):
        api.authenticate(UserFactory.credentials(new_user))
        account = api.users.me()
        test_data.track_user(account.id)
        assert account.email == new_user.email
        assert account.first_name == new_user.first_name
