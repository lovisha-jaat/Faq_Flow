(function () {
    "use strict";

    // The script tag that loaded this widget
    const scriptElement = document.currentScript;

    if (!scriptElement) {
        console.error("FAQFlow: Widget script element was not found.");
        return;
    }

    const companyId =
        scriptElement.getAttribute("data-company-id");

    const apiBase =
        (
            scriptElement.getAttribute("data-api-base") ||
            new URL(scriptElement.src).origin
        ).replace(/\/$/, "");

    const apiUrl = `${apiBase}/api/chat`;

    if (!companyId) {
        console.error(
            "FAQFlow: data-company-id is missing."
        );
        return;
    }

    // Prevent loading the widget twice
    if (document.getElementById("faqflow-widget-root")) {
        return;
    }

    /* =====================================================
       STYLES
    ===================================================== */

    const style = document.createElement("style");

    style.textContent = `
        #faqflow-widget-root {
            position: fixed;
            right: 24px;
            bottom: 24px;
            z-index: 2147483647;
            font-family: Arial, sans-serif;
        }

        #faqflow-widget-button {
            width: 60px;
            height: 60px;
            display: grid;
            place-items: center;
            border: none;
            border-radius: 50%;
            background: #123f88;
            color: white;
            font-size: 25px;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(18, 63, 136, 0.3);
        }

        #faqflow-widget-window {
            position: absolute;
            right: 0;
            bottom: 75px;
            width: 350px;
            height: 500px;
            display: none;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid #dbe5f3;
            border-radius: 18px;
            background: white;
            box-shadow: 0 20px 55px rgba(15, 39, 78, 0.22);
        }

        #faqflow-widget-window.faqflow-open {
            display: flex;
        }

        .faqflow-widget-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 17px;
            background: #082552;
            color: white;
        }

        .faqflow-widget-header h3 {
            margin: 0;
            font-size: 16px;
        }

        .faqflow-widget-header p {
            margin: 4px 0 0;
            color: #b9cff0;
            font-size: 11px;
        }

        #faqflow-close-button {
            border: none;
            background: transparent;
            color: white;
            font-size: 24px;
            cursor: pointer;
        }

        #faqflow-widget-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f6f9fd;
        }

        .faqflow-message {
            max-width: 82%;
            margin-bottom: 12px;
            padding: 11px 13px;
            border-radius: 14px;
            font-size: 13px;
            line-height: 1.55;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }

        .faqflow-bot-message {
            margin-right: auto;
            border: 1px solid #e0e8f4;
            background: white;
            color: #183153;
        }

        .faqflow-user-message {
            margin-left: auto;
            background: #123f88;
            color: white;
        }

        .faqflow-widget-form {
            display: flex;
            gap: 8px;
            padding: 12px;
            border-top: 1px solid #e1e8f2;
            background: white;
        }

        #faqflow-widget-input {
            flex: 1;
            min-width: 0;
            padding: 11px 12px;
            border: 1px solid #cbd8e9;
            border-radius: 11px;
            outline: none;
            font-size: 13px;
        }

        #faqflow-widget-input:focus {
            border-color: #2464c7;
        }

        #faqflow-widget-send {
            width: 43px;
            border: none;
            border-radius: 11px;
            background: #123f88;
            color: white;
            cursor: pointer;
            font-size: 17px;
        }

        #faqflow-widget-send:disabled {
            cursor: not-allowed;
            opacity: 0.6;
        }

        @media (max-width: 480px) {
            #faqflow-widget-root {
                right: 12px;
                bottom: 12px;
            }

            #faqflow-widget-window {
                position: fixed;
                top: 12px;
                right: 12px;
                bottom: 85px;
                left: 12px;
                width: auto;
                height: auto;
            }
        }
    `;

    document.head.appendChild(style);

    /* =====================================================
       WIDGET HTML
    ===================================================== */

    const widgetRoot = document.createElement("div");

    widgetRoot.id = "faqflow-widget-root";

    widgetRoot.innerHTML = `
        <div id="faqflow-widget-window">

            <header class="faqflow-widget-header">
                <div>
                    <h3>FAQFlow Assistant</h3>
                    <p>Online and ready to help</p>
                </div>

                <button
                    type="button"
                    id="faqflow-close-button"
                    aria-label="Close chatbot"
                >
                    ×
                </button>
            </header>

            <div id="faqflow-widget-messages">
                <div class="faqflow-message faqflow-bot-message">
                    Hello! How can I help you today?
                </div>
            </div>

            <form class="faqflow-widget-form" id="faqflow-widget-form">
                <input
                    type="text"
                    id="faqflow-widget-input"
                    placeholder="Ask a question..."
                    maxlength="500"
                    autocomplete="off"
                    required
                >

                <button
                    type="submit"
                    id="faqflow-widget-send"
                    aria-label="Send question"
                >
                    ➤
                </button>
            </form>

        </div>

        <button
            type="button"
            id="faqflow-widget-button"
            aria-label="Open chatbot"
        >
            💬
        </button>
    `;

    document.body.appendChild(widgetRoot);

    /* =====================================================
       ELEMENTS
    ===================================================== */

    const widgetWindow =
        document.getElementById("faqflow-widget-window");

    const openButton =
        document.getElementById("faqflow-widget-button");

    const closeButton =
        document.getElementById("faqflow-close-button");

    const messages =
        document.getElementById("faqflow-widget-messages");

    const form =
        document.getElementById("faqflow-widget-form");

    const input =
        document.getElementById("faqflow-widget-input");

    const sendButton =
        document.getElementById("faqflow-widget-send");

    /* =====================================================
       FUNCTIONS
    ===================================================== */

    function addMessage(text, type) {
        const message = document.createElement("div");

        message.className =
            `faqflow-message faqflow-${type}-message`;

        message.textContent = text;

        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;

        return message;
    }

    function openWidget() {
        widgetWindow.classList.add("faqflow-open");
        input.focus();
    }

    function closeWidget() {
        widgetWindow.classList.remove("faqflow-open");
    }

    async function sendQuestion(question) {
        addMessage(question, "user");

        const typingMessage = addMessage(
            "Thinking...",
            "bot"
        );

        input.disabled = true;
        sendButton.disabled = true;

        try {
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    company_id: Number(companyId),
                    question: question
                })
            });

            let data;

            try {
                data = await response.json();
            } catch (error) {
                throw new Error(
                    "The server returned an invalid response."
                );
            }

            if (!response.ok) {
                throw new Error(
                    data.error ||
                    "The chatbot could not process your question."
                );
            }

            typingMessage.textContent =
                data.answer ||
                "No answer was returned.";

        } catch (error) {
            console.error(
                "FAQFlow widget error:",
                error
            );

            typingMessage.textContent =
                "Sorry, I could not connect to the chatbot. Please try again.";

        } finally {
            input.disabled = false;
            sendButton.disabled = false;
            input.focus();
            messages.scrollTop = messages.scrollHeight;
        }
    }

    /* =====================================================
       EVENTS
    ===================================================== */

    openButton.addEventListener(
        "click",
        openWidget
    );

    closeButton.addEventListener(
        "click",
        closeWidget
    );

    form.addEventListener(
        "submit",
        function (event) {
            event.preventDefault();

            const question =
                input.value.trim();

            if (!question) {
                return;
            }

            input.value = "";

            sendQuestion(question);
        }
    );

    console.log(
        "FAQFlow widget loaded for company:",
        companyId
    );
})();