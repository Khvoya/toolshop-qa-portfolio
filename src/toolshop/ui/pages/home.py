from playwright.sync_api import Locator, expect

from toolshop.models import Product
from toolshop.steps import step
from toolshop.ui.base_page import BasePage
from toolshop.ui.components import PaginationComponent, ProductCardComponent


class HomePage(BasePage):
    @step("Open the product catalog")
    def open(self, path: str = "/") -> None:
        self.navigate(path)
        expect(self.product_cards.first).to_be_visible()

    @property
    def product_cards(self) -> Locator:
        return self.page.locator("a[data-test^='product-']")

    @property
    def pagination(self) -> PaginationComponent:
        return PaginationComponent(self.page)

    def product_card(self, product: Product) -> ProductCardComponent:
        return ProductCardComponent(self.page, product.id)

    @step("Search for a product")
    def search(self, query: str) -> None:
        self.page.get_by_test_id("search-query").fill(query)
        self.page.get_by_test_id("search-submit").click()
        expect(self.page.get_by_test_id("search-term")).to_have_text(query)
