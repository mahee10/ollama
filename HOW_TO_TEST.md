# How to test

Two ways to run and verify this project locally:

| Category | What you test | How |
|----------|----------------|-----|
| **1. Python scripts + Ollama** | Lesson scripts that call Ollama directly | `python <script>.py` |
| **2. HTTP API** | FastAPI server (`api.py`) on port 8000 | curl, PowerShell, or browser `/docs` |

Both need **Ollama** running on `http://localhost:11434` with **`llama3.2:1b`** pulled.

---

## Shared setup

Run all commands from the project root (e.g. `d:\Projects\Learn\Agents\ollama`).

### Install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Git Bash:** `source .venv/Scripts/activate`  
**Without activating:** `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`

### Confirm Ollama is running

```powershell
ollama list
```

Expected: `llama3.2:1b` (or pull it):

```powershell
ollama pull llama3.2:1b
```

```powershell
curl.exe http://localhost:11434/api/tags
```

Quick smoke test:

```powershell
ollama run llama3.2:1b "Say hello in one sentence."
```

| Check | Command |
|-------|---------|
| Ollama installed | `ollama --version` |
| Server running | `ollama list` |
| Model available | `ollama pull llama3.2:1b` |
| Python deps | `pip install -r requirements.txt` |

---

## 1. Local testing — Python scripts + Ollama models

These scripts use the **Ollama Python library** and talk to Ollama on port **11434**. No HTTP API server required.

### 1.1 Basic chat — `Ollama.py`

Travel assistant with a system prompt.

```powershell
python Ollama.py
```

**Expected:** Printed travel answer in the terminal.  
**Customize:** Edit `messages` in the file.

### 1.2 RAG-style context — `OllamaRag.py`

Loads `CBUS2025.txt` into the system prompt.

```powershell
python OllamaRag.py
```

**Expected:** Answer about Columbus grounded in the guide.  
**Requires:** `CBUS2025.txt` in the same folder.

### 1.3 Tool calling (weather) — `OllamaTool.py`

Model may call `get_current_weather` via wttr.in.

```powershell
python OllamaTool.py
```

**Expected:** Weather-related reply in plain English.  
**Requires:** Internet access for [wttr.in](https://wttr.in).

### 1.4 Multi-agent chaining — `travelAgent_Chaining_Ollama.py`

Handoff chain: hotel → flight → travel agent (OpenAI Agents SDK + Ollama).

```powershell
python travelAgent_Chaining_Ollama.py
```

**Expected:** Multi-step travel plan printed to the console.  
**Requires:** `openai`, `openai-agents` (in `requirements.txt`).

### 1.5 Orchestrator — `travelAgent_Orchestrator_IBM_Granite.py`

One travel agent calls flight/hotel sub-agents as tools.

```powershell
python travelAgent_Orchestrator_IBM_Granite.py
```

**Expected:** Summarized trip plan in natural language.

### Category 1 checklist

- [ ] `ollama list` shows `llama3.2:1b`
- [ ] `python Ollama.py` prints a response
- [ ] `python OllamaRag.py` prints a response (uses `CBUS2025.txt`)
- [ ] `python OllamaTool.py` prints a response (needs network)
- [ ] `python travelAgent_Chaining_Ollama.py` completes (optional)
- [ ] `python travelAgent_Orchestrator_IBM_Granite.py` completes (optional)

### Category 1 troubleshooting

| Problem | What to do |
|---------|------------|
| Connection refused `:11434` | Start Ollama desktop app or `ollama serve` |
| Model not found | `ollama pull llama3.2:1b` |
| `CBUS2025.txt` not found | Run scripts from the project root |
| Weather / tool script fails | Check internet; wttr.in must be reachable |
| Travel agent import errors | `pip install openai openai-agents`; Python 3.10+ |
| Slow first run | Model loading into memory — normal |

---

## 2. Local testing — HTTP API (`api.py`)

The API wraps the same three lesson patterns as HTTP endpoints on **http://localhost:8000**.

| Script | API endpoint |
|--------|----------------|
| `Ollama.py` | `POST /chat` |
| `OllamaRag.py` | `POST /rag` |
| `OllamaTool.py` | `POST /weather` |

### 2.1 Start the server

```powershell
uvicorn api:app --reload --port 8000
```

Or without activating venv:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload --port 8000
```

Leave the terminal open. Expected log: `Uvicorn running on http://127.0.0.1:8000`.

### 2.2 Browser

| URL | Expected |
|-----|----------|
| http://localhost:8000/ | JSON listing endpoints |
| http://localhost:8000/docs | Swagger UI — try POST requests in the browser |

> `/chat`, `/rag`, and `/weather` are **POST only**. Opening them in the browser (GET) returns `Not Found`.

### 2.3 curl (Windows PowerShell)

Use **`curl.exe`** so PowerShell does not alias `curl` to `Invoke-WebRequest`.

**Root:**
```powershell
curl.exe http://localhost:8000/
```

**Chat:**
```powershell
curl.exe -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"Hello! Give me a 1-sentence travel tip for Columbus, OH.\"}"
```

**RAG:**
```powershell
curl.exe -X POST http://localhost:8000/rag ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"What is unique in Columbus, Ohio that I should do next week?\"}"
```

**Weather:**
```powershell
curl.exe -X POST http://localhost:8000/weather ^
  -H "Content-Type: application/json" ^
  -d "{\"city\":\"Columbus\"}"
```

**Expected shapes:**
```json
{"content":"..."}
```
```json
{"content":"...","weather":{"temperature":"...","condition":"..."}}
```

Responses may take **10–30+ seconds** while the model runs.

### 2.4 curl (Git Bash / WSL)

```bash
curl http://localhost:8000/

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello! Give me a 1-sentence travel tip for Columbus, OH."}'

curl -X POST http://localhost:8000/rag \
  -H "Content-Type: application/json" \
  -d '{"message":"What is unique in Columbus, Ohio that I should do next week?"}'

curl -X POST http://localhost:8000/weather \
  -H "Content-Type: application/json" \
  -d '{"city":"Columbus"}'
```

### 2.5 PowerShell (`Invoke-RestMethod`)

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/chat `
  -ContentType "application/json" `
  -Body '{"message":"Hello! Give me a 1-sentence travel tip for Columbus, OH."}'

Invoke-RestMethod -Method Post -Uri http://localhost:8000/rag `
  -ContentType "application/json" `
  -Body '{"message":"What is unique in Columbus, Ohio that I should do next week?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:8000/weather `
  -ContentType "application/json" `
  -Body '{"city":"Columbus"}'
```

### 2.6 Endpoint reference

| Method | Path | Body |
|--------|------|------|
| GET | `/` | — |
| GET | `/docs` | — |
| POST | `/chat` | `{"message":"..."}` |
| POST | `/rag` | `{"message":"..."}` |
| POST | `/weather` | `{"city":"..."}` |

### Category 2 checklist

- [ ] Ollama running (`ollama list`)
- [ ] uvicorn running on port 8000
- [ ] `http://localhost:8000/` returns endpoint JSON
- [ ] `http://localhost:8000/docs` loads
- [ ] `POST /chat` returns `content`
- [ ] `POST /rag` returns `content`
- [ ] `POST /weather` returns `content` and `weather`

### Category 2 troubleshooting

| Problem | What to do |
|---------|------------|
| `{"detail":"Not Found"}` on `/chat` in browser | Use POST (curl, Swagger, or `Invoke-RestMethod`) |
| Connection refused `:8000` | Start uvicorn |
| Connection refused `:11434` | Start Ollama (API still needs Ollama behind it) |
| `/weather` error or empty `weather` | Check internet; wttr.in must be reachable |
| `Activate.ps1` syntax error in Bash | Use `source .venv/Scripts/activate` |
| Slow first request | Model loading — normal |

---

## Next: public URL (optional)

After **category 2** works locally, see [TODO.md](TODO.md) section **#2 Cloudflare Tunnel** to expose the API on the internet.
