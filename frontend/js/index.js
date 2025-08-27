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
    const url = 'http://127.0.0.1:8000/api/deelnemer-cursus/'; 
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

const handleFormSubmit = async (event) => {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    submitButton.disabled = true;

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => (data[key] = value));

    if (data.vastzettenCheck) {
        savedCourseData = {
            cursus: data.cursus,
            cursusdatum: data.cursusdatum,
            refreshercheck: document.getElementById('refreshercheck').checked,
            'geldigheid-jaren': data['geldigheid-jaren'],
            'geldigheid-datum-input': data['geldigheid-datum-input']
        };
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
    }

    if (geldigheidDropdown) {
        geldigheidDropdown.addEventListener('change', handleGeldigheidChange);
    }
});