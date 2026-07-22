"""Loads the given evaluation set and splits it into dev/test, stratified
by question_type and difficulty so the split is reproducible and proportional
rather than a plain random shuffle"""

import json
import random
from collections import defaultdict


def load_eval_set(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def stratified_split(items, dev_fraction=0.2, seed=42):
    """Splits proportionally within each (question_type, difficulty) group."""
    groups = defaultdict(list)
    for item in items:
        key = (item["question_type"], item.get("difficulty", "unknown"))
        groups[key].append(item)

    rng = random.Random(seed)
    dev, test = [], []
    for group in groups.values():
        group = group[:]
        rng.shuffle(group)
        n_dev = round(len(group) * dev_fraction)
        dev.extend(group[:n_dev])
        test.extend(group[n_dev:])
    return dev, test


def save_split(dev, test, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"dev": dev, "test": test}, f, ensure_ascii=False, indent=2)


def load_split(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["dev"], data["test"]