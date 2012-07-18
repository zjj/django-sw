#coding=utf-8
from django.shortcuts import render_to_response

def handler403(request):
    content = {}
    if request.user.is_authenticated():
        content.update({"username":request.user.first_name})
    return render_to_response("jforms/message.html",{"message":"没有权限执行该操作",}) 


