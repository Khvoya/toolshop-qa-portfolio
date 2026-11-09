from toolshop.models.common import ApiModel, Page


class Brand(ApiModel):
    id: str
    name: str


class Category(ApiModel):
    id: str
    name: str
    slug: str | None = None


class ProductImage(ApiModel):
    id: str
    file_name: str | None = None
    title: str | None = None


class EmbeddedProduct(ApiModel):
    id: str
    name: str
    description: str
    price: float
    is_location_offer: bool
    is_rental: bool
    in_stock: bool
    co2_rating: str | None = None
    is_eco_friendly: bool
    brand: Brand | None = None
    category: Category | None = None
    product_image: ProductImage | None = None


class Product(EmbeddedProduct):
    brand: Brand
    category: Category


class ProductPage(Page[Product]):
    pass
