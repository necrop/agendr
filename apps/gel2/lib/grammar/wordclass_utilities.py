

main_wordclasses = ("NN", "NNS", "JJ", "VB", "RB", "NP", "CC", "IN",
    "UH", "PP", "PP$")

base_descriptors = {"NN": "noun", "JJ": "adjective", "VB": "verb",
    "NP": "proper name", "NNS": "plural noun", "RB": "adverb",
    "CC": "conjunction", "UH": "interjection",
    "IN": "preposition", "PP": "personal pronoun", "PP$": "possessive pronoun"}

detailed_descriptors = {"NN": "singular", "NNS": "plural", "NP": "proper name",
    "JJ": "positive adjective", "JJR": "comparative adjective",
    "JJS": "superlative adjective", "RB": "positive adverb",
    "RBR": "comparative adverb", "RBS": "superlative adverb",
    "VB": "infinitive", "VBZ": "3rd-person present",
    "VBG": "present participle", "VBD": "past", "VBN": "past participle"}

inflections = {"NN": ("NN", "NNS"),
    "JJ": ("JJ", "JJR", "JJS"),
    "RB": ("RB", "RBR", "RBS"),
    "VB": ("VB", "VBZ", "VBG", "VBD", "VBN"),}


def human_readable_pos(pos, mode=None):
    if mode is None or mode is "base":
        try:
            return base_descriptors[pos]
        except KeyError:
            return pos
    else:
        try:
            return detailed_descriptors[pos]
        except KeyError:
            try:
                return base_descriptors[pos]
            except KeyError:
                return pos

def inflections_for_wordclass(wordclass):
    try:
        return inflections[wordclass]
    except KeyError:
        return (wordclass,)
