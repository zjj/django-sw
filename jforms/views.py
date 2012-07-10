from django.shortcuts import render_to_response
from jforms.functions import *
def myhome(request):
    content = {}
    adduser(content,request.user)
    return render_to_response("jforms/myhome.html", content)
