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
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return (
            Budget.objects
            .filter(user=self.request.user)
            .select_related('category')
        )
class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return (
            Budget.objects
            .filter(user=self.request.user)
            .select_related('category')
        )
class BudgetSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        active_budgets = (
            Budget.objects
            .filter(
                user=user,
                start_date__lte=today,
                end_date__gte=today,
            )
            .select_related('category')
        )
        total_budgeted = (
            active_budgets.aggregate(total=Sum('amount'))['total']
            or Decimal('0')
        )
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
            if spent > Decimal(str(budget_data['amount'])):
                over_budget_categories.append({
                    'category_id': budget_data['category'],
                    'category_name': budget_data['category_name'],
                    'budgeted': budget_data['amount'],
                    'spent': budget_data['spent'],
                    'over_by': str(spent - Decimal(str(budget_data['amount']))),
                })
        total_remaining = total_budgeted - total_spent
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
