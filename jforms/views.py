from django.shortcuts import render_to_response
from jforms.functions import *
def myhome(request):
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
            print ph.html
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

      


    return render_to_response("jforms/myhome.html", content)
