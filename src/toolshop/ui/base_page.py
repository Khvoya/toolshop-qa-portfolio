from playwright.sync_api import Page

from toolshop.config import Settings


class BasePage:
    def __init__(self, page: Page, settings: Settings) -> None:
        self.page = page
        self.settings = settings

    def navigate(self, path: str) -> None:
        url = f"{self.settings.ui_base_url.rstrip('/')}/{path.lstrip('/')}"
        self.page.goto(url, wait_until="domcontentloaded")

    def session_storage_value(self, key: str) -> str:
        value = self.page.evaluate("key => sessionStorage.getItem(key)", key)
        if not isinstance(value, str) or not value:
            raise RuntimeError(f"Session storage key {key!r} is empty")
        return value
