from playwright.sync_api import Locator, expect

from toolshop.models import Product
from toolshop.steps import step
from toolshop.ui.base_page import BasePage


class CartPage(BasePage):
    @step("Open the shopping cart")
    def open(self, path: str = "/checkout") -> None:
        self.navigate(path)
        expect(self.page.get_by_test_id("cart-total")).to_be_visible()

    def row(self, product: Product) -> Locator:
        return self.page.locator("tbody tr").filter(
            has=self.page.get_by_test_id("product-title").get_by_text(product.name, exact=False)
        )

    def product_title(self, product: Product) -> Locator:
        return self.row(product).get_by_test_id("product-title")

    def quantity(self, product: Product) -> Locator:
        return self.page.get_by_label(f"Quantity for {product.name}", exact=True)

    def line_price(self, product: Product) -> Locator:
        return self.row(product).get_by_test_id("line-price")

    @property
    def total(self) -> Locator:
        return self.page.get_by_test_id("cart-total")

    @step("Change cart item quantity")
    def set_quantity(self, product: Product, quantity: int) -> None:
        field = self.quantity(product)
        field.fill(str(quantity))
        field.press("Tab")
        expect(field).to_have_value(str(quantity))

    @step("Proceed from cart to sign-in")
    def proceed_to_sign_in(self) -> None:
        self.page.get_by_test_id("proceed-1").click()
