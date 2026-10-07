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



// const formSteps = document.querySelectorAll(".form-step");
// const steps = document.querySelectorAll(".step");

// function showStep(stepNumber) {

//     // Hide all form sections
//     formSteps.forEach(section => {
//         section.classList.remove("active");
//     });

//     // Show selected section
//     document
//         .querySelector(`.form-step[data-step="${stepNumber}"]`)
//         .classList.add("active");


//     // Update progress indicator
//     steps.forEach(step => {

//         const number = Number(step.dataset.step);

//         step.classList.toggle(
//             "active",
//             number <= stepNumber
//         );

//     });
    
// }

// // Load saved progress when page opens
// const currentStep = Number(
//     document.getElementById("currentStep").value
// );
// showStep(currentStep);
// // updateProgress(currentStep);

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

/* About → Qualification */

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


/* Qualification → About */

document
    .getElementById("backQualification")
    .addEventListener("click", function () {

        showStep(3);

    });

/* Qualification → Certification */

document
    .getElementById("nextQualification")
    .addEventListener("click", function () {

        const formData = new FormData();

        formData.append(
            "section",
            "qualification"
        );

        formData.append(
            "high_qualification",
            document.getElementById(
                "high_qualification"
            ).value
        );

        formData.append(
            "study_field",
            document.getElementById(
                "study_field"
            ).value
        );

        formData.append(
            "degree_name",
            document.getElementById(
                "degree_name"
            ).value
        );

        formData.append(
            "college_name",
            document.getElementById(
                "college_name"
            ).value
        );

        formData.append(
            "university",
            document.getElementById(
                "university"
            ).value
        );

        formData.append(
            "study_country",
            document.getElementById(
                "study_country"
            ).value
        );

        formData.append(
            "tutor_gpa",
            document.getElementById(
                "tutor_gpa"
            ).value
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

                console.log(
                    "Qualification saved successfully."
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


/* Certification → Qualification */

document
    .getElementById("backCertification")
    .addEventListener("click", function () {
        showStep(4);
    });

/* Certifiction → CV */

document
    .getElementById("nextCertification")
    .addEventListener("click", function () {

        const certificate =
            document.getElementById("certificate").files[0];

        // Check certificate
        if (!certificate) {

            alert("Please upload a certificate.");

            return;
        }

        const formData = new FormData();

        formData.append(
            "section",
            "certification"
        );

        formData.append(
            "certificate",
            certificate
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

                console.log(
                    "Certificate saved successfully."
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
// vbnm,.  
    

/* CV → Certification */

document
    .getElementById("backCV")
    .addEventListener("click", function () {
        showStep(5);
    });
    

// save profile final button click event
document
    .getElementById("save_profile")
    .addEventListener("click", function () {

        const cv =
            document.getElementById("cv").files[0];

        if (!cv) {
            alert("Please upload your CV.");
            return;
        }

        const formData = new FormData();

        formData.append("section", "cv");
        formData.append("cv", cv);

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

                // CV saved successfully
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

//preview certificate

// const certificateInput=document.getElementById("certificate");
// const chooseBtn=document.getElementById("chooseCertificate")
// chooseBtn.addEventListener("click", function(){
    
//         certificateInput.addEventListener("change", function () {

//         const f = this.files[0];

//         if (!f) {
//             return;
//         }

//         // Check file type

//         if (!f.type.startsWith("image/")) {

//             alert("Please select an image file.");

//             this.value = "";

//             return;
//         }


//         // Check file size

//         if (f.size > 2 * 1024 * 1024) {

//             alert("Image size must be less than 2MB.");

//             this.value = "";

//             return;
//         }


//         const reader = new FileReader();


//         reader.onload = function (event) {

//             certificatePreview.src = event.target.result;

//         };


//         reader.readAsDataURL(file);

//     });

// });

/////////////////////////////
//preview certificate
// document.addEventListener("DOMContentLoaded", function () {

//     const certificateInput =document.getElementById("certificate");

//     const certificatePreview =document.getElementById("certificatePreview");

//     const removeCertificate =document.getElementById("removeCertificate");


//     /* Profile picture preview */

//     certificateInput.addEventListener("change", function () {

//         const file = this.files[0];

//         if (!file) {
//             return;
//         }

//         // Check file type

//         if (!file.type.startsWith("image/")) {

//             alert("Please select an image file.");

//             this.value = "";

//             return;
//         }


//         // Check file size

//         if (file.size > 2 * 1024 * 1024) {

//             alert("Image size must be less than 2MB.");

//             this.value = "";

//             return;
//         }


//         const reader = new FileReader();


//         reader.onload = function (event) {

//             certificatePreview.src = event.target.result;

//         };


//         reader.readAsDataURL(file);

//     });


//     /* Remove profile picture */

//     removeCertificate.addEventListener("click", function () {

//         certificateInput.value = "";

//         certificatePreview.src = "{% static 'assets/images/profile/faq_man.png' %}";

//     });
// });

/////////////////////////////
////////////////////////////
///////////////////////////
/* Location → Personal */

// document
//     .getElementById("backLocation")
//     .addEventListener("click", function () {

//         showStep(1);

//     });


// /* Location → About */

// document
//     .getElementById("nextLocation")
//     .addEventListener("click", function () {

//         showStep(3);

//     });


// /* About → Location */

// document
//     .getElementById("backAbout")
//     .addEventListener("click", function () {

//         showStep(2);

//     });

// /* About → Qualification */

// document
//     .getElementById("nextAbout")
//     .addEventListener("click", function () {

//         showStep(4);

//     });


// /* Qualification → About */

// document
//     .getElementById("backQualification")
//     .addEventListener("click", function () {

//         showStep(3);

//     });

// /* Qualification → Certification */

// document
//     .getElementById("nextQualification")
//     .addEventListener("click", function () {

//         showStep(5);

//     });


// /* Certification → Qualification */

// document
//     .getElementById("backCertification")
//     .addEventListener("click", function () {
//         showStep(4);
//     });

// /* Certifiction → CV */

// document
//     .getElementById("nextCertification")
//     .addEventListener("click", function () {
//         showStep(6);
//     });


// /* CV → Certification */

// document
//     .getElementById("backCV")
//     .addEventListener("click", function () {

//         showStep(5);

//     });


