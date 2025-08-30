document.addEventListener('DOMContentLoaded', () => {

    // Functies
    const showStatus = (message, isSuccess) => {
        const statusDiv = document.getElementById('status-message');
        if (!statusDiv) return;
        statusDiv.textContent = message;
        statusDiv.className = 'mt-3 alert';
        if (isSuccess) {
            statusDiv.classList.add('alert-success');
        } else {
            statusDiv.classList.add('alert-danger');
        }
    };

    const toggleSendReminderButton = () => {
        const checkboxes = document.querySelectorAll('.reminder-checkbox');
        const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
        const sendReminderBtn = document.getElementById('sendReminderBtn');
        
        if (sendReminderBtn) {
            sendReminderBtn.style.display = anyChecked ? 'block' : 'none';
        }
    };

    const renderRemindersTable = (reminders, container) => {
        container.innerHTML = '';
        if (reminders.length === 0) {
            container.innerHTML = '<p class="text-center text-white">Geen certificaten gevonden die binnenkort verlopen. Alles is up-to-date!</p>';
            return;
        }

        const table = document.createElement('table');
        table.classList.add('table', 'table-striped', 'table-hover', 'text-white');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Deelnemer</th>
                    <th>E-mail</th>
                    <th>Cursus</th>
                    <th>Verloopdatum</th>
                    <th>Dagen Resterend</th>
                    <th>Kies</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        `;
        
        const tbody = table.querySelector('tbody');
        reminders.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.naam}</td>
                <td>${item.email}</td>
                <td>${item.cursus}</td>
                <td>${item.expiry_date}</td>
                <td>${item.days_remaining}</td>
                <td><input type="checkbox" class="form-check-input reminder-checkbox" data-deelnemer-id="${item.deelnemer_id}" data-cursus-id="${item.cursus_id}"></td>
            `;
            tbody.appendChild(row);
        });

        container.appendChild(table);
        
        // Voeg de "Verstuur Reminders" knop toe na de tabel
        const sendReminderBtn = document.createElement('button');
        sendReminderBtn.id = 'sendReminderBtn';
        sendReminderBtn.classList.add('btn', 'btn-primary', 'mt-3');
        sendReminderBtn.textContent = 'Verstuur Reminders';
        sendReminderBtn.style.display = 'none';
        container.appendChild(sendReminderBtn);
    };

    // Hoofdfunctie voor het ophalen van de herinneringen
    const fetchReminders = async () => {
        const remindersList = document.getElementById('remindersList');
        const loadingMessage = document.getElementById('loadingMessage');

        loadingMessage.textContent = 'Certificaten aan het scannen...';
        remindersList.innerHTML = '';

        try {
            const response = await fetch('http://127.0.0.1:8000/api/v1/expiring-certificates/');
            if (!response.ok) {
                throw new Error('Netwerkrespons was niet ok');
            }
            const data = await response.json();
            
            loadingMessage.textContent = '';
            renderRemindersTable(data, remindersList);
            toggleSendReminderButton(); // Initialiseer de knopstatus na het renderen
            
        } catch (error) {
            loadingMessage.textContent = '';
            showStatus(`Fout bij het laden van herinneringen: ${error.message}`, false);
            console.error('Fout bij het ophalen van herinneringen:', error);
        }
    };

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

    // Nieuwe functie toevoegen:
    const sendSelectedReminders = async () => {
        const checkedBoxes = document.querySelectorAll('.reminder-checkbox:checked');
        const reminders = Array.from(checkedBoxes).map(checkbox => ({
            deelnemer_id: checkbox.dataset.deelnemerId,
            cursus_id: checkbox.dataset.cursusId
        }));

        try {
            const response = await fetch('http://127.0.0.1:8000/api/v1/send-expiry-reminders/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reminders })
            });
            
            if (response.ok) {
                showStatus(`${reminders.length} reminder(s) verzonden!`, true);
            }
        } catch (error) {
            showStatus('Fout bij versturen reminders', false);
        }
    };

    // Initialisatie van de event listeners
    const scanRemindersBtn = document.getElementById('scanRemindersBtn');
    const remindersList = document.getElementById('remindersList');

    if (scanRemindersBtn) {
        scanRemindersBtn.addEventListener('click', fetchReminders);
    }
    
    // Event delegation voor de checkboxes in de tabel
    if (remindersList) {
        remindersList.addEventListener('change', (event) => {
            if (event.target.classList.contains('reminder-checkbox')) {
                toggleSendReminderButton();
            }
        });

        // Event listener voor de Verstuur Reminders knop
        remindersList.addEventListener('click', async (event) => {
            if (event.target.id === 'sendReminderBtn') {
                await sendSelectedReminders();
            }
        });
    }
});