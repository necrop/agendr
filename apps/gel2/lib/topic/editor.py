
from ...models import Topic
from ..find_record import find_record

class Editor(object):

    def __init__(self, args):
        self.args = {k: v.strip() for k, v in args.items()}
        self.id = int(self.args.get("id", 0))
        self.action = self.args.get("action")

    def execute(self):
        self.node = find_record("topic", self.id)
        if self.node is None:
            pass
        elif self.action == "edit":
            self._edit()
        elif self.action == "move":
            self._move()
        elif self.action == "add":
            self._add()
        elif self.action == "delete":
            self._delete()

    def _edit(self):
        if self.args.get("name"):
            self.node.name = self.args.get("name")
        if self.args.get("description"):
            self.node.description = self.args.get("description")
        else:
            self.node.description = None
        self.node.save()

    def _move(self):
        if self.args.get("parent") == "root":
            self.node.superordinate = None
            self.node.save()
        else:
            new_parent = find_record("topic", self.args.get("parent"))
            if new_parent is not None and new_parent.id != self.id:
                self.node.superordinate = new_parent
                self.node.save()

    def _add(self):
        if self.args.get("newName"):
            if self.args.get("newDescription"):
                desc = self.args.get("newDescription")
            else:
                desc = None
            Topic(
                name=self.args.get("newName"),
                description=desc,
                superordinate=self.node,
            ).save()


    def _delete(self):
        self.node.delete()

