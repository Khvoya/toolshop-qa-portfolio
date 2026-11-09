import allure
import pytest

from toolshop.api.client import redact

pytestmark = pytest.mark.self


@allure.title("Self: diagnostics redact credentials recursively")
def test_sensitive_data_is_redacted() -> None:
    with allure.step("Act: redact nested request and response data"):
        result = redact(
            {
                "email": "qa@example.com",
                "password": "secret",
                "nested": [{"access_token": "token", "safe": 42}],
            }
        )
    with allure.step("Assert: secrets are hidden while useful diagnostics remain"):
        assert result == {
            "email": "qa@example.com",
            "password": "[REDACTED]",
            "nested": [{"access_token": "[REDACTED]", "safe": 42}],
        }
