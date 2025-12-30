document.addEventListener("DOMContentLoaded", function () {
  var inNumber = window.productPageInNumber || "";
  if (inNumber) {
    JsBarcode("#barcode", inNumber, {
      format: "CODE128",
      lineColor: "#111827",
      background: "transparent",
      width: 3,
      height: 70,
      displayValue: false,
      margin: 0
    });
  }

  function updateOptionLayout() {
    var container = document.querySelector("[data-option-container]");
    if (!container) {
      return;
    }
    var buttons = Array.from(container.querySelectorAll("[data-option-button]"));
    if (!buttons.length) {
      return;
    }
    buttons.forEach(function (button) {
      button.style.flex = "0 0 auto";
      button.style.width = "auto";
    });

    var gapValue = window.getComputedStyle(container).gap || "12px";
    var gap = parseFloat(gapValue) || 12;
    var containerWidth = container.clientWidth;
    var maxWidth = Math.max.apply(
      null,
      buttons.map(function (button) {
        return button.getBoundingClientRect().width;
      })
    );
    if (!containerWidth || !maxWidth) {
      return;
    }
    var columns = Math.min(3, Math.floor((containerWidth + gap) / (maxWidth + gap)));
    columns = Math.max(1, columns);
    var columnWidth = (containerWidth - gap * (columns - 1)) / columns;

    buttons.forEach(function (button) {
      button.style.flex = "0 0 " + columnWidth + "px";
      button.style.width = columnWidth + "px";
    });
  }

  updateOptionLayout();
  window.addEventListener("resize", function () {
    window.requestAnimationFrame(updateOptionLayout);
  });
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(updateOptionLayout);
  }
});
