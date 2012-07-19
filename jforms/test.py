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

#测试评审
@permission_required("jforms.change_testjudgement",login_url='/login/',raise_exception=True)
def testjudge(request,index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    groups = Group.objects.all()
    content.update({"groups":groups})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]

    h = History.objects.filter(requirement=r,finished=True)
    if len(h) != 0:
        content.update({"message":"该需求已结束",})
        return render_to_response("jforms/message.html",content)

    d = Development.objects.filter(requirement=r)
    d = d[len(d)-1]
    dj = DevJudgement.objects.filter(dev=d)
    dj = dj[len(dj)-1]

    if request.method == "POST": 
        tj = TestJudgement.objects.filter(devjudge=dj)
        if len(tj) > 0:
            tj = tj[len(tj)-1]
            content.update({"tj":tj})
            last_testapply = tj.testapply
            last_testreport = tj.testreport
        else:
            last_testapply = None
            last_testreport = None

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

        tjf = TestJudgeEditForm(request.POST,request.FILES)
        stat = request.POST.get("stat","unlocked")
        if tjf.is_valid():
            overview = tjf.cleaned_data["overview"]
            judgement = tjf.cleaned_data["judgement"]
            result = tjf.cleaned_data["result"]
            explain = tjf.cleaned_data["explain"]
            date = tjf.cleaned_data["date"]
            if date == u'':
                date = None
            judges = tjf.cleaned_data["judges"]
            new_tj = TestJudgement.objects.create(devjudge=dj,author=request.user,overview=overview,\
                            judgement=judgement,result=result,testapply=testapply,date=date,\
                            testreport=testreport,explain=explain,stat=stat)
            new_tj.judges=judges
            new_tj.save()
        else:
            try:
                content.update({"testapply_name":tj.testapply.name.split("/")[-1]})
                content.update({"testapply_url":tj.testapply.url})
            except:
                pass
            try:
                content.update({"testreport_name":tj.testreport.name.split("/")[-1]})
                content.update({"testreport_url":tj.testreport.url})
            except:
                pass

            content.update({"test":tjf})
            return render_to_response('jforms/test.html',content)

        #log
        q1 = Q(version__isnull=False)
        q2 = Q(requirement=r)
        ver = Development.objects.filter(q1&q2)
        if len(ver) == 0:
            version = ""
        else:
            version = ver[len(ver)-1].version+1
        stage = u"dev"
        message = u"testjudge was edited by %s "%request.user.username
        if version =="":
            html = u'<a href="/testjudge/%s">编辑测试评审</a> <a href="/testjudgeview/%s">查看测试评审</a> <a href="/viewdev/%s">查看研发</a> \
                    <a href="/viewdevjudge/%s/">查看研发评审</a>'%(index,index,index,index)
        else:
            html = u'<a href="/testjudge/%s">编辑测试评审</a> <sup><font color=red>第%s次修正</font></sup> <a href="/testjudgeview/%s">查看测试评审</a> <a href="/viewdev/%s">查看研发</a> \
                    <a href="/viewdevjudge/%s/">查看研发评审</a> <a href="/history/%s/"><sup>历史</sup></a>'%(index,version-1,index,index,index,index)
        stat = new_tj.stat
        log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
        log.save()

        if stat == "prelocked":
            persons = set()
            for user in new_tj.judges.all():
                persons.add(user)
            try:
                persons.add(dept_manager("软件部"))
                persons.add(dept_manager("测试部"))
            except:
                pass
            r = Requirement.objects.filter(index=index)
            ancestor = r[0].author
            project = r[len(r)-1].project
            persons.add(myboss(ancestor))
            persons.add(pm(project))
            for i in persons:
                tjc = TestJudgementConfirm.objects.create(testjudge=new_tj,signature=i,signed=False)
            #log
            stage = u"dev"
            message = u"testjudge was edited by %s "%request.user.username
            if version == "":
                html = u'测试评审中 <a href="/testjudgeview/%s">查看测试评审</a> <a href="/viewdev/%s">查看研发</a> \
                        <a href="/viewdevjudge/%s/">查看研发评审</a>'%(index,index,index)
            else:
                html = u'测试评审中 <a href="/testjudgeview/%s">查看测试评审</a> <a href="/viewdev/%s">查看研发</a> \
                        <a href="/viewdevjudge/%s/">查看研发评审</a> <a href="/history/%s/"><sup>历史</sup></a>'%(index,index,index,index)
            stat = new_tj.stat
            log = History(requirement=r[len(r)-1],stage=stage,stat=stat,message=message,html=html,finished=False)
            log.save()

            try :# to mail them to confirm
                message=u"<a href=\"%s/testjudgeview/%s/\"> %s/testjudgeview/%s/</a>"%(settings.SERVER_ROOT,index,settings.SERVER_ROOT,index,)
                myemail=request.user.email
                author = request.user.first_name
                email_to=[]
                for i in persons:
                    email_to.append(i.email)
                msg = EmailMessage(u'[%s]请您对软件需求表(%s号：%s)进行测试评审会签'%(author,index,r[0].require_name),message, myemail, email_to)
                msg.content_subtype = "html"
                msg.send()
            except:
                pass

            content.update({"message":"测试评审定稿"})
            return render_to_response('jforms/message.html',content)

    tj = TestJudgement.objects.filter(devjudge=dj)
    if len(tj) == 0:
        test = TestJudgeEditForm()
        last_testapply = None
        last_testreport = None
    else:
        tj = tj[len(tj)-1]
        content.update({"tj":tj})
        last_testapply = tj.testapply
        last_testreport = tj.testreport
        if tj.stat == "prelocked":
           content.update({"message":"测试评审暂时已经定稿，无法进行修改."})
           return render_to_response('jforms/message.html',content)
        if tj.stat == "locked":
           content.update({"message":"测试已经评审完毕，无法进行修改."})
           return render_to_response('jforms/message.html',content)
        test = TestJudgeEditForm(instance=tj)
    content.update({"test":test,})

    try:
        content.update({"testapply_name":last_testapply.name.split("/")[-1]})
        content.update({"testapply_url":last_testapply.url})
    except:
        pass
    try:
        content.update({"testreport_name":last_testreport.name.split("/")[-1]})
        content.update({"testreport_url":last_testreport.url})
    except:
        pass

    groups = Group.objects.all()
    content.update({"groups":groups})

    return render_to_response('jforms/test.html',content)

@login_required(login_url="/login/")
def testjudgeconfirm(request, username, index):
    content={}
    content.update({"index":index})
    content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    d = Development.objects.filter(requirement=r)
    d = d[len(d)-1]
    dj = DevJudgement.objects.filter(dev=d)
    dj = dj[len(dj)-1]
    tj = TestJudgement.objects.filter(devjudge=dj)
    tj = tj[len(tj)-1]

    if request.method == "POST":
        password=request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            tjc = TestJudgementConfirm.objects.get(testjudge=tj,signature=user)
            tjc.signed = True
            tjc.time = datetime.datetime.now()
            tjc.save()
            s = TestJudgementConfirm.objects.filter(testjudge=tj)
            done = True
            for i in s:
                if i.signed == False:
                    done = False
                    break
            if done == True:
                tj.stat = "locked"
                tj.save()
                
                if tj.result == "amend" or tj.result == "failure":
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
                    if tj.result == "amend":
                        stage = u"dev"
                        message = u"test_judge signature done:%s"%tj.result
                        stat = tj.stat
                        version = d.version
                        html = u'<a href="/dev/%s/">编辑研发<a><sup><font color=red>第%s次修正</font></sup>  <a href="/history/%s"> <sup>历史</sup> </a>'%(index,version,index)
                        log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=False)
                        log.save()
                    if tj.result == "failure":
                        stage = u"dev"
                        message = u"testjudge signature done: %s "%tj.result
                        version = d.version
                        if version == "":
                            html = u'<font color=red>研发失败,需求放弃</font><a href="/testjudgeview/%s">查看测试评审</a> <a href="/viewdev/%s">查看研发</a> \
                                    <a href="/viewdevjudge/%s/">查看研发评审</a>'%(index,index,index)
                        else:
                            html = u'<font color=red>研发失败,需求放弃</font><a href="/testjudgeview/%s">查看测试评审</a> <a href="/viewdev/%s">查看研发</a> \
                                    <a href="/viewdevjudge/%s/">查看研发评审</a>  <a href="/history/%s"> <sup>历史</sup> </a> '%(index,index,index,index)
                        stat = tj.stat
                        log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=True)
                        log.save()

                if tj.result == "success":
                    q = Q(version__isnull=False)
                    last_d = Development.objects.filter(q)
                    if len(last_d) == 0:
                        d.version=1
                        d.ifpass = True
                        d.save()
                    else:
                        last = last_d[len(last_d)-1]
                        d.version = last.version+1
                        d.ifpass = True
                        d.save()
                    #log
                    stage = u"dev"
                    message = u"test_judge signature done:%s"%tj.result
                    if d.version == 1:
                        html = u'<font color=green>研发成功,需求完成</font> <a href="/testjudgeview/%s">查看测试评审</a> <a href="/viewdev/%s">查看研发</a> \
                                   <a href="/viewdevjudge/%s/">查看研发评审</a>'%(index,index,index)
                    elif d.version > 1:
                        html = u'<font color=green>研发成功,需求完成</font> <a href="/testjudgeview/%s">查看测试评审</a> <a href="/viewdev/%s">查看研发</a> \
                                   <a href="/viewdevjudge/%s/">查看研发评审</a>  <a href="/history/%s"> <sup>历史</sup> </a>'%(index,index,index,index)
                    stat = tj.stat 
                    log = History(requirement=r,stage=stage,stat=stat,message=message,html=html,finished=True)
                    log.save()
                   
            content.update({"message":"测试评审会签成功"})
            return render_to_response("jforms/message.html",content);
        else:
            content.update({"message":"密码错误,测试评审会签失败"})
            return render_to_response("jforms/message.html",content);
    
    user = User.objects.get(username=username)
    s = TestJudgementConfirm.objects.get(signature=user,testjudge=tj)
    if s.signed == True:
        content.update({"message":"该用户已经对评审进行会签"})
        return render_to_response("jforms/message.html",content);

    return render_to_response('jforms/testconfirm.html',content)

def testjudgeview(request,index):
    content={}
    content.update({"index":index})
    if request.user.is_authenticated():
        content.update({"username":request.user.first_name})
    r = Requirement.objects.filter(index=index)
    r = r[len(r)-1]
    d = Development.objects.filter(requirement=r)
    d = d[len(d)-1]
    dj = DevJudgement.objects.filter(dev=d)
    dj = dj[len(dj)-1]
    tj = TestJudgement.objects.filter(devjudge=dj)
    tj = tj[len(tj)-1]
    testapply = {}
    testreport = {}
    try:
        testapply["url"] = tj.testapply.url
        testapply["name"] = tj.testapply.name.split("/")[-1]
    except:
        pass
    try:
        testreport["url"] = tj.testreport.url
        testreport["name"] = tj.testreport.name.split("/")[-1]
    except:
        pass
    content.update({"testapply":testapply})
    content.update({"testreport":testreport})
    s = TestJudgementConfirm.objects.filter(testjudge=tj)
    content.update({"judges":s}) 
    test = TestJudgeEditForm(instance=tj)
    content.update({"test":test,})
    return render_to_response('jforms/testview.html',content)

def viewtestjudge_id(request,id):
    content={}
    if request.user.is_authenticated():
        content.update({"username":request.user.first_name})
    tj = TestJudgement.objects.get(id=id)
    content.update({"index":tj.devjudge.dev.requirement.index})
    testapply = {}
    testreport = {}
    testapply["url"] = tj.testapply.url
    testapply["name"] = tj.testapply.name.split("/")[-1]
    testreport["url"] = tj.testreport.url
    testreport["name"] = tj.testreport.name.split("/")[-1]
    content.update({"testapply":testapply})
    content.update({"testreport":testreport})
    s = TestJudgementConfirm.objects.filter(testjudge=tj)
    content.update({"judges":s}) 
    test = TestJudgeEditForm(instance=tj)
    content.update({"test":test,})
    return render_to_response('jforms/testview.html',content)

