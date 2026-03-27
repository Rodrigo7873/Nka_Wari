/**
 * Logic for the sliding Donation Panel
 */

function openDonPanel() {
    // We can potentially close the side menu first if needed, 
    // but the task asks for the panel to open.
    const panel = document.getElementById('donPanel');
    const overlay = document.getElementById('donOverlay');
    
    // Close side menu if it's open to avoid stacking
    const sideMenu = document.getElementById('sideMenu');
    const menuOverlay = document.getElementById('menuOverlay');
    if (sideMenu && sideMenu.classList.contains('open')) {
        sideMenu.classList.remove('open');
        menuOverlay.classList.remove('open');
    }

    if (panel && overlay) {
        panel.classList.add('open');
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}

function closeDonPanel() {
    const panel = document.getElementById('donPanel');
    const overlay = document.getElementById('donOverlay');
    
    if (panel && overlay) {
        panel.classList.remove('open');
        overlay.classList.remove('open');
        document.body.style.overflow = '';
    }
}

// Close when clicking overlay
document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('donOverlay');
    if (overlay) {
        overlay.addEventListener('click', closeDonPanel);
    }
});
