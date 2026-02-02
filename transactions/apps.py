"""Transactions app configuration."""

from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    """Configuration for the transactions app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'
    verbose_name = 'Transaction Management'
