/**
 * Notifications sliding panel logic
 */

function toggleNotifications() {
    const panel = document.getElementById('notification-panel');
    const overlay = document.getElementById('notif-overlay');
    
    if (panel.classList.contains('active')) {
        closeNotifications();
    } else {
        openNotifications();
    }
}

function openNotifications() {
    const panel = document.getElementById('notification-panel');
    const overlay = document.getElementById('notif-overlay');
    
    panel.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent scrolling
}

function closeNotifications() {
    const panel = document.getElementById('notification-panel');
    const overlay = document.getElementById('notif-overlay');
    
    panel.classList.remove('active');
    overlay.classList.remove('active');
    document.body.style.overflow = ''; // Restore scrolling
}

// Close panel when clicking outside (on overlay)
document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('notif-overlay');
    
    if (overlay) {
        overlay.addEventListener('click', closeNotifications);
    }
});
