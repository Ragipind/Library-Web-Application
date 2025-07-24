// Any custom JS scripts
document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert");
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => alert.style.display = 'none');
        }, 3000);
    }
});
