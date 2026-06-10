async function renderNotifications(unreadOnly = false) {
  try {
    const data = await API.notifications.getAll(unreadOnly);
    const notifications = data.notifications || [];
    const unreadCount = data.unread_count ?? notifications.filter(n => !n.is_read && !n.lu).length;
    const totalCount = data.total ?? notifications.length;
    const readCount = totalCount - unreadCount;

    document.getElementById('headerUnreadCount').textContent = `${unreadCount} nouvelle${unreadCount > 1 ? 's' : ''}`;
    document.getElementById('statTotal').textContent = totalCount;
    document.getElementById('statUnread').textContent = unreadCount;
    document.getElementById('statRead').textContent = readCount;
    document.getElementById('pageBellDot').style.display = unreadCount > 0 ? 'block' : 'none';

    const list = document.getElementById('notificationsList');
    if (!notifications.length) {
      list.innerHTML = '<div class="no-notifs">Aucune notification disponible pour le moment. Revenez plus tard ou vérifiez votre activité.</div>';
      return;
    }

    list.innerHTML = notifications.map(notification => {
      const isRead = notification.is_read || notification.lu;
      const title = notification.titre || notification.title || 'Notification';
      const content = notification.contenu || notification.body || notification.message || 'Contenu indisponible.';
      const type = notification.type || notification.categorie || 'Général';
      const date = notification.created_at || notification.createdAt || notification.date || new Date().toISOString();
      return `
        <article class="notification-card ${isRead ? '' : 'unread'}">
          <header>
            <strong>${title}</strong>
            <span class="tag">${type}</span>
          </header>
          <p>${content}</p>
          <div class="meta">
            <span>Reçue le ${formatDate(date)}</span>
            <span>${isRead ? 'Lue' : 'Non lue'}</span>
          </div>
          <div class="actions">
            ${!isRead ? `<button class="primary" onclick="markNotificationRead(${notification.id})">Marquer lu</button>` : ''}
            <button class="danger" onclick="removeNotification(${notification.id})">Supprimer</button>
          </div>
        </article>
      `;
    }).join('');
  } catch (error) {
    document.getElementById('notificationsList').innerHTML = '<div class="no-notifs">Impossible de charger les notifications. Vérifiez votre connexion ou reconnectez-vous.</div>';
    console.error('Erreur notifications:', error);
  }
}

async function markNotificationRead(id) {
  try {
    await API.notifications.markRead(id);
    await renderNotifications(document.getElementById('showUnreadBtn').classList.contains('active'));
  } catch (error) {
    console.error('Impossible de marquer la notification comme lue', error);
  }
}

async function removeNotification(id) {
  try {
    await API.notifications.delete(id);
    await renderNotifications(document.getElementById('showUnreadBtn').classList.contains('active'));
  } catch (error) {
    console.error('Impossible de supprimer la notification', error);
  }
}

async function markAllNotificationsRead() {
  try {
    await API.notifications.markAllRead();
    await renderNotifications(document.getElementById('showUnreadBtn').classList.contains('active'));
  } catch (error) {
    console.error('Impossible de marquer toutes les notifications comme lues', error);
  }
}

function updateFilterButtons(activeButton) {
  document.getElementById('showAllBtn').classList.toggle('active', activeButton === 'all');
  document.getElementById('showUnreadBtn').classList.toggle('active', activeButton === 'unread');
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('showAllBtn').addEventListener('click', () => {
    updateFilterButtons('all');
    renderNotifications(false);
  });

  document.getElementById('showUnreadBtn').addEventListener('click', () => {
    updateFilterButtons('unread');
    renderNotifications(true);
  });

  document.getElementById('markAllReadBtn').addEventListener('click', async () => {
    await markAllNotificationsRead();
    updateFilterButtons('all');
  });

  renderNotifications(false);
});
