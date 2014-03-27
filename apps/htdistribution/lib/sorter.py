
def element_sorter(request, elements):
    """Sort a list of elements according to request.GET parameters
    """
    sort_order = request.GET.get("sort", None)
    reverse = request.GET.get("reverse", None)
    if sort_order is not None:
        try:
            # Sort in SQL; this will only work if the list is a QuerySet...
            elements = list(elements.order_by(sort_order))
        except AttributeError:
            # ... otherwise, fall back on Python sorting
            elements.sort(key=lambda e: e.__dict__[sort_order])

        if reverse and sort_order in ("alphasort", "gender", "year"):
            elements.reverse()
        if not reverse and sort_order in ("size", "skew2", "skew3"):
            elements.reverse()

    return list(elements)
