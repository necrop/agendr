#-------------------------------------------------------------------------------
# Name: inflection
# Purpose:
#
# Author: James McCracken
#-------------------------------------------------------------------------------

import re

from ..utils.regexcompiler import ReplacementListCompiler

inf_rx = {
    "VBZ": ReplacementListCompiler((
        (r"([sxz]|sh|ch)$", r"\1es"),
        (r"([^aeiou])y$", r"\1ies"),
        (r"$", r"s"))),
    "VBG": ReplacementListCompiler((
        (r"e$", r"ing"),
        (r"([bcdfghlmnprstvwz][aeiou])([bdfglmnpstz])$", r"\1\2\2ing"),
        (r"([bcdfghlmnprstvwz][aiou])r$", r"\1rring"),
        (r"$", r"ing"))),
    "VBD": ReplacementListCompiler((
        (u"(e|\u00e9)$", r"\1d"),
        (r"([^aeiou])y$", r"\1ied"),
        (r"([bcdfghlmnprstvwz][aeiou])([bdfglmnpstz])$", r"\1\2\2ed"),
        (r"([bcdfghlmnprstvwz][aiou])r$", r"\1rred"),
        (r"$", r"ed"))),
    "NNS": ReplacementListCompiler((
        (r"([aoy])sis$", r"\1ses"),
        (r"thesis$", r"theses"),
        (r"ix$", r"ices"),
        (r"man$", r"men"),
        (r"person$", r"people"),
        (r"childe?$", r"children"),
        (r"tooth$", r"teeth"),
        (r"goose$", r"geese"),
        (r"foot$", r"feet"),
        (r"sheep$", r"sheep"),
        (r"mouse$", r"mice"),
        (r"zoon$", r"zoa"),
        (r"eau$", r"eaux"),
        (r"(l|w|kn)ife$", r"\1ives"),
        (r"lf$", r"lves"),
        (r"eaf$", r"eaves"),
        (r"([^\'][sxz]|sh|ch)$", r"\1es"),
        (r"([^aeiou])y$", r"\1ies"),
        (r"([^A-Z' 0-9.,?!-])$", r"\1s"))),
    "JJR": ReplacementListCompiler((
        (r"e$", r"er"),
        (r"([^aeiou])y$", r"\1ier"),
        (r"([bcdfghlmnprstvwz][aeiou])([bdfglmnpstz])$", r"\1\2\2er"),
        (r"([bcdfghlmnprstvwz][aiou])r$", r"\1rrer"),
        (r"$", r"er"))),
    "JJS": ReplacementListCompiler((
        (r"e$", r"est"),
        (r"([^aeiou])y$", r"\1iest"),
        (r"([bcdfghlmnprstvwz][aeiou])([bdfglmnpstz])$", r"\1\2\2est"),
        (r"([bcdfghlmnprstvwz][aiou])r$", r"\1rrest"),
        (r"$", r"est")))
}
inf_rx["RBR"] = inf_rx["JJR"]
inf_rx["RBS"] = inf_rx["JJS"]
inf_rx["VBN"] = inf_rx["VBD"]

compound_rx = re.compile(r"^([^ -]+)([ -](of|in|with)[ -].*|-general)$", re.I)
phrasal_vb_rx = re.compile(r"^(.{3,})([ -](up|down|back|away|in|out|off|on|to|for|by|after|against|again|with|upon))$")
verbals = ("VBZ", "VBD", "VBN", "VBG")


class Inflection(object):
    """Engine to manage various ways to inflect a lemma.

    No arguments.
    """

    def __init__(self):
        pass

    def compute_inflection(self, lemma, wordclass):
        """Compute the inflection of a lemma, for a given wordclass.

        Wordclass should use one of the following Penn Treebank codes:
        NNS, VBZ, VBG, VBN, VBD, JJR, JJS, RBR, RBS

        If anything other than a string is passed as the first argument, or
        a non-valid wordclass is passed as the second argument, the lemma
        is returned unchanged.

        Arguments:
        1. lemma (string)
        2. wordclass (Penn Treebank code, e.g. "NNS")

        Returns a string representing the inflected form.
        """
        wordclass = wordclass.strip().upper()
        inf = lemma
        if wordclass == "NNS":
            inf = self.pluralize(lemma)
        else:
            tail = ""
            if wordclass in verbals:
                match = phrasal_vb_rx.search(lemma)
                if match is not None:
                    lemma, tail = match.group(1, 2)
            try:
                inf = inf_rx[wordclass].edit_once(lemma)
                inf = inf + tail
            except KeyError:
                pass
        return inf

    def pluralize(self, lemma):
        """Return the plural of a singular noun.

        Returns a pluralized string
        """
        tail = ""
        cmatch = compound_rx.search(lemma)
        if cmatch is not None:
            lemma = cmatch.group(1)
            tail = cmatch.group(2)
        inf = inf_rx["NNS"].edit_once(lemma)
        return inf + tail

