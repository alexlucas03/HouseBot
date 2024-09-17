function changeOwner(dishDate, dishType) {
    const userName = document.getElementById('user-name').value;

    if (!userName) {
        alert("Please enter your name before changing the owner.");
        return;
    }

    const data = {
        date: dishDate,
        type: dishType,
        owner: userName
    };

    fetch('/change-owner', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error('Error in request: ' + text);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);  // Log the error to the console
        alert('There was an error: ' + error.message);  // Show a user-friendly error message
    });
}
