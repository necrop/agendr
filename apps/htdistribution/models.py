import math
from django.db import models
from django.core.urlresolvers import reverse

oed_baseurl = "http://www.oed.com/"
element_types = [(t, t) for t in ("author", "title", "language", "compound")]

class ThesaurusClass(models.Model):
    label = models.CharField(max_length=100)
    level = models.IntegerField(db_index=True)
    count = models.IntegerField()
    superordinate = models.ForeignKey("self", null=True)
    size = models.IntegerField()
    originx = models.FloatField()
    originy = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    def breadcrumb(self):
        b = self.label
        if self.superordinate is not None:
            b = self.superordinate.breadcrumb() + u" \u00bb " + b
        return b

    def indented(self):
        def recurse(node, val):
            if node.superordinate is not None:
                val += u"\u00a0\u00a0\u00a0\u00a0"
                return recurse(node.superordinate, val)
            else:
                return val
        return recurse(self, u"") + self.breadcrumb()

    def is_leaf(self):
        if not self.topic_set.all():
            return True
        else:
            return False

    def oed_url(self):
        template = "%sview/th/class/%d"
        return template % (oed_baseurl, self.id)

    def centre(self):
        return (self.originx + (self.width * 0.5),
                self.originy + (self.height * 0.5))

    def center(self):
        return self.centre()

    def inner_rectangle(self):
        try:
            return self.inner_rect
        except AttributeError:
            self.inner_rect = ((self.originx + (self.width * 0.1),
                                self.originy + (self.height * 0.1),),
                                self.width * 0.8,
                                self.height * 0.8)
            return self.inner_rect

    def area(self):
        return self.width * self.height

    def inner_area(self):
        return self.inner_rectangle()[1] * self.inner_rectangle()[2]


class Element(models.Model):
    normalized_total = 10000

    alphasort = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, null=True)
    year = models.IntegerField(null=True)
    type = models.CharField(max_length=20, choices=element_types, db_index=True)
    oedidentifier = models.CharField(max_length=50)
    size = models.IntegerField()
    chistat2 = models.FloatField()
    pvalue2 = models.FloatField()
    chistat3 = models.FloatField()
    pvalue3 = models.FloatField()

    def __unicode__(self):
        return "%s (#%d)" % (self.label, self.id)

    def get_absolute_url(self):
        return reverse("htdistribution_element", kwargs={"id": str(self.id)})

    def oed_url(self):
        if self.type in ("author", "title"):
            template = "%sview/source/%s"
        elif self.type == "language":
            template ="%ssearch?scope=SENSE&langClass=%s"
        elif self.type == "compound":
            template = "%sview/Entry/%s"
        return template % (oed_baseurl, self.oedidentifier)

    def phi(self, level=2):
        if level == 2:
            return math.sqrt(float(self.chistat2) / self.size)
        elif level == 3:
            return math.sqrt(float(self.chistat3) / self.size)

    def countsets(self, **kwargs):
        tax_level = kwargs.get("level", None)
        if tax_level is None:
            csets = list(self.countset_set.all())
        else:
            csets = list(self.countset_set.filter(level=tax_level))
        if kwargs.get("addZeros"):
            # Add zero values for any classes not included so far
            included = set([cs.thesaurusclass.id for cs in csets])
            thesclasses = ThesaurusClass.objects.filter(level=tax_level).\
                          exclude(id__in=included)
            for c in thesclasses:
                null_cs = CountSet(element=self, thesaurusclass=c,
                    level=tax_level, majorsenses=0, minorsenses=0,
                    subentries=0, total=0, branchtotal=0)
                csets.append(null_cs)
        return csets

    def normalizing_ratio(self):
        try:
            return self.nd
        except AttributeError:
            if not self.size:
                self.nd = 1
            else:
                nd = float(Element.normalized_total) / float(self.size)
            return nd

    def rank_countsets(self, **kwargs):
        tax_level = kwargs.get("level", 3) # 2 or 3
        mode = kwargs.get("mode", "fraction") # 'fraction' or 'density'
        threshold = kwargs.get("threshold", 100) # threshold for small classes
        skip_small_classes = kwargs.get("skipSmallClasses", False)
        csets = self.countsets(level=tax_level, addZeros=True)
        if mode in ("share", "fraction"):
            csets = sorted(csets, key=lambda c: c.share(size=self.size), reverse=True)
        elif mode == "density":
            csets = sorted(csets, key=lambda c: c.density(), reverse=True)
        if skip_small_classes:
            csets = [c for c in csets if c.thesaurusclass.size > threshold]
        return csets

    class Meta:
        ordering = ["alphasort",]


class CountSet(models.Model):
    element = models.ForeignKey(Element)
    thesaurusclass = models.ForeignKey(ThesaurusClass)
    level = models.IntegerField(db_index=True)
    majorsenses = models.IntegerField()
    minorsenses = models.IntegerField()
    subentries = models.IntegerField()
    total = models.IntegerField()
    branchtotal = models.IntegerField()

    def density(self):
        try:
            return self.dty
        except AttributeError:
            self.dty = float(self.branchtotal) / float(self.thesaurusclass.size)
            return self.dty

    def density_normalized(self, **kwargs):
        try:
            return self.dty_norm
        except AttributeError:
            ratio = kwargs.get("ratio", None)
            if ratio is not None:
                self.dty_norm = self.density() * ratio
            else:
                self.dty_norm = self.density() * self.element.normalizing_ratio()
            return self.dty_norm

    def share(self, **kwargs):
        try:
            return self.sh
        except AttributeError:
            size = kwargs.get("size") or self.element.size
            if not size:
                self.sh = float(0)
            else:
                self.sh = float(self.branchtotal) / float(size)
            return self.sh

    def fraction(self, **kwargs):
        return self.share(**kwargs)

    def __unicode__(self):
        return "%s -> %s: %d" % (self.element.label,
            self.thesaurusclass.label, self.total)


class Collection(models.Model):
    label = models.CharField(max_length=100)
    alphasort = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=20, choices=element_types)
    elements = models.ManyToManyField(Element)

    def get_absolute_url(self):
        return reverse("htdistribution_collection", kwargs={"id": str(self.id)})

    def compute_alphasort(self):
        return self.label.lower().replace("-", "").replace(" ", "")\
            .replace(",", "")

    def complement(self):
        element_ids = set([e.id for e in self.elements.all()])
        return Element.objects.filter(type=self.type).\
            exclude(id__in=element_ids)

    def members(self):
        return ", ".join([e.label for e in self.elements.all()])

    def __unicode__(self):
        return "%s (%s)" % (self.label, self.type)

    class Meta:
        ordering = ["alphasort",]


