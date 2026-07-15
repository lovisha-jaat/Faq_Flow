/* =========================================================
   FAQFLOW AI
   FAQ MANAGEMENT JAVASCRIPT
========================================================= */

document.addEventListener("DOMContentLoaded", function () {
    initializeFaqCategoryFilter();
    initializeFaqCharacterCounters();
    initializeFaqLivePreview();
    initializeFaqFormLoading();
    initializeFaqRestoreButton();
    initializeFaqResetButton();
});


/* =========================================================
   FAQ CATEGORY FILTER
========================================================= */

function initializeFaqCategoryFilter() {
    const categoryFilter =
        document.getElementById("categoryFilter");

    const faqRows =
        document.querySelectorAll(".faq-row");

    const filterEmptyMessage =
        document.getElementById("filterEmptyMessage");

    if (!categoryFilter || faqRows.length === 0) {
        return;
    }

    categoryFilter.addEventListener(
        "change",
        function () {
            const selectedCategory =
                this.value.trim().toLowerCase();

            let visibleRows = 0;

            faqRows.forEach(function (row) {
                const rowCategory =
                    (row.dataset.category || "")
                        .trim()
                        .toLowerCase();

                const shouldDisplay =
                    selectedCategory === "all" ||
                    rowCategory === selectedCategory;

                row.style.display =
                    shouldDisplay ? "" : "none";

                if (shouldDisplay) {
                    visibleRows++;
                }
            });

            if (filterEmptyMessage) {
                filterEmptyMessage.style.display =
                    visibleRows === 0
                        ? "flex"
                        : "none";
            }
        }
    );
}


/* =========================================================
   DELETE FAQ MODAL
========================================================= */

function openDeleteModal(faqId, faqQuestion) {
    const modal =
        document.getElementById("deleteModal");

    const questionElement =
        document.getElementById("deleteFaqQuestion");

    const confirmDeleteButton =
        document.getElementById("confirmDeleteButton");

    if (
        !modal ||
        !questionElement ||
        !confirmDeleteButton
    ) {
        return;
    }

    questionElement.textContent =
        faqQuestion || "Selected FAQ";

    confirmDeleteButton.href =
        `/faqs/delete/${faqId}`;

    modal.classList.add("show");

    modal.setAttribute(
        "aria-hidden",
        "false"
    );

    document.body.classList.add(
        "modal-open"
    );
}


function closeDeleteModal() {
    const modal =
        document.getElementById("deleteModal");

    if (!modal) {
        return;
    }

    modal.classList.remove("show");

    modal.setAttribute(
        "aria-hidden",
        "true"
    );

    document.body.classList.remove(
        "modal-open"
    );
}


document.addEventListener(
    "keydown",
    function (event) {
        if (event.key === "Escape") {
            closeDeleteModal();
        }
    }
);


/* =========================================================
   CHARACTER COUNTERS
========================================================= */

function initializeFaqCharacterCounters() {
    const questionInput =
        document.getElementById("question");

    const answerInput =
        document.getElementById("answer");

    const questionCount =
        document.getElementById("questionCount");

    const answerCount =
        document.getElementById("answerCount");

    if (questionInput && questionCount) {
        updateCharacterCount(
            questionInput,
            questionCount,
            250
        );

        questionInput.addEventListener(
            "input",
            function () {
                updateCharacterCount(
                    questionInput,
                    questionCount,
                    250
                );
            }
        );
    }

    if (answerInput && answerCount) {
        updateCharacterCount(
            answerInput,
            answerCount,
            1500
        );

        answerInput.addEventListener(
            "input",
            function () {
                updateCharacterCount(
                    answerInput,
                    answerCount,
                    1500
                );
            }
        );
    }
}


function updateCharacterCount(
    input,
    counter,
    maximumLength
) {
    const currentLength =
        input.value.length;

    counter.textContent =
        `${currentLength} / ${maximumLength}`;

    counter.classList.remove(
        "character-warning",
        "character-danger"
    );

    if (currentLength >= maximumLength) {
        counter.classList.add(
            "character-danger"
        );
    } else if (
        currentLength >=
        maximumLength * 0.85
    ) {
        counter.classList.add(
            "character-warning"
        );
    }
}


/* =========================================================
   LIVE FAQ PREVIEW
========================================================= */

function initializeFaqLivePreview() {
    const questionInput =
        document.getElementById("question");

    const answerInput =
        document.getElementById("answer");

    const categoryInput =
        document.getElementById("category");

    const previewQuestion =
        document.getElementById("previewQuestion");

    const previewAnswer =
        document.getElementById("previewAnswer");

    const previewCategory =
        document.getElementById("previewCategory");

    if (
        !previewQuestion &&
        !previewAnswer &&
        !previewCategory
    ) {
        return;
    }

    function updatePreview() {
        if (
            questionInput &&
            previewQuestion
        ) {
            previewQuestion.textContent =
                questionInput.value.trim() ||
                "FAQ question preview";
        }

        if (
            answerInput &&
            previewAnswer
        ) {
            previewAnswer.textContent =
                answerInput.value.trim() ||
                "FAQ answer preview";
        }

        if (
            categoryInput &&
            previewCategory
        ) {
            previewCategory.textContent =
                categoryInput.value ||
                "General";
        }
    }

    if (questionInput) {
        questionInput.addEventListener(
            "input",
            updatePreview
        );
    }

    if (answerInput) {
        answerInput.addEventListener(
            "input",
            updatePreview
        );
    }

    if (categoryInput) {
        categoryInput.addEventListener(
            "change",
            updatePreview
        );
    }

    updatePreview();
}


/* =========================================================
   FORM SUBMISSION LOADING STATE
========================================================= */

function initializeFaqFormLoading() {
    const addFaqForm =
        document.getElementById("addFaqForm");

    const editFaqForm =
        document.getElementById("editFaqForm");

    if (addFaqForm) {
        addFaqForm.addEventListener(
            "submit",
            function () {
                const submitButton =
                    document.getElementById(
                        "submitFaqButton"
                    );

                setFaqButtonLoading(
                    submitButton,
                    "Adding FAQ..."
                );
            }
        );
    }

    if (editFaqForm) {
        editFaqForm.addEventListener(
            "submit",
            function () {
                const updateButton =
                    document.getElementById(
                        "updateFaqButton"
                    );

                setFaqButtonLoading(
                    updateButton,
                    "Saving Changes..."
                );
            }
        );
    }
}


function setFaqButtonLoading(
    button,
    loadingText
) {
    if (!button) {
        return;
    }

    button.disabled = true;

    button.innerHTML = `
        <i class="fa-solid fa-spinner fa-spin"></i>
        ${loadingText}
    `;
}


/* =========================================================
   RESET ADD FAQ FORM
========================================================= */

function initializeFaqResetButton() {
    const resetButton =
        document.getElementById("resetButton");

    if (!resetButton) {
        return;
    }

    resetButton.addEventListener(
        "click",
        function () {
            setTimeout(function () {
                initializeFaqCharacterCounters();
                initializeFaqLivePreview();
            }, 0);
        }
    );
}


/* =========================================================
   RESTORE ORIGINAL EDIT VALUES
========================================================= */

function initializeFaqRestoreButton() {
    const restoreButton =
        document.getElementById("restoreButton");

    const questionInput =
        document.getElementById("question");

    const answerInput =
        document.getElementById("answer");

    const categoryInput =
        document.getElementById("category");

    if (
        !restoreButton ||
        !questionInput ||
        !answerInput ||
        !categoryInput
    ) {
        return;
    }

    const originalQuestion =
        questionInput.value;

    const originalAnswer =
        answerInput.value;

    const originalCategory =
        categoryInput.value;

    restoreButton.addEventListener(
        "click",
        function () {
            questionInput.value =
                originalQuestion;

            answerInput.value =
                originalAnswer;

            categoryInput.value =
                originalCategory;

            questionInput.dispatchEvent(
                new Event("input")
            );

            answerInput.dispatchEvent(
                new Event("input")
            );

            categoryInput.dispatchEvent(
                new Event("change")
            );

            if (
                typeof showGlobalMessage ===
                "function"
            ) {
                showGlobalMessage(
                    "Original FAQ values restored.",
                    "success"
                );
            }
        }
    );
}