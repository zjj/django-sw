#coding=utf-8
from django.db.models import Q
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,Group
from jforms.models import Requirement, Hardware, Project, SoftwareType, Dept, RequirementConfirm, History
from django.shortcuts import render_to_response
from django.core.mail import send_mail,EmailMessage
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from jforms.forms import *
from jforms.functions import *
import datetime

@permission_required("jforms.change_development",login_url='/login/',raise_exception=True)
def dev(request, index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    h = History.objects.filter(requirement=r,finished=True)
    if len(h) != 0:
        content.update({"message":"该需求已结束",})
        return render_to_response("jforms/message.html",content)

    if request.method == "POST":
        j = Development.objects.filter(requirement=r) 
        if len(j) != 0:
            d = j[len(j)-1]
            if d.stat == "locked" and d.version is None:
                content.update({"message":"已经锁定，无法再进行修改",})
                return render_to_response("jforms/message.html",content)
        author = request.user
        bg = request.POST.get("bg","")
        design = request.POST.get("design","")
        stat = request.POST.get("stat","unlocked")
        p = Development(requirement=r,author=author,bg=bg,design=design,stat=stat)
        p.save()
        #log
        q1 = Q(version__isnull=False)
        q2 = Q(requirement=r)
        ver = Development.objects.filter(q1&q2)
        if len(ver) == 0:
            version = ""
        else:
            version = ver[len(ver)-1].version+1
        stage = u"dev"
        message = u"dev was edited by %s"%request.user.username
        if version == "":
            html = u'<a href="/dev/%s/">编辑研发<a> <a href="/viewdev/%s">查看研发</a>'%(index,index)
        else:
            html = u'<a href="/dev/%s/">编辑研发<a><sup><font color=red>第%s次修正</font></sup> <a href="/viewdev/%s/">查看研发</a> \
                    <a href="/history/%s/"><sup>历史</sup></a>'%(index,version,index,index)
        log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
        log.save()
  
        if stat == "locked":
            stage = u"dev"
            message = u"dev was locked by %s"%request.user.username
            if version == "":
                html = u'<a href="/devjudge/%s/">新建研发评审</a> <a href="/viewdev/%s">查看研发</a>'%(index,index)
            else:
                html = u'<a href="/devjudge/%s/">新建研发评审</a> <sup><font color=red>第%s次修正</font></sup> \
                        <a href="/viewdev/%s">查看研发</a> <a href="/history/%s/"><sup>历史</sup></a>'%(index,version,index,index)
            log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
            log.save()
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


def viewdev(request,index):
    content={}
    content.update({"index":index})
    if request.user.is_authenticated():
        content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    
    j = Development.objects.filter(requirement=r) 
    if len(j) != 0:
        d = j[len(j)-1]
        content.update({"dev":d})
    return render_to_response('jforms/viewdev.html',content)

#内部验证(研发评审)
@permission_required("jforms.change_devjudgement",login_url='/login/',raise_exception=True)
def devjudge(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]

    h = History.objects.filter(requirement=r,finished=True)
    if len(h) != 0:
        content.update({"message":"该需求已结束",})
        return render_to_response("jforms/message.html",content)

    d = Development.objects.filter(requirement=r)
    d = d[len(d)-1]
    
    if request.method == "POST":
        dj = DevJudgement.objects.filter(dev=d)
        if len(dj) != 0:
            dj = dj[len(dj)-1]
            if dj.stat == "prelocked" or dj.stat == "locked":
                content.update({"message":"该编号研发评审已经定稿，无法再次修改",})
                return render_to_response("jforms/message.html",content)
        
        djf = DevJudgeForm(request.POST)
        if djf.is_valid():
            bg = djf.cleaned_data["bg"]  
            testinside = djf.cleaned_data["testinside"]  
            judgement = djf.cleaned_data["judgement"]  
            result = djf.cleaned_data["result"]  
            judges = djf.cleaned_data["judges"]
            stat = request.POST.get("stat","unlocked")
            dj = DevJudgement.objects.create(dev=d,author=request.user,bg=bg,testinside=testinside,judgement=judgement,result=result,stat=stat)
            dj.judges=judges
            dj.save()
            #log
            q1 = Q(version__isnull=False)
            q2 = Q(requirement=r)
            ver = Development.objects.filter(q1&q2)
            if len(ver) == 0:
                version = ""
            else:
                version = ver[len(ver)-1].version+1
            stage = u"dev"
            message = u"dev was edited by %s"%request.user.username
            if version == "":
                html = u'<a href="/devjudge/%s/">编辑研发评审</a> <a href="/viewdevjudge/%s/">查看研发评审</a> <a href="/viewdev/%s">查看研发</a>'%(index,index,index)
            else:
                html = u'<a href="/devjudge/%s/">编辑研发评审</a> <sup><font color=red>第%s次修正</font></sup> <a href="/viewdevjudge/%s/">查看研发评审</a> \
                        <a href="/viewdev/%s">查看研发</a> <a href="/history/%s/"><sup>历史</sup></a>'%(index,version,index,index,index)
            log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
            log.save()
            if stat == "prelocked":
                persons = set()
                for user in dj.judges.all():
                    persons.add(user)
                try:
                    persons.add(dept_manager("软件部"))
                except:
                    pass
                r = Requirement.objects.filter(index=index)
                ancestor = r[0].author
                project = r[len(r)-1].project
                persons.add(myboss(ancestor))
                persons.add(pm(project))
                for i in persons:
                    djc = DevJudgementConfirm.objects.create(devjudge=dj,user=i,signed=False)
                
                stage = u"dev" 
                message = u"devjudge was locked by %s"%request.user.username
                if version == "":
                    html = u'研发评审中 <a href="/viewdevjudge/%s/">查看研发评审</a> <a href="/viewdev/%s">查看研发</a>'%(index,index)
                else:
                    html = u'研发评审中 <a href="/viewdevjudge/%s/">查看研发评审</a> <a href="/viewdev/%s">查看研发</a> <sup><font color=red>第%s次修正</font></sup> \
                            <a href="/history/%s/"><sup> 历史</sup></a>'%(index,index,version,index)
                log = History(requirement=r[len(r)-1],stage=stage,stat=stat,message=message,html=html,finished=False)
                log.save()
                    
                try :# to mail them to confirm
                    message=u"<a href=\"%s/viewdevjudge/%s/\"> %s/viewdevjudge/%s/</a>"%(settings.SERVER_ROOT,index,settings.SERVER_ROOT,index,)
                    myemail=request.user.email
                    author = request.user.first_name
                    email_to=[]
                    for i in persons:
                        email_to.append(i.email)
                    msg = EmailMessage(u'[%s]请您对软件需求表(%s号：%s)进行研发评审会签'%(author,index,r[0].require_name),message, myemail, email_to)
                    msg.content_subtype = "html"
                    msg.send()
                except:
                    pass

                content.update({"message":"研发评审已保存，并且已经定稿",})
                return render_to_response("jforms/message.html",content)
            content.update({"message":"研发评审已保存",})
            return render_to_response("jforms/message.html",content)
        else:
            content["devjudge"]=djf
            groups = Group.objects.all()
            content.update({"groups":groups})
            return render_to_response('jforms/devjudge.html',content)
            
    dj = DevJudgement.objects.filter(dev=d)
    if len(dj) != 0:
        dj = dj[len(dj)-1]
        content.update({"dj":dj})
        if dj.stat == "prelocked" or dj.stat == "locked":
            content.update({"message":"该编号研发评审已经定稿，无法再次修改",})
            return render_to_response("jforms/message.html",content)
        j = DevJudgeEditForm(instance=dj)
    else:
        j = DevJudgeForm()
    content["devjudge"]=j
    groups = Group.objects.all()
    content.update({"groups":groups})
    return render_to_response('jforms/devjudge.html',content)
        

def viewdevjudge(request,index):
    content={}
    content.update({"index":index})
    if request.user.is_authenticated():
        content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    d = Development.objects.filter(requirement=r)
    d = d[len(d)-1]
            
    dj = DevJudgement.objects.filter(dev=d)
    if len(dj) != 0:
        dj = dj[len(dj)-1]
        j = DevJudgeEditForm(instance=dj)
    content["devjudge"]=j
    judges = DevJudgementConfirm.objects.filter(devjudge=dj)
    content.update({"judges":judges})
    return render_to_response('jforms/viewdevjudge.html',content)

def viewdevjudge_id(request,id):
    content={}
    if request.user.is_authenticated():
        content.update({"username":request.user.first_name})
            
    dj = DevJudgement.objects.get(id=id)
    j = DevJudgeEditForm(instance=dj)
    content["devjudge"]=j
    judges = DevJudgementConfirm.objects.filter(devjudge=dj)
    content.update({"judges":judges})
    return render_to_response('jforms/viewdevjudge.html',content)

@login_required(login_url="/login/")
def devjudgeconfirm(request,username,index):
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
        password=request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            djc = DevJudgementConfirm.objects.get(devjudge=dj,user=user)
            djc.signed = True
            djc.time = datetime.datetime.now()
            djc.save()
            s = DevJudgementConfirm.objects.filter(devjudge=dj)
            done = True
            for i in s:
                if i.signed == False:
                    done = False
                    break
            if done == True:
                dj.stat = "locked"
                dj.save()
                #log
                q1 = Q(version__isnull=False)
                q2 = Q(requirement=r)
                ver = Development.objects.filter(q1&q2)
                if len(ver) == 0:
                    version = ""
                else:
                    version = ver[len(ver)-1].version+1

                if dj.result == "test":
                    stage = u"dev"
                    message = u"devjudge done:test"
                    if version == "":
                        html =  u'<a href="/testjudge/%s">新建测试评审</a> <a href="/viewdev/%s">查看研发</a> <a href="/viewdevjudge/%s/">查看研发评审</a>'%(index,index,index)
                    else:
                        html =  u'<a href="/testjudge/%s">新建测试评审</a> <sup><font color=red>第%s次修正</font></sup> <a href="/viewdev/%s">查看研发</a> \
                                    <a href="/viewdevjudge/%s/">查看研发评审</a>'%(index,version,index,index,)
                    log = History(requirement=r,stage=stage,stat=dj.stat,message=message,html=html,finished=False)
                    log.save()

                elif dj.result == "success":
                    stage = u"dev"
                    message = u"devjudge done :success"
                    if version == "":
                        html = u'<font color=green>研发完成</font> <a href="/viewdev/%s">查看研发</a> <a href="/viewdevjudge/%s/">查看研发评审</a>'%(index,index)
                    else:
                        html = u'<font color=green>研发完成</font> <a href="/viewdev/%s">查看研发</a> <a href="/viewdevjudge/%s/">查看研发评审</a> \
                                <a href="/history/%s/"><sup> 历史</sup></a>'%(index,index,version)
                    stat = dj.result
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=True)
                    log.save()

                elif dj.result == "amend":
                    q1 = Q(version__isnull=False)
                    q2 = Q(requirement=r)
                    last_d = Development.objects.filter(q1&q2)
                    if len(last_d) == 0:
                        d.version=1
                        d.ifpass = False
                        d.save()
                    else:
                        last = last_d[len(last_d)-1]
                        d.version = last.version+1
                        d.ifpass = False
                        d.save()
                    #log
                    stage = u"dev"
                    version = d.version
                    message = u"devjudge done :amend "
                    html = u'<a href="/dev/%s/">编辑研发<a> <sup><font color=red>第%s次修正</font></sup> <a href="/history/%s"> <sup>历史</sup> </a>'%(index,version,index)
                    stat = dj.result
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                    log.save()

                elif dj.result == "failure":
                    stage = u"dev"
                    message = u"devjudge done :failure "
                    if version == "":
                        html = u'<font color=green>研发完成</font> <a href="/viewdev/%s">查看研发</a> <a href="/viewdevjudge/%s/">查看研发评审</a>'%(index,index)
                    else:
                        html = u'<font color=green>研发完成</font> <a href="/viewdev/%s">查看研发</a> <a href="/viewdevjudge/%s/">查看研发评审</a> \
                                <a href="/history/%s/"><sup> 历史</sup></a>'%(index,index,version)
                    stat = dj.result
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=True)
                    log.save()
                
            content.update({"message":"会签成功"})
        else:
            content.update({"message":"密码错误,会签失败"})
        return render_to_response('jforms/message.html',content)

    return render_to_response('jforms/testconfirm.html',content)

def viewdev_id(request,id):
    content={}
    if request.user.is_authenticated():
        content.update({"username":request.user.first_name})
    d = Development.objects.get(id=id) 
    content.update({"dev":d})
    return render_to_response('jforms/viewdev.html',content)









