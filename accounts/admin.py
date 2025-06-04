# accounts/admin.py
from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "phone_number", "is_active")
    search_fields = ("username", "email")
