from django.contrib.auth.models import User,Group
from jforms.models import *

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

def centerboss(user):
    group = user.groups.all()[0]
    dept = Dept.objects.get(group=group)
    center = dept.center_set.all()[0]
    return center.boss

def centerbossof(name):
    center = Center.objects.get(name=name)
    return center.boss
    
