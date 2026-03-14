from django.contrib.auth.models import AbstractUser
from django.db import models


class UserAccount(AbstractUser):
    """Custom user model for the platform."""
    role = models.CharField(
        max_length=30,
        choices=[
            ('admin', 'Administrator'),
            ('engineer', 'Engineer'),
            ('analyst', 'Data Analyst'),
            ('viewer', 'Viewer'),
        ],
        default='viewer',
    )
    organization = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_accounts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.role})"
