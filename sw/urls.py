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
    url(r'^newrequirement/$','jforms.requirement.newrequirement'),
    url(r'^editrequirement/(?P<index>\d+)/$','jforms.requirement.editrequirement'),
    url(r'^viewrequirement/(?P<index>\d+)/$','jforms.requirement.viewrequirement'),
    url(r'^requirementconfirm/(?P<username>\w+)/(?P<index>\d+)/$', 'jforms.requirement.requirementconfirm'),
    url(r'myhome/$','jforms.views.myhome'),
    url(r'^editassessment/(?P<index>\d+)/$','jforms.requirement.editassessment'),
    url(r'^judgerequirement/(?P<index>\d+)/$','jforms.requirement.judgerequirement'),
    url(r'^judgerequirementconfirm/(?P<username>\w+)/(?P<index>\d+)/$','jforms.requirement.judgerequirementconfirm'),
    url(r'^dev/(?P<index>\d+)/$','jforms.dev.dev'),
    url(r'^devjudge/(?P<index>\d+)/$','jforms.dev.devjudge'),
    url(r'^testjudge/(?P<index>\d+)/$','jforms.test.testjudge'),
    url(r'^testjudegeconfirm/(?P<username>\w+)/(?P<index>\d+)/$','jforms.test.testjudgeconfirm'),
    url(r'^testjudgeview/(?P<index>\d+)/$','jforms.test.testjudgeview'),
)
