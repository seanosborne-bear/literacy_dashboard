# San Diego County Literacy Dashboard

An interactive Streamlit dashboard mapping literacy need, program access, and service gaps across every zip code in San Diego County. Built as part of a volunteer data analytics project.

**Live app:** https://literacydashboard-axgurpktkyb6eumzikhcnb.streamlit.app/

## What's in this repo

- `Home.py` — entry point / landing page
- `pages/` — the 8 dashboard components (hotspot map, literacy rates, temporal trends, accessibility & transit, service gap rankings, micro-area score, program directory, about)
- `utils.py` — shared functions that load and clean the data in `data/`
- `data/` — 13 static CSV files the dashboard reads at runtime
- `requirements.txt` — Python dependencies

## Running locally

```
pip install -r requirements.txt
streamlit run Home.py
```

Opens at `http://localhost:8501`.

## Deployment

Deployed on Streamlit Community Cloud, connected to this repo's `main` branch (entry file: `Home.py`). Any push to `main` triggers an automatic redeploy within about a minute.

## More detail

- **User Guide** — how to use the dashboard (navigation, filters, interpreting charts, downloading data)
- **Technical Documentation** — architecture, data pipeline, dependencies, deployment steps, known issues

Both are maintained as separate documents outside this repo; ask the project owner for current links.
