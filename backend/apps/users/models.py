from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """ Пользователь """
    phone = models.CharField('Номер телефона', max_length=20)

    class Meta:
        db_table = 'custom_user'
