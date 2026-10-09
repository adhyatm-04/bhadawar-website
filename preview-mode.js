window.BHADAWAR_PREVIEW_READY = (async () => {
  if (window.location.protocol === 'file:') return false;
  try {
    const response = await fetch('/api/preview-config', { credentials: 'same-origin', cache: 'no-store' });
    if (!response.ok) return false;
    const config = await response.json();
    if (!config.public_preview) return false;

    if (!document.querySelector('.public-preview-banner')) {
      const notice = document.createElement('aside');
      notice.className = 'public-preview-banner';
      notice.setAttribute('role', 'status');
      notice.textContent = 'TEMPORARY PREVIEW · Orders and bookings are for testing only and will not be prepared or charged. Please do not enter real phone numbers or addresses.';
      document.body.prepend(notice);
    }
    return true;
  } catch {
    return false;
  }
})();
