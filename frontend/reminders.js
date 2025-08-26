document.addEventListener('DOMContentLoaded', function() {
    const scanRemindersBtn = document.getElementById('scanRemindersBtn');
    const remindersList = document.getElementById('remindersList');
    const loadingMessage = document.getElementById('loadingMessage');
    let sendReminderBtn = null; // Declareer de knop hier zodat deze toegankelijk is

    // Functie om de "Verstuur Reminders" knop te tonen/verbergen
    function toggleSendReminderButton() {
        const checkboxes = document.querySelectorAll('.reminder-checkbox');
        const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
        
        if (sendReminderBtn) { // Controleer of de knop al bestaat
            sendReminderBtn.style.display = anyChecked ? 'block' : 'none';
        }
    }

    if (scanRemindersBtn && remindersList) {
        scanRemindersBtn.addEventListener('click', function() {
            loadingMessage.textContent = 'Certificaten aan het scannen...';
            remindersList.innerHTML = ''; // Maak de lijst leeg bij een nieuwe scan
            if (sendReminderBtn) { // Verberg de knop bij een nieuwe scan
                sendReminderBtn.style.display = 'none';
            }

            fetch('http://127.0.0.1:8000/api/v1/expiring-certificates/')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Netwerkrespons was niet ok');
                    }
                    return response.json();
                })
                .then(data => {
                    loadingMessage.textContent = ''; // Verwijder laadbericht
                    if (data.length === 0) {
                        remindersList.innerHTML = '<p class="text-center text-success">Geen certificaten gevonden die binnenkort verlopen. Alles is up-to-date!</p>';
                    } else {
                        // Creëer een tabel om de resultaten weer te geven
                        const table = document.createElement('table');
                        table.classList.add('table', 'table-striped', 'table-hover', 'text-white');
                        table.innerHTML = `
                            <thead>
                                <tr>
                                    <th>Deelnemer</th>
                                    <th>E-mail</th>
                                    <th>Cursus</th>
                                    <th>Verloopdatum</th>
                                    <th>Kies</th>
                                </tr>
                            </thead>
                            <tbody>
                            </tbody>
                        `;
                        const tbody = table.querySelector('tbody');

                        data.forEach(item => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${item.deelnemer.voornaam || ''} ${item.deelnemer.tussenvoegsel || ''} ${item.deelnemer.achternaam || ''}</td>
                                <td>${item.deelnemer.email || ''}</td>
                                <td>${item.cursus.cursus || ''}</td>
                                <td>${item.verloopdatum || ''}</td>
                                <td><input type="checkbox" class="form-check-input reminder-checkbox" data-deelnemer-id="${item.deelnemer.id}" data-cursus-id="${item.cursus.id}"></td>
                            `;
                            tbody.appendChild(row);
                        });
                        remindersList.appendChild(table);

                        // Voeg de "Verstuur Reminders" knop toe na de tabel
                        sendReminderBtn = document.createElement('button');
                        sendReminderBtn.id = 'sendReminderBtn';
                        sendReminderBtn.classList.add('btn', 'btn-primary', 'mt-3');
                        sendReminderBtn.textContent = 'Verstuur Reminders';
                        sendReminderBtn.style.display = 'none'; // Verberg de knop initieel
                        remindersList.appendChild(sendReminderBtn);

                        // Voeg event listener toe aan de remindersList voor event delegation
                        remindersList.addEventListener('change', function(event) {
                            if (event.target.classList.contains('reminder-checkbox')) {
                                toggleSendReminderButton();
                            }
                        });

                        // Roep de functie aan om de initiële staat van de knop in te stellen
                        toggleSendReminderButton();
                    }
                })
                .catch(error => {
                    loadingMessage.textContent = '';
                    remindersList.innerHTML = `<p class="text-center text-danger">Fout bij het laden van herinneringen: ${error.message}</p>`;
                    console.error('Fout bij het ophalen van herinneringen:', error);
                });
        });
    }

    // NIEUWE LOGICA VOOR HET INKLAPPEN VAN DE NAVIGATIEBALK
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.getElementById('navbarNav');

    if (navbarToggler && navbarCollapse) {
        document.addEventListener('click', function(event) {
            if (navbarCollapse.classList.contains('show') && 
                !navbarToggler.contains(event.target) && 
                !navbarCollapse.contains(event.target)) {
                
                const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                    toggle: false
                });
                bsCollapse.hide();
            }
        });
    }
});

// De pingBackend functie kan ook hier staan, of in een apart gedeeld bestand als je wilt
function pingBackend() {
    fetch('http://127.0.0.1:8000/api/v1/ping/')
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        alert('Fout: De backend is niet bereikbaar.');
    });
}
