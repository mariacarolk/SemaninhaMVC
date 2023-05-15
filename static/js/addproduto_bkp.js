function addRow() {
    var template = document.getElementById('produtos-template');
    var index = parseInt(template.getAttribute('data-index')) || 0; // Parse the initial data-index as integer, default to 0 if NaN
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

    index++; // Increment the index
    template.setAttribute('data-index', index); // Update the data-index attribute
    document.getElementById('produtos').appendChild(clonedRow);
}

function removeRow(button) {
    var row = button.closest('tr');
    row.parentNode.removeChild(row);
}
