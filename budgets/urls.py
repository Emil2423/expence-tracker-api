"""
URL patterns for budgets.
"""

from django.urls import path

from .views import (
    BudgetDetailView,
    BudgetListCreateView,
    BudgetSummaryView,
)


urlpatterns = [
    path('budgets/', BudgetListCreateView.as_view(), name='budget_list_create'),
    path('budgets/<int:pk>/', BudgetDetailView.as_view(), name='budget_detail'),
    path('budgets/summary/', BudgetSummaryView.as_view(), name='budget_summary'),
]
