import allure
import pytest
from playwright.sync_api import Page, expect

from toolshop.models import TestUser
from toolshop.ui import CartPage, CheckoutPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.title("UI: checkout requires a payment method")
@pytest.mark.negative
def test_checkout_payment_validation(
    page_with_cart: Page,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
    registered_user: TestUser,
) -> None:
    assert page_with_cart
    with allure.step("Arrange: reach payment through an API-created cart and browser session"):
        cart_page.open()
        cart_page.proceed_to_sign_in()
        checkout_page.sign_in(None)
        checkout_page.fill_address(registered_user.account.address)
    with allure.step("Assert: order submission is disabled until payment is selected"):
        expect(checkout_page.finish_button).to_be_visible()
        expect(checkout_page.finish_button).to_be_disabled()
