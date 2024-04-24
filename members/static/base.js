document.addEventListener('DOMContentLoaded', function () {
    // Find all flash messages and set timeout for each
    const messages = document.querySelectorAll('.flash-message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.display = 'none';
        }, 3000); // Message disappears after 3seconds
    });
});
