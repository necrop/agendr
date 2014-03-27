
from collections import deque

entries_label = "gel2_entry_history"
searches_label = "gel2_search_history"
maxlen = 10

class History(object):

    def __init__(self, request):
        self.request = request
        self._initialize()

    def store_entry(self, entry):
        if entry.id in [e[0] for e in self.session[entries_label]]:
            return False
        else:
            k = self.session[entries_label]
            k.append((entry.id, entry.label,))
            self.session[entries_label] = k
            return True

    def store_search(self, query):
        sig = self._search_signature(query)
        if sig in [e[2] for e in self.session[searches_label]]:
            # don't store if a version of the search already exists in history
            return False
        elif self.request.GET.get("page") is not None:
            # don't store if the search is page=2, page=3, etc.
            return False
        else:
            k = self.session[searches_label]
            k.append((self.request.get_full_path(), query, sig,))
            self.session[searches_label] = k
            return True

    def list_history(self):
        return {"entries": self.session[entries_label],
                "searches": self.session[searches_label],}

    def _initialize(self):
        """Creates data structures for entries and searches
        in request.session, if they don't already exist.
        """
        if not entries_label in self.request.session:
            self.request.session[entries_label] = deque([], maxlen)
        if not searches_label in self.request.session:
            self.request.session[searches_label] = deque([], maxlen)
        self.session = self.request.session

    def _search_signature(self, lemma):
        """'Signature' composed of normalized parameters of the
        search form.

        This prevents the history from storing two versions of what's
        essentially the same search.
        """
        sig = lemma + "_"
        sig += "_".join(sorted(["%s=%s" % (key, value)
               for key, value in self.request.GET.items()
               if not key.startswith("csrf") and key != "page"]))
        return sig.lower()
