// Wacht tot de DOM volledig geladen is voordat scripts worden uitgevoerd
document.addEventListener('DOMContentLoaded', async () => {
    // Referentie naar het formulier
    const qrScanForm = document.getElementById('qr-scan-form');

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

    // Functie om URL-parameters te parsen en formulier te vullen
    const getUrlParamsAndFillForm = () => {
        const urlParams = new URLSearchParams(window.location.search);
        const params = {};
        for (const [key, value] of urlParams.entries()) {
            params[key] = value;
        }

        if (params.cursusNaam) {
            const cursusNaamElement = document.getElementById('scannedCursusNaam');
            if (cursusNaamElement) {
                cursusNaamElement.value = decodeURIComponent(params.cursusNaam);
            }
        }
        if (params.cursusdatum) {
            const cursusDatumElement = document.getElementById('scannedCursusdatum');
            if (cursusDatumElement) {
                cursusDatumElement.value = decodeURIComponent(params.cursusdatum);
            }
        }
    };
    
    getUrlParamsAndFillForm();

    if (qrScanForm) {
        qrScanForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            // Gebruik de FormData API om alle velden veilig te verzamelen
            const formData = new FormData(qrScanForm);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            console.log('Gegevens om naar backend te versturen:', data);

            try {
                // Pas de URL aan naar jouw Django API endpoint
                const response = await fetch('/api/v1/qr-deelnemer-event/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log('Registratie succesvol:', result);
                    displayMessage('success', 'Certificaat succesvol geregistreerd! (Verstuurd naar Django backend)');
                    qrScanForm.reset();
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
    }
});