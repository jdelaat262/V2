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

const handleGeldigheidChange = (event) => {
    const datumInput = document.getElementById('geldigheid-datum-input');
    if (datumInput) {
        datumInput.hidden = event.target.value !== 'custom';
    }
};

const submitToAPI = async (data) => {
    const url = 'http://127.0.0.1:8000/api/v1/deelnemer-cursus/';
    console.log('Versturen naar URL:', url); // Debug: URL check
    console.log('Data die wordt verstuurd:', data); // Debug: uitgaande data
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        console.log('Response status:', response.status); // Debug: response status
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const responseData = await response.json();
        console.log('Response data ontvangen:', responseData); // Debug: response data
        return { success: true, data: responseData };
    } catch (error) {
        console.error('Fout in submitToAPI:', error); // Debug: error details
        return { success: false, message: error.message };
    }
};

const handleFormSubmit = async (event) => {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    submitButton.disabled = true;

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => (data[key] = value));

    console.log('Formulier data verzameld:', data); // Debug: vorm data

    if (data.vastzettenCheck) {
        savedCourseData = {
            cursus: data.cursus,
            cursusdatum: data.cursusdatum,
            refreshercheck: document.getElementById('refreshercheck').checked,
            'geldigheid-jaren': data['geldigheid-jaren'],
            'geldigheid-datum-input': data['geldigheid-datum-input']
        };
        console.log('Cursus data opgeslagen voor vastzetten:', savedCourseData); // Debug: saved data
    }

    const result = await submitToAPI(data);

    if (result.success) {
        console.log('Succes! Data van de server:', result.data);
        showStatus('Formulier succesvol verzonden!', true);
        
        form.reset();
        if (data.vastzettenCheck && savedCourseData) {
            document.getElementById('cursus').value = savedCourseData.cursus;
            document.getElementById('cursusdatum').value = savedCourseData.cursusdatum;
            document.getElementById('refreshercheck').checked = savedCourseData.refreshercheck;
            document.getElementById('geldigheid-jaren').value = savedCourseData['geldigheid-jaren'];
            document.getElementById('vastzettenCheck').checked = true;
            if (savedCourseData['geldigheid-jaren'] === 'custom') {
                document.getElementById('geldigheid-datum-input').hidden = false;
                document.getElementById('geldigheid-datum-input').value = savedCourseData['geldigheid-datum-input'];
            }
        }
    } else {
        console.error('Fout bij het versturen:', result.message);
        showStatus('Er is een fout opgetreden bij het verzenden.', false);
    }
    submitButton.disabled = false;
};

document.addEventListener('DOMContentLoaded', () => {
    const certificaatForm = document.getElementById('form-certificaat');
    const geldigheidDropdown = document.getElementById('geldigheid-jaren');

    if (certificaatForm) {
        certificaatForm.addEventListener('submit', handleFormSubmit);
        console.log('Form submit event listener toegevoegd'); // Debug: event listener
    }

    if (geldigheidDropdown) {
        geldigheidDropdown.addEventListener('change', handleGeldigheidChange);
        console.log('Geldigheid dropdown event listener toegevoegd'); // Debug: event listener
    }
});