from django.conf.urls import url

from pyanalysis.apps.api import views
from django.views.decorators.csrf import csrf_exempt

api_root_urls = {
    'similarity': url(r'^similarity/$', views.SimilarityGraphView.as_view(), name='similarity-graph'),
    'script': url(r'^script/$', views.ScriptContentView.as_view(), name='script'),
    'comparator': url(r'^comparator/$', views.ScriptComparatorView.as_view(), name='comparator'),
    'vargraph': url(r'^vargraph/$', views.ScriptVariableGraphView.as_view(), name='vargraph'),
    'dataset': url(r'^dataset/$', csrf_exempt(views.DatasetView.as_view()), name='dataset'),
}

urlpatterns = api_root_urls.values() + [
    url(r'^$', views.APIRoot.as_view(root_urls=api_root_urls)),
]
