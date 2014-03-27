from django.db.models import Q
from ..models import Element, Collection

def search_url(base_url, query):
    query = query.strip().replace("  ", " ")
    return "%s/searchresults/%s" % (base_url, query)

def results(query):
    if not query:
        return ([], [])
    else:
        elements = Element.objects.filter( Q(label__icontains=query) |
            Q(alphasort__icontains=query))
        collections = Collection.objects.filter( Q(label__icontains=query) |
            Q(alphasort__icontains=query))
        return (elements, collections)
