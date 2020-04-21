#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
#@ Author    :   Eva.Chen
#@ Contact   :   1985467552@qq.com
#@ Time      :   2020/4/11 4:36 下午
#@ Desc      :   None
'''
from django import forms
from django.contrib.auth.models import User
from django.forms import TextInput
import re

def email_check(email):
    pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
    return re.match(pattern, email)
# 自定义验证规则
def telephone_check(telephone):
    pattern = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
    if not re.match(pattern, telephone):
        raise forms.ValidationError("手机号格式不正确")

class RegistrationForm(forms.Form):

    username = forms.CharField(label='Username', max_length=50)
    email = forms.EmailField(label='Email',)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < 6:
            raise forms.ValidationError("Your username must be at least 6 characters long.")
        elif len(username) > 50:
            raise forms.ValidationError("Your username is too long.")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your username already exists.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email_check(email):
            filter_result = User.objects.filter(email__exact=email)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your email already exists.")
        else:
            raise forms.ValidationError("Please enter a valid email.")

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < 6:
            raise forms.ValidationError("Your password is too short.")
        elif len(password1) > 20:
            raise forms.ValidationError("Your password is too long.")

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2

class LoginForm(forms.Form):

    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        filter_result = User.objects.filter(username__exact=username)
        if not filter_result:
            raise forms.ValidationError("This username does not exist. Please register first")

        return username

class ProfileForm(forms.Form):
    first_name = forms.CharField(label='名', widget=TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='姓', widget=TextInput(attrs={'class': 'form-control'}))
    telephone = forms.CharField(validators=[telephone_check], label='电话', widget=TextInput(attrs={'class': 'form-control'}))
    org = forms.CharField(label='公司', widget=TextInput(attrs={'class': 'form-control'}))

class PwdChangeForm(forms.Form):
    old_password = forms.CharField(label='旧密码', widget=TextInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label='新密码', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput)
    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')

        if len(password1) < 6:
            raise forms.ValidationError("Your password is too short.")
        elif len(password1) > 20:
            raise forms.ValidationError("Your password is too long.")

        return password1

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2