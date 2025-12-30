function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function debounce(fn, delay) {
  var timer;
  return function () {
    var context = this;
    var args = arguments;
    clearTimeout(timer);
    timer = setTimeout(function () {
      fn.apply(context, args);
    }, delay);
  };
}

document.addEventListener("DOMContentLoaded", function () {
  var input = document.getElementById("search-input");
  var clearButton = document.getElementById("clear-search");
  var emptyState = document.getElementById("search-empty");
  var profilesSection = document.getElementById("profiles-section");
  var categoriesSection = document.getElementById("categories-section");
  var productsSection = document.getElementById("products-section");
  var profilesList = document.getElementById("profiles-list");
  var categoriesList = document.getElementById("categories-list");
  var productsList = document.getElementById("products-list");
  var productsCount = document.getElementById("products-count");
  var filterButtons = Array.from(document.querySelectorAll("[data-filter]"));
  var overlay = document.querySelector("[data-search-overlay]");
  var openButtons = Array.from(document.querySelectorAll("[data-search-open]"));
  var closeButtons = Array.from(document.querySelectorAll("[data-search-close]"));
  var manageOverlay = document.querySelector("[data-manage-overlay]");
  var toolOverlay = document.querySelector("[data-tool-overlay]");
  var navHome = document.querySelector("[data-nav-home]");

  if (!input || !clearButton) {
    // Allow overlay open/close even when the search UI is hidden.
    input = null;
    clearButton = null;
  }

  function setFilter(activeFilter) {
    if (!filterButtons.length) {
      return;
    }
    filterButtons.forEach(function (button) {
      var isActive = button.dataset.filter === activeFilter;
      button.classList.toggle("bg-primary", isActive);
      button.classList.toggle("text-white", isActive);
      button.classList.toggle("shadow-md", isActive);
      button.classList.toggle("shadow-primary/20", isActive);
      button.classList.toggle("bg-white", !isActive);
      button.classList.toggle("text-slate-600", !isActive);
      button.classList.toggle("border", !isActive);
      button.classList.toggle("border-slate-200", !isActive);
    });

    if (profilesSection) {
      profilesSection.classList.toggle(
      "hidden",
      activeFilter !== "all" && activeFilter !== "profiles"
      );
    }
    if (categoriesSection) {
      categoriesSection.classList.toggle(
      "hidden",
      activeFilter !== "all" && activeFilter !== "categories"
      );
    }
    if (productsSection) {
      productsSection.classList.toggle(
      "hidden",
      activeFilter !== "all" && activeFilter !== "products"
      );
    }
  }

  if (filterButtons.length) {
    filterButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        setFilter(button.dataset.filter);
      });
    });
  }

  function renderProfiles(profiles) {
    if (!profilesList) {
      return;
    }
    profilesList.innerHTML = profiles
      .map(function (profile) {
        return [
          '<a href="/profile/' + profile.id + '/" ',
          'class="shrink-0 w-32 bg-white rounded-xl border border-slate-100 p-3 shadow-sm flex flex-col items-center justify-center gap-2 active:scale-95 transition-transform cursor-pointer group">',
          '<div class="size-10 rounded-full bg-green-50 text-primary flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-colors">',
          '<span class="material-symbols-outlined text-[20px]">straighten</span>',
          "</div>",
          '<span class="text-sm font-bold text-slate-800">',
          escapeHtml(profile.name),
          "</span>",
          '<span class="text-[10px] text-slate-400 font-medium">',
          escapeHtml(profile.category),
          "</span>",
          "</a>"
        ].join("");
      })
      .join("");
  }

  function renderCategories(categories) {
    if (!categoriesList) {
      return;
    }
    categoriesList.innerHTML = categories
      .map(function (category) {
        return [
          '<a href="/cat/' + escapeHtml(category.slug) + '/" ',
          'class="bg-white rounded-xl p-3 border border-slate-100 shadow-sm flex items-center gap-3 active:bg-slate-50 transition-colors cursor-pointer">',
          '<div class="shrink-0 size-10 rounded-lg bg-slate-100 flex items-center justify-center text-slate-500">',
          '<span class="material-symbols-outlined">forest</span>',
          "</div>",
          '<div class="flex flex-col">',
          '<span class="font-semibold text-sm text-slate-900">',
          escapeHtml(category.name),
          "</span>",
          "</div>",
          "</a>"
        ].join("");
      })
      .join("");
  }

  function renderProducts(products) {
    if (!productsList || !productsCount) {
      return;
    }
    productsCount.textContent = products.length + " Found";
    productsList.innerHTML = products
      .map(function (product) {
        var subtitle = [product.profile, product.category, product.option]
          .filter(Boolean)
          .join(" • ");
        return [
          '<a href="/product/' + product.id + '/" ',
          'class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 active:ring-2 active:ring-primary/20 transition-all cursor-pointer group">',
          '<div class="flex gap-4">',
          '<div class="shrink-0 w-20 h-20 rounded-xl bg-slate-50 p-1 border border-slate-100 relative overflow-hidden">',
          product.image_url
            ? '<img alt="' +
              escapeHtml(product.name) +
              '" class="w-full h-full object-contain mix-blend-multiply opacity-90 group-hover:scale-105 transition-transform duration-300" src="' +
              escapeHtml(product.image_url) +
              '"/>'
            : '<div class="w-full h-full bg-slate-100"></div>',
          "</div>",
          '<div class="flex-1 flex flex-col justify-between py-0.5">',
          "<div>",
          '<h4 class="text-slate-900 font-bold text-[15px] leading-tight mb-1">',
          escapeHtml(product.name),
          "</h4>",
          '<div class="text-xs text-slate-500">',
          escapeHtml(subtitle),
          "</div>",
          "</div>",
          '<div class="flex justify-between items-end mt-2">',
          '<span class="text-[10px] text-slate-400">I/N ' +
            escapeHtml(product.in_number) +
            "</span>",
          "</div>",
          "</div>",
          "</div>",
          "</a>"
        ].join("");
      })
      .join("");
  }

  function updateSections(payload) {
    if (!emptyState && !profilesSection && !categoriesSection && !productsSection) {
      return;
    }
    var hasResults =
      payload.products.length || payload.profiles.length || payload.categories.length;
    if (emptyState && input) {
      emptyState.classList.toggle("hidden", hasResults || input.value.length >= 2);
    }

    if (profilesSection) {
      profilesSection.classList.toggle("hidden", !payload.profiles.length);
    }
    if (categoriesSection) {
      categoriesSection.classList.toggle("hidden", !payload.categories.length);
    }
    if (productsSection) {
      productsSection.classList.toggle("hidden", !payload.products.length);
    }

    renderProfiles(payload.profiles);
    renderCategories(payload.categories);
    renderProducts(payload.products);
  }

  function runSearch() {
    if (!input) {
      return;
    }
    var query = input.value.trim();
    if (query.length < 2) {
      updateSections({ products: [], profiles: [], categories: [] });
      return;
    }
    fetch(window.searchApiUrl + "?q=" + encodeURIComponent(query))
      .then(function (response) {
        return response.json();
      })
      .then(function (payload) {
        updateSections(payload);
      })
      .catch(function () {
        updateSections({ products: [], profiles: [], categories: [] });
      });
  }

  if (input) {
    input.addEventListener("input", debounce(runSearch, 250));
  }
  if (clearButton && input) {
    clearButton.addEventListener("click", function () {
      input.value = "";
      updateSections({ products: [], profiles: [], categories: [] });
      input.focus();
    });
  }

  if (filterButtons.length) {
    setFilter("all");
  }

  function closeSearchOverlay() {
    if (!overlay) {
      return;
    }
    overlay.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
  }

  if (overlay) {
    openButtons.forEach(function (button) {
      button.addEventListener("click", function (event) {
        event.preventDefault();
        if (manageOverlay) {
          manageOverlay.classList.add("hidden");
        }
        if (toolOverlay) {
          toolOverlay.classList.add("hidden");
        }
        overlay.classList.remove("hidden");
        document.body.classList.add("overflow-hidden");
        if (input) {
          input.focus();
        }
      });
    });

    closeButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        closeSearchOverlay();
      });
    });
  }

  if (navHome) {
    navHome.addEventListener("click", function (event) {
      event.preventDefault();
      closeSearchOverlay();
      if (manageOverlay) {
        manageOverlay.classList.add("hidden");
      }
      if (toolOverlay) {
        toolOverlay.classList.add("hidden");
      }
    });
  }
});
