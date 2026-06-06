// main.js — students will add JavaScript here as features are built

(function () {
    "use strict";

    // ---------- Video modal ("See how it works") ----------
    var modal = document.getElementById("videoModal");
    var iframe = document.getElementById("videoModalIframe");
    var openBtn = document.querySelector(".hero-cta-secondary");

    if (modal && iframe && openBtn) {
        var originalSrc = iframe.getAttribute("data-src") || "";

        function openModal() {
            // Attach the YouTube src with autoplay only on open,
            // so the video never starts until the user clicks the button.
            iframe.setAttribute("src", originalSrc + "?autoplay=1&rel=0");
            modal.hidden = false;
            modal.setAttribute("aria-hidden", "false");
            document.body.style.overflow = "hidden";
        }

        function closeModal() {
            // Clearing src stops playback and resets the player state.
            iframe.setAttribute("src", "");
            modal.hidden = true;
            modal.setAttribute("aria-hidden", "true");
            document.body.style.overflow = "";
        }

        openBtn.addEventListener("click", openModal);

        // Close on any element marked with [data-modal-close]
        // (the backdrop and the X button).
        modal.querySelectorAll("[data-modal-close]").forEach(function (el) {
            el.addEventListener("click", closeModal);
        });

        // Close on Escape key.
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && !modal.hidden) {
                closeModal();
            }
        });
    }
})();
