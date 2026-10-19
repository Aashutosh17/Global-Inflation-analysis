from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def test_processed_dataset_has_expected_schema():
    data = pd.read_csv(DATA_DIR / "processed_inflation_data.csv")

    required_columns = {
        "country",
        "country_code",
        "year",
        "inflation_rate",
        "inflation_category",
        "is_anomaly",
    }

    assert required_columns.issubset(data.columns)
    assert len(data) > 0
    assert data["country"].notna().all()
    assert data["year"].between(2000, 2024).all()


def test_dashboard_exposes_health_endpoint():
    from dashboard.run_dashboard import server

    response = server.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
