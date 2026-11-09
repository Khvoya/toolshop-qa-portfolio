import allure
import pytest
from pydantic import SecretStr

from toolshop.api import ApiResponseError, ToolshopApi
from toolshop.factories import UserFactory
from toolshop.models import TestUser

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.title("API: registration returns the customer contract")
@pytest.mark.smoke
def test_registered_user_can_be_read(api: ToolshopApi, registered_user: TestUser) -> None:
    with allure.step("Act: read the current user with the generated bearer token"):
        current_user = api.users.me()
    with allure.step("Assert: persisted identity and address match the registration"):
        assert current_user.id == registered_user.id
        assert current_user.email == registered_user.account.email
        assert current_user.address == registered_user.account.address


@allure.title("API: weak password is rejected during registration")
@pytest.mark.negative
def test_registration_rejects_weak_password(api: ToolshopApi) -> None:
    with allure.step("Arrange: a unique customer DTO with a weak password"):
        new_user = UserFactory.build().model_copy(update={"password": SecretStr("weakpassword")})
    with allure.step("Act: submit the invalid registration request"):
        error = api.users.register_rejected(new_user)
    with allure.step("Assert: validation details are returned"):
        assert error.model_extra


@allure.title("API: duplicate email cannot be registered twice")
@pytest.mark.negative
def test_registration_rejects_duplicate_email(api: ToolshopApi, registered_user: TestUser) -> None:
    with allure.step("Arrange: another customer with the same email"):
        duplicate = UserFactory.build().model_copy(update={"email": registered_user.account.email})
    with (
        allure.step("Act/Assert: the duplicate request is rejected"),
        pytest.raises(ApiResponseError) as error,
    ):
        api.users.register(duplicate)
    assert error.value.status == 409
