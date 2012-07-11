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

def dev(request, index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]

    if request.method == "POST":
        j = Development.objects.filter(requirement=r) 
        if len(j) != 0:
            d = j[len(j)-1]
            if d.stat == "locked" and d.version is None:
                content.update({"message":"已经锁定，无法再进行修改",})
                return render_to_response("jforms/message.html",content)
        #check = Development.objects.filter(requirement=r,stat="locked")
        #if len(check) > 0:
        #    content.update({"message":"已经锁定，无法再进行修改",})
        #    return render_to_response("jforms/message.html",content)
        author = request.user
        bg = request.POST.get("bg","")
        design = request.POST.get("design","")
        stat = request.POST.get("stat","unlocked")
        p = Development(requirement=r,author=author,bg=bg,design=design,stat=stat)
        p.save()
        if stat == "locked":
            return render_to_response("jforms/message.html",{"message":"本次研发结束"})
        return render_to_response("jforms/message.html",{"message":"本次已经保存，下次可继续进行修改",})
    
    j = Development.objects.filter(requirement=r) 
    if len(j) != 0:
        d = j[len(j)-1]
        if d.ifpass == True:
            content.update({"message":"研发已结束,并且已经通过测试评审",})
            return render_to_response("jforms/message.html",content)
        if d.stat == "locked" and d.version is None:
            content.update({"message":"研发已结束,需求处于后续评审中，无法进行修改",})
            return render_to_response("jforms/message.html",content)
        else:     
            content.update({"dev":d})
    return render_to_response('jforms/dev.html',content)

#内部验证(研发评审)
def devjudge(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    d = Development.objects.filter(requirement=r)
    d = d[len(d)-1]
    
    if request.method == "POST":
        dj = DevJudgement.objects.filter(dev=d)
        if len(dj) != 0:
            dj = dj[len(dj)-1]
            if dj.stat == "locked":
                content.update({"message":"该编号研发评审已经定稿，无法再次修改",})
                return render_to_response("jforms/message.html",content)

        dj = DevJudgeForm(request.POST)
        if dj.is_valid():
            bg = dj.cleaned_data["bg"]  
            testinside = dj.cleaned_data["testinside"]  
            judgement = dj.cleaned_data["judgement"]  
            result = dj.cleaned_data["result"]  
            judges = dj.cleaned_data["judges"]
            stat = request.POST.get("stat","unlocked")
            djm = DevJudgement.objects.create(dev=d,author=request.user,bg=bg,testinside=testinside,judgement=judgement,result=result)
            djm.judges=judges
            djm.save()
        if stat == "locked":
            djm.stat = "locked"
            djm.save()
            content.update({"message":"研发评审已保存，并且已经定稿",})
            return render_to_response("jforms/message.html",content)
        else:
            content.update({"message":"本次研发评审修改已保存",})
            return render_to_response("jforms/message.html",content)
            
    dj = DevJudgement.objects.filter(dev=d)
    if len(dj) != 0:
        dj = dj[len(dj)-1]
        if dj.stat == "locked":
            content.update({"message":"该编号研发评审已经定稿，无法再次修改",})
            return render_to_response("jforms/message.html",content)
        j = DevJudgeEditForm(instance=dj)
    else:
        j = DevJudgeForm()
    content["devjudge"]=j
    return render_to_response('jforms/devjudge.html',content)
        

