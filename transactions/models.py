from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
class Category(models.Model):
    TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    name = models.CharField(
        max_length=50,
        verbose_name='category name',
        help_text='Name of the category (max 50 characters).',
    )
    type = models.CharField(
        max_length=7,
        choices=TYPE_CHOICES,
        verbose_name='category type',
        help_text='Type of category: INCOME or EXPENSE.',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='user',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='date created',
    )
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ['type', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'user'],
                name='unique_category_per_user',
            )
        ]
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='user',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='category',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='amount',
        help_text='Transaction amount (must be positive).',
    )
    note = models.TextField(
        blank=True,
        default='',
        verbose_name='note',
        help_text='Optional description or note for the transaction.',
    )
    date = models.DateTimeField(
        verbose_name='transaction date',
        help_text='Date and time of the transaction.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='date created',
    )
    class Meta:
        verbose_name = 'transaction'
        verbose_name_plural = 'transactions'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['date']),
        ]
    def __str__(self):
        return f"{self.category.name}: {self.amount} on {self.date.strftime('%Y-%m-%d')}"
    @property
    def is_income(self):
        return self.category.type == 'INCOME'
    @property
    def is_expense(self):
        return self.category.type == 'EXPENSE'
