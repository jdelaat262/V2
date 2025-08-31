document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const encodedData = urlParams.get('reminders');

    if (!encodedData) {
        document.getElementById('message-container').innerHTML = '<p class="alert alert-danger">Geen reminders geselecteerd.</p>';
        return;
    }

    const reminders = JSON.parse(atob(encodedData));
    window.selectedReminders = reminders; // Bewaar voor de finale verzending

    const fetchEmailPreview = async () => {
        try {
            const response = await fetch('/api/v1/preview-reminder-emails/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reminders })
            });

            if (response.ok) {
                const previewData = await response.json();
                document.getElementById('emailAddresses').value = previewData.emails.join(', ');
                document.getElementById('emailSubject').value = previewData.subject;
                document.getElementById('emailBody').value = previewData.body;
            } else {
                throw new Error('Kon geen e-mail preview ophalen.');
            }
        } catch (error) {
            console.error('Fout bij het ophalen van e-mail preview:', error);
            document.getElementById('message-container').innerHTML = `<p class="alert alert-danger">Fout: ${error.message}</p>`;
        }
    };
    
    // Roep de functie aan om de preview te laden
    await fetchEmailPreview();

    // Event listener voor de definitieve verzendknop
    const sendFinalBtn = document.getElementById('sendFinalBtn');
    if (sendFinalBtn) {
        sendFinalBtn.addEventListener('click', async () => {
            const customSubject = document.getElementById('emailSubject').value;
            const customBody = document.getElementById('emailBody').value;
            const finalEmails = document.getElementById('emailAddresses').value.split(',').map(e => e.trim());

            try {
                const response = await fetch('/api/v1/send-custom-reminders/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        reminders: window.selectedReminders,
                        subject: customSubject,
                        body: customBody,
                        emails: finalEmails
                    })
                });

                if (response.ok) {
                    const result = await response.json();
                    alert(`Reminders succesvol verstuurd naar ${finalEmails.length} adres(sen)!`);
                    window.location.href = '/reminders/'; // Terug naar de reminders-pagina
                } else {
                    throw new Error('Fout bij het versturen van reminders.');
                }
            } catch (error) {
                alert('Fout bij het versturen van reminders: ' + error.message);
            }
        });
    }
});