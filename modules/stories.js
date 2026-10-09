import { icon } from './icons.js';

export function createStoriesModule(context) {
  const { data, menu, API, $, $$, money, escapeHtml, toast, save, updateCartCounters, updateOrderModeUI, openDialog, closeDialog, config, mediaUrl, syncFromBackend, loadData } = context;
let fsViewerIndex  = 0;
let fsViewerTimer  = null;
let fsMuted        = true;
let fsViewerPaused = false;
const FS_SLIDE_MS  = 5000;
/* Image map: dish ID → local asset */
const dishPhotoMap = {
  'mains-paneer-butter-masala':  'assets/dishes/mains-paneer-butter-masala.webp',
  'breads-butter-naan':          'assets/dishes/breads-butter-naan.webp',
  'daal-daal-makhni':            'assets/dishes/daal-daal-makhni.webp',
  'snacks-paneer-tikka':         'assets/dishes/snacks-paneer-tikka.webp',
  'mains-bhadawari-special-paneer': 'assets/dishes/mains-bhadawari-special-paneer.webp',
};
const fallbackPhotos = [
  'assets/food-paneer.jpg','assets/food-snacks.jpg','assets/food-daal.jpg',
  'assets/food-bread.jpg', 'assets/food-thali.jpg','assets/food-rice.jpg',
];
function storyPhoto(s, idx) {
  return s.photo ? mediaUrl(s.photo) : dishPhotoMap[s.dishId] || fallbackPhotos[idx % fallbackPhotos.length] || 'assets/food-paneer.jpg';
}
/* ── Helpers ── */
function starsHtml(n) {
  return '★'.repeat(n) + '☆'.repeat(5 - n);
}
function timeAgo(iso) {
  const d = new Date(iso);
  const diff = Math.floor((Date.now() - d) / 1000);
  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
  return `${Math.floor(diff/86400)}d ago`;
}
function awardPoint(amount, label) {
  data.wallet.balance += amount;
  data.wallet.entries = data.wallet.entries || [];
  data.wallet.entries.unshift({ type:'credit', amount, label, date: new Date().toISOString() });
  save();
  updateCartCounters();
}
function storyPoints(story) {
  return Number(story.pts || 1);
}
function initFoodStories() {
  renderStoryBar();
  renderFoodStories();
  renderLeaderboard('monthly');
  renderMiniLeaderboard('monthly');
  initViewerControls();
  initStoriesEvents();
  initAdminStoriesDesk();
}
/* ── Story Bar (Instagram-style) ── */
function renderStoryBar() {
  const bar = $('#fs-story-bar');
  if (!bar) return;
  const approved = (data.foodStories || []).filter(s => s.status === 'approved').sort((a,b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at));
  // Keep the Add Story bubble (first child), replace rest
  const addBubble = bar.querySelector('.fs-story-add');
  bar.innerHTML = '';
  if (addBubble) bar.appendChild(addBubble);
  approved.forEach((s, i) => {
    const photo = s.mediaType === 'video' ? (dishPhotoMap[s.dishId] || fallbackPhotos[i % fallbackPhotos.length]) : storyPhoto(s, i);
    const bubbleLabel = s.editorial ? s.dish.split(' ').slice(0, 2).join(' ') : s.author.split(' ')[0];
    const bubble = document.createElement('button');
    bubble.type = 'button';
    bubble.className = 'fs-story-bubble';
    bubble.dataset.storyIdx = i;
    bubble.innerHTML = `
      <div class="fs-bubble-ring fs-bubble-ring--unseen">
        <img class="fs-bubble-img" src="${escapeHtml(photo)}" alt="${escapeHtml(s.author)}"
             onerror="this.src='assets/food-paneer.jpg'">
      </div>
      <span class="fs-bubble-name">${escapeHtml(bubbleLabel)}</span>
    `;
    bubble.addEventListener('click', () => {
      fsViewerIndex = i;
      showViewerStory(approved);
      openViewerOnMobile();
    });
    bar.appendChild(bubble);
  });
}
/* ── Feed Cards ── */
function renderFoodStories() {
  const grid = $('#published-stories-grid');
  if (!grid) return;
  const approved = (data.foodStories || []).filter(s => s.status === 'approved').sort((a,b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at));
  const badge = $('#stories-count-badge');
  if (badge) badge.textContent = approved.length;
  if (!approved.length) {
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:60px 20px;color:#9a8760">
        <div class="fs-empty-icon" aria-hidden="true">${icon('bowl')}</div>
        <h3 style="font-size:18px;font-weight:700;color:#3a2a1a;margin:0 0 8px">No stories yet</h3>
        <p style="margin:0 0 20px;font-size:14px">Be the first to share your Bhadawar experience!</p>
        <button class="fs-share-btn btn-share-story" style="display:inline-flex">
          <span class="fs-share-icon" aria-hidden="true">${icon('edit')}</span> Share Your Story <span class="fs-pts-chip">+1 Pt</span>
        </button>
      </div>`;
    return;
  }
  grid.innerHTML = approved.map((s, i) => {
    const photo = storyPhoto(s, i);
    const liked = (data.likedStories || []).includes(s.id);
    const media = s.mediaType === 'video'
      ? `<video class="fs-card-img" src="${escapeHtml(photo)}" poster="${escapeHtml(dishPhotoMap[s.dishId] || fallbackPhotos[i % fallbackPhotos.length])}" muted playsinline preload="metadata"></video><span class="fs-video-chip">▶ Video</span>`
      : `<img class="fs-card-img" src="${escapeHtml(photo)}" alt="${escapeHtml(s.dish)}" loading="lazy" onerror="this.src='assets/food-paneer.jpg'">`;
    return `
    <article class="fs-story-card" data-story-idx="${i}"
             aria-label="Story by ${escapeHtml(s.author)}">
      <div class="fs-card-img-wrap">
        ${media}
        <div class="fs-card-gradient"></div>
        <div class="fs-card-dish-badge">${icon('bowl')} ${escapeHtml(s.dish)}</div>
        ${s.orderAbove599 ? '<div class="fs-card-verified">✔ Verified Order</div>' : ''}
      </div>
      <div class="fs-card-body">
        <div class="fs-card-author">
          <div class="fs-card-avatar">${s.author[0].toUpperCase()}</div>
          <div>
            <div class="fs-card-name">${escapeHtml(s.author)}</div>
            <div class="fs-card-time">${timeAgo(s.date)}</div>
          </div>
        <div class="fs-card-pts" style="margin-left:auto">${s.editorial ? 'Kitchen story' : '+' + storyPoints(s) + 'pt' + (storyPoints(s)>1?'s':'')}</div>
        </div>
        <div class="fs-card-stars">${s.editorial ? 'FROM THE BHADAWAR KITCHEN' : starsHtml(s.rating)}</div>
        <p class="fs-card-text">"${escapeHtml(s.text)}"</p>
        <div class="fs-card-actions">
          <button type="button" class="fs-card-action-btn ${liked ? 'is-liked' : ''}" data-like-story="${escapeHtml(s.id)}" aria-label="${liked ? 'Unlike' : 'Like'} ${escapeHtml(s.author)}’s story" aria-pressed="${liked}">${icon('heart')} ${Number(s.likes || 0) + (liked ? 1 : 0)}</button>
          <button type="button" class="fs-card-action-btn" data-share-story="${escapeHtml(s.id)}">${icon('share')} Share</button>
          <button class="fs-card-read-btn" data-viewer-idx="${i}">Read Story</button>
        </div>
      </div>
    </article>`;
  }).join('');
  grid.querySelectorAll('[data-like-story]').forEach(btn => btn.addEventListener('click', async e => {
    e.stopPropagation();
    const id = btn.dataset.likeStory;
    data.likedStories = data.likedStories || [];
    const at = data.likedStories.indexOf(id);
    if (at >= 0) data.likedStories.splice(at, 1); else data.likedStories.push(id);
    const story = approved.find(item => item.id === id);
    if (story) {
      story.likes = Math.max(0, Number(story.likes || 0) + (at >= 0 ? -1 : 1));
      if (!story.editorial) await API.post('food-stories/like', { story_id: id, liked: at < 0 });
    }
    save(); renderFoodStories();
  }));
  grid.querySelectorAll('[data-share-story]').forEach(btn => btn.addEventListener('click', async e => {
    e.stopPropagation();
    const story = approved.find(item => item.id === btn.dataset.shareStory);
    if (!story) return;
    const shareData = { title: `${story.dish} · Bhadawar Food Story`, text: `${story.author}: ${story.text}`, url: `${location.origin}${location.pathname}#food-stories` };
    try { if (navigator.share) await navigator.share(shareData); else { await navigator.clipboard.writeText(shareData.url); toast('Story link copied'); } }
    catch { /* Share sheet dismissed. */ }
  }));
  // Wire Read Story buttons
  grid.querySelectorAll('[data-viewer-idx]').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      fsViewerIndex = parseInt(btn.dataset.viewerIdx);
      const approved2 = (data.foodStories||[]).filter(s=>s.status==='approved').sort((a,b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at));
      showViewerStory(approved2);
      openViewerOnMobile();
    });
  });
  grid.querySelectorAll('.fs-card-img-wrap').forEach(wrap => wrap.addEventListener('click', () => {
    const index = parseInt(wrap.closest('.fs-story-card').dataset.storyIdx);
    if (!Number.isNaN(index)) { fsViewerIndex = index; showViewerStory(approved); openViewerOnMobile(); }
  }));
  // Init viewer with first story
  const allApproved = (data.foodStories||[]).filter(s=>s.status==='approved').sort((a,b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at));
  if (allApproved.length) showViewerStory(allApproved);
}
/* ── Story Viewer ── */
function showViewerStory(stories) {
  if (!stories.length) return;
  fsViewerIndex = ((fsViewerIndex % stories.length) + stories.length) % stories.length;
  clearTimeout(fsViewerTimer);
  const s     = stories[fsViewerIndex] || stories[0];
  const photo = storyPhoto(s, fsViewerIndex);
  const img   = $('#fs-viewer-img');
  const video = $('#fs-viewer-video');
  const dish  = $('#fs-viewer-dish');
  const story = $('#fs-viewer-story');
  const auth  = $('#fs-viewer-author');
  const stars = $('#fs-viewer-stars');
  const prog  = $('#fs-progress-row');
  if (s.mediaType === 'video' && video) {
    if (img) img.hidden = true;
    video.hidden = false;
    video.src = photo;
    video.muted = fsMuted;
    video.currentTime = 0;
    if (!fsViewerPaused) video.play().catch(() => {});
  } else if (img) {
    if (video) { video.pause(); video.removeAttribute('src'); video.load(); video.hidden = true; }
    img.hidden = false;
    img.style.opacity = '0';
    img.src = photo;
    img.onload = () => { img.style.opacity = '1'; };
    img.onerror = () => { img.src = 'assets/food-paneer.jpg'; img.style.opacity='1'; };
  }
  if (dish)  dish.innerHTML  = `${icon('bowl')} ${escapeHtml(s.dish)}`;
  if (story) story.textContent = '"' + s.text + '"';
  if (stars) stars.textContent = s.editorial ? 'From the Bhadawar kitchen' : starsHtml(s.rating);
  if (auth)  auth.innerHTML = `
    <div class="fs-viewer-av">${s.author[0].toUpperCase()}</div>
    <div>
      <div class="fs-viewer-name">${escapeHtml(s.author)}</div>
      <div class="fs-viewer-time">${timeAgo(s.date)}</div>
    </div>
    ${s.orderAbove599 ? '<span style="margin-left:auto;font-size:10px;background:rgba(23,131,69,.85);color:#fff;padding:2px 8px;border-radius:50px">✔ Verified</span>' : ''}
  `;
  // Progress segments
  if (prog) {
    prog.innerHTML = stories.map((_, i) => `
      <div class="fs-progress-seg ${i < fsViewerIndex ? 'done' : i === fsViewerIndex ? 'active' : ''}">
        ${i === fsViewerIndex ? `<div class="fs-progress-fill ${fsViewerPaused ? 'paused' : ''}"></div>` : ''}
      </div>`).join('');
  }
  const muteButton = $('#fs-mute-btn');
  if (muteButton) { muteButton.innerHTML = icon(fsMuted ? 'soundOff' : 'soundOn'); muteButton.setAttribute('aria-label', fsMuted ? 'Unmute story' : 'Mute story'); }
  const pauseButton = $('#fs-pause-btn');
  if (pauseButton) { pauseButton.innerHTML = icon(fsViewerPaused ? 'play' : 'pause'); pauseButton.setAttribute('aria-label', fsViewerPaused ? 'Play story' : 'Pause story'); }
  // Highlight active bubble
  $$('[data-story-idx]').forEach(b => b.querySelector('.fs-bubble-ring')?.classList.remove('fs-bubble-ring--active'));
  const activeBubble = $(`[data-story-idx="${fsViewerIndex}"]`);
  activeBubble?.querySelector('.fs-bubble-ring')?.classList.add('fs-bubble-ring--active');
  // Auto-advance
  if (!fsViewerPaused) fsViewerTimer = setTimeout(() => {
    fsViewerIndex = (fsViewerIndex + 1) % stories.length;
    showViewerStory(stories);
  }, FS_SLIDE_MS);
}
function initViewerControls() {
  const stories = () => (data.foodStories||[]).filter(s=>s.status==='approved').sort((a,b) => new Date(b.date || b.created_at) - new Date(a.date || a.created_at));
  $('#fs-viewer-prev')?.addEventListener('click', () => {
    const s = stories();
    if (!s.length) return;
    fsViewerPaused = false;
    fsViewerIndex = (fsViewerIndex - 1 + s.length) % s.length;
    showViewerStory(s);
  });
  $('#fs-viewer-next')?.addEventListener('click', () => {
    const s = stories();
    if (!s.length) return;
    fsViewerPaused = false;
    fsViewerIndex = (fsViewerIndex + 1) % s.length;
    showViewerStory(s);
  });
  $('#fs-viewer-close')?.addEventListener('click', () => {
    clearTimeout(fsViewerTimer);
    $('#fs-viewer-video')?.pause();
    const col = $('#fs-viewer-col');
    if (col) col.style.display = 'none';
  });
  $('#fs-mute-btn')?.addEventListener('click', () => {
    fsMuted = !fsMuted;
    const btn = $('#fs-mute-btn');
    if (btn) btn.innerHTML = icon(fsMuted ? 'soundOff' : 'soundOn');
    const video = $('#fs-viewer-video');
    if (video) video.muted = fsMuted;
    btn?.setAttribute('aria-label', fsMuted ? 'Unmute story' : 'Mute story');
  });
  $('#fs-pause-btn')?.addEventListener('click', () => {
    fsViewerPaused = !fsViewerPaused;
    const video = $('#fs-viewer-video');
    if (fsViewerPaused) {
      clearTimeout(fsViewerTimer);
      video?.pause();
      $('.fs-progress-fill')?.classList.add('paused');
    }
    else { video?.play().catch(() => {}); showViewerStory(stories()); return; }
    const btn = $('#fs-pause-btn');
    if (btn) { btn.innerHTML = icon(fsViewerPaused ? 'play' : 'pause'); btn.setAttribute('aria-label', fsViewerPaused ? 'Play story' : 'Pause story'); }
  });
  $('#fs-viewer-read-btn')?.addEventListener('click', () => {
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
        <span style="background:#fdf6e7;border:1px solid #f0d88a;color:#7a5200;font-size:11px;font-weight:700;padding:3px 10px;border-radius:50px">${icon('bowl')} ${escapeHtml(story.dish)}</span>
        <span style="background:#e6f9ef;border:1px solid #b2e5c8;color:#178345;font-size:11px;font-weight:700;padding:3px 10px;border-radius:50px">+${story.pts} Point${story.pts>1?'s':''} Earned</span>
        ${story.orderAbove599 ? '<span style="background:#e8f4ff;border:1px solid #b3d8f5;color:#0a6fa0;font-size:11px;font-weight:700;padding:3px 10px;border-radius:50px">✔ Verified Order</span>' : ''}
      </div>
    `);
  });
}
function openViewerOnMobile() {
  // On mobile, scroll to viewer
  const col = $('#fs-viewer-col');
  if (col) {
    col.style.display = '';
    col.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}
/* ── Render Leaderboard (full panel) ── */
function renderLeaderboard(period) {
  const podium = $('#podium-cards-grid');
  const tbody  = $('#leaderboard-table-body');
  const list   = (data.leaderboard || {})[period] || [];
  if (podium) {
    const top3  = list.slice(0, 3);
    const order = top3.length >= 3 ? [top3[1], top3[0], top3[2]] : top3;
    const cls   = ['silver','gold','bronze'];
    const medals= [icon('trophy') + ' 2nd', icon('trophy') + ' 1st', icon('trophy') + ' 3rd'];
    podium.innerHTML = order.map((p, i) => `
      <div class="fs-podium-card ${cls[i]}">
        <div class="fs-podium-medal">${medals[i]}</div>
        <div class="fs-podium-av">${p.avatar}</div>
        <div class="fs-podium-name">${escapeHtml(p.name)}</div>
        <div class="fs-podium-stats">${p.blogs} stories · ${p.points} pts</div>
      </div>`).join('');
  }
  if (tbody) {
    tbody.innerHTML = list.map(p => `
      <tr>
        <td class="fs-lb-rank">${p.badge || '#'+p.rank}</td>
        <td>
          <span class="fs-lb-av">${p.avatar}</span>
          <strong>${escapeHtml(p.name)}</strong>
        </td>
        <td>${p.blogs}</td>
        <td>${p.points}</td>
        <td>${period === 'monthly' && p.rank <= 5 ? `<span class="fs-gift-eligible">${icon('gift')} Surprise gift eligible</span>` : p.badge || '—'}</td>
      </tr>`).join('');
  }
}
/* ── Mini Leaderboard (sidebar) ── */
function renderMiniLeaderboard(period) {
  const list = $('#fs-mini-lb-list');
  if (!list) return;
  const data2 = (data.leaderboard || {})[period] || [];
  list.innerHTML = data2.slice(0, 7).map(p => `
    <div class="fs-mini-lb-row">
      <div class="fs-mini-rank">${p.badge || '#'+p.rank}</div>
      <div class="fs-mini-av">${p.avatar}</div>
      <div class="fs-mini-info">
        <div class="fs-mini-name">${escapeHtml(p.name)}</div>
        <div class="fs-mini-stats">${p.blogs} stories</div>
      </div>
      <div class="fs-mini-pts">+${p.points}pt${p.points>1?'s':''}</div>
    </div>`).join('');
}
/* ── Story Submission Modal ── */
function openStoryModal() {
  const dishOptions = menu.map(m => `<option value="${m.id}">${escapeHtml(m.name)}</option>`).join('');
  const eligibleOrders = (data.orders || []).filter(o => Number(o.subtotal) > 599 && ['delivered','completed'].includes(String(o.status).toLowerCase()));
  const orderOptions = eligibleOrders.map(o => `<option value="${escapeHtml(o.id)}">Order #${escapeHtml(o.id)} · ${money(o.subtotal)} · completed</option>`).join('');
  openDialog(`
    <div class="dialog-kicker">BHADAWAR FOOD STORIES</div>
    <h2>Share your <em>experience.</em></h2>
    <p style="color:#888;font-size:13px">Approved stories earn <strong>1 Bhadawar Point</strong>. Link a completed order above ₹599 for <strong>2 extra points</strong>.</p>
    <form id="story-submit-form" style="display:flex;flex-direction:column;gap:12px">
      <div class="field">
        <label>Your Name</label>
        <input id="st-name" required placeholder="Full Name" value="${escapeHtml(data.customerName||'')}">
      </div>
      <div class="field">
        <label>Mobile (for admin only)</label>
        <input id="st-phone" type="tel" required placeholder="10-digit mobile" value="${escapeHtml(data.deliveryAddress.phone || data.wallet.phone || '')}">
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
  document.getElementById('st-media')?.addEventListener('change', function() {
    const file = this.files[0]; if (!file) return;
    const prev = document.getElementById('st-media-preview');
    const url  = URL.createObjectURL(file);
    prev.innerHTML = file.type.startsWith('video/')
      ? `<video src="${url}" controls style="width:100%;border-radius:8px;max-height:180px"></video>`
      : `<img src="${url}" style="width:100%;border-radius:8px;max-height:180px;object-fit:cover">`;
  });
  document.getElementById('story-submit-form').onsubmit = async e => {
    e.preventDefault();
    const file = document.getElementById('st-media').files[0];
    if (!file) { toast('Choose a food photo or video first.', true); return; }
    if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) { toast('Upload an image or video file.', true); return; }
    if (file.size > 50 * 1024 * 1024) { toast('Please keep each upload under 50 MB.', true); return; }
    const dishSel  = document.getElementById('st-dish');
    const form = new FormData();
    form.set('author', document.getElementById('st-name').value.trim());
    form.set('phone', document.getElementById('st-phone').value.trim());
    form.set('dish', dishSel.options[dishSel.selectedIndex].text);
    form.set('dish_id', dishSel.value);
    form.set('rating', document.getElementById('st-rating').value);
    form.set('text', document.getElementById('st-text').value.trim());
    form.set('order_id', document.getElementById('st-order').value);
    form.set('media', file);
    data.wallet.phone = form.get('phone');
    data.customerName = form.get('author');
    save();
    const submit = e.submitter;
    if (submit) { submit.disabled = true; submit.textContent = 'Uploading…'; }
    const result = await API.postForm('food-stories', form);
    if (!result?.success) {
      if (submit) { submit.disabled = false; submit.textContent = 'Submit Story →'; }
      toast(result?.error || 'Could not upload the story. Start the Bhadawar preview server and try again.', true);
      return;
    }
    closeDialog();
    await syncFromBackend();
    toast('Story submitted for admin approval.');
  };
}
/* ── Admin Stories Desk ── */
function initAdminStoriesDesk() {
  const desk = $('#admin-stories-desk');
  if (!desk) return;
  const pending = (data.foodStories || []).filter(s => s.status === 'pending');
  if (!pending.length) {
    desk.innerHTML = '<p style="color:#888;text-align:center;padding:24px">No pending stories for review.</p>';
    return;
  }
  desk.innerHTML = pending.map(s => `
    <div class="admin-story-card" data-story-id="${escapeHtml(s.id)}">
      <div class="admin-story-header">
        <span class="story-avatar">${s.author[0].toUpperCase()}</span>
        <div>
          <strong>${escapeHtml(s.author)}</strong> · ${escapeHtml(s.dish)}
          <div style="font-size:12px;color:#888">${starsHtml(s.rating)} · ${timeAgo(s.date)}</div>
        </div>
        ${s.orderId ? `<span class="verified-badge">Order #${escapeHtml(s.orderId)}</span>` : ''}
      </div>
      <p style="margin:8px 0;font-size:14px">"${escapeHtml(s.text)}"</p>
      ${s.photo ? (s.mediaType === 'video' ? `<video src="${escapeHtml(mediaUrl(s.photo))}" controls playsinline style="width:min(100%,360px);max-height:260px;border-radius:10px;background:#211"></video>` : `<img src="${escapeHtml(mediaUrl(s.photo))}" alt="Customer food upload" style="width:min(100%,360px);max-height:260px;object-fit:cover;border-radius:10px">`) : ''}
      <div style="display:flex;gap:8px;margin-top:8px">
        <button class="button button-green btn-approve-story" data-story-id="${escapeHtml(s.id)}" style="flex:1">✔ Approve (+1 point)</button>
        <button class="button" style="flex:1;background:#e44;color:#fff" data-reject-id="${escapeHtml(s.id)}">✖ Reject</button>
      </div>
    </div>
  `).join('');
  desk.querySelectorAll('.btn-approve-story').forEach(btn => {
    btn.addEventListener('click', async () => {
      const storyId = btn.dataset.storyId;
      const story = data.foodStories.find(s => s.id === storyId);
      if (!story) return;
      btn.disabled = true;
      const result = await API.post('food-stories/approve', { story_id: storyId });
      if (!result?.success) { btn.disabled = false; toast(result?.error || 'Could not approve this story.', true); return; }
      await syncFromBackend();
      toast(result.message || 'Story approved. +1 point added to the wallet.');
    });
  });
  desk.querySelectorAll('[data-reject-id]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const storyId = btn.dataset.rejectId;
      const story = data.foodStories.find(s => s.id === storyId);
      if (!story) return;
      btn.disabled = true;
      const result = await API.post('food-stories/reject', { story_id: storyId });
      if (!result?.success) { btn.disabled = false; toast(result?.error || 'Could not reject this story.', true); return; }
      await syncFromBackend();
      toast('Story rejected. No points were awarded.');
    });
  });
}
/* ── Stories UI Events ── */
function initStoriesEvents() {
  const googleReview = $('#google-review-link');
  if (googleReview) googleReview.href = config.googleReviewUrl || 'https://www.google.com/maps/search/?api=1&query=Bhadawar+Hotel+Agra';
  // Hero feature cards are shortcuts into the matching story actions.
  $$('.fs-info-card[data-story-shortcut]').forEach(card => {
    card.addEventListener('click', () => {
      const shortcut = card.dataset.storyShortcut;
      if (shortcut === 'bonus') {
        openStoryModal();
        return;
      }
      const tab = shortcut === 'leaderboard' ? 'leaderboard' : 'feed';
      const tabButton = $(`.fs-tab[data-story-tab="${tab}"]`);
      if (tabButton) tabButton.click();
      const target = shortcut === 'leaderboard' ? $('#leaderboard') : $('#published-stories-grid');
      target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
  // Main tabs: Feed ↔ Leaderboard
  $$('.fs-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.fs-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tab = btn.dataset.storyTab;
      const feedEl = $('#panel-stories-feed');
      const lbEl   = $('#panel-stories-leaderboard');
      if (feedEl) feedEl.hidden = (tab !== 'feed');
      if (lbEl)   lbEl.hidden   = (tab !== 'leaderboard');
      if (tab === 'leaderboard') {
        const activePeriod = $('.fs-lb-toggle .fs-lb-btn.active')?.dataset?.period || 'monthly';
        renderLeaderboard(activePeriod);
      }
    });
  });
  // Leaderboard period toggles (both in feed panel and mini)
  document.addEventListener('click', e => {
    const btn = e.target.closest('.fs-lb-btn');
    if (!btn) return;
    const isMini = !!btn.dataset.mini;
    const period = btn.dataset.period;
    // Toggle active state only within same group
    const parent = btn.closest('.fs-lb-toggle');
    parent?.querySelectorAll('.fs-lb-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    if (isMini) {
      renderMiniLeaderboard(period);
    } else {
      renderLeaderboard(period);
    }
  });
  // Share Story buttons
  document.addEventListener('click', e => {
    if (e.target.closest('.btn-share-story')) {
      openStoryModal();
    }
  });
  $('#feed-review-shortcut')?.addEventListener('click', openStoryModal);

  // Auto-switch to leaderboard tab if URL has #leaderboard hash
  function checkHashTab() {
    if (window.location.hash === '#leaderboard') {
      const lbBtn = document.querySelector('.fs-tab[data-story-tab="leaderboard"]');
      if (lbBtn) {
        lbBtn.click();
        document.getElementById('food-stories')?.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }
  window.addEventListener('hashchange', checkHashTab);
  checkHashTab();
}
window.addEventListener('pageshow', () => {
  if (document.body.dataset.page !== 'home') return;
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
