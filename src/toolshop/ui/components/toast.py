from playwright.sync_api import Locator, Page

from toolshop.ui.components.base import BaseComponent


class ToastComponent(BaseComponent):
    def __init__(self, page: Page) -> None:
        super().__init__(page, page.get_by_role("alert").last)

    @property
    def message(self) -> Locator:
        return self.root
