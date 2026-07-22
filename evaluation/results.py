"""Saves and loads evaluation run results to/from JSON, so different runs
(different k, different retrieval method, before/after a fix) can be
compared later, plotted, whatever, without re-running everything each time.

Works for either evaluate_retrieval's rows or evaluate_answers' rows, both
are already flat, JSON-safe dicts (or dicts with a nested metadata dict, in
the retrieval case), no special handling needed either way.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# fields worth pulling out of the rows automatically, if every row in a run
# agrees on the same value, since that's a hyperparameter of the run itself,
# not something worth re-typing by hand and risking it drifting out of sync
_AUTO_DETECT_FIELDS = ("k", "relevance_threshold")


def _auto_params(rows):
    if not rows:
        return {}
    auto = {}
    for field in _AUTO_DETECT_FIELDS:
        if field in rows[0] and all(r.get(field) == rows[0][field] for r in rows):
            auto[field] = rows[0][field]
    return auto


def save_results(rows, path, label=None, **extra_meta):
    """rows: list of dicts from evaluate_retrieval or evaluate_answers.
    label: a short name for this run, e.g. 'baseline_dense_k5', so you can
    tell runs apart later without relying on the filename alone.
    extra_meta: anything worth recording that ISN'T already on every row,
    e.g. method='hybrid'. Values already present and consistent across rows
    (k, relevance_threshold) get pulled in automatically, no need to pass
    those yourself, and doing so can't accidentally contradict what actually ran."""
    payload = {
        "label": label,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        **_auto_params(rows),
        **extra_meta,
        "rows": rows,
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_results(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)