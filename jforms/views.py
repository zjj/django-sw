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



def myhome(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    content = {}
    adduser(content,request.user)
    reqs = Requirement.objects.filter(author=request.user)
    reqs = reqs.order_by("-time")
    req_set = set()
    for i in reqs:
        req_set.add(i.index)
        if len(req_set) >= 10:
            break
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
     
    content.update({"list":ret})  

    #RequirementConfirm signature
    #RequireJudgementConfirm user
    #PreDevJudgementConfirm user
    #DevJudgementConfirm user
    #TestJudgementConfirm signature
    # req not finished and signature not signed
    ret = []
    user = request.user

    rc = RequirementConfirm.objects.filter(signature=user,signed=False)
    for i in rc:
        h = History.objects.filter(requirement=i.requirement,finished=True)
        if len(h) == 0:
            ret.append(i.requirement)

    rjc = RequireJudgementConfirm.objects.filter(user=user,signed=False)
    for i in rjc:
        h =  History.objects.filter(requirement=i.requirement,finished=True)
        if len(h) == 0:
            ret.append(i.requirement)

    pdjc = PreDevJudgementConfirm.objects.filter(user=user,signed=False)
    for i in pdjc:
        h = History.objects.filter(requirement=i.predevjudge.predev.requirement,finished=True)
        if len(h) == 0:
            ret.append(i.predevjudge.predev.requirement)

    djc = DevJudgementConfirm.objects.filter(user=user,signed=False)
    for i in djc:
        h = History.objects.filter(requirement=i.devjudge.dev.requirement,finished=True)
        if len(h) == 0:
            ret.append(i.devjudge.dev.requirement)

    tjc = TestJudgementConfirm.objects.filter(signature=user,signed=False)
    for i in tjc:
        h = History.objects.filter(requirement=i.testjudge.devjudge.dev.requirement,finished=True)
        if len(h) == 0:
            ret.append(i.testjudge.devjudge.dev.requirement)
    reqs = ret 
    req_set = set()
    for i in reqs:
        req_set.add(i.index)
        if len(req_set) >= 10:
            break
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
     
    content.update({"list1":ret})  
    
    return render_to_response("jforms/myhome.html", content)














