"""Bounded robust dry-down regression over a single uninterrupted watering cycle."""
import math
from datetime import datetime, timezone
from statistics import median


def forecast_moisture(readings, threshold=30, now=None):
    now = now or datetime.now(timezone.utc)
    result = dict(status='insufficient_data', method='theil_sen', sample_count=0,
                  dry_down_rate_pct_per_hr=None, moisture_in_1h_pct=None,
                  hours_until_threshold=None, residual_mae_pct=None,
                  reason='Need at least 4 valid readings spanning 1 hour after watering.')
    points = {}
    for row in readings:
        value, timestamp = row.soil_moisture, row.timestamp
        if timestamp is None:
            continue
        timestamp = timestamp.replace(tzinfo=timezone.utc) if timestamp.tzinfo is None else timestamp
        if timestamp <= now:
            points[timestamp] = (value, bool(row.pump_on))
    segment = []
    for timestamp, (value, pump_on) in sorted(points.items()):
        if pump_on:
            segment = []
            continue
        if value is None or not math.isfinite(value) or not 0 <= value <= 100:
            continue
        if segment and (timestamp-segment[-1][0]).total_seconds() > 3600:
            segment = []
        segment.append((timestamp, value))
    if not segment:
        return result
    # A sustained refill resets the fit; median slopes handle isolated spikes.
    for i in range(len(segment)-2, 0, -1):
        if segment[i][1] - segment[i-1][1] > 5 and segment[i+1][1] >= segment[i][1]-2:
            segment = segment[i:]
            break
    if len(segment) > 120:
        segment = [segment[round(i*(len(segment)-1)/119)] for i in range(120)]
    result['sample_count'] = len(segment)
    if (now-segment[-1][0]).total_seconds() > 300:
        return result | dict(status='stale_data', reason='Latest soil reading is older than 5 minutes.')
    span = (segment[-1][0]-segment[0][0]).total_seconds()/3600
    if len(segment) < 4 or span < 1:
        return result
    xy = [((timestamp-segment[0][0]).total_seconds()/3600, value) for timestamp,value in segment]
    slopes = [(y2-y1)/(x2-x1) for i,(x1,y1) in enumerate(xy) for x2,y2 in xy[i+1:] if x2>x1]
    slope = median(slopes)
    intercept = median([y-slope*x for x,y in xy])
    mae = sum(abs(y-(intercept+slope*x)) for x,y in xy)/len(xy)
    if median([abs(y-(intercept+slope*x)) for x,y in xy]) > 5:
        return result | dict(status='unstable', reason='Moisture varies too much for a useful forecast.')
    latest = xy[-1][1]
    horizon = min(span, 6)
    deadline = 0 if latest <= threshold else ((latest-threshold)/-slope if slope < -0.1 else None)
    if deadline is not None and deadline > horizon:
        deadline = None
    return result | dict(status='available', dry_down_rate_pct_per_hr=round(max(0,-slope), 2),
                         moisture_in_1h_pct=round(max(0,min(100,latest+slope)), 1),
                         hours_until_threshold=round(deadline, 2) if deadline is not None else None,
                         residual_mae_pct=round(mae, 2),
                         reason=f'Statistical estimate; assumes no watering and unchanged conditions. Horizon {horizon:.1f}h; no automatic pump actuation.')
