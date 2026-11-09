from datetime import date

from toolshop.api.client import ApiClient
from toolshop.models import (
    Cart,
    Credentials,
    ErrorResponse,
    Favorite,
    NewUser,
    Order,
    OrderCreate,
    OrderPage,
    Product,
    ProductPage,
    Token,
    User,
)
from toolshop.steps import step


class AuthApi:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    @step("Authenticate through API")
    def login(self, credentials: Credentials) -> Token:
        payload = {
            "email": str(credentials.email),
            "password": credentials.password.get_secret_value(),
        }
        return self._client.request_model(
            "POST", "/users/login", model=Token, payload=payload, retry=False
        )

    @step("Reject invalid credentials through API")
    def login_rejected(self, credentials: Credentials) -> ErrorResponse:
        payload = {
            "email": str(credentials.email),
            "password": credentials.password.get_secret_value(),
        }
        return self._client.request_model(
            "POST",
            "/users/login",
            model=ErrorResponse,
            expected_status=401,
            payload=payload,
            retry=False,
        )

    @step("Log out through API")
    def logout(self) -> None:
        self._client.request("GET", "/users/logout")


class UsersApi:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    @step("Register a user through API")
    def register(self, new_user: NewUser) -> User:
        payload = new_user.model_dump(mode="json", exclude={"password"})
        payload["password"] = new_user.password.get_secret_value()
        return self._client.request_model(
            "POST",
            "/users/register",
            model=User,
            expected_status=201,
            payload=payload,
            retry=False,
        )

    @step("Reject invalid user registration through API")
    def register_rejected(self, new_user: NewUser) -> ErrorResponse:
        payload = new_user.model_dump(mode="json", exclude={"password"})
        payload["password"] = new_user.password.get_secret_value()
        return self._client.request_model(
            "POST",
            "/users/register",
            model=ErrorResponse,
            expected_status=422,
            payload=payload,
            retry=False,
        )

    @step("Read the authenticated user through API")
    def me(self) -> User:
        return self._client.request_model("GET", "/users/me", model=User)

    @step("Delete a generated user through admin API")
    def delete(self, user_id: str) -> None:
        self._client.request("DELETE", f"/users/{user_id}", expected_status=(204, 404), retry=False)


class ProductsApi:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    @step("Read a product catalog page through API")
    def list(self, page: int = 1) -> ProductPage:
        return self._client.request_model(
            "GET", "/products", model=ProductPage, params={"page": page}
        )

    @step("Search products through API")
    def search(self, query: str, page: int = 1) -> ProductPage:
        return self._client.request_model(
            "GET", "/products/search", model=ProductPage, params={"q": query, "page": page}
        )

    @step("Read product details through API")
    def get(self, product_id: str) -> Product:
        return self._client.request_model("GET", f"/products/{product_id}", model=Product)

    def first_regular_in_stock(self) -> Product:
        for page_number in range(1, self.list().last_page + 1):
            for product in self.list(page_number).data:
                if product.in_stock and not product.is_rental and product.name != "Thor Hammer":
                    return product
        raise RuntimeError("No regular in-stock product is available")


class CartsApi:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    @step("Create a cart through API")
    def create(self) -> str:
        data = self._client.request("POST", "/carts", expected_status=201, payload={}, retry=False)
        cart_id = data.get("id") if isinstance(data, dict) else None
        if not isinstance(cart_id, str):
            raise TypeError("Cart creation response does not contain an id")
        return cart_id

    @step("Add a product to the cart through API")
    def add_item(self, cart_id: str, product_id: str, quantity: int = 1) -> None:
        self._client.request(
            "POST",
            f"/carts/{cart_id}",
            payload={"product_id": product_id, "quantity": quantity},
            retry=False,
        )

    @step("Read the cart through API")
    def get(self, cart_id: str) -> Cart:
        return self._client.request_model("GET", f"/carts/{cart_id}", model=Cart)

    @step("Update cart item quantity through API")
    def update_quantity(self, cart_id: str, product_id: str, quantity: int) -> None:
        self._client.request(
            "PUT",
            f"/carts/{cart_id}/product/quantity",
            payload={"product_id": product_id, "quantity": quantity},
            retry=False,
        )

    @step("Delete the cart through API")
    def delete(self, cart_id: str) -> None:
        self._client.request("DELETE", f"/carts/{cart_id}", expected_status=(204, 404), retry=False)


class FavoritesApi:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    @step("List favorites through API")
    def list(self) -> list[Favorite]:
        return self._client.request_list("GET", "/favorites", model=Favorite)

    @step("Reject anonymous favorites access through API")
    def list_unauthorized(self) -> ErrorResponse:
        return self._client.request_model(
            "GET", "/favorites", model=ErrorResponse, expected_status=401
        )

    @step("Add a favorite through API")
    def add(self, product_id: str) -> Favorite:
        return self._client.request_model(
            "POST",
            "/favorites",
            model=Favorite,
            expected_status=201,
            payload={"product_id": product_id},
            retry=False,
        )

    @step("Delete a favorite through API")
    def delete(self, favorite_id: str) -> None:
        self._client.request(
            "DELETE", f"/favorites/{favorite_id}", expected_status=(204, 404), retry=False
        )


class OrdersApi:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    @step("Create an order through API")
    def create(self, order: OrderCreate) -> Order:
        payload = order.model_dump(mode="json")
        payload["invoice_date"] = date.today().isoformat()
        return self._client.request_model(
            "POST",
            "/invoices",
            model=Order,
            expected_status=201,
            payload=payload,
            retry=False,
        )

    @step("List orders through API")
    def list(self) -> OrderPage:
        return self._client.request_model("GET", "/invoices", model=OrderPage)

    @step("Read an order through API")
    def get(self, order_id: str) -> Order:
        return self._client.request_model("GET", f"/invoices/{order_id}", model=Order)


class ToolshopApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client
        self.auth = AuthApi(client)
        self.users = UsersApi(client)
        self.products = ProductsApi(client)
        self.carts = CartsApi(client)
        self.favorites = FavoritesApi(client)
        self.orders = OrdersApi(client)

    def authenticate(self, credentials: Credentials) -> Token:
        token = self.auth.login(credentials)
        self.client.authenticate(token.access_token)
        return token
