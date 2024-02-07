from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    birth_day = models.DateField(default=None, null=False)
    can_be_contacted = models.BooleanField(default=False, null=False, verbose_name='Allowed contact')
    can_be_shared = models.BooleanField(default=False, null=False, verbose_name='Share data consent')
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'  # indicates email as identifier in User Model
    REQUIRED_FIELDS = ['password', 'birth_day', 'can_be_shared', 'can_be_contacted']
