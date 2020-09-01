from django.db import models
from user.models import User

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=50, null=False)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Category'
        verbose_name = 'Category Management'
        verbose_name_plural = verbose_name

class Article(models.Model):
    title = models.CharField(max_length=50, null=False)
    category = models.ForeignKey(to=Category, on_delete=models.DO_NOTHING)
    tag = models.CharField(max_length=25, null=False)
    summary = models.CharField(max_length=200, null=False)
    content = models.TextField(null=False)
    image = models.FileField(upload_to='images/%Y%m%d/', null=True)

    num_viewed = models.PositiveIntegerField(null=False, default=0)
    num_comments = models.PositiveIntegerField(null=False, default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Article'
        ordering = ('-created_time',)
        verbose_name = 'Article Management'
        verbose_name_plural = verbose_name


class Comment(models.Model):
    content = models.TextField(null=False)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    article = models.ForeignKey(to=Article, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'Comment'
        verbose_name = 'Comment Management'
        verbose_name_plural = verbose_name
