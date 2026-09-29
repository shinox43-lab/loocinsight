// Mobile nav-menu toggle — replaces WordPress/Elementor Pro's dynamically-loaded
// nav-menu.bundle.min.js, which no longer exists now the site is static.
// The Elementor CSS already has the open/close animation wired to the
// ".elementor-active" class on ".elementor-menu-toggle"; this just flips it.
//
// Why event delegation (and not per-element listeners): the theme's own JS
// clones the header at runtime to build the sticky / mobile variants, so extra
// .elementor-menu-toggle nodes appear AFTER any load-time binding — those clones
// never got a handler, which is exactly why the mobile burger did nothing while
// desktop worked. Delegating on document (capture phase) catches every toggle,
// whenever it is created, and lets us stop the tap before other stray handlers
// (or the outside-close logic) can cancel it.
(function () {
  function closeToggle(t) {
    t.classList.remove("elementor-active");
    t.setAttribute("aria-expanded", "false");
  }
  function openToggle(t) {
    t.classList.add("elementor-active");
    t.setAttribute("aria-expanded", "true");
  }
  function closeAll(except) {
    document.querySelectorAll(".elementor-menu-toggle.elementor-active").forEach(function (t) {
      if (t !== except) closeToggle(t);
    });
  }

  document.addEventListener(
    "click",
    function (e) {
      var toggle = e.target.closest && e.target.closest(".elementor-menu-toggle");
      if (toggle) {
        e.preventDefault();
        e.stopPropagation();
        var isOpen = toggle.classList.contains("elementor-active");
        closeAll(toggle);
        if (isOpen) closeToggle(toggle);
        else openToggle(toggle);
        return;
      }
      // Tap outside a toggle: close everything unless the tap was inside an open panel.
      var panel = e.target.closest && e.target.closest(".elementor-nav-menu__container");
      if (!panel) closeAll(null);
    },
    true // capture: run before the theme's own handlers
  );

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeAll(null);
  });
})();
