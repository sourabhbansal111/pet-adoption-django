from .models import Order, OrderItem
from django.contrib import admin

# Register your models here.
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'email', 'total', 'created']
    list_filter = ['created']
    search_fields = ['order_number', 'name', 'email']
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)