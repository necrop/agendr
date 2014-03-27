from ...models import Entry, Topic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta

from ..find_record import find_record

results_per_page = 20


class ResultsList(object):

    def __init__(self, request, **kwargs):
        self.args = kwargs
        self.params = {k.lower(): v for k, v in request.GET.items()}
        for k in self.params:
            if k.endswith("reverse") and self.params[k] == "on":
                self.params[k] = True
        self.out_of_range = False
        try:
            self.page_num = int(self.params.get("page", 1))
        except ValueError:
            self.page_num = 1

    def list_results(self):
        lemma = (self.args.get("lemma") or
                 self.params.get("lemma") or
                 self.params.get("query") or
                 "").strip().lower().replace(" ", "")
        if len(lemma.split("-", 1)) == 2:
            lemma_from, lemma_to = lemma.split("-", 1)
        elif lemma.endswith("*"):
            lemma_from = lemma.replace("*", "")
            lemma_to = lemma.replace("*", "") + "zz"
        else:
            lemma_from, lemma_to = (None, None)

        # Initial query-set based on lemma
        if not lemma or lemma == "a-zzz":
            qset = Entry.objects.all()
        elif lemma_from is not None:
            qset = Entry.objects.filter(alphasort__gte=lemma_from,
                                        alphasort__lte=lemma_to,)
        else:
            qset = Entry.objects.filter(alphasort=lemma)

        # Filter by date/time (lastedited)
        if self.params.get("lastedited") is not None :
            delta = int(self.params.get("lastedited"))
            cutoff = datetime.now() - timedelta(minutes=delta)
            qset = qset.filter(datestamp__gte=cutoff)

        # Filter by obs status
        if self.params.get("status") == "obs":
            qset = qset.exclude(wordclass__obsolete=False)
        elif self.params.get("status") == "current":
            qset = qset.filter(wordclass__obsolete=False)

        # Filter by wordclass
        if (self.params.get("wordclass") is not None and
            self.params.get("wordclassreverse") == True):
            qset = qset.exclude(wordclass__penn=self.params.get("wordclass"))
        elif self.params.get("wordclass") is not None:
            qset = qset.filter(wordclass__penn=self.params.get("wordclass"))

        # Filter by what the entry links to
        if self.params.get("linkedto") == "unlinked":
            qset = qset.filter(link__isnull=True)
        elif (self.params.get("linkedto") is not None and
              self.params.get("linkedreverse") == True):
            qset = qset.exclude(link__target_resource__id=self.params.get("linkedto"))
        elif self.params.get("linkedto") is not None:
            qset = qset.filter(link__target_resource__id=self.params.get("linkedto"))

        # Filter by topic/taxonomy branch
        if self.params.get("topic") is not None:
            branch = topic_branch(self.params.get("topic"))
            if branch:
                qset = qset.filter(topics__id__in=list(branch))

        # Filter by link target ID (not used in regular search, but
        #   used by the API)
        if (self.params.get("targetentry") is not None and
            self.params.get("targetnode") == "null"):
            # If targetNode is explicitly set to 'null', only return
            # mathes for links where entryNode is not set
            qset = qset.filter(
                link__target_id=self.params.get("targetentry"),
                link__target_node__isnull=True,
            )
        elif (self.params.get("targetentry") is not None and
              self.params.get("targetnode") is not None):
            qset = qset.filter(
                link__target_id=self.params.get("targetentry"),
                link__target_node=self.params.get("targetnode"),
            )
        elif self.params.get("targetentry") is not None:
            qset = qset.filter(
                link__target_id=self.params.get("targetentry"),
            )
        elif self.params.get("targetnode") is not None:
            qset = qset.filter(
                link__target_node=self.params.get("targetnode"),
            )

        # Deduplicate (duplicates may occur if the query spans multiple tables,
        # e.g. when doing targetentry and targetnode queries)
        qset = qset.distinct()


        # Filter by validation check
        if self.params.get("validationcheck") == "unlinked":
            qset = qset.filter(link__isnull=True)
        elif self.params.get("validationcheck") == "missingWordclass":
            from .validation import check_for_missing_wordclass
            qset = check_for_missing_wordclass(qset)
        elif self.params.get("validationcheck") == "missingType":
            from .validation import check_for_missing_type
            qset = check_for_missing_type(qset)
        elif self.params.get("validationcheck") == "duplicateWordclass":
            from .validation import check_for_duplicate_wordclass
            qset = check_for_duplicate_wordclass(qset)
        elif self.params.get("validationcheck") == "lemmaMismatch":
            from .validation import check_for_lemma_mismatch
            qset = check_for_lemma_mismatch(qset)


        # sort (placeholder; no sorting at present)
        if self.params.get("sort") is not None:
            pass

        # slice into a single page of results
        if self.page_num == 0:
            # unpaginated
            page_size = len(qset) + 1
            self.page_num = 1
        else:
            # normally paginated
            page_size = results_per_page

        paged = Paginator(qset, page_size)
        try:
            self.results = paged.page(self.page_num)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            self.results = paged.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            self.results = paged.page(paged.num_pages)
            self.out_of_range = True

        return self.results

    def summary(self):
        """Human-readable summary of results
        """
        if self.results.paginator.count == 0:
            return "No results found"
        elif self.results.paginator.count == 1:
            return "1 result"
        else:
            return "%d - %d of %d results" % (self.results.start_index(),
                   self.results.end_index(), self.results.paginator.count,)

    def is_out_of_range(self):
        return self.out_of_range

    def paginators(self):
        """Generate previous/next links
        """
        prevlink = None
        nextlink = None
        if self.results.has_other_pages():
            args = {k: v for k, v in self.params.items()}
            if self.results.has_previous():
                args["page"] = str(self.results.previous_page_number())
                prevlink = "&".join("%s=%s" % (k, v,) for k, v in args.items())
            if self.results.has_next():
                args["page"] = str(self.results.next_page_number())
                nextlink = "&".join("%s=%s" % (k, v,) for k, v in args.items())
        return (prevlink, nextlink)


def topic_branch(topic_id):
    from ..topic.taxonomy import Taxonomy
    return Taxonomy().list_branch(topic_id)

