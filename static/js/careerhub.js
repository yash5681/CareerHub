/**
 * CAREERHUB — Interactive Frontend ES6 Modules
 * AJAX Job Saving, Notifications, Live Messaging, and Dynamic Resume Previews
 */

// CSRF Token Helper for Fetch requests
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Toast Notification Trigger
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const bgClass = type === 'success' ? 'bg-success text-white' : 
                  type === 'danger' ? 'bg-danger text-white' : 'bg-dark text-white';

  const toastEl = document.createElement('div');
  toastEl.className = `toast align-items-center ${bgClass} border-0 shadow-lg`;
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body py-3 px-3 fw-semibold">
        <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'} me-2"></i>
        ${message}
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;

  container.appendChild(toastEl);
  const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
  toast.show();
  toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

// Bookmark / Save Job Handler
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.btn-save-job').forEach(button => {
    button.addEventListener('click', async (e) => {
      e.preventDefault();
      const jobId = button.dataset.jobId;
      if (!jobId) return;

      try {
        const response = await fetch(`/jobs/${jobId}/save/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
          }
        });
        
        if (response.status === 401) {
          window.location.href = '/auth/login/?next=' + encodeURIComponent(window.location.pathname);
          return;
        }

        const data = await response.json();
        if (data.status === 'saved') {
          button.classList.add('active', 'text-danger');
          button.innerHTML = '<i class="fa-solid fa-bookmark"></i> <span class="d-none d-md-inline">Saved</span>';
          showToast(data.message || 'Job saved to your bookmarks!', 'success');
        } else if (data.status === 'removed') {
          button.classList.remove('active', 'text-danger');
          button.innerHTML = '<i class="fa-regular fa-bookmark"></i> <span class="d-none d-md-inline">Save</span>';
          showToast(data.message || 'Job removed from bookmarks.', 'info');
        }
      } catch (err) {
        console.error('Error saving job:', err);
      }
    });
  });

  // Mark all notifications read
  const markAllBtn = document.getElementById('markAllNotificationsRead');
  if (markAllBtn) {
    markAllBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      try {
        const resp = await fetch('/notifications/mark-all-read/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        const data = await resp.json();
        if (data.success) {
          document.querySelectorAll('.notification-item.unread').forEach(el => {
            el.classList.remove('unread');
          });
          const badge = document.querySelector('.notification-badge');
          if (badge) badge.remove();
          showToast('All notifications marked as read', 'success');
        }
      } catch (err) {
        console.error('Error marking notifications:', err);
      }
    });
  }
});
