from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from transactions.models import Category, Transaction
from .models import Budget
User = get_user_model()
class BudgetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(user=self.user)
        Category.objects.filter(user=self.user).delete()
        self.income_category = Category.objects.create(
            name='Salary',
            type='INCOME',
            user=self.user,
        )
        self.expense_category = Category.objects.create(
            name='Food',
            type='EXPENSE',
            user=self.user,
        )
        today = timezone.now().date()
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('500.00'),
            period='MONTHLY',
            start_date=today.replace(day=1),
            end_date=today,
        )
        self.list_url = reverse('budget_list_create')
        self.detail_url = reverse('budget_detail', kwargs={'pk': self.budget.pk})
    def test_list_budgets(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(Decimal(response.data['results'][0]['amount']), Decimal('500.00'))
    def test_create_budget(self):
        other_expense_category = Category.objects.create(
            name='Transport',
            type='EXPENSE',
            user=self.user,
        )
        today = timezone.now().date()
        response = self.client.post(
            self.list_url,
            {
                'category': other_expense_category.pk,
                'amount': '200.00',
                'period': 'WEEKLY',
                'start_date': today.isoformat(),
                'end_date': (today + timezone.timedelta(days=7)).isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], '200.00')
        self.assertEqual(response.data['period'], 'WEEKLY')
    def test_create_budget_for_income_category_fails(self):
        today = timezone.now().date()
        response = self.client.post(
            self.list_url,
            {
                'category': self.income_category.pk,
                'amount': '500.00',
                'period': 'MONTHLY',
                'start_date': today.isoformat(),
                'end_date': (today + timezone.timedelta(days=30)).isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)
    def test_create_budget_invalid_date_range(self):
        today = timezone.now().date()
        response = self.client.post(
            self.list_url,
            {
                'category': self.expense_category.pk,
                'amount': '500.00',
                'period': 'MONTHLY',
                'start_date': today.isoformat(),
                'end_date': (today - timezone.timedelta(days=7)).isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_update_budget(self):
        response = self.client.patch(
            self.detail_url,
            {'amount': '600.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.budget.refresh_from_db()
        self.assertEqual(self.budget.amount, Decimal('600.00'))
    def test_delete_budget(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Budget.objects.filter(pk=self.budget.pk).exists())
    def test_budget_shows_spent_amount(self):
        Transaction.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('150.00'),
            date=timezone.now(),
        )
        Transaction.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('100.00'),
            date=timezone.now(),
        )
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['spent']), Decimal('250.00'))
        self.assertEqual(Decimal(response.data['remaining']), Decimal('250.00'))
        self.assertEqual(response.data['progress_percentage'], 50.0)
class BudgetSummaryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(user=self.user)
        Category.objects.filter(user=self.user).delete()
        self.income_category = Category.objects.create(
            name='Salary',
            type='INCOME',
            user=self.user,
        )
        self.food_category = Category.objects.create(
            name='Food',
            type='EXPENSE',
            user=self.user,
        )
        self.transport_category = Category.objects.create(
            name='Transport',
            type='EXPENSE',
            user=self.user,
        )
        today = timezone.now().date()
        first_day = today.replace(day=1)
        Budget.objects.create(
            user=self.user,
            category=self.food_category,
            amount=Decimal('500.00'),
            period='MONTHLY',
            start_date=first_day,
            end_date=today,
        )
        Budget.objects.create(
            user=self.user,
            category=self.transport_category,
            amount=Decimal('200.00'),
            period='MONTHLY',
            start_date=first_day,
            end_date=today,
        )
        Transaction.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('5000.00'),
            date=timezone.now(),
        )
        Transaction.objects.create(
            user=self.user,
            category=self.food_category,
            amount=Decimal('300.00'),
            date=timezone.now(),
        )
        Transaction.objects.create(
            user=self.user,
            category=self.transport_category,
            amount=Decimal('250.00'),
            date=timezone.now(),
        )
        self.summary_url = reverse('budget_summary')
    def test_get_budget_summary(self):
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['total_budgeted']), Decimal('700.00'))
        self.assertEqual(Decimal(response.data['total_spent']), Decimal('550.00'))
        self.assertEqual(Decimal(response.data['total_remaining']), Decimal('150.00'))
    def test_summary_shows_over_budget_categories(self):
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        over_budget = response.data['over_budget_categories']
        self.assertEqual(len(over_budget), 1)
        self.assertEqual(over_budget[0]['category_name'], 'Transport')
    def test_summary_includes_income_and_expenses(self):
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_income', response.data)
        self.assertIn('total_expenses', response.data)
        self.assertEqual(Decimal(response.data['total_income']), Decimal('5000.00'))
        self.assertEqual(Decimal(response.data['total_expenses']), Decimal('550.00'))
class BudgetPermissionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123!',
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='StrongPass123!',
        )
        self.client.force_authenticate(user=self.user)
        self.other_category = Category.objects.create(
            name='Other Food',
            type='EXPENSE',
            user=self.other_user,
        )
        today = timezone.now().date()
        self.other_budget = Budget.objects.create(
            user=self.other_user,
            category=self.other_category,
            amount=Decimal('500.00'),
            period='MONTHLY',
            start_date=today.replace(day=1),
            end_date=today,
        )
    def test_cannot_access_other_users_budget(self):
        url = reverse('budget_detail', kwargs={'pk': self.other_budget.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    def test_cannot_create_budget_with_other_users_category(self):
        today = timezone.now().date()
        response = self.client.post(
            reverse('budget_list_create'),
            {
                'category': self.other_category.pk,
                'amount': '500.00',
                'period': 'MONTHLY',
                'start_date': today.isoformat(),
                'end_date': (today + timezone.timedelta(days=30)).isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
