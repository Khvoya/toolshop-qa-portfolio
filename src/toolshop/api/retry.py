import random
import time
from collections.abc import Callable


def retry_call[T](
    operation: Callable[[], T],
    *,
    retry_result: Callable[[T], bool],
    retry_exception: Callable[[Exception], bool],
    max_attempts: int,
    initial_delay_seconds: float,
    max_delay_seconds: float,
    sleep: Callable[[float], None] = time.sleep,
    random_value: Callable[[], float] = random.random,
) -> T:
    for attempt in range(1, max_attempts + 1):
        try:
            result = operation()
        except Exception as error:
            if attempt == max_attempts or not retry_exception(error):
                raise
        else:
            if attempt == max_attempts or not retry_result(result):
                return result

        delay = min(initial_delay_seconds * (2 ** (attempt - 1)), max_delay_seconds)
        sleep(delay * (0.5 + random_value()))

    raise AssertionError("Retry loop must return or raise")
