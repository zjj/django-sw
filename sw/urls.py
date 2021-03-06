from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

def i18n_javascript(request):
    return admin.site.i18n_javascript(request)

handler403="jforms.handler403.handler403"

urlpatterns = patterns('',
    url(r'^admin/jsi18n', i18n_javascript),
    url(r'admin/', include(admin.site.urls)),
    url(r'register/$','account.views.register'),
    url(r'password_change/$','account.views.password_change'),
    url(r'logout/$','account.views.logout'),
    url(r'login/$','account.views.login'),
    url(r'^$','jforms.views.myhome'),
    url(r'^newrequirement/$','jforms.requirement.newrequirement'),
    url(r'^editrequirement/(?P<index>\d+)/$','jforms.requirement.editrequirement'),
    url(r'^viewrequirement/(?P<index>\d+)/$','jforms.requirement.viewrequirement'),
    url(r'^judgerequirementview/(?P<index>\d+)/$','jforms.requirement.judgerequirementview'),
    url(r'^requirementconfirm/(?P<username>\w+)/(?P<index>\d+)/$', 'jforms.requirement.requirementconfirm'),
    url(r'myhome/$','jforms.views.myhome'),
    url(r'myreqs/$','jforms.views.myreqs'),
    url(r'mysigned/$','jforms.views.mysigned'),
    url(r'^editassessment/(?P<index>\d+)/$','jforms.requirement.editassessment'),
    url(r'^viewassessment/(?P<index>\d+)/$','jforms.requirement.viewassessment'),
    url(r'^judgerequirement/(?P<index>\d+)/$','jforms.requirement.judgerequirement'),
    url(r'^judgerequirementconfirm/(?P<username>\w+)/(?P<index>\d+)/$','jforms.requirement.judgerequirementconfirm'),
    url(r'^dev/(?P<index>\d+)/$','jforms.dev.dev'),
    url(r'^history/(?P<index>\d+)/$','jforms.history.history'),
    url(r'^viewdev/(?P<index>\d+)/$','jforms.dev.viewdev'),
    url(r'^viewdev_id/(?P<id>\d+)/$','jforms.dev.viewdev_id'),
    url(r'^devjudge/(?P<index>\d+)/$','jforms.dev.devjudge'),
    url(r'^viewdevjudge/(?P<index>\d+)/$','jforms.dev.viewdevjudge'),
    url(r'^viewdevjudge_id/(?P<id>\d+)/$','jforms.dev.viewdevjudge_id'),
    url(r'^devjudgeconfirm/(?P<username>\w+)/(?P<index>\d+)/$','jforms.dev.devjudgeconfirm'),
    url(r'^testjudge/(?P<index>\d+)/$','jforms.test.testjudge'),
    url(r'^testjudegeconfirm/(?P<username>\w+)/(?P<index>\d+)/$','jforms.test.testjudgeconfirm'),
    url(r'^testjudgeview/(?P<index>\d+)/$','jforms.test.testjudgeview'),
    url(r'^viewtestjudge_id/(?P<id>\d+)/$','jforms.test.viewtestjudge_id'),
    url(r'^process/$','jforms.process.process'),
    url(r'^filter/$','jforms.process.filter'),
    url(r'^predev/(?P<index>\d+)/$','jforms.predev.predev'),
    url(r'^predevjudge/(?P<index>\d+)/$','jforms.predev.predevjudge'),
    url(r'^predevconfirm/(?P<username>\w+)/(?P<index>\d+)/$','jforms.predev.predevconfirm'),
    url(r'^viewpredevjudge/(?P<index>\d+)/$','jforms.predev.viewpredevjudge'),
    url(r'^viewpredev/(?P<index>\d+)/$','jforms.predev.viewpredev'),
)
