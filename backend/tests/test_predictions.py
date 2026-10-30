from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models.schemas import SensorData
from app.services.ml_service import predict_crop


def sample(**overrides):
    return SensorData(**(dict(N=50, P=40, K=40, temperature=25, humidity=65,
                             ph=6.5, rainfall=100, tds=150) | overrides))


def test_crop_prediction_is_repeatable():
    assert len({predict_crop(sample()) for _ in range(40)}) == 1


@pytest.mark.parametrize('field,value', [('humidity', 101), ('ph', -1), ('N', -2),
                                        ('temperature', float('nan'))])
def test_invalid_crop_inputs(field, value):
    with pytest.raises(ValidationError):
        sample(**{field: value})


def test_prediction_api_discloses_method(client):
    response = client.post('/predict', json=sample().model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data['method'] == 'agronomic_similarity'
    assert len(data['alternatives']) == 3
    assert data['limitations']


def series(values, step_minutes=20, **extra):
    now = datetime.now(timezone.utc)
    return [SimpleNamespace(timestamp=now - timedelta(minutes=(len(values)-1-i)*step_minutes),
                            soil_moisture=value, pump_on=False, **extra)
            for i, value in enumerate(values)]


def test_moisture_forecast_uses_time_and_resists_outlier():
    from app.analytics.forecast import forecast_moisture
    result = forecast_moisture(series([50, 48, 95, 44, 42, 40]), threshold=30)
    assert result['status'] == 'available'
    assert result['dry_down_rate_pct_per_hr'] == pytest.approx(6, abs=0.5)
    assert result['hours_until_threshold'] == pytest.approx(10/6, abs=0.1)
    assert result['moisture_in_1h_pct'] == pytest.approx(34, abs=0.5)


def test_forecast_requires_history_and_fresh_data():
    from app.analytics.forecast import forecast_moisture
    assert forecast_moisture(series([50, 49]))['status'] == 'insufficient_data'
    old = series([50, 48, 46, 44])
    for row in old:
        row.timestamp -= timedelta(hours=2)
    assert forecast_moisture(old)['status'] == 'stale_data'


def test_forecast_does_not_extrapolate_across_watering():
    from app.analytics.forecast import forecast_moisture
    rows = series([50, 48, 46, 60, 59, 58])
    rows[3].pump_on = True
    assert forecast_moisture(rows)['status'] == 'insufficient_data'


def test_forecast_ignores_missing_values_and_duplicate_times():
    from app.analytics.forecast import forecast_moisture
    rows = series([50, 48, None, 44, 42, 40])
    rows.append(rows[-1])
    assert forecast_moisture(rows)['dry_down_rate_pct_per_hr'] == pytest.approx(6)


def test_flat_moisture_has_no_watering_deadline():
    from app.analytics.forecast import forecast_moisture
    assert forecast_moisture(series([50]*5))['hours_until_threshold'] is None


def test_null_sensor_recommendations_do_not_crash(client, seeded_device):
    from app.models.db_models import SensorReading
    from app.analytics.rule_engine import PlantHealthEngine
    from app.models.db_models import PlantProfile
    result = PlantHealthEngine.evaluate(PlantProfile(), SensorReading(), [], [])
    assert result['confidence'] == 0
    assert result['status'] == 'Sensor Data Missing'
