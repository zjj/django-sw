#coding=utf-8
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
from django.conf import settings

def newrequirement(request):
    content = {}
    adduser(content,request.user)
    if request.method == "POST":
        r = RequirementForm(request.POST)
        if r.is_valid():
            require_name = r.cleaned_data['require_name']
            project = r.cleaned_data['project']
            hardware = r.cleaned_data['hardware']
            software_type = r.cleaned_data['software_type']
            describle = r.cleaned_data['describle']
            details = r.cleaned_data['details']
            only_predev = r.cleaned_data['only_predev']
            need_test = r.cleaned_data['need_test']
            expired_date = r.cleaned_data['expired_date']
            cc = r.cleaned_data['cc']
            executer = r.cleaned_data['executer']
            index=Requirement.objects.all()
            index=index.aggregate(Max("index")).values()[0]
            if index == None:
                index = 1 
            else:
                index += 1
            requirement = Requirement.objects.create(index=index,\
               require_name=require_name,\
               hardware=hardware,\
               software_type=software_type,\
               describle=describle,\
               details=details,\
               project=project,\
               need_test=need_test,\
               only_predev=only_predev,\
               expired_date=expired_date,\
               author=request.user,\
               stat="unlocked")
            requirement.executer = executer
            requirement.cc = cc
            requirement.save()           
            #log 
            stage = u"requirement"
            message = u"requirement was created by %s"%request.user.first_name
            stat = u"unlocked" 
            html = '<a href="/editrequirement/%s/">编辑需求</a> <a href="/viewrequirement/%s/"> 查看需求</a>'%(index,index,)
            log = History(requirement=requirement,stage=stage,stat=stat,message=message,html=html,finished=False)
            log.save()
        else:
            content.update({"requirement":r})
            groups = Group.objects.all()
            content.update({"groups":groups})
            return render_to_response('jforms/newrequirement.html',content)
        return render_to_response('jforms/new_successful.html',{"index":index})
    r = RequirementForm()
    content.update({"requirement":r})
    groups = Group.objects.all()
    content.update({"groups":groups})
    return render_to_response('jforms/newrequirement.html',content)

def editrequirement(request, index):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    content = {}
    content.update({"index":index})
    adduser(content,request.user)
    if request.method == "POST":
        last_r = Requirement.objects.filter(index=index)
        last_stat = last_r[len(last_r)-1].stat
        if last_stat == "prelocked" or last_stat == "locked":
            return render_to_response('jforms/message.html',{"message":u"需求无法进行修改"})

        r = RequirementForm(request.POST)
        if r.is_valid():
            require_name = r.cleaned_data['require_name']
            project = r.cleaned_data['project']
            hardware = r.cleaned_data['hardware']
            software_type = r.cleaned_data['software_type']
            describle = r.cleaned_data['describle']
            details = r.cleaned_data['details']
            only_predev = r.cleaned_data['only_predev']
            need_test = r.cleaned_data['need_test']
            expired_date = r.cleaned_data['expired_date']
            cc = r.cleaned_data['cc']
            executer = r.cleaned_data['executer']
            stat = request.POST.get('stat','unlocked')
            
            requirement = Requirement.objects.create(index=index,\
               require_name=require_name,\
               hardware=hardware,\
               software_type=software_type,\
               describle=describle,\
               details=details,\
               project=project,\
               need_test=need_test,\
               only_predev=only_predev,\
               expired_date=expired_date,\
               author=request.user,\
               stat=stat)
            requirement.cc = cc
            requirement.executer = executer
            requirement.save()
            #log 
            stage = u"requirement"
            message = u"requirement was edit by %s"%request.user.first_name
            html = '<a href="/editrequirement/%s/">编辑需求</a> <a href="/viewrequirement/%s/"> 查看需求</a>'%(index,index,)
            log = History(requirement=requirement,stage=stage,stat=stat,message=message,html=html,finished=False)
            log.save()

            if stat == "prelocked":
                persons = set()
                persons.add(myboss(request.user))
                persons.add(dept_manager(u"软件部")) 
                if executer is not None and len(executer)!=0 :
                    for i in executer:
                        persons.add(i)
                if project is not None :
                    persons.add(pm(project))
                    if project.sold == True:
                        persons.add(dept_manager(u"市场部")) 
                        persons.add(dept_manager(u"客服部"))
                        persons.add(dept_manager(u"销售部")) 
                for user in persons:
                    rc = RequirementConfirm.objects.create(requirement=requirement,signature=user,signed=False,accept=True)
                    rc.save()
                try:# to mail them to accept
                    message=u"<a href=\"%s/viewrequirement/%s/\"> %s/viewrequirement/%s/</a>"%(settings.SERVER_ROOT,index,settings.SERVER_ROOT,index,)
                    myemail=request.user.email
                    author = request.user.first_name
                    email_to=[]
                    for i in persons:
                        email_to.append(i.email)
                          
                    msg = EmailMessage(u'[%s]请您对软件需求表(%s号：%s)进行需求确认会签'%(author,index,require_name),message, myemail, email_to)
                    msg.content_subtype = "html"
                    msg.send()
                except:
                    pass
                
                try:# to mail them just to tell them
                    message=u"<a href=\"%s/viewrequirement/%s/\"> %s/viewrequirement/%s/</a>"%(settings.SERVER_ROOT,index,settings.SERVER_ROOT,index,)
                    myemail=request.user.email
                    author = request.user.first_name
                    email_to=[]
                    for i in cc:
                        email_to.append(i.email)
                    msg = EmailMessage(u'[%s]请您查看软件需求表(%s号：%s)'%(author,index,require_name),message, myemail, email_to)
                    msg.content_subtype = "html"
                    msg.send()
                except:
                    pass
                #log 
                stage = u"requirement"
                message = u"requirement was prelocked"
                stat = u"prelocked" 
                html = '需求确认中 <a href="/viewrequirement/%s/"> 查看需求</a>'%(index,)
                log = History(requirement=requirement,stage=stage,stat=stat,message=message,html=html,finished=False)
                log.save()

            return render_to_response('jforms/message.html',{"message":"本次修改已经保存","username":request.user.first_name})
        else:
            content.update({"requirement":r})
            groups = Group.objects.all()
            content.update({"groups":groups})
         
            r = Requirement.objects.filter(index=index)
            ancestor = r[0].author
            if len(r)!=0:
                r = r[len(r)-1]
                content.update({"req":r})
            groups = Group.objects.all()
            content.update({"groups":groups})
            if ancestor == request.user:
                content.update({"is_ancestor":"yes"})
            return render_to_response('jforms/editrequirement.html',content)
    
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    ancestor = r[0].author
    if len(r)!=0:
        r = r[len(r)-1]
        content.update({"req":r})
    if r.stat == "prelocked":
        return render_to_response('jforms/message.html',{"message":"需求确认中，无法进行修改"})
    if r.stat == "locked":
        return render_to_response('jforms/message.html',{"message":"需求已经确认，无法进行修改"})
    r = RequirementEditForm(instance=r)
    content.update({"requirement":r})
    groups = Group.objects.all()
    content.update({"groups":groups})
    if ancestor == request.user:
        content.update({"is_ancestor":"yes"})
    return render_to_response('jforms/editrequirement.html',content)


def viewrequirement(request, index):
    content = {}
    content.update({"index":index})
    adduser(content,request.user)
    #req
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    ancestor = r[0].author
    content.update({"ancestor":ancestor})
    
    ancestor.groups.all()[0].name
    content.update({"dept":ancestor.groups.all()[0].name})
    
    if len(r)!=0:
        r = r[len(r)-1]
    content.update({"executer":r.executer})
    content.update({"cc":r.cc})
    rc = RequirementConfirm.objects.filter(requirement=r)
    r = RequirementEditForm(instance=r)
    content.update({"requirement":r})
    content.update({"rc":rc}) 
    #ass
    try:
        r = Requirement.objects.filter(index=index)
        if len(r)!=0:
            r = r[len(r)-1]
        content.update({"req":r})
        assessment = Assessment.objects.filter(requirement=r)
        assessment = assessment[len(assessment)-1]
        assessor = assessment.assessor.values()
        content.update({"assessor":assessor})
        assessment = AssessmentEditForm(instance=assessment)
        content.update({"assessment":assessment})
    except:
        pass
    #judge
    try:
        rj = RequireJudgement.objects.filter(requirement=r)
        if len(rj) != 0:
            rj = rj[len(rj)-1]
            rjef = RequireJudgementEditForm(instance=rj)
            content.update({"rjef":rjef})
            s = RequireJudgementConfirm.objects.filter(requirement=r)
            content.update({"confirm":s})
    except:
        pass
        
    return render_to_response('jforms/viewrequirement.html',content)

def requirementconfirm(request,username,index):
    import sys 
    reload(sys)
    sys.setdefaultencoding('utf8') 
    if request.method == "POST":
        reason = request.POST.get("txt","")
        result = request.POST.get("result","")
        user = User.objects.get(username=username)
        r = Requirement.objects.filter(index=index)
        r = r[len(r)-1]
        rc = RequirementConfirm.objects.get(requirement=r,signature=user)
        if result == "accept":
            rc.accept = True
        else:
            rc.accept = False
            rc.reason = reason
        rc.whosigned = request.user
        rc.time = datetime.datetime.now()
        rc.signed = True
        rc.save()

        rcs = RequirementConfirm.objects.filter(requirement=r)
        done = True
        accept = True
        if len(rcs) != 0:
            for i in rcs:
                if  i.signed == True and i.accept == False :
                    accept = False
                if i.signed == False:
                    done = False
            
            if accept == False: 
                r.stat = "locked"
                r.save()
                #log
                stage = u"requirement"
                message = u"requirement was reject"
                stat = u"aborted"
                html = '<font color=red>有确认人员拒绝需求<font> <a href="/viewrequirement/%s/"> 查看详情</a>'%(index,)
                log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=True)
                log.save()
            else:
                if done == True:
                    r.stat = "locked"
                    r.save()
                    #log
                    stage = u"requirement"
                    message = u"requirement was accept"
                    stat = u"accept"
                    html = '<a href="/editassessment/%s/"> 新建风险评估 </a> <a href="/viewrequirement/%s/"> 查看需求详情</a>'%(index,index)
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                    log.save()
        return render_to_response("jforms/message.html",{"message":"需求确认成功！"});

    content = {}
    user = User.objects.get(username = username)
    if myboss(request.user) != user  and username != request.user.username:
        return render_to_response("jforms/message.html",{"message":"无权进行需求确认并且无权代理此人进行需求确认！"});
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    rc = RequirementConfirm.objects.get(requirement=r,signature=user)
    if rc.signed == True:
        if rc.whosigned == rc.signature:
            return render_to_response("jforms/message.html",{"message":"确认已经被用户本人确认"});
        else:
            return render_to_response("jforms/message.html",{"message":"确认已经由%s代理确认"%(rs.whosigned.first_name,)});

    if username == request.user.username:
        content.update({"agent":"no"})
    else:
        content.update({"agent":"yes"})
    
    content.update({"username":username})
    content.update({"index":index})
    return render_to_response('jforms/requirementconfirm.html',content)

def editassessment(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    if request.method == "POST":
        r = Requirement.objects.filter(index=index)
        if len(r)!=0:
            r = r[len(r)-1]
        exist = True
        last = Assessment.objects.filter(requirement=r)
        if len(last) != 0:
            last = last[len(last)-1]
            if last.stat == "locked":
                content.update({"message":"评估无法进行修改"})
                return render_to_response('jforms/message.html',content)
        else:
            exist = False
        ass = AssessmentForm(request.POST)
        if ass.is_valid():
            assessment = ass.cleaned_data["assessment"]
            need_predev = ass.cleaned_data["need_predev"]
            need_test = ass.cleaned_data["need_test"]
            assessor = ass.cleaned_data["assessor"]
            stat = request.POST.get("stat","unlocked")
            ass = Assessment.objects.create(requirement=r,author=request.user, \
                            assessment=assessment, need_test=need_test, need_predev=need_predev,stat=stat)
            ass.assessor = assessor
            ass.save()
            if stat == "locked":
                #log
                stage = u"requirement"
                message = u"assessment was locked by %s"%request.user.first_name
                html = u'<a href="/judgerequirement/%s/">新建需求评审</a> <a href="/viewrequirement/%s/"> 查看需求详情</a>'%(index,index,)
                stat = stat 
                log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                log.save()
            else:
                if exist == False: 
                    stage = u"requirement"
                    message = u"assessment was created by %s"%request.user.first_name
                    stat = stat 
                    html = u'<a href="/editassessment/%s/">编辑需求评估</a> <a href="/viewrequirement/%s/"> 查看需求详情</a>'%(index,index,)
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                    log.save()
                
            content.update({"message":"评估已保存"})
            return render_to_response('jforms/message.html',content)
            
    r = Requirement.objects.filter(index=index)
    if len(r)!=0:
        r = r[len(r)-1]
    content.update({"req":r})
    assessment = Assessment.objects.filter(requirement=r)
    if len(assessment) != 0:
        last = assessment[len(assessment)-1]
        if last.stat == "locked":
            content.update({"message":"评估无法进行修改"})
            return render_to_response('jforms/message.html',content)
    if len(assessment)!=0:
        assessment = assessment[len(assessment)-1]
        content.update({"ass":assessment})
        assessment = AssessmentEditForm(instance=assessment)
    else:
        assessment = AssessmentEditForm()
    content.update({"assessment":assessment})
    groups = Group.objects.all()
    content.update({"groups":groups})
    
    return render_to_response('jforms/editassessment.html',content)

def judgerequirement(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    if request.method == "POST":
        r = Requirement.objects.filter(index=index)
        if len(r) != 0:
            r=r[len(r)-1]
        exist = True
        last = RequireJudgement.objects.filter(requirement=r)
        if len(last) != 0:
            last = last[len(last)-1]
            if last.stat == "locked" or last.stat == "prelocked":
                content.update({"message":"评审无法进行修改"})
                return render_to_response('jforms/message.html',content)
        else:
            exist = False
        rj = RequireJudgementForm(request.POST)
        if rj.is_valid():
            judgement = rj.cleaned_data["judgement"]
            result = rj.cleaned_data["result"]
            judges = rj.cleaned_data["judges"]
            stat = request.POST.get("stat","unlocked")
            rj = RequireJudgement.objects.create(requirement=r,author=request.user, \
                            judgement=judgement,result=result,stat=stat)
            rj.judges = judges
            rj.save()
            if stat == "prelocked":
                #log
                stage = u"requirement"
                message = u"judgement was prelocked by %s"%request.user.first_name
                html = u'需求评审会签中 <a href="/judgerequirementview/%s/">需求评审详情</a>'%(index,)
                stat = stat 
                log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                log.save()
                #
                persons = set()
                r = Requirement.objects.filter(index=index)
                ancestor = r[0].author
                project = r[len(r)-1].project
                persons.add(myboss(ancestor))
                persons.add(myboss(request.user))
                persons.add(dept_manager("软件部")) 
                if judges is not None and len(judges)!=0 :
                    for i in judges:
                        persons.add(i)
                if project is not None :
                    persons.add(pm(project))
                for user in persons:
                    rc = RequireJudgementConfirm.objects.create(requirement=r[len(r)-1],user=user,signed=False)
                    rc.save()
                #email them
                try :# to mail them to accept
                    message="<a href=\"%s/judgerequirementview/%s/\"> %s/judgerequirementview/%s/</a>"%(settings.SERVER_ROOT,index,settings.SERVER_ROOT,index,)
                    myemail=request.user.email
                    author = request.user.first_name
                    email_to=[]
                    for i in persons:
                        email_to.append(i.email)
                    msg = EmailMessage('[%s]请您对软件需求表(%s号：%s)进行需求评审会签'%(author,index,r[0].require_name),message, myemail, email_to)
                    msg.content_subtype = "html"
                    msg.send()
                except:
                    pass
            
            else:
                if exist == False: 
                    stage = u"requirement"
                    message = u"judgement was created by %s"%request.user.first_name
                    stat = stat 
                    html = u'<a href=/judgerequirement/%s/>编辑需求评审 <a href="/viewrequirement/%s/"> 需求详情</a>'%(index,index,)
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                    log.save()
            content.update({"message":"评审已保存"})
            return render_to_response('jforms/message.html',content)

    r = Requirement.objects.filter(index=index)
    if len(r) != 0:
        r=r[len(r)-1]
    rj = RequireJudgement.objects.filter(requirement=r)
    if len(rj) != 0:
        rj = rj[len(rj)-1]
        content.update({"rj":rj})
        if rj.stat == "locked" or rj.stat == "prelocked":
            content.update({"message":"评审无法进行修改"})
            return render_to_response('jforms/message.html',content)
        rjef = RequireJudgementEditForm(instance=rj)
    else:
        rjef = RequireJudgementEditForm()
    content.update({"rjef":rjef})

    groups = Group.objects.all()
    content.update({"groups":groups})
    
    return render_to_response('jforms/requirejudement.html',content)

def judgerequirementconfirm(request,username, index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    if request.method == "POST":
        password=request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            r = Requirement.objects.filter(index=index)
            r = r[len(r)-1]
            s = RequireJudgementConfirm.objects.get(requirement=r,user=user)
            s.signed = True
            s.time = datetime.datetime.now()
            s.save()
            s = RequireJudgementConfirm.objects.filter(requirement=r)
            done = True
            for i in s:
                if i.signed == False:
                    done = False
                    break
            if done == True:
                p = RequireJudgement.objects.filter(requirement=r)
                if len(p) != 0:
                    p = p[len(p)-1]
                    p.stat = "locked"
                    p.save()
                    
                    if p.result != "reject":
                        q1 = Q(project=r.project)
                        q2 = Q(p_index__isnull=False)
                        items_of_project = Requirement.objects.filter(q1&q2)
                        if len(items_of_project) == 0:
                            r.p_index = 1
                        else:
                            item = items_of_project[len(items_of_project)-1]
                            r.p_index = item.p_index+1
                        r.save()
  
                    #log
                    stage = u"requirement"
                    message = u"judgement signature done:%s"%p.result
                    stat = p.stat
                    if p.result == "develop":
                        html = u'<a href="/viewrequirement/%s/">查看需求详情</a>'%(index,)
                        log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                        log.save() 
                        stage = "dev"
                        html = u'<a href="/dev/%s/">新建研发</a>'%(index,) 
                        log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                        log.save()
                    elif p.result == "predev":
                        html = u'<a href="/viewrequirement/%s/">查看需求详情</a>'%(index,)
                        log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                        log.save()
                        stage = u"predev"
                        html = u'<a href="/predev/%s/">新建预研</a>'%(index,)
                        log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                        log.save()
                    elif p.result == "reject":
                        html = u'<font color=red>需求评审结束，需求拒绝</font> <a href="/viewrequirement/%s/">查看需求详情</a>'%(index,)
                        log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=True)
                        log.save()

            content.update({"message":"评审会签成功"})
            return render_to_response("jforms/message.html",content);
        else:
            content.update({"message":"未通过验证，会签失败"})
            return render_to_response("jforms/message.html",content);
    
    r = Requirement.objects.filter(index=index)
    r =r[len(r)-1]
    user = User.objects.get(username=username)
    s = RequireJudgementConfirm.objects.get(requirement=r,user=user)
    if s.signed == True:
            content.update({"message":"该用户已经对评审进行会签"})
            return render_to_response("jforms/message.html",content);
     
    return render_to_response('jforms/requirejudementconfirm.html',content)
     
def judgerequirementview(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    if len(r) != 0:
        r=r[len(r)-1]
    rj = RequireJudgement.objects.filter(requirement=r)
    if len(rj) != 0:
        rj = rj[len(rj)-1]
        rjef = RequireJudgementEditForm(instance=rj)
        content.update({"rjef":rjef})
        s = RequireJudgementConfirm.objects.filter(requirement=r)
        content.update({"confirm":s})
        return render_to_response('jforms/requirejudementview.html',content)
    else:
        content.update({"message":"暂时无该编号的需求评审查看"})
        return render_to_response('jforms/message.html',content)

def viewassessment(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    if len(r)!=0:
        r = r[len(r)-1]
    content.update({"req":r})
    assessment = Assessment.objects.filter(requirement=r)
    assessment = assessment[len(assessment)-1]
    assessor = assessment.assessor.values()
    content.update({"assessor":assessor})
    assessment = AssessmentEditForm(instance=assessment)
    content.update({"assessment":assessment})
    return render_to_response('jforms/viewassessment.html',content)

