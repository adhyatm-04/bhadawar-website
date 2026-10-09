(function polyfill() {
  const relList = document.createElement("link").relList;
  if (relList && relList.supports && relList.supports("modulepreload")) return;
  for (const link of document.querySelectorAll('link[rel="modulepreload"]')) processPreload(link);
  new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type !== "childList") continue;
      for (const node of mutation.addedNodes) if (node.tagName === "LINK" && node.rel === "modulepreload") processPreload(node);
    }
  }).observe(document, {
    childList: true,
    subtree: true
  });
  function getFetchOpts(link) {
    const fetchOpts = {};
    if (link.integrity) fetchOpts.integrity = link.integrity;
    if (link.referrerPolicy) fetchOpts.referrerPolicy = link.referrerPolicy;
    if (link.crossOrigin === "use-credentials") fetchOpts.credentials = "include";
    else if (link.crossOrigin === "anonymous") fetchOpts.credentials = "omit";
    else fetchOpts.credentials = "same-origin";
    return fetchOpts;
  }
  function processPreload(link) {
    if (link.ep) return;
    link.ep = true;
    const fetchOpts = getFetchOpts(link);
    fetch(link.href, fetchOpts);
  }
})();
window.BHADAWAR_PREVIEW_READY = (async () => {
  if (window.location.protocol === "file:") return false;
  try {
    const response = await fetch("/api/preview-config", { credentials: "same-origin", cache: "no-store" });
    if (!response.ok) return false;
    const config = await response.json();
    if (!config.public_preview) return false;
    if (!document.querySelector(".public-preview-banner")) {
      const notice = document.createElement("aside");
      notice.className = "public-preview-banner";
      notice.setAttribute("role", "status");
      notice.textContent = "TEMPORARY PREVIEW · Orders and bookings are for testing only and will not be prepared or charged. Please do not enter real phone numbers or addresses.";
      document.body.prepend(notice);
    }
    return true;
  } catch {
    return false;
  }
})();
