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
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
class TransactionFilter(filters.FilterSet):
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
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilter
    def get_queryset(self):
        return (
            Transaction.objects
            .filter(user=self.request.user)
            .select_related('category')
        )
class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return (
            Transaction.objects
            .filter(user=self.request.user)
            .select_related('category')
        )
class TransactionSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        queryset = Transaction.objects.filter(user=user)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
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
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        months = int(request.query_params.get('months', 12))
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
