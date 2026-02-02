"""
URL patterns for user authentication.
"""

from django.urls import path

from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    UserProfileView,
    UserRegistrationView,
)


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]
