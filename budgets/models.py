"""
Models for budget management.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from transactions.models import Category


class Budget(models.Model):
    """
    Budget model for tracking spending limits.
    
    Users can set budgets for specific categories with weekly or monthly periods.
    """

    PERIOD_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='user',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='category',
        help_text='Category to track spending for.',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='budget amount',
        help_text='Maximum amount to spend in this category.',
    )
    period = models.CharField(
        max_length=7,
        choices=PERIOD_CHOICES,
        verbose_name='budget period',
        help_text='Time period for the budget (WEEKLY or MONTHLY).',
    )
    start_date = models.DateField(
        verbose_name='start date',
        help_text='Budget start date.',
    )
    end_date = models.DateField(
        verbose_name='end date',
        help_text='Budget end date.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='date created',
    )

    class Meta:
        verbose_name = 'budget'
        verbose_name_plural = 'budgets'
        ordering = ['-start_date', 'category__name']
        indexes = [
            models.Index(fields=['user', 'start_date', 'end_date']),
            models.Index(fields=['user', 'category']),
        ]

    def __str__(self):
        """Return string representation of budget."""
        return f"{self.category.name} - {self.amount} ({self.get_period_display()})"

    def clean(self):
        """Validate budget data."""
        from django.core.exceptions import ValidationError
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({
                    'end_date': 'End date must be after start date.'
                })

    def save(self, *args, **kwargs):
        """Validate before saving."""
        self.full_clean()
        super().save(*args, **kwargs)
