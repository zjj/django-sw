#coding=utf-8
import re 
from string import Template
from django import forms
from django.db.models import Q
from django.db.models import Max
from django.contrib.auth.models import User,Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from jforms.models import Requirement, Hardware, Project, SoftwareType, Assessment
from jforms.models import *
from django.core.mail import send_mail,EmailMessage
from django.shortcuts import render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.forms.models import modelformset_factory
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple, Select, SelectMultiple
from django.forms import ModelForm

class myModelMultipleChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return  "%s" % (obj.first_name,)

class RequirementForm(forms.Form):
    require_name = forms.CharField(max_length=100,label="需求名:",required=True)
    project = forms.ModelChoiceField(queryset=Project.objects.all(),label="所属项目:",empty_label="所属项目" ,required = False)
    hardware = forms.ModelChoiceField(queryset=Hardware.objects.all(),label="硬件平台:",empty_label="硬件类型",required = False) 
    software_type = forms.ModelChoiceField(queryset=SoftwareType.objects.all(),label="软件类型:",empty_label="软件类型",required = False)
    describle = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="需求背景与描述:")
    details = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="需求规格:",required = False)
    only_predev = forms.BooleanField(label="仅预研",required = False) 
    need_test = forms.BooleanField(label="需测试",required = False)
    expired_date = forms.CharField(widget=forms.DateTimeInput(attrs={'class':"vDateField"}),label="需求时间:",required = True)
    executer = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="需求接口人:",required = False)
    cc = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="其他通知人员:",required = False)

class RequirementEditForm(ModelForm):
    require_name = forms.CharField(max_length=100,label="需求名:",required=True)
    project = forms.ModelChoiceField(queryset=Project.objects.all(),label="所属项目:",empty_label="所属项目" ,required = False)
    hardware = forms.ModelChoiceField(queryset=Hardware.objects.all(),label="硬件平台:",empty_label="硬件类型",required = False) 
    software_type = forms.ModelChoiceField(queryset=SoftwareType.objects.all(),label="软件类型:",empty_label="软件类型",required = False)
    describle = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="需求背景与描述:")
    details = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="需求规格:",required = False)
    only_predev = forms.BooleanField(label="仅预研",required = False) 
    need_test = forms.BooleanField(label="需测试",required = False)
    expired_date = forms.CharField(widget=forms.DateTimeInput(format="%Y-%m-%d",attrs={'class':"vDateField"}),label="需求时间:",required = True)
    executer = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="需求接口人:",required = False)
    cc = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="其他通知人员:",required = False)
    
    class Meta:
        model = Requirement
        exclude = ('index','p_index','time')


class AssessmentEditForm(ModelForm):
    assessment = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="风险评估:")
    need_predev = forms.BooleanField(label="需预研",required = False)
    need_test = forms.BooleanField(label="预研需测试",required = False)
    assessor = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="评估方:",required = False)
    class Meta:
        model = Assessment
        fields = ("assessment","need_predev","need_test","assessor")

class AssessmentForm(forms.Form):
    assessment = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="风险评估:")
    need_predev = forms.BooleanField(label="需预研",required = False)
    need_test = forms.BooleanField(label="预研需测试",required = False)
    assessor = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="评估方:",required = False)
    assessor = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="评估方:",required = False)

REQUIRE_RESULT_CHOICES = (('develop','进行研发'),
                  ('predev','进行预研'),
                  ('reject', '拒绝'))

class RequireJudgementForm(forms.Form):
    judgement = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="评审内容:")
    result = forms.ChoiceField(widget=Select,choices=REQUIRE_RESULT_CHOICES,label="评审结论:",required = False)
    judges = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="评审人员:",required = False)

class RequireJudgementEditForm(ModelForm):
    judgement = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="评审内容:")
    result = forms.ChoiceField(widget=Select,choices=REQUIRE_RESULT_CHOICES,label="评审结论:",required = False)
    judges = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="评审人员:",required = False)
    class Meta:
        model = RequireJudgement
        fields = ("judgement","result","judges")

DEV_RESULT_CHOICES = (('test','提交测试'),
                  ('success','需求完成'),
                  ('amend','研发修正'),
                  ('failure', '需求放弃'))

class mybgTextarea(forms.Textarea):
        
    def render(self, name, value, attrs=None):
        if value is None: 
            value = """
<p>验证环境描述：</p> <table style="width: 410px; height: 197px;" border="1" align="left"> <tbody> <tr> <td>机型：</td> <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td> <td>&nbsp;CPU:</td> <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td> </tr> <tr> <td>PMON：</td> <td>&nbsp;</td> <td>&nbsp;Memory:</td> <td>&nbsp;</td> </tr> <tr> <td>EC：</td> <td>&nbsp;</td> <td>&nbsp;VGA:</td> <td>&nbsp;</td> </tr> <tr> <td>&nbsp;OS：</td> <td>&nbsp;</td> <td>&nbsp;Audio:</td> <td>&nbsp;</td> </tr> <tr> <td>&nbsp;EC Module:</td> <td>&nbsp;</td> <td>&nbsp;Lan:</td> <td>&nbsp;</td> </tr> <tr> <td>&nbsp;Kernel:</td> <td>&nbsp;</td> <td>&nbsp;Wifi:</td> <td>&nbsp;</td> </tr> <tr> <td>&nbsp;Fn Key:</td> <td>&nbsp;</td> <td>&nbsp;Camera:</td> <td>&nbsp;</td> </tr> </tbody> </table> 
"""
        return forms.Textarea.render(self,name,value,attrs)

class mytestTextarea(forms.Textarea):
    
    def render(self, name, value, attrs=None):
        if value is None: 
            value = """
<p>验证记录：</p>
<table style="width: 516px; height: 179px;" border="1" align="left">
<tbody>
<tr>
<td>验证项目</td>
<td>验证通过描述</td>
<td>结果</td>
<td>备注</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
"""
        return forms.Textarea.render(self,name,value,attrs)


class DevJudgeForm(forms.Form):
    bg = forms.CharField(widget=mybgTextarea(attrs={'cols': 80, 'rows': 20}),label="内部验证环境:")
    testinside = forms.CharField(widget=mytestTextarea(attrs={'cols': 80, 'rows': 20}),label="内部验证:")
    judgement = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="评审内容:")
    result = forms.ChoiceField(widget=Select,choices=DEV_RESULT_CHOICES,label="评审结论:",required = False)
    judges = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="评审人员:",required = False)

class DevJudgeEditForm(ModelForm):
    bg = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="内部验证环境:")
    testinside = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="内部验证:")
    judgement = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20 }),label="评审内容:")
    result = forms.ChoiceField(widget=Select,choices=DEV_RESULT_CHOICES,label="评审结论:",required = False)
    judges = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="评审人员:",required = False)
    class Meta:
        model = RequireJudgement
        fields = ("bg","testinside","judgement","result","judges")


TEST_RESULT_CHOICES = (('success','研发完成,需求结束'),
                  ('failure','研发放弃'),
                  ('amend', '需修正,继续研发'))

class TestJudgeEditForm(ModelForm):
    overview = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 10}),label="测试评审结论:")
    result = forms.ChoiceField(widget=Select,choices=TEST_RESULT_CHOICES,required = False)
    judgement = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="评审记录:")
    date = forms.CharField(widget=forms.DateTimeInput(format="%Y-%m-%d",attrs={'class':"vDateField"}),label="完成时间:",required = False)
    explain = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 10}),label="解释:",required=False)
    judges = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="评审人员:",required = False)
    class Meta:
        model = TestJudgement
        fields = ("overview","result","judgement","date","explain","judges",)


PREDEV_TEST_RESULT_CHOICES = (('success','满足需求,需求结束'),
                  ('failure','放弃'),
                  ('dev', '进行研发'))

class PreDevJudgeEditForm(ModelForm):
    overview = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 10}),label="结论概况:")
    result = forms.ChoiceField(widget=Select,choices=PREDEV_TEST_RESULT_CHOICES,required = True,label="评审结论")
    analysis = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="可行性分析报告:")
    judgement = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}),label="评审记录:")
    judges = myModelMultipleChoiceField(widget=CheckboxSelectMultiple,queryset=User.objects.all(),label="评审人员:",required = False)
    class Meta:
        model = PreDevJudgement
        fields = ("overview","result","analysis","judgement","judges",)


