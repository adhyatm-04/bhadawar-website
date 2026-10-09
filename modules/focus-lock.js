let activeTrap = null;

const focusableSelector = [
  'a[href]', 'area[href]', 'button:not([disabled])', 'input:not([disabled]):not([type="hidden"])',
  'select:not([disabled])', 'textarea:not([disabled])', 'iframe', 'object', 'embed',
  '[contenteditable="true"]', '[tabindex]:not([tabindex="-1"])'
].join(',');

export function trapFocus(root, { onEscape } = {}) {
  if (!root) return () => {};
  activeTrap?.release(false);
  const previousFocus = document.activeElement;
  const getFocusable = () => Array.from(root.querySelectorAll(focusableSelector)).filter(element =>
    !element.hidden && element.getAttribute('aria-hidden') !== 'true' && element.getClientRects().length > 0
  );

  const trap = {
    release(restore = true) {
      root.removeEventListener('keydown', onKeyDown);
      if (activeTrap === trap) activeTrap = null;
      if (restore && previousFocus?.isConnected && typeof previousFocus.focus === 'function') {
        previousFocus.focus({ preventScroll: true });
      }
    }
  };

  function onKeyDown(event) {
    if (event.key === 'Escape' && onEscape) {
      event.preventDefault();
      onEscape();
      return;
    }
    if (event.key !== 'Tab') return;
    const focusable = getFocusable();
    if (!focusable.length) {
      event.preventDefault();
      root.focus({ preventScroll: true });
      return;
    }
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && (document.activeElement === first || !root.contains(document.activeElement))) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && (document.activeElement === last || !root.contains(document.activeElement))) {
      event.preventDefault();
      first.focus();
    }
  }

  activeTrap = trap;
  root.addEventListener('keydown', onKeyDown);
  const first = getFocusable()[0];
  requestAnimationFrame(() => (first || root).focus({ preventScroll: true }));
  return () => trap.release(true);
}
