// static/js/hospital_dashboard.js
document.addEventListener('DOMContentLoaded', function () {
    // Auto calculate duration if start and end time filled (create_shift page)
    const startTime = document.getElementById('start_time');
    const endTime = document.getElementById('end_time');

    if (startTime && endTime) {
        function calculateDuration() {
            if (startTime.value && endTime.value) {
                const start = new Date(`2000-01-01T${startTime.value}`);
                const end = new Date(`2000-01-01T${endTime.value}`);
                let diff = (end - start) / (1000 * 60 * 60);
                if (diff < 0) diff += 24; // for overnight shifts
                console.log(`Duration: ${diff.toFixed(1)} hours`);
                // Future mein duration field auto fill kar sakte ho
            }
        }

        startTime.addEventListener('change', calculateDuration);
        endTime.addEventListener('change', calculateDuration);
    }

    // Success message fade out
    const alerts = document.querySelectorAll('.alert-success, .alert-error');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});