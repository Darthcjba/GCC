from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'projectium.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('authentication.urls', namespace='authentication')),
    url(r'^', include('project.urls', namespace='project')),

)
