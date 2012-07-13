from django.contrib.auth.models import User,Group
from jforms.models import Requirement, Hardware, Project, SoftwareType, Dept, History

def adduser(content,user):
    content.update({"username":user.first_name}) 

def myboss(user):
    group = user.groups.all()[0]
    dept = Dept.objects.get(group=group)
    return dept.manager

def pm(project):
    return project.pm

def dept_manager(dept):
    group  = Group.objects.get(name=dept)
    dept = Dept.objects.get(group=group)
    return dept.manager

def log(requirement="",stage="",stat="",message=""):
    h = History(requirement=requirement,stage=stage,stat=stat,message=message)
    h.save()


