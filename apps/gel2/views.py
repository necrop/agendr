from datetime import datetime

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpRequest
from django.contrib.auth.decorators import login_required
from django.core.servers.basehttp import FileWrapper

from .lib.history import History

base_url = "/projects/gel2"


@login_required
def homepage(request):
    """Home page
    """
    from .models import Resource
    params = {"page_title": "home", "num_resources": Resource.objects.count(),}
    return render(request, "gel2/home.html", _add_base_params(params, request))


@login_required
def search(request):
    """Advanced search form
    """
    from .models import Resource, Topic
    # 'gel2_search' stores search arguments in session data
    if not "gel2_search" in request.session:
        request.session["gel2_search"] = {}
    wordclasses = [("NN", "noun"), ("JJ", "adjective"), ("VB", "verb"),
                   ("RB", "adverb"), ("NP", "proper name"),
                   ("IN", "preposition"), ("CC", "conjunction"),
                   ("UH", "interjection"),]
    timestamps = [(60, "in the last hour"), (1440, "in the last 24 hours"),
                  (10080, "in the last 7 days"), (43200, "in the last 30 days")]
    topics = sorted(Topic.objects.all(), key=lambda t: t.breadcrumb())
    params = {"page_title": "search", "resources": Resource.objects.all(),
              "topics": topics, "wordclasses": wordclasses,
              "timestamps": timestamps,
              "previously": request.session["gel2_search"]}
    return render(request, "gel2/search.html", _add_base_params(params, request))


def submit_search(request):
    """Handles a submitted search

    Both quick search and advanced search submit to here
    """
    def cache_post(p):
        """Store search-form arguments in session data
        """
        p2 = {}
        for k, v in p.items():
            if k.startswith("csrf"):
                pass
            elif v.strip().isdigit():
                p2[k] = int(v)
            else:
                p2[k] = v.strip()
        request.session["gel2_search"] = p2

    from .lib.search.resultsurl import results_url
    if request.method == "POST":
        post = request.POST.copy()
        cache_post(post)
        return HttpResponseRedirect(results_url(base_url, post, None))
    else:
        return redirect(homepage)


def results(request, **kwargs):
    """Results of a search
    """
    from .lib.search.resultslist import ResultsList
    from .lib.search.resultsurl import delete_url
    History(request).store_search(kwargs.get("lemma", "a-zzz"))

    results_list = ResultsList(request, **kwargs)
    paged_results = results_list.list_results()

    if "gel2_search" in request.session:
        param_string = "; ".join(["%s=%s" % (k, str(v)) for k, v in
                       sorted(request.session["gel2_search"].items())])
    else:
        param_string = "no data stored"

    if request.GET.get("action") == "delete":
        from .lib.editor.deleter import Deleter
        for record in paged_results:
            Deleter(record).delete()
        params = {"num_results": paged_results.paginator.count}
        return render(request, "gel2/editor/results_delete_confirmation.html",
                      _add_base_params(params, request))
    else:
        prevlink, nextlink = results_list.paginators()
        title = results_list.summary()
        params = {"page_title": title, "body_title": title,
                  "results": paged_results, "prevlink": prevlink,
                  "nextlink": nextlink, "params": param_string,
                  "delete_url": delete_url(request)}
        return render(request, "gel2/results.html",
                      _add_base_params(params, request))


@login_required
def entry_display(request, **kwargs):
    """Displays an entry record
    """
    from .lib.find_record import find_record
    e = find_record("entry", kwargs.get("id"))
    if e is not None:
        History(request).store_entry(e)
        params = {"page_title": e.label, "entry": e}
        return render(request, "gel2/entry.html", _add_base_params(params, request))
    else:
        params = {"id": kwargs.get("id", "")}
        return render(request, "gel2/entry_not_found.html", _add_base_params(params, request))


def random_entry(request):
    """Displays a random entry
    """
    from .models import Entry
    from django.db.models import Max, Min
    from random import randint
    max_ = Entry.objects.aggregate(Max('id'))['id__max']
    min_ = Entry.objects.aggregate(Min('id'))['id__min']
    id = None
    while id is None:
        try:
            id = Entry.objects.get(pk=randint(min_, max_)).pk
        except Entry.DoesNotExist:
            pass
    return redirect(entry_display, id=id)


def frequency_chart(request, **kwargs):
    """Generates and returns a .png frequency chart
    """
    from .lib.find_record import find_record
    from .lib.frequency.frequencyplot import FrequencyPlot
    level = kwargs.get("level", "entry")
    record = find_record(level, kwargs.get("id"))
    p = FrequencyPlot(record)
    return p.draw_chart()


@login_required
def list_resources(request, **kwargs):
    """Shows a list of all external resources registered with GEL2
    (i.e. all Resource records)
    """
    from .models import Resource
    r = Resource.objects.all()
    params = {"resources": r, "page_title": "resources"}
    return render(request, "gel2/resources.html", _add_base_params(params, request))


@login_required
def editor(request, **kwargs):
    """Actions any submitted form for adding, editing, or deleting an
    Entry, Wordclass, Type, or Resource record
    """
    from .lib.find_record import find_record
    from .lib.editor.deleter import Deleter, DeleteResource
    from .lib.editor.merger import Merger
    from .lib.editor.editorform import EditorForm

    # If action='add', id is the ID of the *parent* item.
    # For all other actions, id is the ID of the item being acted on.
    referrer = request.META["HTTP_REFERER"]
    action = kwargs.get("action")
    record = find_record(kwargs.get("level", "entry"), kwargs.get("id"))

    if record is None and action != "add":
        return HttpResponseRedirect(referrer)

    elif (kwargs.get("level") == "resource" and
          kwargs.get("action") == "delete"):
        DeleteResource(record).delete()
        return redirect(list_resources)

    elif kwargs.get("level") == "resource":
        if action == "add":
            # Fake a record so that the template has something to use
            record = {"id": 0, "level": "resource"}
        params = {"page_title": action + " resource", "referrer": referrer,
                  "body_title": action.capitalize() + " resource",
                  "action": action, "record": record}
        return render(request, "gel2/editor/edit_resource.html",
                      _add_base_params(params, request))

    elif action == "delete":
        id = record.id
        Deleter(record).delete()
        if record.level() == "entry":
            params = {"page_title": "deletion successful", "record": record,
                      "id": id}
            return render(request, "gel2/editor/delete_confirmation.html",
                          _add_base_params(params, request))
        else:
            return HttpResponseRedirect(referrer)

    elif action == "move":
        original_id = record.entry.id
        targetid = request.POST.get("targetid", "0").strip()
        if not targetid.isdigit():
            targetid = "0"
        target_entry = find_record("entry", targetid)
        if target_entry is not None and original_id != targetid:
            record.entry.bubble_save() # update timestamp on source entry
            record.entry = target_entry # move wordclass to new entry
            record.bubble_save() # save and update timestamp on new entry
        return redirect(entry_display, id=original_id)

    elif action == "merge":
        targetid = request.POST.get("targetid", "0").strip()
        if not targetid.isdigit():
            targetid = "0"
        if targetid != record.id:
            target_entry = find_record("entry", targetid)
            Merger(record, target_entry).merge()
        return redirect(entry_display, id=targetid)

    elif action == "edit":
        template, form = EditorForm(record).edit_form()
        title = "%s (%s #%d)" % (record.identifier(), record.level(), record.id)
        params = {"page_title": "edit " + record.level(), "referrer": referrer,
                  "body_title": title,
                  "action": "edit", "record": record, "form": form}
        return render(request, "gel2/editor/" + template,
                      _add_base_params(params, request))

    elif action == "add":
        template, form, title = EditorForm(record).add_form()
        if kwargs.get("level") == "root":
            # In case of adding a new entry, fake a record so that the
            #  template has something to use
            record = {"id": 0, "level": "root"}
        params = {"page_title": "add record", "referrer": referrer,
                  "body_title": title, "action": "add", "record": record,
                  "form": form}
        return render(request, "gel2/editor/" + template,
                      _add_base_params(params, request))


def submit_edit_form(request, **kwargs):
    """Accepts a submitted edit form, passes it to the appropriate function
    for implementing this, then redirects to an appropriate page
    """
    from .lib.editor.execute import RecordEdit, RecordAdd, ResourceEdit
    if request.method == "POST":
        post = request.POST.copy()
        if post.get("level") == "resource":
            ResourceEdit(post).implement()
            return redirect(list_resources)
        elif post.get("action") == "edit":
            RecordEdit(post).implement()
            return HttpResponseRedirect(post.get("referrer", base_url))
        elif post.get("action") == "add":
            record = RecordAdd(post).implement()
            if record.level() == "entry":
                return redirect(entry_display, id=str(record.id))
            else:
                return HttpResponseRedirect(post.get("referrer", base_url))
    else:
        return redirect(homepage)


def info(request, **kwargs):
    """Displays static information pages (help, about, etc.)
    """
    page = kwargs.get("page", "about")
    params = {"page_title": page,}
    return render(request, "gel2/info/" + page + ".html",
                  _add_base_params(params, request))


@login_required
def statistics(request, **kwargs):
    """Calculates and displays key statistics from the GEL2 database
    (essentially, just counting the number of records of each type)
    """
    from .models import (Entry, Wordclass, Type, Resource, Link,
                         FreqTable, Topic)
    records = [(r[0], r[1].objects.count()) for r in (("entries", Entry),
        ("wordclasses", Wordclass), ("types", Type),
        ("frequency tables", FreqTable), ("links", Link),
        ("taxonomy nodes", Topic), ("resources", Resource),)]
    params = {"page_title": "statistics", "records": records}
    return render(request, "gel2/statistics.html",
                  _add_base_params(params, request))


def api(request, **kwargs):
    """Handler for requests received via the API
    """
    from .lib.api.apiresponse import ApiResponse
    action = kwargs.get("action", "getentry").lower()
    response = ApiResponse(action, request).get_response()
    if request.GET.get("format") == "chart":
        return HttpResponse(response, content_type="image/png")
    else:
        return HttpResponse(response, content_type="application/json")


@login_required
def custom_fields(request, **kwargs):
    from .lib.custom.customfieldeditor import CustomFieldForm
    form = CustomFieldForm().form()
    params = {"page_title": "custom fields", "form": form,}
    return render(request, "gel2/custom_fields.html",
                  _add_base_params(params, request))


def custom_fields_edit(request, **kwargs):
    from .lib.custom.customfieldeditor import CustomFieldEdit, CustomFieldAdd
    if request.method == "POST":
        post = request.POST.copy()
        if post.get("action") == "edit":
            CustomFieldEdit(post).execute()
        elif post.get("action") == "add":
            CustomFieldAdd(post).execute()
        return redirect(custom_fields)
    else:
        return redirect(homepage)


def custom_fields_delete(request, **kwargs):
    from .lib.custom.customfieldeditor import CustomFieldDelete
    id = kwargs.get("id")
    CustomFieldDelete(id).delete()
    return redirect(custom_fields)


@login_required
def taxonomy(request, **kwargs):
    from .models import Topic
    topics = sorted(Topic.objects.all(), key=lambda t: t.breadcrumb())
    params = {"page_title": "taxonomy", "topics": topics}
    return render(request, "gel2/taxonomy.html",
                  _add_base_params(params, request))


def taxonomy_edit(request, **kwargs):
    from lib.topic.editor import Editor
    if request.method == "POST":
        ed = Editor(request.POST.copy())
        ed.execute()
    return redirect(taxonomy)


@login_required
def validate(request, **kwargs):
    params = {"page_title": "validation"}
    return render(request, "gel2/validate.html",
                  _add_base_params(params, request))


@login_required
def imports(request, **kwargs):
    from .models import ImportJob
    params = {"page_title": "imports", "jobs": ImportJob.objects.all()}
    return render(request, "gel2/imports.html",
                  _add_base_params(params, request))


def import_new(request, **kwargs):
    from .lib.imports.register import register_new_job
    if request.method == "POST":
        register_new_job(request.POST, request.FILES["file"])
    return redirect(imports)


def import_upload_csv(request, **kwargs):
    from .lib.imports.register import upload_csv
    if request.method == "POST":
        jobid = request.POST.get("jobid", 0)
        upload_csv(jobid, request.FILES["file"])
    return redirect(imports)


def import_download(request, **kwargs):
    from .lib.find_record import find_record
    job = find_record("ImportJob", kwargs.get("id"))
    type = kwargs.get("type")
    if type == "zip":
        filepath = job.zip.path
        filename = job.zipname()
        contenttype = "application/zip"
    if type == "csv":
        filepath = job.csv.path
        filename = job.csvname()
        contenttype = "text/csv"
    wrapper = FileWrapper(file(filepath))
    response = HttpResponse(wrapper, content_type='text/plain')
    response["Content-Disposition"] = "attachment; filename=%s" % (filename)
    return response


def import_process(request, **kwargs):
    """Processes relating to data imports

    In a production environment, import_analyse_zip and import_add_to_db
      are run asynchronously (with 'delay', handled by celeryd). In a
      test environment (DEBUG==True), they're run live (without 'delay').
    """
    from .lib.find_record import find_record
    from .lib.imports.register import delete_job
    from agendr.gel2.tasks import import_analyse_zip, import_add_to_db, import_rollback

    action = kwargs.get("action", "generate")
    job = find_record("ImportJob", kwargs.get("id"))
    if action == "delete":
        delete_job(job)
    elif action == "generatecsv":
        if settings.DEBUG == True:
            import_analyse_zip(job)
        else:
            import_analyse_zip.delay(job)
    elif action == "import":
        job.importstarted = datetime.now()
        job.save()
        if settings.DEBUG == True:
            import_add_to_db(job)
        else:
            import_add_to_db.delay(job)
    elif action == "rollback":
        if settings.DEBUG == True:
            import_rollback(job)
        else:
            import_rollback.delay(job)
    return redirect(imports)


def import_rake(request, **kwargs):
    from .lib.imports.register import rake
    rake()
    return redirect(imports)


def _add_base_params(params, request):
    params["baseurl"] = base_url
    params["history"] = History(request).list_history()
    params["server"] = HttpRequest.build_absolute_uri(request, "/").strip("/")
    if "gel2_search" in request.session:
        params["query_term"] = request.session["gel2_search"].get("lemma", "")
    else:
        params["query_term"] = ""
    return params

