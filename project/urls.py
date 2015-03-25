from django.conf.urls import patterns, url
from project import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^users/$', views.UserList.as_view(), name='user_list'),
    url(r'^users/(?P<pk>\d+)/$', views.UserDetail.as_view(), name='user_detail'),
    url(r'^projects/$', views.ProjectList.as_view(), name='project_list'),
    url(r'^projects/(?P<pk>\d+)/$', views.ProjectDetail.as_view(), name='project_detail'),
    url('^login/$', 'django.contrib.auth.views.login', name='login'),
    url('^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
)
