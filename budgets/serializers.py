from decimal import Decimal
from django.db.models import Sum
from rest_framework import serializers
from transactions.models import Category, Transaction
from .models import Budget
class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name',
        read_only=True,
    )

    category_type = serializers.CharField(
        source='category.type',
        read_only=True,
    )

    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Budget

        fields = [
            'id',
            'category',
            'category_name',
            'category_type',
            'amount',
            'period',
            'start_date',
            'end_date',
            'spent',
            'remaining',
            'progress_percentage',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
            'category_name',
            'category_type',
            'spent',
            'remaining',
            'progress_percentage',
        ]

    def get_spent(self, obj):

        spent = (
            Transaction.objects
            .filter(
                user=obj.user,
                category=obj.category,
                date__date__gte=obj.start_date,
                date__date__lte=obj.end_date,
            )
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0')
        )
        return spent
    
    def get_remaining(self, obj):
        spent = self.get_spent(obj)
        remaining = obj.amount - spent
        return max(remaining, Decimal('0'))
    
    def get_progress_percentage(self, obj):
        spent = self.get_spent(obj)
        if obj.amount > 0:
            percentage = (spent / obj.amount) * 100
            return min(round(percentage, 2), 100)
        return 0
    
    def validate_amount(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "Budget amount must be greater than zero."
            )
        return value
    
    def validate_category(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError(
                "Category does not belong to you."
            )
        if value.type != 'EXPENSE':
            raise serializers.ValidationError(
                "Budgets can only be set for expense categories."
            )
        return value
    
    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
class BudgetSummarySerializer(serializers.Serializer):
    total_budgeted = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_remaining = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    budgets = serializers.ListField(child=serializers.DictField())
    over_budget_categories = serializers.ListField(
        child=serializers.DictField()
    )
