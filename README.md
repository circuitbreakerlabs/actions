# Circuit Breaker Labs GitHub Actions

[![zizmor](https://img.shields.io/badge/Check-_?label=%F0%9F%8C%88%20zizmor)](https://github.com/circuitbreakerlabs/actions/actions/workflows/lint.yml)
[![Ruff](https://img.shields.io/badge/Ruff-Check-34223D?logo=ruff)](https://github.com/circuitbreakerlabs/actions/actions/workflows/lint.yml)
[![MyPy](https://img.shields.io/badge/Mypy-Check-blue?logo=python)](https://github.com/circuitbreakerlabs/actions/actions/workflows/type-checking.yml)

GitHub actions utilizing the Circuit Breaker Labs API through its
[Python client](https://github.com/circuitbreakerlabs/circuitbreakerlabs-python).

## Usage

Each one of the available actions corresponds to an endpoint in
[the API](https://api.circuitbreakerlabs.ai/v1/docs). For example the
[`evaluate-system-prompt`](https://github.com/circuitbreakerlabs/actions/blob/main/evaluate-system-prompt/action.yml)
action corresponds to the
[`evaluate_system_prompt`](https://api.circuitbreakerlabs.ai/v1/docs#tag/Evaluations/operation/evaluate_system_prompt_post)
endpoint. The inputs to each action serve as arguments for the relevant API
request. Action inputs and their descriptions are available in the relevant
`action.yml` files.

### System Prompt Evaluation Examples

Here, we're using the
[`evaluate-system-prompt`](https://github.com/circuitbreakerlabs/actions/blob/main/evaluate-system-prompt/action.yml)
action, which calls its
[associated endpoint](https://api.circuitbreakerlabs.ai/v1/docs#tag/Evaluations/operation/evaluate_system_prompt_post).

```yml
name: Evaluate System Prompt

on:
  workflow_dispatch:

jobs:
  evaluate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Run system prompt evaluation
        uses: circuitbreakerlabs/actions/evaluate-system-prompt@v1
        with:
          fail-action-threshold: "0.80"
          fail-case-threshold: "0.5"
          variations: "1"
          maximum-iteration-layers: "1"
          system-prompt: "You are a helpful assistant"
          openrouter-model-name: "anthropic/claude-3.7-sonnet"
          circuit-breaker-labs-api-key: ${{ secrets.CBL_API_KEY }}
```

This action effectively translates to the following POST request

```sh
curl -X 'POST' \
  'https://api.circuitbreakerlabs.ai/v1/evaluate_system_prompt' \
  -H 'accept: application/json' \
  -H "cbl-api-key: $CBL_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
  "threshold": 0.5,
  "variations": 1,
  "maximum_iteration_layers": 1,
  "openrouter_model_name": "anthropic/claude-3.7-sonnet",
  "system_prompt": "You are a helpful assistant"
}'
```

<details>
    <summary>More Thorough Example</summary>

Here, we read the system prompt and model name from a `model_config.json` file,
and only run the action if this file changes.

```yml
name: Evaluate System Prompt

on:
  push:
    paths:
      - "model_config.json"
  workflow_dispatch:

jobs:
  evaluate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Read configuration from JSON
        id: read-config
        run: |
          PROMPT=$(jq -r '.system_prompt' model_config.json)
          MODEL=$(jq -r '.model' model_config.json)
          echo "prompt<<EOF" >> $GITHUB_OUTPUT
          echo "$PROMPT" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
          echo "model=$MODEL" >> $GITHUB_OUTPUT

      - name: Run system prompt evaluation
        uses: circuitbreakerlabs/actions/evaluate-system-prompt@main
        with:
          fail-action-threshold: "0.80"
          fail-case-threshold: "0.5"
          variations: "1"
          maximum-iteration-layers: "1"
          system-prompt: ${{ steps.read-prompt.outputs.prompt }}
          openrouter-model-name: ${{ steps.read-config.outputs.model }}
          circuit-breaker-labs-api-key: ${{ secrets.CBL_API_KEY }}
```

</details>
