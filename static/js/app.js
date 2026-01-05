// Persian date converter
document.addEventListener('DOMContentLoaded', function() {
    const dateElements = document.querySelectorAll('.persian-date');
    dateElements.forEach(el => {
        const dateStr = el.getAttribute('data-date');
        if (dateStr) {
            try {
                const date = new Date(dateStr);
                const persianDate = date.toLocaleDateString('fa-IR');
                el.textContent = persianDate;
            } catch (e) {
                el.textContent = dateStr;
            }
        }
    });

    // Confirm delete
    const deleteButtons = document.querySelectorAll('.confirm-delete');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('آیا مطمئن هستید؟')) {
                e.preventDefault();
            }
        });
    });
});
