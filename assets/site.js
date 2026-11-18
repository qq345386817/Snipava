const menu = document.querySelector(".language");
const trigger = menu.querySelector("summary");
document.addEventListener("click", (event) => {
  if (menu.open && !menu.contains(event.target)) menu.open = false;
});
document.addEventListener("keydown", (event) => {
  if (menu.open && event.key === "Escape") {
    menu.open = false;
    trigger.focus();
  }
});
