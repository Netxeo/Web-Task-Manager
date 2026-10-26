export function showMessage(text) {
    const container = document.querySelector(".flashes") || document.body.appendChild(
        Object.assign(document.createElement("div"), { className: "flashes", role: "status" })
    );
    const message = Object.assign(document.createElement("p"), { className: "flash", textContent: text });
    container.append(message);
    dismissLater(message);
}

function dismissLater(flash) {
    setTimeout(() => {
        flash.classList.add("is-leaving");
        flash.addEventListener("transitionend", () => flash.remove(), { once: true });
    }, 4000);
}

export function initInterface() {
    document.querySelectorAll("[data-autosubmit]").forEach((select) => {
        select.addEventListener("change", () => select.form.requestSubmit());
    });
    document.querySelectorAll("[data-dismiss]").forEach(dismissLater);
    document.querySelector(".panel-form .field-input")?.focus();
    document.addEventListener("keydown", (event) => {
        const close = document.querySelector("[data-close-panel]");
        if (event.key === "Escape" && close && !document.querySelector("dialog[open]")) {
            window.location.href = close.href;
        }
    });
}
