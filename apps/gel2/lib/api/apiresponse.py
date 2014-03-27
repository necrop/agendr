import json

from ..find_record import find_record
from ..search.resultslist import ResultsList
from .jsonconstructor import EntryJson
from ..frequency.frequencyplot import FrequencyPlot



class ApiResponse(object):

    def __init__(self, action, request):
        self.action = action
        self.request = request
        self.args = booleanize(self.request.GET)

    def get_response(self):
        self.success = True
        self.message = None

        if self.action == "getentry":
            response_data = self._get_entry()
        elif self.action == "search":
            response_data = self._search()
        elif self.action == "findentry":
            response_data = self._find_entry()
        else:
            response_data = {}
            self.success = False
            self.message = "Available actions are 'getentry' or 'search'"

        if self.args.get("format") == "chart":
            return response_data
        elif self.args.get("prettyPrint"):
            response_data["_META"] = self._meta()
            return json.dumps(response_data, sort_keys=True, ensure_ascii=False,
                   indent=4, separators=(',', ': '))
        else:
            response_data["_META"] = self._meta()
            return json.dumps(response_data, ensure_ascii=False)

    def _get_entry(self):
        id = self.args.get("id", "0")
        e = find_record("entry", id)
        if e is None:
            self.success = False
            self.message = "Entry not found"
            return {}
        else:
            if self.args.get("format") == "chart":
                return FrequencyPlot(e).draw_chart()
            else:
                return EntryJson(e).data(**self.args)

    def _search(self):
        rl = ResultsList(self.request, **self.args)
        results = rl.list_results()
        if rl.is_out_of_range():
            self.success = False
            self.message = "Page number out of range"
            return {}
        else:
            include_links = self.args.get("includeLinks", True)
            m = {
                "numResults": results.paginator.count,
                "pageNum": rl.page_num,
                "pageSize": results.paginator.per_page,
                "rankFirstResult": results.start_index(),
                "rankLastResult": results.end_index(),
                "totalPages": results.paginator.num_pages,
                "results": [result_slug(e, include_links) for e in results],
            }
            return m

    def _find_entry(self):
        rl = ResultsList(self.request, **self.args)
        results = rl.list_results()
        if results:
            if self.args.get("format") == "chart":
                return FrequencyPlot(results[0]).draw_chart()
            else:
                return EntryJson(results[0]).data(**self.args)
        else:
            self.success = False
            self.message = "Entry not found"
            return {}

    def _meta(self):
        params = {k: v for k, v in self.args.items()}
        params["action"] = self.action
        m = {
            "success": bool(self.success),
            "uri": self.request.get_full_path(),
            "params": params,
        }
        if self.message is not None:
            m["error"] = self.message
        return m


def booleanize(args):
    args2 = {}
    for k, v in args.items():
        if v.lower() in ("y", "yes", "true"):
            v = True
        elif v.lower() in ("n", "no", "false"):
            v = False
        args2[k] = v
    return args2

def result_slug(entry, include_links):
    m = {
        "id": entry.id,
        "lemma": entry.label,
        "wordclasses": [w.penn for w in entry.wordclasses()],
    }
    if include_links == True:
        m["links"] = [link_slug(l) for l in entry.links()]
    return m

def link_slug(link):
    return {
        "resource": link.target(),
        "resourceId": link.target_resource.id,
        "targetEntry": link.target_id,
        "targetNode": link.target_node,
    }

