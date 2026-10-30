"""Train a standardized nearest-centroid classifier from a labelled crop CSV.

Run from backend: python -m ml.train crops.csv --output ml/crop-model.json
"""
import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev

from app.models.schemas import SensorData
from app.services.ml_service import FEATURES


def train_model(rows, seed=42):
    groups = defaultdict(list)
    for row in rows:
        label = str(row.get('label', '')).strip()
        if not label:
            raise ValueError('Each row needs a crop label')
        sample = SensorData(**{name: row[name] for name in FEATURES}, tds=0)
        groups[label].append([getattr(sample, name) for name in FEATURES])
    if len(groups) < 2 or any(len(values) < 5 for values in groups.values()):
        raise ValueError('Need at least two crops with five samples each')
    train, test = [], []
    rng = random.Random(seed)
    for label, values in sorted(groups.items()):
        rng.shuffle(values)
        count = max(1, round(len(values)*0.2))
        test.extend((label, x) for x in values[:count])
        train.extend((label, x) for x in values[count:])
    # Fit preprocessing only on the training split to avoid validation leakage.
    means = [mean(x[i] for _,x in train) for i in range(len(FEATURES))]
    scales = [pstdev(x[i] for _,x in train) or 1 for i in range(len(FEATURES))]
    centroids = {}
    for label in groups:
        centroids[label] = [mean((x[i]-means[i])/scales[i] for crop,x in train if crop == label)
                            for i in range(len(FEATURES))]
    correct = 0
    recalls = defaultdict(list)
    for label, values in test:
        normalized = [(x-m)/s for x,m,s in zip(values,means,scales)]
        predicted = min(centroids, key=lambda crop: (sum((x-c)**2 for x,c in zip(normalized,centroids[crop])), crop))
        correct += predicted == label
        recalls[label].append(int(predicted == label))
    return dict(version=1, features=list(FEATURES), mean=means, scale=scales,
                centroids=centroids, seed=seed,
                validation_metrics=dict(accuracy=correct/len(test),
                                        balanced_accuracy=mean(mean(v) for v in recalls.values()),
                                        train_samples=len(train), test_samples=len(test),
                                        split='stratified_80_20',
                                        limitation='Random holdout; validate separately across farms and seasons.'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_path', type=Path)
    parser.add_argument('--output', type=Path, default=Path('ml/crop-model.json'))
    args = parser.parse_args()
    with args.csv_path.open(encoding='utf-8-sig', newline='') as source:
        model = train_model(list(csv.DictReader(source)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(model, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(model['validation_metrics'], indent=2))


if __name__ == '__main__':
    main()
