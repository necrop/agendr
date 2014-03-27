
from datetime import datetime

from ..examinezip import examine_zip
from .loadcsv import load_csv, update_csv
from ...find_record import find_record
from ...editor.execute import ResourceEdit, RecordAdd
from ....models import Resource, Link

class AddToDB(object):

    def __init__(self, job):
        self.job = job
        self.csvfile = job.csv.path
        config, xml_files = examine_zip(job.zip.path)
        self.config = config

    def process(self):
        self.new_links, self.new_entries = load_csv(self.csvfile)
        self._register_resource()
        if self.target_resource is not None:
            self._add_new_links()
            self._add_new_entries()
        else:
            # some kind of catastrophic failure: no resource to link stuff to
            pass

        update_csv(self.csvfile, self.new_links, self.new_entries)
        self.job.results = self._readable_results()
        self.job.importcompleted = datetime.now()
        self.job.save()


    def _register_resource(self):
        bibdata = {}
        for key, value in self.config.items("resourceDetails"):
            if value.lower() == "none" or not value:
                value = None
            bibdata[key.lower()] = value

        if bibdata.get("id") is not None:
            try:
                id = int(bibdata.get("id"))
            except ValueError:
                id = None
        else:
            id = None
        label = bibdata.get("shorttitle")

        self.target_resource = None
        for r in Resource.objects.all():
            if id == r.id or label == r.label:
                self.target_resource = r
        if self.target_resource is None:
            args = {"action": "add", "level": "resource", "comment": None,
                    "label": label}
            args["title"] = bibdata.get("fulltitle") or None
            args["homepage"] = bibdata.get("homepage") or None
            args["url_template_entry"] = bibdata.get("urltemplateentry") or None
            args["url_template_node"] = bibdata.get("urltemplatenode") or None
            self.target_resource = ResourceEdit(args).implement()

    def _add_new_links(self):
        for l in self.new_links:
            record = find_record("entry", l.recordID)
            if record is not None:
                # Check if the record already has this link
                if record.is_linked_to(self.target_resource.id,
                                       entryID=l.entryID,
                                       nodeID=l.nodeID or None):
                    l.status = "redundant"
                else:
                    new_link = Link(
                        entry=record,
                        target_resource=self.target_resource,
                        target_id=l.entryID,
                        target_node=l.nodeID or None
                    )
                    new_link.save()
                    record.bubble_save()
                    l.status = "link created (ID %d)" % (new_link.id,)
            else:
                l.status = "failed (record not found)"

    def _add_new_entries(self):
        for e in self.new_entries:
            if e.lemma is not None and e.lemma:
                args = {"action": "add", "level": "root", "generate": True}
                args["label"] = e.lemma
                args["penn"] = e.wordclass or "NN"
                args["definition"] = e.definition or None
                args["obsolete"] = False
                record = RecordAdd(args).implement()
                if record is not None:
                    new_link = Link(
                        entry=record,
                        target_resource=self.target_resource,
                        target_id=e.entryID,
                        target_node=e.nodeID or None
                    )
                    new_link.save()
                    e.status = "entry created (ID %d)" % (record.id,)
                else:
                    e.status = "failed (could not create entry)"
            else:
                e.status = "failed (lemma not defined)"

    def _readable_results(self):
        results = {
            "links": {
                "created": len([l for l in self.new_links
                                if l.status.startswith("link created")]),
                "failed": len([l for l in self.new_links
                               if l.status.startswith("failed")]),
                "redundant": len([l for l in self.new_links
                                  if l.status.startswith("redundant")]),
            },
            "entries": {
                "created": len([l for l in self.new_entries
                                if l.status.startswith("entry created")]),
                "failed": len([l for l in self.new_entries
                               if l.status.startswith("failed")]),
            }
        }
        lines = []
        for k, vals in sorted(results.items()):
            l = k.capitalize() + ": " + "; ".join(["%s=%d" % (j, v)
                for j, v in sorted(vals.items())])
            lines.append(l)
        return "|".join(lines)
