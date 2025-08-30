// Wacht tot de DOM volledig geladen is voordat scripts worden uitgevoerd
document.addEventListener('DOMContentLoaded', async () => {
    // Referentie naar het formulier
    const qrScanForm = document.getElementById('qr-scan-form');
    // Geen Firebase-instanties meer nodig: let db, auth, userId; 

    // Functie om berichten weer te geven (vervangt alert)
    const displayMessage = (type, message) => {
        const messageContainer = document.getElementById('message-container');
        if (!messageContainer) {
            console.warn('Message container niet gevonden, gebruik alert als fallback.');
            alert(message);
            return;
        }
        messageContainer.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    };

    // Functie om URL-parameters te parsen
    const getUrlParams = () => {
        const params = {};
        const queryString = window.location.search;
        console.log("Huidige URL Query String:", queryString); // Debugging
        const urlParams = new URLSearchParams(queryString);
        
        for (const [key, value] of urlParams.entries()) {
            params[key] = value;
        }
        console.log("Geparseerde URL Parameters:", params); // Debugging
        return params;
    };

    // Haal de parameters op uit de URL
    const params = getUrlParams();

    // Vul de formuliervelden met de ontvangen parameters (altijd uitvoeren)
    // Certificaat gegevens
    if (params.cursusNaam) {
        document.getElementById('scannedCursusNaam').value = decodeURIComponent(params.cursusNaam);
        console.log("CursusNaam ingevuld:", decodeURIComponent(params.cursusNaam)); // Debugging
    } else {
        console.log("CursusNaam parameter niet gevonden."); // Debugging
    }
    if (params.cursusdatum) {
        document.getElementById('scannedCursusdatum').value = decodeURIComponent(params.cursusdatum);
        console.log("Cursusdatum ingevuld:", decodeURIComponent(params.cursusdatum)); // Debugging
    } else {
        console.log("Cursusdatum parameter niet gevonden."); // Debugging
    }
    if (params.geldigheidJaren) {
        document.getElementById('scannedGeldigheid').value = decodeURIComponent(params.geldigheidJaren) + ' jaar';
        console.log("GeldigheidJaren ingevuld:", decodeURIComponent(params.geldigheidJaren)); // Debugging
    } else {
        console.log("GeldigheidJaren parameter niet gevonden."); // Debugging
    }
    if (params.refresher === 'true') {
        document.getElementById('scannedRefresher').checked = true;
        console.log("Refresher ingesteld op true."); // Debugging
    } else {
        console.log("Refresher parameter niet gevonden of is niet 'true'."); // Debugging
    }

    // --- Geen Firebase Initialisatie en Authenticatie meer ---
    // De blokken voor Firebase-initialisatie en authenticatie zijn verwijderd.

    // Event listener voor het versturen van het formulier
    qrScanForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Voorkom standaard formulierinzending

        // De checks voor 'db' en 'userId' zijn verwijderd, omdat we geen Firebase meer gebruiken.

        // Verzamel alle gegevens van het formulier
        const formData = {
            cursusNaam: document.getElementById('scannedCursusNaam').value,
            cursusdatum: document.getElementById('scannedCursusdatum').value,
            geldigheidJaren: document.getElementById('scannedGeldigheid').value.replace(' jaar', ''), // Verwijder ' jaar' voor opslag
            refresher: document.getElementById('scannedRefresher').checked,
            aanhef: document.querySelector('input[name="aanhef"]:checked')?.value || '',
            voornaam: document.getElementById('voornaam').value,
            tussenvoegsel: document.getElementById('tussenvoegsel').value,
            achternaam: document.getElementById('achternaam').value,
            bedrijfsnaam: document.getElementById('bedrijfsnaam').value,
            email: document.getElementById('email').value,
            geboortedatum: document.getElementById('geboortedatum').value,
            windaId: document.getElementById('windaId').value,
            telefoonnummer: document.getElementById('telefoonnummer').value
            // createdAt: serverTimestamp(), // Niet meer nodig zonder Firestore
            // scannedByUserId: userId,      // Niet meer nodig zonder Firebase Auth
            // appId: typeof __app_id !== 'undefined' ? __app_id : 'default-app-id' // Niet direct meer nodig, tenzij voor API
        };

        console.log('Gegevens om naar backend te versturen:', formData);

        // TODO: Hier komt de logica om de gegevens naar je Django-backend API te sturen.
        // Dit is nu een placeholder.
        try {
            // Voorbeeld van een fetch-request naar een fictieve Django API:
            const response = await fetch('http://JOUW_DJANGO_IP:8001/api/certificaten/', { // Pas de URL aan naar jouw Django API endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Voeg hier eventuele CSRF-token of authenticatieheaders toe indien nodig voor Django
                    // 'X-CSRFToken': getCookie('csrftoken'), // Als je CSRF bescherming hebt ingeschakeld
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Registratie succesvol:', result);
                displayMessage('success', 'Certificaat succesvol geregistreerd! (Verstuurd naar Django backend)');
                
                // Optioneel: reset het formulier of stuur de gebruiker door
                document.getElementById('aanhefDhr').checked = false;
                document.getElementById('aanhefMevr').checked = false;
                document.getElementById('voornaam').value = '';
                document.getElementById('tussenvoegsel').value = '';
                document.getElementById('achternaam').value = '';
                document.getElementById('bedrijfsnaam').value = '';
                document.getElementById('email').value = '';
                document.getElementById('geboortedatum').value = '';
                document.getElementById('windaId').value = '';
                document.getElementById('telefoonnummer').value = '';
            } else {
                const errorData = await response.json();
                console.error('Fout bij het versturen van gegevens naar Django:', errorData);
                displayMessage('error', `Fout bij registratie: ${errorData.message || 'Onbekende fout'}. Probeer het opnieuw.`);
            }

        } catch (error) {
            console.error('Netwerkfout of onverwachte fout bij versturen gegevens:', error);
            displayMessage('error', `Er is een netwerkfout opgetreden bij de registratie. Zorg ervoor dat de Django-server draait en bereikbaar is. ${error.message}`);
        }
    });
});

// Functie om CSRF-token uit cookies te halen (indien nodig voor Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
