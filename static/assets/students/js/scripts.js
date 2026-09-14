document.addEventListener("DOMContentLoaded", function () {

    const profileInput =
        document.getElementById("profile_picture");

    const profilePreview =
        document.getElementById("profilePreview");

    const removePhoto =
        document.getElementById("removePhoto");


    /* Profile picture preview */

    profileInput.addEventListener("change", function () {

        const file = this.files[0];

        if (!file) {
            return;
        }


        // Check file type

        if (!file.type.startsWith("image/")) {

            alert("Please select an image file.");

            this.value = "";

            return;
        }


        // Check file size

        if (file.size > 2 * 1024 * 1024) {

            alert("Image size must be less than 2MB.");

            this.value = "";

            return;
        }


        const reader = new FileReader();


        reader.onload = function (event) {

            profilePreview.src = event.target.result;

        };


        reader.readAsDataURL(file);

    });


    /* Remove profile picture */

    removePhoto.addEventListener("click", function () {

        profileInput.value = "";

        profilePreview.src = "{% static 'assets/images/profile/faq_man.png' %}";

    });


    /* Use browser location */

    const useLocation =
        document.getElementById("useLocation");


    useLocation.addEventListener("click", function () {

        if (!navigator.geolocation) {

            alert(
                "Location services are not supported by your browser."
            );

            return;
        }


        useLocation.textContent = "Getting location...";


        navigator.geolocation.getCurrentPosition(

            function (position) {

                const latitude =
                    position.coords.latitude;

                const longitude =
                    position.coords.longitude;


                document.getElementById("latitude").value =
                    latitude;

                document.getElementById("longitude").value =
                    longitude;


                useLocation.textContent =
                    "✓ Location Selected";


                alert(
                    "Your location has been selected."
                );

            },


            function (error) {

                useLocation.textContent =
                    "📍 Use My Location";


                if (error.code === 1) {

                    alert(
                        "Please allow location access in your browser."
                    );

                } else {

                    alert(
                        "Unable to get your location."
                    );

                }

            }

        );

    });


    /* Select location button */

    const selectLocation =
        document.getElementById("selectLocation");


    selectLocation.addEventListener("click", function () {

        alert(
            "Map selection will be connected here."
        );

    });


    /* Form validation */

    const form =
        document.getElementById("profileForm");


    form.addEventListener("submit", function (event) {

        const firstName =
            document.getElementById("first_name").value.trim();

        const lastName =
            document.getElementById("last_name").value.trim();

        const phone =
            document.getElementById("phone").value.trim();


        if (firstName === "") {

            alert("Please enter your first name.");

            event.preventDefault();

            return;
        }


        if (lastName === "") {

            alert("Please enter your last name.");

            event.preventDefault();

            return;
        }


        if (phone !== "" &&
            !/^[0-9]{10}$/.test(phone)) {

            alert(
                "Please enter a valid 10-digit phone number."
            );

            event.preventDefault();

            return;
        }

    });

});