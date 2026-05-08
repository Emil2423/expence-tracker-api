from django.contrib import admin
from .models import Category, Transaction
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['name', 'user__username']
    ordering = ['type', 'name']
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'category', 'amount', 'date', 'created_at']
    list_filter = ['category__type', 'category', 'date', 'created_at']
    search_fields = ['note', 'user__username', 'category__name']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
    raw_id_fields = ['user', 'category']
