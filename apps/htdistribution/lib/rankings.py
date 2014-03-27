from collections import defaultdict

def rankings(element, **kwargs):
    """
    """
    clip = kwargs.get("clip")
    threshold = kwargs.get("threshold")

    rank = defaultdict(dict)
    for mode in ("fraction", "density",):
        for level, label in ((2, "two"), (3, "three"),):
            cs = element.rank_countsets(mode=mode, level=level)
            if threshold:
                cs = [c for c in cs if c.thesaurusclass.size >= threshold]
            if clip:
                cs = cs[:clip]
            rank[mode][label] = cs

    return rank
