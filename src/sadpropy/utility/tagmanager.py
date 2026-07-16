import numpy as np
from ._exceptions import ValidationError

__all__ = ["TagManager"]

class TagManager:
    def __init__(self):
        categories = {
            "Node",
            "Element",
            "Material",
            "Section",
            "Beam Integration",
            "Geometric Transformation",
            "Timeseries",
            "Pattern",
        }
        self._counters = {category: 1 for category in categories}
        self._used = {category: set() for category in categories}
        self._name_to_tag = {category: {} for category in categories}
        self._tag_to_name = {category: {} for category in categories}

    # MAIN METHOD: STORE TAG
    def _store_tag(self, category, name, tag):
        if category not in self._counters:
            raise ValidationError(f"Unknown category '{category}'")
        
        if name in self._name_to_tag[category]:
            raise ValidationError(f"{category} name '{name}' already exists")

        self._name_to_tag[category][name] = int(tag)
        self._tag_to_name[category][tag] = name

    # SUPPORTING METHOD: ADD AUTOMATIC TAG
    def add(self, category, n=1, names=None):
        if category not in self._counters:
            raise ValidationError(f"Unknown category '{category}'")
        
        if n < 1:
            raise ValidationError("Number of tag allocation must be at least 1")
        
        start = self._counters[category]
        tags = np.arange(start, start + n, dtype=np.int32)
        self._used[category].update(tags.tolist())
        self._counters[category] += n

        if names is not None:
            if len(names) != n:
                raise ValidationError("Length of names must equal Number of tag")
            for name, tag in zip(names, tags):
                self._store_tag(category, name, int(tag))
        if n == 1:
            return int(tags[0])
        return tags

    # SUPPORTING METHOD: LOOKUP
    def get_tag(self, category, name):
        if category not in self._counters:
            raise ValidationError(f"Unknown category '{category}'")
        return self._name_to_tag[category][name]

    def get_name(self, category, tag):
        if category not in self._counters:
            raise ValidationError(f"Unknown category '{category}'")
        return self._tag_to_name[category].get(int(tag))

    # SUPPORTING METHOD: GET INFORMATION
    def next_tag(self, category):
        if category not in self._counters:
            raise ValidationError(f"Unknown category '{category}'")
        return self._counters[category]

    def count(self, category):
        if category not in self._counters:
            raise ValidationError(f"Unknown category '{category}'")
        return len(self._used[category])

    # SUPPORTING METHOD: RESET
    def reset(self):
        for category in self._counters:
            self._counters[category] = 1
            self._used[category].clear()
            self._name_to_tag[category].clear()
            self._tag_to_name[category].clear()