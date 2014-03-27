
def check_for_missing_wordclass(qset):
    return [e for e in qset if not e.wordclasses()]

def check_for_missing_type(qset):
    qset2 = []
    for e in qset:
        if [wc for wc in e.wordclasses() if not wc.contains_base_type()]:
            qset2.append(e)
    return qset2

def check_for_duplicate_wordclass(qset):
    qset2 = []
    for e in qset:
        if len(set([wc.penn for wc in e.wordclasses()])) < len(e.wordclasses()):
            qset2.append(e)
    return qset2

def check_for_lemma_mismatch(qset):
    qset2 = []
    for e in qset:
        if e.wordclasses() and e.wordclasses()[0].penn == "NP":
            pass
        else:
            if not [t for t in e.types() if t.form == e.label]:
                qset2.append(e)
    return qset2
