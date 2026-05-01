/**
 * BabyLady eCommerce - Main JavaScript
 */

// ===== CSRF TOKEN HELPER =====
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

// ===== TOAST NOTIFICATION =====
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast-custom ${type}`;
  toast.innerHTML = `
    <div class="d-flex align-items-center gap-2">
      <i class="bi bi-${type === 'success' ? 'check-circle-fill text-success' : 'exclamation-circle-fill text-danger'}"></i>
      <span>${message}</span>
    </div>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ===== ADD TO CART (product cards) =====
document.addEventListener('click', function(e) {
  const btn = e.target.closest('.add-to-cart-btn');
  if (!btn) return;
  e.preventDefault();
  const productId = btn.dataset.productId;
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

  fetch('/orders/add-to-cart/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ product_id: productId, quantity: 1 }),
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast(data.message, 'success');
      // Update cart badge
      document.querySelectorAll('.cart-badge').forEach(el => {
        el.textContent = data.cart_count;
        el.style.display = data.cart_count > 0 ? 'flex' : 'none';
      });
    } else {
      showToast(data.message || 'Error adding to cart', 'error');
    }
  })
  .catch(() => showToast('Network error. Please try again.', 'error'))
  .finally(() => {
    btn.disabled = false;
    btn.innerHTML = originalText;
  });
});

// ===== WISHLIST TOGGLE =====
function toggleWishlist(productId, btn) {
  if (!btn) return;
  fetch('/store/wishlist/toggle/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ product_id: productId }),
  })
  .then(r => {
    if (r.status === 302 || r.redirected) {
      window.location.href = '/accounts/login/?next=' + window.location.pathname;
      return;
    }
    return r.json();
  })
  .then(data => {
    if (!data) return;
    if (data.status === 'added') {
      btn.querySelector('i')?.classList.replace('bi-heart', 'bi-heart-fill');
      btn.classList.add('active');
      showToast(data.message, 'success');
    } else {
      btn.querySelector('i')?.classList.replace('bi-heart-fill', 'bi-heart');
      btn.classList.remove('active');
      showToast(data.message, 'success');
    }
    // Update wishlist count
    document.querySelectorAll('[title="Wishlist"] .cart-badge, .nav-icon-btn[href*="wishlist"] .cart-badge').forEach(el => {
      const count = parseInt(el.textContent || '0');
      el.textContent = data.status === 'added' ? count + 1 : Math.max(0, count - 1);
    });
  })
  .catch(() => showToast('Please login to use wishlist', 'error'));
}

// Wishlist buttons on product cards
document.addEventListener('click', function(e) {
  const btn = e.target.closest('.wishlist-btn[data-product-id]');
  if (!btn) return;
  e.preventDefault();
  toggleWishlist(btn.dataset.productId, btn);
});

// ===== BACK TO TOP =====
const backToTopBtn = document.getElementById('backToTop');
if (backToTopBtn) {
  window.addEventListener('scroll', () => {
    backToTopBtn.classList.toggle('visible', window.scrollY > 400);
  });
}

// ===== STICKY NAVBAR SHADOW =====
window.addEventListener('scroll', function() {
  const navbar = document.querySelector('.navbar');
  if (navbar) navbar.classList.toggle('shadow-sm', window.scrollY > 10);
});

// ===== DISMISS ALERTS AUTO =====
setTimeout(() => {
  document.querySelectorAll('.alert:not(.alert-permanent)').forEach(el => {
    if (el.classList.contains('show')) {
      el.classList.remove('show');
      setTimeout(() => el.remove(), 150);
    }
  });
}, 5000);

// ===== LAZY LOADING IMAGES =====
if ('IntersectionObserver' in window) {
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          imageObserver.unobserve(img);
        }
      }
    });
  });
  document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
}

// ===== SEARCH SUGGESTIONS (simple) =====
const searchInput = document.querySelector('.search-input');
if (searchInput) {
  let searchTimeout;
  searchInput.addEventListener('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      // Can add AJAX suggestions here
    }, 300);
  });
}

// ===== MOBILE SIDEBAR (dashboard) =====
const sidebarToggle = document.getElementById('sidebarToggle');
if (sidebarToggle) {
  sidebarToggle.addEventListener('click', function() {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('dashboardMain');
    if (window.innerWidth <= 991) {
      sidebar?.classList.toggle('mobile-open');
    } else {
      sidebar?.classList.toggle('collapsed');
      main?.classList.toggle('expanded');
    }
  });
}
