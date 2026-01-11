// static/js/doctor_dashboard.js
document.addEventListener('DOMContentLoaded', function () {
    console.log('Doctor Dashboard JS Loaded');

    // 1. Apply Button - AJAX Apply (no page reload)
    const applyButtons = document.querySelectorAll('.apply-btn');
    applyButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const shiftId = this.dataset.shiftId;
            const url = `/doctor/apply/${shiftId}`;

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Application submitted successfully!', 'success');
                    this.textContent = 'Applied';
                    this.disabled = true;
                    this.style.background = '#28a745';
                } else {
                    showAlert(data.message || 'Something went wrong', 'error');
                }
            })
            .catch(err => {
                showAlert('Network error. Try again.', 'error');
            });
        });
    });

    // 2. Simple Alert Function (no external library)
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        document.querySelector('.main').insertBefore(alertDiv, document.querySelector('.main').firstChild);

        // Auto remove after 5 seconds
        setTimeout(() => {
            alertDiv.style.opacity = '0';
            setTimeout(() => alertDiv.remove(), 500);
        }, 5000);
    }

    // 3. Filters (Specialty, Pay Range) - Client side filtering
    const filterSpecialty = document.getElementById('filter-specialty');
    const filterPay = document.getElementById('filter-pay');
    const jobRows = document.querySelectorAll('.job-row');

    if (filterSpecialty || filterPay) {
        function filterJobs() {
            const specialty = filterSpecialty ? filterSpecialty.value.toLowerCase() : '';
            const minPay = filterPay ? parseFloat(filterPay.value) || 0 : 0;

            jobRows.forEach(row => {
                const rowSpecialty = row.dataset.specialty.toLowerCase();
                const rowPay = parseFloat(row.dataset.pay);

                const matchesSpecialty = specialty === '' || rowSpecialty.includes(specialty);
                const matchesPay = rowPay >= minPay;

                row.style.display = matchesSpecialty && matchesPay ? '' : 'none';
            });
        }

        if (filterSpecialty) filterSpecialty.addEventListener('change', filterJobs);
        if (filterPay) filterPay.addEventListener('input', filterJobs);
    }

    // 4. Success message fade out (from flash)
    const flashAlerts = document.querySelectorAll('.alert-success, .alert-error');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});