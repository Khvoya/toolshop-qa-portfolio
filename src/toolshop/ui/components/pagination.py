from playwright.sync_api import Page

from toolshop.ui.components.base import BaseComponent


class PaginationComponent(BaseComponent):
    def __init__(self, page: Page) -> None:
        root = page.get_by_role("navigation").filter(has=page.get_by_test_id("pagination-next"))
        super().__init__(page, root)

    def next_page(self) -> None:
        self.root.get_by_test_id("pagination-next").click()

    def open_page(self, page_number: int) -> None:
        self.root.get_by_role("button", name=f"Page-{page_number}").click()
