function addRow() {
    var template = document.getElementById('produtos-template');
    var index = parseInt(template.getAttribute('data-index')) || 1; // Parse the initial data-index as integer, default to 0 if NaN
    template.setAttribute('data-index', index); // Update the data-index attribute
    var clonedRow = template.cloneNode(true);
    clonedRow.style.display = '';
    clonedRow.id = clonedRow.id.replace('template', index);

    // Update the name attributes in the cloned row
    var inputs = clonedRow.getElementsByTagName('input');
    var selects = clonedRow.getElementsByTagName('select');
    var textareas = clonedRow.getElementsByTagName('textarea');

    for (var i = 0; i < inputs.length; i++) {
        inputs[i].name = inputs[i].name.replace('0', index);
    }

    for (var i = 0; i < selects.length; i++) {
        selects[i].name = selects[i].name.replace('0', index);

    }
    for (var i = 0; i < textareas.length; i++) {
        textareas[i].name = textareas[i].name.replace('0', index);
    }

    index++;// Increment the index
    template.setAttribute('data-index', index); // Update the data-index attribute

    // Append the cloned row to the table
    document.getElementById('produtos').appendChild(clonedRow);

    // Send the form data to the server using AJAX
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'cardapio/novo_cardapio', true); // Update the URL to match your Flask view URL
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                // Handle the success response
                // You can update the UI or take other actions here
            } else {
                // Handle the error response
                // You can update the UI or take other actions here
            }
        }
    };
    xhr.send(new FormData(document.getElementById('cardapio-form')));
}

function removeRow(button) {
    var row = button.closest('tr');
    row.parentNode.removeChild(row);
}
