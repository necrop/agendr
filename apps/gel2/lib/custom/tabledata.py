from collections import defaultdict
from ...models import CustomField
from .valueparser import value_parser

class TableData(object):
    data = defaultdict(list)

    def __init__(self):
        pass

    def _load_data(self):
        if not TableData.data:
            for f in CustomField.objects.all():
                TableData.data[f.level].append(Field(f))

    def fields(self, level):
        self._load_data()
        try:
            return TableData.data[level]
        except KeyError:
            return []

    def contains(self, level, name):
        for f in self.fields(level):
            if f.name == name:
                return True
        return False

    def property(self, **kwargs):
        level = kwargs.get("level")
        field = kwargs.get("field")
        prop = kwargs.get("property", "default")
        for f in self.fields(level):
            if f.name == field:
                try:
                    return f.__dict__[property]
                except KeyError:
                    return None

    def clear(self):
        TableData.data.clear()


class Field(object):

    def __init__(self, record):
        for k in [f.name for f in record._meta.fields]:
            self.__dict__[k] = record.__dict__[k]
        self._parse_default()
        self._parse_choices()

    def _parse_default(self):
        self.default= value_parser(self.default, self.type)

    def _parse_choices(self):
        if self.choices is None or self.choices == "":
            self.choiceslist = []
        else:
            self.choiceslist = [c.strip() for c in self.choices.split("|")]
