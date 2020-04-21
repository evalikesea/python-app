from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.urls import reverse


class Restaurant(models.Model):
    name = models.TextField()
    address = models.TextField(blank=True, default='')
    telephone = models.TextField(blank=True, default='')
    url = models.URLField(blank=True, null=True)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('myrestaurants:restaurant_detail', args=[str(self.id)])


class Dish(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True, default='')
    price = models.DecimalField('USD amount', max_digits=8, decimal_places=2, blank=True, null=True)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    image = models.ImageField(upload_to="myrestaurants", blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, null=True, related_name='dishes', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('myrestaurants:dish_detail', args=[str(self.restaurant.id), str(self.id)])


# This Abstract Review can be used to create RestaurantReview and DishReview
class Review(models.Model):
    RATING_CHOICES = ((1, 'one'), (2, 'two'), (3, 'three'), (4, 'four'), (5, 'five'))
    rating = models.PositiveSmallIntegerField('Rating (stars)', blank=False, default=3, choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)

    class Meta:
        abstract = True

    '''
    class Meta:
        # 按Priority降序, order_date升序排列.
        get_latest_by = ['-priority', 'order_date']
        # 自定义数据库里表格的名字
        db_table = 'music_album'
        # 按什么排序
        ordering = ['pub_date']
        # 定义APP的标签
        app_label = 'myapp'
        # 声明此类是否为抽象，Django就会认为这个模型是抽象类，不会在数据库里创建review的数据表
        abstract = True
        # 添加授权
        permissions = (("can_deliver_pizzas", "Can deliver pizzas"),)
    '''

class RestaurantReview(Review):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="reviews")

    def __str__(self):
        return "{} review".format(self.restaurant.name)
