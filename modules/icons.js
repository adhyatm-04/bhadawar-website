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

export function icon(name, className = '') {
  const body = paths[name] || paths.star;
  const classes = ['icon-svg', className].filter(Boolean).join(' ');
  return `<svg class="${classes}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${body}</svg>`;
}

export function hydrateIcons(root = document) {
  root.querySelectorAll('[data-icon]').forEach(placeholder => {
    const name = placeholder.dataset.icon;
    placeholder.innerHTML = icon(name);
  });
}
