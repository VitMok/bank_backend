# Generated by Django 4.0.5 on 2022-06-05 19:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=255, verbose_name='Номер счёта')),
                ('type', models.CharField(choices=[('a', 'Депозитный'), ('b', 'Кредитный')], max_length=1, verbose_name='Вид счёта')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Баланс')),
                ('currency', models.CharField(choices=[('r', 'Рубли'), ('d', 'Доллары'), ('e', 'Евро')], max_length=1, verbose_name='Валюта')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Дата и время изменения')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'db_table': 'bank_account',
            },
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Величина перевода')),
                ('currency', models.CharField(choices=[('r', 'Рубли'), ('d', 'Доллары'), ('e', 'Евро')], max_length=1, verbose_name='Валюта')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время перевода')),
                ('from_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_account', to='business.account', verbose_name='Банковский счёт для списания')),
                ('to_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_account', to='business.account', verbose_name='Банковский счёт для пополнения')),
            ],
            options={
                'db_table': 'transfer',
            },
        ),
        migrations.CreateModel(
            name='Replenishment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Величина пополнения')),
                ('currency', models.CharField(choices=[('r', 'Рубли'), ('d', 'Доллары'), ('e', 'Евро')], max_length=1, verbose_name='Валюта')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время пополнения')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='business.account', verbose_name='Банковский счёт')),
            ],
            options={
                'db_table': 'replenishment',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant', models.CharField(max_length=255, verbose_name='Продавец')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Величина оплаты')),
                ('currency', models.CharField(choices=[('r', 'Рубли'), ('d', 'Доллары'), ('e', 'Евро')], max_length=1, verbose_name='Валюта')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время оплаты')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='business.account', verbose_name='Банковский счёт')),
            ],
            options={
                'db_table': 'payment',
            },
        ),
    ]
