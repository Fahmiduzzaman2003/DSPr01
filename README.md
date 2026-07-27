# HSC Result Predictor

Predicts a student's HSC result from background data (family, schooling, habits,
SSC result) and compares five regression models side by side.

**React frontend + FastAPI backend**, deployed separately: frontend on Vercel,
backend on Render.

## The UI

| Tab | Contents |
|---|---|
| **Predict** | Form generated from the training schema; every model scores the same student. Results ranked green (most accurate model) → red (least). |
| **Model comparison** | MAE, MSE, RMSE and R² as bar charts, coloured green (best) → red (worst) and labelled with the gap to the winner, plus a metrics table tinted by ranking. |
| **Diagnostics** | Actual vs predicted scatter and a residual histogram for any model, in that model's rank colour. |

Colour is never the only cue: charts are sorted best-to-worst, every bar carries
a value label, and the table repeats the numbers in full.

## Models

Linear Regression · Random Forest · Gradient Boosting · Voting Ensemble ·
Stacking Ensemble (Ridge meta-learner) — each wrapped in the same preprocessing
pipeline (median impute + scaling for numeric, mode impute + one-hot for
categorical) and evaluated on an identical 20% hold-out split.

## Layout

| Path | Role |
|---|---|
| [config.py](config.py) | Paths, model zoo, metric definitions, form labels, rank ramp |
| [train.py](train.py) | Trains all models → `artifacts/` |
| [main.py](main.py) | FastAPI backend |
| [frontend/](frontend/) | React + Vite + Recharts UI |
| [notebook.ipynb](notebook.ipynb) | Original exploration (unchanged) |

## API

| Endpoint | Returns |
|---|---|
| `GET /api/health` | liveness probe |
| `GET /api/config` | features, model ranking, metrics, rank colours |
| `POST /api/predict` | every model's prediction for one student |
| `GET /api/diagnostics/{model}` | hold-out scatter points + binned residuals |

## Run locally

Two terminals.

**Backend** (port 8000):

```bash
pip install -r requirements.txt
python train.py            # once, to build artifacts/
uvicorn main:app --reload --port 8000
```

**Frontend** (port 5173):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api` to port 8000, so no CORS setup
is needed in development.

---

## Deploy the backend to Render

1. Push this repo to GitHub. `artifacts/` **must** be committed — see the note below.
2. **render.com → New → Blueprint**, select the repo. It reads [render.yaml](render.yaml)
   and configures build, start command and health check automatically.
3. Copy the resulting URL, e.g. `https://hsc-result-api.onrender.com`.

Without a blueprint, use **New → Web Service** with:

| Setting | Value |
|---|---|
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Env var | `PYTHON_VERSION` = `3.11.9` |

Free tier sleeps after 15 minutes idle; the first request then takes ~50 s.

## Deploy the frontend to Vercel

1. **vercel.com → Add New → Project**, select the same repo.
2. Set **Root Directory** to `frontend`. Vercel detects Vite from
   [frontend/vercel.json](frontend/vercel.json).
3. Add an environment variable:

   ```
   VITE_API_URL = https://hsc-result-api.onrender.com
   ```

   It is read at build time, so **redeploy after changing it**.
4. Deploy, then set `ALLOWED_ORIGINS` on Render to your Vercel URL to lock down CORS.

## Why `artifacts/` is committed

The API loads pre-trained pipelines at startup. Training instead takes ~15 s
locally and a minute or more on shared CPU, which delays the port bind past the
platform health check — the container gets killed with a clean log and no
traceback. `train.py` saves with `compress=3`, taking the five pipelines from
68 MB to ~14 MB while still loading in under a second.
