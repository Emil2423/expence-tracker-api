"""Budgets app configuration."""

from django.apps import AppConfig


class BudgetsConfig(AppConfig):
    """Configuration for the budgets app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budgets'
    verbose_name = 'Budget Management'
