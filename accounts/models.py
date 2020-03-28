from django.contrib.auth.models import AbstractUser
from django.db import models

GENDER = (('M', 'Male'),
          ('F', 'Female'))


class User(AbstractUser):
    name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER)
    contact = models.CharField(max_length=10, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return str(self.name)
