
from ...models import Topic
from ..find_record import find_record

class Taxonomy(object):
    topix = []

    def __init__(self):
        pass

    def topics(self):
        if not Taxonomy.topix:
            Taxonomy.topix = sorted(Topic.objects.all(),
                                    key=lambda t: t.breadcrumb())
        return Taxonomy.topix

    def find_topic(self, id):
        try:
            id = int(id)
        except ValueError:
            # In case the argument is actually the topic name, not its ID
            matches = [t for t in self.topics()
                       if t.name.lower() == id.lower()]
            if matches:
                id = matches[0].id
            else:
                id = None
        return find_record("topic", id)

    def list_branch(self, id):
        parent = self.find_topic(id)
        if parent is None:
            return set()
        else:
            branch = set([parent.id])
            for t in self.topics():
                if (t.superordinate is not None and
                    (t.superordinate == parent or
                     t.superordinate.superordinate == parent)):
                    branch.add(t.id)
            return branch
