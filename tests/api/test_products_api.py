import allure
import pytest

from toolshop.api import ToolshopApi
from toolshop.models import Product

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.title("API: catalog page matches the typed product contract")
@pytest.mark.smoke
def test_catalog_contract(api: ToolshopApi) -> None:
    with allure.step("Act: request the first catalog page"):
        page = api.products.list()
    with allure.step("Assert: pagination and product fields are valid"):
        assert page.current_page == 1
        assert page.data
        assert len(page.data) <= page.per_page
        assert page.total >= len(page.data)
        assert all(item.id and item.name and item.price >= 0 for item in page.data)


@allure.title("API: catalog pagination returns the requested page")
def test_catalog_pagination(api: ToolshopApi) -> None:
    with allure.step("Arrange: read catalog metadata"):
        first_page = api.products.list()
        if first_page.last_page < 2:
            pytest.skip("The seeded catalog has only one page")
    with allure.step("Act: request the second catalog page"):
        second_page = api.products.list(page=2)
    with allure.step("Assert: the requested page contains distinct products"):
        assert second_page.current_page == 2
        assert second_page.data
        assert {item.id for item in second_page.data}.isdisjoint(
            {item.id for item in first_page.data}
        )


@allure.title("API: product search returns matching products")
def test_product_search(api: ToolshopApi, product: Product) -> None:
    with allure.step("Act: search by the exact seeded product name"):
        results = api.products.search(product.name)
    with allure.step("Assert: the requested product is present and details are consistent"):
        assert results.total >= 1
        assert product.id in {item.id for item in results.data}
        details = api.products.get(product.id)
        assert details.id == product.id
        assert details.name == product.name
        assert details.price == product.price
