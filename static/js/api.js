/* SmartCart AI – API Layer */

const API = {
  BASE: '/api',

  async _req(method, path, body = null) {
    const opts = {
      method,
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' }
    };
    if (body) opts.body = JSON.stringify(body);
    try {
      const res = await fetch(this.BASE + path, opts);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
      return data;
    } catch (e) {
      console.error('[API Error]', path, e.message);
      throw e;
    }
  },

  get:    (path)       => API._req('GET', path),
  post:   (path, body) => API._req('POST', path, body),
  put:    (path, body) => API._req('PUT', path, body),
  delete: (path)       => API._req('DELETE', path),

  // ── Auth ─────────────────────────────────────────────────────────────
  login:    (creds)    => API.post('/auth/login', creds),
  register: (data)     => API.post('/auth/register', data),
  logout:   ()         => API.post('/auth/logout'),
  me:       ()         => API.get('/auth/me'),
  updateProfile: (d)   => API._req('PUT', '/auth/profile', d),

  // ── Products ─────────────────────────────────────────────────────────
  getProducts(params = {}) {
    const q = new URLSearchParams(params).toString();
    return API.get(`/products${q ? '?' + q : ''}`);
  },
  getProduct: (id)     => API.get(`/products/${id}`),
  getCategories: ()    => API.get('/categories'),

  // ── Recommendations ──────────────────────────────────────────────────
  recommend(userId, n = 20) {
    const q = userId ? `?user_id=${userId}&n=${n}` : `?n=${n}`;
    return API.get(`/recommend${q}`);
  },
  trending(n = 20, category = null) {
    let q = `?n=${n}`;
    if (category) q += `&category=${encodeURIComponent(category)}`;
    return API.get(`/trending${q}`);
  },
  similar: (id, n = 10)   => API.get(`/similar/${id}?n=${n}`),
  search:  (q, n = 30)    => API.get(`/search?q=${encodeURIComponent(q)}&n=${n}`),
  explain: (uid, pid)     => API.get(`/explain?user_id=${uid}&product_id=${pid}`),

  // ── Cart ─────────────────────────────────────────────────────────────
  getCart:         ()       => API.get('/cart'),
  addToCart:       (d)      => API.post('/cart', d),
  updateCart:      (id, d)  => API._req('PUT', `/cart/${id}`, d),
  removeFromCart:  (id)     => API.delete(`/cart/${id}`),
  checkout:        ()       => API.post('/cart/checkout'),

  // ── Wishlist ─────────────────────────────────────────────────────────
  getWishlist:     ()       => API.get('/wishlist'),
  addToWishlist:   (d)      => API.post('/wishlist', d),
  removeWishlist:  (id)     => API.delete(`/wishlist/${id}`),

  // ── Reviews ──────────────────────────────────────────────────────────
  addReview: (d)            => API.post('/reviews', d),

  // ── Tracking ─────────────────────────────────────────────────────────
  track: (product_id, action) => API.post('/track', { product_id, action }),

  // ── Admin ─────────────────────────────────────────────────────────────
  analytics:  ()   => API.get('/admin/analytics'),
  adminUsers: ()   => API.get('/admin/users'),
  adminOrders:()   => API.get('/admin/orders'),
  evaluate:   ()   => API.get('/admin/evaluate'),
};
