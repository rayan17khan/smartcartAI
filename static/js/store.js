/* SmartCart AI – Global State Store */

const Store = (() => {
  let state = {
    user:             null,
    cart:             [],
    wishlist:         [],
    recentlyViewed:   [],   // starts empty — loaded per user after login
    currentPage:      'home',
    searchQuery:      '',
    selectedCategory: null,
  };

  const listeners = {};

  function on(event, fn) {
    if (!listeners[event]) listeners[event] = [];
    listeners[event].push(fn);
  }
  function emit(event, data) {
    (listeners[event] || []).forEach(fn => fn(data));
  }

  function set(key, val) {
    state[key] = val;
    emit('change', { key, val });
    emit(key, val);
  }

  function get(key) { return state[key]; }

  // ── Recently Viewed helpers ───────────────────────────────────────────────
  function _recentKey(user) {
    return user ? `sc_recent_${user.user_id}` : 'sc_recent_guest';
  }

  // Load the correct recently-viewed list for a given user from localStorage
  function loadRecentlyViewed(user) {
    const key    = _recentKey(user);
    const recent = JSON.parse(localStorage.getItem(key) || '[]');
    set('recentlyViewed', recent);
  }

  // ── User ──────────────────────────────────────────────────────────────────
  async function loadUser() {
    try {
      const data = await API.me();
      if (data.authenticated) {
        set('user', data.user);
        loadRecentlyViewed(data.user);   // ← load THIS user's history
        emit('userLoaded', data.user);
      } else {
        loadRecentlyViewed(null);        // ← load guest history
      }
    } catch (_) {
      loadRecentlyViewed(null);
    }
  }

  function logout() {
    set('user', null);
    set('cart', []);
    set('wishlist', []);
    loadRecentlyViewed(null);            // ← switch to guest history on logout
  }

  // ── Cart ──────────────────────────────────────────────────────────────────
  async function loadCart() {
    if (!state.user) { set('cart', []); return; }
    try {
      const data = await API.getCart();
      set('cart', data.cart || []);
    } catch (_) {}
  }

  function cartCount()  { return state.cart.reduce((s, i) => s + (i.quantity||1), 0); }
  function cartTotal()  { return state.cart.reduce((s, i) => s + i.price * (i.quantity||1), 0); }
  function inCart(pid)  { return state.cart.some(i => i.product_id === pid); }

  async function addToCart(product) {
    if (!state.user) { navigate('login'); showToast('Please login to add items to cart', 'info'); return; }
    try {
      await API.addToCart({ product_id: product.product_id, quantity: 1 });
      await loadCart();
      updateBadges();
      showToast(`${product.product_name} added to cart ✓`, 'success');
    } catch (e) { showToast(e.message, 'error'); }
  }

  async function removeFromCart(cartItemId) {
    try {
      await API.removeFromCart(cartItemId);
      await loadCart();
      updateBadges();
    } catch (e) { showToast(e.message, 'error'); }
  }

  // ── Wishlist ──────────────────────────────────────────────────────────────
  async function loadWishlist() {
    if (!state.user) { set('wishlist', []); return; }
    try {
      const data = await API.getWishlist();
      set('wishlist', data.wishlist || []);
    } catch (_) {}
  }

  function inWishlist(pid) { return state.wishlist.some(i => i.product_id === pid); }

  async function toggleWishlist(product) {
    if (!state.user) { navigate('login'); showToast('Please login to use wishlist', 'info'); return; }
    const existing = state.wishlist.find(i => i.product_id === product.product_id);
    try {
      if (existing) {
        await API.removeWishlist(existing.wishlist_item_id);
        showToast('Removed from wishlist', 'info');
      } else {
        await API.addToWishlist({ product_id: product.product_id });
        showToast('Added to wishlist ♥', 'success');
      }
      await loadWishlist();
      updateBadges();
    } catch (e) { showToast(e.message, 'error'); }
  }

  // ── Recently Viewed ───────────────────────────────────────────────────────
  function addRecentlyViewed(product) {
    const user       = state.user;
    const storageKey = _recentKey(user);

    let recent = state.recentlyViewed.filter(p => p.product_id !== product.product_id);
    recent.unshift(product);
    recent = recent.slice(0, 12);
    set('recentlyViewed', recent);
    localStorage.setItem(storageKey, JSON.stringify(recent));   // save under user-specific key
  }

  return {
    get, set, on, emit,
    loadUser, logout,
    loadCart, cartCount, cartTotal, inCart, addToCart, removeFromCart,
    loadWishlist, inWishlist, toggleWishlist,
    addRecentlyViewed, loadRecentlyViewed,
  };
})();