document.addEventListener('DOMContentLoaded', () => {
    const qrGeneratorForm = document.getElementById('qr-generator-form');

    if (qrGeneratorForm) {
        qrGeneratorForm.addEventListener('submit', (event) => {
            const cursusNaam = qrGeneratorForm.querySelector('#qrCursus').value;
            const cursusdatum = qrGeneratorForm.querySelector('#qrCursusdatum').value;

            if (!cursusNaam || !cursusdatum) {
                // Toon een melding als de validatie faalt
                alert('Vul alstublieft de cursusnaam en cursusdatum in.');
                event.preventDefault(); // Voorkom het verzenden van het formulier
            }
        });
    }
});