document.documentElement.classList.add("js");

const dialog = document.getElementById("confirm-dialog");
let pendingForm = null;

document.addEventListener("submit", (event) => {
    const form = event.target;
    if (form.dataset.confirm) {
        event.preventDefault();
        pendingForm = form;
        dialog.querySelector("#confirm-message").textContent = form.dataset.confirm;
        dialog.showModal();
        return;
    }
    const button = form.querySelector("[data-busy-label]");
    if (button) {
        button.disabled = true;
        button.textContent = button.dataset.busyLabel;
    }
});

dialog.querySelector("[data-confirm-accept]").addEventListener("click", () => {
    const form = pendingForm;
    dialog.close();
    form.submit();
});

dialog.querySelector("[data-confirm-cancel]").addEventListener("click", () => dialog.close());
dialog.addEventListener("close", () => {
    pendingForm = null;
});

document.querySelectorAll("[data-autosubmit]").forEach((select) => {
    select.addEventListener("change", () => select.form.requestSubmit());
});

document.querySelectorAll("[data-dismiss]").forEach((flash) => {
    setTimeout(() => {
        flash.classList.add("is-leaving");
        flash.addEventListener("transitionend", () => flash.remove(), { once: true });
    }, 4000);
});

document.addEventListener("keydown", (event) => {
    const close = document.querySelector(".panel-header .icon-button");
    if (event.key === "Escape" && close && !dialog.open) {
        window.location.href = close.href;
    }
});

document.querySelector(".panel-form .field-input")?.focus();
