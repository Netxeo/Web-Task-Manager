import { initBoard } from "./board.js";
import { initConfirm } from "./confirm.js";
import { initTabs } from "./tabs.js";
import { initInterface } from "./ui.js";

document.documentElement.classList.add("js");
initConfirm();
initTabs();
initInterface();
initBoard();
