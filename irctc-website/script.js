document.getElementById('ticketForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        train: document.getElementById('train').value,
        from: document.getElementById('from').value,
        to: document.getElementById('to').value,
        date: document.getElementById('date').value,
        passenger: document.getElementById('passenger').value,
    };

    try {
        const response = await fetch('http://localhost:3000/book-ticket', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
        });

        const data = await response.json();
        const messageDiv = document.getElementById('responseMessage');
        messageDiv.style.display = 'block';
        messageDiv.textContent = data.message;

        if (response.ok) {
            messageDiv.className = 'response-message success';
        } else {
            messageDiv.className = 'response-message error';
        }
    } catch (error) {
        alert('An error occurred. Please try again.');
    }
});
