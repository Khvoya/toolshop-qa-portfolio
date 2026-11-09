from datetime import date

from pydantic import EmailStr, Field, SecretStr

from toolshop.models.common import ApiModel


class Address(ApiModel):
    street: str
    house_number: str | None = None
    city: str
    state: str
    country: str
    postal_code: str


class Credentials(ApiModel):
    email: EmailStr
    password: SecretStr


class NewUser(ApiModel):
    first_name: str = Field(min_length=1, max_length=40)
    last_name: str = Field(min_length=1, max_length=20)
    address: Address
    phone: str = Field(max_length=24)
    dob: date
    email: EmailStr
    password: SecretStr = Field(min_length=8)


class User(ApiModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    address: Address
    phone: str
    dob: date
    created_at: str | None = None


class Token(ApiModel):
    access_token: str
    token_type: str
    expires_in: int = Field(gt=0)


class TestUser(ApiModel):
    __test__ = False

    account: User
    credentials: Credentials
    token: SecretStr | None = None

    @property
    def id(self) -> str:
        return self.account.id
