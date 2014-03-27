
def find_record(level, id):
    """Given a record type and record ID, finds and retuns the
    corresponding record, or None if the record does not exist.

    find_record("entry", 14563)
    """
    try:
        id = int(id)
    except (ValueError, TypeError):
        return None

    level = level.lower()
    if level == "entry":
        from ..models import Entry
        j = Entry
    elif level == "wordclass":
        from ..models import Wordclass
        j = Wordclass
    elif level == "type":
        from ..models import Type
        j = Type
    elif level == "resource":
        from ..models import Resource
        j = Resource
    elif level == "link":
        from ..models import Link
        j = Link
    elif level == "topic":
        from ..models import Topic
        j = Topic
    elif level == "importjob":
        from ..models import ImportJob
        j = ImportJob
    else:
        return None

    try:
        return j.objects.get(id=id)
    except j.DoesNotExist:
        return None
