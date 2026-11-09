import allure
import pytest
from pydantic import SecretStr

from toolshop.api import ToolshopApi
from toolshop.models import Credentials, TestUser

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.title("API: a registered customer receives a bearer token")
@allure.description("Registration is arranged through API; login returns a usable typed token.")
@pytest.mark.smoke
def test_customer_login(api: ToolshopApi, registered_user: TestUser) -> None:
    with allure.step("Act: authenticate with the generated credentials"):
        token = api.auth.login(registered_user.credentials)
    with allure.step("Assert: the token is present and has an expiration"):
        assert token.access_token
        assert token.token_type.lower() == "bearer"
        assert token.expires_in > 0


@allure.title("API: invalid credentials are rejected")
@pytest.mark.negative
def test_login_with_invalid_password(api: ToolshopApi, registered_user: TestUser) -> None:
    credentials = Credentials(
        email=registered_user.credentials.email,
        password=SecretStr("Wrong!Password123"),
    )
    with allure.step("Act: submit a valid email and an invalid password"):
        error = api.auth.login_rejected(credentials)
    with allure.step("Assert: API exposes an authentication error"):
        assert error.error


@allure.title("API: logout invalidates the current token")
def test_logout_invalidates_token(api: ToolshopApi, registered_user: TestUser) -> None:
    with allure.step("Act: log out the authenticated API session"):
        api.auth.logout()
    with allure.step("Assert: the invalidated token cannot access private favorites"):
        error = api.favorites.list_unauthorized()
        assert error.message == "Unauthorized"
