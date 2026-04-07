// Toggle visibilidad contraseña
document.addEventListener('DOMContentLoaded', function () {
    const toggleBtns = document.querySelectorAll('.btn-toggle-password');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const input = this.closest('.input-wrapper').querySelector('input');
            if (input.type === 'password') {
                input.type = 'text';
                this.querySelector('i').classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                this.querySelector('i').classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
    });

    // Auto-hide alerts after 4s
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });
});
