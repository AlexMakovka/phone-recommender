import csv
import math
import os
from datetime import datetime


# Feature importance weights for each user preference category.
# New preferences:
#  - social: focus on battery, moderate camera and screen
#  - work: focus on battery and RAM
#  - budget: handled separately in _build_weights
weight_map = {
    'photo':  {'camera': 3, 'battery': 1, 'ram': 1, 'screen': 1},  # Photography
    'gaming': {'camera': 0, 'battery': 2, 'ram': 3, 'screen': 2},  # Gaming
    'video':  {'camera': 0, 'battery': 2, 'ram': 1, 'screen': 4},  # Video
    'social': {'camera': 1, 'battery': 2, 'ram': 1, 'screen': 1},  # Social networks & messaging
    'work':   {'camera': 1, 'battery': 2, 'ram': 2, 'screen': 1},  # Work & business tasks
    # 'budget' — handled separately via price
}


def _compute_feature_ranges(phones):
    """
    Compute min and max values for each numeric feature for normalization.
    """
    cameras = [p['Camera'] for p in phones]
    batteries = [p['Battery'] for p in phones]
    rams = [p['RAM'] for p in phones]
    screens = [p['Screen'] for p in phones]
    prices = [p['Price'] for p in phones]

    ranges = {
        'Camera': (min(cameras), max(cameras)),
        'Battery': (min(batteries), max(batteries)),
        'RAM': (min(rams), max(rams)),
        'Screen': (min(screens), max(screens)),
        'Price': (min(prices), max(prices))
    }
    return ranges


def _normalize_value(value, vmin, vmax):
    """
    Normalize value to [0,1]. Returns 0.5 if min == max.
    """
    if vmax == vmin:
        return 0.5
    return (value - vmin) / (vmax - vmin)


def _phone_to_vector(phone, ranges):
    """
    Convert phone into a normalized numeric feature vector.
    Feature order: [camera, battery, ram, screen, price].
    Price is inversely normalized (cheaper = better).
    """
    cam = _normalize_value(phone['Camera'], *ranges['Camera'])
    bat = _normalize_value(phone['Battery'], *ranges['Battery'])
    ram = _normalize_value(phone['RAM'], *ranges['RAM'])
    scr = _normalize_value(phone['Screen'], *ranges['Screen'])

    price_raw = _normalize_value(phone['Price'], *ranges['Price'])
    price = 1.0 - price_raw  # invert price: cheaper = closer to 1

    return [cam, bat, ram, scr, price]


def _build_weights(user_prefs):
    """
    Build final feature weights based on user's selected preferences.
    Returns a dict with weights for camera, battery, ram, screen, price.
    """
    weights = {'camera': 0.0, 'battery': 0.0, 'ram': 0.0, 'screen': 0.0}

    for pref in user_prefs:
        if pref in weight_map:
            for feature, w in weight_map[pref].items():
                weights[feature] += w

    # Base handling for price
    if not user_prefs:
        # If user has no preferences – uniform distribution
        weights = {'camera': 1.0, 'battery': 1.0, 'ram': 1.0, 'screen': 1.0}
        price_weight = 2.0  # emphasize price more
    else:
        # If preferences exist, price is considered but not dominant
        price_weight = 1.0

    # If user explicitly wants low price — increase price weight
    if 'budget' in user_prefs:
        price_weight += 2.0

    weights['price'] = price_weight
    return weights


def _build_ideal_vector(weights):
    """
    Build the "ideal" phone vector in normalized feature space.
    For features with non-zero weight, ideal = 1 (max),
    for zero-weight features = 0.5 (neutral).
    Price ideal = 1 (cheaper is better).
    Returns vector in order [camera, battery, ram, screen, price].
    """
    def ideal_for_feature(name):
        return 1.0 if weights[name] > 0 else 0.5

    ideal_cam = ideal_for_feature('camera')
    ideal_bat = ideal_for_feature('battery')
    ideal_ram = ideal_for_feature('ram')
    ideal_scr = ideal_for_feature('screen')
    ideal_price = 1.0

    return [ideal_cam, ideal_bat, ideal_ram, ideal_scr, ideal_price]


def _weighted_euclidean_distance(vec_phone, vec_ideal, weights):
    """
    Weighted Euclidean distance between phone and ideal vector.
    This is the k-nearest neighbors core:
    we look for k phones closest to the "ideal" device.
    """
    feature_order = ['camera', 'battery', 'ram', 'screen', 'price']
    diff_sum = 0.0
    for i, feature_name in enumerate(feature_order):
        w = weights.get(feature_name, 0.0)
        if w <= 0:
            continue
        diff = vec_phone[i] - vec_ideal[i]
        diff_sum += w * (diff ** 2)
    return math.sqrt(diff_sum)


def recommend(user_prefs, phones, k=3,
              price_max=None, ram_min=None,
              screen_min=None, screen_max=None):
    """
    Return top-k phone models recommended based on user preferences.

    Steps:
    1. Apply hard filters (price, RAM, screen size).
    2. Build "ideal" vector in normalized feature space.
    3. Find k nearest neighbors (minimum weighted distance).
    """
    if not phones:
        return []

    # 1. Filter by hard constraints
    filtered = []
    for phone in phones:
        if price_max is not None and phone['Price'] > price_max:
            continue
        if ram_min is not None and phone['RAM'] < ram_min:
            continue
        if screen_min is not None and phone['Screen'] < screen_min:
            continue
        if screen_max is not None and phone['Screen'] > screen_max:
            continue
        filtered.append(phone)

    # If nothing remains after filtering, use full list
    if not filtered:
        filtered = phones

    ranges = _compute_feature_ranges(filtered)
    weights = _build_weights(user_prefs)
    ideal_vec = _build_ideal_vector(weights)

    scored = []
    for phone in filtered:
        phone_vec = _phone_to_vector(phone, ranges)
        dist = _weighted_euclidean_distance(phone_vec, ideal_vec, weights)
        scored.append((dist, phone))

    scored.sort(key=lambda x: x[0])
    top_recommendations = [item[1] for item in scored[:k]]
    return top_recommendations


def log_user_interaction(user_id, user_prefs, recommended_phones, log_path='data/behavior_log.csv'):
    """
    Log user behavior:
    - user_id: user identifier (login/name)
    - selected preferences
    - recommended phones

    Data is stored in CSV and can be used for behavior analysis (Data Mining).
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    file_exists = os.path.isfile(log_path)
    with open(log_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'user', 'preferences', 'recommended_phones'])

        timestamp = datetime.now().isoformat(timespec='seconds')
        prefs_str = ';'.join(user_prefs) if user_prefs else ''
        rec_names = ';'.join([p['Name'] for p in recommended_phones])

        user_str = user_id if user_id else 'guest'
        writer.writerow([timestamp, user_str, prefs_str, rec_names])


def get_user_history(user_id, log_path='data/behavior_log.csv', limit=10):
    """
    Return the last `limit` recommendation records for the specified user.
    If user_id == None, returns an empty list.
    """
    if not user_id:
        return []

    if not os.path.isfile(log_path):
        return []

    history = []
    with open(log_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('user') != user_id:
                continue
            history.append({
                'timestamp': row.get('timestamp'),
                'preferences': row.get('preferences', '').split(';') if row.get('preferences') else [],
                'recommended_phones': row.get('recommended_phones', '').split(';') if row.get('recommended_phones') else []
            })

    # last `limit` records
    history = history[-limit:]
    # reverse so newest are first
    history.reverse()
    return history
