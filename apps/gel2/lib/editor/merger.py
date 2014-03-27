from ..find_record import find_record
from .deleter import Deleter


class Merger(object):

    def __init__(self, source, target):
        self.source = source
        self.target = target

    def merge(self):
        if self.source is not None and self.target is not None:
            self._transfer_wordclasses()
            self._transfer_links()
            self._delete_source()

    def _transfer_wordclasses(self):
        """Transfer wordclasses or wordclass contents to the target entry
        """
        for wordclass in self.source.wordclasses():
            target_wordclass = None
            for wc2 in self.target.wordclasses():
                if wordclass.penn == wc2.penn:
                    target_wordclass = wc2
            if target_wordclass is None:
                # simply move this wordclass to the new entry
                wordclass.entry = self.target
                wordclass.bubble_save()
            else:
                # merge this wordclass with its target (type by type)
                merge_types(wordclass, target_wordclass)

    def _transfer_links(self):
        """Transfer links to the target entry
        """
        for link in self.source.links():
            link.entry = self.target
            link.bubble_save()

    def _delete_source(self):
        """Delete the original entry
        """
        # We reload the source entry, to avoid possible contradictions
        #  when the child wordclasses and types get deleted (since
        #  some of these will already have been moved to the target
        #  entry)
        id = self.source.id
        self.source = find_record("entry", id)
        Deleter(self.source).delete()


def merge_types(wordclass1, wordclass2):
    for t1 in wordclass1.types():
        target = None
        for t2 in wordclass2.types():
            if t1.penn == t2.penn and t1.form == t2.form:
                target = t2
        if target is None:
            # simply move this type to the new wordclass
            t1.wordclass = wordclass2
            t1.bubble_save()
        elif (t1.frequency_table() is not None and
              target.frequency_table() is None):
            # transfer frequency table
            ft = t1.frequency_table()
            ft.type = target
            ft.bubble_save()
        elif t1.frequency_table() is not None:
            # transfer individual frequencies
            merge_frequencies(t1.frequency_table(), target.frequency_table())

def merge_frequencies(table1, table2):
    table2.tools().ingest(table1.tools())
    for year, datapoint in table2.tools().data().items():
        column = "f%d" % (year,)
        if datapoint.frequency <= 0:
            table2.__dict__[column] = None
        else:
            table2.__dict__[column] = datapoint.frequency
    table2.bubble_save()
