from ...models import Resource

def resource_list(record):
    resources = []
    for r in Resource.objects.all():
        res = ResourceData(resourceid=r.id, label=r.label, entryid=None,
                           nodeid=None, linkid=None, resource_record=r)
        for l in record.links():
            if l.target_resource.id == r.id:
                res.entryid = l.target_id
                res.nodeid = l.target_node
                res.linkid = l.id
        resources.append(res)
    return resources


class ResourceData(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v
