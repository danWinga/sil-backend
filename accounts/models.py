# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class Customer(AbstractUser):
    """
    Extend the default User to add a phone number for SMS.
    We keep username for compatibility but enforce unique email.
    """

    email = models.EmailField("email address", unique=True)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        help_text="E.164 format, e.g. +2547XXXXXXXX",
    )

    REQUIRED_FIELDS = ["email"]  # keep username as USERNAME_FIELD
    # If you prefer email-as-username, you'd override USERNAME_FIELD.

    def __str__(self):
        return f"{self.username} <{self.email}>"
