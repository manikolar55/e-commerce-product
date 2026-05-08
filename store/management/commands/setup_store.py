"""
Management command to set up initial store data:
categories, subcategories, sizes, colors, site settings, admin user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Category, SubCategory, Size, Color, SiteSettings

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up initial store data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up BabyLady Store...')

        # Site Settings
        settings, _ = SiteSettings.objects.get_or_create(pk=1, defaults={
            'site_name': 'BabyLady Store',
            'phone': '03348833996',
            'email': 'contact@flowsbin.com',
            'whatsapp': '923348833996',
            'address': 'Main Market, Lahore, Pakistan',
            'meta_title': 'BabyLady Store - Premium Baby & Ladies Products in Pakistan',
            'meta_description': 'Shop premium baby products and ladies fashion online. Free delivery on orders above Rs.2000. Cash on Delivery across Pakistan.',
            'announcement_bar': '🎁 FREE DELIVERY on orders above Rs.2000 | Cash on Delivery Available Nationwide',
            'free_shipping_threshold': 2000,
            'shipping_cost': 150,
        })
        self.stdout.write(f'  ✓ Site settings configured')

        # Baby Categories
        baby_subs = ['Baby Clothes', 'Baby Toys', 'Baby Feeding', 'Baby Care', 'Baby Shoes', 'Baby Accessories']
        baby_cat, created = Category.objects.get_or_create(
            slug='baby-products',
            defaults={'name': 'Baby Products', 'category_type': 'baby', 'is_active': True, 'order': 1}
        )
        if created:
            for i, name in enumerate(baby_subs):
                SubCategory.objects.get_or_create(
                    category=baby_cat,
                    name=name,
                    defaults={'slug': name.lower().replace(' ', '-'), 'is_active': True, 'order': i}
                )
        self.stdout.write(f'  ✓ Baby products category with {len(baby_subs)} subcategories')

        # Ladies Categories
        ladies_subs = ['Dresses', 'Bags & Purses', 'Makeup & Beauty', 'Shoes & Sandals', 'Accessories', 'Suits']
        ladies_cat, created = Category.objects.get_or_create(
            slug='ladies-products',
            defaults={'name': 'Ladies Products', 'category_type': 'ladies', 'is_active': True, 'order': 2}
        )
        if created:
            for i, name in enumerate(ladies_subs):
                SubCategory.objects.get_or_create(
                    category=ladies_cat,
                    name=name,
                    defaults={'slug': name.lower().replace(' ', '-').replace('&', 'and'), 'is_active': True, 'order': i}
                )
        self.stdout.write(f'  ✓ Ladies products category with {len(ladies_subs)} subcategories')

        # Sizes
        sizes_data = [
            ('XS', 0), ('S', 1), ('M', 2), ('L', 3), ('XL', 4), ('XXL', 5),
            ('0-3M', 6), ('3-6M', 7), ('6-12M', 8), ('12-18M', 9), ('1-2Y', 10),
            ('2-3Y', 11), ('3-4Y', 12), ('4-5Y', 13), ('Free Size', 14),
        ]
        for name, order in sizes_data:
            Size.objects.get_or_create(name=name, defaults={'order': order})
        self.stdout.write(f'  ✓ {len(sizes_data)} sizes created')

        # Colors
        colors_data = [
            ('Red', '#ef4444'), ('Blue', '#3b82f6'), ('Pink', '#ec4899'),
            ('White', '#ffffff'), ('Black', '#000000'), ('Green', '#22c55e'),
            ('Yellow', '#eab308'), ('Purple', '#a855f7'), ('Orange', '#f97316'),
            ('Grey', '#6b7280'), ('Navy', '#1e3a5f'), ('Beige', '#d4c5a0'),
            ('Multi Color', ''), ('Sky Blue', '#87ceeb'), ('Maroon', '#800000'),
        ]
        for name, hex_code in colors_data:
            Color.objects.get_or_create(name=name, defaults={'hex_code': hex_code})
        self.stdout.write(f'  ✓ {len(colors_data)} colors created')

        # Admin User
        if not User.objects.filter(is_superuser=True).exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='contact@flowsbin.com',
                password='Admin@12345',
                first_name='Admin',
                last_name='User',
                is_staff=True,
            )
            self.stdout.write(f'  ✓ Admin user created: contact@flowsbin.com / Admin@12345')
        else:
            self.stdout.write(f'  ✓ Admin user already exists')

        self.stdout.write(self.style.SUCCESS('\n✅ BabyLady Store setup complete!'))
        self.stdout.write('\nNext steps:')
        self.stdout.write('  1. Run: python manage.py runserver')
        self.stdout.write('  2. Visit: http://localhost:8000')
        self.stdout.write('  3. Admin: http://localhost:8000/dashboard/')
        self.stdout.write('  4. Login: contact@flowsbin.com / Admin@12345')
