document.addEventListener("DOMContentLoaded", () => {
    const desktopToggle = document.getElementById(
        "rmrsRobustnessDesktopToggle"
    );

    const mobileButton = document.getElementById(
        "rmrsRobustnessMobileButton"
    );

    const sheet = document.getElementById(
        "rmrsRobustnessSheet"
    );

    const sheetToggle = document.getElementById(
        "rmrsRobustnessSheetToggle"
    );

    if (!desktopToggle || !mobileButton || !sheet) {
        return;
    }

    const closeButtons = sheet.querySelectorAll(
        "[data-robustness-close]"
    );

    const dialogPanel = sheet.querySelector(
        ".rmrs-robustness-sheet-panel"
    );

    const closeButton = sheet.querySelector(
        ".rmrs-robustness-sheet-close"
    );

    const getCookie = (name) => {
        const cookie = document.cookie
            .split(";")
            .map((item) => item.trim())
            .find((item) => item.startsWith(`${name}=`));

        if (!cookie) {
            return "";
        }

        return decodeURIComponent(
            cookie.substring(name.length + 1)
        );
    };

    const toggleRobustness = async () => {
        desktopToggle.disabled = true;

        if (sheetToggle) {
            sheetToggle.disabled = true;
        }

        try {
            const response = await fetch(
                "/recommendations/toggle-robustness/",
                {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "X-Requested-With": "XMLHttpRequest",
                    },
                }
            );

            if (!response.ok) {
                throw new Error(
                    `Robustness toggle failed (${response.status}).`
                );
            }

            /*
             * Reload after the backend updates the session.
             *
             * A later frontend batch will add the short visual
             * recommendation transition required by the final UI.
             */
            sessionStorage.setItem(
                "rmrsRobustnessModeChanged",
                "true"
            );

            window.location.reload();

        } catch (error) {
            console.error(error);

            desktopToggle.disabled = false;

            if (sheetToggle) {
                sheetToggle.disabled = false;
            }
        }
    };

    const openSheet = () => {
        sheet.hidden = false;

        mobileButton.setAttribute(
            "aria-expanded",
            "true"
        );

        /*
         * Move keyboard focus into the dialog.
         */
        window.requestAnimationFrame(() => {
            if (closeButton) {
                closeButton.focus();
            } else if (sheetToggle) {
                sheetToggle.focus();
            }
        });
    };

    const closeSheet = () => {
        sheet.hidden = true;

        mobileButton.setAttribute(
            "aria-expanded",
            "false"
        );

        /*
         * Return keyboard focus to the button
         * that opened the dialog.
         */
        mobileButton.focus();
    };

    const getFocusableElements = () => {
        if (!dialogPanel) {
            return [];
        }

        return Array.from(
            dialogPanel.querySelectorAll(
                [
                    "button:not([disabled])",
                    "a[href]",
                    "input:not([disabled])",
                    "select:not([disabled])",
                    "textarea:not([disabled])",
                    '[tabindex]:not([tabindex="-1"])',
                ].join(",")
            )
        );
    };

    const trapDialogFocus = (event) => {
        if (
            event.key !== "Tab"
            || sheet.hidden
        ) {
            return;
        }

        const focusableElements =
            getFocusableElements();

        if (!focusableElements.length) {
            event.preventDefault();
            return;
        }

        const firstElement =
            focusableElements[0];

        const lastElement =
            focusableElements[
                focusableElements.length - 1
            ];

        if (
            event.shiftKey
            && document.activeElement
                === firstElement
        ) {
            event.preventDefault();
            lastElement.focus();
            return;
        }

        if (
            !event.shiftKey
            && document.activeElement
                === lastElement
        ) {
            event.preventDefault();
            firstElement.focus();
        }
    };

    desktopToggle.addEventListener(
        "click",
        toggleRobustness
    );

    mobileButton.addEventListener(
        "click",
        openSheet
    );

    if (sheetToggle) {
        sheetToggle.addEventListener(
            "click",
            toggleRobustness
        );
    }

    closeButtons.forEach((button) => {
        button.addEventListener(
            "click",
            closeSheet
        );
    });

    document.addEventListener(
        "keydown",
        (event) => {
            if (
                event.key === "Escape"
                && !sheet.hidden
            ) {
                event.preventDefault();
                closeSheet();
                return;
            }

            trapDialogFocus(event);
        }
    );

    const modeChanged =
    sessionStorage.getItem("rmrsRobustnessModeChanged");

    if (modeChanged === "true") {
        sessionStorage.removeItem(
            "rmrsRobustnessModeChanged"
        );

        const recommendationPanel =
            document.querySelector(".recommendation-panel");

        if (recommendationPanel) {
            recommendationPanel.classList.add(
                "rmrs-rank-transition"
            );

            window.setTimeout(() => {
                recommendationPanel.classList.remove(
                    "rmrs-rank-transition"
                );
            }, 450);
        }
    }
});