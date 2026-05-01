from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='product_list'),
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('category/<slug:cat_slug>/<slug:slug>/', views.subcategory_view, name='subcategory'),
    path('search/', views.search_view, name='search'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
