#-------------------------------------------------------------------------------
# Name: analyse
# Purpose:
#
# Author: James McCracken
#-------------------------------------------------------------------------------

from django.core.files.uploadedfile import SimpleUploadedFile

from ..examinezip import examine_zip
from .fileparser import FileParser
from .matcher import match_entries_to_records
from .generatecsv import generate_csv


def analyse(importjob):
    config, xml_files = examine_zip(importjob.zip.path)
    if config is not None and xml_files:
        filename = "job-%d.csv" % (importjob.id,)
        importjob.csv = SimpleUploadedFile(filename, "")
        importjob.save()

        fparser = FileParser(config)
        fparser.parse(xml_files)
        match_entries_to_records(fparser.entries)
        generate_csv(config, fparser.entries, importjob.csv.path)
