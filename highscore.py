import json
import os

_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")


def hs_load():
    try:
        if os.path.exists(_FILE):
            with open(_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return []


def hs_save(score):
    scores = hs_load()
    scores.append(score)
    scores.sort(reverse=True)
    scores = scores[:5]
    try:
        with open(_FILE, 'w') as f:
            json.dump(scores, f)
    except Exception:
        pass
    return scores
