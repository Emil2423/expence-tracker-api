"""
User models for the finance tracker application.

Extends Django's AbstractUser to provide custom user functionality.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for the finance tracker application.
    
    Extends Django's AbstractUser to allow for future customization
    while maintaining compatibility with Django's authentication system.
    """

    email = models.EmailField(
        unique=True,
        verbose_name='email address',
        help_text='Required. A valid email address.',
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='date created',
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='date updated',
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-created_at']

    def __str__(self):
        """Return string representation of user."""
        return self.username
