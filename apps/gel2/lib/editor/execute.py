import re

from ...models import Entry, Wordclass, Type, Resource, FreqTable, Link
from ..find_record import find_record
from ..grammar.inflection import Inflection
from .utilities import core_fields, freqtable_fields
from ..custom.valueparser import value_parser

mdls = {"entry": Entry, "root": Entry, "wordclass": Wordclass, "type": Type,
        "resource": Resource, "link": Link, "frequency table": FreqTable}


class ExecuteBase(object):
    """Base class for RecordEdit, RecordAdd, and ResourceEdit
    """

    def __init__(self, args):
        self.level = args.get("level", "entry")
        self.record_id = args.get("recordid")
        self.args = mdls[self.level]().clean_values(args)


class RecordEdit(ExecuteBase):

    def implement(self):
        self.record = find_record(self.level, self.record_id)
        if self.record is None:
            return False
        else:
            self._edit_core_fields()
            if self.record.custom_parsed():
                self._edit_custom_fields()
            if self.level == "entry":
                self._edit_entry()
            elif self.level == "wordclass":
                self._edit_wordclass()
            elif self.level == "type":
                self._edit_type()
            self.record.bubble_save()
            return True

    def _edit_core_fields(self):
        for f in core_fields[self.level]:
            if self.record.__dict__[f] != self.args.get(f, ""):
                self.record.__dict__[f] = self.args.get(f, "")

    def _edit_custom_fields(self):
        values = {int(k.split("_")[1]): v for k, v in self.args.items()
                  if k.startswith("custom_")}
        store = []
        for id, value in values.items():
            for cf in self.record.custom_parsed():
                if cf.id == id:
                    # coerce the value into the correct type
                    value = value_parser(value, cf.type)
                    if value != cf.default:
                        store.append((id, str(value)))
        self.record.custom = "\t".join(["%d:%s" % cf for cf in store])
        if not self.record.custom:
            self.record.custom = None

    def _edit_entry(self):
        # update the alphasort version of the label
        self.record.update_alphasort()
        # resource links
        self._update_resource_links()
        # topics
        self._update_topics()

    def _edit_wordclass(self):
        # obsoleteness
        if self.args.get("obsolete") == "on" and not self.record.obsolete:
            self.record.obsolete = True
        elif self.record.obsolete:
            self.record.obsolete = False

    def _edit_type(self):
        # frequency table
        self._update_frequency_table()

    def _update_resource_links(self):
        links = self.record.links()
        for link in links:
            new_entryid = self.args.get("link_%d_entryid" % (link.id,))
            new_nodeid = self.args.get("link_%d_nodeid" % (link.id,))
            if new_entryid != link.target_id or new_nodeid != link.target_node:
                if new_entryid is None:
                    # delete link
                    link.delete()
                else:
                    # amend link
                    link.target_id = new_entryid
                    link.target_node = new_nodeid
                    link.save()
        # create new link
        if self.args.get("new_link_entryid") is not None:
            res = find_record("resource", self.args.get("new_link_resourceid"))
            if res is not None:
                new_link = Link(
                    entry=self.record,
                    target_resource=res,
                    target_id=self.args.get("new_link_entryid"),
                    target_node=self.args.get("new_link_nodeid")
                )
                new_link.save()

    def _update_topics(self):
        topics_on = ticked_topics(self.args)
        # remove any topics that have been unticked
        for t in self.record.topic_list():
            if not t.id in topics_on:
                t.delete()
        # add topics that *have* been ticked (shouldn't matter if this duplicates an existing topic)
        for id in topics_on:
            #if [t for t in self.record.topic_list() if t.id == id]:
            #    pass
            #else:
            new_topic = find_record("topic", id)
            if new_topic is not None:
                self.record.topics.add(new_topic)

    def _update_frequency_table(self):
        # handle child frequency table
        ft = self.record.frequency_table()
        # delete frequency table
        if self.args.get("removeFreqTable") == "on":
            if ft is not None:
                ft.delete()
        # edit/create frequency table
        else:
            frequencies = {}
            for f, v, in self.args.items():
                if re.search(r"^freqtable_(f[0-9]{4})$", f):
                    m = re.search(r"^freqtable_(f[0-9]{4})$", f)
                    field = m.group(1)
                    try:
                        freq = float(v)
                    except (TypeError, ValueError,):
                        freq = float(0)
                    # round to 2 significant digits
                    freq = float("%.2g" % freq)
                    if freq == 0 or freq < 0:
                        freq = None
                    frequencies[field] = freq
            nonzero = [freq for freq in frequencies.values()
                       if freq is not None and freq > 0]
            if ft is None and nonzero:
                # create a new frequency table
                kwargs = {"type": self.record}
                for field in freqtable_fields:
                    try:
                        kwargs[field] = frequencies[field]
                    except KeyError:
                        kwargs[field] = None
                ft = FreqTable(**kwargs)
                ft.dated_save()
            elif ft is not None:
                # compare existing frequency table, and update if necessary
                ft_changed = False
                for field in freqtable_fields:
                    if (field in frequencies and
                        frequencies[field] != getattr(ft, field)):
                        ft.__dict__[field] = frequencies[field]
                        ft_changed = True
                if ft_changed:
                    ft.dated_save()


class RecordAdd(ExecuteBase):

    def implement(self):
        self.parent = find_record(self.level, self.record_id)
        if self.level == "root":
            new_model = Entry
            new_level = "entry"
        elif self.level == "entry":
            new_model = Wordclass
            new_level = "wordclass"
        elif self.level == "wordclass":
            new_model = Type
            new_level = "type"
        self.args = new_model().clean_values(self.args)
        core = {f: self.args.get(f, "") for f in core_fields[new_level]}
        new = new_model(**core)

        if new_level == "entry":
            self._edit_entry(new)
            new.bubble_save()
            self._add_topics(new)
            self._add_children(new)
        elif new_level == "wordclass":
            self._edit_wordclass(new)
            new.bubble_save()
            self._add_children(new)
        elif new_level == "type":
            self._edit_type(new)
            new.bubble_save()
        return new

    def _edit_entry(self, new):
        # add alphasort version of label
        new.update_alphasort()

    def _edit_wordclass(self, new):
        # link to parent entry
        new.entry = self.parent
        # obsoleteness
        if self.args.get("obsolete") == "on":
            new.obsolete = True
        else:
            new.obsolete = False

    def _edit_type(self, new):
        # link to parent wordclass
        new.wordclass = self.parent

    def _add_topics(self, new):
        topics_on = ticked_topics(self.args)
        for id in topics_on:
            new_topic = find_record("topic", id)
            if new_topic is not None:
                new.topics.add(new_topic)

    def _add_children(self, new):
        args = {k: v for k, v in self.args.items()}
        args["level"] = new.level()
        args["recordid"] = str(new.id)
        if new.level() == "wordclass":
            args["variant"] = "s"
            args["form"] = new.label()
        RecordAdd(args).implement()
        if (new.level() == "wordclass" and
            args.get("generate") in ("on", True) and
            new.penn in ("NN", "VB")):
            self._add_inflections(new, args)

    def _add_inflections(self, new, args):
        inflector = Inflection()
        if new.penn == "NN":
            inflections = ("NNS",)
        if new.penn == "VB":
            inflections = ("VBZ", "VBG", "VBN", "VBD",)
        for pos in inflections:
            args["penn"] = pos
            args["form"] = inflector.compute_inflection(new.label(), pos)
            RecordAdd(args).implement()


class ResourceEdit(ExecuteBase):

    def implement(self):
        if self.args.get("action") == "add":
            return self._add_resource()
        elif self.args.get("action") == "edit":
            return self._edit_resource()

    def _edit_resource(self):
        try:
            record = Resource.objects.get(id=self.record_id)
        except Resource.DoesNotExist:
            return
        for field in self._fields():
            record.__dict__[field] = self.args.get(field, "")
        record.save()
        return record

    def _add_resource(self):
        args = {f: self.args.get(f, "") for f in self._fields()}
        record = Resource(**args)
        record.save()
        return record

    def _fields(self):
        return [f.name for f in Resource._meta.fields
                if f.name not in ("id", "pk")]


def ticked_topics(args):
    return set([int(k.replace("topic_", "")) for k, v in
                args.items() if k.startswith("topic_") and v == "on"])

