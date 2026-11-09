import allure
import pytest

from toolshop.factories import UserFactory

pytestmark = pytest.mark.self


@allure.title("Self: user factory creates unique credentials")
def test_user_factory_uniqueness() -> None:
    with allure.step("Act: build two customer DTOs"):
        first = UserFactory.build()
        second = UserFactory.build()
    with allure.step("Assert: generated identities are independent and valid"):
        assert first.email != second.email
        assert first.password.get_secret_value() != second.password.get_secret_value()
        assert first.address.postal_code == "1234AB"
