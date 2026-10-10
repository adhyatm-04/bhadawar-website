export function createApiModule({ baseUrl, getData, getDefaultData, renderers }) {
  const apiOrigin = baseUrl.replace(/\/api\/?$/, '');
  function readResponseBody(text) {
    if (!text) return {};
    try {
      return JSON.parse(text);
    } catch {
      return { __nonJson: true, error: text.replace(/\s+/g, ' ').trim().slice(0, 240) };
    }
  }

  function reportFailure(endpoint, status, message, { notifyUnavailable = true } = {}) {
    const unavailable = status === 0 || status === 404 || status >= 500;
    const detail = { endpoint, httpStatus: status, error: message, unavailable };
    console.warn(`[Bhadawar API] ${endpoint}: ${status ? `HTTP ${status}` : 'network error'} — ${message}`);
    if (unavailable && notifyUnavailable && typeof window !== 'undefined' && typeof CustomEvent !== 'undefined') {
      window.dispatchEvent(new CustomEvent('bhadawar:api-error', { detail }));
    }
    return { success: false, ...detail };
  }

  async function request(endpoint, options, failureOptions) {
    let response;
    try {
      response = await fetch(`${baseUrl}/${endpoint}`, options);
    } catch {
      return reportFailure(endpoint, 0, 'Could not reach the backend.', failureOptions);
    }

    const body = readResponseBody(await response.text());
    if (!response.ok) {
      const message = body?.error || body?.message || `Request failed (${response.status} ${response.statusText || 'HTTP error'}).`;
      return reportFailure(endpoint, response.status, String(message), failureOptions);
    }
    if (body?.__nonJson) {
      return reportFailure(endpoint, response.status, 'The API route returned a non-JSON response.', failureOptions);
    }
    if (body?.error && body?.success === false) {
      return { ...body, httpStatus: response.status };
    }
    return { ...body, httpStatus: response.status };
  }

  const API = {
    async get(endpoint, { notifyUnavailable = true } = {}) {
      return request(endpoint, { credentials: 'same-origin' }, { notifyUnavailable });
    },
    async post(endpoint, payload) {
      return request(endpoint, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    },
    async postForm(endpoint, payload) {
      return request(endpoint, { method: 'POST', body: payload, credentials: 'same-origin' });
    }
  };

  function mediaUrl(path) {
    if (!path || /^(https?:|blob:|data:)/i.test(path)) return path;
    const clean = path.replace(/^\/+/, '');
    return clean.startsWith('uploads/') ? `${apiOrigin}/${clean}` : path;
  }

  async function syncFromBackend() {
    const data = getData();
    if (document.body.dataset.page === 'team') {
      const ordersResponse = await API.get('orders', { notifyUnavailable: false });
      if (ordersResponse?.success) data.orders = ordersResponse.orders || [];
    }

    // These are optional homepage/feed reads with built-in local fallbacks. Keep transient
    // backend outages from covering the menu with a toast during initial page load.
    const storiesResponse = await API.get('food-stories', { notifyUnavailable: false });
    if (storiesResponse?.success && storiesResponse.stories) {
      const approvedStories = storiesResponse.stories.map(story => ({
        ...story,
        date: story.created_at || story.date,
        photo: story.photo ? mediaUrl(story.photo) : '',
        mediaType: story.media_type || story.mediaType || 'image',
        orderAbove599: Boolean(story.bonus_rewarded),
        orderId: story.order_id || story.orderId || '',
        pts: Number(story.pts || 1),
        dishId: story.dish_id
      }));
      if (document.body.dataset.page === 'team') {
        const pendingResponse = await API.get('food-stories?status=pending', { notifyUnavailable: false });
        const pendingStories = (pendingResponse?.stories || []).map(story => ({
          ...story,
          date: story.created_at || story.date,
          photo: story.photo ? mediaUrl(story.photo) : '',
          mediaType: story.media_type || 'image',
          orderId: story.order_id || '',
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

    const leaderboardResponse = await API.get('leaderboard', { notifyUnavailable: false });
    if (leaderboardResponse?.success) {
      data.leaderboard = {
        alltime: leaderboardResponse.alltime || [],
        monthly: leaderboardResponse.monthly || []
      };
      renderers.renderLeaderboard('monthly');
      renderers.renderMiniLeaderboard('monthly');
    }

    if (data.customerProfile?.phone) {
      const walletResponse = await API.get(`wallet?phone=${encodeURIComponent(data.customerProfile.phone)}`, { notifyUnavailable: false });
      if (walletResponse?.success) {
        data.wallet.balance = walletResponse.balance;
        if (walletResponse.transactions?.length) data.wallet.entries = walletResponse.transactions;
        renderers.updateCartCounters();
      }
    }
    if (document.body.dataset.page === 'team') renderers.renderTeamPage();
  }

  return { API, mediaUrl, syncFromBackend };
}
