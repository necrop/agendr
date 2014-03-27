from ...models import Element, Collection
from ..charts.colors import add_colors

def anonymous_url(base_url, post):
    setname = post.get("setname", "author")
    ids, idlist = build_idlist(post)
    if len(ids) > 1:
        return "%s/collection/anon/%s" % (base_url, idlist)
    else:
        return "%s/collection/fail?type=%s" % (base_url, setname)

def save_collection(base_url, post):
    label = post.get("label", "unnamed")
    description = post.get("description", None) or None
    setname = post.get("setname", "author")
    idlist = post.get("idlist", "")
    elements = collection_elements(idlist)
    if elements:
        setname = elements[0].type
    coll = Collection(label=label, description=description, type=setname)
    coll.alphasort = coll.compute_alphasort()
    coll.save() # has to be saved once before elements can be added
    coll.elements = elements
    coll.save() # ...then saved again with elements
    return "%s/collection/%d" % (base_url, coll.id)

def collection_elements(idlist):
    """Retrieve the set of elements (as an alpha-sorted list) corresponding
    to a hyphen-separated string of IDs
    """
    elements = []
    ids = [int(id) for id in idlist.split("-")]
    elements = list(Element.objects.filter(id__in=ids))
    elements = add_colors(elements)
    return elements

def update_collection(post):
    collection_id = int(post.get("id", 0))
    element_ids, element_idlist = build_idlist(post)
    additions = [int(a) for a in post.getlist("additions")]

    coll = Collection.objects.get(id=collection_id)
    coll.label = post.get("label", "unnamed")
    coll.description = post.get("description") or None
    coll.alphasort = coll.compute_alphasort()
    coll.elements = collection_elements(element_idlist)

    for a in additions:
        try:
            e = Element.objects.get(id=a)
        except Element.DoesNotExist:
            pass
        else:
            coll.elements.add(e)

    coll.save()

def build_idlist(post):
    ids = []
    for k in [k.replace("element_", "") for k in post.keys()
              if k.startswith("element_") and post[k] == "on"]:
        try:
            int(k)
        except ValueError:
            pass
        else:
            ids.append(k)
    return (ids, "-".join(sorted(ids)))

