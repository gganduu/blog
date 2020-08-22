from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, blank=False)
    img = models.ImageField(upload_to='images/%Y%m%d/', blank=True)
    description = models.CharField(max_length=500, blank=True)

    class Meta:
           db_table = 'users'

    def __str__(self):
        return self.mobile



