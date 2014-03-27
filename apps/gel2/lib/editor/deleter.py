
class Deleter(object):
    """Utility for deleting a record, including the recursive deletion
    of any child records (e.g. when deleting an entry, all child wordclasses,
    types, links, and frequency tables also get deleted).

    Usage: Deleter(record).delete()
    """

    def __init__(self, record):
        self.record = record

    def delete(self):
        # update the parent record's datestamp
        if self.record.parent() is not None:
            self.record.parent().bubble_save()
        # delete child records, then delete self.record itself
        if self.record.level() == "entry":
            self._delete_entry(self.record)
        elif self.record.level() == "wordclass":
            self._delete_wordclass(self.record)
        elif self.record.level() == "type":
            self._delete_type(self.record)

    def _delete_entry(self, record):
        # first delete any child wordclasses and links...
        for w in record.wordclasses():
            self._delete_wordclass(w)
        for l in record.links():
            self._delete_link(l)
        # ...delete the entry itself
        record.delete()

    def _delete_wordclass(self, record):
        # first delete any child types...
        for t in record.types():
            self._delete_type(t)
        # ...delete the wordclass itself
        record.delete()

    def _delete_type(self, record):
        # first delete the child frequency table, if any...
        if record.freq_table() is not None:
            self._delete_frequency_table(record.freq_table())
        # ...now delete the type itself
        record.delete()

    def _delete_frequency_table(self, record):
        record.delete()

    def _delete_link(self, record):
        record.delete()


class DeleteResource(object):
    """Utility for deleting a resource, including the deletion
    of all Link records pointing to that resource.

    Usage: DeleteResource(record).delete()
    """

    def __init__(self, record):
        self.record = record

    def delete(self):
        from ...models import Link
        Link.objects.filter(target_resource=self.record).delete()
        self.record.delete()
