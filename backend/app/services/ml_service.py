"""Explainable crop ranking; optionally uses a locally trained centroid model."""
import json
import logging
import math
import os
from functools import lru_cache
from pathlib import Path
from app.models.schemas import SensorData

FEATURES = ('N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall')
# Broad illustrative suitability ranges, not learned parameters or yield guarantees.
RANGES = {
    'Rice': ((60,120),(25,60),(25,60),(20,35),(75,95),(5.5,7),(150,300)),
    'Wheat': ((40,100),(20,60),(20,60),(12,25),(40,70),(6,7.5),(40,110)),
    'Maize': ((60,120),(30,70),(20,60),(18,32),(50,80),(5.5,7.5),(60,150)),
    'Cotton': ((60,120),(20,60),(20,70),(25,38),(35,65),(6,8),(40,120)),
    'Chickpea': ((10,50),(35,75),(20,70),(15,28),(20,60),(6,8),(30,90)),
    'Potato': ((40,100),(30,80),(50,150),(12,24),(50,85),(5,6.5),(50,120)),
}


@lru_cache(maxsize=4)
def _load_model(path, modified_ns):
    model = json.loads(Path(path).read_text(encoding='utf-8'))
    if model['features'] != list(FEATURES) or model['version'] != 1:
        raise ValueError('Unsupported crop model schema')
    for key in ('mean', 'scale'):
        if len(model[key]) != len(FEATURES) or not all(math.isfinite(x) for x in model[key]):
            raise ValueError('Invalid model normalization')
    if any(x <= 0 for x in model['scale']) or len(model['centroids']) < 2:
        raise ValueError('Invalid model classes or scale')
    for values in model['centroids'].values():
        if len(values) != len(FEATURES) or not all(math.isfinite(x) for x in values):
            raise ValueError('Invalid centroid')
    return model


def predict_crop_details(data: SensorData):
    values = [getattr(data, name) for name in FEATURES]
    model_path = os.getenv('CROP_MODEL_PATH')
    model = None
    if model_path:
        try:
            model = _load_model(model_path, Path(model_path).stat().st_mtime_ns)
        except (OSError, ValueError, KeyError, TypeError):
            logging.getLogger(__name__).warning('Crop model unavailable; using suitability ranges')
    ranked = []
    if model:
        normalized = [(x-m)/s for x,m,s in zip(values, model['mean'], model['scale'])]
        for crop, centroid in model['centroids'].items():
            distance = sum((x-c)**2 for x,c in zip(normalized, centroid)) / len(FEATURES)
            ranked.append((crop, 1 / (1 + distance), []))
        method = 'trained_nearest_centroid'
    else:
        for crop, ranges in RANGES.items():
            penalties = [max(lo-x, 0, x-hi)/(hi-lo) for x,(lo,hi) in zip(values, ranges)]
            score = math.exp(-sum(p*p for p in penalties)/len(FEATURES))
            outside = [name for name,p in zip(FEATURES, penalties) if p > 0]
            ranked.append((crop, score, outside))
        method = 'agronomic_similarity'
    ranked.sort(key=lambda item: (-item[1], item[0]))
    return {
        'recommended_crop': ranked[0][0],
        'method': method,
        'alternatives': [{'crop': crop, 'suitability_score': round(score, 4),
                          'outside_preferred_range': outside} for crop,score,outside in ranked[:3]],
        'validation_metrics': model.get('validation_metrics') if model else None,
        'limitations': 'Suitability scores are not calibrated probabilities or yield predictions. '
                        'Confirm soil test units, rainfall period, season and local agronomy. '
                        'TDS is not used as a substitute for nutrient measurements.'
                        + ('' if model else ' No dataset-trained crop model is loaded.'),
    }


def predict_crop(data: SensorData):
    return predict_crop_details(data)['recommended_crop']
