function createApiModule({ baseUrl, getData, getDefaultData, renderers }) {
  const apiOrigin = baseUrl.replace(/\/api\/?$/, "");
  function readResponseBody(text) {
    if (!text) return {};
    try {
      return JSON.parse(text);
    } catch {
      return { __nonJson: true, error: text.replace(/\s+/g, " ").trim().slice(0, 240) };
    }
  }
  function reportFailure(endpoint, status, message) {
    const unavailable = status === 0 || status === 404 || status >= 500;
    const detail = { endpoint, httpStatus: status, error: message, unavailable };
    console.warn(`[Bhadawar API] ${endpoint}: ${status ? `HTTP ${status}` : "network error"} — ${message}`);
    if (unavailable && typeof window !== "undefined" && typeof CustomEvent !== "undefined") {
      window.dispatchEvent(new CustomEvent("bhadawar:api-error", { detail }));
    }
    return { success: false, ...detail };
  }
  async function request(endpoint, options) {
    let response;
    try {
      response = await fetch(`${baseUrl}/${endpoint}`, options);
    } catch {
      return reportFailure(endpoint, 0, "Could not reach the backend.");
    }
    const body = readResponseBody(await response.text());
    if (!response.ok) {
      const message = body?.error || body?.message || `Request failed (${response.status} ${response.statusText || "HTTP error"}).`;
      return reportFailure(endpoint, response.status, String(message));
    }
    if (body?.__nonJson) {
      return reportFailure(endpoint, response.status, "The API route returned a non-JSON response.");
    }
    if (body?.error && body?.success === false) {
      return { ...body, httpStatus: response.status };
    }
    return { ...body, httpStatus: response.status };
  }
  const API = {
    async get(endpoint) {
      return request(endpoint, { credentials: "same-origin" });
    },
    async post(endpoint, payload) {
      return request(endpoint, {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    },
    async postForm(endpoint, payload) {
      return request(endpoint, { method: "POST", body: payload, credentials: "same-origin" });
    }
  };
  function mediaUrl(path) {
    if (!path || /^(https?:|blob:|data:)/i.test(path)) return path;
    const clean = path.replace(/^\/+/, "");
    return clean.startsWith("uploads/") ? `${apiOrigin}/${clean}` : path;
  }
  async function syncFromBackend() {
    const data = getData();
    if (document.body.dataset.page === "team") {
      const ordersResponse = await API.get("orders");
      if (ordersResponse?.success) data.orders = ordersResponse.orders || [];
    }
    const storiesResponse = await API.get("food-stories");
    if (storiesResponse?.success && storiesResponse.stories) {
      const approvedStories = storiesResponse.stories.map((story) => ({
        ...story,
        date: story.created_at || story.date,
        photo: story.photo ? mediaUrl(story.photo) : "",
        mediaType: story.media_type || story.mediaType || "image",
        orderAbove599: Boolean(story.bonus_rewarded),
        orderId: story.order_id || story.orderId || "",
        pts: Number(story.pts || 1),
        dishId: story.dish_id
      }));
      if (document.body.dataset.page === "team") {
        const pendingResponse = await API.get("food-stories?status=pending");
        const pendingStories = (pendingResponse?.stories || []).map((story) => ({
          ...story,
          date: story.created_at || story.date,
          photo: story.photo ? mediaUrl(story.photo) : "",
          mediaType: story.media_type || "image",
          orderId: story.order_id || "",
          orderAbove599: Boolean(story.bonus_rewarded),
          pts: Number(story.pts || 1),
          dishId: story.dish_id
        }));
        data.foodStories = [...pendingStories, ...approvedStories];
      } else {
        data.foodStories = approvedStories.length ? approvedStories : structuredClone(getDefaultData().foodStories);
      }
      renderers.renderStoryBar();
      renderers.renderFoodStories();
    }
    const leaderboardResponse = await API.get("leaderboard");
    if (leaderboardResponse?.success) {
      data.leaderboard = {
        alltime: leaderboardResponse.alltime || [],
        monthly: leaderboardResponse.monthly || []
      };
      renderers.renderLeaderboard("monthly");
      renderers.renderMiniLeaderboard("monthly");
    }
    if (data.customerProfile?.phone) {
      const walletResponse = await API.get(`wallet?phone=${encodeURIComponent(data.customerProfile.phone)}`);
      if (walletResponse?.success) {
        data.wallet.balance = walletResponse.balance;
        if (walletResponse.transactions?.length) data.wallet.entries = walletResponse.transactions;
        renderers.updateCartCounters();
      }
    }
    if (document.body.dataset.page === "team") renderers.renderTeamPage();
  }
  return { API, mediaUrl, syncFromBackend };
}
function calculateWalletRedemption(total, balance, maxRedeemPercent = 50, enabled = true) {
  const safeTotal = Math.max(0, Number(total) || 0);
  const safeBalance = Math.max(0, Math.floor(Number(balance) || 0));
  const percent = Math.max(0, Math.min(100, Number(maxRedeemPercent) || 0));
  return enabled ? Math.min(safeBalance, Math.floor(safeTotal * percent / 100)) : 0;
}
function createWalletModule(context) {
  const { getData, money, openDialog, closeDialog, openCartDrawer, icon: icon2 } = context;
  function openWalletDialog() {
    const data = getData();
    openDialog(`
      <div class="wallet-dialog-content">
        <div class="wallet-dialog-topline">
          <div class="dialog-kicker">BHADAWAR REWARDS</div>
          <span class="wallet-ready-pill"><span aria-hidden="true"></span> Ready to use</span>
        </div>
        <h2>Your Bhadawar <em>Wallet.</em></h2>
        <p class="wallet-dialog-lede">Good food brings rewards. Earn points on every online delivery and dine-in.</p>
        <div class="wallet-dialog-balance">
          <div class="wallet-dialog-balance-copy">
            <small>AVAILABLE BALANCE</small>
            <div class="wallet-dialog-points"><strong>${Number(data.wallet.balance) || 0}</strong><span>points</span></div>
            <p>Worth <b>${money(data.wallet.balance)}</b> to use on your orders</p>
          </div>
          <div class="wallet-dialog-icon-wrap">${icon2("coin", "wallet-dialog-coin")}</div>
        </div>
        <div class="wallet-dialog-note"><span>₹1 spent</span><b>→</b><span>1 point</span><i></i><span>100 points = ₹100 off</span></div>
        <div class="wallet-dialog-actions">
          <button class="button button-green" id="wallet-use-now">Order Now <span aria-hidden="true">→</span></button>
          <a href="account.html" class="button button-outline">Account details</a>
        </div>
      </div>
    `);
    document.querySelector("#wallet-use-now")?.addEventListener("click", () => {
      closeDialog();
      openCartDrawer();
    });
  }
  return { openWalletDialog };
}
function calculateCart(context, orderType = context.getOrderType()) {
  const { data, config, itemById, distanceFromRestaurantKm } = context;
  const pricedRows = data.cart.map((row) => ({ row, item: itemById(row.id), qty: Number(row.qty) })).filter((entry) => entry.item && Number.isFinite(entry.qty) && entry.qty > 0);
  const subtotal = pricedRows.reduce((sum, { row, item, qty }) => sum + (Number(item.price) || 0) * qty, 0);
  const corporateSubtotal = pricedRows.reduce((sum, { row, item, qty }) => sum + (row.corporate ? (Number(item.price) || 0) * qty : 0), 0);
  const corporateDiscount = corporateSubtotal > 2e4 ? Math.round(corporateSubtotal * 0.15) : corporateSubtotal > 1e4 ? Math.round(corporateSubtotal * 0.1) : 0;
  const tax = Math.round(subtotal * (Number(config.sampleTaxPercent ?? 5) / 100));
  const address = data.deliveryAddress || {};
  const hasCoordinates = address.latitude != null && address.longitude != null && Number.isFinite(Number(address.latitude)) && Number.isFinite(Number(address.longitude));
  const pinnedDistance = hasCoordinates ? distanceFromRestaurantKm(address.latitude, address.longitude) : Number(address.deliveryDistanceKm);
  const deliveryDistanceBand = hasCoordinates && Number.isFinite(pinnedDistance) ? pinnedDistance > 10 ? "over10" : pinnedDistance > 5 ? "5to10" : "under5" : address.deliveryDistanceBand || "under5";
  const phoneKey = String(address.phone || data.wallet?.phone || "").replace(/\D/g, "").slice(-10);
  const firstOrder = !data.orders?.some(
    (order) => String(order.customer_phone || "").replace(/\D/g, "").slice(-10) === phoneKey && order.order_type !== "corporate"
  );
  const delivery = orderType === "delivery" && deliveryDistanceBand !== "over10" ? firstOrder ? 0 : deliveryDistanceBand === "5to10" ? Number(config.sampleLongDeliveryFee ?? 50) : Number(config.sampleDeliveryFee ?? 35) : 0;
  const total = subtotal + tax + delivery - corporateDiscount;
  return { subtotal, corporateSubtotal, corporateDiscount, tax, delivery, deliveryDistanceBand, firstOrder, outsideDeliveryRange: deliveryDistanceBand === "over10", total };
}
function renderCartDrawer(context) {
  const { data, $, itemById, money, escapeHtml, calcCart, getOrderType, icon: icon2 } = context;
  const list = $("#drawer-cart-items");
  if (!list) return;
  const rows = data.cart.map((row) => ({ row, item: itemById(row.id) })).filter((entry) => entry.item && Number.isInteger(Number(entry.row.qty)) && Number(entry.row.qty) > 0);
  if (!rows.length) {
    list.innerHTML = `
      <div class="cart-empty-state">
        ${icon2("bowl", "cart-empty-icon")}
        <strong>Your order is empty</strong>
        <p>Add some fresh Agra favorites from our menu.</p>
      </div>`;
    $("#bill-item-total").textContent = "₹0";
    $("#bill-delivery-fee").textContent = "₹0";
    $("#bill-tax").textContent = "₹0";
    $("#bill-grand-total").textContent = "₹0";
    const proceed2 = $("#drawer-proceed-btn");
    if (proceed2) {
      proceed2.disabled = true;
      proceed2.textContent = "Add dishes to continue";
    }
    return;
  }
  const proceed = $("#drawer-proceed-btn");
  if (proceed) {
    proceed.disabled = false;
    proceed.textContent = "Proceed to checkout →";
  }
  list.innerHTML = rows.map(({ row, item }) => {
    const photoSrc = item.photo?.startsWith("assets/") ? item.photo : "assets/food-paneer.jpg";
    return `
      <div class="drawer-cart-item">
        <div class="drawer-item-thumb"><img src="${escapeHtml(photoSrc)}" alt="${escapeHtml(item.name)}" onerror="this.src='assets/bhadawar-mark.png'"></div>
        <div class="drawer-item-info"><strong class="drawer-item-title">${escapeHtml(item.name)}</strong><span class="drawer-item-price">${money(item.price)}</span></div>
        <div class="quantity-control">
          <button type="button" data-drawer-qty="${escapeHtml(item.id)}" data-step="-1" aria-label="Decrease ${escapeHtml(item.name)}">−</button>
          <span>${Number(row.qty)}</span>
          <button type="button" data-drawer-qty="${escapeHtml(item.id)}" data-step="1" aria-label="Increase ${escapeHtml(item.name)}">+</button>
        </div>
        <button type="button" class="drawer-item-delete-btn" data-drawer-delete="${escapeHtml(item.id)}" aria-label="Remove ${escapeHtml(item.name)}">${icon2("trash")}</button>
      </div>`;
  }).join("");
  const calc = calcCart();
  const usePoints = Boolean($("#cart-use-points")?.checked && data.wallet.balance > 0);
  const pointsDiscount = calculateWalletRedemption(calc.total, data.wallet.balance, data.settings?.maxRedeemPercent ?? 50, usePoints);
  const grandTotal = Math.max(0, calc.total - pointsDiscount);
  $("#bill-item-total").textContent = money(calc.subtotal);
  $("#bill-delivery-fee").textContent = calc.outsideDeliveryRange && getOrderType() === "delivery" ? "Not available beyond 10 km" : calc.delivery ? money(calc.delivery) : "Free";
  $("#bill-tax").textContent = money(calc.tax) + ".00";
  $("#bill-grand-total").textContent = money(grandTotal) + ".00";
  const discountRow = $("#bill-discount-row");
  if (discountRow) {
    discountRow.hidden = !usePoints;
    $("#bill-discount").textContent = `−${money(pointsDiscount)}`;
  }
  const walletBalance = $("#cart-wallet-balance");
  if (walletBalance) walletBalance.textContent = `${data.wallet.balance} points (${money(data.wallet.balance)})`;
}
function addCartItem(context, id) {
  const { data, itemById, save, renderDrawerCart, renderFullMenu, toast } = context;
  const item = itemById(id);
  if (!item) return;
  const row = data.cart.find((entry) => entry.id === id);
  if (row) row.qty = Number(row.qty || 0) + 1;
  else data.cart.push({ id, qty: 1 });
  save();
  renderDrawerCart();
  renderFullMenu();
  toast(`Added to order: ${item.name}`);
}
function changeCartQuantity(context, id, step) {
  const { data, addToCart, save, renderDrawerCart } = context;
  const row = data.cart.find((entry) => entry.id === id);
  if (!row) {
    if (step > 0) addToCart(id);
    return;
  }
  row.qty = Number(row.qty || 0) + step;
  if (row.qty <= 0) data.cart = data.cart.filter((entry) => entry.id !== id);
  save();
  renderDrawerCart();
}
function deleteCartItem(context, id) {
  const { data, save, renderDrawerCart, toast } = context;
  data.cart = data.cart.filter((entry) => entry.id !== id);
  save();
  renderDrawerCart();
  toast("Item removed from order");
}
const paths = {
  location: '<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  coin: '<circle cx="12" cy="12" r="9"/><path d="M15.5 9.5c-.5-.8-1.5-1.2-3-1.2-1.4 0-2.4.7-2.4 1.7 0 2.8 5.8.8 5.8 3.6 0 1.1-1.2 2-3 2-1.4 0-2.6-.5-3.3-1.4M12.4 6.7v10.6"/>',
  cart: '<path d="M3 4h2l2.2 11.2a2 2 0 0 0 2 1.6h8.5a2 2 0 0 0 1.9-1.5L21 8H6"/><circle cx="10" cy="20" r="1"/><circle cx="18" cy="20" r="1"/>',
  delivery: '<path d="M3 7h11v10H3zM14 10h4l3 3v4h-7z"/><circle cx="7" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>',
  bag: '<path d="M5 8h14l1 13H4L5 8Z"/><path d="M9 9V6a3 3 0 0 1 6 0v3"/>',
  dining: '<path d="M4 3v8M7 3v8M4 7h3M5.5 11v10M16 3v18M16 3c3 2 4 5 4 8h-4"/>',
  leaf: '<path d="M20 4c-9 0-15 3-15 10a6 6 0 0 0 6 6c7 0 9-7 9-16Z"/><path d="M5 20c3-5 7-8 12-11"/>',
  card: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18M7 15h4"/>',
  gift: '<path d="M3 10h18v11H3zM2 6h20v4H2zM12 6v15M12 6H8.5a2.5 2.5 0 1 1 2.3-3.5L12 6Zm0 0h3.5a2.5 2.5 0 1 0-2.3-3.5L12 6Z"/>',
  heart: '<path d="M20.8 8.8c0 5-8.8 11-8.8 11s-8.8-6-8.8-11A4.8 4.8 0 0 1 12 6a4.8 4.8 0 0 1 8.8 2.8Z"/>',
  story: '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".7" fill="currentColor" stroke="none"/>',
  book: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22V5.5Z"/><path d="M4 6v16M8 7h8M8 11h8"/>',
  trophy: '<path d="M8 4h8v4a4 4 0 0 1-8 0V4ZM8 6H4v2a4 4 0 0 0 4 4M16 6h4v2a4 4 0 0 1-4 4M12 12v6M8 21h8M9 18h6"/>',
  phone: '<path d="M6 3h12a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"/><path d="M10 18h4"/>',
  chat: '<path d="M20 11.5a7.5 7.5 0 0 1-8 7.5 8 8 0 0 1-3.4-.8L4 20l1.2-4.1A7.3 7.3 0 0 1 4 12C4 7.9 7.6 5 12 5s8 2.9 8 6.5Z"/>',
  home: '<path d="m3 11 9-8 9 8v10H5V11"/><path d="M9 21v-6h6v6"/>',
  work: '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18M10 12v2h4v-2"/>',
  search: '<circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/>',
  trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 14h10l1-14M9 7V4h6v3"/>',
  bowl: '<path d="M4 11h16l-1.5 7a3 3 0 0 1-3 2h-7a3 3 0 0 1-3-2L4 11Z"/><path d="M3 11a9 9 0 0 1 18 0M8 7h.01M12 5h.01M16 7h.01"/>',
  receipt: '<path d="M6 3 8 4l2-1 2 1 2-1 2 1 2-1v18l-2-1-2 1-2-1-2 1-2-1-2 1V3Z"/><path d="M9 8h6M9 12h6M9 16h4"/>',
  tag: '<path d="M20 13 13 20 3 10V4h6l11 9Z"/><circle cx="7.5" cy="7.5" r="1"/>',
  compass: '<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2.2 4.8-4.8 2.2 2.2-4.8 4.8-2.2Z"/>',
  drink: '<path d="M7 3h10l-1 5H8L7 3ZM8 8l1 13h6l1-13M9 12h6"/>',
  share: '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.7 10.6 6.6-4.2M8.7 13.4l6.6 4.2"/>',
  close: '<path d="m6 6 12 12M18 6 6 18"/>',
  check: '<path d="m4 12 5 5L20 6"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  user: '<circle cx="12" cy="8" r="3.5"/><path d="M5 21a7 7 0 0 1 14 0"/>',
  logout: '<path d="M10 17l5-5-5-5M15 12H3M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7"/>',
  arrow: '<path d="M4 12h15M13 6l6 6-6 6"/>',
  pin: '<path d="M12 21s7-6 7-12a7 7 0 0 0-14 0c0 6 7 12 7 12Z"/><circle cx="12" cy="9" r="2"/>',
  soundOff: '<path d="M4 10v4h4l5 4V6l-5 4H4ZM17 9l4 6M21 9l-4 6"/>',
  soundOn: '<path d="M4 10v4h4l5 4V6l-5 4H4ZM17 9a5 5 0 0 1 0 6M19 6a9 9 0 0 1 0 12"/>',
  pause: '<path d="M8 5h3v14H8zM15 5h3v14h-3z"/>',
  play: '<path d="m7 4 13 8-13 8V4Z" fill="currentColor" stroke="none"/>',
  star: '<path d="m12 3 2.8 5.8 6.4.9-4.6 4.5 1.1 6.4-5.7-3-5.7 3 1.1-6.4-4.6-4.5 6.4-.9L12 3Z"/>',
  edit: '<path d="m4 16-.8 4.8L8 20l11-11-4-4L4 16Z"/><path d="m13.5 6.5 4 4"/>',
  restaurant: '<path d="M5 3v8M8 3v8M5 7h3M6.5 11v10M16 3v18M16 3c3 2 4 5 4 8h-4"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>'
};
function icon(name, className = "") {
  const body = paths[name] || paths.star;
  const classes = ["icon-svg", className].filter(Boolean).join(" ");
  return `<svg class="${classes}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${body}</svg>`;
}
function hydrateIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((placeholder) => {
    const name = placeholder.dataset.icon;
    placeholder.innerHTML = icon(name);
  });
}
function createStoriesModule(context) {
  const { data, menu, API, $, $$, money, escapeHtml, toast, save, updateCartCounters, updateOrderModeUI, openDialog, closeDialog, config, mediaUrl, syncFromBackend, loadData } = context;
  let fsViewerIndex = 0;
  let fsViewerTimer = null;
  let fsMuted = true;
  let fsViewerPaused = false;
  const FS_SLIDE_MS = 5e3;
  const dishPhotoMap = {
    "mains-paneer-butter-masala": "assets/dishes/mains-paneer-butter-masala.webp",
    "breads-butter-naan": "assets/dishes/breads-butter-naan.webp",
    "daal-daal-makhni": "assets/dishes/daal-daal-makhni.webp",
    "snacks-paneer-tikka": "assets/dishes/snacks-paneer-tikka.webp",
    "mains-bhadawari-special-paneer": "assets/dishes/mains-bhadawari-special-paneer.webp"
  };
  const fallbackPhotos = [
    "assets/food-paneer.jpg",
    "assets/food-snacks.jpg",
    "assets/food-daal.jpg",
    "assets/food-bread.jpg",
    "assets/food-thali.jpg",
    "assets/food-rice.jpg"
  ];
  function storyPhoto(s, idx) {
    return s.photo ? mediaUrl(s.photo) : dishPhotoMap[s.dishId] || fallbackPhotos[idx % fallbackPhotos.length] || "assets/food-paneer.jpg";
  }
  function starsHtml(n) {
    return "★".repeat(n) + "☆".repeat(5 - n);
  }
  function timeAgo(iso) {
    const d = new Date(iso);
    const diff = Math.floor((Date.now() - d) / 1e3);
    if (diff < 60) return "Just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  }
  function storyPoints(story) {
    return Number(story.pts || 1);
  }
  function initFoodStories() {
    renderStoryBar();
    renderFoodStories();
    renderLeaderboard("monthly");
    renderMiniLeaderboard("monthly");
    initViewerControls();
    initStoriesEvents();
    initAdminStoriesDesk();
  }
  function renderStoryBar() {
    const bar = $("#fs-story-bar");
    if (!bar) return;
    const approved = (data.foodStories || []).filter((s) => s.status === "approved").sort((a, b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at));
    const addBubble = bar.querySelector(".fs-story-add");
    bar.innerHTML = "";
    if (addBubble) bar.appendChild(addBubble);
    approved.forEach((s, i) => {
      const photo = s.mediaType === "video" ? dishPhotoMap[s.dishId] || fallbackPhotos[i % fallbackPhotos.length] : storyPhoto(s, i);
      const bubbleLabel = s.editorial ? s.dish.split(" ").slice(0, 2).join(" ") : s.author.split(" ")[0];
      const bubble = document.createElement("button");
      bubble.type = "button";
      bubble.className = "fs-story-bubble";
      bubble.dataset.storyIdx = i;
      bubble.innerHTML = `
      <div class="fs-bubble-ring fs-bubble-ring--unseen">
        <img class="fs-bubble-img" src="${escapeHtml(photo)}" alt="${escapeHtml(s.author)}"
             onerror="this.src='assets/food-paneer.jpg'">
      </div>
      <span class="fs-bubble-name">${escapeHtml(bubbleLabel)}</span>
    `;
      bubble.addEventListener("click", () => {
        fsViewerIndex = i;
        showViewerStory(approved);
        openViewerOnMobile();
      });
      bar.appendChild(bubble);
    });
  }
  function renderFoodStories() {
    const grid = $("#published-stories-grid");
    if (!grid) return;
    const approved = (data.foodStories || []).filter((s) => s.status === "approved").sort((a, b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at));
    const badge = $("#stories-count-badge");
    if (badge) badge.textContent = approved.length;
    if (!approved.length) {
      grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:60px 20px;color:#9a8760">
        <div class="fs-empty-icon" aria-hidden="true">${icon("bowl")}</div>
        <h3 style="font-size:18px;font-weight:700;color:#3a2a1a;margin:0 0 8px">No stories yet</h3>
        <p style="margin:0 0 20px;font-size:14px">Be the first to share your Bhadawar experience!</p>
        <button class="fs-share-btn btn-share-story" style="display:inline-flex">
          <span class="fs-share-icon" aria-hidden="true">${icon("edit")}</span> Share Your Story <span class="fs-pts-chip">+1 Pt</span>
        </button>
      </div>`;
      return;
    }
    grid.innerHTML = approved.map((s, i) => {
      const photo = storyPhoto(s, i);
      const liked = (data.likedStories || []).includes(s.id);
      const media = s.mediaType === "video" ? `<video class="fs-card-img" src="${escapeHtml(photo)}" poster="${escapeHtml(dishPhotoMap[s.dishId] || fallbackPhotos[i % fallbackPhotos.length])}" muted playsinline preload="metadata"></video><span class="fs-video-chip">▶ Video</span>` : `<img class="fs-card-img" src="${escapeHtml(photo)}" alt="${escapeHtml(s.dish)}" loading="lazy" onerror="this.src='assets/food-paneer.jpg'">`;
      return `
    <article class="fs-story-card" data-story-idx="${i}"
             aria-label="Story by ${escapeHtml(s.author)}">
      <div class="fs-card-img-wrap">
        ${media}
        <div class="fs-card-gradient"></div>
        <div class="fs-card-dish-badge">${icon("bowl")} ${escapeHtml(s.dish)}</div>
        ${s.orderAbove599 ? '<div class="fs-card-verified">✔ Verified Order</div>' : ""}
      </div>
      <div class="fs-card-body">
        <div class="fs-card-author">
          <div class="fs-card-avatar">${s.author[0].toUpperCase()}</div>
          <div>
            <div class="fs-card-name">${escapeHtml(s.author)}</div>
            <div class="fs-card-time">${timeAgo(s.date)}</div>
          </div>
        <div class="fs-card-pts" style="margin-left:auto">${s.editorial ? "Kitchen story" : "+" + storyPoints(s) + "pt" + (storyPoints(s) > 1 ? "s" : "")}</div>
        </div>
        <div class="fs-card-stars">${s.editorial ? "FROM THE BHADAWAR KITCHEN" : starsHtml(s.rating)}</div>
        <p class="fs-card-text">"${escapeHtml(s.text)}"</p>
        <div class="fs-card-actions">
          <button type="button" class="fs-card-action-btn ${liked ? "is-liked" : ""}" data-like-story="${escapeHtml(s.id)}" aria-label="${liked ? "Unlike" : "Like"} ${escapeHtml(s.author)}’s story" aria-pressed="${liked}">${icon("heart")} ${Number(s.likes || 0) + (liked ? 1 : 0)}</button>
          <button type="button" class="fs-card-action-btn" data-share-story="${escapeHtml(s.id)}">${icon("share")} Share</button>
          <button class="fs-card-read-btn" data-viewer-idx="${i}">Read Story</button>
        </div>
      </div>
    </article>`;
    }).join("");
    grid.querySelectorAll("[data-like-story]").forEach((btn) => btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const id = btn.dataset.likeStory;
      data.likedStories = data.likedStories || [];
      const at = data.likedStories.indexOf(id);
      if (at >= 0) data.likedStories.splice(at, 1);
      else data.likedStories.push(id);
      const story = approved.find((item) => item.id === id);
      if (story) {
        story.likes = Math.max(0, Number(story.likes || 0) + (at >= 0 ? -1 : 1));
        if (!story.editorial) await API.post("food-stories/like", { story_id: id, liked: at < 0 });
      }
      save();
      renderFoodStories();
    }));
    grid.querySelectorAll("[data-share-story]").forEach((btn) => btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const story = approved.find((item) => item.id === btn.dataset.shareStory);
      if (!story) return;
      const shareData = { title: `${story.dish} · Bhadawar Food Story`, text: `${story.author}: ${story.text}`, url: `${location.origin}${location.pathname}#food-stories` };
      try {
        if (navigator.share) await navigator.share(shareData);
        else {
          await navigator.clipboard.writeText(shareData.url);
          toast("Story link copied");
        }
      } catch {
      }
    }));
    grid.querySelectorAll("[data-viewer-idx]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        fsViewerIndex = parseInt(btn.dataset.viewerIdx);
        const approved2 = (data.foodStories || []).filter((s) => s.status === "approved").sort((a, b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at));
        showViewerStory(approved2);
        openViewerOnMobile();
      });
    });
    grid.querySelectorAll(".fs-card-img-wrap").forEach((wrap) => wrap.addEventListener("click", () => {
      const index = parseInt(wrap.closest(".fs-story-card").dataset.storyIdx);
      if (!Number.isNaN(index)) {
        fsViewerIndex = index;
        showViewerStory(approved);
        openViewerOnMobile();
      }
    }));
    const allApproved = (data.foodStories || []).filter((s) => s.status === "approved").sort((a, b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at));
    if (allApproved.length) showViewerStory(allApproved);
  }
  function showViewerStory(stories) {
    if (!stories.length) return;
    fsViewerIndex = (fsViewerIndex % stories.length + stories.length) % stories.length;
    clearTimeout(fsViewerTimer);
    const s = stories[fsViewerIndex] || stories[0];
    const photo = storyPhoto(s, fsViewerIndex);
    const img = $("#fs-viewer-img");
    const video = $("#fs-viewer-video");
    const dish = $("#fs-viewer-dish");
    const story = $("#fs-viewer-story");
    const auth = $("#fs-viewer-author");
    const stars = $("#fs-viewer-stars");
    const prog = $("#fs-progress-row");
    if (s.mediaType === "video" && video) {
      if (img) img.hidden = true;
      video.hidden = false;
      video.src = photo;
      video.muted = fsMuted;
      video.currentTime = 0;
      if (!fsViewerPaused) video.play().catch(() => {
      });
    } else if (img) {
      if (video) {
        video.pause();
        video.removeAttribute("src");
        video.load();
        video.hidden = true;
      }
      img.hidden = false;
      img.style.opacity = "0";
      img.src = photo;
      img.onload = () => {
        img.style.opacity = "1";
      };
      img.onerror = () => {
        img.src = "assets/food-paneer.jpg";
        img.style.opacity = "1";
      };
    }
    if (dish) dish.innerHTML = `${icon("bowl")} ${escapeHtml(s.dish)}`;
    if (story) story.textContent = '"' + s.text + '"';
    if (stars) stars.textContent = s.editorial ? "From the Bhadawar kitchen" : starsHtml(s.rating);
    if (auth) auth.innerHTML = `
    <div class="fs-viewer-av">${s.author[0].toUpperCase()}</div>
    <div>
      <div class="fs-viewer-name">${escapeHtml(s.author)}</div>
      <div class="fs-viewer-time">${timeAgo(s.date)}</div>
    </div>
    ${s.orderAbove599 ? '<span style="margin-left:auto;font-size:10px;background:rgba(23,131,69,.85);color:#fff;padding:2px 8px;border-radius:50px">✔ Verified</span>' : ""}
  `;
    if (prog) {
      prog.innerHTML = stories.map((_, i) => `
      <div class="fs-progress-seg ${i < fsViewerIndex ? "done" : i === fsViewerIndex ? "active" : ""}">
        ${i === fsViewerIndex ? `<div class="fs-progress-fill ${fsViewerPaused ? "paused" : ""}"></div>` : ""}
      </div>`).join("");
    }
    const muteButton = $("#fs-mute-btn");
    if (muteButton) {
      muteButton.innerHTML = icon(fsMuted ? "soundOff" : "soundOn");
      muteButton.setAttribute("aria-label", fsMuted ? "Unmute story" : "Mute story");
    }
    const pauseButton = $("#fs-pause-btn");
    if (pauseButton) {
      pauseButton.innerHTML = icon(fsViewerPaused ? "play" : "pause");
      pauseButton.setAttribute("aria-label", fsViewerPaused ? "Play story" : "Pause story");
    }
    $$("[data-story-idx]").forEach((b) => b.querySelector(".fs-bubble-ring")?.classList.remove("fs-bubble-ring--active"));
    const activeBubble = $(`[data-story-idx="${fsViewerIndex}"]`);
    activeBubble?.querySelector(".fs-bubble-ring")?.classList.add("fs-bubble-ring--active");
    if (!fsViewerPaused) fsViewerTimer = setTimeout(() => {
      fsViewerIndex = (fsViewerIndex + 1) % stories.length;
      showViewerStory(stories);
    }, FS_SLIDE_MS);
  }
  function initViewerControls() {
    const stories = () => (data.foodStories || []).filter((s) => s.status === "approved").sort((a, b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at));
    $("#fs-viewer-prev")?.addEventListener("click", () => {
      const s = stories();
      if (!s.length) return;
      fsViewerPaused = false;
      fsViewerIndex = (fsViewerIndex - 1 + s.length) % s.length;
      showViewerStory(s);
    });
    $("#fs-viewer-next")?.addEventListener("click", () => {
      const s = stories();
      if (!s.length) return;
      fsViewerPaused = false;
      fsViewerIndex = (fsViewerIndex + 1) % s.length;
      showViewerStory(s);
    });
    $("#fs-viewer-close")?.addEventListener("click", () => {
      clearTimeout(fsViewerTimer);
      $("#fs-viewer-video")?.pause();
      const col = $("#fs-viewer-col");
      if (col) col.style.display = "none";
    });
    $("#fs-mute-btn")?.addEventListener("click", () => {
      fsMuted = !fsMuted;
      const btn = $("#fs-mute-btn");
      if (btn) btn.innerHTML = icon(fsMuted ? "soundOff" : "soundOn");
      const video = $("#fs-viewer-video");
      if (video) video.muted = fsMuted;
      btn?.setAttribute("aria-label", fsMuted ? "Unmute story" : "Mute story");
    });
    $("#fs-pause-btn")?.addEventListener("click", () => {
      fsViewerPaused = !fsViewerPaused;
      const video = $("#fs-viewer-video");
      if (fsViewerPaused) {
        clearTimeout(fsViewerTimer);
        video?.pause();
        $(".fs-progress-fill")?.classList.add("paused");
      } else {
        video?.play().catch(() => {
        });
        showViewerStory(stories());
        return;
      }
      const btn = $("#fs-pause-btn");
      if (btn) {
        btn.innerHTML = icon(fsViewerPaused ? "play" : "pause");
        btn.setAttribute("aria-label", fsViewerPaused ? "Play story" : "Pause story");
      }
    });
    $("#fs-viewer-read-btn")?.addEventListener("click", () => {
      const s = stories();
      if (!s.length) return;
      const story = s[fsViewerIndex];
      openDialog(`
      <div class="dialog-kicker">BHADAWAR FOOD STORY</div>
      <h2>${escapeHtml(story.author)}'s <em>Review</em></h2>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
        <span style="color:#f4b400;font-size:16px">${starsHtml(story.rating)}</span>
        <span style="font-size:12px;color:#888">${timeAgo(story.date)}</span>
      </div>
      <div style="background:#fdf7f0;border-radius:10px;padding:14px;font-size:14px;line-height:1.65;color:#3a2010;border-left:3px solid #56180f;margin-bottom:12px">
        "${escapeHtml(story.text)}"
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <span style="background:#fdf6e7;border:1px solid #f0d88a;color:#7a5200;font-size:11px;font-weight:700;padding:3px 10px;border-radius:50px">${icon("bowl")} ${escapeHtml(story.dish)}</span>
        <span style="background:#e6f9ef;border:1px solid #b2e5c8;color:#178345;font-size:11px;font-weight:700;padding:3px 10px;border-radius:50px">+${story.pts} Point${story.pts > 1 ? "s" : ""} Earned</span>
        ${story.orderAbove599 ? '<span style="background:#e8f4ff;border:1px solid #b3d8f5;color:#0a6fa0;font-size:11px;font-weight:700;padding:3px 10px;border-radius:50px">✔ Verified Order</span>' : ""}
      </div>
    `);
    });
  }
  function openViewerOnMobile() {
    const col = $("#fs-viewer-col");
    if (col) {
      col.style.display = "";
      col.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }
  function renderLeaderboard(period) {
    const podium = $("#podium-cards-grid");
    const tbody = $("#leaderboard-table-body");
    const list = (data.leaderboard || {})[period] || [];
    if (podium) {
      const top3 = list.slice(0, 3);
      const order = top3.length >= 3 ? [top3[1], top3[0], top3[2]] : top3;
      const cls = ["silver", "gold", "bronze"];
      const medals = [icon("trophy") + " 2nd", icon("trophy") + " 1st", icon("trophy") + " 3rd"];
      podium.innerHTML = order.map((p, i) => `
      <div class="fs-podium-card ${cls[i]}">
        <div class="fs-podium-medal">${medals[i]}</div>
        <div class="fs-podium-av">${p.avatar}</div>
        <div class="fs-podium-name">${escapeHtml(p.name)}</div>
        <div class="fs-podium-stats">${p.blogs} stories · ${p.points} pts</div>
      </div>`).join("");
    }
    if (tbody) {
      tbody.innerHTML = list.map((p) => `
      <tr>
        <td class="fs-lb-rank">${p.badge || "#" + p.rank}</td>
        <td>
          <span class="fs-lb-av">${p.avatar}</span>
          <strong>${escapeHtml(p.name)}</strong>
        </td>
        <td>${p.blogs}</td>
        <td>${p.points}</td>
        <td>${period === "monthly" && p.rank <= 5 ? `<span class="fs-gift-eligible">${icon("gift")} Surprise gift eligible</span>` : p.badge || "—"}</td>
      </tr>`).join("");
    }
  }
  function renderMiniLeaderboard(period) {
    const list = $("#fs-mini-lb-list");
    if (!list) return;
    const data2 = (data.leaderboard || {})[period] || [];
    list.innerHTML = data2.slice(0, 7).map((p) => `
    <div class="fs-mini-lb-row">
      <div class="fs-mini-rank">${p.badge || "#" + p.rank}</div>
      <div class="fs-mini-av">${p.avatar}</div>
      <div class="fs-mini-info">
        <div class="fs-mini-name">${escapeHtml(p.name)}</div>
        <div class="fs-mini-stats">${p.blogs} stories</div>
      </div>
      <div class="fs-mini-pts">+${p.points}pt${p.points > 1 ? "s" : ""}</div>
    </div>`).join("");
  }
  function openStoryModal() {
    const dishOptions = menu.map((m) => `<option value="${m.id}">${escapeHtml(m.name)}</option>`).join("");
    const eligibleOrders = (data.orders || []).filter((o) => Number(o.subtotal) > 599 && ["delivered", "completed"].includes(String(o.status).toLowerCase()));
    const orderOptions = eligibleOrders.map((o) => `<option value="${escapeHtml(o.id)}">Order #${escapeHtml(o.id)} · ${money(o.subtotal)} · completed</option>`).join("");
    openDialog(`
    <div class="dialog-kicker">BHADAWAR FOOD STORIES</div>
    <h2>Share your <em>experience.</em></h2>
    <p style="color:#888;font-size:13px">Approved stories earn <strong>1 Bhadawar Point</strong>. Link a completed order above ₹599 for <strong>2 extra points</strong>.</p>
    <form id="story-submit-form" style="display:flex;flex-direction:column;gap:12px">
      <div class="field">
        <label>Your Name</label>
        <input id="st-name" required placeholder="Full Name" value="${escapeHtml(data.customerName || "")}">
      </div>
      <div class="field">
        <label>Mobile (for admin only)</label>
        <input id="st-phone" type="tel" required placeholder="10-digit mobile" value="${escapeHtml(data.deliveryAddress.phone || data.wallet.phone || "")}">
      </div>
      <div class="field">
        <label>Dish</label>
        <select id="st-dish">${dishOptions}</select>
      </div>
      <div class="field">
        <label>Rating</label>
        <select id="st-rating">
          <option value="5">★★★★★ Excellent</option>
          <option value="4">★★★★☆ Very Good</option>
          <option value="3">★★★☆☆ Good</option>
          <option value="2">★★☆☆☆ Fair</option>
          <option value="1">★☆☆☆☆ Poor</option>
        </select>
      </div>
      <div class="field">
        <label>Your Story</label>
        <textarea id="st-text" required placeholder="Tell us about the taste, your memory, the moment…" style="min-height:90px"></textarea>
      </div>
      <div class="field">
        <label>Completed order (optional)</label>
        <select id="st-order"><option value="">No order bonus</option>${orderOptions}</select>
        <small style="color:#777">Only completed orders with a food subtotal above ₹599 qualify. Your approved story is the feedback.</small>
      </div>
      <div class="field">
        <label>Food photo or video</label>
        <input type="file" id="st-media" accept="image/*,video/*" required style="padding:6px">
        <div id="st-media-preview" style="margin-top:8px"></div>
      </div>
      <p style="font-size:11px;color:#777;margin:0">Google Reviews are separate and never carry Bhadawar reward points.</p>
      <button class="button button-green" type="submit" style="width:100%;margin-top:4px">Submit Story →</button>
    </form>
  `);
    document.getElementById("st-media")?.addEventListener("change", function() {
      const file = this.files[0];
      if (!file) return;
      const prev = document.getElementById("st-media-preview");
      const url = URL.createObjectURL(file);
      prev.innerHTML = file.type.startsWith("video/") ? `<video src="${url}" controls style="width:100%;border-radius:8px;max-height:180px"></video>` : `<img src="${url}" style="width:100%;border-radius:8px;max-height:180px;object-fit:cover">`;
    });
    document.getElementById("story-submit-form").onsubmit = async (e) => {
      e.preventDefault();
      const file = document.getElementById("st-media").files[0];
      if (!file) {
        toast("Choose a food photo or video first.", true);
        return;
      }
      if (!file.type.startsWith("image/") && !file.type.startsWith("video/")) {
        toast("Upload an image or video file.", true);
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        toast("Please keep each upload under 50 MB.", true);
        return;
      }
      const dishSel = document.getElementById("st-dish");
      const form = new FormData();
      form.set("author", document.getElementById("st-name").value.trim());
      form.set("phone", document.getElementById("st-phone").value.trim());
      form.set("dish", dishSel.options[dishSel.selectedIndex].text);
      form.set("dish_id", dishSel.value);
      form.set("rating", document.getElementById("st-rating").value);
      form.set("text", document.getElementById("st-text").value.trim());
      form.set("order_id", document.getElementById("st-order").value);
      form.set("media", file);
      data.wallet.phone = form.get("phone");
      data.customerName = form.get("author");
      save();
      const submit = e.submitter;
      if (submit) {
        submit.disabled = true;
        submit.textContent = "Uploading…";
      }
      const result = await API.postForm("food-stories", form);
      if (!result?.success) {
        if (submit) {
          submit.disabled = false;
          submit.textContent = "Submit Story →";
        }
        toast(result?.error || "Could not upload the story. Start the Bhadawar preview server and try again.", true);
        return;
      }
      closeDialog();
      await syncFromBackend();
      toast("Story submitted for admin approval.");
    };
  }
  function initAdminStoriesDesk() {
    const desk = $("#admin-stories-desk");
    if (!desk) return;
    const pending = (data.foodStories || []).filter((s) => s.status === "pending");
    if (!pending.length) {
      desk.innerHTML = '<p style="color:#888;text-align:center;padding:24px">No pending stories for review.</p>';
      return;
    }
    desk.innerHTML = pending.map((s) => `
    <div class="admin-story-card" data-story-id="${escapeHtml(s.id)}">
      <div class="admin-story-header">
        <span class="story-avatar">${s.author[0].toUpperCase()}</span>
        <div>
          <strong>${escapeHtml(s.author)}</strong> · ${escapeHtml(s.dish)}
          <div style="font-size:12px;color:#888">${starsHtml(s.rating)} · ${timeAgo(s.date)}</div>
        </div>
        ${s.orderId ? `<span class="verified-badge">Order #${escapeHtml(s.orderId)}</span>` : ""}
      </div>
      <p style="margin:8px 0;font-size:14px">"${escapeHtml(s.text)}"</p>
      ${s.photo ? s.mediaType === "video" ? `<video src="${escapeHtml(mediaUrl(s.photo))}" controls playsinline style="width:min(100%,360px);max-height:260px;border-radius:10px;background:#211"></video>` : `<img src="${escapeHtml(mediaUrl(s.photo))}" alt="Customer food upload" style="width:min(100%,360px);max-height:260px;object-fit:cover;border-radius:10px">` : ""}
      <div style="display:flex;gap:8px;margin-top:8px">
        <button class="button button-green btn-approve-story" data-story-id="${escapeHtml(s.id)}" style="flex:1">✔ Approve (+1 point)</button>
        <button class="button" style="flex:1;background:#e44;color:#fff" data-reject-id="${escapeHtml(s.id)}">✖ Reject</button>
      </div>
    </div>
  `).join("");
    desk.querySelectorAll(".btn-approve-story").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const storyId = btn.dataset.storyId;
        const story = data.foodStories.find((s) => s.id === storyId);
        if (!story) return;
        btn.disabled = true;
        const result = await API.post("food-stories/approve", { story_id: storyId });
        if (!result?.success) {
          btn.disabled = false;
          toast(result?.error || "Could not approve this story.", true);
          return;
        }
        await syncFromBackend();
        toast(result.message || "Story approved. +1 point added to the wallet.");
      });
    });
    desk.querySelectorAll("[data-reject-id]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const storyId = btn.dataset.rejectId;
        const story = data.foodStories.find((s) => s.id === storyId);
        if (!story) return;
        btn.disabled = true;
        const result = await API.post("food-stories/reject", { story_id: storyId });
        if (!result?.success) {
          btn.disabled = false;
          toast(result?.error || "Could not reject this story.", true);
          return;
        }
        await syncFromBackend();
        toast("Story rejected. No points were awarded.");
      });
    });
  }
  function initStoriesEvents() {
    const googleReview = $("#google-review-link");
    if (googleReview) googleReview.href = config.googleReviewUrl || "https://www.google.com/maps/search/?api=1&query=Bhadawar+Hotel+Agra";
    $$(".fs-info-card[data-story-shortcut]").forEach((card) => {
      card.addEventListener("click", () => {
        const shortcut = card.dataset.storyShortcut;
        if (shortcut === "bonus") {
          openStoryModal();
          return;
        }
        const tab = shortcut === "leaderboard" ? "leaderboard" : "feed";
        const tabButton = $(`.fs-tab[data-story-tab="${tab}"]`);
        if (tabButton) tabButton.click();
        const target = shortcut === "leaderboard" ? $("#leaderboard") : $("#published-stories-grid");
        target?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
    $$(".fs-tab").forEach((btn) => {
      btn.addEventListener("click", () => {
        $$(".fs-tab").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const tab = btn.dataset.storyTab;
        const feedEl = $("#panel-stories-feed");
        const lbEl = $("#panel-stories-leaderboard");
        if (feedEl) feedEl.hidden = tab !== "feed";
        if (lbEl) lbEl.hidden = tab !== "leaderboard";
        if (tab === "leaderboard") {
          const activePeriod = $(".fs-lb-toggle .fs-lb-btn.active")?.dataset?.period || "monthly";
          renderLeaderboard(activePeriod);
        }
      });
    });
    document.addEventListener("click", (e) => {
      const btn = e.target.closest(".fs-lb-btn");
      if (!btn) return;
      const isMini = !!btn.dataset.mini;
      const period = btn.dataset.period;
      const parent = btn.closest(".fs-lb-toggle");
      parent?.querySelectorAll(".fs-lb-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      if (isMini) {
        renderMiniLeaderboard(period);
      } else {
        renderLeaderboard(period);
      }
    });
    document.addEventListener("click", (e) => {
      if (e.target.closest(".btn-share-story")) {
        openStoryModal();
      }
    });
    $("#feed-review-shortcut")?.addEventListener("click", openStoryModal);
    function checkHashTab() {
      if (window.location.hash === "#leaderboard") {
        const lbBtn = document.querySelector('.fs-tab[data-story-tab="leaderboard"]');
        if (lbBtn) {
          lbBtn.click();
          document.getElementById("food-stories")?.scrollIntoView({ behavior: "smooth" });
        }
      }
    }
    window.addEventListener("hashchange", checkHashTab);
    checkHashTab();
  }
  window.addEventListener("pageshow", () => {
    if (document.body.dataset.page !== "home") return;
    Object.assign(data, loadData());
    updateCartCounters();
    updateOrderModeUI();
  });
  return {
    initFoodStories,
    initAdminStoriesDesk,
    renderStoryBar,
    renderFoodStories,
    renderLeaderboard,
    renderMiniLeaderboard
  };
}
let activeTrap = null;
const focusableSelector = [
  "a[href]",
  "area[href]",
  "button:not([disabled])",
  'input:not([disabled]):not([type="hidden"])',
  "select:not([disabled])",
  "textarea:not([disabled])",
  "iframe",
  "object",
  "embed",
  '[contenteditable="true"]',
  '[tabindex]:not([tabindex="-1"])'
].join(",");
function trapFocus(root, { onEscape } = {}) {
  if (!root) return () => {
  };
  activeTrap?.release(false);
  const previousFocus = document.activeElement;
  const getFocusable = () => Array.from(root.querySelectorAll(focusableSelector)).filter(
    (element) => !element.hidden && element.getAttribute("aria-hidden") !== "true" && element.getClientRects().length > 0
  );
  const trap = {
    release(restore = true) {
      root.removeEventListener("keydown", onKeyDown);
      if (activeTrap === trap) activeTrap = null;
      if (restore && previousFocus?.isConnected && typeof previousFocus.focus === "function") {
        previousFocus.focus({ preventScroll: true });
      }
    }
  };
  function onKeyDown(event) {
    if (event.key === "Escape" && onEscape) {
      event.preventDefault();
      onEscape();
      return;
    }
    if (event.key !== "Tab") return;
    const focusable = getFocusable();
    if (!focusable.length) {
      event.preventDefault();
      root.focus({ preventScroll: true });
      return;
    }
    const first2 = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && (document.activeElement === first2 || !root.contains(document.activeElement))) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && (document.activeElement === last || !root.contains(document.activeElement))) {
      event.preventDefault();
      first2.focus();
    }
  }
  activeTrap = trap;
  root.addEventListener("keydown", onKeyDown);
  const first = getFocusable()[0];
  requestAnimationFrame(() => (first || root).focus({ preventScroll: true }));
  return () => trap.release(true);
}
export {
  createStoriesModule as a,
  calculateWalletRedemption as b,
  createApiModule as c,
  calculateCart as d,
  changeCartQuantity as e,
  deleteCartItem as f,
  addCartItem as g,
  hydrateIcons as h,
  icon as i,
  createWalletModule as j,
  renderCartDrawer as r,
  trapFocus as t
};
