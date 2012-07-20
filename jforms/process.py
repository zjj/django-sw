#coding=utf-8
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.contrib.auth.models import User,Group
from jforms.models import Requirement, Hardware, Project, SoftwareType, Dept, RequirementConfirm, History
from django.shortcuts import render_to_response
from django.core.mail import send_mail,EmailMessage
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from jforms.forms import *
from jforms.functions import *
import datetime

def process(request):
    content = {}
    if request.user.is_authenticated():
        content.update({"username":request.user.first_name})
    reqs = Requirement.objects.all()
    req_set = set()
    for i in reqs:
        req_set.add(i.index)
    reqs = []
    ret = []
    for i in req_set:
        req = Requirement.objects.filter(index=i)
        req = req[len(req)-1]
        reqs.append(req)
    for i in reqs:
        each = {"requirement":i}
        try:
            rh = History.objects.filter(requirement=i,stage="requirement")
            rh = rh[len(rh)-1]
            each.update({"req":rh})
        except:
            pass
        try: 
            ph = History.objects.filter(requirement=i,stage="predev")
            ph = ph[len(ph)-1]
            each.update({"predev":ph})
        except:
            pass
        try:
            dh = History.objects.filter(requirement=i,stage="dev")
            dh = dh[len(dh)-1]
            each.update({"dev":dh})
        except:
            pass
        ret.append(each)
   
    paginator = Paginator(ret,20)
    page = request.GET.get('page')
    try:
        ret = paginator.page(page)
    except PageNotAnInteger:
        ret = paginator.page(1)
    except EmptyPage:
        ret = paginator.page(paginator.num_pages)
    content["list"] = ret 

    all_hardware_type = Hardware.objects.all()
    hardware_list = []
    for i in all_hardware_type:
        hardware_list.append(i.hardware)

    all_software_type = SoftwareType.objects.all()
    software_list = []
    for i in all_software_type:
        software_list.append(i.software_type)

    all_project = Project.objects.all()
    project_list = []
    for i in all_project:
        project_list.append(i.project)
    
    dept_list = Dept.objects.all()
   
    content.update({"hardware_list":hardware_list,\
         "software_list":software_list,\
         "project_list":project_list,\
         "dept_list":dept_list,})

    return render_to_response("jforms/process.html",content)

def filter(request):
    content = {}
    if request.user.is_authenticated():
        content.update({"username":request.user.first_name})
    project = request.GET.get("project","none")
    if project != "none":
        project = Project.objects.get(project=project) 
        q1=Q(project=project)
    else:
        q1=Q()
    software_type = request.GET.get("software_type","none")
    if software_type != "none":
        software_type = SoftwareType.objects.get(software_type=software_type)
        q2 = Q(software_type=software_type)
    else:
        q2 = Q() 
    hardware = request.GET.get("hardware","none")
    if hardware != "none":
        hardware = Hardware.objects.get(hardware=hardware)
        q3 = Q(hardware=hardware)
    else:
        q3=Q()
    start_date = request.GET.get("start_date",u"")
    end_date = request.GET.get("end_date",u"")
    if start_date != u"" and end_date != u"":
        q4=Q(expired_date__lte=end_date)
        q5=Q(expired_date__gte=start_date)
    else:
        q4=Q()
        q5=Q()

    dept = request.GET.get("dept",u"")

    reqs=Requirement.objects.filter(q1 & q2 & q3 & q4 & q5)
    req_set = set()
    for i in reqs:
        req_set.add(i.index)
    reqs = []
    ret = []
    for i in req_set:
        req = Requirement.objects.filter(index=i)
        req = req[len(req)-1]
        if dept != "none":
            if req.author.groups.all()[0].dept_set.all()[0].id == int(dept):
                reqs.append(req)
        else:
            reqs.append(req)
            
    for i in reqs:
        each = {"requirement":i}
        try:
            rh = History.objects.filter(requirement=i,stage="requirement")
            rh = rh[len(rh)-1]
            each.update({"req":rh})
        except:
            pass
        try: 
            ph = History.objects.filter(requirement=i,stage="predev")
            ph = ph[len(ph)-1]
            each.update({"predev":ph})
        except:
            pass
        try:
            dh = History.objects.filter(requirement=i,stage="dev")
            dh = dh[len(dh)-1]
            each.update({"dev":dh})
        except:
            pass
        ret.append(each)
   
    paginator = Paginator(ret,20)
    page = request.GET.get('page')
    try:
        ret = paginator.page(page)
    except PageNotAnInteger:
        ret = paginator.page(1)
    except EmptyPage:
        ret = paginator.page(paginator.num_pages)
    content["list"] = ret 

    all_hardware_type = Hardware.objects.all()
    hardware_list = []
    for i in all_hardware_type:
        hardware_list.append(i.hardware)

    all_software_type = SoftwareType.objects.all()
    software_list = []
    for i in all_software_type:
        software_list.append(i.software_type)

    all_project = Project.objects.all()
    project_list = []
    for i in all_project:
        project_list.append(i.project)

    dept_list = Dept.objects.all()
   
    content.update({"hardware_list":hardware_list,\
         "software_list":software_list,\
         "project_list":project_list,\
         "dept_list":dept_list,})

    return render_to_response("jforms/process.html",content)

@login_required(login_url="/login/")
def search(request):
    pass
    











