from django.contrib import admin
from .models import Category, Product
from django.utils.html import format_html
from django.db import models

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'is_active', 'image_preview')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_active')
    
    # This method MUST be inside the class
    def image_preview(self, obj):
        if obj.image:  # assumes your Product model has an ImageField called 'image'
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    
    image_preview.short_description = "Image"  # column header in admin