# Create your views here.
from django.contrib.auth.models import User 
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response

def emailbook(request):
    list = User.objects.all()
    content={"list":list}
    return render_to_response('account/emailbook.html',content)

def inputtest(request):
    return render_to_response('account/inputtest.html')
    
