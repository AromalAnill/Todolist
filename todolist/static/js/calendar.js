/**
 * Calendar Application JavaScript
 * Handles calendar interactions, task management, and UI updates
 */

// Helper function to format dates
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Helper function to get today's date
function getTodayDate() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Disable past dates on calendar load
document.addEventListener('DOMContentLoaded', function() {
    const today = new Date(document.querySelector('[data-today]')?.getAttribute('data-today') || new Date());
    const dayElements = document.querySelectorAll('.day');
    
    dayElements.forEach(dayElement => {
        const dateStr = dayElement.getAttribute('data-date');
        const dateObj = new Date(dateStr);
        
        if (dateObj < today) {
            dayElement.classList.add('past');
            dayElement.style.cursor = 'not-allowed';
        }
    });
});

// Make calendar responsive
function makeCalendarResponsive() {
    const calendarContainer = document.querySelector('.calendar');
    if (window.innerWidth < 768) {
        calendarContainer.style.fontSize = '80%';
    } else {
        calendarContainer.style.fontSize = '100%';
    }
}

window.addEventListener('resize', makeCalendarResponsive);
window.addEventListener('load', makeCalendarResponsive);

// Keyboard navigation for accessibility
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = bootstrap.Modal.getInstance(document.getElementById('addTaskModal'));
        if (modal) {
            modal.hide();
        }
    }
});
