import allure
import pytest

from toolshop.api import ApiResponseError, ToolshopApi
from toolshop.models import Cart, Product

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.title("API: cart item quantity can be updated")
@pytest.mark.smoke
def test_cart_quantity_update(api: ToolshopApi, cart: Cart, product: Product) -> None:
    with allure.step("Act: change the generated cart item quantity"):
        api.carts.update_quantity(cart.id, product.id, 3)
        updated = api.carts.get(cart.id)
    with allure.step("Assert: the cart contains only the requested quantity"):
        assert len(updated.cart_items) == 1
        assert updated.cart_items[0].product_id == product.id
        assert updated.cart_items[0].quantity == 3


@allure.title("API: zero cart quantity is rejected")
@pytest.mark.negative
def test_cart_rejects_zero_quantity(api: ToolshopApi, cart: Cart, product: Product) -> None:
    with (
        allure.step("Act: submit an invalid zero quantity"),
        pytest.raises(ApiResponseError) as error,
    ):
        api.carts.add_item(cart.id, product.id, quantity=0)
    with allure.step("Assert: the request fails validation"):
        assert error.value.status == 422
