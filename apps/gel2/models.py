import re
from unidecode import unidecode

from django.db import models
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse

from .lib.grammar.wordclass_utilities import human_readable_pos
from .lib.recordmixin import RecordMixin, EntryMixin
from .lib.utils.alphasort import alphasort


class Topic(models.Model):
    """Topic from the topic taxonomy
    """
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, null=True, blank=True)
    superordinate = models.ForeignKey("self", null=True)

    def breadcrumb(self):
        b = self.name
        if self.superordinate is not None:
            b = self.superordinate.breadcrumb() + u" \u00bb " + b
        return b

    def level(self):
        def recurse(node, val):
            val += 1
            if node.superordinate is not None:
                return recurse(node.superordinate, val)
            else:
                return val
        return recurse(self, 0)

    def indented(self):
        def recurse(node, val):
            if node.superordinate is not None:
                val += u"\u00a0\u00a0\u00a0\u00a0"
                return recurse(node.superordinate, val)
            else:
                return val
        return recurse(self, u"") + self.name

    def is_leaf(self):
        if not self.topic_set.all():
            return True
        else:
            return False


class Entry(models.Model, EntryMixin):
    """Main GEL2 entry (representing a lemma)
    """
    alphasort = models.CharField(max_length=50, db_index=True)
    label = models.CharField(max_length=50)
    soundfile_us = models.CharField(max_length=50, blank=True, null=True)
    soundfile_uk = models.CharField(max_length=50, blank=True, null=True)
    datestamp = models.DateTimeField()
    custom = models.TextField(blank=True, null=True)
    topics = models.ManyToManyField(Topic)

    def __unicode__(self):
        return "%s (#%d)" % (self.label, self.id)

    def get_absolute_url(self):
        return reverse("gel_entry", kwargs={"id": str(self.id)})

    def level(self):
        return "entry"

    def identifier(self):
        return self.label

    def wordclasses(self):
        try:
            return self.wc
        except AttributeError:
            self.wc = sorted(self.wordclass_set.all(), key=lambda w: w.penn)
            if len(self.wc) == 1:
                self.wc[0].solo = True
            else:
                for w in self.wc:
                    w.solo = False
            return self.wc

    def wordclasses_sorted(self):
        return sorted(self.wordclasses(),
                      key=lambda wc: wc.mod_frequency(zeroed=True),
                      reverse=True)

    def wordclass_list(self):
        return ", ".join([w.pos_description() for w in
                          self.wordclasses_sorted()])

    def contains_wordclass(self, penn):
        if penn in [w.penn for w in self.wordclasses()]:
            return True
        else:
            return False

    def definition(self):
        for wc in self.wordclasses_sorted():
            if wc.definition is not None and wc.definition:
                return wc.definition
        return ""

    def topic_list(self):
        return sorted(self.topics.all(), key=lambda t: t.breadcrumb())

    def links(self):
        return self.link_set.all()

    def is_linked_to(self, resource_id, **kwargs):
        resource_id = int(resource_id)
        entry_id = kwargs.get("entryID") or None
        node_id = kwargs.get("nodeID") or None
        links = [l for l in self.links() if l.target_resource.id == resource_id]
        if not links:
            return False
        elif entry_id is None:
            return True
        else:
            for l in links:
                if l.target_id == entry_id and l.target_node == node_id:
                    return True
            return False

    def types(self):
        try:
            return self.tps
        except AttributeError:
            self.tps = []
            for wc in self.wordclasses():
                self.tps.extend(wc.types())
            return self.tps

    def is_obsolete(self):
        if not self.wordclasses():
            return False
        for wc in self.wordclasses():
            if not wc.obsolete:
                return False
        return True

    def obsolete(self):
        return self.is_obsolete()

    def update_alphasort(self):
        self.alphasort = alphasort(self.label)

    def to_json(self, **kwargs):
        from .lib.api.jsonconstructor import EntryJson
        return EntryJson(self).data(**kwargs)

    class Meta:
        ordering = ["alphasort",]


class Wordclass(models.Model, EntryMixin):
    """Wordclass subdivision (child of an Entry record)
    """
    datestamp = models.DateTimeField()
    entry = models.ForeignKey(Entry)
    penn = models.CharField(max_length=6)
    definition = models.CharField(max_length=60, blank=True, null=True)
    custom = models.TextField(blank=True, null=True)
    obsolete = models.BooleanField()

    def __unicode__(self):
        return "wordclass %s in entry #%d" % (self.penn, self.entry.id)

    def level(self):
        return "wordclass"

    def identifier(self):
        return self.label()

    def pos_description(self):
        return human_readable_pos(self.penn)

    def is_obsolete(self):
        return self.obsolete

    def types(self):
        try:
            return self.tps
        except AttributeError:
            self.tps = sorted(self.type_set.all(), key=lambda t: t.penn)
            if len(self.tps) == 1:
                self.tps[0].solo = True
            else:
                for t in self.tps:
                    t.solo = False
            return self.tps

    def contains_base_type(self):
        for t in self.types():
            if t.penn == self.penn:
                return True
        return False

    def type_rows(self):
        row_size = 3
        return [self.types()[i:i+row_size]
                for i in range(0, len(self.types()), row_size)]

    def parent_entry_id(self):
        return self.entry.id

    def label(self):
        return self.parent().label


class Type(models.Model, RecordMixin):
    """Inflected form + p.o.s (child of a Wordclass record)
    """
    datestamp = models.DateTimeField()
    wordclass = models.ForeignKey(Wordclass)
    form = models.CharField(max_length=50)
    penn = models.CharField(max_length=6)
    variant = models.CharField(max_length=1)
    custom = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "type %s_%s in wordclass #%d" % (self.form, self.penn,
                                                self.wordclass.id)

    def level(self):
        return "type"

    def identifier(self):
        return "%s_%s" % (self.form, self.penn,)

    def pos_description(self):
        return human_readable_pos(self.penn)

    def frequency_table(self):
        try:
            return self.freqtable_set.all()[0]
        except IndexError:
            return None

    def freq_table(self):
        return self.frequency_table()

    def mod_frequency(self):
        if self.freq_table() is None:
            return None
        else:
            return self.freq_table().tools().average_frequency(range=(1970, 2000))

    def frequency_list(self):
        if self.freq_table() is None:
            return None
        else:
            return self.freq_table().tools().data_list()

    def human_readable_variant(self):
        if self.variant == "s":
            return "standard spelling"
        elif self.variant == "v":
            return "variant spelling"
        elif self.variant == "u":
            return "US spelling"

    def parent_entry_id(self):
        return self.wordclass.entry.id


class FreqTable(models.Model, RecordMixin):
    """Frequency table, linked to a Type record
    """
    datestamp = models.DateTimeField()
    type = models.ForeignKey(Type, unique=True)
    f1750 = models.FloatField(null=True)
    f1760 = models.FloatField(null=True)
    f1770 = models.FloatField(null=True)
    f1780 = models.FloatField(null=True)
    f1790 = models.FloatField(null=True)
    f1800 = models.FloatField(null=True)
    f1810 = models.FloatField(null=True)
    f1820 = models.FloatField(null=True)
    f1830 = models.FloatField(null=True)
    f1840 = models.FloatField(null=True)
    f1850 = models.FloatField(null=True)
    f1860 = models.FloatField(null=True)
    f1870 = models.FloatField(null=True)
    f1880 = models.FloatField(null=True)
    f1890 = models.FloatField(null=True)
    f1900 = models.FloatField(null=True)
    f1910 = models.FloatField(null=True)
    f1920 = models.FloatField(null=True)
    f1930 = models.FloatField(null=True)
    f1940 = models.FloatField(null=True)
    f1950 = models.FloatField(null=True)
    f1960 = models.FloatField(null=True)
    f1970 = models.FloatField(null=True)
    f1980 = models.FloatField(null=True)
    f1990 = models.FloatField(null=True)
    f2000 = models.FloatField(null=True)

    def __unicode__(self):
        return "frequency table for type #%d" % (self.type.id,)

    def level(self):
        return "frequency table"

    def tools(self):
        from .lib.frequency.frequencytools import FrequencyTools
        try:
            return self.tls
        except AttributeError:
            self.tls = FrequencyTools(model_to_dict(self))
            return self.tls

    def parent_entry_id(self):
        return self.type.wordclass.entry.id


class Resource(models.Model, RecordMixin):
    """Details of any external resource linked from GEL2
    """
    title = models.CharField(max_length=100)
    label = models.CharField(max_length=30)
    homepage = models.CharField(max_length=100)
    url_template_entry = models.CharField(max_length=100)
    url_template_node = models.CharField(max_length=100)
    comment = models.CharField(max_length=100, blank=True, null=True)

    def num_links(self):
        return self.link_set.count()

    def level(self):
        return "resource"

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ["label",]


class Link(models.Model, RecordMixin):
    """Links a GEL2 entry to an entry or subentry in an external resource
    """
    entry = models.ForeignKey(Entry)
    target_resource = models.ForeignKey(Resource)
    target_id = models.CharField(max_length=30, db_index=True)
    target_node = models.CharField(max_length=30, blank=True, null=True)

    def __unicode__(self):
        if self.target_node is not None:
            return "link: %d to ../%s#%s" % (self.wordclass.id, self.target_id,
                                             self.target_node,)
        else:
            return "link: %d to ../%s" % (self.wordclass.id, self.target_id,)

    def level(self):
        return "link"

    def target(self):
        return self.target_resource.label

    def signature(self):
        return (self.target(), self.target_id,)

    def url(self):
        try:
            return self.urlval
        except AttributeError:
            if self.target_node is not None:
                self.urlval = self.target_resource.url_template_node\
                             .replace("{{ENTRYID}}", self.target_id)\
                             .replace("{{NODEID}}", self.target_node)
            else:
                self.urlval = self.target_resource.url_template_entry\
                             .replace("{{ENTRYID}}", self.target_id)
            self.urlval = self.urlval.strip("#")
            return self.urlval

    def html(self):
        return """
        <a href="%s" target="ext"
        title="external site: opens in new tab/window">
          %s <i class="icon-share-alt"></i>
        </a>
        """ % (self.url(), self.target(),)

    def parent_entry_id(self):
        return self.wordclass.entry.id


class CustomField(models.Model):
    """Stores parameters for any cutsom field defined by a user
    """
    LEVELS = [(l, l) for l in ("entry", "wordclass", "type")]
    TYPES = [(t, t) for t in ("text", "select", "boolean", "integer", "float",
             "url", "url template")]

    name = models.CharField(max_length=50)
    level = models.CharField(max_length=10, choices=LEVELS)
    type = models.CharField(max_length=20, choices=TYPES)
    default = models.CharField(max_length=100, blank=True, null=True)
    choices = models.CharField(max_length=200, blank=True, null=True)
    urltemplate = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    def options(self):
        if self.choices is None:
            return []
        else:
            return [j.strip() for j in self.choices.split("|")]


class ImportJob(models.Model):
    """Track progress and file locations for import jobs
    """
    name = models.CharField(max_length=100)
    initiated = models.DateTimeField()
    zip = models.FileField(upload_to="gel2import", null=True)
    validzip = models.BooleanField()
    csv = models.FileField(upload_to="gel2import", null=True)
    importstarted = models.DateTimeField(null=True)
    importcompleted = models.DateTimeField(null=True)
    results = models.CharField(max_length=300, null=True)

    def has_csv(self):
        return bool(self.csv)

    def is_running(self):
        if self.importstarted is not None and self.importcompleted is None:
            return True
        else:
            return False

    def zipname(self):
        if bool(self.zip):
            return self.zip.name.split("/")[-1]

    def csvname(self):
        if bool(self.csv):
            return self.csv.name.split("/")[-1]

    def status(self):
        if not self.validzip:
            return "invalid"
        elif self.importcompleted is not None:
            return "completed"
        elif self.importstarted is not None:
            return "running"
        elif not bool(self.csv):
            return "awaiting CSV"
        else:
            return "ready to import"

    def exit_log(self):
        if self.results is None:
            return []
        else:
            return self.results.split("|")
