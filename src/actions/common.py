from __future__ import annotations

from argparse import ArgumentTypeError
from collections.abc import Iterable

from circuit_breaker_labs.models.message import Message
from circuit_breaker_labs.models.multi_turn_failed_test_result import (
    MultiTurnFailedTestResult,
)
from circuit_breaker_labs.models.multi_turn_test_type import MultiTurnTestType
from circuit_breaker_labs.models.single_turn_failed_test_result import (
    SingleTurnFailedTestResult,
)
from circuit_breaker_labs.models.test_case_pack import TestCasePack

BASE_URL = "https://api.circuitbreakerlabs.ai/v1/"


def compute_failure_rate(*, total_passed: int, total_failed: int) -> float:
    total_cases = total_passed + total_failed
    if total_cases == 0:
        return 0.0
    return total_failed / total_cases


def print_single_turn_failed_cases(
    *,
    failure_rate: float,
    failed_cases: Iterable[Iterable[SingleTurnFailedTestResult]],
) -> None:
    print(f"Overall Failure Rate: {failure_rate:.2%}\n")
    for layer_index, cases in enumerate(failed_cases):
        for case in cases:
            print("---- Failed Case ----")
            print(f"    Layer: {layer_index}")
            print(f"    Safety Score: {case.safe_response_score}")
            print(f"    User Input: {case.user_input}")
            print(f"    Model Response: {case.model_response}")
            print()


def print_multi_turn_failed_cases(
    *,
    failure_rate: float,
    failed_cases: Iterable[MultiTurnFailedTestResult],
) -> None:
    print(f"Overall Failure Rate: {failure_rate:.2%}\n")
    for case_index, case in enumerate(failed_cases, start=1):
        print("---- Failed Case ----")
        print(f"    Case: {case_index}")
        print(f"    Min Safety Score: {case.min_safe_response_score}")
        print("    Conversation:")
        for turn_index, message in enumerate(case.conversation, start=1):
            _print_message(turn_index=turn_index, message=message)
        print()


def _print_message(*, turn_index: int, message: Message) -> None:
    role = message.role.value
    content = message.content
    print(f"        [{turn_index}] {role}: {content}")


def parse_test_case_pack(value: str) -> TestCasePack:
    try:
        return TestCasePack(value)
    except ValueError as exc:  # pragma: no cover - defensive guard
        valid_options = ", ".join(pack.value for pack in TestCasePack)
        raise ArgumentTypeError(
            f"Invalid test case pack '{value}'. Expected one of: {valid_options}",
        ) from exc


def parse_multi_turn_test_type(value: str) -> MultiTurnTestType:
    try:
        return MultiTurnTestType(value)
    except ValueError as exc:  # pragma: no cover - defensive guard
        valid_options = ", ".join(test_type.value for test_type in MultiTurnTestType)
        raise ArgumentTypeError(
            f"Invalid multi-turn test type '{value}'. Expected one of: {valid_options}",
        ) from exc
