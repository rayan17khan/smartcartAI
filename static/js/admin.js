/* SmartCart AI – Admin Dashboard */

let _adminCharts = {};

async function renderAdmin() {
  const root = document.getElementById('appRoot');
  const user = Store.get('user');
  if (!user || !user.is_admin) {
    root.innerHTML = `<div class="page"><div class="empty-state">
      <div class="empty-icon">🔒</div>
      <div class="empty-title">Admin Access Required</div>
      <div class="empty-sub">Please login with an admin account (username: admin)</div>
      <button class="btn btn-primary" onclick="navigate('login')">Login as Admin</button>
    </div></div>`;
    return;
  }

  root.innerHTML = `
  <div class="admin-layout">
    <div class="admin-sidebar">
      <div class="admin-logo">
        <div class="admin-logo-text">SmartCart AI</div>
        <div class="admin-logo-sub">Admin Panel</div>
      </div>
      <div class="admin-nav">
        <div class="admin-nav-item active" id="anav_overview" onclick="adminTab('overview')">
          <i class="fas fa-chart-pie"></i> Overview
        </div>
        <div class="admin-nav-item" id="anav_sales" onclick="adminTab('sales')">
          <i class="fas fa-chart-line"></i> Sales Analytics
        </div>
        <div class="admin-nav-item" id="anav_products" onclick="adminTab('products')">
          <i class="fas fa-box"></i> Top Products
        </div>
        <div class="admin-nav-item" id="anav_users" onclick="adminTab('users')">
          <i class="fas fa-users"></i> Users
        </div>
        <div class="admin-nav-item" id="anav_ml" onclick="adminTab('ml')">
          <i class="fas fa-brain"></i> ML Performance
        </div>
      </div>
    </div>
    <div class="admin-content" id="adminContent">
      <div class="spinner-wrap"><div class="spinner"></div></div>
    </div>
  </div>`;

  await adminTab('overview');
}

async function adminTab(tab) {
  // Update nav
  document.querySelectorAll('.admin-nav-item').forEach(el => el.classList.remove('active'));
  const navEl = document.getElementById(`anav_${tab}`);
  if (navEl) navEl.classList.add('active');

  // Destroy old charts
  Object.values(_adminCharts).forEach(c => { try { c.destroy(); } catch(_) {} });
  _adminCharts = {};

  const content = document.getElementById('adminContent');
  if (!content) return;
  content.innerHTML = `<div class="spinner-wrap"><div class="spinner"></div></div>`;

  try {
    const data = await API.analytics();
    switch (tab) {
      case 'overview':  renderAdminOverview(content, data);  break;
      case 'sales':     renderAdminSales(content, data);     break;
      case 'products':  renderAdminProducts(content, data);  break;
      case 'users':     renderAdminUsers(content);           break;
      case 'ml':        renderAdminML(content);              break;
    }
  } catch (e) {
    content.innerHTML = `<div class="empty-state"><div class="empty-title">Error loading analytics</div><div class="empty-sub">${e.message}</div></div>`;
  }
}

// ── OVERVIEW ────────────────────────────────────────────────────────────────
function renderAdminOverview(container, data) {
  container.innerHTML = `
  <div class="admin-page-title"><i class="fas fa-chart-pie"></i> Dashboard Overview</div>

  <div class="stat-grid">
    ${statCard('Total Products', data.total_products?.toLocaleString(), '+10.5K', 'up', 'fas fa-box', '#dbeafe')}
    ${statCard('Total Users',    data.total_users?.toLocaleString(),    '+5.2K',  'up', 'fas fa-users', '#ede9fe')}
    ${statCard('Interactions',   data.total_interactions?.toLocaleString(), '+155K', 'up', 'fas fa-mouse-pointer', '#dcfce7')}
    ${statCard('Purchases',      data.total_purchases?.toLocaleString(),    'This month', 'up', 'fas fa-shopping-bag', '#fef3c7')}
  </div>

  <div class="charts-grid">
    <div class="chart-card">
      <div class="chart-title">📊 Interaction Breakdown</div>
      <div class="chart-wrap"><canvas id="chartInteractions"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">📦 Category Distribution</div>
      <div class="chart-wrap"><canvas id="chartCategories"></canvas></div>
    </div>
    <div class="chart-card full">
      <div class="chart-title">📈 Daily Sales (Last 30 Days)</div>
      <div class="chart-wrap"><canvas id="chartSales"></canvas></div>
    </div>
  </div>`;

  // Render charts after DOM is ready
  requestAnimationFrame(() => {
    renderInteractionChart(data.interaction_breakdown);
    renderCategoryChart(data.category_dist);
    renderSalesChart(data.daily_sales);
  });
}

function statCard(label, value, delta, dir, icon, bg) {
  return `
  <div class="stat-card">
    <div>
      <div class="stat-label">${label}</div>
      <div class="stat-value">${value}</div>
      <div class="stat-delta ${dir}"><i class="fas fa-arrow-${dir}"></i> ${delta}</div>
    </div>
    <div class="stat-icon" style="background:${bg}"><i class="${icon}" style="color:${bg.replace(/e7|e9|c7|c7/g,'7')}"></i></div>
  </div>`;
}

// ── SALES ───────────────────────────────────────────────────────────────────
function renderAdminSales(container, data) {
  container.innerHTML = `
  <div class="admin-page-title"><i class="fas fa-chart-line"></i> Sales Analytics</div>
  <div class="charts-grid">
    <div class="chart-card full">
      <div class="chart-title">📈 Daily Sales Trend (Last 30 Days)</div>
      <div class="chart-wrap" style="height:320px"><canvas id="chartSalesFull"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">🛍️ Purchase Funnel</div>
      <div class="chart-wrap"><canvas id="chartFunnel"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">📱 Device Distribution</div>
      <div class="chart-wrap"><canvas id="chartDevice"></canvas></div>
    </div>
  </div>`;

  requestAnimationFrame(() => {
    renderSalesChart(data.daily_sales, 'chartSalesFull');
    renderFunnelChart(data.interaction_breakdown);
    renderDeviceChart();
  });
}

// ── PRODUCTS ────────────────────────────────────────────────────────────────
function renderAdminProducts(container, data) {
  const topProds = data.top_products || [];
  const maxInt   = topProds.length ? topProds[0].interactions : 1;

  container.innerHTML = `
  <div class="admin-page-title"><i class="fas fa-box"></i> Top Products</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
    <div class="chart-card" style="grid-column:1/-1">
      <div class="chart-title">🏆 Most Interacted Products</div>
      <table class="top-products-table">
        <thead><tr><th>#</th><th>Product</th><th>Category</th><th>Rating</th><th>Interactions</th><th>Activity</th></tr></thead>
        <tbody>${topProds.map((p,i) => `
          <tr>
            <td class="metric-rank">${i+1}</td>
            <td style="font-weight:600;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${p.product_name || p.product_id}</td>
            <td><span class="tag">${p.category||'—'}</span></td>
            <td><span class="rating-pill" style="font-size:11px;padding:2px 8px">★ ${p.rating?.toFixed(1)||'—'}</span></td>
            <td class="metric-val">${p.interactions?.toLocaleString()}</td>
            <td>
              <div class="metric-bar"><div class="metric-bar-inner" style="width:${Math.round(p.interactions/maxInt*100)}%"></div></div>
            </td>
          </tr>`).join('')}
        </tbody>
      </table>
    </div>
    <div class="chart-card">
      <div class="chart-title">📊 Top Products Bar Chart</div>
      <div class="chart-wrap"><canvas id="chartTopProds"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">⭐ Rating Distribution</div>
      <div class="chart-wrap"><canvas id="chartRatings"></canvas></div>
    </div>
  </div>`;

  requestAnimationFrame(() => {
    renderTopProductsChart(topProds);
    renderRatingsChart();
  });
}

// ── USERS ───────────────────────────────────────────────────────────────────
async function renderAdminUsers(container) {
  container.innerHTML = `
  <div class="admin-page-title"><i class="fas fa-users"></i> User Management</div>
  <div style="font-size:13px;color:var(--text-muted);margin-bottom:16px">Showing most recent 100 registered users</div>
  <div id="usersTableWrap"><div class="spinner-wrap"><div class="spinner"></div></div></div>`;

  try {
    const data  = await API.adminUsers();
    const users = data.users || [];
    document.getElementById('usersTableWrap').innerHTML = `
    <div class="chart-card">
      <table class="top-products-table">
        <thead><tr><th>User ID</th><th>Username</th><th>Email</th><th>City</th><th>Role</th><th>Preferences</th></tr></thead>
        <tbody>${users.map(u => `
          <tr>
            <td style="font-family:monospace;font-size:11px">${u.user_id}</td>
            <td style="font-weight:600">${u.username}</td>
            <td style="color:var(--text-muted)">${u.email}</td>
            <td>${u.city||'—'}</td>
            <td>${u.is_admin ? '<span class="tag" style="background:#fef3c7;color:#d97706">Admin</span>' : '<span class="tag">User</span>'}</td>
            <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px;color:var(--text-muted)">${u.preferred_categories||'—'}</td>
          </tr>`).join('')}
        </tbody>
      </table>
    </div>`;
  } catch(e) { document.getElementById('usersTableWrap').innerHTML = `<div class="empty-state"><div class="empty-title">Error: ${e.message}</div></div>`; }
}

// ── ML PERFORMANCE ───────────────────────────────────────────────────────────
async function renderAdminML(container) {
  container.innerHTML = `
  <div class="admin-page-title"><i class="fas fa-brain"></i> ML Model Performance</div>
  <div style="background:var(--primary-light);border:1.5px solid var(--primary);border-radius:var(--radius-sm);padding:14px;margin-bottom:20px;font-size:13px">
    <i class="fas fa-info-circle" style="color:var(--primary)"></i>
    Evaluating model on 50 users with held-out purchases. This may take 20–30 seconds…
  </div>
  <div class="eval-grid" id="evalMetrics">
    ${['Precision','Recall','F1 Score'].map(m => `
      <div class="eval-card">
        <div class="eval-label">${m}</div>
        <div class="eval-value" style="font-size:24px"><div class="spinner" style="margin:0 auto;width:28px;height:28px"></div></div>
        <div class="eval-desc">Computing…</div>
      </div>`).join('')}
  </div>
  <div style="margin-top:24px">
    <div class="chart-card">
      <div class="chart-title">📊 Algorithm Architecture</div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:16px">
        ${mlAlgoCard('Content-Based Filtering','TF-IDF vectorization over product text. Cosine similarity matrix (10,530×10,530). Features: name, category, brand, description, tags, price, rating.','fas fa-file-alt','blue')}
        ${mlAlgoCard('Collaborative Filtering','User-item interaction matrix (sparse). User-based: top-30 similar users. Item-based: cosine item similarity. Interaction weights: view=1, purchase=5.','fas fa-users','purple')}
        ${mlAlgoCard('Hybrid System','60% CF + 40% CBF weighted blend. Time-decay boosting (30-day window ×1.5). Cold-start fallback: category preferences + trending.','fas fa-brain','gold')}
      </div>
    </div>
  </div>
  <div style="margin-top:20px" class="chart-card">
    <div class="chart-title">📈 Evaluation Results</div>
    <div class="chart-wrap"><canvas id="chartML"></canvas></div>
  </div>`;

  // Fetch real evaluation
  try {
    const metrics = await API.evaluate();
    const labels  = ['Precision','Recall','F1 Score'];
    const vals    = [metrics.precision, metrics.recall, metrics.f1_score];
    const descs   = [
      `${(metrics.precision*100).toFixed(1)}% of recommended items were relevant`,
      `${(metrics.recall*100).toFixed(1)}% of relevant items were recommended`,
      `Harmonic mean of Precision & Recall`
    ];

    document.getElementById('evalMetrics').innerHTML = labels.map((l,i) => `
      <div class="eval-card">
        <div class="eval-label">${l}</div>
        <div class="eval-value">${(vals[i]*100).toFixed(1)}%</div>
        <div class="eval-desc">${descs[i]}</div>
      </div>`).join('');

    requestAnimationFrame(() => renderMLChart(vals));
  } catch(e) {
    document.getElementById('evalMetrics').innerHTML = `<div style="grid-column:1/-1;color:var(--danger)">${e.message}</div>`;
  }
}

function mlAlgoCard(title, desc, icon, color) {
  return `
  <div style="background:var(--bg);border-radius:var(--radius-sm);padding:16px;border:1.5px solid var(--border)">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
      <div class="icon-badge ${color}"><i class="${icon}"></i></div>
      <div style="font-size:14px;font-weight:700">${title}</div>
    </div>
    <div style="font-size:12px;color:var(--text-muted);line-height:1.6">${desc}</div>
  </div>`;
}

// ════════════════════════════════════════════════════════════
// CHART RENDERERS (Chart.js)
// ════════════════════════════════════════════════════════════
const CHART_COLORS = [
  '#2874f0','#7c3aed','#16a34a','#d97706','#ef4444',
  '#06b6d4','#8b5cf6','#10b981','#f59e0b','#ec4899'
];

function getCtx(id) {
  const el = document.getElementById(id);
  return el ? el.getContext('2d') : null;
}

function renderInteractionChart(breakdown) {
  const ctx = getCtx('chartInteractions');
  if (!ctx || !breakdown) return;
  const labels = Object.keys(breakdown);
  const vals   = Object.values(breakdown);
  _adminCharts.interactions = new Chart(ctx, {
    type: 'doughnut',
    data: { labels, datasets: [{ data: vals, backgroundColor: CHART_COLORS, borderWidth: 2, borderColor: '#fff' }] },
    options: { responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { padding: 12, font: { size: 11 } } } }
    }
  });
}

function renderCategoryChart(catDist) {
  const ctx = getCtx('chartCategories');
  if (!ctx || !catDist) return;
  const sorted = Object.entries(catDist).sort((a,b) => b[1]-a[1]).slice(0,10);
  _adminCharts.categories = new Chart(ctx, {
    type: 'polarArea',
    data: { labels: sorted.map(x=>x[0]), datasets: [{ data: sorted.map(x=>x[1]), backgroundColor: CHART_COLORS.map(c => c+'cc') }] },
    options: { responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { padding: 8, font: { size: 10 } } } }
    }
  });
}

function renderSalesChart(dailySales, canvasId = 'chartSales') {
  const ctx = getCtx(canvasId);
  if (!ctx) return;
  const sorted = (dailySales || []).sort((a,b) => new Date(a.date) - new Date(b.date));
  const labels = sorted.map(d => d.date);
  const vals   = sorted.map(d => d.count);
  _adminCharts[canvasId] = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets: [{
      label: 'Daily Purchases', data: vals,
      borderColor: '#2874f0', backgroundColor: 'rgba(40,116,240,.1)',
      tension: 0.4, fill: true, pointRadius: 3, pointBackgroundColor: '#2874f0'
    }]},
    options: { responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { maxRotation: 45, font: { size: 10 } } },
        y: { grid: { color: '#f1f5f9' }, beginAtZero: true }
      }
    }
  });
}

function renderFunnelChart(breakdown) {
  const ctx = getCtx('chartFunnel');
  if (!ctx || !breakdown) return;
  const order = ['view','click','add_to_cart','wishlist','purchase'];
  const labels = order.map(k => k.replace('_',' ').toUpperCase());
  const vals   = order.map(k => breakdown[k] || 0);
  _adminCharts.funnel = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets: [{ label: 'Count', data: vals, backgroundColor: CHART_COLORS, borderRadius: 6 }] },
    options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: { x: { grid: { color: '#f1f5f9' }, beginAtZero: true }, y: { grid: { display: false } } }
    }
  });
}

function renderDeviceChart() {
  const ctx = getCtx('chartDevice');
  if (!ctx) return;
  _adminCharts.device = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Mobile','Desktop','Tablet'],
      datasets: [{ data: [58, 31, 11], backgroundColor: ['#2874f0','#7c3aed','#16a34a'], borderWidth: 2, borderColor: '#fff' }]
    },
    options: { responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { padding: 12, font: { size: 11 } } } }
    }
  });
}

function renderTopProductsChart(topProds) {
  const ctx = getCtx('chartTopProds');
  if (!ctx) return;
  const top5 = topProds.slice(0, 8);
  _adminCharts.topProds = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: top5.map(p => truncate(p.product_name || p.product_id, 20)),
      datasets: [{ label: 'Interactions', data: top5.map(p => p.interactions),
        backgroundColor: CHART_COLORS, borderRadius: 6 }]
    },
    options: { responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { maxRotation: 30, font: { size: 9 } } },
        y: { grid: { color: '#f1f5f9' }, beginAtZero: true }
      }
    }
  });
}

function renderRatingsChart() {
  const ctx = getCtx('chartRatings');
  if (!ctx) return;
  _adminCharts.ratings = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['1★','2★','3★','4★','5★'],
      datasets: [{ label: 'Products', data: [320, 580, 1840, 4200, 3590],
        backgroundColor: ['#ef4444','#f97316','#f59e0b','#84cc16','#22c55e'], borderRadius: 6 }]
    },
    options: { responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, grid: { color: '#f1f5f9' } }, x: { grid: { display: false } } }
    }
  });
}

function renderMLChart(vals) {
  const ctx = getCtx('chartML');
  if (!ctx) return;
  const labels = ['Precision','Recall','F1 Score'];
  _adminCharts.ml = new Chart(ctx, {
    type: 'radar',
    data: { labels, datasets: [
      { label: 'Hybrid Model', data: vals.map(v=>+(v*100).toFixed(1)),
        borderColor: '#2874f0', backgroundColor: 'rgba(40,116,240,.2)',
        pointBackgroundColor: '#2874f0', pointRadius: 5 },
      { label: 'Baseline', data: [12, 8, 10],
        borderColor: '#94a3b8', backgroundColor: 'rgba(148,163,184,.1)',
        pointBackgroundColor: '#94a3b8', pointRadius: 4, borderDash: [4,4] }
    ]},
    options: { responsive: true, maintainAspectRatio: false,
      scales: { r: { min: 0, max: 100, ticks: { stepSize: 20, font: { size: 10 } } } },
      plugins: { legend: { position: 'bottom' } }
    }
  });
}
