var map = L.map('map').setView([42.3188, -72.6389], 15); // Centered on Smith College

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Fetch events from backend and add markers to the map
fetch('http://127.0.0.1:5000/events')
    .then(response => response.json())
    .then(events => {
        events.forEach(event => {
            var latLng = getLatLngForLocation(event.location);
            if (latLng) {
                var marker = L.marker(latLng).addTo(map)
                    .bindPopup(`${event.location}<br>${event.time}<br>Free Food: ${event.free_food}`)
                    .openPopup();
            }
        });
    })
    .catch(error => {
        console.error('Error fetching events:', error);
    });

document.getElementById('search-button').addEventListener('click', function() {
    var query = document.getElementById('search-input').value.toLowerCase();
    map.eachLayer(function(layer) {
        if (layer instanceof L.Marker) {
            var popupContent = layer.getPopup().getContent().toLowerCase();
            if (popupContent.includes(query)) {
                layer.openPopup();
            } else {
                layer.closePopup();
            }
        }
    });
});

function getLatLngForLocation(location) {
    // Expanded list of locations with coordinates
    var locations = {
        "Campus Center": [42.3188, -72.6392],
        "Neilson Library": [42.3192, -72.6375],
        "Seelye Hall": [42.3196, -72.6382],
        "Alumnae Gymnasium": [42.3174, -72.6371],
        "Ford Hall": [42.3202, -72.6387],
        "McConnell Hall": [42.3200, -72.6395]
        // Add more locations as needed
    };
    return locations[location] || null;
}

