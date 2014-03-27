#-------------------------------------------------------------------------------
# Name: PosMap
# Purpose:
#
# Author: James McCracken
#-------------------------------------------------------------------------------

maps = {
    "NN": ("n", "noun", "sb", "nf", "nm", "nsing", "singular", "sing"),
    "NNS": ("npl", "nplural", "plural", "pl"),
    "NP": ("npr", "prn", "propernoun"),
    "VB": ("v", "verb", "vb", "vi", "vt", "vrefl"),
    "JJ": ("adj", "a", "adjective", "pp", u"pr\u00e9t", "pret", "quantif",
           "modif", "modifier"),
    "RB": ("adv", "adverb"),
    "UH": ("int", "interjection", "excl", "exclamation"),
    "PP": ("pron", "pronoun"),
    "CC": ("conj", "conjunction"),
    "IN": ("prep", "preposition"),
}


class PosMap(object):
    reverse_map = {}

    def __init__(self, config):
        if not PosMap.reverse_map:
            self._parse_map()
        self.custom = {k.strip(): v.strip() for k, v in
                       config.items("posIndicators")}

    def _parse_map(self):
        for penn, vals in maps.items():
            for v in vals:
                PosMap.reverse_map[v] = penn

    def convert(self, pos):
        if not pos:
            return None
        elif pos.upper() in maps:
            return pos.upper()
        elif pos in self.custom:
            return self.custom[pos]

        pos = pos.split(",")[0].strip()
        if pos in self.custom:
            return self.custom[pos]

        pos = pos.lower().replace(".", "").replace(" ", "")
        if pos in self.custom:
            return self.custom[pos]
        elif pos in PosMap.reverse_map:
            return PosMap.reverse_map[pos]
        elif pos.startswith("v"):
            return "VB"
        elif pos.startswith("n"):
            return "NN"
        elif pos.startswith("a"):
            return "JJ"
        else:
            return None
