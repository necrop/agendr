
from ...models import CustomField
from .tabledata import TableData
from .valueparser import value_parser


class CustomParser(object):

    def __init__(self, level, custom_string):
        self.level = level
        self.custom_string = custom_string

    def fields(self):
        try:
            return self.fieldslist
        except AttributeError:
            self._parse()
            return self.fieldslist

    def _parse(self):
        # Include all fields registered for this level, initially with the
        #  value set to the default
        self.fieldslist = []
        registered_fields = TableData().fields(self.level)
        for r in registered_fields:
            self.fieldslist.append(Field(r, r.default))

        # Now overwrite the values with any explicit values given in the
        # custom string
        if self.custom_string is None:
            pass
        else:
            keyval_pairs = [f.strip() for f in self.custom_string.split("\t")
                            if len(f.strip().split(":")) == 2]
            for keyval_pair in keyval_pairs:
                id, value = keyval_pair.split(":")
                try:
                    id = int(id)
                except ValueError:
                    pass
                else:
                    for f in self.fieldslist:
                        if f.id == id:
                            f.value = value_parser(value, f.type)


class Field(object):

    def __init__(self, r, value):
        for k, v in r.__dict__.items():
            self.__dict__[k] = v
        self.value = value_parser(value, self.type)

    def is_default(self):
        if self.value == self.default:
            return True
        else:
            return False

    def compiled_url(self):
        def add_http(url):
            if (url.startswith("http://") or
                url.startswith("https://") or
                url.startswith("ftp://")):
                return url
            else:
                return "http://" + url.lstrip(" :/")
        if self.type == "url":
            return add_http(self.value)
        elif (self.type == "url template" and
            self.urltemplate is not None and
            self.value is not None):
            return add_http(self.urltemplate.replace("{{PARAM}}", self.value))
        else:
            return None
