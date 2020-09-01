from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, null=False, blank=False)
    # Upload images to sub folders created by year-month-day
    img = models.ImageField(upload_to='avatar/%Y%m%d/', null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)

    # modify authentication field
    USERNAME_FIELD = 'mobile'

    # required field of supper user
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'User'
        verbose_name = 'User Management'
        verbose_name_plural = verbose_name


    def __str__(self):
        return self.mobile


