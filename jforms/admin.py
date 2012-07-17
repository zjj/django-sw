from jforms.models import *
from django.contrib import admin
admin.site.register(Requirement)
admin.site.register(SoftwareType)
class Hardware_c(admin.ModelAdmin):
    list_display = ['hardware']
    fields = list_display
admin.site.register(Hardware, Hardware_c)
class Project_c(admin.ModelAdmin):
    list_display = ['project','short','sold','pm']
    fields = ['project','short','sold','pm']
admin.site.register(Project,Project_c)
class Dept_c(admin.ModelAdmin):
    list_display = ['group']
admin.site.register(Dept, Dept_c)
class RC_c(admin.ModelAdmin):
    list_display = ['requirement','signature','whosigned','accept','signed']
    fields = ['requirement','signature','whosigned','accept','reason','signed']
admin.site.register(RequirementConfirm,RC_c)
admin.site.register(Assessment)

class History_c(admin.ModelAdmin):
    fields = ['requirement','stage','stat','message','finished']
    list_display = fields
admin.site.register(History,History_c)
admin.site.register(RequireJudgementConfirm)
admin.site.register(Development)
admin.site.register(DevJudgement)
admin.site.register(TestJudgement)
admin.site.register(TestJudgementConfirm)
admin.site.register(RequireJudgement)
admin.site.register(PreDevJudgement)
admin.site.register(PreDevJudgementConfirm)
