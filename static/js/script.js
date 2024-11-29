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

function checkInitial() {
    var initialBar = document.querySelector(".initialbar");
    var subBar = document.querySelector(".subbar");
    var bigBody = document.querySelector(".bigbody");
    var subBarChildren = subBar.children;
    
    for (var i = 0; i < subBarChildren.length; i++) {
        if (subBarChildren[i] !== initialBar) {
            subBarChildren[i].style.display = "none";
        }
    }

    initialBar.style.display = (initialBar.style.display === "block") ? "none" : "block";
    subBar.style.display = initialBar.style.display
}

function checkChange() {
    var changeBody = document.querySelector(".changebody");
    var subBar = document.querySelector(".subbar");
    var bigBody = document.querySelector(".bigbody");

    subBar.style.display = "none";
    
    var bigBodyChildren = bigBody.children;
    for (var i = 0; i < bigBodyChildren.length; i++) {
        if (bigBodyChildren[i] !== changeBody) {
            bigBodyChildren[i].style.display = "none";
        }
    }

    var subBarChildren = subBar.children;
    for (var i = 0; i < subBarChildren.length; i++) {
        subBarChildren[i].style.display = "none";
    }

    changeBody.style.display = (changeBody.style.display === "block") ? "none" : "block";
}

function checkManual() {
    var manualBar = document.querySelector(".manualbar");
    var subBar = document.querySelector(".subbar");
    var bigBody = document.querySelector(".bigbody");
    var subBarChildren = subBar.children;

    for (var i = 0; i < subBarChildren.length; i++) {
        if (subBarChildren[i] !== manualBar) {
            subBarChildren[i].style.display = "none";
        }
    }

    manualBar.style.display = (manualBar.style.display === "block") ? "none" : "block";
    subBar.style.display = manualBar.style.display
}

function checkPicks() {
    var picksBody = document.querySelector(".picksbody");
    var subBar = document.querySelector(".subbar");
    var bigBody = document.querySelector(".bigbody");

    subBar.style.display = "none";
    
    var bigBodyChildren = bigBody.children;
    for (var i = 0; i < bigBodyChildren.length; i++) {
        if (bigBodyChildren[i] !== picksBody) {
            bigBodyChildren[i].style.display = "none";
        }
    }

    var subBarChildren = subBar.children;
    for (var i = 0; i < subBarChildren.length; i++) {
        subBarChildren[i].style.display = "none";
    }

    picksBody.style.display = (picksBody.style.display === "block") ? "none" : "block";
}

function checkInitialize() {
    var initialBody = document.querySelector(".initialbody");
    var subBar = document.querySelector(".subbar");
    var bigBody = document.querySelector(".bigbody");

    subBar.style.display = "none";
    
    var bigBodyChildren = bigBody.children;
    for (var i = 0; i < bigBodyChildren.length; i++) {
        if (bigBodyChildren[i] !== initialBody) {
            bigBodyChildren[i].style.display = "none";
        }
    }

    var subBarChildren = subBar.children;
    for (var i = 0; i < subBarChildren.length; i++) {
        subBarChildren[i].style.display = "none";
    }

    initialBody.style.display = (initialBody.style.display === "block") ? "none" : "block";
}

function checkRules() {
    var rulesBody = document.querySelector(".rulesbody");
    var subBar = document.querySelector(".subbar");
    var bigBody = document.querySelector(".bigbody");

    subBar.style.display = "none";
    
    var bigBodyChildren = bigBody.children;
    for (var i = 0; i < bigBodyChildren.length; i++) {
        if (bigBodyChildren[i] !== rulesBody) {
            bigBodyChildren[i].style.display = "none";
        }
    }

    var subBarChildren = subBar.children;
    for (var i = 0; i < subBarChildren.length; i++) {
        subBarChildren[i].style.display = "none";
    }

    rulesBody.style.display = (rulesBody.style.display === "block") ? "none" : "block";
}

function checkAll() {
    var allBody = document.querySelector(".allbody");
    var subBar = document.querySelector(".subbar");
    var bigBody = document.querySelector(".bigbody");

    subBar.style.display = "none";
    
    var bigBodyChildren = bigBody.children;
    for (var i = 0; i < bigBodyChildren.length; i++) {
        if (bigBodyChildren[i] !== allBody) {
            bigBodyChildren[i].style.display = "none";
        }
    }

    var subBarChildren = subBar.children;
    for (var i = 0; i < subBarChildren.length; i++) {
        subBarChildren[i].style.display = "none";
    }

    allBody.style.display = (allBody.style.display === "block") ? "none" : "block";
}

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

const user = "{{ user }}";

function toggleActionBar() {
    var actionBar = document.querySelector(".actionbar");
    var bigBody = document.querySelector(".bigbody");
    var topBar = document.querySelector(".top-bar");
    
    var bigBodyChildren = bigBody.children;
    for (var i = 0; i < bigBodyChildren.length; i++) {
        if (bigBodyChildren[i] !== allBody) {
            bigBodyChildren[i].style.display = "none";
        }
    }

    var subBarChildren = subBar.children;
    for (var i = 0; i < subBarChildren.length; i++) {
        subBarChildren[i].style.display = "none";
    }

    bigBody.style.display = "none"
    actionBar.style.display = (actionBar.style.display === "block") ? "none" : "block";
    topBar.style.display = (actionBar.style.display === "block") ? "block" : "fixed";
}