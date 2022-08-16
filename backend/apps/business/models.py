from django.db import models
from django.conf import settings


class Account(models.Model):
    """ Банковский счёт """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    number = models.CharField('Номер счёта', max_length=255)
    TYPES = (
        ('a', 'Депозитный'),
        ('b', 'Кредитный'),
    )
    type = models.CharField('Вид счёта', max_length=1, choices=TYPES)
    balance = models.DecimalField('Баланс', max_digits=12, decimal_places=2, default=0)
    CURRENCIES = (
        ('r', 'Рубли'),
        ('d', 'Доллары'),
        ('e', 'Евро'),
    )
    currency = models.CharField('Валюта', max_length=1, choices=CURRENCIES)
    created = models.DateTimeField('Дата и время создания', auto_now_add=True)
    updated = models.DateTimeField('Дата и время изменения', auto_now=True)

    class Meta:
        db_table = 'bank_account'

    def __str__(self):
        return self.number

class RequestCreateAccount(models.Model):
    """ Запрос пользователя на создание банковского счёта """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    TYPES = (
        ('a', 'Депозитный'),
        ('b', 'Кредитный'),
    )
    type = models.CharField('Вид счёта', max_length=1, choices=TYPES)
    CURRENCIES = (
        ('r', 'Рубли'),
        ('d', 'Доллары'),
        ('e', 'Евро'),
    )
    currency = models.CharField('Валюта', max_length=1, choices=CURRENCIES)
    created = models.DateTimeField('Дата и время создания', auto_now_add=True)

    class Meta:
        db_table = 'request_create_account'

class Replenishment(models.Model):
    """ Пополнение банековского счёта """
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        verbose_name='Банковский счёт'
    )
    amount = models.DecimalField('Величина пополнения', max_digits=12, decimal_places=2)
    CURRENCIES = (
        ('r', 'Рубли'),
        ('d', 'Доллары'),
        ('e', 'Евро'),
    )
    currency = models.CharField('Валюта', max_length=1, choices=CURRENCIES)
    created = models.DateTimeField('Дата и время пополнения', auto_now_add=True)

    class Meta:
        db_table = 'replenishment'

class Transfer(models.Model):
    """ Перевод средств со счёта на счёт """
    from_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        verbose_name='Банковский счёт для списания',
        related_name='from_account',
    )
    to_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        verbose_name='Банковский счёт для пополнения',
        related_name='to_account',
    )
    amount = models.DecimalField('Величина перевода', max_digits=12, decimal_places=2)
    CURRENCIES = (
        ('r', 'Рубли'),
        ('d', 'Доллары'),
        ('e', 'Евро'),
    )
    currency = models.CharField('Валюта', max_length=1, choices=CURRENCIES)
    created = models.DateTimeField('Дата и время перевода', auto_now_add=True)

    class Meta:
        db_table = 'transfer'

class Payment(models.Model):
    """ Оплата """
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        verbose_name='Банковский счёт',
    )
    merchant = models.CharField('Продавец', max_length=255)
    amount = models.DecimalField('Величина оплаты', max_digits=12, decimal_places=2)
    CURRENCIES = (
        ('r', 'Рубли'),
        ('d', 'Доллары'),
        ('e', 'Евро'),
    )
    currency = models.CharField('Валюта', max_length=1, choices=CURRENCIES)
    created = models.DateTimeField('Дата и время оплаты', auto_now_add=True)

    class Meta:
        db_table = 'payment'
