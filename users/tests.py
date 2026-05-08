from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()
class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('user_register')
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'first_name': 'Test',
            'last_name': 'User',
        }
    def test_register_user_success(self):
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User registered successfully.')
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertTrue(User.objects.filter(username='testuser').exists())
    def test_register_user_password_mismatch(self):
        data = self.valid_user_data.copy()
        data['password_confirm'] = 'DifferentPass123!'
        response = self.client.post(
            self.register_url,
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)
    def test_register_user_duplicate_email(self):
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='Pass123!',
        )
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    def test_register_user_weak_password(self):
        data = self.valid_user_data.copy()
        data['password'] = '123'
        data['password_confirm'] = '123'
        response = self.client.post(
            self.register_url,
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_register_creates_default_categories(self):
        from transactions.models import Category
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='testuser')
        categories = Category.objects.filter(user=user)
        self.assertTrue(categories.exists())
        self.assertTrue(categories.filter(type='INCOME').exists())
        self.assertTrue(categories.filter(type='EXPENSE').exists())
class UserLoginTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('token_obtain_pair')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123!',
        )
    def test_login_success(self):
        response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'StrongPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    def test_login_wrong_password(self):
        response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'WrongPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_login_nonexistent_user(self):
        response = self.client.post(
            self.login_url,
            {
                'username': 'nonexistent',
                'password': 'Pass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
class UserProfileTests(APITestCase):
    def setUp(self):
        self.profile_url = reverse('user_profile')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123!',
            first_name='Test',
            last_name='User',
        )
        self.client.force_authenticate(user=self.user)
    def test_get_profile(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    def test_update_profile(self):
        response = self.client.patch(
            self.profile_url,
            {'first_name': 'Updated'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
    def test_profile_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.change_password_url = reverse('change_password')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='OldPass123!',
        )
        self.client.force_authenticate(user=self.user)
    def test_change_password_success(self):
        response = self.client.post(
            self.change_password_url,
            {
                'old_password': 'OldPass123!',
                'new_password': 'NewPass123!',
                'new_password_confirm': 'NewPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))
    def test_change_password_wrong_old_password(self):
        response = self.client.post(
            self.change_password_url,
            {
                'old_password': 'WrongPass123!',
                'new_password': 'NewPass123!',
                'new_password_confirm': 'NewPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_change_password_mismatch(self):
        response = self.client.post(
            self.change_password_url,
            {
                'old_password': 'OldPass123!',
                'new_password': 'NewPass123!',
                'new_password_confirm': 'DifferentPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
