import allure
import pytest

from toolshop.api import ToolshopApi
from toolshop.models import Product, TestUser
from toolshop.services import TestDataManager

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.title("API: authenticated customer can create and list a favorite")
@pytest.mark.smoke
def test_favorite_lifecycle(
    api: ToolshopApi,
    test_data: TestDataManager,
    registered_user: TestUser,
    product: Product,
) -> None:
    with allure.step("Arrange: create a favorite through the API fixture service"):
        test_data.create_favorite(product)
    with allure.step("Act: list the current customer's favorites"):
        favorites = api.favorites.list()
    with allure.step("Assert: the favorite belongs to the generated user and product"):
        assert len(favorites) == 1
        assert favorites[0].user_id == registered_user.id
        assert favorites[0].product_id == product.id
        assert favorites[0].product is not None
        assert favorites[0].product.name == product.name


@allure.title("API: anonymous customer cannot list favorites")
@pytest.mark.negative
def test_anonymous_favorites_are_rejected(api: ToolshopApi) -> None:
    with allure.step("Act: request a private resource without a token"):
        error = api.favorites.list_unauthorized()
    with allure.step("Assert: API returns an authorization error"):
        assert error.message == "Unauthorized"
