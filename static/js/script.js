function changeOwner(month, id) {
    const data = {
        month: month,
        id: id,
        owner: user,
    };

    fetch('/change-owner', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

function unclaim(month, id) {
    const data = {
        month: month,
        id: id,
        owner: null,
    };

    fetch('/change-owner', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

const user = "{{ user }}";

const addRowButton = document.querySelector('.add-row-button');
const peopleTableBody = document.getElementById('people-table-body');

addRowButton.addEventListener('click', () => {
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td><input type="text" name="name[]"></td>
        <td><input type="text" name="userid[]"></td>
    `;
    peopleTableBody.appendChild(newRow);
});

const deleteRowButton = document.querySelector('.delete-row-button');

deleteRowButton.addEventListener('click', () => {
    console.log("trying to delete row");
    const rows = peopleTableBody.querySelectorAll('tr');
    console.log(rows);
    console.log(rows.length);  // Fix the typo here
    if (rows.length > 1) { // Don't delete the last row if it's the only one (header row included)
        const lastRow = rows[rows.length - 1];
        console.log(lastRow);
        lastRow.remove();
    }
});



