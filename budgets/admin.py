"""
Django admin configuration for budgets app.
"""

from django.contrib import admin

from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Admin configuration for Budget model."""

    list_display = ['id', 'user', 'category', 'amount', 'period', 'start_date', 'end_date', 'created_at']
    list_filter = ['period', 'start_date', 'end_date', 'created_at']
    search_fields = ['user__username', 'category__name']
    ordering = ['-start_date', 'category__name']
    date_hierarchy = 'start_date'
    raw_id_fields = ['user', 'category']
