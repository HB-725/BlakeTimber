document.addEventListener("DOMContentLoaded", function () {
  var overlay = document.querySelector("[data-manage-overlay]");
  var openButtons = Array.from(document.querySelectorAll("[data-manage-open]"));
  var closeButtons = Array.from(document.querySelectorAll("[data-manage-close]"));
  var navHome = document.querySelector("[data-nav-home]");
  var navManage = document.querySelector("[data-nav-manage]");
  var navTool = document.querySelector("[data-nav-tool]");
  var searchOverlay = document.querySelector("[data-search-overlay]");
  var toolOverlay = document.querySelector("[data-tool-overlay]");
  var statusContainer = document.querySelector("[data-manage-status]");
  var authSection = document.querySelector("[data-manage-auth]");
  var guestSection = document.querySelector("[data-manage-guest]");
  var loginForm = document.getElementById("manage-login-form");
  var logoutForm = document.getElementById("manage-logout-form");

  if (!overlay) {
    return;
  }

  function setActiveNav(isManageActive) {
    if (!navHome || !navManage || !navTool) {
      return;
    }
    navHome.classList.toggle("text-primary", !isManageActive);
    navHome.classList.toggle("text-slate-400", isManageActive);
    navManage.classList.toggle("text-primary", isManageActive);
    navManage.classList.toggle("text-slate-400", !isManageActive);
    navTool.classList.toggle("text-primary", false);
    navTool.classList.toggle("text-slate-400", true);
  }

  openButtons.forEach(function (button) {
    button.addEventListener("click", function (event) {
      event.preventDefault();
      if (searchOverlay) {
        searchOverlay.classList.add("hidden");
      }
      if (toolOverlay) {
        toolOverlay.classList.add("hidden");
      }
      overlay.classList.remove("hidden");
      document.body.classList.add("overflow-hidden");
      setActiveNav(true);
    });
  });

  closeButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      overlay.classList.add("hidden");
      document.body.classList.remove("overflow-hidden");
      setActiveNav(false);
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

  function setStatus(message, isError) {
    if (!statusContainer) {
      return;
    }
    var box = statusContainer.querySelector("div");
    if (!box) {
      return;
    }
    box.textContent = message;
    statusContainer.classList.remove("hidden");
    box.classList.toggle("border-rose-200", isError);
    box.classList.toggle("bg-rose-50", isError);
    box.classList.toggle("text-rose-700", isError);
    box.classList.toggle("border-emerald-200", !isError);
    box.classList.toggle("bg-emerald-50", !isError);
    box.classList.toggle("text-emerald-700", !isError);
    window.clearTimeout(window.manageStatusTimer);
    window.manageStatusTimer = window.setTimeout(function () {
      statusContainer.classList.add("hidden");
    }, 3000);
  }

  function swapToAuth() {
    if (authSection) {
      authSection.classList.remove("hidden");
    }
    if (guestSection) {
      guestSection.classList.add("hidden");
    }
  }

  function swapToGuest() {
    if (authSection) {
      authSection.classList.add("hidden");
    }
    if (guestSection) {
      guestSection.classList.remove("hidden");
    }
  }

  function getCsrfToken(form) {
    var tokenInput = form.querySelector("input[name='csrfmiddlewaretoken']");
    return tokenInput ? tokenInput.value : "";
  }

  if (loginForm) {
    loginForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var formData = new FormData(loginForm);
      fetch(loginForm.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(loginForm)
        },
        body: formData
      })
        .then(function (response) {
          if (!response.ok) {
            return response.json().then(function (payload) {
              throw new Error(payload.error || "Login failed.");
            });
          }
          return response.json();
        })
        .then(function () {
          swapToAuth();
          setStatus("Signed in successfully.", false);
        })
        .catch(function (error) {
          setStatus(error.message || "Login failed.", true);
        });
    });
  }

  if (logoutForm) {
    logoutForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var formData = new FormData(logoutForm);
      fetch(logoutForm.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(logoutForm)
        },
        body: formData
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Logout failed.");
          }
          return response.json();
        })
        .then(function () {
          swapToGuest();
          setStatus("Signed out successfully.", false);
          fetch("/admin-mode/exit/");
        })
        .catch(function (error) {
          setStatus(error.message || "Logout failed.", true);
        });
    });
  }
});
