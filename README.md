# House Price Predictor

Predicts a home's sale price from 14 of its characteristics and compares six
regression models side by side.

Dataset: **Ames Housing** — Kaggle's "House Prices: Advanced Regression
Techniques", fetched through scikit-learn's OpenML mirror and cut from 81
columns to 14 interpretable ones by [scripts/build_dataset.py](scripts/build_dataset.py).
1,460 rows, mixed numeric and categorical, with 81 genuine missing values so
the pipeline's imputer does real work.

**React frontend + FastAPI backend**, deployed separately: frontend on Vercel,
backend on Render.

## The UI

| Tab | Contents |
|---|---|
| **Predict** | Form generated from the training schema; every model scores the same house. Results ranked green (most accurate model) → red (least). |
| **Model comparison** | MAE, MSE, RMSE and R² as bar charts, coloured green (best) → red (worst) and labelled with the gap to the winner, plus a metrics table tinted by ranking. |
| **Feature importance** | Permutation importance per model — the only method every model supports, so scores stay comparable. |
| **Diagnostics** | Actual vs predicted scatter and a residual histogram for any model, in that model's rank colour. |
| **EDA** | The ydata-profiling report for the dataset, embedded — distributions, missing values, correlations, interactions. |

Colour is never the only cue: charts are sorted best-to-worst, every bar carries
a value label, and the table repeats the numbers in full.

## Models

Linear Regression · Random Forest · Gradient Boosting · Support Vector
Regression (RBF) · Voting Ensemble · Stacking Ensemble (Ridge meta-learner) —
each wrapped in the same preprocessing
pipeline (median impute + scaling for numeric, mode impute + one-hot for
categorical) and evaluated on an identical 20% hold-out split.

## Layout

| Path | Role |
|---|---|
| [config.py](config.py) | Paths, model zoo, metric definitions, form labels, rank ramp |
| [scripts/build_dataset.py](scripts/build_dataset.py) | Rebuilds `ames_housing.csv` from OpenML |
| [scripts/build_profile.py](scripts/build_profile.py) | Rebuilds `frontend/public/eda.html` (needs its own env, see the file) |
| [train.py](train.py) | Trains all models → `artifacts/` |
| [main.py](main.py) | FastAPI backend |
| [frontend/](frontend/) | React + Vite + Recharts UI |
| [notebook.ipynb](notebook.ipynb) | Earlier exploration on the original BSP student dataset |

## API

| Endpoint | Returns |
|---|---|
| `GET /api/health` | liveness probe |
| `GET /api/config` | features, model ranking, metrics, rank colours |
| `POST /api/predict` | every model's prediction for one house |
| `GET /api/diagnostics/{model}` | hold-out scatter points + binned residuals |
| `GET /api/importance/{model}` | permutation importance per feature |

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

The SPA rewrite in `vercel.json` uses `/((?!api/).*)` rather than `/(.*)` on
purpose: a catch-all also swallows `/api/*` and serves `index.html`, so a missing
`VITE_API_URL` surfaces as `Unexpected token '<'` instead of anything useful.

## Why `artifacts/` is committed

The API loads pre-trained pipelines at startup. Training instead takes ~15 s
locally and a minute or more on shared CPU, which delays the port bind past the
platform health check — the container gets killed with a clean log and no
traceback. `train.py` saves with `compress=3`, taking the pipelines from ~68 MB
to ~14 MB while still loading in under a second.
