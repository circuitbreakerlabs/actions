# Circuit Breaker Labs GitHub Actions

GitHub actions utilizing the Circuit Breaker Labs API.

## Usage

For the required inputs to each action, check the relevant `action.yml` file.

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
