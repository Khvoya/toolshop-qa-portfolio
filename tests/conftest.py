import json
import re
from collections.abc import Generator, Iterator
from pathlib import Path
from typing import cast

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, ConsoleMessage, Error, Page, Playwright
from pytest import TestReport

from toolshop.api import ApiClient, ToolshopApi
from toolshop.config import Settings, get_settings
from toolshop.models import Cart, Credentials, Product, TestUser
from toolshop.services import TestDataManager
from toolshop.ui import (
    CartPage,
    CheckoutPage,
    FavoritesPage,
    HomePage,
    LoginPage,
    ProductDetailsPage,
    RegisterPage,
)

ARTIFACTS = Path("artifacts")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, TestReport, TestReport]:
    outcome = yield
    report = cast(TestReport, outcome.get_result())
    setattr(item, f"rep_{call.when}", report)
    return report


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session", autouse=True)
def configure_test_id(playwright: Playwright) -> None:
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(scope="session")
def browser_type_launch_args(settings: Settings) -> dict[str, object]:
    return {"headless": settings.headless}


@pytest.fixture
def api(playwright: Playwright, settings: Settings) -> Iterator[ToolshopApi]:
    request = playwright.request.new_context(base_url=settings.api_base_url)
    yield ToolshopApi(ApiClient(request, settings))
    request.dispose()


@pytest.fixture
def admin_api(playwright: Playwright, settings: Settings) -> Iterator[ToolshopApi]:
    request = playwright.request.new_context(base_url=settings.api_base_url)
    client = ApiClient(request, settings)
    result = ToolshopApi(client)
    result.authenticate(Credentials(email=settings.admin_email, password=settings.admin_password))
    yield result
    request.dispose()


@pytest.fixture
def test_data(api: ToolshopApi, admin_api: ToolshopApi) -> Iterator[TestDataManager]:
    manager = TestDataManager(api, admin_api)
    yield manager
    manager.cleanup()


@pytest.fixture
def registered_user(test_data: TestDataManager) -> TestUser:
    return test_data.create_user(authenticate=True)


@pytest.fixture
def product(api: ToolshopApi) -> Product:
    return api.products.first_regular_in_stock()


@pytest.fixture
def cart(test_data: TestDataManager, product: Product) -> Cart:
    return test_data.create_cart(product)


@pytest.fixture
def context(browser: Browser, settings: Settings) -> Iterator[BrowserContext]:
    browser_context = browser.new_context(
        base_url=settings.ui_base_url,
        viewport={"width": 1440, "height": 1000},
        record_video_dir=ARTIFACTS / "videos",
    )
    yield browser_context
    browser_context.close()


@pytest.fixture
def page(
    context: BrowserContext, settings: Settings, request: pytest.FixtureRequest
) -> Iterator[Page]:
    result = context.new_page()
    result.set_default_timeout(settings.action_timeout_ms)
    result.set_default_navigation_timeout(settings.navigation_timeout_ms)
    console_errors: list[str] = []

    def collect_console(message: ConsoleMessage) -> None:
        if message.type == "error":
            console_errors.append(message.text)

    def collect_page_error(error: Error) -> None:
        console_errors.append(str(error))

    result.on("console", collect_console)
    result.on("pageerror", collect_page_error)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield result

    report = getattr(request.node, "rep_call", None)
    failed = bool(report and report.failed)
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", request.node.name)
    test_dir = ARTIFACTS / "diagnostics" / safe_name
    test_dir.mkdir(parents=True, exist_ok=True)
    if failed:
        allure.attach(
            result.screenshot(full_page=True),
            name="Failure screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(result.url, name="Last page URL", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            "\n".join(console_errors) or "No browser errors",
            name="Browser errors",
            attachment_type=allure.attachment_type.TEXT,
        )
        trace_path = test_dir / "trace.zip"
        context.tracing.stop(path=trace_path)
    else:
        context.tracing.stop()
    context.close()
    video_path = Path(result.video.path()) if result.video else None
    if video_path and failed:
        allure.attach(
            video_path.read_bytes(),
            name="Failure video",
            attachment_type=allure.attachment_type.WEBM,
        )
        allure.attach(
            (test_dir / "trace.zip").read_bytes(),
            name="Playwright trace",
            attachment_type=allure.attachment_type.ZIP,
        )
    elif video_path:
        video_path.unlink(missing_ok=True)


@pytest.fixture
def authenticated_page(page: Page, registered_user: TestUser) -> Page:
    if registered_user.token is None:
        raise RuntimeError("The registered user has no API token")
    token = json.dumps(registered_user.token.get_secret_value())
    page.add_init_script(f"localStorage.setItem('auth-token', {token});")
    return page


@pytest.fixture
def page_with_cart(authenticated_page: Page, cart: Cart) -> Page:
    cart_id = json.dumps(cart.id)
    authenticated_page.add_init_script(f"sessionStorage.setItem('cart_id', {cart_id});")
    return authenticated_page


@pytest.fixture
def home_page(page: Page, settings: Settings) -> HomePage:
    return HomePage(page, settings)


@pytest.fixture
def login_page(page: Page, settings: Settings) -> LoginPage:
    return LoginPage(page, settings)


@pytest.fixture
def register_page(page: Page, settings: Settings) -> RegisterPage:
    return RegisterPage(page, settings)


@pytest.fixture
def product_details_page(page: Page, settings: Settings) -> ProductDetailsPage:
    return ProductDetailsPage(page, settings)


@pytest.fixture
def cart_page(page: Page, settings: Settings) -> CartPage:
    return CartPage(page, settings)


@pytest.fixture
def checkout_page(page: Page, settings: Settings) -> CheckoutPage:
    return CheckoutPage(page, settings)


@pytest.fixture
def favorites_page(authenticated_page: Page, settings: Settings) -> FavoritesPage:
    return FavoritesPage(authenticated_page, settings)
