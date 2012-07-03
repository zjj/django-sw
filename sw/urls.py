from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

def i18n_javascript(request):
    return admin.site.i18n_javascript(request)

urlpatterns = patterns('',
    url(r'^admin/jsi18n', i18n_javascript),
    url(r'admin/', include(admin.site.urls)),
    url(r'register/$','account.views.register'),
    url(r'password_change/$','account.views.password_change'),
    url(r'logout/$','account.views.logout'),
    url(r'login/$','account.views.login'),
    url(r'^$','account.views.login'),
)
