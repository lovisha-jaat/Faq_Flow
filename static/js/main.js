/* =========================================================
   FAQFLOW AI
   GLOBAL JAVASCRIPT
========================================================= */

document.addEventListener("DOMContentLoaded", function () {
    initializeFlashMessages();
    initializeMobileNavigation();
    initializeExternalLinks();
    initializeFormProtection();
});


/* =========================================================
   FLASH MESSAGE AUTO HIDE
========================================================= */

function initializeFlashMessages() {
    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert, index) {
        setTimeout(function () {
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            alert.style.transition = "all 0.3s ease";

            setTimeout(function () {
                alert.remove();
            }, 300);
        }, 3500 + index * 400);
    });
}


/* =========================================================
   MOBILE NAVIGATION
========================================================= */

function initializeMobileNavigation() {
    const navbar = document.querySelector(".navbar");
    const navList = document.querySelector(".navbar ul");

    if (!navbar || !navList) {
        return;
    }

    const menuButton = document.createElement("button");

    menuButton.type = "button";
    menuButton.className = "mobile-menu-button";
    menuButton.setAttribute("aria-label", "Open navigation menu");

    menuButton.innerHTML = `
        <i class="fa-solid fa-bars"></i>
    `;

    navbar.querySelector(".container").appendChild(menuButton);

    menuButton.addEventListener("click", function () {
        navList.classList.toggle("mobile-nav-open");

        const icon = menuButton.querySelector("i");

        if (navList.classList.contains("mobile-nav-open")) {
            icon.classList.remove("fa-bars");
            icon.classList.add("fa-xmark");

            menuButton.setAttribute(
                "aria-label",
                "Close navigation menu"
            );
        } else {
            icon.classList.remove("fa-xmark");
            icon.classList.add("fa-bars");

            menuButton.setAttribute(
                "aria-label",
                "Open navigation menu"
            );
        }
    });

    document.addEventListener("click", function (event) {
        const clickedInsideNavbar = navbar.contains(event.target);

        if (!clickedInsideNavbar) {
            navList.classList.remove("mobile-nav-open");

            const icon = menuButton.querySelector("i");

            icon.classList.remove("fa-xmark");
            icon.classList.add("fa-bars");
        }
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 700) {
            navList.classList.remove("mobile-nav-open");

            const icon = menuButton.querySelector("i");

            icon.classList.remove("fa-xmark");
            icon.classList.add("fa-bars");
        }
    });
}


/* =========================================================
   EXTERNAL LINKS
========================================================= */

function initializeExternalLinks() {
    const externalLinks = document.querySelectorAll(
        'a[target="_blank"]'
    );

    externalLinks.forEach(function (link) {
        if (!link.hasAttribute("rel")) {
            link.setAttribute(
                "rel",
                "noopener noreferrer"
            );
        }
    });
}


/* =========================================================
   FORM DOUBLE-SUBMIT PROTECTION
========================================================= */

function initializeFormProtection() {
    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {
        form.addEventListener("submit", function () {
            const submitButton = form.querySelector(
                'button[type="submit"]'
            );

            if (!submitButton) {
                return;
            }

            if (submitButton.dataset.allowMultipleSubmit === "true") {
                return;
            }

            setTimeout(function () {
                submitButton.disabled = true;
            }, 20);
        });
    });
}


/* =========================================================
   COPY TEXT HELPER
========================================================= */

async function copyTextToClipboard(text) {
    if (!text) {
        return false;
    }

    try {
        await navigator.clipboard.writeText(text);

        return true;
    } catch (error) {
        const temporaryTextArea =
            document.createElement("textarea");

        temporaryTextArea.value = text;

        temporaryTextArea.style.position = "fixed";
        temporaryTextArea.style.left = "-9999px";
        temporaryTextArea.style.opacity = "0";

        document.body.appendChild(
            temporaryTextArea
        );

        temporaryTextArea.select();

        const copied = document.execCommand("copy");

        temporaryTextArea.remove();

        return copied;
    }
}


/* =========================================================
   SHOW GLOBAL MESSAGE
========================================================= */

function showGlobalMessage(
    message,
    type = "success",
    duration = 3000
) {
    const existingMessage =
        document.querySelector(".global-message");

    if (existingMessage) {
        existingMessage.remove();
    }

    const messageElement =
        document.createElement("div");

    messageElement.className =
        `global-message global-message-${type}`;

    let iconClass = "fa-circle-check";

    if (type === "error") {
        iconClass = "fa-circle-exclamation";
    }

    if (type === "warning") {
        iconClass = "fa-triangle-exclamation";
    }

    messageElement.innerHTML = `
        <i class="fa-solid ${iconClass}"></i>
        <span></span>
        <button
            type="button"
            aria-label="Close message"
        >
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;

    messageElement.querySelector("span").textContent =
        message;

    document.body.appendChild(messageElement);

    requestAnimationFrame(function () {
        messageElement.classList.add("show");
    });

    const closeButton =
        messageElement.querySelector("button");

    closeButton.addEventListener("click", function () {
        removeGlobalMessage(messageElement);
    });

    setTimeout(function () {
        removeGlobalMessage(messageElement);
    }, duration);
}


function removeGlobalMessage(messageElement) {
    if (!messageElement) {
        return;
    }

    messageElement.classList.remove("show");

    setTimeout(function () {
        messageElement.remove();
    }, 250);
}


/* =========================================================
   CONFIRM ACTION HELPER
========================================================= */

function confirmAction(message) {
    return window.confirm(
        message || "Are you sure?"
    );
}


/* =========================================================
   AUTO RESIZE TEXTAREA
========================================================= */

function autoResizeTextarea(textarea) {
    if (!textarea) {
        return;
    }

    textarea.style.height = "auto";

    textarea.style.height =
        Math.min(textarea.scrollHeight, 160) + "px";
}


/* =========================================================
   FORMAT CURRENT TIME
========================================================= */

function getCurrentTime() {
    return new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}