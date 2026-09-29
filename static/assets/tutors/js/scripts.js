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

document
    .getElementById("nextPersonal")
    .addEventListener("click", function () {

        showStep(2);

    });


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

        showStep(3);

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

        showStep(4);

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