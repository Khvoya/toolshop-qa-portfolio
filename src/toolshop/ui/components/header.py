from playwright.sync_api import Page

from toolshop.ui.components.navigation import MainNavComponent


class HeaderComponent:
    def __init__(self, page: Page) -> None:
        self.navigation = MainNavComponent(page)
