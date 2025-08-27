function pingBackend() {
    // Functie om de verbinding met de backend te testen
    fetch('http://127.0.0.1:8000/api/v1/ping/')
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Toon een melding als de verbinding succesvol is
    })
    .catch(error => {
        alert('Fout: De backend is niet bereikbaar.'); 
    });
}