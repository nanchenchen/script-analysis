from django.conf.urls import patterns, include, url
from django.contrib import admin

from pyanalysis.apps.base import views

urlpatterns = patterns('',
                    #   url(r'^$', views.HomeView.as_view(), name='home'),
                       # url(r'^explorer/$', views.ExplorerView.as_view(), name='explorer'),
                    #   (r'^accounts/logout/$', 'django.contrib.auth.views.logout',{'next_page': '/'}),
                    #   url(r'^accounts/', include('django.contrib.auth.urls')),
                     #  url(r'^explorer(?:/(?P<dataset_pk>\d+))?/$', views.ExplorerView.as_view(), name='explorer'),
                     #  url(r'^grouper(?:/(?P<dataset_pk>\d+))?/$', views.GrouperView.as_view(), name='grouper'),
                    url(r'^script_browser(?:/(?P<dataset_pk>\d+))?/$', views.ScriptBrowserView.as_view(), name='script_browser'),
                    url(r'^script_comparator(?:/(?P<dataset_pk>\d+))?/$', views.ScriptComparatorView.as_view(), name='script_comparator'),
                    url(r'^script_vargraph(?:/(?P<script_pk>\d+))?/$', views.ScriptVarGraphView.as_view(), name='script_vargraph'),
)
