from playwright.sync_api import Locator, Page, expect

from toolshop.steps import step
from toolshop.ui.components.base import BaseComponent


class MainNavComponent(BaseComponent):
    def __init__(self, page: Page) -> None:
        root = page.get_by_role("navigation").filter(has=page.get_by_test_id("nav-home"))
        super().__init__(page, root)

    @property
    def sign_in_link(self) -> Locator:
        return self.root.get_by_test_id("nav-sign-in")

    @property
    def cart_quantity(self) -> Locator:
        return self.root.get_by_test_id("cart-quantity")

    @step("Open the sign-in page")
    def open_sign_in(self) -> None:
        self.sign_in_link.click()

    @step("Open user favorites")
    def open_favorites(self) -> None:
        self.root.get_by_test_id("nav-menu").click()
        self.root.get_by_test_id("nav-my-favorites").click()

    @step("Sign out")
    def sign_out(self) -> None:
        self.root.get_by_test_id("nav-menu").click()
        self.root.get_by_test_id("nav-sign-out").click()
        expect(self.sign_in_link).to_be_visible()

    @step("Open the cart")
    def open_cart(self) -> None:
        self.root.get_by_test_id("nav-cart").click()
