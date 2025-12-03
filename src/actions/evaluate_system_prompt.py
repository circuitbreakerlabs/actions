import sys
from argparse import ArgumentParser
from dataclasses import dataclass

from circuit_breaker_labs.api.evaluations import evaluate_system_prompt_post
from circuit_breaker_labs.client import Client
from circuit_breaker_labs.models import EvaluateSystemPromptRequest, RunTestsResponse

from .common import BASE_URL, print_failed_cases


@dataclass
class CommandLineArguments:
    fail_action_threshold: float
    fail_case_threshold: float
    variations: int
    maximum_iteration_layers: int
    system_prompt: str
    openrouter_model_name: str
    circuit_breaker_labs_api_key: str


def get_cli_args() -> CommandLineArguments:
    parser = ArgumentParser(
        description="Evaluate a system prompt using Circuit Breaker Labs API",
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
        "--variations",
        type=int,
        required=True,
        help="Number of variations",
    )
    parser.add_argument(
        "--maximum-iteration-layers",
        type=int,
        required=True,
        help="Maximum iteration layers",
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

    args = parser.parse_args()
    return CommandLineArguments(
        fail_action_threshold=args.fail_action_threshold,
        fail_case_threshold=args.fail_case_threshold,
        variations=args.variations,
        maximum_iteration_layers=args.maximum_iteration_layers,
        system_prompt=args.system_prompt,
        openrouter_model_name=args.openrouter_model_name,
        circuit_breaker_labs_api_key=args.circuit_breaker_labs_api_key,
    )


def main() -> None:
    args = get_cli_args()

    request = EvaluateSystemPromptRequest(
        args.fail_case_threshold,
        args.variations,
        args.maximum_iteration_layers,
        args.system_prompt,
        args.openrouter_model_name,
    )

    client = Client(BASE_URL)

    response = evaluate_system_prompt_post.sync_detailed(
        client=client,
        body=request,
        cbl_api_key=args.circuit_breaker_labs_api_key,
    )

    if not isinstance((run_tests_response := response.parsed), RunTestsResponse):
        print(f"Error: {response.status_code}")
        print(response.content.decode())
        sys.exit(1)

    failure_rate = run_tests_response.total_failed / (
        run_tests_response.total_passed + run_tests_response.total_failed
    )

    if failure_rate > args.fail_action_threshold:
        print_failed_cases(run_tests_response.failed_results)
        sys.exit(1)

    print("All tests passed within the acceptable failure threshold.")


if __name__ == "__main__":
    main()
