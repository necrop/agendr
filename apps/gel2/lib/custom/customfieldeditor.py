from ...models import CustomField
from .tabledata import TableData
from .valueparser import value_parser

class CustomFieldForm(object):

    def __init__(self):
        self.table_data = TableData()

    def form(self):
        form = {
            "existing_fields": [],
            "levels_list": [l[0] for l in CustomField.LEVELS],
            "types_list": [l[0] for l in CustomField.TYPES],
        }
        for level in ("entry", "wordclass", "type",):
            ldata = {"level": level, "fields": self.table_data.fields(level)}
            form["existing_fields"].append(ldata)
        return form


class CustomFieldDelete(object):

    def __init__(self, id):
        self.id = id
        self.table_data = TableData()

    def delete(self):
        c = CustomField.objects.get(id=self.id)
        if c is not None:
            c.delete()
            self.table_data.clear()


class CustomEditBase(object):

    def __init__(self, post):
        self.args = self._clean_args(post)
        self.table_data = TableData()

    def _clean_args(self, args):
        return {k: v.strip() or None for k, v in args.items()}


class CustomFieldEdit(CustomEditBase):

    def execute(self):
        cf = CustomField.objects.get(id=int(self.args.get("recordid", 0)))
        if cf is not None:
            cf.name = self.args.get("name")
            cf.description = self.args.get("description", None)
            cf.urltemplate = self.args.get("urltemplate", None)
            cf.default = value_parser(self.args.get("default"), cf.type)
            if cf.type == "select":
                cf.choices = self.args.get("choices")
            cf.save()
            self.table_data.clear()


class CustomFieldAdd(CustomEditBase):

    def execute(self):
        f = {k: self.args[k] for k in (
             "name", "level", "type", "description", "urltemplate")}
        f["choices"] = self._clean_choices()
        if self.args["type"] in (
            "text", "integer", "float", "url", "url template"):
            f["default"] = self.args["default-text"]
        elif self.args["type"] == "boolean":
            f["default"] = self.args["default-boolean"]
        elif self.args["type"] == "select":
            f["default"] = self.args["default-select"]
        if not self.table_data.contains(f["level"], f["name"]):
            CustomField(**f).save()
            self.table_data.clear()

    def _clean_choices(self):
        if self.args["choices"] is None:
            return None
        else:
            c = self.args["choices"].strip(" |")
            parts = [p.strip() for p in c.split("|") if p.strip()]
            return "|".join(parts)
