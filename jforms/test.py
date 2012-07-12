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
def testjudge(request,index):
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
    if len(tj) != 0:
        tj = tj[len(tj)-1]
        if tj.stat == "prelocked":
           content.update({"message":"测试评审暂时已经定稿，无法进行修改."})
           return render_to_response('jforms/message.html',content)
        if tj.stat == "locked":
           content.update({"message":"测试已经评审完毕，无法进行修改."})
           return render_to_response('jforms/message.html',content)

    if request.method == "POST":
        tj = TestJudgeEditForm(request.POST,request.FILES)
        stat = request.POST.get("stat","unlocked")
        if tj.is_valid():
            overview = tj.cleaned_data["overview"]
            judgement = tj.cleaned_data["judgement"]
            result = tj.cleaned_data["result"]
            testapply = tj.cleaned_data["testapply"]
            testreport = tj.cleaned_data["testreport"]
            explain = tj.cleaned_data["explain"]
            date = tj.cleaned_data["date"]
            judges = tj.cleaned_data["judges"]
            new_tj = TestJudgement.objects.create(devjudge=dj,author=request.user,overview=overview,\
                            judgement=judgement,result=result,testapply=testapply,date=date,\
                            testreport=testreport,explain=explain,stat=stat)
            new_tj.judges=judges
            new_tj.save()
        else:
            last_tj = TestJudgement.objects.filter(devjudge=dj)
            if len(last_tj) == 0:
                last_tj = TestJudgeEditForm(request.POST,request.FILES)
                content.update({"test":last_tj})
                return render_to_response('jforms/test.html',content)
            else:
               last_tj = last_tj[len(last_tj)-1]
            new_tj = TestJudgeEditForm(request.POST,request.FILES,instance=last_tj)
            new_tj = new_tj.save()
            new_tj.stat = stat
            new_tj.save()

        if stat == "prelocked":
            persons = set()
            for i in new_tj.judges.values():
                user = User.objects.get(id=i["id"])
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
            content.update({"message":"测试评审定稿"})
            return render_to_response('jforms/message.html',content)

        tj = TestJudgement.objects.filter(devjudge=dj)
        if len(tj) == 0:
            tj = None
        else:
            tj = tj[len(tj)-1]
        test = TestJudgeEditForm(instance=tj)
        content.update({"test":test})
        return render_to_response('jforms/test.html',content)

    tj = TestJudgement.objects.filter(devjudge=dj)
    if len(tj) == 0:
        test = TestJudgeEditForm()
    else:
        tj = tj[len(tj)-1]
        if tj.stat == "prelocked":
           content.update({"message":"测试评审暂时已经定稿，无法进行修改."})
           return render_to_response('jforms/message.html',content)
        if tj.stat == "locked":
           content.update({"message":"测试已经评审完毕，无法进行修改."})
           return render_to_response('jforms/message.html',content)
        test = TestJudgeEditForm(instance=tj)
    content.update({"test":test,})
    return render_to_response('jforms/test.html',content)

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
                #log
                stage = u"test_judge"
                message = u"test_judge signature done:%s"%tj.result
                statchange = tj.stat 
                log = History(requirement=r,stage=stage,statchange=statchange,message=message)
                log.save()
                
                if tj.result == "amend" or tj.result == "failure":
                    q = Q(version__isnull=False)
                    last_d = Development.objects.filter(q)
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
                    stage = u"test_judge"
                    message = u"test_judge signature done:%s"%tj.result
                    statchange = tj.stat 
                    log = History(requirement=r,stage=stage,statchange=statchange,message=message)
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
                    stage = u"test_judge"
                    message = u"test_judge signature done:%s"%tj.result
                    statchange = tj.stat 
                    log = History(requirement=r,stage=stage,statchange=statchange,message=message)
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

