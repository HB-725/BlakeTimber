document.addEventListener("DOMContentLoaded", function () {
  var overlay = document.querySelector("[data-tool-overlay]");
  var openButtons = Array.from(document.querySelectorAll("[data-tool-open]"));
  var navHome = document.querySelector("[data-nav-home]");
  var navTool = document.querySelector("[data-nav-tool]");
  var navManage = document.querySelector("[data-nav-manage]");
  var manageOverlay = document.querySelector("[data-manage-overlay]");
  var searchOverlay = document.querySelector("[data-search-overlay]");

  if (!overlay) {
    return;
  }

  function setActiveNav(isToolActive) {
    if (!navHome || !navTool || !navManage) {
      return;
    }
    navHome.classList.toggle("text-primary", !isToolActive);
    navHome.classList.toggle("text-slate-400", isToolActive);
    navTool.classList.toggle("text-primary", isToolActive);
    navTool.classList.toggle("text-slate-400", !isToolActive);
    navManage.classList.toggle("text-primary", false);
    navManage.classList.toggle("text-slate-400", true);
  }

  openButtons.forEach(function (button) {
    button.addEventListener("click", function (event) {
      event.preventDefault();
      if (manageOverlay) {
        manageOverlay.classList.add("hidden");
      }
      if (searchOverlay) {
        searchOverlay.classList.add("hidden");
      }
      overlay.classList.remove("hidden");
      document.body.classList.add("overflow-hidden");
      setActiveNav(true);
    });
  });

  if (navHome) {
    navHome.addEventListener("click", function (event) {
      event.preventDefault();
      overlay.classList.add("hidden");
      document.body.classList.remove("overflow-hidden");
      setActiveNav(false);
    });
  }
});
