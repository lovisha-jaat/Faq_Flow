/* =========================================================
   FAQFLOW AI - CHATBOT
========================================================= */

document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chatForm");
    const questionInput = document.getElementById("questionInput");
    const chatMessages = document.getElementById("chatMessages");
    const sendButton = document.getElementById("sendMessageButton");
    const clearButton = document.getElementById("clearChatButton");
    const characterCount = document.getElementById(
        "chatCharacterCount"
    );

    const suggestedButtons = document.querySelectorAll(
        ".suggested-question"
    );

    if (
        !chatForm ||
        !questionInput ||
        !chatMessages ||
        !sendButton
    ) {
        console.error(
            "FAQFlow: Chatbot HTML elements were not found."
        );
        return;
    }

    const config = window.FAQFLOW_CONFIG || {};

    const apiUrl = config.apiUrl || "/api/chat";
    const companyId = config.companyId;

    console.log("FAQFlow API URL:", apiUrl);
    console.log("FAQFlow Company ID:", companyId);


    function getCurrentTime() {
        return new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });
    }


    function scrollToBottom() {
        chatMessages.scrollTop =
            chatMessages.scrollHeight;
    }


    function updateCharacterCount() {
        if (characterCount) {
            characterCount.textContent =
                questionInput.value.length + " / 500";
        }
    }


    function resizeTextarea() {
        questionInput.style.height = "auto";

        questionInput.style.height =
            Math.min(
                questionInput.scrollHeight,
                130
            ) + "px";
    }


    function appendUserMessage(message) {
        const row = document.createElement("div");

        row.className =
            "chatbot-message user-chat-message";

        row.innerHTML = `
            <div class="message-avatar">
                <i class="fa-solid fa-user"></i>
            </div>

            <div class="message-wrapper">
                <div class="message-bubble">
                    <p></p>
                </div>

                <span class="message-time"></span>
            </div>
        `;

        row.querySelector("p").textContent =
            message;

        row.querySelector(".message-time").textContent =
            getCurrentTime();

        chatMessages.appendChild(row);

        scrollToBottom();
    }


    function appendBotMessage(message, data = {}) {
        const row = document.createElement("div");

        row.className =
            "chatbot-message bot-chat-message";

        if (data.status === "unanswered") {
            row.classList.add(
                "chatbot-response-unanswered"
            );
        }

        row.innerHTML = `
            <div class="message-avatar">
                <i class="fa-solid fa-robot"></i>
            </div>

            <div class="message-wrapper">
                <div class="message-bubble">
                    <p></p>
                </div>

                <span class="message-time"></span>
            </div>
        `;

        row.querySelector("p").textContent =
            message;

        row.querySelector(".message-time").textContent =
            getCurrentTime();

        if (
            data.category &&
            data.category !== "Unknown"
        ) {
            const category =
                document.createElement("span");

            category.className =
                "message-category";

            category.textContent =
                data.category;

            row.querySelector(
                ".message-wrapper"
            ).insertBefore(
                category,
                row.querySelector(".message-time")
            );
        }

        chatMessages.appendChild(row);

        scrollToBottom();
    }


    function showTypingIndicator() {
        const typing = document.createElement("div");

        typing.id = "chatbotTypingIndicator";

        typing.className =
            "chatbot-message bot-chat-message typing-message";

        typing.innerHTML = `
            <div class="message-avatar">
                <i class="fa-solid fa-robot"></i>
            </div>

            <div class="message-wrapper">
                <div class="message-bubble">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            </div>
        `;

        chatMessages.appendChild(typing);

        scrollToBottom();

        return typing;
    }


    async function sendQuestion(question) {
        if (!question) {
            return;
        }

        if (!companyId) {
            appendBotMessage(
                "Company ID is missing. Please log in again."
            );
            return;
        }

        appendUserMessage(question);

        questionInput.value = "";
        questionInput.disabled = true;
        sendButton.disabled = true;

        updateCharacterCount();
        resizeTextarea();

        const typingIndicator =
            showTypingIndicator();

        try {
            const response = await fetch(apiUrl, {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    company_id: companyId,
                    question: question
                })
            });

            const data = await response.json();

            typingIndicator.remove();

            console.log("Chatbot response:", data);

            if (!response.ok) {
                throw new Error(
                    data.message ||
                    data.error ||
                    "Unable to get an answer."
                );
            }

            appendBotMessage(
                data.answer ||
                "No answer was returned.",
                data
            );

        } catch (error) {
            typingIndicator.remove();

            console.error(
                "Chatbot error:",
                error
            );

            appendBotMessage(
                error.message ||
                "Something went wrong. Please try again."
            );

        } finally {
            questionInput.disabled = false;
            sendButton.disabled = false;

            questionInput.focus();

            scrollToBottom();
        }
    }


    chatForm.addEventListener(
        "submit",
        function (event) {
            event.preventDefault();

            const question =
                questionInput.value.trim();

            sendQuestion(question);
        }
    );


    questionInput.addEventListener(
        "input",
        function () {
            updateCharacterCount();
            resizeTextarea();
        }
    );


    questionInput.addEventListener(
        "keydown",
        function (event) {
            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {
                event.preventDefault();

                chatForm.requestSubmit();
            }
        }
    );


    suggestedButtons.forEach(function (button) {
        button.addEventListener(
            "click",
            function () {
                const question =
                    this.dataset.question ||
                    this.textContent.trim();

                sendQuestion(question);
            }
        );
    });


    if (clearButton) {
        clearButton.addEventListener(
            "click",
            function () {
                chatMessages.innerHTML = "";

                appendBotMessage(
                    "Conversation cleared. How can I help you?"
                );
            }
        );
    }


    updateCharacterCount();
    resizeTextarea();
    scrollToBottom();
});