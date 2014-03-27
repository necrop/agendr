import re

from ...models import FreqTable, Topic, Resource
from ..grammar.wordclass_utilities import (human_readable_pos,
    main_wordclasses, inflections_for_wordclass)
from .utilities import core_fields, variant_opts, freqtable_fields


class EditorForm(object):

    def __init__(self, record):
        self.record = record

    def edit_form(self):
        template = "edit_" + self.record.level() + ".html"
        form = {}
        if self.record.level() == "entry":
            form["current_resources"] = self.record.links()
            form["known_resources"] = Resource.objects.all()
            form["topics"] = topic_options(self.record)
        if self.record.level() == "wordclass":
            form["wordclass_options"] = wordclass_options(level="wordclass",
                current=self.record.penn)
        elif self.record.level() == "type":
            form["variant_options"] = variant_options(v=self.record.variant)
            form["wordclass_options"] = wordclass_options(level="type",
                current=self.record.penn, wordclass=self.record.wordclass.penn)
            form["freqtable"] = self._frequency_table()
        form["custom_fields"] = self.record.custom_parsed()
        return (template, form)

    def add_form(self):
        form = {}
        if self.record == None:
            template = "edit_entry.html"
            title = "Create new entry"
            form["wordclass_options"] = wordclass_options(level="wordclass")
            form["topics"] = topic_options(None)
        elif self.record.level() == "entry":
            template = "edit_wordclass.html"
            title = "Add wordclass to entry #%d (%s)" % (self.record.id,
                    self.record.label)
            form["wordclass_options"] = wordclass_options(level="wordclass")
        elif self.record.level() == "wordclass":
            template = "edit_type.html"
            title = "Add type to wordclass #%d (%s_%s)" % (self.record.id,
                    self.record.label(), self.record.penn)
            form["variant_options"] = variant_options()
            form["wordclass_options"] = wordclass_options(level="type",
                wordclass=self.record.penn)
        return (template, form, title)

    def _frequency_table(self):
        vals = []
        ft = self.record.frequency_table()
        for field in [f.name for f in FreqTable._meta.fields
                      if re.search(r"^f[0-9]{4}$", f.name)]:
            label = field.strip("f")
            if ft is None:
                vals.append({"field": field,
                             "label": label,
                             "value": None,
                             "is_set": False})
            else:
                vals.append({"field": field,
                             "label": label,
                             "value": getattr(ft, field) or float(0),
                             "is_set": True})
        return vals


def wordclass_options(**kwargs):
    level = kwargs.get("level", "wordclass")
    current_penn = kwargs.get("current", None)
    wordclass = kwargs.get("wordclass", "NN")
    options = []
    if level == "wordclass":
        for penn in main_wordclasses:
            if penn == current_penn:
                selected = True
            else:
                selected = False
            options.append((penn,
                            human_readable_pos(penn, mode="base"),
                            selected))
    if level == "type":
        inflections = inflections_for_wordclass(wordclass)
        for penn in inflections:
            if penn == current_penn:
                selected = True
            else:
                selected = False
            options.append((penn,
                            human_readable_pos(penn, mode="full"),
                            selected))
    return options

def variant_options(**kwargs):
    current_variant = kwargs.get("v", None)
    options = []
    for v in variant_opts:
        if v[0] == current_variant:
            selected = True
        else:
            selected = False
        options.append((v[0], v[1], selected,))
    return options

def topic_options(record):
    options = sorted(Topic.objects.all(), key=lambda t: t.breadcrumb())
    if record is None:
        selected = set()
    else:
        selected = set([t.id for t in record.topic_list()])
    for opt in options:
        if opt.id in selected:
            opt.selected = True
        else:
            opt.selected = False
    return options
