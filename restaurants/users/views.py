from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib import auth
from .forms import RegistrationForm, LoginForm, ProfileForm, PwdChangeForm
from django.http import HttpResponseRedirect
from django.urls import reverse

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']

            user = User.objects.create_user(username=username, password=password, email=email)
            user_profile = UserProfile(user=user)
            user_profile.save()

            return HttpResponseRedirect("/accounts/login/")
    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                if user.is_superuser:
                    return redirect('/admin/')
                else:
                    auth.login(request, user)
                    return HttpResponseRedirect(reverse('myrestaurants:restaurant_list', ))

            else:
                return render(request, 'users/login.html', {'form': form, 'message': 'Wrong password.Please try again'})

    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

def profile(request, pk):
    profile = get_object_or_404(UserProfile, user_id=pk)
    return render(request, 'users/profile.html', {'profile': profile})

def pwd_change(request, pk=None):
    if request.method == "POST":
        form = PwdChangeForm(request.POST)
        if form.is_valid():
            old_password = request.POST.get("old_password")
            new_password1 = request.POST.get("new_password1")
            new_password2 = request.POST.get("new_password2")
            # 得到当前登录的用户，判断旧密码是不是和当前的密码一样
            username = request.user  # 打印的是当前登录的用户名
            user = User.objects.get(id=pk)  # 查看用户
            ret = user.check_password(old_password)  # 检查密码是否正确
            if ret:
                user.set_password(new_password1)  # 如果正确就给设置一个新密码
                user.save()  # 保存
                return HttpResponseRedirect(reverse('users:login'))
            else:
                return render(request, "pwd_change.html", {"message": "输入密码有误"})
    else:
        form = PwdChangeForm()
    return render(request, 'users/pwd_change.html', {'form': form})

def profile_update(request,pk=None):
    profile = UserProfile.objects.get(user_id=pk)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk=pk)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            profile.telephone = form.cleaned_data['telephone']
            profile.org = form.cleaned_data['org']
            profile.save()
            return HttpResponseRedirect(reverse('users:profile', args=[pk]))
    else:
        form = ProfileForm(data={'first_name': profile.user.first_name,
                                 'last_name': profile.user.last_name,
                                 'org': profile.org,
                                 'telephone': profile.telephone})

    return render(request, 'users/profile_update.html', {'form': form})

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('users:login'))