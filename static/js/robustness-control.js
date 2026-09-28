document.addEventListener("DOMContentLoaded", () => {
    const openButton = document.getElementById(
        "rmrsRobustnessMobileButton"
    );

    const sheet = document.getElementById(
        "rmrsRobustnessSheet"
    );

    if (!openButton || !sheet) {
        return;
    }

    const closeButtons = sheet.querySelectorAll(
        "[data-robustness-close]"
    );

    const openSheet = () => {
        sheet.hidden = false;
        openButton.setAttribute("aria-expanded", "true");

        const closeButton = sheet.querySelector(
            ".rmrs-robustness-sheet-close"
        );

        if (closeButton) {
            closeButton.focus();
        }
    };


    const closeSheet = () => {
        sheet.hidden = true;
        openButton.setAttribute("aria-expanded", "false");
        openButton.focus();
    };


    openButton.addEventListener(
        "click",
        openSheet
    );


    closeButtons.forEach((button) => {
        button.addEventListener(
            "click",
            closeSheet
        );
    });


    document.addEventListener("keydown", (event) => {
        if (
            event.key === "Escape"
            && !sheet.hidden
        ) {
            closeSheet();
        }
    });
});