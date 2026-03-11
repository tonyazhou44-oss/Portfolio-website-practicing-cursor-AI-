document.addEventListener("DOMContentLoaded", () => {
  const yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear().toString();
  }

  document.querySelectorAll("[data-scroll-to]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-scroll-to");
      if (!targetId) return;
      const el = document.getElementById(targetId);
      if (!el) return;
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  const tiltCards = document.querySelectorAll("[data-tilt]");
  tiltCards.forEach((card) => {
    const maxTilt = 6;

    card.addEventListener("pointermove", (event) => {
      const rect = card.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      const xRatio = (x / rect.width) * 2 - 1;
      const yRatio = (y / rect.height) * 2 - 1;
      const rotateX = -(yRatio * maxTilt);
      const rotateY = xRatio * maxTilt;

      card.style.transform = `translateY(-4px) scale(1.01) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
      card.style.transition = "transform 80ms ease-out, box-shadow 200ms ease-out";
    });

    function resetTilt() {
      card.style.transform = "";
      card.style.transition = "";
    }

    card.addEventListener("pointerleave", resetTilt);
    card.addEventListener("pointerdown", resetTilt);
  });
});
