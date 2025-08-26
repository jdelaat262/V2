let savedCourseData = null; // Variabele om cursusgegevens tijdelijk op te slaan

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

document.addEventListener('DOMContentLoaded', function() {
    // Selecteer het hoofdformulier met de ID 'form-certificaat'
    const certificaatForm = document.getElementById('form-certificaat');
    
    // Als het formulier bestaat, voeg dan een event listener toe voor het 'submit' event
    if (certificaatForm) {
        certificaatForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Voorkom de standaard formulierinzending
            
            // Schakel de submit-knop uit om dubbele inzendingen te voorkomen
            const submitButton = certificaatForm.querySelector('button[type="submit"]');
            if (submitButton) submitButton.disabled = true;

            // --- Handmatig verzamelen van alle formuliergegevens ---
            // Dit omzeilt potentiële problemen met FormData die velden mist.
            const data = {
                // Cursusgegevens
                cursus: document.getElementById('cursus').value,
                cursusdatum: document.getElementById('cursusdatum').value || null,
                refreshercheck: document.getElementById('refreshercheck').checked, // Checkbox waarde
                'geldigheid-jaren': document.getElementById('geldigheid-jaren').value,
                'geldigheid-datum-input': document.getElementById('geldigheid-datum-input').value || null,

                // Deelnemersgegevens
                aanhef: certificaatForm.querySelector('input[name="aanhef"]:checked')?.value || '', // Radiobuttons
                voornaam: document.getElementById('voornaam').value,
                tussenvoegsel: document.getElementById('tussenvoegsel').value,
                achternaam: document.getElementById('achternaam').value,
                bedrijfsnaam: document.getElementById('bedrijfsnaam').value,
                email: document.getElementById('email').value,
                geboortedatum: document.getElementById('geboortedatum').value || null,
                telefoonnummer: document.getElementById('telefoonnummer').value, // Nieuw veld
                windaId: document.getElementById('windaId').value,
                // notes: document.getElementById('notes').value, // Voeg toe als je een 'notes' veld hebt in HTML
            };
            
            // Logica voor de 'vastzetten' checkbox
            const vastzettenCheck = document.getElementById('vastzettenCheck');

            if (vastzettenCheck && vastzettenCheck.checked) {
                // Als de checkbox is aangevinkt, sla dan de cursusgegevens op
                savedCourseData = {
                    cursus: data.cursus,
                    cursusdatum: data.cursusdatum,
                    refreshercheck: data.refresher, // Gebruik de reeds verwerkte boolean
                    'geldigheid-jaren': data['geldigheid-jaren'],
                    'geldigheid-datum-input': data['geldigheid-datum-input']
                };
            }

            // Verwerk de 'refresher' checkbox waarde naar een boolean
            // Dit is nu al gedaan bij het handmatig verzamelen, maar we zorgen dat de sleutel klopt
            data.refresher = !!data.refresher; // Zorgt dat het een boolean is

            // Converteer lege datumstrings naar null voor de backend
            // Dit is nu al gedaan bij het handmatig verzamelen, maar we zorgen dat het null is als leeg
            data.geboortedatum = data.geboortedatum === '' ? null : data.geboortedatum;
            data.cursusdatum = data.cursusdatum === '' ? null : data.cursusdatum;
            data['geldigheid-datum-input'] = data['geldigheid-datum-input'] === '' ? null : data['geldigheid-datum-input'];
            
            // Verwerk de geldigheid op basis van de dropdown of de custom input
            if (data['geldigheid-jaren'] === 'custom' && data['geldigheid-datum-input']) {
                 data.geldigheid_jaren = data['geldigheid-datum-input']; // Gebruik de custom datum
                 data.geldigheid_datum = data['geldigheid-datum-input']; // Sla de custom datum ook op in geldigheid_datum
            } else {
                 data.geldigheid_jaren = data['geldigheid-jaren']; // Gebruik de gekozen jaren
                 data.geldigheid_datum = null; // Als geen custom datum, dan is geldigheid_datum null
            }

            // Verwijder 'geldigheid-datum-input' als deze niet langer nodig is na verwerking
            delete data['geldigheid-datum-input'];
            
            // Stuur de verwerkte data naar de backend API
            fetch('http://127.0.0.1:8000/api/v1/certificaten/', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => {
                if (!response.ok) {
                    // Als de respons niet OK is, gooi een foutmelding
                    throw new Error('Netwerkrespons was niet ok');
                }
                return response.json(); // Parseer de JSON-respons
            })
            .then(responseData => {
                console.log('Succes! Data van de server:', responseData);
                alert('Formulier succesvol verzonden!');
                
                // Reset het formulier en herstel de vastgezette gegevens indien van toepassing
                if (vastzettenCheck && vastzettenCheck.checked && savedCourseData) {
                    certificaatForm.reset(); // Reset het hele formulier
                    // Herstel de vastgezette cursusgegevens
                    document.getElementById('cursus').value = savedCourseData.cursus;
                    document.getElementById('cursusdatum').value = savedCourseData.cursusdatum;
                    document.getElementById('refreshercheck').checked = !!savedCourseData.refreshercheck;
                    document.getElementById('geldigheid-jaren').value = savedCourseData['geldigheid-jaren'];
                    document.getElementById('vastzettenCheck').checked = true; // Houd de vastzetten-checkbox aangevinkt
                } else {
                    certificaatForm.reset(); // Reset het hele formulier als er niets is vastgezet
                }
            })
            .catch((error) => {
                console.error('Fout bij het versturen:', error);
                alert('Er is een fout opgetreden bij het verzenden.');
            })
            .finally(() => {
                if (submitButton) submitButton.disabled = false; // Schakel de knop weer in
            });
        });
    }

    // Logica voor het tonen/verbergen van de custom datum input
    const dropdown = document.getElementById('geldigheid-jaren');
    const datumInput = document.getElementById('geldigheid-datum-input');
    if (dropdown && datumInput) {
        dropdown.addEventListener('change', function() {
            if (this.value === 'custom') {
                datumInput.hidden = false; // Toon de custom datum input
            } else {
                datumInput.hidden = true; // Verberg de custom datum input
            }
        });
    }
});
