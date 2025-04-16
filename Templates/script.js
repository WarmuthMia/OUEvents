// Function to filter events based on search query, category, and date
function filterEvents() {
    const searchQuery = document.getElementById('search-bar').value.trim().toLowerCase();
    const selectedCategory = document.getElementById('category').value;
    const selectedDate = document.getElementById('date').value;

    const events = JSON.parse(localStorage.getItem('events')) || [];
    const filteredEvents = events.filter(event => {
        // Filter by search query (check event name, host, location, and category)
        const matchesSearch = [event.name, event.host, event.location, event.category].some(
            field => field && field.toLowerCase().includes(searchQuery)
        );

        // Filter by category
        const matchesCategory = selectedCategory === 'all' || event.category === selectedCategory;

        // Filter by date (match if event date starts with selected date)
        const matchesDate = !selectedDate || event.time.startsWith(selectedDate);

        return matchesSearch && matchesCategory && matchesDate;
    });

    renderEventCards(filteredEvents);
    addMarkers(filteredEvents);
}

// Function to save events to localStorage
function saveEvents(events) {
    localStorage.setItem('events', JSON.stringify(events));
}
// Load events from localStorage when the page loads
window.addEventListener('DOMContentLoaded', loadEvents);

// Function to add a new event and save it to the database
function addEvent(eventObj) {
    const formData = new FormData();
    formData.append('name', eventObj.name);
    formData.append('host', eventObj.host);
    formData.append('time', eventObj.time);
    formData.append('location', eventObj.location);
    formData.append('category', eventObj.category);
    if (eventObj.poster) {
        // Convert Base64 back to Blob
        const byteString = atob(eventObj.poster.split(',')[1]);
        const mimeString = eventObj.poster.split(',')[0].split(':')[1].split(';')[0];
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        const blob = new Blob([ab], { type: mimeString });
        formData.append('image', blob, 'poster.png');
    }

    fetch('http://localhost:5000/add_event', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Event added successfully!');
            filterEvents(); // Refresh localStorage data
        } else {
            alert(data.message || 'Failed to add event.');
        }
    })
    .catch(error => {
        console.error('Error submitting event to backend:', error);
        alert('There was a problem submitting the event.');
    });
}


// Function to render event cards
function renderEventCards(events) {
    const eventCardsContainer = document.getElementById('event-cards-container');
    eventCardsContainer.innerHTML = ''; // Clear existing cards

    events.forEach(event => {
        const eventCard = document.createElement('div');
        eventCard.className = 'event-card';
        eventCard.setAttribute('data-category', event.category);

        eventCard.innerHTML = `
            <img src="${event.poster || 'https://placekitten.com/150/150?text=No+Image'}" alt="Event Poster" class="event-poster">
            <div class="event-details">
                <h3>${event.name}</h3>
                <p><strong>Host:</strong> ${event.host}</p>
                <p><strong>Time:</strong> ${event.time}</p>
                <p><strong>Location:</strong> ${event.location}</p>
                <div class="event-category">${event.category}</div>
            </div>
        `;
        eventCardsContainer.appendChild(eventCard);
    });
}

// Function to add markers to the map
function addMarkers(events) {
    markers.forEach(marker => map.removeLayer(marker)); // Clear existing markers
    markers = []; // Reset the markers array

    events.forEach(event => {
        if (event.coordinates && event.coordinates.length === 2) {
            const marker = L.marker(event.coordinates)
                .bindPopup(`<b>${event.name}</b><br>${event.location}`)
                .addTo(map);
            markers.push(marker); // Add marker to the array
        }
    });
}

// Function to load events from localStorage and render them
function loadEvents() {
    const events = JSON.parse(localStorage.getItem('events')) || [];
    renderEventCards(events);
    addMarkers(events);
}

// Function to geocode an address using the Nominatim API
function geocodeAddress(address, callback) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const coordinates = [
                    parseFloat(data[0].lat),
                    parseFloat(data[0].lon)
                ];
                callback(coordinates); // Return the coordinates
            } else {
                alert('Unable to geocode address. Please check the address and try again.');
            }
        })
        .catch(error => {
            console.error('Error geocoding address:', error);
            alert('An error occurred while geocoding the address.');
        });
}

// Add event listener to the form for adding new events on HTMLPage1.html
document.getElementById('add-event-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent form submission

    const form = e.target; // ← Save the form reference here

    // Get form data
    const eventName = document.getElementById('event-name').value;
    const eventHost = document.getElementById('event-host').value;
    const eventTime = document.getElementById('event-time').value;
    const eventLocation = document.getElementById('event-location').value;
    const eventCategory = document.getElementById('event-category').value;
    const posterFile = document.getElementById('event-poster').files[0];

    if (posterFile) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const posterBase64 = e.target.result;

            const newEvent = {
                name: eventName,
                host: eventHost,
                time: eventTime,
                location: eventLocation,
                category: eventCategory,
                poster: posterBase64
            };

            addEvent(newEvent);
            form.reset(); // form reset here
            };
            reader.readAsDataURL(posterFile);
        } else {
            const newEvent = {
                name: eventName,
                host: eventHost,
                time: eventTime,
                location: eventLocation,
                category: eventCategory,
                poster: null
            };      

            addEvent(newEvent);
            form.reset(); 
        }
            /*
            geocodeAddress(eventLocation, (coordinates) => {
                const newEvent = {
                    name: eventName,
                    host: eventHost,
                    time: eventTime,
                    location: eventLocation,
                    category: eventCategory,
                    coordinates: coordinates,
                    poster: posterBase64
                };

                addEvent(newEvent);
                form.reset(); // form reset here
            });
        };
        reader.readAsDataURL(posterFile);
    } else {
        geocodeAddress(eventLocation, (coordinates) => {
            const newEvent = {
                name: eventName,
                host: eventHost,
                time: eventTime,
                location: eventLocation,
                category: eventCategory,
                coordinates: coordinates,
                poster: null
            };

            addEvent(newEvent);
            form.reset(); 
        });
    }
        */
});

// Initialize the map
var map = L.map('map').setView([35.207, -97.445], 15);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Create an array to store map markers
let markers = [];

// Load and display events when the page loads
window.addEventListener('DOMContentLoaded', loadEvents);

// Add event listeners for filtering
document.getElementById('search-bar').addEventListener('input', filterEvents);
document.getElementById('category').addEventListener('change', filterEvents);
document.getElementById('date').addEventListener('change', filterEvents);