
from .loadcsv import rollback_csv
from ...editor.deleter import Deleter
from ...find_record import find_record

class Rollback(object):

    def __init__(self, job):
        self.job = job
        self.csvfile = job.csv.path

    def process(self):
        # Reset the job status
        self.job.importstarted = None
        self.job.importcompleted = None
        self.job.results = None
        self.job.save()

        # Rewrite the CSV file, and return a list of IDs for created links
        #  and entries logged in the CSV file
        links, entries = rollback_csv(self.csvfile)

        # Delete links
        for id in links:
            record = find_record("link", id)
            if record is not None:
                record.delete()

        # Delete entries (using the Deleter tool, since that will also
        #  delete any child records)
        for id in entries:
            record = find_record("entry", id)
            if record is not None:
                Deleter(record).delete()
