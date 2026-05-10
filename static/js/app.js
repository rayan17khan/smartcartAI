/* ════════════════════════════════════════════════════════════
   SmartCart AI – Main App Entry Point & SPA Router
   Handles: routing, auth init, badge updates, navigation
════════════════════════════════════════════════════════════ */

// ─── Current route state ───────────────────────────────────────────────────
let _currentPage  = 'home';
let _currentParam = null;

// ─── SPA Router ───────────────────────────────────────────────────────────
async function navigate(page, param = null) {
  _currentPage  = page;
  _currentParam = param;

  // Scroll to top on page change
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Close any open search dropdown
  const dd = document.getElementById('searchDropdown');
  if (dd) dd.classList.add('hidden');

  // Update browser URL (pushState for SPA feel)
  const url = param ? `#${page}/${encodeURIComponent(param)}` : `#${page}`;
  history.pushState({ page, param }, '', url);

  // Render the correct page
  switch (page) {
    case 'home':     await renderHome();         break;
    case 'shop':     await renderShop(param);    break;
    case 'product':  await renderProduct(param); break;
    case 'cart':     await renderCart();         break;
    case 'wishlist': await renderWishlist();     break;
    case 'login':    renderAuth();               break;
    case 'search':   await renderSearch(param);  break;
    case 'admin':    await renderAdmin();        break;
    case 'profile':  renderProfile();            break;
    default:         await renderHome();
  }

  updateBadges();
}

// ─── Handle browser back/forward ──────────────────────────────────────────
window.addEventListener('popstate', (e) => {
  if (e.state) {
    navigate(e.state.page, e.state.param);
  } else {
    navigate('home');
  }
});

// ─── Parse hash on load ────────────────────────────────────────────────────
function parseHashRoute() {
  const hash = window.location.hash.replace('#', '');
  if (!hash) return { page: 'home', param: null };
  const parts = hash.split('/');
  return { page: parts[0], param: parts[1] ? decodeURIComponent(parts[1]) : null };
}

// ─── Profile Page ──────────────────────────────────────────────────────────
function renderProfile() {
  const user = Store.get('user');
  if (!user) { navigate('login'); return; }

  const root = document.getElementById('appRoot');
  root.innerHTML = `
  <div class="page" style="max-width:700px">
    <div style="font-size:22px;font-weight:800;margin-bottom:24px">
      <i class="fas fa-user-circle" style="color:var(--primary)"></i> My Profile
    </div>

    <div style="background:#fff;border-radius:var(--radius);box-shadow:var(--shadow-sm);padding:28px;border:1px solid var(--border)">
      <div style="display:flex;align-items:center;gap:20px;margin-bottom:24px">
        <div style="width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--accent));
          display:flex;align-items:center;justify-content:center;font-size:28px;color:#fff;font-weight:800">
          ${(user.username||'U')[0].toUpperCase()}
        </div>
        <div>
          <div style="font-size:20px;font-weight:700">${user.full_name || user.username}</div>
          <div style="color:var(--text-muted);font-size:14px">${user.email}</div>
          ${user.is_admin ? '<span class="tag" style="background:#fef3c7;color:#d97706;margin-top:6px;display:inline-block">⚡ Admin</span>' : ''}
        </div>
      </div>

      <div class="divider"></div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:20px">
        <div class="form-group">
          <label class="form-label">Full Name</label>
          <input class="form-input" type="text" id="pName" value="${user.full_name||''}" placeholder="Your full name"/>
        </div>
        <div class="form-group">
          <label class="form-label">City</label>
          <input class="form-input" type="text" id="pCity" value="${user.city||''}" placeholder="Your city"/>
        </div>
        <div class="form-group" style="grid-column:1/-1">
          <label class="form-label">Preferred Categories (comma-separated)</label>
          <input class="form-input" type="text" id="pCats"
            value="${user.preferred_categories||''}"
            placeholder="e.g. Electronics, Books, Sports"/>
        </div>
      </div>

      <div style="display:flex;gap:12px;margin-top:8px">
        <button class="btn btn-primary" onclick="saveProfile()">
          <i class="fas fa-save"></i> Save Changes
        </button>
        <button class="btn btn-danger" onclick="doLogout()">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:20px">
      ${profileStatCard('Cart Items',  Store.cartCount(), 'fas fa-shopping-cart', '#dbeafe')}
      ${profileStatCard('Wishlist',    Store.get('wishlist').length, 'fas fa-heart', '#fce7f3')}
      ${profileStatCard('Recently Viewed', Store.get('recentlyViewed').length, 'fas fa-history', '#dcfce7')}
    </div>
  </div>`;
}

function profileStatCard(label, val, icon, bg) {
  return `<div style="background:#fff;border-radius:var(--radius);padding:18px;text-align:center;
    box-shadow:var(--shadow-sm);border:1px solid var(--border)">
    <div style="width:40px;height:40px;border-radius:10px;background:${bg};
      display:flex;align-items:center;justify-content:center;margin:0 auto 8px">
      <i class="${icon}" style="color:${bg.replace(/e7|e9|c7|d1|e0|e2/g,'5').replace(/f/g,'3')}"></i>
    </div>
    <div style="font-size:24px;font-weight:800">${val}</div>
    <div style="font-size:12px;color:var(--text-muted)">${label}</div>
  </div>`;
}

async function saveProfile() {
  const full_name            = document.getElementById('pName')?.value;
  const city                 = document.getElementById('pCity')?.value;
  const preferred_categories = document.getElementById('pCats')?.value;
  try {
    const data = await API.updateProfile({ full_name, city, preferred_categories });
    Store.set('user', data.user);
    showToast('Profile updated ✓', 'success');
    updateBadges();
  } catch(e) { showToast(e.message, 'error'); }
}

async function doLogout() {
  try {
    await API.logout();
  } catch(_) {}
  Store.logout();
  updateBadges();
  showToast('Logged out successfully', 'info');
  navigate('home');
}

// ─── Auth button click (toggle between Login & Profile) ───────────────────
document.getElementById('authBtn')?.addEventListener('click', () => {
  const user = Store.get('user');
  navigate(user ? 'profile' : 'login');
});

// ─── Real-time recommendation polling ─────────────────────────────────────
// Polls every 5 min to refresh recommendations silently
let _recPollTimer = null;
function startRecPolling() {
  clearInterval(_recPollTimer);
  _recPollTimer = setInterval(() => {
    if (_currentPage === 'home') renderHome();
  }, 5 * 60 * 1000);
}

// ─── Keyboard shortcuts ────────────────────────────────────────────────────
document.addEventListener('keydown', (e) => {
  // '/' focuses search
  if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
    e.preventDefault();
    document.getElementById('searchInput')?.focus();
  }
  // Escape closes modal
  if (e.key === 'Escape') closeModal();
});

// ─── Infinite scroll stub (for shop page) ─────────────────────────────────
window.addEventListener('scroll', () => {
  if (_currentPage !== 'shop') return;
  const scrolled   = window.scrollY + window.innerHeight;
  const docHeight  = document.documentElement.scrollHeight;
  // Could trigger next page load here
});

// ─── App Bootstrap ─────────────────────────────────────────────────────────
async function init() {
  // 1. Check auth session
  await Store.loadUser();

  // 2. Load user data if logged in
  const user = Store.get('user');
  if (user) {
    await Promise.all([ Store.loadCart(), Store.loadWishlist() ]);
  }

  // 3. Update nav badges
  updateBadges();

  // 4. Wire up Store events → badge refresh
  Store.on('cart',     updateBadges);
  Store.on('wishlist', updateBadges);
  Store.on('user',     updateBadges);

  // 5. Init search autocomplete
  initSearch();

  // 6. Route to correct page
  const { page, param } = parseHashRoute();
  await navigate(page, param);

  // 7. Start real-time polling
  startRecPolling();

  console.log('%cSmartCart AI ✓', 'color:#2874f0;font-size:16px;font-weight:bold');
  console.log('%cML-powered e-commerce recommendation system', 'color:#7c3aed');
}

// Kick off
init().catch(console.error);
