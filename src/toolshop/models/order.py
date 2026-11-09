from pydantic import Field

from toolshop.models.common import ApiModel, Page


class OrderCreate(ApiModel):
    billing_street: str
    billing_city: str
    billing_state: str
    billing_country: str
    billing_postal_code: str
    payment_method: str = "cash-on-delivery"
    payment_details: dict[str, str] = Field(default_factory=dict)
    cart_id: str


class Order(ApiModel):
    id: str
    user_id: str
    invoice_date: str
    invoice_number: str
    billing_street: str
    billing_city: str
    billing_state: str
    billing_country: str
    billing_postal_code: str
    subtotal: float
    total: float
    status: str
    status_message: str | None = None


class OrderPage(Page[Order]):
    pass
