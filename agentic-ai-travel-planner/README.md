# Agentic AI Travel Planner – Render deployment

This repository contains two separate Render Web Services:
- Streamlit frontend: `fe/app.py`
- FastAPI backend: `be/main.py`

The backend calls Groq. The frontend calls the backend using `BACKEND_URL`.

## 1. Create a Groq API key

1. Sign in at https://console.groq.com/
2. Open API Keys and create a key.
3. Store it privately. Do not commit it to GitHub.

The backend defaults to `openai/gpt-oss-20b`. You can override this with the `GROQ_MODEL` environment variable if that model is unavailable to your account.

## 2. Test locally

Use Python 3.11 or 3.12.

### Backend (terminal 1)

```bash
cd be
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Set the key:

```powershell
$env:GROQ_API_KEY="gsk_your_key"
```

macOS/Linux:

```bash
export GROQ_API_KEY="gsk_your_key"
```

Run:

```bash
uvicorn main:f_obj --reload
```

Test `http://127.0.0.1:8000/docs` and `http://127.0.0.1:8000/health`.

### Frontend (terminal 2)

```bash
cd fe
python -m venv .venv
# Activate the environment as above
pip install -r requirements.txt
```

Set the local backend URL if needed:

```powershell
$env:BACKEND_URL="http://127.0.0.1:8000"
```

Run:

```bash
streamlit run app.py
```

## 3. Push to GitHub

Create a GitHub repository named `agentic-ai-travel-planner`, then from this project root:

```bash
git init
git add .
git commit -m "Prepare AI Travel Planner for Render"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/agentic-ai-travel-planner.git
git push -u origin main
```

Do not upload `.env`, API keys, personal files or virtual environments.

## 4. Deploy the backend on Render

Create a new **Web Service** and select this GitHub repository.

| Setting | Value |
|---|---|
| Name | `travel-planner-api` |
| Runtime | Python 3 |
| Branch | `main` |
| Root Directory | `be` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:f_obj --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

Add Environment Variables:

| Key | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `GROQ_MODEL` | `openai/gpt-oss-20b` (optional) |

Deploy. Copy the backend URL and test:
- `https://YOUR-BACKEND.onrender.com/health`
- `https://YOUR-BACKEND.onrender.com/docs`

## 5. Deploy the frontend on Render

Create another **Web Service** using the same repository.

| Setting | Value |
|---|---|
| Name | `travel-planner-frontend` |
| Runtime | Python 3 |
| Branch | `main` |
| Root Directory | `fe` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT` |
| Instance Type | Free |

Add Environment Variable:

| Key | Value |
|---|---|
| `BACKEND_URL` | Your actual Travel Planner backend URL, without a trailing slash |

Deploy and open the frontend URL.

## Notes

- Render Free web services spin down after inactivity and may take time to wake.
- Free services have limited CPU/RAM and shared monthly instance-hour allowances. Check current limits: https://render.com/docs/free
- Groq Free API has rate limits: https://console.groq.com/docs/rate-limits
- AI-generated prices and travel details are estimates, not live booking data.
