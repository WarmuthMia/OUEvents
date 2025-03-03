// Initialize the map
var map = L.map('map').setView([35.207, -97.445], 15);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Create an array to store markers
let markers = [];

// Function to load events from localStorage
function loadEvents() {
    const events = JSON.parse(localStorage.getItem('events')) || [];
    addMarkers(events);
}

// Function to add markers to the map
function addMarkers(events) {
    markers.forEach(marker => map.removeLayer(marker)); // Clear existing markers
    markers = []; // Reset the markers array

    events.forEach(event => {
        const marker = L.marker(event.coordinates)
            .bindPopup(`<b>${event.name}</b><br>${event.location}`)
            .addTo(map);

        // Add click event listener to the marker
        marker.on('click', () => showEventDetails(event));
        markers.push(marker); // Add marker to the array
    });
}

// Function to show event details
function showEventDetails(event) {
    const eventDetailsContainer = document.getElementById('event-details');
    eventDetailsContainer.innerHTML = `
        <h2>${event.name}</h2>
        <p><strong>Host:</strong> ${event.host}</p>
        <p><strong>Time:</strong> ${event.time}</p>
        <p><strong>Location:</strong> ${event.location}</p>
        <div class="event-category">${event.category}</div>
    `;
}

// Load events when the page loads
loadEvents();
