const steps = document.querySelectorAll(".step");
const formSteps = document.querySelectorAll(".form-step");

const currentStep = Number(
    document.getElementById("currentStep").value
);

let highestStep = currentStep;

function showStep(stepNumber) {

    stepNumber = Number(stepNumber);

    // Hide all sections
    formSteps.forEach(section => {
        section.classList.remove("active");
    });

    // Show selected section
    document
        .querySelector(`.form-step[data-step="${stepNumber}"]`)
        .classList.add("active");

    // Remember furthest step reached
    if (stepNumber > highestStep) {
        highestStep = stepNumber;
    }

    // Update progress bar
    steps.forEach(step => {

        const number = Number(step.dataset.step);

        step.classList.toggle(
            "active",
            number <= highestStep
        );
    });
}

// Open the user's saved/current step
showStep(currentStep);

/* Personal → Location */
const profileForm = document.getElementById("profileForm");
const profileUrl = profileForm.dataset.url;
document
    .getElementById("nextPersonal")
    .addEventListener("click", function () {

        const formData = new FormData();

        formData.append(
            "section",
            "personal"
        );

        formData.append(
            "full_name",
            document.getElementById("full_name").value
        );

        formData.append(
            "gender",
            document.getElementById("gender").value
        );

        formData.append(
            "phone",
            document.getElementById("phone").value
        );

        formData.append(
            "dob",
            document.getElementById("dob").value
        );

        const profilePicture =
            document.getElementById("profile_picture").files[0];

        if (profilePicture) {
            formData.append(
                "profile_picture",
                profilePicture
            );
        }

        fetch(profileUrl, {
            method: "POST",

            headers: {
                "X-CSRFToken":
                    document.querySelector(
                        "[name=csrfmiddlewaretoken]"
                    ).value
            },

            body: formData
        })
        .then(response => response.json())
        .then(data => {

            if (data.success) {

                console.log(
                    "Personal information saved."
                );

                showStep(data.next_step);

            } else {

                alert(data.message);

            }

        })
        .catch(error => {

            console.error(error);

            alert(
                "Something went wrong while saving."
            );

        });

    });

/* Location → Personal */

document
    .getElementById("backLocation")
    .addEventListener("click", function () {

        showStep(1);

    });


/* Location → About */


function validateLocation() {
    const latitude = document.getElementById("latitude").value;
    const longitude = document.getElementById("longitude").value;

    if (!latitude || !longitude) {
        alert("Please select your location on the map.");
        return false;
    }

     return true;
}
document.getElementById("nextLocation").addEventListener("click", function () {

    if (!validateLocation()) {
        return;
    }

    const formData = new FormData();

    formData.append("section", "location");

    formData.append(
        "region",
        document.getElementById("region").value
    );

     formData.append(
        "district",
        document.getElementById("district").value
    );

    formData.append(
        "city",
         document.getElementById("city").value
    );

    formData.append(
        "address",
        document.getElementById("address").value
    );

    formData.append(
         "latitude",
        document.getElementById("latitude").value
    );

    formData.append(
        "longitude",
        document.getElementById("longitude").value
    );

    fetch(profileUrl, {
        method: "POST",

        headers: {
            "X-CSRFToken":
                document.querySelector(
                    "[name=csrfmiddlewaretoken]"
                ).value
        },

        body: formData
    })
    .then(response => response.json())
    .then(data => {

        if (data.success) {

            showStep(data.next_step);

         } else {

            alert(data.message);

        }

    })
    .catch(error => {

        console.error(error);

        alert(
            "Something went wrong while saving."
        );

    });
    
});




/* About → Location */

document
    .getElementById("backAbout")
    .addEventListener("click", function () {

        showStep(2);

    });

/* About → Academic */

document
    .getElementById("nextAbout")
    .addEventListener("click", function () {
        const formData = new FormData();

        formData.append(
            "section",
            "about"
        );

        formData.append(
            "description",
            document.getElementById("description").value
        );

        fetch(profileUrl, {
            method: "POST",

            headers: {
                "X-CSRFToken":
                    document.querySelector(
                        "[name=csrfmiddlewaretoken]"
                    ).value
            },

            body: formData
        })
        .then(response => response.json())
        .then(data => {

            if (data.success) {

                showStep(data.next_step);

            } else {

                alert(data.message);

            }

        });

    });


/* Academic → About */

document
    .getElementById("backAcademic")
    .addEventListener("click", function () {

        showStep(3);

    });


// save profile final button click event
document
    .getElementById("save_profile")
    .addEventListener("click", function () {

        const formData = new FormData();

        formData.append("section", "academic");
        formData.append(
            "education_level", 
            document.getElementById("education_level").value
        );
        formData.append(
            "grade", 
            document.getElementById("grade").value
        );
        formData.append(
            "school_college", 
            document.getElementById("school_college").value
        );

        fetch(profileUrl, {
            method: "POST",

            headers: {
                "X-CSRFToken":
                    document.querySelector(
                        "[name=csrfmiddlewaretoken]"
                    ).value
            },

            body: formData
        })

        .then(response => response.json())

        .then(data => {

            if (data.success) {

                // academic info saved successfully
                window.location.href = data.redirect_url;

            } else {

                alert(data.message);

            }

        })

        .catch(error => {

            console.error(error);

            alert(
                "Something went wrong while saving."
            );

        });

    });

// Validating location
 function validateLocation() {

    const region = document.getElementById("region").value;
    const district = document.getElementById("district").value;
    const city = document.getElementById("city").value;
    const address = document.getElementById("address").value.trim();

    const latitude = document.getElementById("latitude").value;
    const longitude = document.getElementById("longitude").value;


    if (!region) {
        alert("Please select a region.");
        return false;
    }

    if (!district) {
        alert("Please select a district.");
        return false;
    }

    if (!city) {
        alert("Please select a city.");
        return false;
    }

    if (!address) {
        alert("Please enter your address.");
        return false;
    }

    if (!latitude || !longitude) {
        alert("Please select your location on the map.");
        return false;
    }

    return true;
}




