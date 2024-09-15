var ably = new Ably.realtime('LHdIAA.QQSKMw:Xp_PCWf9v7fwdQFm8w3Z1kxP7YHnyj3DBEZ1-6k1YNo');
var channel = ably.channels.get('call-updates');

document.getElementById('issueForm').addEventListener('change', function(event) {
    event.preventDefault();
    const textarea = document.getElementById('issue');
    const issueText = textarea.value.trim();

    fetch('/issue', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ issue: issueText })
    })
    .then(data => {
        document.getElementById('issueDisplay').textContent = issueText;
    });
});

document.getElementById('uploadForm').addEventListener('change', function(event) {
    event.preventDefault();
    
    const fileInput = document.querySelector('input[name="upload"]');
    
    if (fileInput.files.length > 0) {
        const formData = new FormData();
        formData.append('upload', fileInput.files[0]);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(data => {
        document.getElementById('fileDisplay').textContent = fileInput.files[0].name;
      });
        
    } else {
        alert("Please select a file before uploading.");
    }
});

document.getElementById('filterForm').addEventListener('change', function(event) {
    event.preventDefault();
    const select = document.getElementById('tagList');
    
    fetch('/filter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tag: select.value }),
    })
    .then(data => {
        document.getElementById('tagDisplay').textContent = select.value;
      });
});

document.getElementById('primForm').addEventListener('change', function(event) {
    event.preventDefault();
    const number = document.getElementById('num');
    const num = number.value

    fetch('/prim', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prim_num: num })
    })
    .then(data => {
        document.getElementById('primDisplay').textContent = num;
      });
});

document.getElementById('secForm').addEventListener('change', function(event) {
    event.preventDefault();
    const number = document.getElementById('secNum');
    const secNum = number.value

    fetch('/sec', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sec_num: secNum })
    })
    .then(data => {
        document.getElementById('secDisplay').textContent = secNum;
      });
});

document.getElementById('startCalls').addEventListener('click', function() {
    fetch('/start-calls', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
});

document.getElementById('terminateCalls').addEventListener('click', function() {
    fetch('/terminate-calls', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
});

document.getElementById('logoutButton').addEventListener('click', function() {
    window.location.href = '/logout';
});

channel.subscribe('update', function(message) {
    var data = message.data;
    updateList('toCallList', data.to_call);
    updateList('callingList', data.calling);
    updateList('calledList', data.called);
    updateList('acceptedList', data.accepted);
    updateSelect('tagList', data.tags);
    document.getElementById('issueDisplay').textContent = data.custom_issue;
});

function updateList(elementId, items) {
    const list = document.getElementById(elementId);
    list.innerHTML = '';

    if (Array.isArray(items)) {
        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            list.appendChild(li);
        });
    } else {
        console.error(`Expected array but got ${typeof items} for ${elementId}`);
    }
}

function updateSelect(elementId, items) {
    const select = document.getElementById(elementId);
    const selectedTag = select.value;
    
    select.innerHTML = '';

    items.forEach(item => {
        const option = document.createElement('option');
        option.textContent = item;
        option.value = item;

        if (item === selectedTag) {
            option.selected = true;
        }

        select.appendChild(option);
    });
}

document.querySelectorAll('form').forEach(form => {
    form.addEventListener('click', function() {
        const input = this.querySelector('input, textarea, select, file');
        if (input) {
            input.focus();
        }
    });
});