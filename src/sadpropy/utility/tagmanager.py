__all__ = ["TagManager"]

class TagManager:
    def __init__(self):
        self.counters = {
            'Material': 1,
            'Section': 1,
            'Integration': 1,
            'Transformation': 1,
            'Node': 1,
            'Element': 1,
            'Timeseries': 1,
            'Pattern': 1,
        }

        self.used = {key: set() for key in self.counters}
        self.map_def_to_tag = {key: {} for key in self.counters}
        self.map_tag_to_def = {key: {} for key in self.counters}

    # CORE: STORE TAG
    def _store_tag(self, category, name, tag):
        if name in self.map_def_to_tag[category]:
            raise ValueError(f"{category} name '{name}' already exists")

        self.map_def_to_tag[category][name] = tag
        self.map_tag_to_def[category][tag] = name

    # OPERATION: ADD AUTOMATIC TAG
    def add(self, category, name=None):
        tag = self.counters[category]
        while tag in self.used[category]:
            tag += 1

        self.used[category].add(tag)
        self.counters[category] = tag + 1

        if name:
            self._store_tag(category, name, tag)
        return tag

    # OPERATION: STORE MANUAL TAG
    def store(self, category, tag, name=None):
        if tag in self.used[category]:
            raise ValueError(f"{category} tag {tag} already used")

        self.used[category].add(tag)

        if name:
            self._store_tag(category, name, tag)

    # OPERATION: CALL TAG OR NAME
    def get_tag(self, category, name):
        return self.map_def_to_tag[category][name]

    def get_name(self, category, tag):
        return self.map_tag_to_def[category].get(tag)

    # OPERATION: RESET ALL TAGS
    def reset(self):
        for key in self.counters:
            self.counters[key] = 1
            self.used[key].clear()
            self.map_def_to_tag[key].clear()
            self.map_tag_to_def[key].clear()