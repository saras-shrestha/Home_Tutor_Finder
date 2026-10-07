document.addEventListener("DOMContentLoaded", function () {

    const profileInput =document.getElementById("profile_picture");

    const profilePreview =document.getElementById("profilePreview");

    const removePhoto =document.getElementById("removePhoto");


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


    /* Certificate */

    const certificateInput = document.getElementById("certificate");
    const certificatePreview = document.getElementById("certificatePreview");
    const chooseCertificate = document.getElementById("chooseCertificate");
    const removeCertificate = document.getElementById("removeCertificate");


    // Choose certificate
    chooseCertificate.addEventListener("click", function () {
        certificateInput.click();
    });


    // Preview certificate
    certificateInput.addEventListener("change", function () {

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


        // Read image
        const reader = new FileReader();

        reader.onload = function (event) {

            certificatePreview.src = event.target.result;

        };

        reader.readAsDataURL(file);

    });


    // Remove certificate
    removeCertificate.addEventListener("click", function () {

        certificateInput.value = "";

        certificatePreview.src =
            "{% static 'assets/images/profile/profile.png' %}";

    });
    /* certificate part ended */

    /* CV */

    const cvInput = document.getElementById("cv");
    const cvPreview = document.getElementById("cvPreview");
    const chooseCV = document.getElementById("chooseCV");
    const removeCV = document.getElementById("removeCV");


    // Choose certificate
    chooseCV.addEventListener("click", function () {
        cvInput.click();
    });


    // Preview certificate
    cvInput.addEventListener("change", function () {

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


        // Read image
        const reader = new FileReader();

        reader.onload = function (event) {

            cvPreview.src = event.target.result;

        };

        reader.readAsDataURL(file);

    });


    // Remove certificate
    removeCV.addEventListener("click", function () {

        cvInput.value = "";

        cvPreview.src =
            "{% static 'assets/images/profile/profile.png' %}";

    });
    /* cv part ended */

});