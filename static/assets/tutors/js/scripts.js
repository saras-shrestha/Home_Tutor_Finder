const formSteps = document.querySelectorAll(".form-step");
const steps = document.querySelectorAll(".step");


function showStep(stepNumber) {

    // Hide all form sections
    formSteps.forEach(section => {
        section.classList.remove("active");
    });

    // Show selected section
    document
        .querySelector(`.form-step[data-step="${stepNumber}"]`)
        .classList.add("active");


    // Update progress indicator
    steps.forEach(step => {

        const number = Number(step.dataset.step);

        step.classList.toggle(
            "active",
            number <= stepNumber
        );

    });
}


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

// document
//     .getElementById("nextPersonal")
//     .addEventListener("click", function () {

//         showStep(2);

//     });
// document
//     .getElementById("nextPersonal")
//     .addEventListener("click", function () {

//         const fullName = document.getElementById("full_name").value;
//         const gender = document.getElementById("gender").value;
//         const phone = document.getElementById("phone").value;

//         const profilePicture =
//             document.getElementById("profile_picture").files[0];

//         const formData = new FormData();

//         formData.append("full_name", fullName);
//         formData.append("gender", gender);
//         formData.append("phone", phone);

//         if (profilePicture) {
//             formData.append("profile_picture", profilePicture);
//         }

//         fetch("/tutors/tutor-profile/", {
//             method: "POST",

//             headers: {
//                 "X-CSRFToken": document.querySelector(
//                     "[name=csrfmiddlewaretoken]"
//                 ).value
//             },

//             body: formData
//         })
//             .then(response => response.json())
//             .then(data => {

//                 if (data.success) {

//                     console.log("Personal information saved.");

//                     // Only move to next step after successful save
//                     showStep(2);

//                 } else {

//                     alert(data.message);

//                 }

//             })
//             .catch(error => {

//                 console.error(error);

//                 alert("Something went wrong while saving.");

//             });

//     });


/* Location → Personal */

document
    .getElementById("backLocation")
    .addEventListener("click", function () {

        showStep(1);

    });


/* Location → About */

document
    .getElementById("nextLocation")
    .addEventListener("click", function () {

        const formData = new FormData();

        formData.append(
            "section",
            "location"
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
            document.querySelector(
                '[name="description"]'
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

        showStep(5);

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
        showStep(6);
    });


/* CV → Certification */

document
    .getElementById("backCV")
    .addEventListener("click", function () {

        showStep(5);

    });


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


