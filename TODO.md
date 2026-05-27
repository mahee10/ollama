# TODO — Local API + Cloudflare Tunnel (step-by-step)

### Plain-English overview

You’re going to do two things:

1. **Run a small “chat server” on your computer** that your browser (or a React app) can call.
2. **Give it a public URL** (Cloudflare Tunnel) so you can test from anywhere (Vercel, phone, another network).

This file sets up a **basic HTTP API** for your Ollama scripts, then exposes it publicly via **Cloudflare Tunnel** for testing (e.g., from a React UI on Vercel).

---

## #1 Local API (do this first)

### Goal
- Run local endpoints for the three main lessons in this repo:
  - **Basic chat**: `POST http://localhost:8000/chat`
  - **RAG-style doc grounding**: `POST http://localhost:8000/rag`
  - **Tool calling (weather)**: `POST http://localhost:8000/weather`
- Each endpoint calls your local Ollama (`http://localhost:11434`) and returns JSON

### Steps
1. **Create a virtual environment** (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install API dependencies**:

   ```powershell
   pip install fastapi uvicorn ollama
   ```

3. **Create `api.py`** with three endpoints:
   - **`POST /chat`**: accepts `{ "message": "..." }` → returns `{ "content": "..." }`
   - **`POST /rag`**: accepts `{ "message": "..." }` and prepends `CBUS2025.txt` to the prompt
   - **`POST /weather`**: accepts `{ "city": "..." }` and uses the *tool calling pattern* from `OllamaTool.py`

   Notes:
   - Keep the model consistent with your scripts (`llama3.2:1b`).
   - Run from `Day1_Session` so `CBUS2025.txt` can be read by relative path.

4. **Run the server**:

   ```powershell
   uvicorn api:app --reload --port 8000
   ```

5. **Test locally (basic chat)**:

   ```powershell
   Invoke-RestMethod -Method Post -Uri http://localhost:8000/chat `
     -ContentType "application/json" `
     -Body '{"message":"Hello! Give me a 1-sentence travel tip for Columbus, OH."}'
   ```

6. **Test locally (RAG)**:

   ```powershell
   Invoke-RestMethod -Method Post -Uri http://localhost:8000/rag `
     -ContentType "application/json" `
     -Body '{"message":"What is unique in Columbus, Ohio that I should do next week?"}'
   ```

7. **Test locally (tool calling weather)**:

   ```powershell
   Invoke-RestMethod -Method Post -Uri http://localhost:8000/weather `
     -ContentType "application/json" `
     -Body '{"city":"Columbus"}'
   ```

### Local verification checklist
- [ ] Ollama is running (`ollama list` works)
- [ ] `http://localhost:8000/docs` loads (FastAPI Swagger)
- [ ] `POST /chat` returns JSON with a `content` field
- [ ] `POST /rag` returns JSON with a `content` field
- [ ] `POST /weather` returns JSON (temperature/condition or formatted answer)

---

## #2 Cloudflare Tunnel (after local API works)

### Goal
Expose your local API to the internet securely, e.g.:
- Local: `http://localhost:8000`
- Public: `https://<your-subdomain>.trycloudflare.com` (quick test) OR your own domain (recommended)

### Steps (quick test URL: trycloudflare.com)
1. **Download `cloudflared`** and ensure it’s on your PATH.

2. **Start a temporary tunnel** to your local API:

   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```

3. **Copy the HTTPS URL** Cloudflare prints (it will look like `https://something.trycloudflare.com`).

4. **Test via the public URL**:

   ```powershell
   Invoke-RestMethod -Method Post -Uri https://YOUR_URL.trycloudflare.com/chat `
     -ContentType "application/json" `
     -Body '{"message":"What is unique in Columbus, Ohio?"}'
   ```

### Steps (recommended: your own domain, stable URL)
1. **Login**:

   ```powershell
   cloudflared tunnel login
   ```

2. **Create a named tunnel**:

   ```powershell
   cloudflared tunnel create ollama-api
   ```

3. **Create `config.yml`** (in a safe folder) mapping a hostname to your service:
   - `service: http://localhost:8000`
   - `hostname: api.yourdomain.com`

4. **Create the DNS record**:

   ```powershell
   cloudflared tunnel route dns ollama-api api.yourdomain.com
   ```

5. **Run the tunnel**:

   ```powershell
   cloudflared tunnel run ollama-api
   ```

### Tunnel verification checklist
- [ ] Public `/docs` loads (or at least `/chat` works)
- [ ] You can call the public `/chat` from another device/network
- [ ] You’ve added basic protection before sharing broadly (auth/token)

---

## Notes for React/Vercel
- Your React app should call **the tunnel URL**, not `localhost`.
- For Vercel, store the API base URL as an env var (example): `VITE_API_BASE_URL` or `NEXT_PUBLIC_API_BASE_URL`.

