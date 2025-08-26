// Wacht tot de DOM volledig geladen is voordat scripts worden uitgevoerd
document.addEventListener('DOMContentLoaded', () => {
    // Referentie naar het formulier voor QR-code generatie
    const qrGeneratorForm = document.getElementById('qr-generator-form');
    // Referentie naar de div waar de QR-code in de modal getoond zal worden
    const qrcodeInModalDiv = document.getElementById('qrcodeInModal');
    // Referentie naar de Bootstrap modal instantie
    const qrCodeModalElement = document.getElementById('qrCodeModal');
    const qrCodeModal = new bootstrap.Modal(qrCodeModalElement); // Initialiseer Bootstrap Modal
    // Referenties naar de opslaan en delen knoppen
    const saveQrCodeBtn = document.getElementById('saveQrCodeBtn');
    const shareQrCodeBtn = document.getElementById('shareQrCodeBtn');
    // Referentie naar de directe link in de modal
    const directLink = document.getElementById('directLink'); 

    let generatedQrCodeCanvas = null; // Variabele om de gegenereerde QR code canvas bij te houden

    // Voeg een event listener toe voor het submit-event van het formulier
    qrGeneratorForm.addEventListener('submit', (event) => {
        // Voorkom de standaard formulierinzending, zodat de pagina niet herlaadt
        event.preventDefault();

        // Verzamel de ingevoerde gegevens uit het formulier
        const cursusNaam = document.getElementById('qrCursus').value;
        const cursusdatum = document.getElementById('qrCursusdatum').value;
        const geldigheidJaren = document.getElementById('qrGeldigheid').value;
        const refresherCheck = document.getElementById('qrRefresherCheck').checked;

        // Controleer of de verplichte velden zijn ingevuld
        if (!cursusNaam || !cursusdatum) {
            alert('Vul alstublieft de cursusnaam en cursusdatum in.');
            return;
        }

        // De basis-URL is nu vast ingesteld op het opgegeven IP-adres en poort.
        // Dit zorgt ervoor dat de QR-code altijd naar deze HTTP-server verwijst,
        // ongeacht hoe de qr-code-generator.html pagina zelf wordt geopend (file:// of localhost).
        const baseUrl = 'http://192.168.1.161:8001/qr-scan-form.html';

        // Maak een URLSearchParams object om de gegevens als query parameters toe te voegen
        const params = new URLSearchParams();
        params.append('cursusNaam', cursusNaam);
        params.append('cursusdatum', cursusdatum);
        
        // Voeg geldigheid alleen toe als er een waarde is gekozen
        if (geldigheidJaren) {
            params.append('geldigheidJaren', geldigheidJaren);
        }
        
        // Voeg refresher toe als de checkbox is aangevinkt
        if (refresherCheck) {
            params.append('refresher', 'true');
        }

        // Construeer de volledige URL met alle parameters
        const fullUrl = `${baseUrl}?${params.toString()}`;

        // Leeg de vorige QR-code in de modal, indien aanwezig
        qrcodeInModalDiv.innerHTML = '';
        generatedQrCodeCanvas = null; // Reset de canvas referentie

        // Initialiseer de QR-code generator en plaats deze in de modal div
        const qrcode = new QRCode(qrcodeInModalDiv, {
            text: fullUrl, // De URL die in de QR-code gecodeerd wordt
            width: 256,    // Breedte van de QR-code
            height: 256,   // Hoogte van de QR-code
            colorDark : "#000000",
            colorLight : "#ffffff",
            correctLevel : QRCode.CorrectLevel.H // Correctieniveau (L, M, Q, H)
        });

        // Wacht tot de QR code is gerenderd om de canvas te pakken
        setTimeout(() => {
            generatedQrCodeCanvas = qrcodeInModalDiv.querySelector('canvas');
            if (generatedQrCodeCanvas) {
                // Vul de directe link in
                directLink.href = fullUrl;
                directLink.textContent = fullUrl; // Toon de volledige URL als tekst van de link
                qrCodeModal.show();
            } else {
                console.error("QR Code canvas niet gevonden na generatie.");
            }
        }, 100); 

        console.log("QR Code gegenereerd met URL:", fullUrl);
    });

    // Functie om de QR-code op te slaan
    saveQrCodeBtn.addEventListener('click', () => {
        if (generatedQrCodeCanvas) {
            const imageData = generatedQrCodeCanvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.href = imageData;
            link.download = 'safetypro-qrcode.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            console.error("Geen QR Code om op te slaan.");
            alert("Er is geen QR-code gegenereerd om op te slaan.");
        }
    });

    // Functie om de QR-code te delen
    shareQrCodeBtn.addEventListener('click', () => {
        if (generatedQrCodeCanvas) {
            if (navigator.share) {
                generatedQrCodeCanvas.toBlob((blob) => {
                    const file = new File([blob], 'safetypro-qrcode.png', { type: 'image/png' });
                    navigator.share({
                        title: 'SafetyPro QR Code',
                        text: 'Scan deze QR code voor certificaat registratie!',
                        files: [file],
                    }).catch((error) => {
                        console.error('Delen mislukt:', error);
                        alert('Delen is mislukt of geannuleerd.');
                    });
                }, 'image/png');
            } else {
                alert('Deel functionaliteit wordt niet ondersteund in deze browser. Sla de QR-code op en deel deze handmatig.');
            }
        } else {
            console.error("Geen QR Code om te delen.");
            alert("Er is geen QR-code gegenereerd om te delen.");
        }
    });
});
