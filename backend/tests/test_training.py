import json
import pytest


def test_training_holds_out_data_and_exports_safe_json(tmp_path, monkeypatch):
    from ml.train import train_model
    from app.services.ml_service import predict_crop_details
    from app.models.schemas import SensorData
    rows = []
    for crop, temp in [('cool', 15), ('warm', 35)]:
        for i in range(10):
            rows.append(dict(N=40+i, P=30, K=20, temperature=temp+i/10,
                             humidity=60, ph=6.5, rainfall=100, label=crop))
    model = train_model(rows)
    assert model['validation_metrics']['test_samples'] == 4
    assert model['validation_metrics']['accuracy'] == 1
    path = tmp_path / 'crop.json'
    path.write_text(json.dumps(model), encoding='utf-8')
    monkeypatch.setenv('CROP_MODEL_PATH', str(path))
    result = predict_crop_details(SensorData(**(rows[0] | {'tds': 150})))
    assert result['method'] == 'trained_nearest_centroid'
    assert result['recommended_crop'] == 'cool'


def test_training_rejects_too_few_or_single_class_samples():
    from ml.train import train_model
    with pytest.raises(ValueError):
        train_model([])
