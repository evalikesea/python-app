from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
'''
Django Auth模块自带User模型所包含字段
username：用户名
email: 电子邮件
password：密码
first_name：名
last_name：姓
is_active: 是否为活跃用户。默认是True
is_staff: 是否为员工。默认是False
is_superuser: 是否为管理员。默认是False
date_joined: 加入日期。系统自动生成。
'''

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_query_name='profile')
    org = models.CharField(
        'Organization', max_length=128, blank=True)
    telephone = models.CharField(
        'Telephone', max_length=50, blank=True)
    mod_date = models.DateTimeField(
        'Last modified', auto_now=True)

    class Meta:
        verbose_name = 'User Profile'

    def __str__(self):
        return self.user