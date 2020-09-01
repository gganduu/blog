from django.contrib import admin
from blogs import models

# Register your models here.
admin.site.register(models.Category)
admin.site.register(models.Article)