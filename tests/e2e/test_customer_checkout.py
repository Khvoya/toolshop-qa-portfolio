import allure
import pytest
from playwright.sync_api import Page, expect

from toolshop.api import ToolshopApi
from toolshop.models import Cart, Product, TestUser
from toolshop.services import TestDataManager
from toolshop.ui import CartPage, CheckoutPage, HomePage, LoginPage, ProductDetailsPage
from toolshop.ui.components import HeaderComponent

pytestmark = [pytest.mark.e2e, pytest.mark.regression]


@allure.title("E2E: new customer buys a product after UI login")
@allure.description(
    "API creates identity; UI executes login, selection, cart and payment; API verifies the order."
)
@pytest.mark.smoke
def test_customer_checkout_after_ui_login(
    page: Page,
    api: ToolshopApi,
    test_data: TestDataManager,
    registered_user: TestUser,
    product: Product,
    login_page: LoginPage,
    home_page: HomePage,
    product_details_page: ProductDetailsPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
) -> None:
    with allure.step("Arrange: authenticate the generated customer through the login UI"):
        login_page.open()
        login_page.login_successfully(registered_user.credentials)
    with allure.step("Act: select the API-selected product and add it to cart"):
        home_page.open()
        home_page.product_card(product).open()
        product_details_page.add_to_cart()
        test_data.track_cart(product_details_page.session_storage_value("cart_id"))
    with allure.step("Act: verify the cart and complete all checkout steps"):
        HeaderComponent(page).navigation.open_cart()
        expect(cart_page.product_title(product)).to_be_visible()
        cart_page.proceed_to_sign_in()
        checkout_page.sign_in(None)
        checkout_page.fill_address(registered_user.account.address)
        checkout_page.pay_cash_on_delivery()
    with allure.step("Assert: independent API verification finds the customer's paid order"):
        orders = [item for item in api.orders.list().data if item.user_id == registered_user.id]
        assert len(orders) == 1
        assert orders[0].total == pytest.approx(product.price)
        assert orders[0].status == "AWAITING_FULFILLMENT"


@allure.title("E2E: API-prepared cart is checked out through UI")
@allure.description(
    "API fixtures create user and cart; browser storage reuses state; "
    "UI checkout is verified via API."
)
def test_checkout_with_api_preconditions(
    page_with_cart: Page,
    api: ToolshopApi,
    registered_user: TestUser,
    product: Product,
    cart: Cart,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
) -> None:
    assert page_with_cart
    with allure.step("Arrange: open the API-created cart in an authenticated browser"):
        cart_page.open()
        expect(cart_page.quantity(product)).to_have_value("1")
        assert cart.id
    with allure.step("Act: complete sign-in, address and cash-on-delivery payment steps"):
        cart_page.proceed_to_sign_in()
        checkout_page.sign_in(None)
        checkout_page.fill_address(registered_user.account.address)
        checkout_page.pay_cash_on_delivery()
    with allure.step("Assert: the order is persisted with the expected customer and total"):
        order = api.orders.list().data[0]
        assert order.user_id == registered_user.id
        assert order.total == pytest.approx(product.price)
        assert order.status == "AWAITING_FULFILLMENT"
