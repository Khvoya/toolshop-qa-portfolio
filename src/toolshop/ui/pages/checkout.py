from playwright.sync_api import Locator, expect

from toolshop.models import Address, Credentials
from toolshop.steps import step
from toolshop.ui.base_page import BasePage
from toolshop.ui.countries import country_code


class CheckoutPage(BasePage):
    @step("Complete the checkout sign-in step")
    def sign_in(self, credentials: Credentials | None) -> None:
        if credentials is not None and self.page.get_by_test_id("login-submit").is_visible():
            self.page.get_by_test_id("email").fill(str(credentials.email))
            self.page.get_by_test_id("password").fill(credentials.password.get_secret_value())
            self.page.get_by_test_id("login-submit").click()
        proceed = self.page.get_by_test_id("proceed-2")
        expect(proceed).to_be_enabled()
        proceed.click()

    @step("Complete the billing address step")
    def fill_address(self, address: Address) -> None:
        self.page.get_by_test_id("country").select_option(value=country_code(address.country))
        fields = {
            "postal_code": address.postal_code,
            "house_number": address.house_number or "",
            "street": address.street,
            "city": address.city,
            "state": address.state,
        }
        for test_id, value in fields.items():
            self.page.get_by_test_id(test_id).fill(value)
        proceed = self.page.get_by_test_id("proceed-3")
        expect(proceed).to_be_enabled()
        proceed.click()

    @property
    def finish_button(self) -> Locator:
        return self.page.get_by_test_id("finish")

    @property
    def confirmation(self) -> Locator:
        return self.page.locator("#order-confirmation")

    @step("Select cash on delivery and submit the order")
    def pay_cash_on_delivery(self) -> None:
        self.page.get_by_test_id("payment-method").select_option("cash-on-delivery")
        expect(self.finish_button).to_be_enabled()
        self.finish_button.click()
        expect(self.page.get_by_test_id("payment-success-message")).to_be_visible()
        self.finish_button.click()
        expect(self.confirmation).to_be_visible()
        expect(self.confirmation).to_contain_text("INV-")
