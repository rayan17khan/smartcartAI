/* SmartCart AI – Page Renderers (v3 – images match products) */

// ── Get the correct image for a product (uses DB image_url which has matched seeds) ──
function getProductImage(p) {
  // image_url already has a subcategory-matched seed from the dataset
  return p.image_url || `https://picsum.photos/seed/product${p.product_id}/400/400`;
}

// ════════════════════════════════════════════════════════════
// HOME PAGE
// ════════════════════════════════════════════════════════════
async function renderHome() {
  const root = document.getElementById('appRoot');
  root.innerHTML = `<div class="page" id="homePage">
    ${heroHTML()}
    ${offerCardsHTML()}
    <div id="homeRecs">${skeletonCards(8)}</div>
    <div id="homeTrending">${skeletonCards(8)}</div>
    <div id="homeRecent"></div>
    <div id="homeCategories"></div>
  </div>`;

  startFlashTimer('flashTimer');
  const user = Store.get('user');

  try {
    const data = await API.recommend(user?.user_id, 20);
    const recs  = data.recommendations || [];
    document.getElementById('homeRecs').innerHTML =
      scrollStripHTML('recStrip', recs,
        user ? `<span class="ai-badge"><i class="fas fa-brain"></i> AI</span> Recommended for You`
              : '<span class="ai-badge"><i class="fas fa-fire"></i> AI</span> Top Picks',
        'fas fa-robot', 'purple');
  } catch(_) {}

  try {
    const data = await API.trending(20);
    document.getElementById('homeTrending').innerHTML =
      scrollStripHTML('trendStrip', data.trending || [],
        '🔥 Trending Right Now', 'fas fa-fire', 'gold');
  } catch(_) {}

  const recent = Store.get('recentlyViewed');
  if (recent.length > 0) {
    document.getElementById('homeRecent').innerHTML =
      scrollStripHTML('recentStrip', recent, '🕐 Recently Viewed', 'fas fa-history', 'blue');
  }

  document.getElementById('homeCategories').innerHTML = categoryQuickLinks();
}

function heroHTML() {
  return `
  <div class="hero">
    <div class="hero-text">
      <h1>Shop Smarter with <span>AI</span> Recommendations</h1>
      <p>Personalised picks curated just for you using machine learning</p>
      <div style="display:flex;gap:12px;flex-wrap:wrap">
        <button class="btn btn-primary btn-lg" onclick="navigate('shop')">
          <i class="fas fa-shopping-bag"></i> Explore Products
        </button>
        <button class="btn" style="background:rgba(255,255,255,.15);color:#fff;padding:14px 28px;font-size:16px;font-weight:600;border-radius:var(--radius-sm)" onclick="navigate('login')">
          <i class="fas fa-user-plus"></i> Join Free
        </button>
      </div>
      <div class="hero-badges" style="margin-top:20px">
        <div class="hero-badge"><i class="fas fa-brain"></i> AI-Powered Recs</div>
        <div class="hero-badge"><i class="fas fa-shield-alt"></i> Secure Checkout</div>
        <div class="hero-badge"><i class="fas fa-truck"></i> Free Delivery ₹499+</div>
        <div class="hero-badge"><i class="fas fa-undo"></i> 30-Day Returns</div>
      </div>
    </div>
    <div class="hero-visual">🛍️</div>
  </div>
  <div class="flash-sale">
    <div class="flash-title"><i class="fas fa-bolt"></i> Flash Sale – Ending in</div>
    <div class="flash-timer" id="flashTimer"></div>
    <button class="btn" style="background:rgba(255,255,255,.2);color:#fff;border:2px solid rgba(255,255,255,.4)"
      onclick="shopState.category=null;shopState.page=1;navigate('shop')">
      Grab Deals <i class="fas fa-arrow-right"></i>
    </button>
  </div>`;
}

function offerCardsHTML() {
  return `
  <div class="offer-cards">
    <div class="offer-card blue" onclick="goCategory('Electronics')">
      <div class="offer-icon">⚡</div>
      <div><div class="offer-title">Electronics Sale</div><div class="offer-sub">Up to 60% off on gadgets</div></div>
    </div>
    <div class="offer-card purple" onclick="goCategory('Fashion')">
      <div class="offer-icon">👗</div>
      <div><div class="offer-title">Fashion Week</div><div class="offer-sub">New arrivals & trending styles</div></div>
    </div>
    <div class="offer-card gold" onclick="goCategory('Home & Kitchen')">
      <div class="offer-icon">🏠</div>
      <div><div class="offer-title">Home Makeover</div><div class="offer-sub">Upgrade your home today</div></div>
    </div>
  </div>`;
}

// Navigate to a specific category in the shop
function goCategory(cat) {
  shopState.category = cat;
  shopState.page = 1;
  navigate('shop');
}

function categoryQuickLinks() {
  const cats = [
    { name:'Electronics',    emoji:'📱', color:'#dbeafe' },
    { name:'Fashion',        emoji:'👗', color:'#fce7f3' },
    { name:'Home & Kitchen', emoji:'🏠', color:'#dcfce7' },
    { name:'Books',          emoji:'📚', color:'#fef3c7' },
    { name:'Sports',         emoji:'⚽', color:'#ede9fe' },
    { name:'Beauty',         emoji:'💄', color:'#ffe4e6' },
    { name:'Toys',           emoji:'🎮', color:'#e0f2fe' },
    { name:'Grocery',        emoji:'🌿', color:'#d1fae5' },
    { name:'Health',         emoji:'❤️',  color:'#fee2e2' },
    { name:'Automotive',     emoji:'🚗', color:'#f3f4f6' },
  ];
  return `
  <div class="section-header">
    <div class="section-title"><div class="icon-badge blue"><i class="fas fa-th"></i></div> Shop by Category</div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:12px;margin-bottom:32px">
    ${cats.map(c => `
      <div onclick="goCategory('${c.name}')"
        style="background:${c.color};border-radius:var(--radius);padding:20px 12px;text-align:center;cursor:pointer;transition:var(--transition);border:1.5px solid transparent"
        onmouseover="this.style.transform='translateY(-3px)';this.style.boxShadow='var(--shadow)'"
        onmouseout="this.style.transform='';this.style.boxShadow=''">
        <div style="font-size:32px;margin-bottom:6px">${c.emoji}</div>
        <div style="font-size:12px;font-weight:600;color:var(--text)">${c.name}</div>
      </div>`).join('')}
  </div>`;
}

function getCatEmoji(cat) {
  const map = {
    'Electronics':'📱','Fashion':'👗','Home & Kitchen':'🏠','Books':'📚',
    'Sports':'⚽','Beauty':'💄','Toys':'🎮','Grocery':'🌿','Health':'❤️','Automotive':'🚗'
  };
  return map[cat] || '🛍️';
}

// ════════════════════════════════════════════════════════════
// SHOP / PRODUCT LISTING
// ════════════════════════════════════════════════════════════
let shopState = {
  page:1, category:null, min_price:null, max_price:null, min_rating:null, sort:'popularity'
};

async function renderShop(category = null) {
  if (category) { shopState.category = category; shopState.page = 1; }
  const root = document.getElementById('appRoot');
  const currentCat = shopState.category;

  root.innerHTML = `
  <div class="page">
    ${currentCat ? `<div class="breadcrumb">
      <span onclick="shopState.category=null;navigate('shop')">All Products</span>
      <i class="fas fa-chevron-right"></i>
      <span style="color:var(--primary);font-weight:600">${getCatEmoji(currentCat)} ${currentCat}</span>
    </div>` : ''}
    <div class="shop-layout">
      <div class="filter-sidebar">
        <div class="filter-title">🎯 Filters</div>
        <div class="filter-section">
          <div class="filter-label">Category</div>
          <div class="rating-opt">
            <input type="radio" name="catFilter" value="" ${!currentCat?'checked':''}
              onchange="shopSetCategory(null)"/> 🛍️ All Categories
          </div>
          ${['Electronics','Fashion','Home & Kitchen','Books','Sports','Beauty','Toys','Grocery','Health','Automotive']
            .map(c=>`<div class="rating-opt">
              <input type="radio" name="catFilter" value="${c}" ${currentCat===c?'checked':''}
                onchange="shopSetCategory('${c}')"/>
              ${getCatEmoji(c)} ${c}
            </div>`).join('')}
        </div>
        <div class="filter-section">
          <div class="filter-label">Price Range</div>
          <div class="range-wrap">
            <input class="range-input" type="number" placeholder="Min ₹" id="fMinP" value="${shopState.min_price||''}"/>
            <input class="range-input" type="number" placeholder="Max ₹" id="fMaxP" value="${shopState.max_price||''}"/>
          </div>
          <button class="btn btn-outline btn-sm" style="width:100%;margin-top:8px" onclick="shopApplyPriceFilter()">Apply</button>
        </div>
        <div class="filter-section">
          <div class="filter-label">Minimum Rating</div>
          <div class="rating-filter">
            ${[4,3,2,1].map(r=>`<div class="rating-opt">
              <input type="radio" name="ratingFilter" value="${r}" ${shopState.min_rating==r?'checked':''}
                onchange="shopApplyFilter('min_rating',${r})"/>
              ${'★'.repeat(r)}${'☆'.repeat(5-r)} & above
            </div>`).join('')}
            <div class="rating-opt" style="color:var(--primary);font-weight:600;cursor:pointer"
              onclick="shopApplyFilter('min_rating',null)">✕ Clear rating</div>
          </div>
        </div>
        <div class="filter-section">
          <div class="filter-label">Sort By</div>
          <select class="sort-select" onchange="shopApplyFilter('sort',this.value)">
            <option value="popularity" ${shopState.sort==='popularity'?'selected':''}>Popularity</option>
            <option value="rating"     ${shopState.sort==='rating'    ?'selected':''}>Highest Rated</option>
            <option value="price_asc"  ${shopState.sort==='price_asc' ?'selected':''}>Price: Low to High</option>
            <option value="price_desc" ${shopState.sort==='price_desc'?'selected':''}>Price: High to Low</option>
            <option value="discount"   ${shopState.sort==='discount'  ?'selected':''}>Best Discount</option>
          </select>
        </div>
        <button class="btn btn-ghost btn-sm" style="width:100%;margin-top:4px;color:var(--danger)"
          onclick="shopClearAll()">✕ Clear All Filters</button>
      </div>
      <div class="shop-products">
        <div class="shop-header">
          <div class="shop-count" id="shopCount">Loading products…</div>
        </div>
        <div id="shopGrid">${skeletonCards(12)}</div>
        <div id="shopPager"></div>
      </div>
    </div>
  </div>`;
  await loadShopProducts();
}

function shopSetCategory(cat) {
  shopState.category = cat;
  shopState.page = 1;
  renderShop();
}

function shopClearAll() {
  shopState = { page:1, category:null, min_price:null, max_price:null, min_rating:null, sort:'popularity' };
  renderShop();
}

async function loadShopProducts() {
  const params = { page:shopState.page, per_page:24, sort:shopState.sort };
  if (shopState.category)   params.category   = shopState.category;
  if (shopState.min_price)  params.min_price   = shopState.min_price;
  if (shopState.max_price)  params.max_price   = shopState.max_price;
  if (shopState.min_rating) params.min_rating  = shopState.min_rating;

  try {
    const data = await API.getProducts(params);
    const { products, total, pages } = data;
    const countEl = document.getElementById('shopCount');
    const gridEl  = document.getElementById('shopGrid');
    const pagerEl = document.getElementById('shopPager');
    if (!gridEl) return;
    if (countEl) {
      const catLabel = shopState.category
        ? `<span class="ai-badge">${getCatEmoji(shopState.category)} ${shopState.category}</span> `
        : '';
      countEl.innerHTML = `${catLabel}<strong>${total.toLocaleString()}</strong> products found`;
    }
    renderProductGrid(gridEl, products, true);
    renderPagination(pagerEl, shopState.page, pages);
  } catch(e) {
    const gridEl = document.getElementById('shopGrid');
    if (gridEl) gridEl.innerHTML = `<div class="empty-state">
      <div class="empty-icon">⚠️</div>
      <div class="empty-title">Error loading products</div>
      <div class="empty-sub">${e.message}</div></div>`;
  }
}

function shopApplyFilter(key, val) { shopState[key]=val; shopState.page=1; loadShopProducts(); }
function shopApplyPriceFilter() {
  shopState.min_price = document.getElementById('fMinP')?.value||null;
  shopState.max_price = document.getElementById('fMaxP')?.value||null;
  shopState.page = 1; loadShopProducts();
}

function renderPagination(container, current, total) {
  if (!container||total<=1) { if(container) container.innerHTML=''; return; }
  const makeBtn = (p,label,active) =>
    `<button class="page-btn ${active?'active':''}" onclick="shopGoPage(${p})">${label}</button>`;
  let html = makeBtn(1,'«',false);
  if (current>1) html += makeBtn(current-1,'‹',false);
  for (let i=Math.max(1,current-2); i<=Math.min(total,current+2); i++) html+=makeBtn(i,i,i===current);
  if (current<total) html += makeBtn(current+1,'›',false);
  html += makeBtn(total,'»',false);
  container.innerHTML = `<div class="pagination">${html}</div>`;
}

function shopGoPage(p) { shopState.page=p; loadShopProducts(); window.scrollTo({top:0,behavior:'smooth'}); }

// Navbar top category bar
function filterCategory(cat, el) {
  shopState.category = cat;
  shopState.page = 1;
  document.querySelectorAll('.cat-item').forEach(i=>i.classList.remove('active'));
  if (el) el.classList.add('active');
  navigate('shop');
}

// ════════════════════════════════════════════════════════════
// PRODUCT DETAIL PAGE
// ════════════════════════════════════════════════════════════
async function renderProduct(productId) {
  const root = document.getElementById('appRoot');
  root.innerHTML = `<div class="page">${spinnerHTML()}</div>`;

  try {
    const data    = await API.getProduct(productId);
    const product = data.product;
    const reviews = data.reviews || [];
    const user    = Store.get('user');
    const img     = getProductImage(product);  // subcategory-matched image

    Store.addRecentlyViewed(product);
    API.track(productId, 'view').catch(()=>{});

    let explanation = 'Trending in your region';
    if (user) {
      try { const ex = await API.explain(user.user_id, productId); explanation = ex.explanation; } catch(_){}
    }

    // Build 4 thumbnail variants using the same seed family
    const thumbs = [0,1,2,3].map(i => {
      // slightly vary the seed by appending a letter
      const seed = img.split('/seed/')[1]?.split('/')[0] || 'product';
      const variants = ['',  'a', 'b', 'c'];
      return `https://picsum.photos/seed/${seed}${variants[i]}/80/80`;
    });

    root.innerHTML = `
    <div class="page">
      <div class="breadcrumb">
        <span onclick="navigate('home')">Home</span>
        <i class="fas fa-chevron-right"></i>
        <span onclick="goCategory('${product.category}')"
          style="color:var(--primary);cursor:pointer">${getCatEmoji(product.category)} ${product.category}</span>
        <i class="fas fa-chevron-right"></i>
        <span style="color:var(--text)">${truncate(product.product_name, 42)}</span>
      </div>

      <div class="detail-layout">
        <div class="detail-images">
          <img class="detail-main-img" id="mainImg" src="${img}" alt="${product.product_name}"
               onerror="this.src='https://picsum.photos/400/400'"/>
          <div style="display:flex;gap:8px;margin-top:12px">
            ${thumbs.map(t=>`
              <img src="${t}" onclick="document.getElementById('mainImg').src=this.src"
                style="width:70px;height:70px;object-fit:cover;border-radius:8px;cursor:pointer;
                       border:2px solid var(--border);transition:var(--transition)"
                onmouseover="this.style.borderColor='var(--primary)'"
                onmouseout="this.style.borderColor='var(--border)'"
                onerror="this.style.display='none'"/>`).join('')}
          </div>
          <div style="margin-top:16px;padding:14px;background:var(--primary-light);border-radius:var(--radius-sm);border:1.5px solid var(--primary)">
            <div class="ai-badge" style="margin-bottom:8px"><i class="fas fa-brain"></i> AI Insight</div>
            <div style="font-size:13px;color:var(--text);line-height:1.5">${explanation}</div>
          </div>
        </div>

        <div class="detail-info">
          <div class="detail-brand">${product.brand||''}</div>
          <div class="detail-name">${product.product_name}</div>

          <div class="detail-rating-row">
            <div class="rating-pill"><i class="fas fa-star"></i> ${formatRating(product.rating)}</div>
            <span class="detail-reviews">${(product.num_reviews||0).toLocaleString()} ratings</span>
            ${product.is_featured?`<span class="chip active" style="font-size:11px">⭐ Featured</span>`:''}
          </div>

          <div class="detail-price-block">
            <div style="display:flex;align-items:baseline;gap:12px">
              <span class="detail-price">${formatPrice(product.price)}</span>
              ${product.mrp>product.price?`
              <span class="detail-mrp">${formatPrice(product.mrp)}</span>
              <span class="detail-off">${Math.round(product.discount_percent||0)}% off</span>`:''}
            </div>
            <div style="margin-top:8px;display:flex;align-items:center;gap:12px;flex-wrap:wrap">
              <span class="delivery-badge"><i class="fas fa-truck"></i> Free Delivery</span>
              ${product.stock>0
                ?`<span style="color:#16a34a;font-size:13px;font-weight:600">✓ In Stock (${product.stock} units)</span>`
                :`<span style="color:#ef4444;font-size:13px;font-weight:600">✗ Out of Stock</span>`}
            </div>
          </div>

          <div class="divider"></div>
          <div class="detail-desc">${product.description}</div>

          <table class="spec-table" style="margin-top:12px">
            <tr><td>Category</td>
              <td><span onclick="goCategory('${product.category}')"
                style="color:var(--primary);cursor:pointer;font-weight:600">
                ${getCatEmoji(product.category)} ${product.category}</span></td></tr>
            <tr><td>Type</td><td>${product.subcategory||'—'}</td></tr>
            <tr><td>Brand</td><td><strong>${product.brand}</strong></td></tr>
            <tr><td>Rating</td><td>${formatRating(product.rating)} / 5.0 ⭐</td></tr>
            <tr><td>Reviews</td><td>${(product.num_reviews||0).toLocaleString()} customers</td></tr>
            <tr><td>Stock</td><td>${product.stock} units available</td></tr>
            <tr><td>Discount</td><td><span style="color:#16a34a;font-weight:600">${Math.round(product.discount_percent||0)}% off</span></td></tr>
            <tr><td>Tags</td><td>${(product.tags||'').split(',').map(t=>`<span class="tag">${t.trim()}</span>`).join(' ')}</td></tr>
          </table>

          <div class="detail-actions">
            <button class="btn btn-primary btn-lg"
              onclick='Store.addToCart(${JSON.stringify(product)})'>
              <i class="fas fa-cart-plus"></i> Add to Cart
            </button>
            <button class="btn btn-accent btn-lg"
              onclick='buyNow(${JSON.stringify(product)})'>
              <i class="fas fa-bolt"></i> Buy Now
            </button>
            <button class="btn btn-outline btn-lg"
              onclick='Store.toggleWishlist(${JSON.stringify(product)})'>
              <i class="fas fa-heart"></i> Wishlist
            </button>
          </div>

          <div class="divider"></div>
          <div class="tabs-wrap">
            <button class="tab-btn active" onclick="switchDetailTab('reviews',this)">
              Reviews (${reviews.length})</button>
            <button class="tab-btn" onclick="switchDetailTab('qna',this)">Q&amp;A</button>
          </div>
          <div id="detailTabContent">${renderReviews(reviews, productId)}</div>
        </div>
      </div>

      <div id="similarSection" style="margin-top:40px">${skeletonCards(6)}</div>
    </div>`;

    try {
      const sim = await API.similar(productId, 10);
      document.getElementById('similarSection').innerHTML =
        scrollStripHTML('simStrip', sim.similar,
          '🔗 You May Also Like', 'fas fa-link', 'purple');
    } catch(_){}

  } catch(e) {
    root.innerHTML = `<div class="page"><div class="empty-state">
      <div class="empty-icon">⚠️</div>
      <div class="empty-title">Product not found</div>
      <div class="empty-sub">${e.message}</div>
      <button class="btn btn-primary" onclick="navigate('home')">Go Home</button>
    </div></div>`;
  }
}

function renderReviews(reviews, productId) {
  const user = Store.get('user');
  const form = user?`
    <div style="background:var(--bg);border-radius:var(--radius-sm);padding:16px;margin-bottom:16px">
      <div style="font-size:14px;font-weight:600;margin-bottom:10px">✍️ Write a Review</div>
      <div style="display:flex;gap:8px;margin-bottom:8px">
        ${[5,4,3,2,1].map(r=>`<button class="btn btn-ghost btn-sm" onclick="setReviewRating(${r},this)" data-r="${r}">${'★'.repeat(r)}</button>`).join('')}
      </div>
      <textarea id="reviewText" placeholder="Share your experience with this product…"
        style="width:100%;padding:10px;border:1.5px solid var(--border);border-radius:8px;
               font-size:13px;resize:vertical;min-height:80px;font-family:inherit"></textarea>
      <button class="btn btn-primary btn-sm" style="margin-top:8px" onclick="submitReview('${productId}')">
        <i class="fas fa-paper-plane"></i> Submit Review
      </button>
    </div>`:
    `<div style="font-size:13px;color:var(--text-muted);margin-bottom:12px">
      <a onclick="navigate('login')" style="color:var(--primary);cursor:pointer;font-weight:600">Login</a> to write a review
    </div>`;

  const cards = reviews.length
    ?reviews.map(r=>`
      <div class="review-card">
        <div class="review-header">
          <span class="review-user">${r.user||'Anonymous'}</span>
          <span class="review-stars">${stars(r.rating)}</span>
        </div>
        <div class="review-text">${r.comment||'No comment provided'}</div>
        <div class="review-date">${r.date?new Date(r.date).toLocaleDateString():''}</div>
      </div>`).join('')
    :`<div class="empty-state" style="padding:30px">
        <div class="empty-icon">📝</div>
        <div class="empty-title">No reviews yet</div>
        <div class="empty-sub">Be the first to review this product!</div>
      </div>`;
  return form+cards;
}

let _reviewRating = 5;
function setReviewRating(r,btn) {
  _reviewRating=r;
  document.querySelectorAll('[data-r]').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
}
async function submitReview(productId) {
  const comment = document.getElementById('reviewText')?.value;
  try {
    await API.addReview({ product_id:productId, rating:_reviewRating, comment });
    showToast('Review submitted! Thank you ✓','success');
    renderProduct(productId);
  } catch(e) { showToast(e.message,'error'); }
}

function switchDetailTab(tab,btn) {
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  const el = document.getElementById('detailTabContent');
  if (tab==='qna') el.innerHTML=`<div class="empty-state" style="padding:30px">
    <div class="empty-icon">💬</div><div class="empty-title">No Q&A yet</div>
    <div class="empty-sub">Be the first to ask a question!</div></div>`;
}

async function buyNow(product) {
  await Store.addToCart(product); navigate('cart');
}

// ════════════════════════════════════════════════════════════
// CART PAGE
// ════════════════════════════════════════════════════════════
async function renderCart() {
  const root = document.getElementById('appRoot');
  const user = Store.get('user');
  if (!user) {
    root.innerHTML=`<div class="page"><div class="empty-state" style="min-height:50vh">
      <div class="empty-icon">🛒</div>
      <div class="empty-title">Your cart is waiting!</div>
      <div class="empty-sub">Login to view and manage your cart</div>
      <button class="btn btn-primary btn-lg" onclick="navigate('login')"><i class="fas fa-sign-in-alt"></i> Login Now</button>
    </div></div>`; return;
  }
  root.innerHTML=`<div class="page">${spinnerHTML()}</div>`;
  await Store.loadCart();
  const cart = Store.get('cart');

  if (!cart.length) {
    root.innerHTML=`<div class="page"><div class="empty-state">
      <div class="empty-icon">🛒</div>
      <div class="empty-title">Your cart is empty</div>
      <div class="empty-sub">Add products to your cart and they'll show up here</div>
      <button class="btn btn-primary btn-lg" onclick="navigate('shop')"><i class="fas fa-shopping-bag"></i> Start Shopping</button>
    </div></div>`; return;
  }

  const subtotal=cart.reduce((s,i)=>s+i.price*i.quantity,0);
  const savings =cart.reduce((s,i)=>s+((i.mrp||i.price)-i.price)*i.quantity,0);
  const delivery=subtotal>=499?0:49;
  const total   =subtotal+delivery;

  root.innerHTML=`
  <div class="page">
    <div style="font-size:22px;font-weight:800;margin-bottom:20px">
      <i class="fas fa-shopping-cart" style="color:var(--primary)"></i> Shopping Cart
      <span style="font-size:14px;font-weight:400;color:var(--text-muted);margin-left:8px">(${cart.length} items)</span>
    </div>
    <div class="cart-layout">
      <div><div class="cart-items-list">${cart.map(item=>cartItemHTML(item)).join('')}</div></div>
      <div>
        <div class="order-summary">
          <div class="summary-title">Order Summary</div>
          <div class="summary-row"><span>Subtotal (${cart.length} items)</span><span>${formatPrice(subtotal)}</span></div>
          ${savings>0?`<div class="summary-row"><span>Discount</span><span class="savings">- ${formatPrice(savings)}</span></div>`:''}
          <div class="summary-row"><span>Delivery</span><span>${delivery===0?'<span style="color:#16a34a;font-weight:600">FREE</span>':formatPrice(delivery)}</span></div>
          <div class="summary-row total"><span>Total</span><span>${formatPrice(total)}</span></div>
          ${savings>0?`<div style="background:#dcfce7;color:#16a34a;padding:8px 12px;border-radius:8px;font-size:13px;font-weight:600;margin-top:8px">
            <i class="fas fa-tag"></i> You save ${formatPrice(savings)} on this order!</div>`:''}
          <div class="promo-row">
            <input class="promo-input" placeholder="Promo code"/>
            <button class="btn btn-outline btn-sm" onclick="showToast('Promo applied! 10% off','success')">Apply</button>
          </div>
          <button class="btn btn-primary btn-lg btn-block" onclick="doCheckout()" style="margin-top:12px">
            <i class="fas fa-shield-alt"></i> Secure Checkout
          </button>
          <div style="text-align:center;margin-top:10px;font-size:12px;color:var(--text-muted)">
            <i class="fas fa-lock"></i> 100% Secure Payments
          </div>
        </div>
      </div>
    </div>
  </div>`;
}

function cartItemHTML(item) {
  const img = getProductImage(item);
  return `
  <div class="cart-item-card">
    <img class="cart-item-img" src="${img}" alt="${item.product_name}"
         onerror="this.src='https://picsum.photos/90/90'"
         onclick="navigate('product','${item.product_id}')" style="cursor:pointer"/>
    <div class="cart-item-info">
      <div class="cart-item-name" onclick="navigate('product','${item.product_id}')" style="cursor:pointer">
        ${item.product_name}
      </div>
      <div style="font-size:12px;color:var(--text-muted)">${item.brand||''} · ${item.subcategory||item.category}</div>
      <div class="cart-item-price">${formatPrice(item.price)}
        ${item.mrp>item.price?`<span style="color:#16a34a;font-size:12px;font-weight:600;margin-left:6px">${Math.round(item.discount_percent||0)}% off</span>`:''}
      </div>
      <div class="qty-control">
        <button class="qty-btn" onclick="changeQty(${item.cart_item_id},${item.quantity-1})">−</button>
        <span class="qty-num">${item.quantity}</span>
        <button class="qty-btn" onclick="changeQty(${item.cart_item_id},${item.quantity+1})">+</button>
        <span class="cart-remove" onclick="removeCartItem(${item.cart_item_id})">Remove</span>
      </div>
    </div>
    <div style="text-align:right;flex-shrink:0">
      <div style="font-size:16px;font-weight:700">${formatPrice(item.price*item.quantity)}</div>
      ${item.mrp>item.price?`<div style="font-size:12px;color:#16a34a">Save ${formatPrice((item.mrp-item.price)*item.quantity)}</div>`:''}
    </div>
  </div>`;
}

async function changeQty(cartItemId,qty) {
  if (qty<1) { removeCartItem(cartItemId); return; }
  try { await API.updateCart(cartItemId,{quantity:qty}); await Store.loadCart(); renderCart(); updateBadges(); }
  catch(e) { showToast(e.message,'error'); }
}
async function removeCartItem(cartItemId) {
  try { await Store.removeFromCart(cartItemId); renderCart(); updateBadges(); showToast('Item removed','info'); }
  catch(e) { showToast(e.message,'error'); }
}
async function doCheckout() {
  const btn=document.querySelector('[onclick="doCheckout()"]');
  if(btn){btn.disabled=true;btn.innerHTML='<i class="fas fa-spinner fa-spin"></i> Processing…';}
  try {
    const data=await API.checkout();
    showToast(`Order #${data.order_id} placed! ${formatPrice(data.total)}`,'success');
    await Store.loadCart(); updateBadges();
    openModal(`<div style="text-align:center;padding:20px">
      <div style="font-size:56px;margin-bottom:16px">🎉</div>
      <div style="font-size:22px;font-weight:800;margin-bottom:8px">Order Placed Successfully!</div>
      <div style="color:var(--text-muted);margin-bottom:6px">Order ID: <strong>#${data.order_id}</strong></div>
      <div style="font-size:20px;font-weight:700;color:var(--primary);margin-bottom:20px">${formatPrice(data.total)}</div>
      <button class="btn btn-primary btn-lg" onclick="closeModal();navigate('home')">Continue Shopping</button>
    </div>`);
  } catch(e) {
    showToast(e.message,'error');
    if(btn){btn.disabled=false;btn.innerHTML='<i class="fas fa-shield-alt"></i> Secure Checkout';}
  }
}

// ════════════════════════════════════════════════════════════
// WISHLIST
// ════════════════════════════════════════════════════════════
async function renderWishlist() {
  const root=document.getElementById('appRoot');
  const user=Store.get('user');
  if (!user) {
    root.innerHTML=`<div class="page"><div class="empty-state">
      <div class="empty-icon">💝</div><div class="empty-title">Login to view your wishlist</div>
      <button class="btn btn-primary" onclick="navigate('login')">Login</button>
    </div></div>`; return;
  }
  root.innerHTML=`<div class="page">${spinnerHTML()}</div>`;
  await Store.loadWishlist();
  const wishlist=Store.get('wishlist');
  if (!wishlist.length) {
    root.innerHTML=`<div class="page"><div class="empty-state">
      <div class="empty-icon">💝</div><div class="empty-title">Your wishlist is empty</div>
      <div class="empty-sub">Save items you love and come back later</div>
      <button class="btn btn-primary btn-lg" onclick="navigate('shop')"><i class="fas fa-heart"></i> Browse Products</button>
    </div></div>`; return;
  }
  root.innerHTML=`<div class="page">
    <div style="font-size:22px;font-weight:800;margin-bottom:20px">
      <i class="fas fa-heart" style="color:#ef4444"></i> My Wishlist
      <span style="font-size:14px;font-weight:400;color:var(--text-muted);margin-left:8px">(${wishlist.length} items)</span>
    </div>
    <div class="product-grid large">${wishlist.map(p=>productCardHTML(p)).join('')}</div>
  </div>`;
}

// ════════════════════════════════════════════════════════════
// SEARCH RESULTS
// ════════════════════════════════════════════════════════════
async function renderSearch(query) {
  const root=document.getElementById('appRoot');
  root.innerHTML=`<div class="page">
    <div style="font-size:18px;font-weight:700;margin-bottom:16px">
      <i class="fas fa-search" style="color:var(--primary)"></i>
      Results for "<span style="color:var(--primary)">${query}</span>"
      <span class="ai-badge" style="margin-left:8px"><i class="fas fa-brain"></i> AI Ranked</span>
    </div>
    <div id="searchResults">${skeletonCards(12)}</div>
  </div>`;
  try {
    const data=await API.search(query,40);
    const el=document.getElementById('searchResults');
    if (!el) return;
    if (!data.results.length) {
      el.innerHTML=`<div class="empty-state">
        <div class="empty-icon">🔍</div>
        <div class="empty-title">No results for "${query}"</div>
        <div class="empty-sub">Try different keywords or browse categories</div>
        <button class="btn btn-primary" onclick="navigate('shop')">Browse All Products</button>
      </div>`; return;
    }
    el.innerHTML=`<div style="font-size:13px;color:var(--text-muted);margin-bottom:12px">
        ${data.results.length} results found</div>
      <div class="product-grid large">${data.results.map(p=>productCardHTML(p)).join('')}</div>`;
  } catch(e) {
    const el=document.getElementById('searchResults');
    if(el) el.innerHTML=`<div class="empty-state"><div class="empty-title">Search error</div><div class="empty-sub">${e.message}</div></div>`;
  }
}

// ════════════════════════════════════════════════════════════
// AUTH PAGE
// ════════════════════════════════════════════════════════════
function renderAuth() {
  const root=document.getElementById('appRoot');
  root.innerHTML=`
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-left">
        <h2>🛍️ SmartCart AI</h2>
        <p>Your personalised AI-powered shopping destination.</p>
        <div class="auth-perks">
          <div class="auth-perk"><i class="fas fa-brain"></i> AI-Powered Recommendations</div>
          <div class="auth-perk"><i class="fas fa-shield-alt"></i> Secure & Fast Checkout</div>
          <div class="auth-perk"><i class="fas fa-truck"></i> Free Delivery on ₹499+</div>
          <div class="auth-perk"><i class="fas fa-undo"></i> 30-Day Easy Returns</div>
          <div class="auth-perk"><i class="fas fa-heart"></i> Wishlist & Cart Sync</div>
        </div>
      </div>
      <div class="auth-right">
        <div class="auth-tabs">
          <div class="auth-tab active" id="loginTab" onclick="switchAuthTab('login')">Login</div>
          <div class="auth-tab" id="registerTab" onclick="switchAuthTab('register')">Register</div>
        </div>
        <div id="loginForm">
          <div class="form-group">
            <label class="form-label">Username or Email</label>
            <input class="form-input" type="text" id="loginUser" placeholder="Enter username or email"/>
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input class="form-input" type="password" id="loginPass" placeholder="Enter password"
              onkeydown="if(event.key==='Enter')doLogin()"/>
          </div>
          <button class="btn btn-primary btn-lg btn-block" onclick="doLogin()" id="loginBtn">
            <i class="fas fa-sign-in-alt"></i> Login
          </button>
          <div class="test-accounts">
            <div class="test-title">🧪 Test Accounts (click to fill)</div>
            ${[['admin','Admin@123','Admin (Dashboard)'],['alice','Alice@123','Alice'],
               ['bob','Bob@123','Bob'],['demo','Demo@123','Demo']]
              .map(([u,p,l])=>`<div class="test-user" onclick="fillLogin('${u}','${p}')">
                👤 <strong>${l}</strong>: ${u} / ${p}</div>`).join('')}
          </div>
        </div>
        <div id="registerForm" class="hidden">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div class="form-group">
              <label class="form-label">Username</label>
              <input class="form-input" type="text" id="regUser" placeholder="Choose username"/>
            </div>
            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input class="form-input" type="text" id="regName" placeholder="Your full name"/>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input class="form-input" type="email" id="regEmail" placeholder="your@email.com"/>
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input class="form-input" type="password" id="regPass" placeholder="Min 6 characters"
              onkeydown="if(event.key==='Enter')doRegister()"/>
          </div>
          <div class="form-group">
            <label class="form-label">City</label>
            <input class="form-input" type="text" id="regCity" placeholder="Your city"/>
          </div>
          <button class="btn btn-accent btn-lg btn-block" onclick="doRegister()" id="regBtn">
            <i class="fas fa-user-plus"></i> Create Account
          </button>
        </div>
      </div>
    </div>
  </div>`;
}

function switchAuthTab(tab) {
  document.getElementById('loginTab').classList.toggle('active',tab==='login');
  document.getElementById('registerTab').classList.toggle('active',tab==='register');
  document.getElementById('loginForm').classList.toggle('hidden',tab!=='login');
  document.getElementById('registerForm').classList.toggle('hidden',tab!=='register');
}
function fillLogin(user,pass) {
  document.getElementById('loginUser').value=user;
  document.getElementById('loginPass').value=pass;
}
async function doLogin() {
  const username=document.getElementById('loginUser')?.value?.trim();
  const password=document.getElementById('loginPass')?.value;
  if (!username||!password){showToast('Please fill in all fields','error');return;}
  const btn=document.getElementById('loginBtn');
  btn.disabled=true;btn.innerHTML='<i class="fas fa-spinner fa-spin"></i> Logging in…';
  try {
    const data=await API.login({username,password});
    Store.set('user',data.user);
    await Store.loadCart(); await Store.loadWishlist(); updateBadges();
    showToast(`Welcome back, ${data.user.full_name||data.user.username}! 👋`,'success');
    navigate('home');
  } catch(e) {
    showToast(e.message,'error');
    btn.disabled=false;btn.innerHTML='<i class="fas fa-sign-in-alt"></i> Login';
  }
}
async function doRegister() {
  const username =document.getElementById('regUser')?.value?.trim();
  const email    =document.getElementById('regEmail')?.value?.trim();
  const password =document.getElementById('regPass')?.value;
  const full_name=document.getElementById('regName')?.value?.trim();
  const city     =document.getElementById('regCity')?.value?.trim();
  if (!username||!email||!password){showToast('Please fill in all required fields','error');return;}
  if (password.length<6){showToast('Password must be at least 6 characters','error');return;}
  const btn=document.getElementById('regBtn');
  btn.disabled=true;btn.innerHTML='<i class="fas fa-spinner fa-spin"></i> Creating account…';
  try {
    const data=await API.register({username,email,password,full_name,city});
    Store.set('user',data.user); updateBadges();
    showToast(`Welcome to SmartCart AI, ${data.user.username}! 🎉`,'success');
    navigate('home');
  } catch(e) {
    showToast(e.message,'error');
    btn.disabled=false;btn.innerHTML='<i class="fas fa-user-plus"></i> Create Account';
  }
}
