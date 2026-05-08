from django.urls import path
from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    MonthlySummaryView,
    TransactionDetailView,
    TransactionListCreateView,
    TransactionSummaryView,
)
urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category_list_create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('transactions/', TransactionListCreateView.as_view(), name='transaction_list_create'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/summary/', TransactionSummaryView.as_view(), name='transaction_summary'),
    path('transactions/monthly-summary/', MonthlySummaryView.as_view(), name='monthly_summary'),
]
