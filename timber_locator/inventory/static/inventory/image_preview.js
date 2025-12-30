(function () {
  function initPreview(container) {
    var input = container.querySelector("[data-image-input]");
    var preview = container.querySelector("[data-image-preview]");
    if (!input || !preview) {
      return;
    }

    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file) {
        preview.src = "";
        preview.classList.add("hidden");
        return;
      }
      if (!file.type || file.type.indexOf("image/") !== 0) {
        preview.src = "";
        preview.classList.add("hidden");
        return;
      }

      var reader = new FileReader();
      reader.onload = function (event) {
        preview.src = event.target.result;
        preview.classList.remove("hidden");
      };
      reader.readAsDataURL(file);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var containers = document.querySelectorAll("[data-image-preview-container]");
    containers.forEach(initPreview);
  });
})();
