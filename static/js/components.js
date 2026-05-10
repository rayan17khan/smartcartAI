/* SmartCart AI – Reusable UI Components */

// ── Utility helpers ───────────────────────────────────────────────────────
function formatPrice(p) { return '₹' + Number(p).toLocaleString('en-IN', { maximumFractionDigits: 0 }); }
function formatRating(r) { return Number(r).toFixed(1); }
function stars(rating) {
  const full = Math.round(rating);
  return '★'.repeat(Math.min(full, 5)) + '☆'.repeat(Math.max(0, 5 - full));
}
function timeAgo(dateStr) {
  const d = new Date(dateStr), now = new Date();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
  return `${Math.floor(diff/86400)}d ago`;
}
function truncate(str, n = 50) { return str && str.length > n ? str.slice(0, n) + '…' : str; }

// ── Toast ────────────────────────────────────────────────────────────────
let _toastTimer;
function showToast(msg, type = 'info') {
  const el = document.getElementById('toast');
  const icons = { success: 'fa-check-circle', error: 'fa-times-circle', info: 'fa-info-circle' };
  el.className = `toast ${type}`;
  el.innerHTML = `<i class="fas ${icons[type] || 'fa-info-circle'}"></i> ${msg}`;
  el.classList.remove('hidden');
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.add('hidden'), 3200);
}

// ── Modal ─────────────────────────────────────────────────────────────────
function openModal(html) {
  document.getElementById('modalContent').innerHTML = html;
  document.getElementById('modalOverlay').classList.remove('hidden');
}
function closeModal() {
  document.getElementById('modalOverlay').classList.add('hidden');
}

// ── Loading spinner ───────────────────────────────────────────────────────
function spinnerHTML() {
  return `<div class="spinner-wrap"><div class="spinner"></div></div>`;
}

// ── Badge updater ─────────────────────────────────────────────────────────
function updateBadges() {
  const cartBadge = document.getElementById('cartBadge');
  const wBadge    = document.getElementById('wishlistBadge');
  const count     = Store.cartCount();
  const wCount    = Store.get('wishlist').length;
  if (cartBadge) { cartBadge.textContent = count; cartBadge.classList.toggle('hidden', count === 0); }
  if (wBadge)    { wBadge.textContent = wCount; wBadge.classList.toggle('hidden', wCount === 0); }

  const user     = Store.get('user');
  const navUser  = document.getElementById('navUsername');
  const adminBtn = document.getElementById('adminNavBtn');
  if (navUser) navUser.textContent = user ? user.username : 'Login';
  if (adminBtn) adminBtn.classList.toggle('hidden', !(user && user.is_admin));
}

// ── Product Card ─────────────────────────────────────────────────────────
function productCardHTML(p, opts = {}) {
  const wishlisted = Store.inWishlist(p.product_id);
  const disc       = p.discount_percent || 0;
  const recReason  = p.rec_reason ? `
    <div class="rec-reason"><i class="fas fa-robot"></i>${truncate(p.rec_reason, 40)}</div>` : '';
  // Category-specific image
  // image_url is now subcategory-matched in the dataset
  const _img = p.image_url || 'https://picsum.photos/seed/product/400/400';

  return `
  <div class="product-card" onclick="navigate('product', '${p.product_id}')">
    <div class="card-image-wrap">
      <img src="${_img}" alt="${p.product_name}" loading="lazy"
           onerror="this.src='https://picsum.photos/seed/fallback/400/400'"/>
      ${disc > 10 ? `<div class="card-discount-badge">${Math.round(disc)}% OFF</div>` : ''}
      ${p.is_featured ? `<div class="card-featured-badge">⭐ Featured</div>` : ''}
      <button class="card-wishlist-btn ${wishlisted ? 'wishlisted' : ''}"
        onclick="event.stopPropagation(); Store.toggleWishlist(${JSON.stringify(p).replace(/"/g,"'")})">
        <i class="fa${wishlisted ? 's' : 'r'} fa-heart"></i>
      </button>
    </div>
    <div class="card-body">
      <div class="card-brand">${p.brand || ''}</div>
      <div class="card-name">${p.product_name}</div>
      <div class="card-rating">
        <span class="stars">${stars(p.rating)}</span>
        <span class="card-rating-num">${formatRating(p.rating)} (${(p.num_reviews||0).toLocaleString()})</span>
      </div>
      ${recReason}
      <div class="card-price-row">
        <span class="card-price">${formatPrice(p.price)}</span>
        ${p.mrp && p.mrp > p.price ? `<span class="card-mrp">${formatPrice(p.mrp)}</span>` : ''}
        ${disc > 5 ? `<span class="card-off">${Math.round(disc)}% off</span>` : ''}
      </div>
    </div>
    <div class="card-actions">
      <button class="btn-cart" onclick="event.stopPropagation(); Store.addToCart(${JSON.stringify(p).replace(/"/g,"'")})">
        <i class="fas fa-cart-plus"></i> Cart
      </button>
      <button class="btn-buy" onclick="event.stopPropagation(); navigate('product','${p.product_id}')">
        Buy Now
      </button>
    </div>
  </div>`;
}

// ── Product Grid ──────────────────────────────────────────────────────────
function renderProductGrid(container, products, large = false) {
  if (!products || products.length === 0) {
    container.innerHTML = `<div class="empty-state">
      <div class="empty-icon">📦</div>
      <div class="empty-title">No products found</div>
      <div class="empty-sub">Try adjusting your filters or search query</div>
    </div>`;
    return;
  }
  container.innerHTML = `<div class="product-grid ${large ? 'large' : ''}">
    ${products.map(p => productCardHTML(p)).join('')}
  </div>`;
}

// ── Horizontal Scroll Strip ───────────────────────────────────────────────
function scrollStripHTML(id, products, title, icon = '', iconClass = 'blue') {
  if (!products || !products.length) return '';
  return `
  <div class="section-header">
    <div class="section-title">
      <div class="icon-badge ${iconClass}"><i class="${icon}"></i></div>
      ${title}
    </div>
    <span class="section-link" onclick="navigate('shop')">View All →</span>
  </div>
  <div class="scroll-strip-wrap">
    <button class="scroll-arrow left"  onclick="scrollStrip('${id}', -1)"><i class="fas fa-chevron-left"></i></button>
    <div class="scroll-strip" id="${id}">
      ${products.map(p => productCardHTML(p)).join('')}
    </div>
    <button class="scroll-arrow right" onclick="scrollStrip('${id}', 1)"><i class="fas fa-chevron-right"></i></button>
  </div>`;
}

function scrollStrip(id, dir) {
  const el = document.getElementById(id);
  if (el) el.scrollBy({ left: dir * 640, behavior: 'smooth' });
}

// ── Skeleton loaders ──────────────────────────────────────────────────────
function skeletonCards(n = 8) {
  return `<div class="product-grid">${Array(n).fill(`
    <div class="product-card" style="pointer-events:none">
      <div class="card-image-wrap skeleton" style="aspect-ratio:1"></div>
      <div class="card-body" style="gap:8px">
        <div class="skeleton" style="height:10px;width:60%;border-radius:4px"></div>
        <div class="skeleton" style="height:14px;width:90%;border-radius:4px"></div>
        <div class="skeleton" style="height:10px;width:80%;border-radius:4px"></div>
        <div class="skeleton" style="height:18px;width:50%;border-radius:4px"></div>
      </div>
    </div>`).join('')}</div>`;
}

// ── Flash Sale Timer ──────────────────────────────────────────────────────
let _timerInterval;
function startFlashTimer(id, hours = 5, mins = 47, secs = 22) {
  let total = hours*3600 + mins*60 + secs;
  function render() {
    const el = document.getElementById(id);
    if (!el) { clearInterval(_timerInterval); return; }
    const h = String(Math.floor(total/3600)).padStart(2,'0');
    const m = String(Math.floor((total%3600)/60)).padStart(2,'0');
    const s = String(total%60).padStart(2,'0');
    el.innerHTML = `
      <span class="timer-block">${h}</span><span class="timer-sep">:</span>
      <span class="timer-block">${m}</span><span class="timer-sep">:</span>
      <span class="timer-block">${s}</span>`;
    if (total > 0) total--;
  }
  render();
  clearInterval(_timerInterval);
  _timerInterval = setInterval(render, 1000);
}

// ── Search Dropdown ───────────────────────────────────────────────────────
let _searchTimer;
function initSearch() {
  const input    = document.getElementById('searchInput');
  const dropdown = document.getElementById('searchDropdown');
  if (!input) return;

  input.addEventListener('input', () => {
    clearTimeout(_searchTimer);
    const q = input.value.trim();
    if (q.length < 2) { dropdown.classList.add('hidden'); return; }
    _searchTimer = setTimeout(async () => {
      try {
        const data = await API.search(q, 6);
        if (!data.results.length) { dropdown.classList.add('hidden'); return; }
        dropdown.innerHTML = data.results.slice(0, 6).map(p => `
          <div class="search-item" onclick="navigate('product','${p.product_id}'); dropdown.classList.add('hidden')">
            <img src="${p.image_url}" alt="" onerror="this.src='https://picsum.photos/80/80'"/>
            <div class="search-item-info">
              <div class="search-item-name">${p.product_name}</div>
              <div class="search-item-price">${formatPrice(p.price)}
                ${p.discount_percent > 5 ? `<span style="color:#16a34a;font-size:10px;margin-left:4px">${Math.round(p.discount_percent)}% off</span>` : ''}
              </div>
            </div>
          </div>`).join('');
        dropdown.classList.remove('hidden');
      } catch (_) {}
    }, 300);
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      dropdown.classList.add('hidden');
      doSearch();
    }
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.nav-search')) dropdown.classList.add('hidden');
  });
}

function doSearch() {
  const q = document.getElementById('searchInput')?.value?.trim();
  if (q) navigate('search', q);
}
