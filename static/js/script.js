function changeOwner(dishDate, dishType) {
    // Get the value of the user's name from the input field
    const user = document.getElementById('user-name').value;

    if (!user) {
        alert("Please enter your name.");
        return;
    }

    fetch('/change-owner', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ date: dishDate, type: dishType, owner: user })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();  // Reload the page to see the updated owner
        } else {
            console.error('Error updating owner:', data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
