function selectTab(tabs, selected) {
    tabs.forEach((tab) => {
        const active = tab === selected;
        tab.setAttribute("aria-selected", String(active));
        tab.tabIndex = active ? 0 : -1;
        document.getElementById(tab.getAttribute("aria-controls")).hidden = !active;
    });
    history.replaceState(null, "", selected.href);
}

export function initTabs() {
    document.querySelectorAll("[role=tablist]").forEach((list) => {
        const tabs = [...list.querySelectorAll("[role=tab]")];
        tabs.forEach((tab) => {
            tab.addEventListener("click", (event) => {
                event.preventDefault();
                selectTab(tabs, tab);
            });
        });
        list.addEventListener("keydown", (event) => {
            const step = { ArrowRight: 1, ArrowLeft: -1 }[event.key];
            if (!step) {
                return;
            }
            const next = tabs[(tabs.indexOf(document.activeElement) + step + tabs.length) % tabs.length];
            selectTab(tabs, next);
            next.focus();
        });
    });
}
