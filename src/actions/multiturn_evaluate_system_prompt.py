import sys
from argparse import ArgumentParser
from dataclasses import dataclass

from circuit_breaker_labs.api.evaluations import multi_turn_evaluate_system_prompt_post
from circuit_breaker_labs.client import Client
from circuit_breaker_labs.models.multi_turn_evaluate_system_prompt_request import (
    MultiTurnEvaluateSystemPromptRequest,
)
from circuit_breaker_labs.models.multi_turn_run_tests_response import MultiTurnRunTestsResponse
from circuit_breaker_labs.models.multi_turn_test_type import MultiTurnTestType
from circuit_breaker_labs.models.test_case_pack import TestCasePack
from circuit_breaker_labs.types import UNSET

from .common import (
    BASE_URL,
    compute_failure_rate,
    parse_multi_turn_test_type,
    parse_test_case_pack,
    print_multi_turn_failed_cases,
)


@dataclass
class CommandLineArguments:
    fail_action_threshold: float
    fail_case_threshold: float
    max_turns: int
    system_prompt: str
    openrouter_model_name: str
    circuit_breaker_labs_api_key: str
    test_types: list[MultiTurnTestType]
    test_case_packs: list[TestCasePack] | None


def get_cli_args() -> CommandLineArguments:
    parser = ArgumentParser(
        description="Evaluate a system prompt using Circuit Breaker Labs multi-turn API",
    )

    parser.add_argument(
        "--fail-action-threshold",
        type=float,
        required=True,
        help="Test failure rate above this threshold will cause the action to fail",
    )
    parser.add_argument(
        "--fail-case-threshold",
        type=float,
        required=True,
        help="Threshold value for a case to be considered a fail",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        required=True,
        help="Maximum number of turns in the conversation (must be even).",
    )
    parser.add_argument(
        "--test-types",
        type=parse_multi_turn_test_type,
        nargs="+",
        required=True,
        help="Space-separated list of multi-turn test types to execute.",
    )
    parser.add_argument(
        "--system-prompt",
        type=str,
        required=True,
        help="System prompt to evaluate",
    )
    parser.add_argument(
        "--openrouter-model-name",
        type=str,
        required=True,
        help="Openrouter model name",
    )
    parser.add_argument(
        "--circuit-breaker-labs-api-key",
        type=str,
        required=True,
        help="Circuit Breaker Labs API key",
    )
    parser.add_argument(
        "--test-case-packs",
        type=parse_test_case_pack,
        nargs="+",
        help="Optional test case packs to run (space-separated).",
    )

    args = parser.parse_args()
    if args.max_turns % 2 != 0:
        parser.error("--max-turns must be an even integer.")

    return CommandLineArguments(
        fail_action_threshold=args.fail_action_threshold,
        fail_case_threshold=args.fail_case_threshold,
        max_turns=args.max_turns,
        system_prompt=args.system_prompt,
        openrouter_model_name=args.openrouter_model_name,
        circuit_breaker_labs_api_key=args.circuit_breaker_labs_api_key,
        test_types=args.test_types,
        test_case_packs=args.test_case_packs,
    )


def main() -> None:
    args = get_cli_args()

    request = MultiTurnEvaluateSystemPromptRequest(
        threshold=args.fail_case_threshold,
        max_turns=args.max_turns,
        test_types=args.test_types,
        system_prompt=args.system_prompt,
        openrouter_model_name=args.openrouter_model_name,
        test_case_packs=args.test_case_packs if args.test_case_packs is not None else UNSET,
    )

    client = Client(BASE_URL)

    response = multi_turn_evaluate_system_prompt_post.sync_detailed(
        client=client,
        body=request,
        cbl_api_key=args.circuit_breaker_labs_api_key,
    )

    if not isinstance(
        (run_tests_response := response.parsed),
        MultiTurnRunTestsResponse,
    ):
        print(f"Error: {response.status_code}")
        print(response.content.decode())
        sys.exit(1)

    failure_rate = compute_failure_rate(
        total_passed=run_tests_response.total_passed,
        total_failed=run_tests_response.total_failed,
    )

    if failure_rate > args.fail_action_threshold:
        print_multi_turn_failed_cases(
            failure_rate=failure_rate,
            failed_cases=run_tests_response.failed_results,
        )
        sys.exit(1)

    print("All tests passed within the acceptable failure threshold.")


if __name__ == "__main__":
    main()
