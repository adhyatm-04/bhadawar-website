import "./preview-mode-m_uY9Nxy.js";
/* empty css                */
(() => {
  document.querySelector("#corporate-app");
  const loginShell = document.querySelector(".corporate-login-shell");
  const menuView = document.querySelector("#corporate-menu-view");
  const loginForm = document.querySelector("#corporate-login-form");
  const errorBox = document.querySelector("#corporate-login-error");
  let menuItems = [];
  let selectedCategory = "All";
  let staff = null;
  const quantities = /* @__PURE__ */ new Map();
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
  const money = (value) => `₹${Number(value || 0).toLocaleString("en-IN")}`;
  const api = async (path, options = {}) => {
    const response = await fetch(`/api/${path}`, {
      credentials: "same-origin",
      ...options,
      headers: { "Content-Type": "application/json", ...options.headers || {} }
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Could not complete this request.");
    return result;
  };
  function showLogin(message = "") {
    loginShell.hidden = false;
    menuView.hidden = true;
    if (message) {
      errorBox.textContent = message;
      errorBox.hidden = false;
    }
  }
  function renderMenu() {
    const availableItems = menuItems.filter((item) => item.available !== false);
    const categories = ["All", ...new Set(availableItems.map((item) => item.category).filter(Boolean))];
    const visible = availableItems.filter((item) => {
      const matchesCategory = selectedCategory === "All" || item.category === selectedCategory;
      const query = (document.querySelector("#corporate-menu-search")?.value || "").trim().toLowerCase();
      const matchesSearch = !query || `${item.name} ${item.desc} ${item.category}`.toLowerCase().includes(query);
      return matchesCategory && matchesSearch;
    });
    const grid = document.querySelector("#corporate-items-grid");
    if (!grid) return;
    grid.innerHTML = visible.length ? visible.map((item) => `
      <article class="corporate-menu-card">
        <div class="corporate-menu-card-top"><span class="corporate-dish-icon" aria-hidden="true">${escapeHtml(item.emoji || "🍽️")}</span><span class="corporate-category-tag">${escapeHtml(item.category || "Catering")}</span></div>
        <h3>${escapeHtml(item.name)}</h3>
        <p>${escapeHtml(item.desc || "")}</p>
        <div class="corporate-menu-price"><strong>${money(item.price)}</strong><span>${escapeHtml(item.unitLabel || "")}</span></div>
        <label class="corporate-quantity-label">Quantity <span>Min ${Number(item.minQty || 1)}</span><input type="number" min="0" max="500" step="1" value="${Number(quantities.get(item.id) || 0)}" data-corporate-qty="${escapeHtml(item.id)}" aria-label="Quantity for ${escapeHtml(item.name)}"></label>
      </article>`).join("") : '<div class="corporate-no-results">No menu items match that search.</div>';
    document.querySelector("#corporate-result-count").textContent = `${visible.length} of ${availableItems.length} menu items`;
    document.querySelector("#corporate-category-list").innerHTML = categories.map((category) => `<button type="button" class="corporate-category-button ${category === selectedCategory ? "active" : ""}" data-corporate-category="${escapeHtml(category)}">${escapeHtml(category)}</button>`).join("");
    updateOrderSummary();
  }
  function updateOrderSummary(message = "") {
    const selected = menuItems.filter((item) => Number(quantities.get(item.id) || 0) > 0);
    const subtotal = selected.reduce((sum, item) => sum + Number(item.price) * Number(quantities.get(item.id)), 0);
    const discount = Math.round(subtotal * (subtotal > 2e4 ? 0.15 : subtotal > 1e4 ? 0.1 : 0));
    const summary = document.querySelector("#corporate-order-summary");
    if (summary) summary.innerHTML = selected.length ? selected.map((item) => `<div><span>${escapeHtml(item.name)} × ${Number(quantities.get(item.id))}</span><strong>${money(Number(item.price) * Number(quantities.get(item.id)))}</strong></div>`).join("") : '<p class="corporate-empty-order">Select quantities above to start your catering order.</p>';
    const total = document.querySelector("#corporate-order-total");
    if (total) total.innerHTML = `<span>Subtotal <strong>${money(subtotal)}</strong></span>${discount ? `<span>Volume discount <strong>−${money(discount)}</strong></span>` : ""}<span class="corporate-total-payable">Order total <strong>${money(subtotal - discount)}</strong></span>`;
    const button = document.querySelector("#corporate-submit-order");
    if (button) button.disabled = !selected.length;
    const notice = document.querySelector("#corporate-order-status");
    if (notice) {
      notice.textContent = message;
      notice.hidden = !message;
      notice.classList.toggle("is-error", Boolean(message));
    }
    return { selected, subtotal, discount, total: subtotal - discount };
  }
  async function openMenu(currentStaff) {
    staff = currentStaff;
    const result = await api("corporate-menu");
    menuItems = result.items || [];
    selectedCategory = "All";
    loginShell.hidden = true;
    menuView.hidden = false;
    menuView.innerHTML = `
      <header class="corporate-menu-heading">
        <div><div class="corporate-kicker">BHADAWAR · CORPORATE CATERING</div><h1>Your corporate menu</h1><p>Welcome, ${escapeHtml(staff.company || "")} · Staff ID ${escapeHtml(staff.username || "")}</p></div>
        <button type="button" id="corporate-signout" class="corporate-signout">Sign out</button>
      </header>
      <div class="corporate-menu-tools"><label class="corporate-search"><span aria-hidden="true">⌕</span><input id="corporate-menu-search" type="search" placeholder="Search the full catering menu…" aria-label="Search corporate menu"></label><span id="corporate-result-count" class="corporate-result-count"></span></div>
      <nav id="corporate-category-list" class="corporate-category-list" aria-label="Corporate menu categories"></nav>
      <div id="corporate-items-grid" class="corporate-items-grid"></div>
      <form id="corporate-order-form" class="corporate-order-panel">
        <div class="corporate-kicker">YOUR CATERING ORDER</div><h2>Review and submit</h2>
        <div id="corporate-order-summary" class="corporate-order-summary"></div>
        <div id="corporate-order-total" class="corporate-order-total"></div>
        <div class="corporate-order-fields">
          <label>Company<input id="corporate-order-company" value="${escapeHtml(staff.company || "")}" readonly required></label>
          <label>Staff contact number<input id="corporate-order-phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="Enter contact number" required></label>
          <label>Event date<input id="corporate-order-date" type="date" min="${(/* @__PURE__ */ new Date()).toISOString().slice(0, 10)}" required></label>
          <label>Delivery / event location<input id="corporate-order-location" placeholder="Office or venue address" required></label>
        </div>
        <p class="corporate-menu-note">Your order will be sent to Bhadawar for confirmation. Payment is arranged with the catering team.</p>
        <div id="corporate-order-status" class="corporate-order-status" role="status" hidden></div>
        <button type="submit" id="corporate-submit-order" class="corporate-primary-button" disabled>Submit catering order →</button>
      </form>`;
    renderMenu();
    document.querySelector("#corporate-menu-search").addEventListener("input", renderMenu);
    document.querySelector("#corporate-items-grid").addEventListener("input", (event) => {
      const input = event.target.closest("[data-corporate-qty]");
      if (!input) return;
      const quantity = Math.max(0, Math.min(500, Math.floor(Number(input.value) || 0)));
      input.value = String(quantity);
      if (quantity) quantities.set(input.dataset.corporateQty, quantity);
      else quantities.delete(input.dataset.corporateQty);
      updateOrderSummary();
    });
    document.querySelector("#corporate-category-list").addEventListener("click", (event) => {
      const button = event.target.closest("[data-corporate-category]");
      if (!button) return;
      selectedCategory = button.dataset.corporateCategory;
      renderMenu();
    });
    document.querySelector("#corporate-signout").addEventListener("click", async () => {
      await api("auth/logout", { method: "POST", body: "{}" });
      staff = null;
      menuItems = [];
      showLogin();
    });
    document.querySelector("#corporate-order-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const { selected, total } = updateOrderSummary();
      if (!selected.length) return;
      const invalid = selected.find((item) => Number(quantities.get(item.id)) < Number(item.minQty || 1));
      if (invalid) {
        updateOrderSummary(`${invalid.name} requires a minimum quantity of ${Number(invalid.minQty || 1)}.`);
        return;
      }
      const submit = document.querySelector("#corporate-submit-order");
      submit.disabled = true;
      submit.textContent = "Submitting…";
      try {
        const result2 = await api("corporate-orders", {
          method: "POST",
          body: JSON.stringify({
            company_name: staff.company,
            customer_name: staff.company,
            customer_phone: document.querySelector("#corporate-order-phone").value.trim(),
            event_date: document.querySelector("#corporate-order-date").value,
            event_location: document.querySelector("#corporate-order-location").value.trim(),
            items: selected.map((item) => ({ id: item.id, qty: Number(quantities.get(item.id)) }))
          })
        });
        quantities.clear();
        renderMenu();
        document.querySelector("#corporate-order-status").classList.remove("is-error");
        document.querySelector("#corporate-order-status").textContent = `Order ${result2.order_id} submitted. Bhadawar will confirm your ${money(result2.total || total)} catering order.`;
        document.querySelector("#corporate-order-status").hidden = false;
        document.querySelector("#corporate-order-form").reset();
        document.querySelector("#corporate-order-company").value = staff.company || "";
      } catch (error) {
        updateOrderSummary(error.message || "Could not submit this catering order. Please try again.");
      } finally {
        submit.disabled = false;
        submit.textContent = "Submit catering order →";
        if (!menuItems.some((item) => Number(quantities.get(item.id) || 0) > 0)) submit.disabled = true;
      }
    });
  }
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = loginForm.querySelector('button[type="submit"]');
    button.disabled = true;
    errorBox.hidden = true;
    try {
      const result = await api("corporate-auth/login", {
        method: "POST",
        body: JSON.stringify({
          company_name: loginForm.elements.company_name.value.trim(),
          staff_id: loginForm.elements.staff_id.value.trim()
        })
      });
      await openMenu(result.staff);
    } catch (error) {
      errorBox.textContent = error.message;
      errorBox.hidden = false;
      button.disabled = false;
    }
  });
  api("auth/me").then((result) => {
    if (result.staff?.role === "corporate") return openMenu(result.staff);
    if (result.staff) showLogin("Please use your corporate staff sign-in for this page.");
  }).catch(() => {
  });
})();
