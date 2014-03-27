#-------------------------------------------------------------------------------
# Name: match_entries
# Purpose:
#
# Author: James McCracken
#-------------------------------------------------------------------------------

from ....models import Entry

def match_entries_to_records(entries):
    records_matched = set()

    for e in entries:
        qset = Entry.objects.filter(alphasort=e.alphasort())
        results = [r for r in qset if not r.is_obsolete() and
                   comparable_lemmas(e.lemma, r.label) and
                   not r.id in records_matched]

        # filter for results with at least one matching part-of-speech
        filtered = [r for r in results if shared_parts(e, r)]
        # ...but allow non-matching parts-of-speech as long as the
        #  lemmas match exactly, and are relatively long
        if not filtered and len(e.lemma) > 8:
            filtered = [r for r in results if e.lemma == r.label]

        # filter for exactly matching lemmas
        filtered2 = [r for r in filtered if r.label == e.lemma]
        if filtered2:
            filtered = filtered2

        if len(filtered) == 1:
            target = filtered[0]
        elif len(filtered) > 1:
            score_candidates(e, filtered)
            filtered.sort(key=lambda r: r.score, reverse=True)
            target = filtered[0]
        else:
            target = None

        if target is not None:
            records_matched.add(r.id)
            e.match = (str(target.id), target.label, target.definition())
        else:
            e.match = None
        e.alternatives = max((0, len(filtered)-1))


def shared_parts(entry, record):
    return len([wc for wc in entry.wordclasses()
                if record.contains_wordclass(wc)])

def comparable_lemmas(l1, l2):
    def hyphen_position(lemma):
        if lemma.startswith("-"):
            return "start"
        elif lemma.endswith("-"):
            return "end"
        else:
            return "nada"

    def space_position(lemma):
        lemma = lemma.replace("-", " ")
        return (lemma.count(" "), lemma.find(" "))

    if hyphen_position(l1) != hyphen_position(l2):
        return False
    if (space_position(l1)[0] == space_position(l2)[0] and
        space_position(l1)[1] != space_position(l2)[1]):
        return False
    if l1.isupper() != l2.isupper():
        return False
    return True

def score_candidates(e, candidate_records):
    def strip_spaces(lemma):
        return lemma.replace(" ", "").replace("-", "")

    for r in candidate_records:
        score = 0
        if r.label == e.lemma:
            score += 2
        elif strip_spaces(r.label) == strip_spaces(e.lemma):
            score += 1
        score += shared_parts(e, r)
        score += r.mod_frequency()
        r.score = score
