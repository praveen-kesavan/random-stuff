// app.js
// document.addEventListener("DOMContentLoaded", () => {
//     const habitForm = document.getElementById("habit-form");
//     const habitList = document.getElementById("habit-list");

    // Add habit to the list
    // habitForm.addEventListener("submit", (event) => {
    //     event.preventDefault();
    //     const habitInput = document.getElementById("habit");
    //     const habit = habitInput.value;

    //     if (habit) {
    //         console.log("Adding habit:", habit);
    //         const listItem = document.createElement("li");
    //         listItem.textContent = habit;
    //         habitList.appendChild(listItem);
    //         habitInput.value = ""; // Clear input field
    //     }
    // });
// });
let habits = [];
let deletedHabit = null;
let deletedIndex = null;

document.addEventListener("DOMContentLoaded", () => {
    const habitForm = document.getElementById("habit-form");
    const habitList = document.getElementById("habit-list");
    

    // Fetch and display habits from the server
    const loadHabits = () => {
        habitList.innerHTML = ""; // Clear current list
        fetch("http://localhost:4000/habits")
            .then(response => response.json())
            .then(data => {
                data.forEach((habit, index) => {
                    const listItem = document.createElement("li");
                    listItem.style.display = "flex"; // Use flexbox for layout
                    listItem.style.alignItems = "center"; // Align items vertically
                    
                    // Add habit text
                    const habitText = document.createElement("span");
                    habitText.textContent = habit;
                    habitText.style.flex = "1"; // Allow habit text to take up available space
                    listItem.appendChild(habitText);
    
                    // Add delete button
                    const deleteButton = document.createElement("button");
                    deleteButton.textContent = "Delete";
                    deleteButton.style.marginLeft = "10px";
                    deleteButton.style.backgroundColor = "#e76f51";
                    deleteButton.style.color = "white";
                    deleteButton.style.border = "none";
                    deleteButton.style.padding = "5px 10px";
                    deleteButton.style.borderRadius = "3px";
                    deleteButton.style.cursor = "pointer";
                    deleteButton.addEventListener("click", () => deleteHabit(index));
                    listItem.appendChild(deleteButton);
    
                    // Add checkbox
                    const checkbox = document.createElement("input");
                    checkbox.type = "checkbox";
                    checkbox.id = habit;
                    checkbox.style.marginLeft = "10px";
                    checkbox.addEventListener("change", handleCheckboxChange);
                    listItem.appendChild(checkbox);
    
                    // Append the list item to the habit list
                    habitList.appendChild(listItem);
                });
            });
    };
    

    // Add a new habit
    habitForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const habitInput = document.getElementById("habit");
        const habit = habitInput.value;

        if (habit) {
            //console.log("Adding habit:", habit);
            fetch("http://localhost:4000/habits", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ habit }),
            })
                .then(response => response.json())
                .then(() => {
                    habitInput.value = ""; // Clear input field
                    loadHabits(); // Refresh habit list
                });
        }
    });

    // Delete a habit
    const deleteHabit = (index) => {
        fetch("http://localhost:4000/habits/delete", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({index})
        })
        .then(response => response.json())
        .then(data => {
            deletedHabit = data.deletedHabit;
            //console.log("Deleted Habit",deletedHabit);
            deletedIndex = index;
            loadHabits();
            undoButton.style.display = "block";
        })
            };
        
        const undoButton = document.getElementById("undo");
        undoButton.addEventListener("click", () => {
            console.log("Undo button clicked");
            fetch("http://localhost:4000/habits/undo", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ deletedHabit}),
        })
        .then(response => response.json())
        .then(data => {
            habits = data.habits;
            loadHabits();
            undoButton.style.display = "none";
        })
        .catch(error => console.error("Error undoing habit deletion:", error));
    })

    // Handle checkbox 
    function handleCheckboxChange(event) {
        if (event.target.checked) {
            message.style.display = 'block'; // Show appreciation message
            setTimeout(() => {
                message.style.display = 'none';
              }, 2500);
        } else {
            message.style.display = 'none'; // Hide message if unchecked
        }

        }

    // Initial load of habits
    loadHabits();
});
