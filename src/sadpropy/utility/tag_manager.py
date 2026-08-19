import numpy as np
from ._exception import ValidationError

class TagManager:
    __slots__ = (
        "_counters",
        "_name_to_tag",
        "_tag_to_name",
    )

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
        self._counters = {category: np.int32(1) for category in categories}
        self._name_to_tag = {category: {} for category in categories}
        self._tag_to_name = {category: {} for category in categories}

    # HELPER METHOD
    def _validate_category(self, category):
        if category not in self._counters:
            raise ValidationError(f"Unknown category '{category}'")
        
    def _store_tag(self, category, name, tag):
        if category not in self._counters:
            raise ValidationError(f"Unknown category '{category}'")
        
        if name in self._name_to_tag[category]:
            raise ValidationError(f"{category} name '{name}' already exists")

        self._name_to_tag[category][name] = int(tag)
        self._tag_to_name[category][tag] = name

    # MAIN METHOD: ADD AUTOMATIC TAG
    def add(self, category, n=1, names=None):
        self._validate_category(category)
        
        if n < 1:
            raise ValidationError("Number of tag allocation must be at least 1")
        
        start = self._counters[category]
        tags = np.arange(start, start + n, dtype=np.int32)
        self._counters[category] = np.int32(start + n)

        if names is not None:
            names = np.asarray(names, dtype="U32")
            if names.ndim != 1:
                raise ValidationError(f"Names must be a one-dimensional array")
            if len(names) != n:
                raise ValidationError(f"Length of names must equal Number of tag")
            unique = np.unique(names)
            if unique.size != names.size:
                dup = unique[np.bincount(np.searchsorted(unique, names)) > 1]
                raise ValidationError(f"Duplicate names in allocation: {', '.join(dup)}"
                )
            for name, tag in zip(names, tags):
                if name in self._name_to_tag[category]:
                    raise ValidationError(f"{category} name '{name}' already exists")
                self._name_to_tag[category][name] = int(tag)
                self._tag_to_name[category][tag] = name
        return tags

    # MAIN METHOD: LOOKUP
    def get_tag(self, category, names):
        self._validate_category(category)
        names = np.asarray(names, dtype="U32")
        original_shape = names.shape
        names = names.ravel()
        lookup = self._name_to_tag[category]
        tags = np.empty(len(names), dtype=np.int32)
        for i, name in enumerate(names):
            try:
                tags[i] = lookup[name]
            except KeyError:
                raise ValidationError(f"{category} name '{name}' not found") from None
        return tags.reshape(original_shape)

    def get_name(self, category, tags):
        self._validate_category(category)
        tags = np.asarray(tags, dtype=np.int32)
        original_shape = tags.shape
        tags = tags.ravel()
        lookup = self._tag_to_name[category]
        names = np.empty(len(tags), dtype="U64")
        for i, tag in enumerate(tags):
            try:
                names[i] = lookup[int(tag)]
            except KeyError:
                raise ValidationError(f"{category} tag '{tag}' not found") from None
        return names.reshape(original_shape)

    # MAIN METHOD: GET INFORMATION
    def next_tag(self, category):
        self._validate_category(category)
        return self._counters[category]

    def count(self, category):
        self._validate_category(category)
        return len(self._used[category])

    # MAIN METHOD: RESET
    def reset(self):
        for category in self._counters:
            self._counters[category] = np.int32(1)
            self._name_to_tag[category].clear()
            self._tag_to_name[category].clear()