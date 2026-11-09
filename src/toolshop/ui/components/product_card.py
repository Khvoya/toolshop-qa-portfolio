from playwright.sync_api import Locator, Page

from toolshop.ui.components.base import BaseComponent


class ProductCardComponent(BaseComponent):
    def __init__(self, page: Page, product_id: str) -> None:
        super().__init__(page, page.get_by_test_id(f"product-{product_id}"))

    @property
    def name(self) -> Locator:
        return self.root.get_by_test_id("product-name")

    @property
    def price(self) -> Locator:
        return self.root.get_by_test_id("product-price")

    def open(self) -> None:
        self.root.click()
