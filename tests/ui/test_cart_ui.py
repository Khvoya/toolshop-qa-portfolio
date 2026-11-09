import allure
import pytest
from playwright.sync_api import Page, expect

from toolshop.models import Cart, Product
from toolshop.services import TestDataManager
from toolshop.ui import CartPage, ProductDetailsPage
from toolshop.ui.components import HeaderComponent

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.title("UI: adding a product updates the cart badge")
@pytest.mark.smoke
def test_add_product_to_cart(
    page: Page,
    product_details_page: ProductDetailsPage,
    product: Product,
    test_data: TestDataManager,
) -> None:
    with allure.step("Act: add one API-selected product from its details page"):
        product_details_page.open(product)
        product_details_page.add_to_cart()
        test_data.track_cart(product_details_page.session_storage_value("cart_id"))
    with allure.step("Assert: navigation shows one cart item"):
        expect(HeaderComponent(page).navigation.cart_quantity).to_have_text("1")


@allure.title("UI: cart recalculates line and order totals after quantity change")
def test_cart_quantity_recalculation(
    page_with_cart: Page,
    cart_page: CartPage,
    cart: Cart,
    product: Product,
) -> None:
    assert page_with_cart
    with allure.step("Arrange: open an API-created cart"):
        cart_page.open()
        expect(cart_page.quantity(product)).to_have_value("1")
    with allure.step("Act: increase the quantity to three"):
        cart_page.set_quantity(product, 3)
    with allure.step("Assert: line and order totals use the new quantity"):
        expected_total = f"${product.price * 3:.2f}"
        expect(cart_page.line_price(product)).to_have_text(expected_total)
        expect(cart_page.total).to_have_text(expected_total)
