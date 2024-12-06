from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser

class TimeBaseModel(models.Model):
    created_at=models.DateTimeField(
        verbose_name=('Время создания'),
        auto_now_add=True,
    )
    updated_at=models.DateTimeField(
        verbose_name=("Время обновление"),
        auto_now=True,    
    )
    class Meta:
        abstract=True
        
class UserBaseModel(TimeBaseModel):
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150, 
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150, 
        blank=True,
    )
    email = models.EmailField(
        default='',
        unique=True,
        help_text='Напишите свою почту'
    )
    refresh_token = models.CharField(
        verbose_name='Обновляемый Токен для пользователя',
        max_length=255,
        default=uuid4,
        unique=True,
    )
    access_token = models.CharField(
        verbose_name='Токен для пользователя',
        max_length=255,
        default=uuid4,
        unique=True,
    )
    phone_number = models.CharField(
        verbose_name='Номер телефона',
        max_length=15,
        blank=True,
        help_text='Введите свой номер телефона в формате +77772221212',
    )
    
    class Meta:
        abstract=True