from toolshop.models.common import ApiModel
from toolshop.models.product import EmbeddedProduct


class Favorite(ApiModel):
    id: str
    user_id: str
    product_id: str
    product: EmbeddedProduct | None = None
