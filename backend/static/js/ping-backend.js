function pingBackend() {
    fetch('http://127.0.0.1:8000/api/v1/ping/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Netwerkrespons was niet ok');
            }
            return response.json();
        })
        .then(data => {
            alert(data.status); // <-- Deze regel is aangepast
        })
        .catch(error => {
            alert('Fout: De backend is niet bereikbaar.');
        });
}