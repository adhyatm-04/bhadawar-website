export function calculateWalletRedemption(total, balance, maxRedeemPercent = 50, enabled = true) {
  const safeTotal = Math.max(0, Number(total) || 0);
  const safeBalance = Math.max(0, Math.floor(Number(balance) || 0));
  const percent = Math.max(0, Math.min(100, Number(maxRedeemPercent) || 0));
  return enabled ? Math.min(safeBalance, Math.floor(safeTotal * percent / 100)) : 0;
}

export function createWalletModule(context) {
  const { getData, money, openDialog, closeDialog, openCartDrawer, icon } = context;

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
          <div class="wallet-dialog-icon-wrap">${icon('coin', 'wallet-dialog-coin')}</div>
        </div>
        <div class="wallet-dialog-note"><span>₹1 spent</span><b>→</b><span>1 point</span><i></i><span>100 points = ₹100 off</span></div>
        <div class="wallet-dialog-actions">
          <button class="button button-green" id="wallet-use-now">Order Now <span aria-hidden="true">→</span></button>
          <a href="account.html" class="button button-outline">Account details</a>
        </div>
      </div>
    `);
    document.querySelector('#wallet-use-now')?.addEventListener('click', () => {
      closeDialog();
      openCartDrawer();
    });
  }

  return { openWalletDialog };
}
