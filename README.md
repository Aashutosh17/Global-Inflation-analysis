# Global Inflation Analysis

Interactive analysis of annual inflation rates for countries around the world.
The project combines a reproducible Pandas preprocessing pipeline with a Dash
and Plotly dashboard.

## Features

- Country-level inflation trends from 2000 to 2024
- Year-range, country, and inflation-category filters
- Moving averages and year-over-year changes
- Inflation distribution and anomaly visualizations
- Production-ready WSGI entry point and health check

## Project layout

```text
dashboard/       Dash application
data/            Source and processed datasets
notebooks/       Exploratory analysis
scripts/         Data preparation
tests/           Automated tests
```

## Local setup

Python 3.12 is recommended.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

The processed dataset is included. To regenerate it:

```bash
python scripts/preprocess.py
```

Start the development server:

```bash
python dashboard/run_dashboard.py
```

Open [http://127.0.0.1:8050](http://127.0.0.1:8050).

## Tests and quality checks

```bash
pytest -q
ruff check .
```

## Production deployment

The application exposes the Dash server as `dashboard.run_dashboard:server`.
Use Gunicorn or the equivalent WSGI process supplied by your hosting provider:

```bash
gunicorn --bind 0.0.0.0:$PORT dashboard.run_dashboard:server
```

The application reads `HOST`, `PORT`, and `DASH_DEBUG` from the environment.
For local configuration, copy `.env.example` to `.env`; do not commit `.env`.

The repository also includes a `Procfile` and `Dockerfile` for platforms that
support either deployment format. The `/health` endpoint returns a simple
`{"status": "ok"}` response for health checks.

## Data and attribution

The project uses World Bank and IMF inflation datasets collected on
2025-11-18. See [data/README.md](data/README.md) for the files, processing
flow, and redistribution reminder. Confirm the source terms before using the
data commercially.

## License

The application code is released under the [MIT License](LICENSE). The
upstream datasets remain subject to their original terms.
