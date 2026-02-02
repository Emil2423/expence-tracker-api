"""
Views for transaction and category management.
"""

from decimal import Decimal

from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Transaction
from .serializers import (
    CategorySerializer,
    MonthlySummarySerializer,
    TransactionSerializer,
    TransactionSummarySerializer,
)


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating categories.
    
    GET /api/categories - List all categories for the current user
    POST /api/categories - Create a new category
    """

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return categories for the current user."""
        return Category.objects.filter(user=self.request.user)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a category.
    
    GET /api/categories/{id} - Retrieve a category
    PUT /api/categories/{id} - Update a category
    PATCH /api/categories/{id} - Partial update a category
    DELETE /api/categories/{id} - Delete a category
    """

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return categories for the current user."""
        return Category.objects.filter(user=self.request.user)


class TransactionFilter(filters.FilterSet):
    """Filter for transactions."""

    start = filters.DateFilter(field_name='date', lookup_expr='date__gte')
    end = filters.DateFilter(field_name='date', lookup_expr='date__lte')
    category = filters.NumberFilter(field_name='category__id')
    category_type = filters.ChoiceFilter(
        field_name='category__type',
        choices=Category.TYPE_CHOICES,
    )
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['start', 'end', 'category', 'category_type', 'min_amount', 'max_amount']


class TransactionListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating transactions.
    
    GET /api/transactions - List all transactions for the current user
        Query params: start, end, category, category_type, min_amount, max_amount
    POST /api/transactions - Create a new transaction
    """

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilter

    def get_queryset(self):
        """
        Return transactions for the current user.
        
        Uses select_related for optimized queries.
        """
        return (
            Transaction.objects
            .filter(user=self.request.user)
            .select_related('category')
        )


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a transaction.
    
    GET /api/transactions/{id} - Retrieve a transaction
    PUT /api/transactions/{id} - Update a transaction
    PATCH /api/transactions/{id} - Partial update a transaction
    DELETE /api/transactions/{id} - Delete a transaction
    """

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return transactions for the current user."""
        return (
            Transaction.objects
            .filter(user=self.request.user)
            .select_related('category')
        )


class TransactionSummaryView(APIView):
    """
    API view for transaction summary.
    
    GET /api/transactions/summary - Get total income, expenses, and breakdown by category
        Query params: start, end (date range)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get transaction summary for the user."""
        user = request.user
        
        # Get date range from query params
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        
        # Base queryset
        queryset = Transaction.objects.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Calculate totals
        income_total = (
            queryset
            .filter(category__type='INCOME')
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0')
        )
        
        expense_total = (
            queryset
            .filter(category__type='EXPENSE')
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0')
        )
        
        # Get breakdown by category
        income_by_category = list(
            queryset
            .filter(category__type='INCOME')
            .values('category__id', 'category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        
        expenses_by_category = list(
            queryset
            .filter(category__type='EXPENSE')
            .values('category__id', 'category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        
        # Format response
        data = {
            'total_income': income_total,
            'total_expenses': expense_total,
            'net_balance': income_total - expense_total,
            'income_by_category': [
                {
                    'category_id': item['category__id'],
                    'category_name': item['category__name'],
                    'total': item['total'],
                }
                for item in income_by_category
            ],
            'expenses_by_category': [
                {
                    'category_id': item['category__id'],
                    'category_name': item['category__name'],
                    'total': item['total'],
                }
                for item in expenses_by_category
            ],
        }
        
        serializer = TransactionSummarySerializer(data)
        return Response(serializer.data)


class MonthlySummaryView(APIView):
    """
    API view for monthly summary data (chart-ready).
    
    GET /api/transactions/monthly-summary - Get monthly totals for the past year
        Query params: months (number of months to include, default 12)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get monthly summary data."""
        user = request.user
        months = int(request.query_params.get('months', 12))
        
        # Get transactions grouped by month
        queryset = (
            Transaction.objects
            .filter(user=user)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(
                total_income=Sum(
                    'amount',
                    filter=Q(category__type='INCOME'),
                    default=Decimal('0'),
                ),
                total_expenses=Sum(
                    'amount',
                    filter=Q(category__type='EXPENSE'),
                    default=Decimal('0'),
                ),
            )
            .order_by('-month')[:months]
        )
        
        # Format response
        data = [
            {
                'month': item['month'].strftime('%B'),
                'year': item['month'].year,
                'total_income': item['total_income'] or Decimal('0'),
                'total_expenses': item['total_expenses'] or Decimal('0'),
                'net_balance': (item['total_income'] or Decimal('0')) - (item['total_expenses'] or Decimal('0')),
            }
            for item in queryset
        ]
        
        serializer = MonthlySummarySerializer(data, many=True)
        return Response(serializer.data)
