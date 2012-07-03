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


def history(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})

    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    q1 = Q(version__isnull=False)
    q2 = Q(requirement=r)
    ds = Development.objects.filter(q1&q2)
    lists = []
    for d in ds:
        cc = {}
        cc.update({"req":r})
        cc.update({"dev":d})
        dj = DevJudgement.objects.filter(dev=d)
        if len(dj) != 0:
            dj = dj[len(dj)-1]
            cc.update({"dj":dj})
        tj = TestJudgement.objects.filter(devjudge=dj)
        if len(tj) != 0:
            tj = tj[len(tj)-1]
            cc.update({"tj":tj})
        lists.append(cc)
        cc = {}
   
    content.update({"list":lists})
    return render_to_response('jforms/history.html',content)



















