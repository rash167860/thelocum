// static/js/auth-login.js
document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.user-type-btn');
    let selectedType = 'doctor'; // Default

    // Toggle user type buttons
    buttons.forEach(button => {
        button.addEventListener('click', function () {
            buttons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            selectedType = this.getAttribute('data-type');
        });
    });

    // Form submit with Fetch API
    const form = document.getElementById('loginForm');
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const errorMessage = document.getElementById('errorMessage');

        if (!email || !password) {
            errorMessage.textContent = 'Please fill all fields';
            errorMessage.classList.add('show');
            return;
        }

        // Add hidden field for user_type (backend ko pata chale doctor ya hospital)
        let userTypeInput = form.querySelector('input[name="user_type"]');
        if (!userTypeInput) {
            userTypeInput = document.createElement('input');
            userTypeInput.type = 'hidden';
            userTypeInput.name = 'user_type';
            form.appendChild(userTypeInput);
        }
        userTypeInput.value = selectedType;

        const formData = new FormData(form);

        fetch('/login', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(html => {
            if (html.includes('dashboard')) {
                window.location.href = '/dashboard';
            } else {
                // Error flash message ko parse karne ke bajaye page reload (simple way)
                window.location.reload();
            }
        })
        .catch(err => {
            errorMessage.textContent = 'Network error. Try again.';
            errorMessage.classList.add('show');
        });
    });
});