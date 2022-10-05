from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()

# User
router.register('accounts', views.UserBankAccountsView, basename='account')
router.register('operations', views.OperationsHistoryView, basename='operation')

# Admin
router.register('requests-admin', views.RequestsCreateBankAccountView, basename='request_admin')
router.register('accounts-admin', views.BankAccountsAdminView, basename='account_admin')

urlpatterns = [
    path('operations/replenishments/create/', views.ReplenishmentCreateView.as_view()),
    path('operations/replenishments/', views.ReplenishmentsHistoryView.as_view()),
    path('operations/transfers/create/another/', views.TransferCreateAnotherView.as_view()),
    path('operations/transfers/create/yourself/', views.TransferCreateYourselfView.as_view()),
    path('operations/transfers/', views.TransfersHistoryView.as_view()),
    path('operations/payments/create/', views.PaymentCreateView.as_view()),
    path('operations/payments/', views.PaymentsHistoryView.as_view()),
]

urlpatterns += router.urls