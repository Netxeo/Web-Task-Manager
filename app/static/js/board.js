import { showMessage } from "./ui.js";

const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const htmlPolicy = window.trustedTypes?.createPolicy("board", { createHTML: (html) => html });

async function refreshMain() {
    const response = await fetch(window.location.href, { headers: { Accept: "text/html" } });
    const html = await response.text();
    const page = new DOMParser().parseFromString(htmlPolicy ? htmlPolicy.createHTML(html) : html, "text/html");
    const fresh = page.getElementById("contenu");
    if (!response.ok || !fresh) {
        window.location.reload();
        return;
    }
    document.getElementById("contenu").replaceWith(fresh);
    initBoard();
}

async function moveCard(event) {
    const card = event.item;
    const zone = event.to.dataset;
    const toColumn = zone.status !== undefined;
    const response = await fetch(toColumn ? card.dataset.statusUrl : card.dataset.scheduleUrl, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken, Accept: "application/json" },
        body: new URLSearchParams(toColumn ? { status: zone.status } : { day: zone.day }),
    }).catch(() => null);
    if (!response?.ok) {
        event.from.insertBefore(card, event.from.children[event.oldIndex] || null);
        showMessage("Déplacement impossible. Recharge la page et réessaie.");
        return;
    }
    await refreshMain();
}

export function initBoard() {
    if (!window.Sortable) {
        return;
    }
    document.querySelectorAll("[data-dropzone]").forEach((list) => {
        window.Sortable.create(list, {
            group: "tasks",
            sort: false,
            animation: 150,
            delay: 150,
            delayOnTouchOnly: true,
            filter: ".card-toggle",
            preventOnFilter: false,
            ghostClass: "card-ghost",
            chosenClass: "card-chosen",
            dragClass: "card-drag",
            onAdd: moveCard,
        });
    });
}
