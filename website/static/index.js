function deleteNote(noteId) {
    fetch('/delete-note', {
        method: 'POST',
        body: JSON.stringify({ "noteId": noteId }),  // Send the note ID to the server
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())  // Parse JSON response
    .then(data => {
        if (data.success) {
            let noteElement = document.getElementById('note-' + noteId);
            if (noteElement) {
                noteElement.remove();  // Remove from UI
            }
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting note!');
    });
}