from django.contrib import admin
from .models import ProductCategory, Product, Service

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    search_fields = ('name', 'description')
    list_filter = ('parent',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'currency', 'stock_quantity', 'is_active')
    list_filter = ('is_active', 'category', 'currency')
    search_fields = ('name', 'sku', 'description')
    list_editable = ('price', 'stock_quantity', 'is_active')
    autocomplete_fields = ['category']
    fieldsets = (
        (None, {
            'fields': ('name', 'is_active', 'sku')
        }),
        ('Details', {
            'fields': ('description', 'category', 'attributes')
        }),
        ('Pricing & Stock', {
            'fields': (('price', 'currency'), 'stock_quantity')
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'currency', 'billing_cycle', 'is_active')
    list_filter = ('is_active', 'category', 'billing_cycle', 'currency')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_active')
    autocomplete_fields = ['category']
    fieldsets = (
        (None, {
            'fields': ('name', 'is_active', 'category')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Pricing & Billing', {
            'fields': (('price', 'currency'), 'billing_cycle')
        }),
    )
