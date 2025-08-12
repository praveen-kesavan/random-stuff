// server.js
const express = require("express");
const app = express();
const cors = require("cors");

app.use(cors());
app.use(express.json());

const habits = []; // Temporary in-memory storage

// Fetch all habits
app.get("/habits", (req, res) => {
    res.json(habits);
});

// Add a new habit
app.post("/habits", (req, res) => {
    const { habit } = req.body;
    if (habit) {
        if (!habits.includes(habit)) {
            habits.push(habit);
            res.status(200).json({ message: "Habit added successfully!", habits });
        } else {
            res.status(400).json({ message: "Habit already exists" });
        }
    } else {
        res.status(400).json({ message: "Habit is required" });
    }
});

// Delete a habit by index
app.post("/habits/delete", (req, res) => {
    var {index} = req.body;
        const deletedHabit = habits.splice(index, 1); // Remove habit
        res.status(200).json({ message: "Habit deleted successfully!", deletedHabit: deletedHabit, deletedIndex : index });
    
});

// Undo a habit
app.post("/habits/undo", (req, res) => {
    const { deletedHabit } = req.body;
    if (deletedHabit) {
        if (!habits.includes(deletedHabit)) {
            habits.push(deletedHabit);
            res.status(200).json({ message: "Habit re-added successfully!", habits });
        } else {
            res.status(400).json({ message: "Habit already exists" });
        }
    } else {
        res.status(400).json({ message: "Habit is required" });
    }
});

const PORT = process.env.PORT || 4000; 
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});