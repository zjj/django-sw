from jforms.models import Requirement,Hardware, Project, SoftwareType, Dept
from django.contrib import admin
admin.site.register(Requirement)
admin.site.register(SoftwareType)
class Hardware_c(admin.ModelAdmin):
    list_display = ['hardware']
    fields = list_display
admin.site.register(Hardware, Hardware_c)
class Project_c(admin.ModelAdmin):
    list_display = ['project','sold','pm']
    fields = ['project','sold','pm']
admin.site.register(Project,Project_c)
class Dept_c(admin.ModelAdmin):
    list_display = ['group']
admin.site.register(Dept, Dept_c)
