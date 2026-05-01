from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import BlogPost, BlogCategory


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True).select_related('author', 'category')
    cat_slug = request.GET.get('category')
    category = None
    if cat_slug:
        category = get_object_or_404(BlogCategory, slug=cat_slug)
        posts = posts.filter(category=category)
    paginator = Paginator(posts, 9)
    categories = BlogCategory.objects.all()
    return render(request, 'blog/list.html', {
        'posts': paginator.get_page(request.GET.get('page')),
        'categories': categories,
        'current_category': category,
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    post.views += 1
    post.save(update_fields=['views'])
    related = BlogPost.objects.filter(
        is_published=True, category=post.category
    ).exclude(id=post.id)[:3]
    return render(request, 'blog/detail.html', {'post': post, 'related': related})
