# Create your views here.
#coding=utf-8
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User,Group 
from django import forms
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.mail import send_mail,get_connection
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
from django.conf import settings
from django.contrib.auth.views import login as jj_login
from django.contrib.auth.forms import PasswordChangeForm

class register_obj(forms.Form):
    username = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    password = forms.CharField(max_length=128)
    email = forms.EmailField()
    group = forms.CharField(max_length=100)

def register(request):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    if request.user.is_authenticated():
        return HttpResponse("you have been logged in ! <a href=\"%s\">Logout</a>"%reverse("account.views.logout"));    
    if request.method == "POST" and not request.user.is_authenticated():
        reg = register_obj(request.POST)
        if reg.is_valid():
            username = reg.cleaned_data['username'] 
            password = reg.cleaned_data['password'] 
            first_name = reg.cleaned_data['first_name'] 
            email = reg.cleaned_data['email']
            group = reg.cleaned_data['group']
            try:
                user = User.objects.get(username=username)
                return HttpResponse("username exists !");
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=email)
                    return HttpResponse("email has been used !");
                except User.DoesNotExist:
                    try:
                        user = User.objects.get(first_name=first_name)
                        return HttpResponse("the chinese name exists!")
                    except User.DoesNotExist:
                        user = User.objects.create_user(username=username,password=password,email=email)
                        user.first_name=first_name
                        groups = Group.objects.all()
                        for i in groups:
                            if i.name == group:
                                user.groups.add(i) 
                        user.save()
                        try:
                            message = "username :%s \npassword :%s\n"%(username,password)
                            send_mail("Register successful", message,'noreply@lemote.com',
                                    [email],fail_silently=True)
                        except:
                            pass
                        return render_to_response("account/register_successful.html")
        else:
            return HttpResponse("input not valid !");
    content={}
    g = Group.objects.all()
    groups = []
    for group in g:
        groups.append(group.name)
    content["groups"]=groups    
    return render_to_response('account/register.html',content)

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/login/")


def login(request):
    content = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request,user)
            return HttpResponseRedirect(request.POST['next'])
        else:
            auth_logout(request) 
            content.update({"message":u"您的账户暂时还没有被激活,将以匿名用户进行本站访问!"})
            return render_to_response("jforms/message.html",content)
    try:
        next = request.GET['next']
    except KeyError:
        next = "/myhome/"
    if request.user.is_authenticated():
        return HttpResponseRedirect("/myhome/")
    return render_to_response('account/login.html',{"next":next,})

def password_change(request):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    if request.method == "POST":
        old_password = request.POST['old_password']
        password = request.POST['password']
        username = request.user.username
        user = authenticate(username=username, password=old_password)
        ct={}
        if user is not None:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            ct["ret"]="yes"
        else:
            ct["ret"]="no"
        try:
            message = "username :%s \nnewpassword :%s\n"%(username,password)
            send_mail("password_change successful", message,'noreply@lemote.com',
                [user.email],fail_silently=True)
        except:
            pass
        return render_to_response('account/password_change_respond.html',ct)
    print request.user.first_name
    ct = {"username":request.user.first_name}
    return render_to_response('account/password_change.html',ct)
