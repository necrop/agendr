#-------------------------------------------------------------------------------
# Name: DictEntry
# Purpose:
#
# Author: James McCracken
#-------------------------------------------------------------------------------

from ...utils.alphasort import alphasort

class DictEntry(object):

    def __init__(self, entryid, nodeid, lemma, blocks):
        self.entryid = entryid
        self.nodeid = nodeid
        self.lemma = lemma or ""
        self.blocks = blocks

    def alphasort(self):
        try:
            return self.asort
        except AttributeError:
            self.asort = alphasort(self.lemma)
            return self.asort

    def type(self):
        if self.nodeid is None:
            return "subentry"
        else:
            return "entry"

    def wordclasses(self):
        return set([b[0] for b in self.blocks])
