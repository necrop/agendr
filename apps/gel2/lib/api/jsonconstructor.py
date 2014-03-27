import json

class BaseJson(object):

    def __init__(self, object):
        self.object = object

    def fields(self):
        f = dict(self.core_list())
        f.update(self.custom_list())
        return f

    def core_list(self):
        return {}

    def custom_list(self):
        custom = {}
        for f in self.object.custom_parsed():
            if f.type == "url" or f.type == "url template":
                custom[f.name] = f.compiled_url()
            else:
                custom[f.name] = f.value
        return custom

    def to_json(self, **kwargs):
        return json.dumps(self.data(**kwargs))

    def mod_frequency(self):
        if self.object.mod_frequency() is None:
            return None
        else:
            return significant_digits(self.object.mod_frequency(), 2)

    def frequency_table(self):
        if self.object.level() == "type":
            if self.object.frequency_list() is not None:
                return self.object.frequency_list()
            else:
                return []
        elif self.object.summed_frequency() is not None:
            return [(year, significant_digits(f, 2)) for year, f in
                    self.object.summed_frequency().data_list()]
        else:
            return []


class EntryJson(BaseJson):

    def data(self, **kwargs):
        d = {"id": self.object.id, "fields": self.fields(),
             "wordclasses": self.wordclasses(**kwargs)}
        if kwargs.get("includeFrequency", False) == True:
            d["frequencyTable"] = self.frequency_table()
        if kwargs.get("includeLinks", False) == True:
            d["links"] = self.links()
        if kwargs.get("includeTopics", True) == True:
            d["topics"] = self.topics()
        return d

    def core_list(self):
        return {
            "lemma": self.object.label,
            "definition": self.object.definition(),
            "soundfile_us": self.object.soundfile_us,
            "soundfile_uk": self.object.soundfile_uk,
            "obsolete": self.object.is_obsolete(),
            "frequency": self.mod_frequency(),
        }

    def wordclasses(self, **kwargs):
        return [WordclassJson(w).data(**kwargs) for w in self.object.wordclasses()]

    def links(self):
        return [{"resource": l.target(), "entryID": l.target_id,
                "nodeID": l.target_node, "url": l.url(),}
                for l in self.object.links()]

    def topics(self):
        return [{"id": t.id, "label": t.name, "breadcrumb": t.breadcrumb()}
                for t in self.object.topic_list()]


class WordclassJson(BaseJson):

    def data(self, **kwargs):
        d = {"id": self.object.id, "fields": self.fields(),}
        if kwargs.get("includeTypes", False) == True:
            d["types"] = self.types(**kwargs)
        if kwargs.get("includeFrequency", False) == True:
            d["frequencyTable"] = self.frequency_table()
        return d

    def core_list(self):
        return {
            "penn": self.object.penn,
            "definition": self.object.definition,
            "obsolete": self.object.is_obsolete(),
            "frequency": self.mod_frequency(),
        }

    def types(self, **kwargs):
        return [TypeJson(t).data(**kwargs) for t in self.object.types()]


class TypeJson(BaseJson):

    def data(self, **kwargs):
        d = {"id": self.object.id, "fields": self.fields(),}
        if kwargs.get("includeFrequency", False) == True:
            d["frequencyTable"] = self.frequency_table()
        return d

    def core_list(self):
        return {
            "penn": self.object.penn,
            "form": self.object.form,
            "variant": self.object.human_readable_variant(),
            "frequency": self.mod_frequency(),
        }




def significant_digits(val, digits):
    digits = int(digits)
    formatter = "%0." + str(digits) + "g"
    return float(formatter % (val,))
