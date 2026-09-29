document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // ELEMENTS
    // =========================================================

    const daySelect = document.getElementById("daySelect");
    const addTimeBtn = document.getElementById("addTimeBtn");
    const daysContainer = document.getElementById("daysContainer");
    const emptyState = document.getElementById("emptyState");
    const slotCount = document.getElementById("slotCount");
    const saveAvailability =
        document.getElementById("saveAvailability");


    // =========================================================
    // AVAILABILITY DATA
    // =========================================================

    /*
        Example:

        availabilityData = {
            sunday: [
                {
                    start: "07:00",
                    end: "09:00"
                },
                {
                    start: "16:00",
                    end: "18:00"
                }
            ],

            monday: [
                {
                    start: "10:00",
                    end: "12:00"
                }
            ]
        }
    */

    let availabilityData = {};


    // =========================================================
    // ADD FIRST TIME SLOT FOR A DAY
    // =========================================================

    addTimeBtn.addEventListener("click", function () {

        const day = daySelect.value;


        // No day selected
        if (!day) {

            alert("Please select a day first.");

            return;
        }


        // Create the day if it doesn't exist
        if (!availabilityData[day]) {

            availabilityData[day] = [];
        }


        // Add empty time slot
        availabilityData[day].push({
            start: "",
            end: ""
        });


        // Display the day
        renderDay(day);


        // Update count
        updateCount();


        // Optional:
        // Reset dropdown so user can select another day
        daySelect.value = "";

    });


    // =========================================================
    // RENDER DAY
    // =========================================================

    function renderDay(day) {

        let dayCard =
            daysContainer.querySelector(
                `[data-day="${day}"]`
            );


        // -----------------------------------------------------
        // CREATE DAY CARD IF IT DOES NOT EXIST
        // -----------------------------------------------------

        if (!dayCard) {

            dayCard = document.createElement("div");

            dayCard.className = "day-card";

            dayCard.dataset.day = day;


            dayCard.innerHTML = `

                <div class="day-header">

                    <div class="day-name">
                        ${capitalize(day)}
                    </div>

                </div>

                <div class="day-slots"></div>

                <button
                    type="button"
                    class="add-another-slot"
                    data-day="${day}"
                >
                    + Add another slot
                </button>

            `;


            daysContainer.appendChild(dayCard);


            // -------------------------------------------------
            // ADD ANOTHER SLOT BUTTON
            // -------------------------------------------------

            const addAnotherButton =
                dayCard.querySelector(
                    ".add-another-slot"
                );


            addAnotherButton.addEventListener(
                "click",
                function () {

                    addAnotherSlot(day);

                }
            );
        }


        // -----------------------------------------------------
        // GET SLOT CONTAINER
        // -----------------------------------------------------

        const slotsContainer =
            dayCard.querySelector(".day-slots");


        // Clear current slots
        slotsContainer.innerHTML = "";


        // -----------------------------------------------------
        // CREATE EACH TIME SLOT
        // -----------------------------------------------------

        availabilityData[day].forEach(
            function (slot, index) {

                const slotElement =
                    document.createElement("div");


                slotElement.className = "time-slot";


                slotElement.innerHTML = `

                    <input
                        type="time"
                        class="start-time"
                        value="${slot.start}"
                    >

                    <span class="time-arrow">
                        →
                    </span>

                    <input
                        type="time"
                        class="end-time"
                        value="${slot.end}"
                    >

                    <button
                        type="button"
                        class="remove-slot"
                        title="Remove this time slot"
                    >
                        ×
                    </button>

                `;


                // -------------------------------------------------
                // START TIME
                // -------------------------------------------------

                const startInput =
                    slotElement.querySelector(
                        ".start-time"
                    );


                startInput.addEventListener(
                    "change",
                    function () {

                        availabilityData[day][index].start =
                            this.value;


                        validateSlot(day, index);

                    }
                );


                // -------------------------------------------------
                // END TIME
                // -------------------------------------------------

                const endInput =
                    slotElement.querySelector(
                        ".end-time"
                    );


                endInput.addEventListener(
                    "change",
                    function () {

                        availabilityData[day][index].end =
                            this.value;


                        validateSlot(day, index);

                    }
                );


                // -------------------------------------------------
                // REMOVE SLOT
                // -------------------------------------------------

                const removeButton =
                    slotElement.querySelector(
                        ".remove-slot"
                    );


                removeButton.addEventListener(
                    "click",
                    function () {

                        removeSlot(day, index);

                    }
                );


                // -------------------------------------------------
                // ADD SLOT TO DOM
                // -------------------------------------------------

                slotsContainer.appendChild(
                    slotElement
                );

            }
        );


        // Update empty state
        updateEmptyState();

    }


    // =========================================================
    // ADD ANOTHER SLOT TO EXISTING DAY
    // =========================================================

    function addAnotherSlot(day) {

        // Safety check
        if (!availabilityData[day]) {

            availabilityData[day] = [];

        }


        // Add empty slot
        availabilityData[day].push({

            start: "",

            end: ""

        });


        // Re-render day
        renderDay(day);


        // Update count
        updateCount();


        // Focus the new start input
        const dayCard =
            daysContainer.querySelector(
                `[data-day="${day}"]`
            );


        if (dayCard) {

            const inputs =
                dayCard.querySelectorAll(
                    ".start-time"
                );


            const lastInput =
                inputs[inputs.length - 1];


            if (lastInput) {

                lastInput.focus();

            }

        }

    }


    // =========================================================
    // REMOVE SLOT
    // =========================================================

    function removeSlot(day, index) {

        if (!availabilityData[day]) {

            return;

        }


        // Remove slot from JavaScript data
        availabilityData[day].splice(index, 1);


        // -----------------------------------------------------
        // IF NO SLOTS LEFT
        // -----------------------------------------------------

        if (availabilityData[day].length === 0) {

            // Remove entire day from data
            delete availabilityData[day];


            // Remove day card from UI
            const dayCard =
                daysContainer.querySelector(
                    `[data-day="${day}"]`
                );


            if (dayCard) {

                dayCard.remove();

            }

        }

        else {

            // Re-render remaining slots
            renderDay(day);

        }


        // Update counter
        updateCount();


        // Update empty state
        updateEmptyState();

    }


    // =========================================================
    // VALIDATE TIME SLOT
    // =========================================================

    function validateSlot(day, index) {

        const slot =
            availabilityData[day][index];


        // Don't validate until both values exist
        if (!slot.start || !slot.end) {

            return true;

        }


        // End must be after start
        if (slot.start >= slot.end) {

            alert(
                "End time must be after start time."
            );


            // Clear invalid end time
            availabilityData[day][index].end = "";


            // Re-render
            renderDay(day);


            return false;

        }


        // Check overlapping slots
        if (hasOverlap(day, index)) {

            alert(
                "This time slot overlaps with another slot."
            );


            // Clear current slot
            availabilityData[day][index].start = "";
            availabilityData[day][index].end = "";


            renderDay(day);


            return false;

        }


        return true;

    }


    // =========================================================
    // CHECK OVERLAPPING TIME SLOTS
    // =========================================================

    function hasOverlap(day, currentIndex) {

        const current =
            availabilityData[day][currentIndex];


        if (!current.start || !current.end) {

            return false;

        }


        for (
            let i = 0;
            i < availabilityData[day].length;
            i++
        ) {

            // Don't compare with itself
            if (i === currentIndex) {

                continue;

            }


            const other =
                availabilityData[day][i];


            if (!other.start || !other.end) {

                continue;

            }


            /*
                Overlap condition:

                Current starts before other ends
                AND
                Current ends after other starts
            */

            if (
                current.start < other.end &&
                current.end > other.start
            ) {

                return true;

            }

        }


        return false;

    }


    // =========================================================
    // UPDATE SLOT COUNT
    // =========================================================

    function updateCount() {

        let count = 0;


        Object.values(availabilityData)
            .forEach(function (slots) {

                count += slots.length;

            });


        if (count === 1) {

            slotCount.textContent = "1 slot";

        }

        else {

            slotCount.textContent =
                count + " slots";

        }


        updateEmptyState();

    }


    // =========================================================
    // EMPTY STATE
    // =========================================================

    function updateEmptyState() {

        const hasData =
            Object.keys(availabilityData).length > 0;


        if (hasData) {

            emptyState.style.display = "none";

        }

        else {

            emptyState.style.display = "block";

        }

    }


    // =========================================================
    // CAPITALIZE DAY
    // =========================================================

    function capitalize(value) {

        return value.charAt(0).toUpperCase()
            + value.slice(1);

    }


    // =========================================================
    // GET CSRF TOKEN
    // =========================================================

    function getCSRFToken() {

        const csrfInput =
            document.querySelector(
                "[name=csrfmiddlewaretoken]"
            );


        if (!csrfInput) {

            console.error(
                "CSRF token not found."
            );

            return "";

        }


        return csrfInput.value;

    }


    // =========================================================
    // SAVE AVAILABILITY
    // =========================================================

    saveAvailability.addEventListener(
        "click",
        function () {

            // -------------------------------------------------
            // CHECK WHETHER DATA EXISTS
            // -------------------------------------------------

            if (
                Object.keys(availabilityData)
                    .length === 0
            ) {

                alert(
                    "Please add at least one availability slot."
                );

                return;

            }


            // -------------------------------------------------
            // CHECK FOR EMPTY TIME SLOTS
            // -------------------------------------------------

            for (
                const day in availabilityData
            ) {

                const slots =
                    availabilityData[day];


                for (
                    let i = 0;
                    i < slots.length;
                    i++
                ) {

                    const slot = slots[i];


                    if (
                        !slot.start ||
                        !slot.end
                    ) {

                        alert(
                            `Please complete the time slot for ${capitalize(day)}.`
                        );

                        return;

                    }


                    if (slot.start >= slot.end) {

                        alert(
                            `Invalid time for ${capitalize(day)}.`
                        );

                        return;

                    }

                }

            }


            // -------------------------------------------------
            // SEND DATA TO DJANGO
            // -------------------------------------------------

            fetch(
                "/tutors/save-availability/",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "X-CSRFToken":
                            getCSRFToken()

                    },

                    body: JSON.stringify({

                        availability:
                            availabilityData

                    })

                }
            )


            // -------------------------------------------------
            // RESPONSE
            // -------------------------------------------------

            .then(function (response) {

                if (!response.ok) {

                    throw new Error(
                        "Server error."
                    );

                }


                return response.json();

            })


            // -------------------------------------------------
            // SUCCESS
            // -------------------------------------------------

            .then(function (data) {

                if (data.success) {

                    alert(
                        "Availability saved successfully."
                    );


                    console.log(
                        "Saved data:",
                        availabilityData
                    );

                }

                else {

                    alert(
                        data.message ||
                        "Unable to save availability."
                    );

                }

            })


            // -------------------------------------------------
            // ERROR
            // -------------------------------------------------

            .catch(function (error) {

                console.error(
                    "Error:",
                    error
                );


                alert(
                    "Something went wrong while saving availability."
                );

            });

        }
    );


});