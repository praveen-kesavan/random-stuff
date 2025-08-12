try {
const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

app.post('/book-ticket', (req, res) => {
    const { train, from, to, date, passenger } = req.body;

    // Basic validation
    if (!train || !from || !to || !date || !passenger) {
        return res.status(400).json({ message: 'All fields are required!' });
    }

    // Simulate successful booking
    res.status(200).json({
        message: `Ticket booked successfully for ${passenger} passenger(s) on train "${train}" from "${from}" to "${to}" on "${date}".`,
    });
});

// Start server
const PORT = 3000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
} catch (err) {
    res.status(500).json({ message: 'Internal Server Error' });
}

