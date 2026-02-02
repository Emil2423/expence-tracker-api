"""
Serializers for transactions and categories.
"""

from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import Category, Transaction


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    
    Handles CRUD operations for categories.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        """Validate category name is unique for the user."""
        user = self.context['request'].user
        queryset = Category.objects.filter(user=user, name__iexact=value)
        
        # Exclude current instance when updating
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "You already have a category with this name."
            )
        return value

    def create(self, validated_data):
        """Create category with current user."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    
    Handles CRUD operations for transactions with validation.
    """

    category_name = serializers.CharField(
        source='category.name',
        read_only=True,
    )
    category_type = serializers.CharField(
        source='category.type',
        read_only=True,
    )

    class Meta:
        model = Transaction
        fields = [
            'id',
            'category',
            'category_name',
            'category_type',
            'amount',
            'note',
            'date',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'category_name', 'category_type']

    def validate_amount(self, value):
        """Validate amount is positive."""
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "Amount must be greater than zero."
            )
        return value

    def validate_date(self, value):
        """Validate date is not in the future."""
        if value > timezone.now():
            raise serializers.ValidationError(
                "Transaction date cannot be in the future."
            )
        return value

    def validate_category(self, value):
        """Validate category belongs to the user."""
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError(
                "Category does not belong to you."
            )
        return value

    def create(self, validated_data):
        """Create transaction with current user."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionSummarySerializer(serializers.Serializer):
    """
    Serializer for transaction summary data.
    
    Used for monthly summary endpoint.
    """

    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    income_by_category = serializers.ListField(
        child=serializers.DictField()
    )
    expenses_by_category = serializers.ListField(
        child=serializers.DictField()
    )


class MonthlySummarySerializer(serializers.Serializer):
    """
    Serializer for monthly summary data (chart-ready).
    """

    month = serializers.CharField()
    year = serializers.IntegerField()
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
