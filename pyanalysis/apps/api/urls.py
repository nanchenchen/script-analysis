from django.conf.urls import url

from pyanalysis.apps.api import views
from django.views.decorators.csrf import csrf_exempt

api_root_urls = {
    'similarity': url(r'^similarity/$', views.SimilarityGraphView.as_view(), name='similarity-graph'),
}

urlpatterns = api_root_urls.values() + [
    url(r'^$', views.APIRoot.as_view(root_urls=api_root_urls)),
]
