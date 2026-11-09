from datetime import date
from uuid import uuid4

from pydantic import SecretStr

from toolshop.models import Address, Credentials, NewUser


class UserFactory:
    @staticmethod
    def build() -> NewUser:
        unique = uuid4().hex[:12]
        return NewUser(
            first_name="Portfolio",
            last_name="Tester",
            address=Address(
                street="Gerritsenstraat",
                house_number="42",
                city="Oosthuizen",
                state="Groningen",
                country="NL",
                postal_code="1234AB",
            ),
            phone="0612345678",
            dob=date(1990, 1, 1),
            email=f"qa-{unique}@example.com",
            password=SecretStr(f"Portfolio!{unique}Aa"),
        )

    @staticmethod
    def credentials(new_user: NewUser) -> Credentials:
        return Credentials(email=new_user.email, password=new_user.password)
