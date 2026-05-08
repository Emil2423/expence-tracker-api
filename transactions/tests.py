from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Category, Transaction
User = get_user_model()
class CategoryTests(APITestCase):
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
        Category.objects.filter(user=self.user).delete()
        self.category = Category.objects.create(
            name='Groceries',
            type='EXPENSE',
            user=self.user,
        )
        self.list_url = reverse('category_list_create')
        self.detail_url = reverse('category_detail', kwargs={'pk': self.category.pk})
    def test_list_categories(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Groceries')
    def test_create_category(self):
        response = self.client.post(
            self.list_url,
            {
                'name': 'Transportation',
                'type': 'EXPENSE',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Transportation')
        self.assertTrue(
            Category.objects.filter(name='Transportation', user=self.user).exists()
        )
    def test_create_duplicate_category(self):
        response = self.client.post(
            self.list_url,
            {
                'name': 'Groceries',
                'type': 'EXPENSE',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_update_category(self):
        response = self.client.patch(
            self.detail_url,
            {'name': 'Food'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Food')
    def test_delete_category(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())
    def test_cannot_access_other_users_category(self):
        other_category = Category.objects.create(
            name='Other',
            type='EXPENSE',
            user=self.other_user,
        )
        url = reverse('category_detail', kwargs={'pk': other_category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
class TransactionTests(APITestCase):
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
        self.transaction = Transaction.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('50.00'),
            note='Lunch',
            date=timezone.now(),
        )
        self.list_url = reverse('transaction_list_create')
        self.detail_url = reverse('transaction_detail', kwargs={'pk': self.transaction.pk})
    def test_list_transactions(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    def test_create_transaction(self):
        response = self.client.post(
            self.list_url,
            {
                'category': self.income_category.pk,
                'amount': '1000.00',
                'note': 'Monthly salary',
                'date': timezone.now().isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], '1000.00')
        self.assertEqual(response.data['category_type'], 'INCOME')
    def test_create_transaction_future_date_fails(self):
        future_date = timezone.now() + timezone.timedelta(days=7)
        response = self.client.post(
            self.list_url,
            {
                'category': self.expense_category.pk,
                'amount': '50.00',
                'note': 'Future expense',
                'date': future_date.isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date', response.data)
    def test_create_transaction_negative_amount_fails(self):
        response = self.client.post(
            self.list_url,
            {
                'category': self.expense_category.pk,
                'amount': '-50.00',
                'note': 'Negative amount',
                'date': timezone.now().isoformat(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_filter_transactions_by_date_range(self):
        past_date = timezone.now() - timezone.timedelta(days=30)
        Transaction.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('100.00'),
            date=past_date,
        )
        start_date = (timezone.now() - timezone.timedelta(days=1)).date().isoformat()
        end_date = timezone.now().date().isoformat()
        response = self.client.get(
            f'{self.list_url}?start={start_date}&end={end_date}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    def test_filter_transactions_by_category(self):
        Transaction.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1000.00'),
            date=timezone.now(),
        )
        response = self.client.get(
            f'{self.list_url}?category={self.expense_category.pk}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['category'],
            self.expense_category.pk
        )
    def test_filter_transactions_by_type(self):
        Transaction.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1000.00'),
            date=timezone.now(),
        )
        response = self.client.get(f'{self.list_url}?category_type=INCOME')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category_type'], 'INCOME')
    def test_update_transaction(self):
        response = self.client.patch(
            self.detail_url,
            {'amount': '75.00'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.amount, Decimal('75.00'))
    def test_delete_transaction(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transaction.objects.filter(pk=self.transaction.pk).exists())
class TransactionSummaryTests(APITestCase):
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
        Transaction.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('5000.00'),
            date=timezone.now(),
        )
        Transaction.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('500.00'),
            date=timezone.now(),
        )
        Transaction.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('300.00'),
            date=timezone.now(),
        )
        self.summary_url = reverse('transaction_summary')
    def test_get_transaction_summary(self):
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['total_income']), Decimal('5000.00'))
        self.assertEqual(Decimal(response.data['total_expenses']), Decimal('800.00'))
        self.assertEqual(Decimal(response.data['net_balance']), Decimal('4200.00'))
    def test_summary_with_date_filter(self):
        old_date = timezone.now() - timezone.timedelta(days=60)
        Transaction.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1000.00'),
            date=old_date,
        )
        start_date = (timezone.now() - timezone.timedelta(days=30)).date().isoformat()
        response = self.client.get(f'{self.summary_url}?start={start_date}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['total_income']), Decimal('5000.00'))
