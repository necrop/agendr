from ...models import ThesaurusClass

threshold = 200

def find_outliers(elements, level):
    element_ids = set([e.id for e in elements])
    classes = ThesaurusClass.objects.filter(level=level, size__gt=threshold)

    for e in elements:
        e.data = []

    for c in classes:
        csets = c.countset_set.filter(element__id__in=element_ids)
        cset_idx = {cset.element.id: cset for cset in csets}
        shares = []
        counts = []
        for e in elements:
            if e.id in cset_idx:
                shares.append(cset_idx[e.id].share(size=e.size))
                counts.append(cset_idx[e.id].branchtotal)
            else:
                shares.append(0)
                counts.append(0)
        c.mean = sum(shares) / len(shares)
        for e, share, count in zip(elements, shares, counts):
            if share > 0.01:
                if c.mean == 0:
                    ratio = 1
                else:
                    ratio = share / c.mean
                e.data.append((c, count, share, ratio))

    for e in elements:
        e.data.sort(key=lambda d: d[3], reverse=True)
        e.top = [d for d in e.data[0:5] if d[3] > 1]
        e.bottom = [d for d in e.data[-5:] if d[3] < 1]
        del(e.data)

    return elements
