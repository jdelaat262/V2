let savedCourseData = null; 

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

// Functie voor het verwerken van het formulier
const processFormData = (form) => {
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => (data[key] = value));

    // Verwerk checkboxen naar boolean
    data.refreshercheck = !!data.refreshercheck;
    data.vastzettenCheck = !!data.vastzettenCheck;

    // Verwerk lege strings naar null
    for (const key in data) {
        if (data[key] === '') {
            data[key] = null;
        }
    }
    
    // Verwerk geldigheid op basis van de dropdown of custom input
    if (data['geldigheid-jaren'] === 'custom' && data['geldigheid-datum-input']) {
        data.geldigheid_jaren = data['geldigheid-datum-input'];
    } else {
        data.geldigheid_jaren = data['geldigheid-jaren'];
    }

    // Verwijder onnodige velden voordat de data naar de API gaat
    delete data['geldigheid-datum-input'];

    return data;
};

// Asynchrone functie voor het versturen van data naar de API
const submitToAPI = async (data) => {
    const url = 'http://127.0.0.1:8000/api/v1/certificaten/';
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const responseData = await response.json();
        return { success: true, data: responseData };
    } catch (error) {
        return { success: false, message: error.message };
    }
};

// De hoofd 'submit' handler
const handleFormSubmit = async (event) => {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    submitButton.disabled = true;

    // Verzamel en verwerk de formulierdata
    const data = processFormData(form);

    // Sla cursusgegevens op als de 'vastzetten' checkbox is aangevinkt
    if (data.vastzettenCheck) {
        savedCourseData = {
            cursus: data.cursus,
            cursusdatum: data.cursusdatum,
            refreshercheck: data.refreshercheck,
            'geldigheid-jaren': data['geldigheid-jaren'],
        };
    }

    // Stuur de data naar de backend en verwerk het resultaat
    const result = await submitToAPI(data);

    if (result.success) {
        console.log('Succes! Data van de server:', result.data);
        showStatus('Formulier succesvol verzonden!', true);
        
        // Reset het formulier en herstel de vastgezette gegevens
        form.reset();
        if (data.vastzettenCheck && savedCourseData) {
            document.getElementById('cursus').value = savedCourseData.cursus;
            document.getElementById('cursusdatum').value = savedCourseData.cursusdatum;
            document.getElementById('refreshercheck').checked = savedCourseData.refreshercheck;
            document.getElementById('geldigheid-jaren').value = savedCourseData['geldigheid-jaren'];
            document.getElementById('vastzettenCheck').checked = true;
        }
    } else {
        console.error('Fout bij het versturen:', result.message);
        showStatus('Er is een fout opgetreden bij het verzenden.', false);
    }
    submitButton.disabled = false;
};

// Logica voor het tonen/verbergen van de custom datum input
const handleGeldigheidChange = (event) => {
    const datumInput = document.getElementById('geldigheid-datum-input');
    if (datumInput) {
        datumInput.hidden = event.target.value !== 'custom';
    }
};

// Initialisatie van alle event listeners bij het laden van de pagina
document.addEventListener('DOMContentLoaded', () => {
    const certificaatForm = document.getElementById('form-certificaat');
    const geldigheidDropdown = document.getElementById('geldigheid-jaren');

    if (certificaatForm) {
        certificaatForm.addEventListener('submit', handleFormSubmit);
    }

    if (geldigheidDropdown) {
        geldigheidDropdown.addEventListener('change', handleGeldigheidChange);
    }
});