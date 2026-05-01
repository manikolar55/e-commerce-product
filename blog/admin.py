from django.contrib import admin
from .models import BlogPost, BlogCategory


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_published', 'views', 'created_at']
    list_filter = ['is_published', 'category', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
