// Functie om de statusmelding bij te werken (in een gedeeld script)
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

// Functie om de knop "Verstuur Reminders" te tonen of verbergen
const toggleSendReminderButton = () => {
    const checkboxes = document.querySelectorAll('.reminder-checkbox');
    const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
    const sendReminderBtn = document.getElementById('sendReminderBtn');
    
    if (sendReminderBtn) {
        sendReminderBtn.style.display = anyChecked ? 'block' : 'none';
    }
};

// Functie voor het renderen van de tabel met herinneringen
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
            <td>${item.deelnemer.voornaam || ''} ${item.deelnemer.tussenvoegsel || ''} ${item.deelnemer.achternaam || ''}</td>
            <td>${item.deelnemer.email || ''}</td>
            <td>${item.cursus.cursus || ''}</td>
            <td>${item.verloopdatum || ''}</td>
            <td><input type="checkbox" class="form-check-input reminder-checkbox" data-deelnemer-id="${item.deelnemer.id}" data-cursus-id="${item.cursus.id}"></td>
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
        const response = await fetch('/api/v1/expiring-certificates/');
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
    fetch('/api/v1/ping/')
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        alert('Fout: De backend is niet bereikbaar.');
    });
}

// Initialisatie van de event listeners
document.addEventListener('DOMContentLoaded', () => {
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
    }
});