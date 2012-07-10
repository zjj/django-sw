#coding=utf-8
from django.db import models
from django.contrib.auth.models import Group, User

class Project(models.Model):
    project = models.CharField(max_length=1000)
    sold = models.BooleanField()
    pm =  models.ForeignKey(User)
    class Meta:
        verbose_name_plural = "项目"
        verbose_name = "项目"
   
    def __unicode__(self):
        return self.project

class SoftwareType(models.Model):
    software_type = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "软件类型"
        verbose_name = "软件类型"

    def __unicode__(self):
        return self.software_type

class Hardware(models.Model):
    hardware = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "硬件平台"
        verbose_name = "硬件平台"
    
    def __unicode__(self):
        return self.hardware

class Dept(models.Model):
    group = models.ForeignKey(Group)
    manager = models.ForeignKey(User)
    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"

    def __unicode__(self):
        return unicode(self.group)

    
class Requirement(models.Model):
    index = models.IntegerField() 
    require_name = models.CharField(max_length=500)
    project = models.ForeignKey(Project,null=True) 
    hardware = models.ForeignKey(Hardware,null=True) 
    software_type = models.ForeignKey(SoftwareType,null=True)
    describle = models.TextField() 
    details = models.TextField() 
    author = models.ForeignKey(User)
    expired_date = models.DateTimeField()
    time = models.DateTimeField(auto_now=True)
    need_test = models.BooleanField()
    only_predev = models.BooleanField() 
    executer = models.ManyToManyField(User,related_name='+',null=True)
    cc = models.ManyToManyField(User,related_name='++',null=True)
    stat = models.CharField(max_length=10)  #unlocked prelocked locked
    class Meta:
        verbose_name = "需求"
        verbose_name_plural = "需求"

    def __unicode__(self):
        return unicode(self.index)


class RequirementConfirm(models.Model):
    requirement = models.ForeignKey(Requirement)
    signature = models.ForeignKey(User)
    whosigned = models.ForeignKey(User,related_name="+",null=True)
    reason = models.TextField()
    accept = models.BooleanField() 
    signed = models.BooleanField() 
    time = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "需求确认会签"    
        verbose_name_plural = "需求确认会签"

class History(models.Model):
    requirement = models.ForeignKey(Requirement)
    stage = models.CharField(max_length=1000)
    statchange = models.CharField(max_length=1000)
    message = models.CharField(max_length=1000,null=True)
    time = models.DateTimeField(auto_now=True)
   
class Assessment(models.Model):
    requirement = models.ForeignKey(Requirement)
    author = models.ForeignKey(User) 
    assessment = models.TextField()
    need_predev = models.BooleanField()
    assessor = models.ManyToManyField(User,related_name="+++")
    stat = models.CharField(max_length=10)  #unlocked locked
    time = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "风险评估"    
        verbose_name_plural = "风险评估"

class RequireJudgement(models.Model):
    requirement = models.ForeignKey(Requirement)
    author = models.ForeignKey(User) 
    judgement = models.TextField()
    judges = models.ManyToManyField(User,related_name="++++")
    result = models.CharField(max_length=1000)
    stat = models.CharField(max_length=10)  #unlocked prelocked locked
    time = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "需求评审"    
        verbose_name_plural = "需求评审"
    
class RequireJudgementConfirm(models.Model):
    requirement = models.ForeignKey(Requirement)
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now=True)
    signed = models.BooleanField() 
    class Meta:
        unique_together = ('requirement', 'user')

class Development(models.Model):
    requirement = models.ForeignKey(Requirement)
    author = models.ForeignKey(User) 
    version = models.IntegerField(null=True)
    bg = models.TextField() # background and development enviroment 
    design= models.TextField()
    time = models.DateTimeField(auto_now=True)
    stat = models.CharField(max_length=10) # unlocked  locked
    ifpass = models.BooleanField() 

class DevJudgement(models.Model):
    dev = models.ForeignKey(Development)
    author = models.ForeignKey(User) 
    bg = models.TextField() #背景
    testinside = models.TextField() #内部测试
    judgement = models.TextField() # 评审记录
    result = models.CharField(max_length=100)
    judges = models.ManyToManyField(User,related_name="+++++")
    time = models.DateTimeField(auto_now=True)
    stat = models.CharField(max_length=10) # unlocked  locked

class TestJudgement(models.Model):
    predevjudge = models.ForeignKey(DevJudgement,null=True) #***here ,should PreDevJudgement***
    devjudge = models.ForeignKey(DevJudgement,null=True)
    author = models.CharField(max_length=100)
    overview = models.TextField()
    judgement = models.TextField()
    result = models.CharField(max_length=100)
    judges = models.CharField(max_length=1000)
    date = models.DateTimeField(null=True)
    explain = models.TextField(null=True)
    time = models.DateTimeField(auto_now=True)
    stat = models.CharField(max_length=10) # unlocked  locked done
    testapply = models.FileField(upload_to="files/%Y/%m/%d")
    testreport = models.FileField(upload_to="files/%Y/%m/%d")

class TestJudgementConfirm(models.Model):
    signature = models.ForeignKey(User)
    signed = models.BooleanField() 
    time = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "测试评审会签"    
        verbose_name_plural = "测试评审会签"


    
    
    
    






