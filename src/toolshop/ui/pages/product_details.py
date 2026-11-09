from playwright.sync_api import Locator, expect

from toolshop.models import Product
from toolshop.steps import step
from toolshop.ui.base_page import BasePage
from toolshop.ui.components import ToastComponent


class ProductDetailsPage(BasePage):
    @step("Open product details")
    def open(self, product: Product) -> None:
        self.navigate(f"/product/{product.id}")
        expect(self.name).to_have_text(product.name)

    @property
    def name(self) -> Locator:
        return self.page.get_by_test_id("product-name")

    @property
    def description(self) -> Locator:
        return self.page.get_by_test_id("product-description")

    @property
    def unit_price(self) -> Locator:
        return self.page.get_by_test_id("unit-price")

    @property
    def toast(self) -> ToastComponent:
        return ToastComponent(self.page)

    @step("Set product quantity")
    def set_quantity(self, quantity: int) -> None:
        self.page.get_by_test_id("quantity").fill(str(quantity))

    @step("Add the product to cart")
    def add_to_cart(self) -> None:
        self.page.get_by_test_id("add-to-cart").click()
        expect(self.toast.message).to_be_visible()

    @step("Add the product to favorites")
    def add_to_favorites(self) -> None:
        self.page.get_by_test_id("add-to-favorites").click()
        expect(self.toast.message).to_be_visible()
