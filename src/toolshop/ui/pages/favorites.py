from playwright.sync_api import Locator, expect

from toolshop.steps import step
from toolshop.ui.base_page import BasePage


class FavoritesPage(BasePage):
    @step("Open favorite products")
    def open(self, path: str = "/account/favorites") -> None:
        self.navigate(path)
        expect(self.page.get_by_test_id("page-title")).to_be_visible()

    @property
    def product_names(self) -> Locator:
        return self.page.get_by_test_id("product-name")
