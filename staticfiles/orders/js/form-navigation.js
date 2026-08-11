document.addEventListener("keydown", function (event) {

    // Only handle Enter
    if (event.key !== "Enter") {
        return;
    }

    const current = event.target;

    // Don't interfere with textareas
    if (current.tagName === "TEXTAREA") {
        return;
    }

    // Find the form containing the current field
    const form = current.closest("form");

    if (!form) {
        return;
    }

    // Get all usable form fields in their HTML order
    const fields = Array.from(
        form.querySelectorAll(
            "input:not([type='hidden']):not([disabled]), " +
            "select:not([disabled]), " +
            "textarea:not([disabled])"
        )
    );

    const currentIndex = fields.indexOf(current);

    // Current element isn't a form field
    if (currentIndex === -1) {
        return;
    }

    // Stop Enter from submitting the form
    event.preventDefault();

    // Find the next field
    const nextField = fields[currentIndex + 1];

    if (nextField) {

        nextField.focus();

        // Select existing text for text inputs
        if (
            nextField.tagName === "INPUT" &&
            (
                nextField.type === "text" ||
                nextField.type === "number"
            )
        ) {
            nextField.select();
        }

        return;
    }

    // If this is the last field, submit the form
    form.requestSubmit();
});
