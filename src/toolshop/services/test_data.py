import allure
from pydantic import SecretStr

from toolshop.api import ApiResponseError, ToolshopApi
from toolshop.factories import UserFactory
from toolshop.models import Cart, Product, TestUser


class TestDataManager:
    __test__ = False

    def __init__(self, api: ToolshopApi, admin_api: ToolshopApi) -> None:
        self.api = api
        self._admin_api = admin_api
        self._user_ids: list[str] = []
        self._cart_ids: list[str] = []
        self._favorite_ids: list[str] = []

    def create_user(self, *, authenticate: bool = False) -> TestUser:
        new_user = UserFactory.build()
        account = self.api.users.register(new_user)
        self._user_ids.append(account.id)
        test_user = TestUser(
            account=account,
            credentials=UserFactory.credentials(new_user),
        )
        if authenticate:
            token = self.api.authenticate(test_user.credentials)
            test_user.token = SecretStr(token.access_token)
        return test_user

    def track_user(self, user_id: str) -> None:
        if user_id not in self._user_ids:
            self._user_ids.append(user_id)

    def track_cart(self, cart_id: str) -> None:
        if cart_id not in self._cart_ids:
            self._cart_ids.append(cart_id)

    def create_cart(self, product: Product, quantity: int = 1) -> Cart:
        cart_id = self.api.carts.create()
        self._cart_ids.append(cart_id)
        self.api.carts.add_item(cart_id, product.id, quantity)
        return self.api.carts.get(cart_id)

    def create_favorite(self, product: Product) -> None:
        favorite = self.api.favorites.add(product.id)
        self._favorite_ids.append(favorite.id)

    def cleanup(self) -> None:
        for favorite_id in reversed(self._favorite_ids):
            self.api.favorites.delete(favorite_id)
        for cart_id in reversed(self._cart_ids):
            self.api.carts.delete(cart_id)
        for user_id in reversed(self._user_ids):
            try:
                self._admin_api.users.delete(user_id)
            except ApiResponseError as error:
                if error.status != 409:
                    raise
                allure.attach(
                    f"User {user_id} retained because upstream preserves order history",
                    name="Cleanup note",
                    attachment_type=allure.attachment_type.TEXT,
                )
