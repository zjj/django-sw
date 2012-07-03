#coding=utf-8
from django.db import models
from django.contrib.auth.models import Group, User

class Project(models.Model):
    project = models.CharField(max_length=1000)
    sold = models.CharField(max_length=100)#yes no
    pm =  models.ForeignKey(User)
    class Meta:
        verbose_name_plural = "项目"
        verbose_name = "项目"

class SoftwareType(models.Model):
    software_type = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "软件类型"
        verbose_name = "软件类型"


class Hardware(models.Model):
    hardware = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "硬件平台"
        verbose_name = "硬件平台"

class Dept(models.Model):
    group = models.ForeignKey(Group)
    manager = models.ForeignKey(User)
    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"


class Requirement(models.Model):
    index = models.IntegerField() 
    require_name = models.CharField(max_length=500)
    hardware = models.ForeignKey(Hardware) 
    software_type = models.ForeignKey(SoftwareType)
    describle = models.TextField() 
    details = models.TextField() 
    author = models.ForeignKey(User)
    project = models.ForeignKey(Project) 
    expired_date = models.DateTimeField()
    time = models.DateTimeField(auto_now=True)
    need_test = models.CharField(max_length=100) 
    only_predev = models.CharField(max_length=100) 
    persons_involved = models.ManyToManyField(User,related_name='+')
    stat = models.CharField(max_length=10)  #unlocked prelocked locked
    class Meta:
        verbose_name = "需求"
        verbose_name_plural = "需求"


