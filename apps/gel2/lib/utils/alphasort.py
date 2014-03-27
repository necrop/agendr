#-------------------------------------------------------------------------------
# Name: alphasort
# Purpose:
#
# Author: James McCracken
#-------------------------------------------------------------------------------

import re
from unidecode import unidecode

ready_simplified = re.compile(r"^[a-z]+$")

def alphasort(lemma):
    if ready_simplified.search(lemma):
        return lemma
    else:
        a = asciify(lemma).lower()
        a = re.sub(r"[^a-z]", "", a)
        return a

def asciify(lemma):
    j = lemma.replace(u"\u021d", "g") # Special handling of yogh
    j = j.replace(u"\u021c", "G") # ditto uppercase-yogh
    return unidecode(j)
