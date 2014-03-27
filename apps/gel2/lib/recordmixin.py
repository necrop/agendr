from datetime import datetime, timedelta
from collections import defaultdict


class RecordMixin(object):
    """Mixin class used for Entry, Wordclass, Type, Link, and FreqTable models.
    """

    def parent(self):
        """Returns the parent record.

        E.g. if self is a Wordclass record, returns the parent Entry record.
        """
        try:
            return self.parent_record
        except AttributeError:
            if self.level() == "entry":
                self.parent_record = None
            elif self.level() == "link":
                self.parent_record = self.entry
            elif self.level() == "wordclass":
                self.parent_record = self.entry
            elif self.level() == "type":
                self.parent_record = self.wordclass
            elif self.level() == "frequency table":
                self.parent_record = self.type
            else:
                self.parent_record = None
            return self.parent_record

    def bubble_save(self, **kwargs):
        """Updates the timestamp and saves the record; also updates the
        datestamp on parent records.

        E.g. when saving a type-level record, also updates the datestamp
        on the parent wordclass record and the parent entry record.
        """
        datestamp_only = kwargs.get("datestampOnly", False)
        self.datestamp = datetime.now() - timedelta(seconds=1)
        if datestamp_only:
            self.save(update_fields=["datestamp",])
        else:
            self.save()
        if self.parent() is not None:
            self.parent().bubble_save(datestampOnly=True)

    def dated_save(self):
        """Updates the timestamp and saves the record
        """
        self.datestamp = datetime.now() - timedelta(seconds=1)
        self.save()

    def custom_parsed(self):
        from .custom.customparser import CustomParser
        return CustomParser(self.level(), self.custom).fields()

    def clean_values(self, vals):
        """Coerce a dictionary of values into the appropriate form for
        the model.
        """
        vals = {k: v or None for k, v in vals.items()}
        for k, v in vals.items():
            if v is not None:
                try:
                    v = v.strip()
                except AttributeError:
                    pass
                else:
                    # Trim to the right length (based on the max_length
                    # attribute of the corresponding model field)
                    matches = [f.max_length for f in self._meta.fields
                               if f.name == k]
                    if matches and matches[0] is not None:
                        v = v[:matches[0]]
            vals[k] = v
        return vals



class EntryMixin(RecordMixin):
    """Mixin class used for Entry and Wordclass models
    """

    def mod_frequency(self, **kwargs):
        if self.summed_frequency() is None:
            if kwargs.get("zeroed") == True:
                return float(0)
            else:
                return None
        else:
            return self.summed_frequency().average_frequency(range=(1970, 2000))

    def summed_frequency(self):
        from .frequency.frequencytools import FrequencyTools
        try:
            return self.virtual_freq_table
        except AttributeError:
            tables = [t.freq_table() for t in self.types()
                      if t.freq_table() is not None]
            if tables:
                summed = defaultdict(lambda: 0)
                for t in tables:
                    for year, val in t.tools().data().items():
                        summed[year] += val.frequency
                self.virtual_freq_table = FrequencyTools(summed)
            else:
                self.virtual_freq_table = None
            return self.virtual_freq_table

