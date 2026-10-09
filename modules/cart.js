import { calculateWalletRedemption } from './wallet.js';

export function calculateCart(context, orderType = context.getOrderType()) {
  const { data, config, itemById, distanceFromRestaurantKm } = context;
  const pricedRows = data.cart.map(row => ({ row, item: itemById(row.id), qty: Number(row.qty) }))
    .filter(entry => entry.item && Number.isFinite(entry.qty) && entry.qty > 0);
  const subtotal = pricedRows.reduce((sum, { row, item, qty }) => sum + (Number(item.price) || 0) * qty, 0);
  const corporateSubtotal = pricedRows.reduce((sum, { row, item, qty }) => sum + (row.corporate ? (Number(item.price) || 0) * qty : 0), 0);
  const corporateDiscount = corporateSubtotal > 20000 ? Math.round(corporateSubtotal * 0.15) : corporateSubtotal > 10000 ? Math.round(corporateSubtotal * 0.10) : 0;
  const tax = Math.round(subtotal * (Number(config.sampleTaxPercent ?? 5) / 100));
  const address = data.deliveryAddress || {};
  const hasCoordinates = address.latitude != null && address.longitude != null &&
    Number.isFinite(Number(address.latitude)) && Number.isFinite(Number(address.longitude));
  const pinnedDistance = hasCoordinates
    ? distanceFromRestaurantKm(address.latitude, address.longitude)
    : Number(address.deliveryDistanceKm);
  const deliveryDistanceBand = hasCoordinates && Number.isFinite(pinnedDistance)
    ? pinnedDistance > 10 ? 'over10' : pinnedDistance > 5 ? '5to10' : 'under5'
    : address.deliveryDistanceBand || 'under5';
  const phoneKey = String(address.phone || data.wallet?.phone || '').replace(/\D/g, '').slice(-10);
  const firstOrder = !data.orders?.some(order =>
    String(order.customer_phone || '').replace(/\D/g, '').slice(-10) === phoneKey && order.order_type !== 'corporate'
  );
  const delivery = orderType === 'delivery' && deliveryDistanceBand !== 'over10'
    ? firstOrder ? 0 : deliveryDistanceBand === '5to10' ? Number(config.sampleLongDeliveryFee ?? 50) : Number(config.sampleDeliveryFee ?? 35)
    : 0;
  const total = subtotal + tax + delivery - corporateDiscount;
  return { subtotal, corporateSubtotal, corporateDiscount, tax, delivery, deliveryDistanceBand, firstOrder, outsideDeliveryRange: deliveryDistanceBand === 'over10', total };
}

export function renderCartDrawer(context) {
  const { data, $, itemById, money, escapeHtml, calcCart, getOrderType, icon } = context;
  const list = $('#drawer-cart-items');
  if (!list) return;
  const rows = data.cart.map(row => ({ row, item: itemById(row.id) }))
    .filter(entry => entry.item && Number.isInteger(Number(entry.row.qty)) && Number(entry.row.qty) > 0);
  if (!rows.length) {
    list.innerHTML = `
      <div class="cart-empty-state">
        ${icon('bowl', 'cart-empty-icon')}
        <strong>Your order is empty</strong>
        <p>Add some fresh Agra favorites from our menu.</p>
      </div>`;
    $('#bill-item-total').textContent = '₹0';
    $('#bill-delivery-fee').textContent = '₹0';
    $('#bill-tax').textContent = '₹0';
    $('#bill-grand-total').textContent = '₹0';
    const proceed = $('#drawer-proceed-btn');
    if (proceed) { proceed.disabled = true; proceed.textContent = 'Add dishes to continue'; }
    return;
  }
  const proceed = $('#drawer-proceed-btn');
  if (proceed) { proceed.disabled = false; proceed.textContent = 'Proceed to checkout →'; }
  list.innerHTML = rows.map(({ row, item }) => {
    const photoSrc = item.photo?.startsWith('assets/') ? item.photo : 'assets/food-paneer.jpg';
    return `
      <div class="drawer-cart-item">
        <div class="drawer-item-thumb"><img src="${escapeHtml(photoSrc)}" alt="${escapeHtml(item.name)}" onerror="this.src='assets/bhadawar-mark.png'"></div>
        <div class="drawer-item-info"><strong class="drawer-item-title">${escapeHtml(item.name)}</strong><span class="drawer-item-price">${money(item.price)}</span></div>
        <div class="quantity-control">
          <button type="button" data-drawer-qty="${escapeHtml(item.id)}" data-step="-1" aria-label="Decrease ${escapeHtml(item.name)}">−</button>
          <span>${Number(row.qty)}</span>
          <button type="button" data-drawer-qty="${escapeHtml(item.id)}" data-step="1" aria-label="Increase ${escapeHtml(item.name)}">+</button>
        </div>
        <button type="button" class="drawer-item-delete-btn" data-drawer-delete="${escapeHtml(item.id)}" aria-label="Remove ${escapeHtml(item.name)}">${icon('trash')}</button>
      </div>`;
  }).join('');
  const calc = calcCart();
  const usePoints = Boolean($('#cart-use-points')?.checked && data.wallet.balance > 0);
  const pointsDiscount = calculateWalletRedemption(calc.total, data.wallet.balance, data.settings?.maxRedeemPercent ?? 50, usePoints);
  const grandTotal = Math.max(0, calc.total - pointsDiscount);
  $('#bill-item-total').textContent = money(calc.subtotal);
  $('#bill-delivery-fee').textContent = calc.outsideDeliveryRange && getOrderType() === 'delivery' ? 'Not available beyond 10 km' : calc.delivery ? money(calc.delivery) : 'Free';
  $('#bill-tax').textContent = money(calc.tax) + '.00';
  $('#bill-grand-total').textContent = money(grandTotal) + '.00';
  const discountRow = $('#bill-discount-row');
  if (discountRow) {
    discountRow.hidden = !usePoints;
    $('#bill-discount').textContent = `−${money(pointsDiscount)}`;
  }
  const walletBalance = $('#cart-wallet-balance');
  if (walletBalance) walletBalance.textContent = `${data.wallet.balance} points (${money(data.wallet.balance)})`;
}

export function addCartItem(context, id) {
  const { data, itemById, save, renderDrawerCart, renderFullMenu, toast } = context;
  const item = itemById(id);
  if (!item) return;
  const row = data.cart.find(entry => entry.id === id);
  if (row) row.qty = Number(row.qty || 0) + 1;
  else data.cart.push({ id, qty: 1 });
  save();
  renderDrawerCart();
  renderFullMenu();
  toast(`Added to order: ${item.name}`);
}

export function changeCartQuantity(context, id, step) {
  const { data, addToCart, save, renderDrawerCart } = context;
  const row = data.cart.find(entry => entry.id === id);
  if (!row) {
    if (step > 0) addToCart(id);
    return;
  }
  row.qty = Number(row.qty || 0) + step;
  if (row.qty <= 0) data.cart = data.cart.filter(entry => entry.id !== id);
  save();
  renderDrawerCart();
}

export function deleteCartItem(context, id) {
  const { data, save, renderDrawerCart, toast } = context;
  data.cart = data.cart.filter(entry => entry.id !== id);
  save();
  renderDrawerCart();
  toast('Item removed from order');
}
