from django.db import transaction
from rest_framework import serializers

from .models import (
    RequestCreateAccount,
    Account,
    Replenishment,
    Transfer,
    Payment,
)
from .services import (
    _check_number_bank_account,
    _check_amount,
    _transfer_funds_from_account_to_account,
)


class CreateRequestCreateAccountSerializer(serializers.ModelSerializer):
    """ Создание пользователем запроса
     на создание банковского счёта """

    class Meta:
        model = RequestCreateAccount
        fields = ('type', 'currency')

class RequestCreateAccountSerializer(serializers.ModelSerializer):
    """ Запрос пользователя на создание
     банковского счёта """
    user = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = RequestCreateAccount
        fields = '__all__'

class BankAccountSerializer(serializers.ModelSerializer):
    """ Банковский счёт, который
    видит пользователь """

    class Meta:
        model = Account
        fields = ('id', 'number', 'balance', 'currency')

class BankAccountDetailSerializer(serializers.ModelSerializer):
    """ Полное описание банковского счёта,
    который видит пользователь """

    class Meta:
        model = Account
        exclude = ('user',)

class BankAccountAdminSerializer(serializers.ModelSerializer):
    """ Банковский счёт, который
    видит персонал """
    user = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Account
        fields = ('id', 'number', 'user', 'type',
                  'balance', 'currency')

class BankAccountDetailAdminSerializer(serializers.ModelSerializer):
    """ Полное описание банковского счёта,
    который видит персонал """
    user = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Account
        fields = '__all__'

class CreateReplenishmentSerializer(serializers.ModelSerializer):
    """ Пополнение банковского счёта """

    class Meta:
        model = Replenishment
        fields = '__all__'

    def validate_amount(self, value):
        """ Проверка количества отправляемых средств """
        if value <= 0:
            raise serializers.ValidationError('Количество отправляемых средств должно быть больше нуля.')
        return value

class ReplenishmentSerializer(serializers.ModelSerializer):
    """ Просмотр операции пополнения
    банковского счёта """
    account = serializers.SlugRelatedField(read_only=True, slug_field='number')

    class Meta:
        model = Replenishment
        fields = '__all__'

class CreateTransferAnotherSerializer(serializers.ModelSerializer):
    """ Перевод средств пользователем другому пользователю """
    account_for_enrollment = serializers.CharField()

    class Meta:
        model = Transfer
        fields = ('from_account', 'account_for_enrollment', 'amount')

    def __init__(self, *args, **kwargs):
        super(CreateTransferAnotherSerializer, self).__init__(*args, **kwargs)
        self.fields['from_account'] = serializers.PrimaryKeyRelatedField(
            queryset=Account.objects.filter(user=self.context['request'].user)
        )

    def validate_account_for_enrollment(self, value):
        """ Проверка корректного номера
        банковского счёта """
        if _check_number_bank_account(value):
            return value
        else:
            raise serializers.ValidationError('Банковского счёта с таким номером не существует.')

    def validate_amount(self, value):
        """ Проверка количества отправляемых средств """
        if value <= 0:
            raise serializers.ValidationError('Количество отправляемых средств должно быть больше нуля.')
        return value

    def validate(self, data):
        if _check_amount(data['from_account'].balance, data['amount']):
            return data
        else:
            raise serializers.ValidationError('Количество отправляемых средств превышает размер текущего баланса.')

    @transaction.atomic
    def create(self, validated_data):
        acc_for_enroll = validated_data.pop('account_for_enrollment')
        to_account = Account.objects.get(number=acc_for_enroll)
        transfer = Transfer.objects.create(from_account=validated_data['from_account'],
                                           to_account=to_account,
                                           amount=validated_data['amount'],
                                           currency=validated_data['from_account'].currency)
        _transfer_funds_from_account_to_account(transfer.from_account, transfer.to_account, transfer.amount)
        return transfer

class CreateTransferYourselfSerializer(serializers.ModelSerializer):
    """ Перевод средств пользователем
    между своими счетами """

    class Meta:
        model = Transfer
        exclude = ('id', 'currency')

    def __init__(self, *args, **kwargs):
        super(CreateTransferYourselfSerializer, self).__init__(*args, **kwargs)
        self.fields['from_account'] = serializers.PrimaryKeyRelatedField(
            queryset=Account.objects.filter(user=self.context['request'].user)
        )
        self.fields['to_account'] = serializers.PrimaryKeyRelatedField(
            queryset=Account.objects.filter(user=self.context['request'].user)
        )

class TransferSerializer(serializers.ModelSerializer):
    """ Просмотр операции перевода средств """
    from_account = serializers.StringRelatedField()
    to_account = serializers.StringRelatedField()

    class Meta:
        model = Transfer
        fields = '__all__'

class CreatePaymentSerializer(serializers.ModelSerializer):
    """ Оплата товаров или услуг """

    class Meta:
        model = Payment
        exclude = ('currency',)

    def __init__(self, *args, **kwargs):
        super(CreatePaymentSerializer, self).__init__(*args, **kwargs)
        self.fields['account'] = serializers.PrimaryKeyRelatedField(
            queryset=Account.objects.filter(user=self.context['request'].user)
        )

class PaymentSerializer(serializers.ModelSerializer):
    """ Просмотр операции оплаты товаров или услуг """
    account = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = ('id', 'account', 'merchant', 'amount')

class OperationsHistorySerializer(serializers.Serializer):
    """ Вывод списка всех операций пользователя """
    replenishment = ReplenishmentSerializer(many=True)
    transfer = TransferSerializer(many=True)
    payment = PaymentSerializer(many=True)