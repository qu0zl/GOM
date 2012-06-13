from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {"template": "gom/gom.html"}, name="gom"),
    url(r"^terms/$", direct_to_template, {"template": "gom/terms.html"}, name="terms"),
    url(r"^privacy/$", direct_to_template, {"template": "gom/privacy.html"}, name="privacy"),
    url(r"^dmca/$", direct_to_template, {"template": "gom/dmca.html"}, name="dmca"),
    url(r"^what_next/$", direct_to_template, {"template": "gom/what_next.html"}, name="what_next"),
    url(r"^help/unit/$", direct_to_template, {"template": "gom/unit_help.html"}, name="unit_help"),
    url(r"^help/force/$", direct_to_template, {"template": "gom/force_help.html"}, name="force_help"),
    url(r"^help/multi/$", direct_to_template, {"template": "gom/multi_help.html"}, name="multi_help"),
    (r'^unit/(\d+)/$', 'gom.views.unitForm'),
    (r'^unit/(\d+)/save/$', 'gom.views.unitSave'),
    (r'^force/(\d+)/$', 'gom.views.forceForm'),
    (r'^force/(\d+)/save/$', 'gom.views.forceSave'),
    (r'^force/forceEntryCount/$', 'gom.views.updateEntryCount'),
    (r'^list/(?P<what>\w+)/$', 'gom.views.listHandler'),
    (r'^list/(?P<filterType>\w+)/(?P<filterValue>\w+)/$', 'gom.views.list'),
    (r'^list/(?P<filterType>\w+)/(?P<filterValue>\w+)/(?P<filterValue2>\w+)/$', 'gom.views.list'),
)

