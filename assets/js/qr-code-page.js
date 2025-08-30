// In qr-code-page.js

document.addEventListener('DOMContentLoaded', () => {
    // Haal de query parameters uit de URL
    const urlParams = new URLSearchParams(window.location.search);
    const cursusNaam = urlParams.get('cursusNaam');
    const cursusdatum = urlParams.get('cursusdatum');

    if (cursusNaam && cursusdatum) {
        // Bouw de URL die in de QR-code gecodeerd wordt
        const qrUrl = `http://192.168.1.161:8001/qr-scan-form.html?cursusNaam=${encodeURIComponent(cursusNaam)}&cursusdatum=${cursusdatum}`;

        // Genereer de QR-code
        const qrcodeContainer = document.getElementById('qrcodeDisplay');
        qrcodeContainer.innerHTML = '';
        const qrcode = new QRCode(qrcodeContainer, {
            text: qrUrl,
            width: 256,
            height: 256,
            colorDark: "#000000",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H
        });

        // Update de link
        const directLink = document.getElementById('directLink');
        directLink.href = qrUrl;
        directLink.textContent = qrUrl;

        console.log("QR Code gegenereerd met URL:", qrUrl);
    } else {
        // Toon een foutmelding als de gegevens ontbreken
        const mainContent = document.querySelector('.container');
        if (mainContent) {
            mainContent.innerHTML = '<p class="text-center text-danger">Fout: Cursusgegevens ontbreken.</p>';
        }
    }
});

// Functie voor het opslaan van de QR-code
const saveQrCode = () => {
    const qrcodeContainer = document.getElementById('qrcodeDisplay');
    const canvas = qrcodeContainer.querySelector('canvas');
    if (canvas) {
        const imageData = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = imageData;
        link.download = 'safetypro-qrcode.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } else {
        alert("Geen QR Code om op te slaan.");
    }
};

// Functie voor het delen van de QR-code
const shareQrCode = () => {
    const qrcodeContainer = document.getElementById('qrcodeDisplay');
    const canvas = qrcodeContainer.querySelector('canvas');
    if (canvas && navigator.share) {
        canvas.toBlob((blob) => {
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
};