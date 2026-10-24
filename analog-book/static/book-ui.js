(() => {
  "use strict";

  const top = document.getElementById("book-top");
  if (!top) return;

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  const update = () => {
    top.hidden = window.scrollY < 600;
  };

  window.addEventListener("scroll", update, { passive: true });
  top.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: reduced.matches ? "auto" : "smooth" });
  });
  update();
})();
