document.addEventListener("DOMContentLoaded", function () {

    /* =========================
       🌙 THEME TOGGLE
    ========================= */

    const toggleBtn = document.getElementById("themeToggle");

    if (toggleBtn) {
        console.log("✅ Theme JS Loaded");

        // Load saved theme
        if (localStorage.getItem("theme") === "dark") {
            document.body.classList.add("dark-mode");
            toggleBtn.innerText = "☀️ Light Mode";
        } else {
            toggleBtn.innerText = "🌙 Dark Mode";
        }

        toggleBtn.addEventListener("click", function () {
            document.body.classList.toggle("dark-mode");

            if (document.body.classList.contains("dark-mode")) {
                localStorage.setItem("theme", "dark");
                toggleBtn.innerText = "☀️ Light Mode";
            } else {
                localStorage.setItem("theme", "light");
                toggleBtn.innerText = "🌙 Dark Mode";
            }
        });

    } else {
        console.log("❌ Theme button not found");
    }


    /* =========================
       🔍 SEARCH FILTER
    ========================= */

    const searchInput = document.getElementById("searchInput");

    if (searchInput) {
        searchInput.addEventListener("keyup", function () {
            let value = this.value.toLowerCase();
            let cards = document.querySelectorAll(".book-wrapper");

            cards.forEach(card => {
                let text = card.innerText.toLowerCase();
                card.style.display = text.includes(value) ? "" : "none";
            });
        });
    }

});