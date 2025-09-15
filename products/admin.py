from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'price', 'stock_qty', 'status')
    search_fields = ('sku', 'name', 'category')
    list_filter = ('category', 'status')
