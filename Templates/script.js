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

// Function to add a new event and save it to localStorage
function addEvent(event) {
    const events = JSON.parse(localStorage.getItem('events')) || [];
    events.push(event);
    saveEvents(events);
    filterEvents(); // Refresh the displayed events
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
            <img src="${event.poster || 'https://via.placeholder.com/150'}" alt="Event Poster" class="event-poster">
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
        const marker = L.marker(event.coordinates)
            .bindPopup(`<b>${event.name}</b><br>${event.location}`)
            .addTo(map);
        markers.push(marker); // Add marker to the array
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

    // Get form data
    const eventName = document.getElementById('event-name').value;
    const eventHost = document.getElementById('event-host').value;
    const eventTime = document.getElementById('event-time').value;
    const eventLocation = document.getElementById('event-location').value;
    const eventCategory = document.getElementById('event-category').value;
    const posterFile = document.getElementById('event-poster').files[0];

    // Convert the poster image to a Base64 string
    if (posterFile) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const posterBase64 = e.target.result;

            // Geocode the address
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

                // Save the event to localStorage
                addEvent(newEvent);

                // Reset the form
                e.target.reset();
            });
        };
        reader.readAsDataURL(posterFile);
    } else {
        // Handle case when no poster is uploaded
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
            e.target.reset();
        });
    }
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
