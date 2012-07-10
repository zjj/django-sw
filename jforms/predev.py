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
    





























































