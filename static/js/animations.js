document.addEventListener("DOMContentLoaded", function () {
    setupMovieRows();
    setupAnimations();
});


function setupMovieRows() {
    const rows = document.querySelectorAll(".horizontal-movie-row");

    rows.forEach(function (row) {
        if (row.dataset.carouselReady === "true") {
            return;
        }

        row.dataset.carouselReady = "true";

        const shell = document.createElement("div");
        shell.className = "movie-carousel-shell";

        row.parentNode.insertBefore(shell, row);
        shell.appendChild(row);

        const previousButton = document.createElement("button");
        previousButton.type = "button";
        previousButton.className = "movie-scroll-button prev";
        previousButton.setAttribute("aria-label", "Previous movies");
        previousButton.textContent = "‹";

        const nextButton = document.createElement("button");
        nextButton.type = "button";
        nextButton.className = "movie-scroll-button next";
        nextButton.setAttribute("aria-label", "More movies");
        nextButton.textContent = "›";

        shell.appendChild(previousButton);
        shell.appendChild(nextButton);

        previousButton.addEventListener("click", function () {
            row.scrollBy({
                left: -Math.max(row.clientWidth * 0.8, 250),
                behavior: "smooth"
            });
        });

        nextButton.addEventListener("click", function () {
            row.scrollBy({
                left: Math.max(row.clientWidth * 0.8, 250),
                behavior: "smooth"
            });
        });

        function updateButtons() {
            const maxScroll = row.scrollWidth - row.clientWidth;

            previousButton.style.display =
                row.scrollLeft > 5 ? "grid" : "none";

            nextButton.style.display =
                row.scrollLeft < maxScroll - 5 ? "grid" : "none";
        }

        row.addEventListener("scroll", updateButtons);
        window.addEventListener("resize", updateButtons);

        updateButtons();
    });
}


function setupAnimations() {
    if (typeof window.gsap === "undefined") {
        return;
    }

    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    if (reduceMotion) {
        return;
    }

    gsap.from(".rmrs-navbar", {
        y: -15,
        opacity: 0,
        duration: 0.5,
        ease: "power2.out"
    });

    const heroItems = document.querySelectorAll(
        ".stream-hero-content > *"
    );

    if (heroItems.length > 0) {
        gsap.from(heroItems, {
            y: 20,
            opacity: 0,
            duration: 0.6,
            stagger: 0.08,
            ease: "power2.out"
        });
    }
}