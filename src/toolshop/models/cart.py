from pydantic import Field

from toolshop.models.common import ApiModel
from toolshop.models.product import EmbeddedProduct


class CartItem(ApiModel):
    id: str
    cart_id: str
    product_id: str
    quantity: int = Field(ge=1)
    product: EmbeddedProduct
    discount_percentage: float | None = None
    discounted_price: float | None = None


class Cart(ApiModel):
    id: str
    cart_items: list[CartItem]
    additional_discount_percentage: float | None = None
