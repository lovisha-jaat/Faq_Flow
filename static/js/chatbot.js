/* =========================================================
   FAQFLOW AI
   CHATBOT JAVASCRIPT
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    initializeChatbot();
    initializeSuggestedQuestions();
    initializeTextareaResize();
    initializeChatPreview();
    initializeWidget();
    initializeCopyButtons();

});


/* =========================================================
   CHATBOT
========================================================= */

function initializeChatbot() {

    const form = document.getElementById("chatForm");

    if (!form) return;

    form.addEventListener("submit", sendMessage);

}


async function sendMessage(event) {

    event.preventDefault();

    const input = document.getElementById("chatInput");
    const messages = document.getElementById("chatMessages");

    const text = input.value.trim();

    if (text === "") return;

    appendUserMessage(text);

    input.value = "";

    showTyping();

    try {

        const response = await fetch("/chatbot/message", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: text

            })

        });

        const data = await response.json();

        removeTyping();

        appendBotMessage(data.answer);

    }

    catch {

        removeTyping();

        appendBotMessage(
            "Sorry, something went wrong."
        );

    }

}


/* =========================================================
   USER MESSAGE
========================================================= */

function appendUserMessage(message) {

    const container =
        document.getElementById("chatMessages");

    container.insertAdjacentHTML(

        "beforeend",

        `
        <div class="user-chat-message chatbot-message">

            <div class="message-avatar">
                <i class="fa-solid fa-user"></i>
            </div>

            <div class="message-wrapper">

                <div class="message-bubble">

                    <p>${escapeHtml(message)}</p>

                </div>

                <span class="message-time">

                    ${getCurrentTime()}

                </span>

            </div>

        </div>
        `
    );

    scrollBottom();

}


/* =========================================================
   BOT MESSAGE
========================================================= */

function appendBotMessage(message) {

    const container =
        document.getElementById("chatMessages");

    container.insertAdjacentHTML(

        "beforeend",

        `
        <div class="chatbot-message">

            <div class="message-avatar">

                <i class="fa-solid fa-robot"></i>

            </div>

            <div class="message-wrapper">

                <div class="message-bubble">

                    <p>${escapeHtml(message)}</p>

                </div>

                <span class="message-time">

                    ${getCurrentTime()}

                </span>

            </div>

        </div>
        `
    );

    scrollBottom();

}


/* =========================================================
   TYPING
========================================================= */

function showTyping() {

    const container =
        document.getElementById("chatMessages");

    container.insertAdjacentHTML(

        "beforeend",

        `
        <div
            class="typing-message chatbot-message"
            id="typingAnimation"
        >

            <div class="message-avatar">

                <i class="fa-solid fa-robot"></i>

            </div>

            <div class="message-wrapper">

                <div class="message-bubble">

                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>

                </div>

            </div>

        </div>
        `
    );

    scrollBottom();

}


function removeTyping() {

    const typing =
        document.getElementById(
            "typingAnimation"
        );

    if (typing) {

        typing.remove();

    }

}


/* =========================================================
   SUGGESTIONS
========================================================= */

function initializeSuggestedQuestions() {

    document.querySelectorAll(
        ".suggested-question"
    ).forEach(function (button) {

        button.addEventListener(

            "click",

            function () {

                document.getElementById(
                    "chatInput"
                ).value =
                    this.innerText;

            }

        );

    });

}


/* =========================================================
   AUTO RESIZE
========================================================= */

function initializeTextareaResize() {

    const textarea =
        document.getElementById(
            "chatInput"
        );

    if (!textarea) return;

    textarea.addEventListener(

        "input",

        function () {

            autoResizeTextarea(this);

        }

    );

}


/* =========================================================
   CHAT PREVIEW
========================================================= */

function initializeChatPreview() {

    const toggle =
        document.getElementById(
            "previewToggle"
        );

    const widget =
        document.getElementById(
            "previewWidget"
        );

    if (!toggle || !widget) return;

    toggle.addEventListener(

        "click",

        function () {

            widget.classList.toggle("show");

        }

    );

}


/* =========================================================
   WEBSITE WIDGET
========================================================= */

function initializeWidget() {

    const widgetButton =
        document.getElementById(
            "widgetButton"
        );

    const widget =
        document.getElementById(
            "websiteWidget"
        );

    if (!widgetButton || !widget) return;

    widgetButton.addEventListener(

        "click",

        function () {

            widget.classList.toggle("show");

        }

    );

}


/* =========================================================
   COPY CODE
========================================================= */

function initializeCopyButtons() {

    document.querySelectorAll(

        ".copy-code-button"

    ).forEach(function (button) {

        button.addEventListener(

            "click",

            async function () {

                const code =
                    this.closest(
                        ".integration-code-wrapper"
                    )
                    .querySelector("pre")
                    .innerText;

                const copied =
                    await copyTextToClipboard(
                        code
                    );

                if (copied) {

                    this.innerHTML =

                        `<i class="fa-solid fa-check"></i> Copied`;

                    this.classList.add("copied");

                    setTimeout(() => {

                        this.innerHTML =

                            `<i class="fa-solid fa-copy"></i> Copy`;

                        this.classList.remove("copied");

                    }, 2000);

                }

            }

        );

    });

}


/* =========================================================
   HELPERS
========================================================= */

function scrollBottom() {

    const messages =
        document.getElementById(
            "chatMessages"
        );

    if (!messages) return;

    messages.scrollTop =
        messages.scrollHeight;

}


function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}