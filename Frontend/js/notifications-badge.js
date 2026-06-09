// Centralized notifications badge updater
async function fetchUnreadCount() {
  try {
    const d = await API.notifications.getAll(true);
    const unread = d.unread_count ?? ((d.notifications || []).filter(n => !n.is_read && !n.lu).length);
    return unread;
  } catch (e) {
    console.warn('fetchUnreadCount', e);
    return 0;
  }
}

async function updateNotificationsBadge() {
  const unread = await fetchUnreadCount();
  const has = unread > 0;
  // find all bell elements we added
  const selectors = ['.site-bell', '.notif-bell', '.notification-btn'];
  selectors.forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
      if (has) el.classList.add('has-unread'); else el.classList.remove('has-unread');
      // update accessible label if present
      const label = el.getAttribute('aria-label') || '';
      el.setAttribute('aria-label', has ? `${label} — ${unread} non lue(s)` : label.replace(/ ?—.*$/, ''));
    });
  });
}

// Polling option to keep badge updated
let _notifInterval = null;
function startNotificationsBadgePoll(intervalMs = 30000) {
  updateNotificationsBadge();
  if (_notifInterval) clearInterval(_notifInterval);
  _notifInterval = setInterval(updateNotificationsBadge, intervalMs);
}

// Init on DOM ready
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    if (!/^\/($|index\.html|signin\.html|signup\.html|reset-password\.html)/.test(window.location.pathname)) startNotificationsBadgePoll();
  });
}

// expose for manual control
window.updateNotificationsBadge = updateNotificationsBadge;
window.startNotificationsBadgePoll = startNotificationsBadgePoll;
