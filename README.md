# Circuit Breaker Labs GitHub Actions

[![zizmor](https://img.shields.io/badge/Check-_?label=%F0%9F%8C%88%20zizmor)](https://github.com/circuitbreakerlabs/actions/actions/workflows/lint.yml)
[![Ruff](https://img.shields.io/badge/Ruff-Check-34223D?logo=ruff)](https://github.com/circuitbreakerlabs/actions/actions/workflows/lint.yml)
[![MyPy](https://img.shields.io/badge/Mypy-Check-blue?logo=python)](https://github.com/circuitbreakerlabs/actions/actions/workflows/type-checking.yml)

GitHub actions utilizing the Circuit Breaker Labs API through its
[Python client](https://github.com/circuitbreakerlabs/circuitbreakerlabs-python).

## Usage

Each action in this repository maps directly to one of the four primary
evaluation endpoints exposed by
[the API](https://api.circuitbreakerlabs.ai/v1/docs):

- [`singleturn-evaluate-system-prompt`](https://github.com/circuitbreakerlabs/actions/blob/main/singleturn-evaluate-system-prompt/action.yml)
  &rarr; [`/singleturn_evaluate_system_prompt`](https://api.circuitbreakerlabs.ai/v1/docs#tag/Evaluations/operation/singleturn_evaluate_system_prompt_post)
- [`singleturn-evaluate-openai-finetune`](https://github.com/circuitbreakerlabs/actions/blob/main/singleturn-evaluate-openai-finetune/action.yml)
  &rarr; [`/singleturn_evaluate_openai_finetune`](https://api.circuitbreakerlabs.ai/v1/docs#tag/Evaluations/operation/singleturn_evaluate_openai_finetune_post)
- [`multiturn-evaluate-system-prompt`](https://github.com/circuitbreakerlabs/actions/blob/main/multiturn-evaluate-system-prompt/action.yml)
  &rarr; [`/multiturn_evaluate_system_prompt`](https://api.circuitbreakerlabs.ai/v1/docs#tag/Evaluations/operation/multiturn_evaluate_system_prompt_post)
- [`multiturn-evaluate-openai-finetune`](https://github.com/circuitbreakerlabs/actions/blob/main/multiturn-evaluate-openai-finetune/action.yml)
  &rarr; [`/multiturn_evaluate_openai_finetune`](https://api.circuitbreakerlabs.ai/v1/docs#tag/Evaluations/operation/multiturn_evaluate_openai_finetune_post)

The inputs to each action serve as arguments for the relevant API request.
Action inputs and their descriptions are available in the corresponding
`action.yml` files.

### System Prompt Evaluation Examples

Here, we're using the
[`singleturn-evaluate-system-prompt`](https://github.com/circuitbreakerlabs/actions/blob/main/singleturn-evaluate-system-prompt/action.yml)
action, which calls the
[`/singleturn_evaluate_system_prompt`](https://api.circuitbreakerlabs.ai/v1/docs#tag/Evaluations/operation/singleturn_evaluate_system_prompt_post)
endpoint.

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
        uses: circuitbreakerlabs/actions/singleturn-evaluate-system-prompt@v1
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
  'https://api.circuitbreakerlabs.ai/v1/singleturn_evaluate_system_prompt' \
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
        uses: circuitbreakerlabs/actions/singleturn-evaluate-system-prompt@main
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
