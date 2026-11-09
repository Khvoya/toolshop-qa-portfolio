import json
from collections.abc import Collection, Mapping
from typing import TypeVar, cast

import allure
from playwright.sync_api import APIRequestContext, APIResponse
from playwright.sync_api import Error as PlaywrightError
from pydantic import BaseModel

from toolshop.api.retry import retry_call
from toolshop.config import Settings

type JSONValue = bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"] | None
ModelT = TypeVar("ModelT", bound=BaseModel)
SENSITIVE_FIELDS = {"password", "access_token", "authorization", "token", "secret"}


class ApiResponseError(RuntimeError):
    def __init__(self, method: str, path: str, status: int, body: JSONValue) -> None:
        self.status = status
        self.body = body
        super().__init__(f"{method} {path} returned {status}: {body}")


def redact(value: object) -> JSONValue:
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]" if str(key).lower() in SENSITIVE_FIELDS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if value is None or isinstance(value, bool | int | float | str):
        return value
    return str(value)


class ApiClient:
    def __init__(self, request: APIRequestContext, settings: Settings) -> None:
        self._request = request
        self._settings = settings
        self._token: str | None = None

    def authenticate(self, token: str) -> None:
        self._token = token

    def request(
        self,
        method: str,
        path: str,
        *,
        expected_status: int | Collection[int] = 200,
        params: Mapping[str, str | int | float | bool] | None = None,
        payload: Mapping[str, object] | None = None,
        retry: bool | None = None,
    ) -> JSONValue:
        method = method.upper()
        should_retry = method in {"GET", "HEAD", "OPTIONS"} if retry is None else retry
        allure.attach(
            json.dumps(redact(dict(payload or {})), indent=2, default=str),
            name=f"{method} {path} request",
            attachment_type=allure.attachment_type.JSON,
        )

        def send() -> APIResponse:
            headers = {"Accept": "application/json"}
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"
            return self._request.fetch(
                path,
                method=method,
                params=dict(params) if params is not None else None,
                data=payload,
                headers=headers,
                timeout=self._settings.api_timeout_ms,
            )

        if should_retry:
            response = retry_call(
                send,
                retry_result=lambda item: item.status == 429 or 500 <= item.status < 600,
                retry_exception=lambda error: isinstance(error, PlaywrightError),
                max_attempts=self._settings.api_max_attempts,
                initial_delay_seconds=self._settings.api_retry_initial_delay_seconds,
                max_delay_seconds=self._settings.api_retry_max_delay_seconds,
            )
        else:
            response = send()

        body = self._response_body(response)
        allure.attach(
            json.dumps(redact(body), indent=2, default=str),
            name=f"{method} {path} response ({response.status})",
            attachment_type=allure.attachment_type.JSON,
        )
        expected = {expected_status} if isinstance(expected_status, int) else set(expected_status)
        if response.status not in expected:
            raise ApiResponseError(method, path, response.status, body)
        return body

    def request_model(
        self,
        method: str,
        path: str,
        *,
        model: type[ModelT],
        expected_status: int | Collection[int] = 200,
        params: Mapping[str, str | int | float | bool] | None = None,
        payload: Mapping[str, object] | None = None,
        retry: bool | None = None,
    ) -> ModelT:
        data = self.request(
            method,
            path,
            expected_status=expected_status,
            params=params,
            payload=payload,
            retry=retry,
        )
        return model.model_validate(data)

    def request_list(
        self,
        method: str,
        path: str,
        *,
        model: type[ModelT],
        expected_status: int | Collection[int] = 200,
        params: Mapping[str, str | int | float | bool] | None = None,
    ) -> list[ModelT]:
        data = self.request(method, path, expected_status=expected_status, params=params)
        if not isinstance(data, list):
            raise TypeError(f"Expected a list from {method} {path}")
        return [model.model_validate(item) for item in data]

    @staticmethod
    def _response_body(response: APIResponse) -> JSONValue:
        text = response.text()
        if not text:
            return None
        try:
            return cast(JSONValue, json.loads(text))
        except json.JSONDecodeError:
            return text
