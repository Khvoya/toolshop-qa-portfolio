from toolshop.models import Address, OrderCreate


class CheckoutDataFactory:
    @staticmethod
    def cash_on_delivery(cart_id: str, address: Address) -> OrderCreate:
        return OrderCreate(
            billing_street=address.street,
            billing_city=address.city,
            billing_state=address.state,
            billing_country=address.country,
            billing_postal_code=address.postal_code,
            cart_id=cart_id,
        )
