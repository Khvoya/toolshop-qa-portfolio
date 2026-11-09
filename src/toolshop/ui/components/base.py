from playwright.sync_api import Locator, Page


class BaseComponent:
    def __init__(self, page: Page, root: Locator) -> None:
        self.page = page
        self.root = root
