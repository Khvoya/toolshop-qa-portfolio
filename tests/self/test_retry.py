import allure
import pytest

from toolshop.api.retry import retry_call

pytestmark = pytest.mark.self


@allure.title("Self: retry stops after the first successful result")
def test_retry_recovers_from_transient_result() -> None:
    with allure.step("Arrange: two transient responses followed by success"):
        responses = iter([503, 429, 200])
        delays: list[float] = []
    with allure.step("Act: execute the typed retry helper without real sleeping"):
        result = retry_call(
            lambda: next(responses),
            retry_result=lambda status: status == 429 or status >= 500,
            retry_exception=lambda error: False,
            max_attempts=3,
            initial_delay_seconds=0.2,
            max_delay_seconds=1,
            sleep=delays.append,
            random_value=lambda: 0,
        )
    with allure.step("Assert: success and exponential delays are returned"):
        assert result == 200
        assert delays == [0.1, 0.2]


@allure.title("Self: retry does not repeat a permanent result")
def test_retry_does_not_repeat_permanent_result() -> None:
    calls = 0

    def operation() -> int:
        nonlocal calls
        calls += 1
        return 400

    result = retry_call(
        operation,
        retry_result=lambda status: status >= 500,
        retry_exception=lambda error: False,
        max_attempts=3,
        initial_delay_seconds=0.1,
        max_delay_seconds=1,
        sleep=lambda delay: None,
    )
    assert result == 400
    assert calls == 1


@allure.title("Self: non-retryable exception is propagated unchanged")
def test_retry_propagates_permanent_exception() -> None:
    error = ValueError("invalid response")

    def operation() -> None:
        raise error

    with pytest.raises(ValueError) as raised:
        retry_call(
            operation,
            retry_result=lambda result: False,
            retry_exception=lambda exception: False,
            max_attempts=3,
            initial_delay_seconds=0.1,
            max_delay_seconds=1,
        )
    assert raised.value is error
