from decimal import *

from .models import (
    Account,
)


def _generate_number_bank_account(user:object) -> str:
    """ Генерация номера банковского счёта """
    if Account.objects.filter(user=user).last():
        account = Account.objects.filter(user=user).last()
        return str(int(account.number) + 1)
    else:
        number = str(user.pk) + '0001'
        return number

def _currency_exchange(from_currency:str, to_currency:str, amount:Decimal) -> Decimal:
    """ Обмен валюты """
    currencies = {
        'r': 59.65,
        'd': 1.02,
        'e': 0.95,
    }
    franc = amount / Decimal(currencies[from_currency])
    return franc * Decimal(currencies[to_currency])

def _replenishment_bank_account(account_pk:int, amount:Decimal, currency:str) -> None:
    """ Пополнение банковского счёта """
    account = Account.objects.get(pk=account_pk)
    account.balance += amount
    account.save()

def _check_number_bank_account(number:str) -> bool:
    """ Проверка существования банковского счёта
    с данным номером """
    try:
        Account.objects.get(number=number)
    except:
        return False

    return True

def _check_amount(balance:Decimal, amount:Decimal) -> bool:
    """ Проверка не превышает ли количество отправляемых
    средств пользователем его текущего размера баланса """
    if balance < amount:
        return False
    else:
        return True

def _transfer_funds_from_account_to_account(from_account:object, to_account:object, amount:Decimal) -> None:
    """ Перевод средств со счёта на счёт """
    new_amount = _currency_exchange(from_account.currency, to_account.currency, amount)
    from_account.balance -= amount
    to_account.balance += new_amount
    from_account.save()
    to_account.save()

def _payment(account_pk:str, amount:Decimal) -> None:
    """ Оплата товаров или услуг """
    account = Account.objects.get(pk=account_pk)
    account.balance -= amount
    account.save()