# Day 1 Session — Agentic AI with Ollama

Hands-on examples for **Day 1** of the Agentic AI course: local LLMs via [Ollama](https://ollama.com), simple prompting, RAG-style context, tool calling, and multi-agent travel assistants.

## What you’ll learn (in plain English)

- **How to ask an LLM to behave a certain way**: give it “role + rules” (a system prompt) and see how that changes the response.
- **How to ground answers in your own text**: include a document (`CBUS2025.txt`) so replies stick to provided info instead of guessing.
- **How to let the model fetch real data**: define a small Python function (weather lookup) and let the model call it when needed.
- **How multi-agent workflows can work**: split a task (hotel vs flight vs summary) and combine results into one answer.

## Prerequisites

1. **Ollama** installed and running (`ollama serve` or the Ollama desktop app).
2. Pull the model used by these scripts:

   ```bash
   ollama pull llama3.2:1b
   ```

3. **Python 3.10+** recommended.

## Setup

From this folder (`Day1_Session`):

```bash
pip install ollama
```

For the travel agent scripts (`travelAgent_*.py`), also install the OpenAI Agents SDK and client:

```bash
pip install openai openai-agents
```

Ollama exposes an OpenAI-compatible API at `http://localhost:11434/v1`, which those agents use as the model backend.

## Project layout

| File | Description |
|------|-------------|
| `Ollama.py` | Basic chat with a system prompt (travel assistant). |
| `OllamaRag.py` | Same assistant, but the system prompt includes the full `CBUS2025.txt` guide. |
| `OllamaTool.py` | Tool calling: model invokes `get_current_weather` (wttr.in) and answers in plain English. |
| `travelAgent_Chaining_Ollama.py` | Multi-agent **handoff chain**: hotel → flight → main travel agent. |
| `travelAgent_Orchestrator_IBM_Granite.py` | **Orchestrator** pattern: one travel agent calls flight/hotel sub-agents as tools. |
| `CBUS2025.txt` | Columbus travel guide used as RAG context in `OllamaRag.py`. |

## Usage

Run each script from `Day1_Session` (so relative paths like `CBUS2025.txt` resolve correctly).

### 1. Basic chat — `Ollama.py`

Single-turn travel Q&A with a custom system prompt.

```bash
python Ollama.py
```

Edit the `messages` list in the file to change the user question or system prompt.

### 2. Context in the prompt (RAG-style) — `OllamaRag.py`

Loads `CBUS2025.txt` into the system prompt so answers are grounded in that document.

```bash
python OllamaRag.py
```

Requires `CBUS2025.txt` in the same directory.

### 3. Tool calling — `OllamaTool.py`

Demonstrates Ollama **function tools**:

1. User asks for weather (default: Columbus, next Tuesday).
2. Model may call `get_current_weather(city)` (live data from [wttr.in](https://wttr.in)).
3. Tool result is sent back; model produces a final answer (day of week, high/low, plain English).

```bash
python OllamaTool.py
```

Customize `messages` (user content), `system_prompt`, or `model` in the file. Needs network access for wttr.in.

### 4. Agent handoffs (chaining) — `travelAgent_Chaining_Ollama.py`

Uses the OpenAI Agents SDK with Ollama as the LLM:

- **hotelAgent** → hands off to **flightAgent** → hands off to **travelAgent**
- Default query: trip to Columbus with flights and a downtown hotel

```bash
python travelAgent_Chaining_Ollama.py
```

Ensure Ollama is running on port `11434` before starting.

### 5. Orchestrator with tools — `travelAgent_Orchestrator_IBM_Granite.py`

One **Travel Agent** orchestrator calls:

- `get_flight_details` (flight sub-agent as tool)
- `get_hotel_details` (hotel sub-agent as tool)

Then summarizes the plan in natural language.

```bash
python travelAgent_Orchestrator_IBM_Granite.py
```

Edit the `query` string in `main()` to try different trip requests.

## Configuration

| Setting | Where | Default |
|---------|--------|---------|
| Model | All scripts | `llama3.2:1b` |
| Ollama API URL | Travel agents | `http://localhost:11434/v1` |
| Temperature | Per script | `0.1`–`0.4` (see each file) |

Change the model after pulling it locally, e.g. `ollama pull llama3.2` and update `model="llama3.2"` in code.

## Troubleshooting

- **Connection refused to localhost:11434** — Start Ollama and confirm `ollama list` shows your model.
- **Model not found** — Run `ollama pull llama3.2:1b` (or the model name in the script).
- **`CBUS2025.txt` not found** — Run `OllamaRag.py` from `Day1_Session`, not a parent folder.
- **Weather tool fails** — Check internet access; wttr.in must be reachable from your machine.
- **Travel agent import errors** — Install `openai` and `openai-agents`; use Python 3.10+.

## Related

- [Ollama Python library](https://github.com/ollama/ollama-python)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
