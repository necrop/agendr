from datetime import datetime
import os
from zipfile import ZipFile, is_zipfile

from ..find_record import find_record
from ...models import ImportJob


def register_new_job(args, uploaded_zip):
    if uploaded_zip is not None:
        new_job = ImportJob(name=args.get("name", "[unnamed]").strip(),
                            initiated=datetime.now(), zip=uploaded_zip,
                            validzip=True, csv=None, importstarted=None,
                            importcompleted=None, results=None)
        new_job.save()
        new_job.validzip = zip_is_valid(new_job.zip.path)
        new_job.save()

def delete_job(j):
    if j is not None:
        j.zip.delete()
        if bool(j.csv):
            j.csv.delete()
        j.delete()

def zip_is_valid(filepath):
    if is_zipfile(filepath):
        files = ZipFile(filepath).infolist()
        if ([f for f in files if f.filename.lower().endswith(".ini")] and
            [f for f in files if f.filename.lower().endswith(".xml")]):
            return True
        else:
            return False
    else:
        return False

def upload_csv(id, uploaded_csv):
    j = find_record("ImportJob", id)
    if j is not None:
        if bool(j.csv):
            j.csv.delete()
        j.csv = uploaded_csv
        j.save()

def rake():
    """Remove all import jobs, and clear out the uploads directory
    """
    import settings
    upload_path = None
    for f in ImportJob._meta.fields:
        try:
            upload_path = f.upload_to
        except AttributeError:
            pass
    upload_path = os.path.join(settings.MEDIA_ROOT, upload_path)
    # delete all import jobs
    ImportJob.objects.all().delete()
    # Clear out anything left in the uploads directory
    for f in os.listdir(upload_path):
        os.unlink(os.path.join(upload_path, f))
