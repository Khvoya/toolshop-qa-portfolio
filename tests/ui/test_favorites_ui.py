import allure
import pytest
from playwright.sync_api import expect

from toolshop.models import Product, TestUser
from toolshop.services import TestDataManager
from toolshop.ui import FavoritesPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@allure.title("UI: an API-created favorite is visible in the customer account")
def test_favorites_list(
    favorites_page: FavoritesPage,
    test_data: TestDataManager,
    registered_user: TestUser,
    product: Product,
) -> None:
    assert registered_user.id
    with allure.step("Arrange: create favorite state through API"):
        test_data.create_favorite(product)
    with allure.step("Act: open the favorites page with API browser authentication"):
        favorites_page.open()
    with allure.step("Assert: the selected product is displayed"):
        expect(favorites_page.product_names).to_have_text([product.name])
