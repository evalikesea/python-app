from django.db import models
from django.utils import timezone
import time, uuid
from .config import configs

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

# Create your models here.
class User(models.Model):
    id = models.CharField(primary_key=True, max_length=50, default=next_id)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=50)
    avatar = models.URLField(default=configs.get('default_avatar'))
    details_url = models.URLField(default=configs.get('default_detail'))
    admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    id = models.CharField(primary_key=True, max_length=50, default=next_id)
    user_id = models.CharField(max_length=50, default="")
    name = models.CharField(max_length=50)
    avatar = models.URLField(default=configs.get('default_avatar'))
    details_url = models.URLField(default=configs.get('default_detail'))
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Video(models.Model):
    id = models.CharField(primary_key=True, max_length=50, default=next_id)
    name = models.CharField(max_length=50)
    thumb = models.URLField(default=configs.get('default_thumb'))
    details_url = models.URLField(default=configs.get('default_video'))
    is_favorite = models.BooleanField(default=False)
    from_web = models.CharField(max_length=20, default="bilibili")
    public_time = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)