from django.conf.urls import patterns, url

urlpatterns = patterns("apps.gel2.views",
    url(r"^/?$", "homepage", name="gel_home"),
    url(r"^/home$", "homepage", name="gel_home"),
    url(r"^/search$", "search", name="gel_search"),
    url(r"^/search/submit$", "submit_search", name="gel_submitsearch"),
    url(r"^/results/(?P<lemma>[a-z*-]+)", "results", name="gel_results"),
    url(r"^/entry/(?P<id>\d+)$", "entry_display", name="gel_entry"),
    url(r"^/entry/random$", "random_entry", name="gel_random"),
    url(r"^/editor/(?P<action>[a-z]+)/(?P<level>[a-z]+)/(?P<id>\d+)$", "editor", name="gel_editor"),
    url(r"^/editor/submit$", "submit_edit_form", name="gel_submitedit"),
    url(r"^/frequencychart/(?P<level>[a-z]+)/(?P<id>\d+).png$", "frequency_chart", name="gel_chart"),
    url(r"^/resources$", "list_resources", name="gel_resources"),
    url(r"^/statistics$", "statistics", name="gel_statistics"),
    url(r"^/info/(?P<page>[a-z0-9_-]+)$", "info", name="gel_info"),
    url(r"^/api/(?P<action>[a-z_-]*)$", "api", name="gel_api"),
    url(r"^/customfields$", "custom_fields", name="gel_custom"),
    url(r"^/customfields/submit$", "custom_fields_edit", name="gel_customedit"),
    url(r"^/customfields/delete/(?P<id>\d+)$", "custom_fields_delete", name="gel_customdelete"),
    url(r"^/taxonomy/display$", "taxonomy", name="gel_taxonomy"),
    url(r"^/taxonomy/edit$", "taxonomy_edit", name="gel_taxonomyedit"),
    url(r"^/validate$", "validate", name="gel_validate"),
    url(r"^/import/jobs$", "imports", name="gel_imports"),
    url(r"^/import/new$", "import_new", name="gel_importnew"),
    url(r"^/import/uploadcsv$", "import_upload_csv", name="gel_importcsv"),
    url(r"^/import/process/(?P<id>\d+)/(?P<action>[a-z_]+)$", "import_process", name="gel_importprocess"),
    url(r"^/import/download/(?P<id>\d+)/(?P<type>[a-z]+)$", "import_download", name="gel_importdownload"),
    url(r"^/import/rake$", "import_rake", name="gel_importrake")
)
