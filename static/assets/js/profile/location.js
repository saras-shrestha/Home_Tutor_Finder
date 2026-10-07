let marker;
// Default location: Kathmandu
const defaultLatitude = 27.7172;
const defaultLongitude = 85.3240;


// Create map
map = L.map("map").setView(
    [defaultLatitude, defaultLongitude],
    13
);


// OpenStreetMap tiles
L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    {
        attribution:
            '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: "abcd",
        maxZoom: 20
    }
).addTo(map);

map.on("click", function (event) {

    const latitude = event.latlng.lat;
    const longitude = event.latlng.lng;

    setLocation(latitude, longitude);
});

function setLocation(latitude, longitude) {

    // Save coordinates in hidden inputs
    document.getElementById("latitude").value = latitude;
    document.getElementById("longitude").value = longitude;


    // Remove old marker
    if (marker) {
        map.removeLayer(marker);
    }


    // Create new marker
    marker = L.marker([latitude, longitude])
        .addTo(map);


    // Move map
    map.setView(
        [latitude, longitude],
        16
    );
}

document.getElementById("useLocation").addEventListener("click", function () {

    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(

        function (position) {

            const latitude = position.coords.latitude;

            const longitude = position.coords.longitude;


            setLocation(latitude, longitude);
        },

        function (error) {

            if (error.code === error.PERMISSION_DENIED) {

                alert(
                    "Please allow location access to use this feature."
                );

            } else {

                alert(
                    "Unable to get your location."
                );
            }
        }
    );
});
function validateLocation() {
    const latitude = document.getElementById("latitude").value;
    const longitude = document.getElementById("longitude").value;

    if (!latitude || !longitude) {
        alert("Please select your location on the map.");
        return false;
    }

    return true;
}




document.getElementById('region').addEventListener('change', function () {
    const regionId = this.value;
    const districtSelect = document.getElementById('district');

    districtSelect.innerHTML = '<option value="">Loading...</option>';

    if (!regionId) {
        districtSelect.innerHTML =
            '<option value="">Select District</option>';
        return;
    }

    const url = "{% url 'get_districts' 0 %}".replace('0', regionId);

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            districtSelect.innerHTML =
                '<option value="" selected disabled>Select District</option>';

            data.forEach(district => {
                const option = document.createElement('option');

                option.value = district.id;
                option.textContent = district.name;

                districtSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading districts:', error);

            districtSelect.innerHTML =
                '<option value="">Unable to load districts</option>';
        });
});


document.getElementById('district').addEventListener('change', function () {
    const districtId = this.value;
    const citySelect = document.getElementById('city');

    citySelect.innerHTML = '<option value="">Loading...</option>';

    if (!districtId) {
        citySelect.innerHTML =
            '<option value="" selected disabled>Select City</option>';
        return;
    }

    const url = "{% url 'get_cities' 0 %}".replace('0', districtId);

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            citySelect.innerHTML =
                '<option value="" selected disabled>Select City</option>';

            data.forEach(city => {
                const option = document.createElement('option');

                option.value = city.id;
                option.textContent = city.name;

                citySelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading cities:', error);
            citySelect.innerHTML = '<option value="">Unable to load cities</option>';
        });
});