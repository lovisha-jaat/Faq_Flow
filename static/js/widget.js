/* =========================================================
   FAQFLOW AI
   EMBEDDABLE WEBSITE CHATBOT WIDGET
========================================================= */

(function () {
    "use strict";

    /* ---------------------------------------------------------
       PREVENT DUPLICATE WIDGET
    --------------------------------------------------------- */

    if (window.FAQFlowWidgetLoaded) {
        return;
    }

    window.FAQFlowWidgetLoaded = true;


    /* ---------------------------------------------------------
       GET CURRENT SCRIPT AND COMPANY ID
    --------------------------------------------------------- */

    const currentScript =
        document.currentScript ||
        document.querySelector(
            'script[data-company-id][src*="widget.js"]'
        );

    if (!currentScript) {
        console.error(
            "FAQFlow AI: Widget script could not be detected."
        );
        return;
    }

    const companyId =
        currentScript.getAttribute("data-company-id");

    if (!companyId) {
        console.error(
            "FAQFlow AI: data-company-id is required."
        );
        return;
    }


    /* ---------------------------------------------------------
       WIDGET CONFIGURATION
    --------------------------------------------------------- */

    const scriptUrl = new URL(
        currentScript.src,
        window.location.href
    );

    const backendOrigin = scriptUrl.origin;

    const apiUrl =
        currentScript.getAttribute("data-api-url") ||
        `${backendOrigin}/api/chat`;

    const companyName =
        currentScript.getAttribute("data-company-name") ||
        "Company";

    const assistantName =
        currentScript.getAttribute("data-assistant-name") ||
        `${companyName} Assistant`;

    const primaryColor =
        currentScript.getAttribute("data-primary-color") ||
        "#123a7a";

    const welcomeMessage =
        currentScript.getAttribute("data-welcome-message") ||
        "Hello! How can I help you today?";

    const widgetPosition =
        currentScript.getAttribute("data-position") ||
        "right";


    /* ---------------------------------------------------------
       CREATE WIDGET STYLES
    --------------------------------------------------------- */

    const style = document.createElement("style");

    style.textContent = `
        :root {
            --faqflow-widget-primary: ${primaryColor};
            --faqflow-widget-dark: #071a3d;
            --faqflow-widget-white: #ffffff;
            --faqflow-widget-bg: #f8fafc;
            --faqflow-widget-text: #0f172a;
            --faqflow-widget-muted: #64748b;
            --faqflow-widget-border: #e2e8f0;
            --faqflow-widget-success: #16a34a;
        }

        #faqflow-widget-root,
        #faqflow-widget-root * {
            box-sizing: border-box;
            font-family:
                Inter,
                Poppins,
                Arial,
                sans-serif;
        }

        #faqflow-widget-root {
            position: fixed;
            z-index: 2147483000;
            ${
                widgetPosition === "left"
                    ? "left: 24px;"
                    : "right: 24px;"
            }
            bottom: 24px;
        }

        #faqflow-widget-button {
            position: relative;
            width: 60px;
            height: 60px;
            display: grid;
            place-items: center;
            border: none;
            border-radius: 50%;
            background:
                linear-gradient(
                    135deg,
                    var(--faqflow-widget-primary),
                    #2563eb
                );
            color: var(--faqflow-widget-white);
            cursor: pointer;
            box-shadow:
                0 16px 36px
                rgba(7, 26, 61, 0.28);
            transition:
                transform 0.22s ease,
                box-shadow 0.22s ease;
        }

        #faqflow-widget-button:hover {
            transform: translateY(-4px);
            box-shadow:
                0 20px 42px
                rgba(7, 26, 61, 0.34);
        }

        #faqflow-widget-button svg {
            width: 25px;
            height: 25px;
            fill: currentColor;
        }

        .faqflow-widget-notification {
            position: absolute;
            top: 2px;
            right: 2px;
            width: 14px;
            height: 14px;
            border: 3px solid
                var(--faqflow-widget-white);
            border-radius: 50%;
            background: #ef4444;
        }

        #faqflow-widget-window {
            position: absolute;
            ${
                widgetPosition === "left"
                    ? "left: 0;"
                    : "right: 0;"
            }
            bottom: 76px;
            width: 360px;
            max-width: calc(100vw - 32px);
            overflow: hidden;
            border:
                1px solid
                var(--faqflow-widget-border);
            border-radius: 20px;
            background:
                var(--faqflow-widget-white);
            box-shadow:
                0 28px 70px
                rgba(7, 26, 61, 0.24);
            opacity: 0;
            visibility: hidden;
            transform:
                translateY(18px)
                scale(0.96);
            transform-origin:
                ${
                    widgetPosition === "left"
                        ? "bottom left"
                        : "bottom right"
                };
            transition:
                opacity 0.22s ease,
                visibility 0.22s ease,
                transform 0.22s ease;
        }

        #faqflow-widget-window.faqflow-open {
            opacity: 1;
            visibility: visible;
            transform:
                translateY(0)
                scale(1);
        }

        .faqflow-widget-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            padding: 16px;
            background:
                linear-gradient(
                    135deg,
                    var(--faqflow-widget-dark),
                    var(--faqflow-widget-primary)
                );
            color: var(--faqflow-widget-white);
        }

        .faqflow-widget-heading {
            display: flex;
            align-items: center;
            gap: 11px;
            min-width: 0;
        }

        .faqflow-widget-avatar {
            position: relative;
            width: 42px;
            height: 42px;
            flex-shrink: 0;
            display: grid;
            place-items: center;
            border-radius: 13px;
            background: rgba(255, 255, 255, 0.14);
        }

        .faqflow-widget-avatar svg {
            width: 20px;
            height: 20px;
            fill: currentColor;
        }

        .faqflow-widget-online-dot {
            position: absolute;
            right: -2px;
            bottom: -2px;
            width: 11px;
            height: 11px;
            border: 2px solid
                var(--faqflow-widget-primary);
            border-radius: 50%;
            background:
                var(--faqflow-widget-success);
        }

        .faqflow-widget-heading-text {
            min-width: 0;
        }

        .faqflow-widget-heading h3 {
            margin: 0;
            overflow: hidden;
            color: var(--faqflow-widget-white);
            font-size: 14px;
            font-weight: 700;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .faqflow-widget-heading p {
            margin: 2px 0 0;
            color: #bbf7d0;
            font-size: 10px;
        }

        #faqflow-widget-close {
            width: 34px;
            height: 34px;
            flex-shrink: 0;
            display: grid;
            place-items: center;
            border: none;
            border-radius: 9px;
            background:
                rgba(255, 255, 255, 0.12);
            color: var(--faqflow-widget-white);
            cursor: pointer;
        }

        #faqflow-widget-close:hover {
            background:
                rgba(255, 255, 255, 0.2);
        }

        #faqflow-widget-close svg {
            width: 18px;
            height: 18px;
            fill: currentColor;
        }

        #faqflow-widget-messages {
            height: 340px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 13px;
            padding: 16px;
            background:
                radial-gradient(
                    circle at top right,
                    rgba(37, 99, 235, 0.07),
                    transparent 30%
                ),
                var(--faqflow-widget-bg);
        }

        .faqflow-message-row {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            animation:
                faqflow-message-in
                0.24s ease;
        }

        .faqflow-user-row {
            justify-content: flex-end;
        }

        .faqflow-message-avatar {
            width: 29px;
            height: 29px;
            flex-shrink: 0;
            display: grid;
            place-items: center;
            border-radius: 9px;
            background:
                var(--faqflow-widget-primary);
            color:
                var(--faqflow-widget-white);
        }

        .faqflow-message-avatar svg {
            width: 14px;
            height: 14px;
            fill: currentColor;
        }

        .faqflow-message-content {
            max-width: 78%;
        }

        .faqflow-message-bubble {
            margin: 0;
            padding: 10px 12px;
            border:
                1px solid
                var(--faqflow-widget-border);
            border-radius: 13px;
            border-top-left-radius: 4px;
            background:
                var(--faqflow-widget-white);
            color:
                var(--faqflow-widget-text);
            font-size: 12px;
            line-height: 1.6;
            word-break: break-word;
        }

        .faqflow-user-row
        .faqflow-message-bubble {
            border-color:
                var(--faqflow-widget-primary);
            border-top-left-radius: 13px;
            border-top-right-radius: 4px;
            background:
                var(--faqflow-widget-primary);
            color:
                var(--faqflow-widget-white);
        }

        .faqflow-message-time {
            display: block;
            margin-top: 4px;
            color:
                var(--faqflow-widget-muted);
            font-size: 8px;
        }

        .faqflow-user-row
        .faqflow-message-time {
            text-align: right;
        }

        .faqflow-message-category {
            display: inline-flex;
            margin-top: 6px;
            padding: 4px 7px;
            border-radius: 100px;
            background: #eaf2ff;
            color:
                var(--faqflow-widget-primary);
            font-size: 8px;
            font-weight: 700;
        }

        .faqflow-typing-bubble {
            display: flex;
            align-items: center;
            gap: 4px;
            width: fit-content;
            padding: 13px;
            border:
                1px solid
                var(--faqflow-widget-border);
            border-radius: 13px;
            background:
                var(--faqflow-widget-white);
        }

        .faqflow-typing-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background:
                var(--faqflow-widget-muted);
            animation:
                faqflow-typing
                1.2s infinite ease-in-out;
        }

        .faqflow-typing-dot:nth-child(2) {
            animation-delay: 0.15s;
        }

        .faqflow-typing-dot:nth-child(3) {
            animation-delay: 0.3s;
        }

        .faqflow-widget-suggestions {
            display: flex;
            gap: 7px;
            overflow-x: auto;
            padding: 10px 12px;
            border-top:
                1px solid
                var(--faqflow-widget-border);
            background:
                var(--faqflow-widget-white);
        }

        .faqflow-suggestion-button {
            flex-shrink: 0;
            padding: 7px 10px;
            border: 1px solid #bfdbfe;
            border-radius: 100px;
            background: #eaf2ff;
            color:
                var(--faqflow-widget-primary);
            cursor: pointer;
            font-size: 9px;
            font-weight: 600;
        }

        .faqflow-suggestion-button:hover {
            background:
                var(--faqflow-widget-primary);
            color:
                var(--faqflow-widget-white);
        }

        #faqflow-widget-form {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px;
            border-top:
                1px solid
                var(--faqflow-widget-border);
            background:
                var(--faqflow-widget-white);
        }

        #faqflow-widget-input {
            flex: 1;
            min-width: 0;
            height: 43px;
            padding: 10px 12px;
            border:
                1px solid
                var(--faqflow-widget-border);
            border-radius: 10px;
            background:
                var(--faqflow-widget-bg);
            color:
                var(--faqflow-widget-text);
            font-size: 11px;
            outline: none;
        }

        #faqflow-widget-input:focus {
            border-color:
                var(--faqflow-widget-primary);
            background:
                var(--faqflow-widget-white);
            box-shadow:
                0 0 0 3px
                rgba(37, 99, 235, 0.1);
        }

        #faqflow-widget-send {
            width: 43px;
            height: 43px;
            flex-shrink: 0;
            display: grid;
            place-items: center;
            border: none;
            border-radius: 11px;
            background:
                var(--faqflow-widget-primary);
            color:
                var(--faqflow-widget-white);
            cursor: pointer;
        }

        #faqflow-widget-send:disabled {
            cursor: not-allowed;
            opacity: 0.6;
        }

        #faqflow-widget-send svg {
            width: 17px;
            height: 17px;
            fill: currentColor;
        }

        .faqflow-widget-footer {
            padding: 8px;
            border-top:
                1px solid
                var(--faqflow-widget-border);
            background:
                var(--faqflow-widget-white);
            color:
                var(--faqflow-widget-muted);
            text-align: center;
            font-size: 8px;
        }

        @keyframes faqflow-message-in {
            from {
                opacity: 0;
                transform: translateY(7px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes faqflow-typing {
            0%,
            60%,
            100% {
                opacity: 0.4;
                transform: translateY(0);
            }

            30% {
                opacity: 1;
                transform: translateY(-4px);
            }
        }

        @media (max-width: 480px) {
            #faqflow-widget-root {
                left: 14px;
                right: 14px;
                bottom: 14px;
            }

            #faqflow-widget-button {
                margin-left:
                    ${
                        widgetPosition === "left"
                            ? "0"
                            : "auto"
                    };
            }

            #faqflow-widget-window {
                left: 0;
                right: 0;
                bottom: 74px;
                width: 100%;
                max-width: none;
            }

            #faqflow-widget-messages {
                height: 330px;
            }
        }
    `;

    document.head.appendChild(style);


    /* ---------------------------------------------------------
       SVG ICONS
    --------------------------------------------------------- */

    const icons = {
        chat: `
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="
                    M4 4h16a2 2 0 0 1 2 2v10
                    a2 2 0 0 1-2 2H8l-4 4v-4
                    a2 2 0 0 1-2-2V6
                    a2 2 0 0 1 2-2Z
                "/>
            </svg>
        `,

        robot: `
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="
                    M11 2h2v3h3a4 4 0 0 1 4 4v7
                    a4 4 0 0 1-4 4H8
                    a4 4 0 0 1-4-4V9
                    a4 4 0 0 1 4-4h3V2Zm-3 7
                    a1.5 1.5 0 1 0 0 3
                    1.5 1.5 0 0 0 0-3Zm8 0
                    a1.5 1.5 0 1 0 0 3
                    1.5 1.5 0 0 0 0-3Zm-8 6v2h8v-2H8Z
                "/>
            </svg>
        `,

        close: `
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="
                    M6.4 5 12 10.6 17.6 5
                    19 6.4 13.4 12 19 17.6
                    17.6 19 12 13.4 6.4 19
                    5 17.6 10.6 12 5 6.4Z
                "/>
            </svg>
        `,

        send: `
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="
                    M2.5 3.5 22 12 2.5 20.5
                    2 14l13-2-13-2 .5-6.5Z
                "/>
            </svg>
        `
    };


    /* ---------------------------------------------------------
       CREATE WIDGET HTML
    --------------------------------------------------------- */

    const root = document.createElement("div");
    root.id = "faqflow-widget-root";

    root.innerHTML = `
        <div
            id="faqflow-widget-window"
            role="dialog"
            aria-label="FAQFlow AI Chatbot"
            aria-hidden="true"
        >
            <div class="faqflow-widget-header">

                <div class="faqflow-widget-heading">

                    <div class="faqflow-widget-avatar">

                        ${icons.robot}

                        <span
                            class="faqflow-widget-online-dot"
                        ></span>

                    </div>

                    <div class="faqflow-widget-heading-text">

                        <h3></h3>

                        <p>Online</p>

                    </div>

                </div>

                <button
                    type="button"
                    id="faqflow-widget-close"
                    aria-label="Close chatbot"
                >
                    ${icons.close}
                </button>

            </div>

            <div id="faqflow-widget-messages"></div>

            <div class="faqflow-widget-suggestions">

                <button
                    type="button"
                    class="faqflow-suggestion-button"
                    data-question="What services do you provide?"
                >
                    What services do you provide?
                </button>

                <button
                    type="button"
                    class="faqflow-suggestion-button"
                    data-question="How can I contact support?"
                >
                    How can I contact support?
                </button>

            </div>

            <form id="faqflow-widget-form">

                <input
                    type="text"
                    id="faqflow-widget-input"
                    maxlength="500"
                    placeholder="Ask a question..."
                    autocomplete="off"
                    required
                >

                <button
                    type="submit"
                    id="faqflow-widget-send"
                    aria-label="Send message"
                >
                    ${icons.send}
                </button>

            </form>

            <div class="faqflow-widget-footer">

                Powered by FAQFlow AI

            </div>

        </div>

        <button
            type="button"
            id="faqflow-widget-button"
            aria-label="Open chatbot"
        >
            ${icons.chat}

            <span
                class="faqflow-widget-notification"
            ></span>
        </button>
    `;

    document.body.appendChild(root);


    /* ---------------------------------------------------------
       GET ELEMENTS
    --------------------------------------------------------- */

    const widgetButton =
        document.getElementById(
            "faqflow-widget-button"
        );

    const widgetWindow =
        document.getElementById(
            "faqflow-widget-window"
        );

    const closeButton =
        document.getElementById(
            "faqflow-widget-close"
        );

    const messagesContainer =
        document.getElementById(
            "faqflow-widget-messages"
        );

    const chatForm =
        document.getElementById(
            "faqflow-widget-form"
        );

    const questionInput =
        document.getElementById(
            "faqflow-widget-input"
        );

    const sendButton =
        document.getElementById(
            "faqflow-widget-send"
        );

    const notificationDot =
        document.querySelector(
            ".faqflow-widget-notification"
        );

    const assistantTitle =
        document.querySelector(
            ".faqflow-widget-heading h3"
        );

    assistantTitle.textContent =
        assistantName;


    /* ---------------------------------------------------------
       OPEN AND CLOSE WIDGET
    --------------------------------------------------------- */

    function openWidget() {
        widgetWindow.classList.add(
            "faqflow-open"
        );

        widgetWindow.setAttribute(
            "aria-hidden",
            "false"
        );

        notificationDot.style.display =
            "none";

        setTimeout(function () {
            questionInput.focus();
        }, 150);
    }


    function closeWidget() {
        widgetWindow.classList.remove(
            "faqflow-open"
        );

        widgetWindow.setAttribute(
            "aria-hidden",
            "true"
        );
    }


    widgetButton.addEventListener(
        "click",
        function () {
            const isOpen =
                widgetWindow.classList.contains(
                    "faqflow-open"
                );

            if (isOpen) {
                closeWidget();
            } else {
                openWidget();
            }
        }
    );


    closeButton.addEventListener(
        "click",
        closeWidget
    );


    /* ---------------------------------------------------------
       MESSAGE HELPERS
    --------------------------------------------------------- */

    function getCurrentTime() {
        return new Date().toLocaleTimeString(
            [],
            {
                hour: "2-digit",
                minute: "2-digit"
            }
        );
    }


    function scrollToBottom() {
        messagesContainer.scrollTop =
            messagesContainer.scrollHeight;
    }


    function createBotMessage(
        message,
        category
    ) {
        const row =
            document.createElement("div");

        row.className =
            "faqflow-message-row";

        const avatar =
            document.createElement("div");

        avatar.className =
            "faqflow-message-avatar";

        avatar.innerHTML =
            icons.robot;

        const content =
            document.createElement("div");

        content.className =
            "faqflow-message-content";

        const bubble =
            document.createElement("p");

        bubble.className =
            "faqflow-message-bubble";

        bubble.textContent = message;

        const time =
            document.createElement("span");

        time.className =
            "faqflow-message-time";

        time.textContent =
            getCurrentTime();

        content.appendChild(bubble);

        if (category) {
            const categoryBadge =
                document.createElement("span");

            categoryBadge.className =
                "faqflow-message-category";

            categoryBadge.textContent =
                category;

            content.appendChild(
                categoryBadge
            );
        }

        content.appendChild(time);

        row.appendChild(avatar);
        row.appendChild(content);

        messagesContainer.appendChild(row);

        scrollToBottom();
    }


    function createUserMessage(message) {
        const row =
            document.createElement("div");

        row.className =
            "faqflow-message-row faqflow-user-row";

        const content =
            document.createElement("div");

        content.className =
            "faqflow-message-content";

        const bubble =
            document.createElement("p");

        bubble.className =
            "faqflow-message-bubble";

        bubble.textContent =
            message;

        const time =
            document.createElement("span");

        time.className =
            "faqflow-message-time";

        time.textContent =
            getCurrentTime();

        content.appendChild(bubble);
        content.appendChild(time);

        row.appendChild(content);

        messagesContainer.appendChild(row);

        scrollToBottom();
    }


    function createTypingMessage() {
        const row =
            document.createElement("div");

        row.className =
            "faqflow-message-row";

        row.id =
            "faqflow-typing-message";

        const avatar =
            document.createElement("div");

        avatar.className =
            "faqflow-message-avatar";

        avatar.innerHTML =
            icons.robot;

        const typingBubble =
            document.createElement("div");

        typingBubble.className =
            "faqflow-typing-bubble";

        for (let index = 0; index < 3; index++) {
            const dot =
                document.createElement("span");

            dot.className =
                "faqflow-typing-dot";

            typingBubble.appendChild(dot);
        }

        row.appendChild(avatar);
        row.appendChild(typingBubble);

        messagesContainer.appendChild(row);

        scrollToBottom();

        return row;
    }


    /* ---------------------------------------------------------
       SEND QUESTION TO API
    --------------------------------------------------------- */

    async function sendQuestion(question) {
        createUserMessage(question);

        questionInput.value = "";
        questionInput.disabled = true;
        sendButton.disabled = true;

        const typingMessage =
            createTypingMessage();

        try {
            const response = await fetch(
                apiUrl,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        company_id:
                            Number(companyId),
                        question:
                            question
                    })
                }
            );

            const data =
                await response.json();

            typingMessage.remove();

            if (!response.ok) {
                throw new Error(
                    data.message ||
                    "Unable to get an answer."
                );
            }

            createBotMessage(
                data.answer ||
                "No answer was returned.",
                data.category
            );
        } catch (error) {
            typingMessage.remove();

            createBotMessage(
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


    /* ---------------------------------------------------------
       FORM EVENT
    --------------------------------------------------------- */

    chatForm.addEventListener(
        "submit",
        function (event) {
            event.preventDefault();

            const question =
                questionInput.value.trim();

            if (!question) {
                return;
            }

            sendQuestion(question);
        }
    );


    /* ---------------------------------------------------------
       SUGGESTED QUESTIONS
    --------------------------------------------------------- */

    document
        .querySelectorAll(
            ".faqflow-suggestion-button"
        )
        .forEach(function (button) {
            button.addEventListener(
                "click",
                function () {
                    const question =
                        this.dataset.question;

                    if (!question) {
                        return;
                    }

                    openWidget();
                    sendQuestion(question);
                }
            );
        });


    /* ---------------------------------------------------------
       KEYBOARD SUPPORT
    --------------------------------------------------------- */

    document.addEventListener(
        "keydown",
        function (event) {
            if (event.key === "Escape") {
                closeWidget();
            }
        }
    );


    /* ---------------------------------------------------------
       INITIAL MESSAGE
    --------------------------------------------------------- */

    createBotMessage(
        welcomeMessage
    );
})();