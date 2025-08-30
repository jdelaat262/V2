document.addEventListener('DOMContentLoaded', () => {
    const qrGeneratorForm = document.getElementById('qr-generator-form');

    if (qrGeneratorForm) {
        qrGeneratorForm.addEventListener('submit', (event) => {
            event.preventDefault();

            const cursusNaam = qrGeneratorForm.querySelector('#qrCursus').value;
            const cursusdatum = qrGeneratorForm.querySelector('#qrCursusdatum').value;

            if (!cursusNaam || !cursusdatum) {
                alert('Vul alstublieft de cursusnaam en cursusdatum in.');
                return;
            }

            const baseUrl = `${window.location.origin}/qr-code-page.html`; // <-- Hier is de aanpassing
            const params = new URLSearchParams({
                cursusNaam: encodeURIComponent(cursusNaam), // <-- Hier is de aanpassing
                cursusdatum: cursusdatum
            });

            const fullUrl = `${baseUrl}?${params.toString()}`;

            // Redirect naar de nieuwe pagina met de correcte URL-parameters
            window.location.href = fullUrl;
        });
    }
});