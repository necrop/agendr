import re

def results_url(base_url, args, page_num):

    # In case the request coemes from the form on ther validation page
    if "lemmaFrom" in args and "lemmaTo" in args:
        args["lemma"] = args["lemmaFrom"] + "-" + args["lemmaTo"]

    if not "lemma" in args:
        return base_url
    else:
        lemma = sanitize(args.get("lemma", ""))
        url = "%s/results/%s" % (base_url, lemma,)

        params = ["%s=%s" % (k, str(v)) for k, v in args.items()
                  if not k.startswith("csrf") and
                  k not in ("lemma", "lemmaFrom", "lemmaTo") and
                  v != "null"]
        if page_num is not None and page_num > 1:
            params.append("page=%d" % (page_num,))
        if params:
            url = "%s?%s" % (url, "&".join(params),)

        return url


def delete_url(request):
    params = {k: v for k, v in request.GET.items()
            if not k in ("page", "sort") and not k.startswith("csrf")}
    params["action"] = "delete"
    params["page"] = "0"
    return request.path + "?" + "&".join(["%s=%s" % (k, v)
        for k, v in params.items()])


def sanitize(lemma):
    l = re.sub(r"[^a-z*-]", "", lemma.lower())
    l = l.strip("-")
    if not l:
        l = "a-zzz"
    return l
