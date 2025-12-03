from collections.abc import Iterable

from circuit_breaker_labs.models.failed_test_result import FailedTestResult

BASE_URL = "https://api.circuitbreakerlabs.ai/v1/"


def print_failed_cases(failed_cases: Iterable[Iterable[FailedTestResult]]) -> None:
    for layer, cases in enumerate(failed_cases):
        for case in cases:
            print("---- Failed Case ----")
            print(f"    Layer: {layer}")
            print(f"    Safety Score: {case.safe_response_score}")
            print(f"    User Input: {case.user_input}")
            print(f"    Model Response: {case.model_response}")
            print()
