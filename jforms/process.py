#coding=utf-8
from django.db.models import Q
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

#测试评审
def process(request):
    content = {}
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
        h = History.objects.filter(requirement=i)
        now = h[len(h)-1]
        each = {"requirement":i,"stage":now,}
        ret.append(each)
   
    paginator = Paginator(ret,2)
    page = request.GET.get('page')
    try:
        ret = paginator.page(page)
    except PageNotAnInteger:
        ret = paginator.page(1)
    except EmptyPage:
        ret = paginator.page(paginator.num_pages)
    content["list"] = ret 
    return render_to_response("jforms/process.html",content)
              
