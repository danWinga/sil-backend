# catalog/admin.py
from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    list_filter = ("categories",)
    search_fields = ("name",)