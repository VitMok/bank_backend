from django.shortcuts import get_list_or_404
from rest_framework import mixins, viewsets, generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from decimal import *
from collections import namedtuple
from django.db import transaction

from .models import (
    RequestCreateAccount,
    Account,
    Replenishment,
    Transfer,
    Payment,
)
from .serializers import (
    CreateRequestCreateAccountSerializer,
    RequestCreateAccountSerializer,
    BankAccountSerializer,
    BankAccountDetailSerializer,
    BankAccountAdminSerializer,
    BankAccountDetailAdminSerializer,
    CreateReplenishmentSerializer,
    ReplenishmentSerializer,
    CreateTransferAnotherSerializer,
    CreateTransferYourselfSerializer,
    TransferSerializer,
    CreatePaymentSerializer,
    PaymentSerializer,
    OperationsHistorySerializer,
)
from .services import (
    _replenishment_bank_account,
    _generate_number_bank_account,
    _payment,
)


class UserBankAccountsView(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin):
    """ Вывод банковских счетов пользователя и отправка
    запроса на создание нового счёта """
    queryset = Account.objects.all()
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return BankAccountSerializer
        if self.action == 'retrieve':
            return BankAccountDetailSerializer
        return CreateRequestCreateAccountSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RequestsCreateBankAccountView(viewsets.GenericViewSet,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin):
    """ Запросы на создание банковского счёта """
    permission_classes = [IsAdminUser]
    queryset = RequestCreateAccount.objects.all()
    serializer_class = RequestCreateAccountSerializer

    @action(detail=True, methods=['post'], url_path='confirm')
    @transaction.atomic
    def confirm_request_create_account(self, request, pk=None):
        """ Подтверждение запроса на создание
        нового банковского счёта """
        create_request = self.get_object()
        account = Account.objects.create(user=create_request.user,
                                         number=_generate_number_bank_account(create_request.user),
                                         type=create_request.type,
                                         currency=create_request.currency)
        serializer = BankAccountDetailAdminSerializer(account)
        # raise Exception('Some problem!')
        create_request.delete()
        return Response(serializer.data, status=201)

class BankAccountsAdminView(viewsets.ModelViewSet):
    """ Просмотр и редактирование банковских
    счетов персоналом """
    permission_classes = [IsAdminUser]
    queryset = Account.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return BankAccountAdminSerializer
        return BankAccountDetailAdminSerializer

class ReplenishmentCreateView(generics.ListCreateAPIView):
    """ Пополнение банковского счёта персоналом """
    permission_classes = [IsAdminUser]
    serializer_class = CreateReplenishmentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = BankAccountAdminSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return get_list_or_404(Account.objects.select_related('user').all())

    @transaction.atomic
    def perform_create(self, serializer):
        _replenishment_bank_account(self.request.data['account'],
                                    Decimal(self.request.data['amount']),
                                    self.request.data['currency'])
        serializer.save()

class ReplenishmentsHistoryView(generics.ListAPIView):
    """ История попополнений банковских счетов """
    serializer_class = ReplenishmentSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Replenishment.objects.all()
        accounts = Account.objects.filter(user=self.request.user)
        return Replenishment.objects.filter(account__in=accounts)

class TransferCreateAnotherView(generics.ListCreateAPIView):
    """ Перевод средств пользователем на банковский
    счёт другого пользователя """
    queryset = Account.objects.all()
    serializer_class = CreateTransferAnotherSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = BankAccountSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class TransferCreateYourselfView(generics.ListCreateAPIView):
    """ Перевод средств пользователем
    между своими счетами """
    queryset = Account.objects.all()
    serializer_class = CreateTransferYourselfSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = BankAccountSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class TransfersHistoryView(generics.ListAPIView):
    """ История переводов средств """
    serializer_class = TransferSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transfer.objects.all()
        from_accounts = Account.objects.filter(user=self.request.user)
        return Transfer.objects.filter(from_account__in=from_accounts)

class PaymentCreateView(generics.ListCreateAPIView):
    """ Оплата товаров или услуг """
    queryset = Account.objects.all()
    serializer_class = CreatePaymentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = BankAccountSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        _payment(self.request.data['account'],
                 Decimal(self.request.data['amount']))
        serializer.save()

class PaymentsHistoryView(generics.ListAPIView):
    """ История оплат товаров или услуг пользователем """
    serializer_class = PaymentSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        account = Account.objects.filter(user=self.request.user)
        return Payment.objects.filter(account__in=account)

class OperationsHistoryView(viewsets.ViewSet):
    """ Просмотр всех операций пользователя """

    def list(self, request):
        Operations = namedtuple('Operations', ('replenishment', 'transfer', 'payment'))
        queryset = Operations(
            replenishment=Replenishment.objects.select_related(
                'account',
            ).filter(account__user=request.user),
            transfer=Transfer.objects.select_related(
                'from_account',
            ).filter(from_account__user=request.user),
            payment=Payment.objects.select_related(
                'account',
            ).filter(account__user=request.user),
        )
        serializer = OperationsHistorySerializer(queryset)
        return Response(serializer.data)