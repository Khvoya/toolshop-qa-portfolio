import allure
import pytest
from playwright.sync_api import Page, expect
from pydantic import SecretStr

from toolshop.factories import UserFactory
from toolshop.models import Credentials, TestUser
from toolshop.ui import LoginPage
from toolshop.ui.components import HeaderComponent

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.title("UI: customer can sign in and sign out")
@pytest.mark.smoke
def test_login_and_logout(page: Page, login_page: LoginPage, registered_user: TestUser) -> None:
    with allure.step("Act: sign in with API-generated credentials"):
        login_page.open()
        login_page.login_successfully(registered_user.credentials)
    with allure.step("Assert: the user menu replaces the sign-in link"):
        header = HeaderComponent(page)
        expect(header.navigation.root.get_by_test_id("nav-menu")).to_be_visible()
    with allure.step("Act/Assert: sign out and restore anonymous navigation"):
        header.navigation.sign_out()


@allure.title("UI: invalid credentials show an authentication error")
@pytest.mark.negative
def test_invalid_login(login_page: LoginPage) -> None:
    with allure.step("Arrange: credentials for an unregistered email"):
        new_user = UserFactory.build()
        credentials = Credentials(email=new_user.email, password=SecretStr("Invalid!123"))
    with allure.step("Act: submit the invalid credentials"):
        login_page.open()
        login_page.login(credentials)
    with allure.step("Assert: an accessible error is displayed"):
        expect(login_page.error).to_be_visible()
        expect(login_page.error).to_contain_text("Invalid email or password")
