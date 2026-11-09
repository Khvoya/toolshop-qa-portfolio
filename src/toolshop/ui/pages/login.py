from playwright.sync_api import Locator, expect

from toolshop.models import Credentials
from toolshop.steps import step
from toolshop.ui.base_page import BasePage


class LoginPage(BasePage):
    @step("Open the login page")
    def open(self, path: str = "/auth/login") -> None:
        self.navigate(path)
        expect(self.page.get_by_test_id("login-form")).to_be_visible()

    @property
    def error(self) -> Locator:
        return self.page.get_by_test_id("login-error")

    @step("Submit credentials")
    def login(self, credentials: Credentials) -> None:
        self.page.get_by_test_id("email").fill(str(credentials.email))
        self.page.get_by_test_id("password").fill(credentials.password.get_secret_value())
        self.page.get_by_test_id("login-submit").click()

    @step("Sign in through UI")
    def login_successfully(self, credentials: Credentials) -> None:
        self.login(credentials)
        expect(self.page).to_have_url(f"{self.settings.ui_base_url}/account")
