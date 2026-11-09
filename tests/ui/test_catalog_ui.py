import allure
import pytest
from playwright.sync_api import expect

from toolshop.models import Product
from toolshop.ui import HomePage, ProductDetailsPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.title("UI: catalog shows API product data")
@pytest.mark.smoke
def test_catalog_product_card(home_page: HomePage, product: Product) -> None:
    with allure.step("Act: open the catalog"):
        home_page.open()
    with allure.step("Assert: the selected product card has correct name and price"):
        card = home_page.product_card(product)
        expect(card.name).to_have_text(product.name)
        expect(card.price).to_have_text(f"${product.price:.2f}")


@allure.title("UI: catalog search finds a known product")
def test_catalog_search(home_page: HomePage, product: Product) -> None:
    with allure.step("Arrange: open the catalog"):
        home_page.open()
    with allure.step("Act: submit the exact product name"):
        home_page.search(product.name)
    with allure.step("Assert: the product card is displayed"):
        expect(home_page.product_card(product).root).to_be_visible()


@allure.title("UI: product details match the API model")
def test_product_details(
    home_page: HomePage, product_details_page: ProductDetailsPage, product: Product
) -> None:
    with allure.step("Act: navigate from a catalog card to product details"):
        home_page.open()
        home_page.product_card(product).open()
    with allure.step("Assert: name, description and unit price match API data"):
        expect(product_details_page.name).to_have_text(product.name)
        expect(product_details_page.description).to_have_text(product.description)
        expect(product_details_page.unit_price).to_have_text(f"{product.price:.2f}")
