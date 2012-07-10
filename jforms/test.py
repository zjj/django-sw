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
def test(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    d = Development.objects.filter(requirement=r)
    d = d[len(d)-1]
    dj = DevJudgement.objects.filter(dev=d)
    dj = dj[len(dj)-1]

    if request.method == "POST":
        pass
            
    return render_to_response('jforms/test.html',content)
        

