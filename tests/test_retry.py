import unittest

from geoshield_mllm.utils.retry import RetryConfig, retry_call


class RetryTests(unittest.TestCase):
    def test_retry_eventual_success(self) -> None:
        calls = {"n": 0}
        sleeps: list[float] = []

        def fn() -> str:
            calls["n"] += 1
            if calls["n"] < 3:
                raise RuntimeError("temporary")
            return "ok"

        result = retry_call(fn, RetryConfig(max_attempts=3, initial_seconds=1, multiplier=2), sleep=sleeps.append)
        self.assertEqual(result, "ok")
        self.assertEqual(sleeps, [1, 2])

    def test_retry_raises_final_error(self) -> None:
        with self.assertRaises(RuntimeError):
            retry_call(lambda: (_ for _ in ()).throw(RuntimeError("boom")), RetryConfig(max_attempts=2), sleep=lambda _: None)


def test_retry_eventual_success() -> None:
    calls = {"n": 0}
    sleeps: list[float] = []

    def fn() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("temporary")
        return "ok"

    result = retry_call(fn, RetryConfig(max_attempts=3, initial_seconds=1, multiplier=2), sleep=sleeps.append)
    assert result == "ok"
    assert sleeps == [1, 2]


def test_retry_raises_final_error() -> None:
    try:
        retry_call(lambda: (_ for _ in ()).throw(RuntimeError("boom")), RetryConfig(max_attempts=2), sleep=lambda _: None)
    except RuntimeError:
        return
    raise AssertionError("expected RuntimeError")
