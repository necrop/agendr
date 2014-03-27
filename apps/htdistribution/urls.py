from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from .views import plot

urlpatterns = patterns("apps.htdistribution.views",
    url(r"^/?$", "homepage", name="htdistribution_home"),
    url(r"^/home$", "homepage", name="htdistribution_home"),
    url(r"^/info/(?P<page>[a-z]+)$", "info", name="htdistribution_info"),
    url(r"^/list/(?P<setname>[a-z]+)$", "list_elements", name="htdistribution_list"),
    url(r"^/element/(?P<id>\d+)$", "element_display", name="htdistribution_element"),
    url(r"^/taxonomy$", "taxonomy", name="htdistribution_taxonomy"),
    url(r"^/submitsearch$", "search", name="htdistribution_submitsearch"),
    url(r"^/searchresults/(?P<query>.*)$", "search_results", name="htdistribution_searchresults"),

    url(r"^/collection/(?P<id>\d+)$", "collection", name="htdistribution_collection"),
    url(r"^/collection/anon/(?P<idlist>.*)$", "collection", name="htdistribution_collectionanon"),
    url(r"^/collection/submit$", "collection_submit", name="htdistribution_collectionsubmit"),
    url(r"^/collection/fail$", "collection_fail", name="htdistribution_collectionfail"),
    url(r"^/collection/save$", "collection_save", name="htdistribution_collectionsave"),
    url(r"^/collection/manage$", "collection_manager", name="htdistribution_collections"),
    url(r"^/collection/update$", "collection_update", name="htdistribution_collectionupdate"),
    url(r"^/collection/delete/(?P<id>\d+)$", "collection_delete", name="htdistribution_collectiondelete"),

    url(r"^/plot/(?P<type>[a-z0-9]+)/(?P<idlist>[0-9-]+).png$",
        cache_page(24 * 60 * 60)(plot),
        name="htdistribution_plot"),
)
