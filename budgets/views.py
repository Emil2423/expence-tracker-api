"""
Views for budget management.
"""

from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.models import Transaction

from .models import Budget
from .serializers import BudgetSerializer, BudgetSummarySerializer


class BudgetListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating budgets.
    
    GET /api/budgets - List all budgets for the current user
    POST /api/budgets - Create a new budget
    """

    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return budgets for the current user.
        
        Uses select_related for optimized queries.
        """
        return (
            Budget.objects
            .filter(user=self.request.user)
            .select_related('category')
        )


class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a budget.
    
    GET /api/budgets/{id} - Retrieve a budget
    PUT /api/budgets/{id} - Update a budget
    PATCH /api/budgets/{id} - Partial update a budget
    DELETE /api/budgets/{id} - Delete a budget
    """

    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return budgets for the current user."""
        return (
            Budget.objects
            .filter(user=self.request.user)
            .select_related('category')
        )


class BudgetSummaryView(APIView):
    """
    API view for budget summary with spending progress.
    
    GET /api/budgets/summary - Get overall budget summary with progress per budget
        Returns total income, total expenses, and progress per budget.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get budget summary for the current user."""
        user = request.user
        today = timezone.now().date()
        
        # Get active budgets (within date range)
        active_budgets = (
            Budget.objects
            .filter(
                user=user,
                start_date__lte=today,
                end_date__gte=today,
            )
            .select_related('category')
        )
        
        # Calculate totals from active budgets
        total_budgeted = (
            active_budgets.aggregate(total=Sum('amount'))['total']
            or Decimal('0')
        )
        
        # Calculate total spent across all active budgets
        total_spent = Decimal('0')
        over_budget_categories = []
        
        budget_serializer = BudgetSerializer(
            active_budgets,
            many=True,
            context={'request': request}
        )
        
        for budget_data in budget_serializer.data:
            spent = Decimal(str(budget_data['spent']))
            total_spent += spent
            
            # Check if over budget
            if spent > Decimal(str(budget_data['amount'])):
                over_budget_categories.append({
                    'category_id': budget_data['category'],
                    'category_name': budget_data['category_name'],
                    'budgeted': budget_data['amount'],
                    'spent': budget_data['spent'],
                    'over_by': str(spent - Decimal(str(budget_data['amount']))),
                })
        
        total_remaining = total_budgeted - total_spent
        
        # Get overall income and expenses for current month
        first_day_of_month = today.replace(day=1)
        
        total_income = (
            Transaction.objects
            .filter(
                user=user,
                category__type='INCOME',
                date__date__gte=first_day_of_month,
                date__date__lte=today,
            )
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0')
        )
        
        total_expenses = (
            Transaction.objects
            .filter(
                user=user,
                category__type='EXPENSE',
                date__date__gte=first_day_of_month,
                date__date__lte=today,
            )
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0')
        )
        
        # Build response
        data = {
            'total_budgeted': total_budgeted,
            'total_spent': total_spent,
            'total_remaining': max(total_remaining, Decimal('0')),
            'total_income': total_income,
            'total_expenses': total_expenses,
            'budgets': budget_serializer.data,
            'over_budget_categories': over_budget_categories,
        }
        
        serializer = BudgetSummarySerializer(data)
        return Response(serializer.data)
