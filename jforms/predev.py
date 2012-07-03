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

def predev(request, index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    if request.method == "POST":
        j = PreDevelopment.objects.filter(requirement=r) 
        if len(j) != 0:
            d = j[len(j)-1]
            if d.stat == "locked" and d.version is None:
                content.update({"message":"已经锁定，无法再进行修改",})
                return render_to_response("jforms/message.html",content)
        author = request.user
        bg = request.POST.get("bg","")
        design = request.POST.get("design","")
        stat = request.POST.get("stat","unlocked")
        p = PreDevelopment(requirement=r,author=author,bg=bg,design=design,stat=stat)
        p.save()
        #log
        stage = u"predev"
        message = u"predev was edited by %s"%request.user.username
        html = u'<a href="/predev/%s">编辑预研</a>'%(index,)
        log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
        log.save()
        if stat == "locked":
            #log        
            stage = u"predev"
            message = u"predev was locked by %s"%request.user.username
            html = u'<a href="/predevjudge/%s/">新建预研评审</a> <a href="/viewpredev/%s">查看预研</a>'%(index,index)
            log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
            log.save()
    
            return render_to_response("jforms/message.html",{"message":"本次预研结束"})
        return render_to_response("jforms/message.html",{"message":"本次已经保存，下次可继续进行修改",})
    
    j = PreDevelopment.objects.filter(requirement=r) 
    if len(j) != 0:
        d = j[len(j)-1]
        if d.ifpass == True:
            content.update({"message":"预研已结束,并且已经通过测试评审",})
            return render_to_response("jforms/message.html",content)
        if d.stat == "locked" and d.version is None:
            content.update({"message":"预研已结束,需求处于后续评审中，无法进行修改",})
            return render_to_response("jforms/message.html",content)
        else:     
            content.update({"dev":d})
    return render_to_response('jforms/predev.html',content)

#内部验证(可行性分析报告)
def predevjudge(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    content.update({"req":r})
    ass = Assessment.objects.filter(requirement=r)
    ass = ass[len(ass)-1]
    content.update({"ass":ass})
    d = PreDevelopment.objects.filter(requirement=r)
    d = d[len(d)-1]
    if request.method == "POST":
        last = PreDevJudgement.objects.filter(predev=d)
        if len(last) >0:
            last = last[len(last)-1]
            last_testapply = last.testapply
            last_testreport = last.testreport
        else:
            last_testapply = None
            last_report = None
        try:  
            testapply = request.FILES.get("testapply",None)
            if testapply == None:
                testapply = last_testapply
        except:
            pass
        try:
            testreport = request.FILES.get("testreport",None)
            if testreport == None:
                testreport = last_testreport
        except:
            pass
        stat = request.POST.get("stat","unlocked")
        pdjef = PreDevJudgeEditForm(request.POST)
        if pdjef.is_valid():
            pdj = pdjef.save()
            pdj.predev = d
            pdj.testapply = testapply
            pdj.testreport = testreport
            pdj.author = request.user
            pdj.stat = stat
            pdj.save()
            #log
            stage = u"predev"
            message = u"predevjudge was edited by %s"%request.user.username
            html = u'<a href="/predevjudge/%s/">编辑预研评审</a> <a href="/viewpredev/%s">查看预研</a> <a href="/viewpredevjudge/%s/">查看评审详情</a>'%(index,index,index)
            log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
            log.save()

            content.update({"message":"预研评审已经保存."})
            if stat == "prelocked":
                persons = set()
                for i in pdj.judges.values():
                    user = User.objects.get(id=i["id"])
                    persons.add(user)
                try:
                    persons.add(dept_manager("软件部"))
                    if pdj.testreport :
                        persons.add(dept_manager("测试部"))
                except:
                    pass
                r = Requirement.objects.filter(index=index)
                ancestor = r[0].author
                project = r[len(r)-1].project
                persons.add(myboss(ancestor))
                persons.add(pm(project))
                for i in persons:
                    pdjc = PreDevJudgementConfirm.objects.create(predevjudge=pdj,user=i,signed=False)
                #log
                stage = u"predev"
                message = u"predevjudge was locked by %s"%request.user.username
                html = u'预研评审会签中 <a href="/viewpredev/%s">查看预研</a> <a href="/viewpredevjudge/%s/">查看评审详情</a>'%(index,index)
                log = History(requirement=r[len(r)-1],stage=stage,stat=stat,message=message,html=html,finished=False)
                log.save()

                content.update({"message":"预研评审已经保存,并已定稿"})
            return render_to_response('jforms/message.html',content)
            
        else:
            pdj = PreDevJudgement.objects.filter(predev=d)
            if len(pdj) == 0:
                j = PreDevJudgeEditForm()
            else:
                pdj = pdj[len(pdj)-1]
                try:
                    content.update({"testapply_name":pdj.testapply.name.split("/")[-1]})
                    content.update({"testapply_url":pdj.testapply.url})
                except:
                    pass
                try:
                    content.update({"testreport_name":pdj.testreport.name.split("/")[-1]})
                    content.update({"testreport_url":pdj.testreport.url})
                except:
                    pass
            content.update({"predevjudge":pdjef}) 
            return render_to_response('jforms/predev_judge.html',content)
        
    pdj = PreDevJudgement.objects.filter(predev=d)
    if len(pdj) == 0:
        j = PreDevJudgeEditForm()
    else:
        pdj = pdj[len(pdj)-1]
        try:
            content.update({"testapply_name":pdj.testapply.name.split("/")[-1]})
            content.update({"testapply_url":pdj.testapply.url})
        except:
            pass
        try:
            content.update({"testreport_name":pdj.testreport.name.split("/")[-1]})
            content.update({"testreport_url":pdj.testreport.url})
        except:
            pass
        j = PreDevJudgeEditForm(instance=pdj) 
    content["predevjudge"]=j
    return render_to_response('jforms/predev_judge.html',content)

def predevconfirm(request,username,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})

    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    ass = Assessment.objects.filter(requirement=r)
    ass = ass[len(ass)-1]
    pd = PreDevelopment.objects.filter(requirement=r)
    pd = pd[len(pd)-1]
    pdj = PreDevJudgement.objects.filter(predev=pd)
    pdj = pdj[len(pdj)-1]
    if request.method == "POST":
        password=request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            pdjc = PreDevJudgementConfirm.objects.get(predevjudge=pdj,user=user)
            pdjc.signed = True
            pdjc.time = datetime.datetime.now()
            pdjc.save()
            s = PreDevJudgementConfirm.objects.filter(predevjudge=pdj)
            done = True
            for i in s:
                if i.signed == False:
                    done = False
                    break
            if done == True:
                pdj.stat = "locked"
                pdj.save()
                #log
                if pdj.result == "failure":
                    stage = u"predev"
                    message = u"predevjudge done "
                    html = u'<font color=red>研发放弃</font> <a href="/viewpredev/%s">查看预研</a> <a href="/viewpredevjudge/%s/">查看评审详情</a>'%(index,index)
                    stat = pdj.result 
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=True)
                    log.save()
                elif pdj.result == "success":
                    stage = u"predev"
                    message = u"predevjudge done "
                    html = u'<font color=green>需求完成</font> <a href="/viewpredev/%s">查看预研</a> <a href="/viewpredevjudge/%s/">查看评审详情</a>'%(index,index)
                    stat = pdj.result 
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=True)
                    log.save()
                elif pdj.result == "dev":
                    stage = u"predev"
                    message = u"predevjudge done "
                    html = u'<a href="/viewpredev/%s">查看预研</a> <a href="/viewpredevjudge/%s/">查看评审详情</a>'%(index,index)
                    stat = pdj.result
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                    log.save()
                    stage = u"dev"
                    message = u"predevjudge done"
                    html = u'<a href="/dev/%s">新建研发</a>'%(index,)
                    stat = pdj.stat
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                    log.save()

            content.update({"message":"会签成功"})
        else:
            content.update({"message":"密码错误,会签失败"})
        return render_to_response('jforms/message.html',content)
 
    return render_to_response('jforms/testconfirm.html',content)


def viewpredevjudge(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    content.update({"req":r})
    ass = Assessment.objects.filter(requirement=r)
    ass = ass[len(ass)-1]
    content.update({"ass":ass})
    d = PreDevelopment.objects.filter(requirement=r)
    d = d[len(d)-1]
    pdj = PreDevJudgement.objects.filter(predev=d)
    if len(pdj) == 0:
        j = PreDevJudgeEditForm()
    else:
        pdj = pdj[len(pdj)-1]
        try:
            content.update({"testapply_name":pdj.testapply.name.split("/")[-1]})
            content.update({"testapply_url":pdj.testapply.url})
        except:
            pass
        try:
            content.update({"testreport_name":pdj.testreport.name.split("/")[-1]})
            content.update({"testreport_url":pdj.testreport.url})
        except:
            pass
        j = PreDevJudgeEditForm(instance=pdj) 
    content["predevjudge"]=j
    pdjc = PreDevJudgementConfirm.objects.filter(predevjudge=pdj)
    content.update({"judges":pdjc})
    return render_to_response('jforms/view_predev_judge.html',content)
    
def viewpredev(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    j = PreDevelopment.objects.filter(requirement=r) 
    if len(j) != 0:
        d = j[len(j)-1]
        content.update({"dev":d})
    return render_to_response('jforms/viewpredev.html',content)
