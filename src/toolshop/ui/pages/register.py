from playwright.sync_api import expect

from toolshop.models import NewUser
from toolshop.steps import step
from toolshop.ui.base_page import BasePage
from toolshop.ui.countries import country_code


class RegisterPage(BasePage):
    @step("Open the registration page")
    def open(self, path: str = "/auth/register") -> None:
        self.navigate(path)
        expect(self.page.get_by_test_id("register-form")).to_be_visible()

    @step("Register a new customer through UI")
    def register(self, user: NewUser) -> None:
        fields = {
            "first-name": user.first_name,
            "last-name": user.last_name,
            "dob": user.dob.isoformat(),
            "postal_code": user.address.postal_code,
            "house_number": user.address.house_number or "",
            "street": user.address.street,
            "city": user.address.city,
            "state": user.address.state,
            "phone": user.phone,
            "email": str(user.email),
            "password": user.password.get_secret_value(),
        }
        for test_id, value in fields.items():
            self.page.get_by_test_id(test_id).fill(value)
        self.page.get_by_test_id("country").select_option(value=country_code(user.address.country))
        self.page.get_by_test_id("register-submit").click()
        expect(self.page).to_have_url(f"{self.settings.ui_base_url}/auth/login")
