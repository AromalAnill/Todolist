from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import re


class CustomUser(AbstractUser):
    """Custom user model with phone number authentication."""
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Phone number must be a valid format (9-15 digits, optionally starting with + or 1)',
            )
        ]
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.phone_number})"


class Task(models.Model):
    """Task model for storing user tasks with dates."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date', 'title']
        indexes = [
            models.Index(fields=['user', 'due_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.due_date}"
