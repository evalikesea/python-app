from django.test import TestCase

# Create your tests here.
from django.http import HttpResponse

from favoriteVideo.models import Follow


# 数据库操作
def testdb(request):
    test1 = Follow(name='ios')
    test1.save()
    return HttpResponse("<p>数据添加成功！</p>")