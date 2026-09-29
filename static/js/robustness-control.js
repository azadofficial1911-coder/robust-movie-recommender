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
        mobileButton.setAttribute("aria-expanded", "true");
    };

    const closeSheet = () => {
        sheet.hidden = true;
        mobileButton.setAttribute("aria-expanded", "false");
        mobileButton.focus();
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

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !sheet.hidden) {
            closeSheet();
        }
    });
});
