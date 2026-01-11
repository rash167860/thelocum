// static/js/auth-register-hospital.js
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registerForm');
    const errorDiv = document.getElementById('errorMessage');
    const successDiv = document.getElementById('successMessage');

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const password = document.getElementById('password').value;
        const confirm = document.getElementById('confirmPassword').value;

        if (password !== confirm) {
            errorDiv.textContent = 'Passwords do not match!';
            errorDiv.classList.add('show');
            successDiv.classList.remove('show');
            return;
        }

        const formData = new FormData(form);

        fetch('/register-hospital', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.text();
            }
        })
        .then(data => {
            if (data && data.includes('already registered')) {
                errorDiv.textContent = 'Email already registered!';
                errorDiv.classList.add('show');
            }
        })
        .catch(err => {
            errorDiv.textContent = 'Something went wrong. Try again.';
            errorDiv.classList.add('show');
        });
    });
});