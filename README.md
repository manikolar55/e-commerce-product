# BabyLady eCommerce Store

A production-ready, full-featured eCommerce store for baby and ladies products. Built with Django + Django Templates.

---

## Features

### Customer Store
- Homepage with hero slider, featured products, new arrivals, best sellers
- Baby Products: Clothes, Toys, Feeding, Care, Shoes, Accessories
- Ladies Products: Dresses, Bags, Makeup, Shoes, Accessories, Suits
- Product pages with image gallery, sizes, colors, reviews, related products
- Shopping cart with coupon support
- Checkout with Cash on Delivery (COD)
- Order confirmation & tracking
- Wishlist, Recently Viewed products
- Customer accounts, address book, order history
- WhatsApp order button
- Newsletter subscription
- SEO: meta tags, JSON-LD schema, sitemap.xml, robots.txt, clean URLs
- Blog system for SEO traffic
- Mobile-first responsive design

### Admin Dashboard (`/dashboard/`)
- Overview: revenue, orders, customer stats, charts
- Product management: add/edit/delete, image upload, variants
- Order management: status updates, COD marking, WhatsApp customer
- Customer management with order history
- Coupons: percentage or fixed discounts
- Reports: daily/monthly revenue charts
- Category & subcategory management
- Site settings: logo, phone, WhatsApp, SEO, shipping

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env .env.local
# Edit .env with your settings
```

### 3. Run migrations
```bash
python manage.py migrate
python manage.py setup_store
```

### 4. Start server
```bash
python manage.py runserver
```

### 5. Open browser
- Store: http://localhost:8000
- Dashboard: http://localhost:8000/dashboard/
- Login: `admin@babylady.pk` / `Admin@12345`

---

## Project Structure

```
e-commerce/
├── ecommerce/          # Django project settings
├── store/              # Main store app (products, cart, wishlist)
├── orders/             # Order management
├── accounts/           # Customer authentication
├── dashboard/          # Admin dashboard
├── blog/               # Blog system
├── templates/          # HTML templates
│   ├── base.html       # Base layout
│   ├── store/          # Store templates
│   ├── dashboard/      # Admin templates
│   ├── accounts/       # Auth templates
│   └── blog/           # Blog templates
├── static/
│   ├── css/style.css   # Main stylesheet
│   ├── css/dashboard.css
│   └── js/main.js      # Main JavaScript
├── media/              # Uploaded files
└── manage.py
```

---

## Deployment

### Production Settings
1. Set `DEBUG=False` in `.env`
2. Set a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Set up PostgreSQL database
5. Configure email settings

### Gunicorn + Nginx
```bash
pip install gunicorn
gunicorn ecommerce.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### Collect Static Files
```bash
python manage.py collectstatic
```

---

## Admin Credentials (Development)
- Email: `admin@babylady.pk`
- Password: `Admin@12345`
- **Change these before production!**

---

## Tech Stack
- **Backend**: Django 4.2
- **Frontend**: Bootstrap 5.3, Swiper.js, Chart.js
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Static Files**: WhiteNoise
- **Icons**: Bootstrap Icons
- **Fonts**: Google Fonts (Inter + Playfair Display)
