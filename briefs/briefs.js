(function () {
  "use strict";
  var search = document.getElementById("brief-search");
  var country = document.getElementById("brief-country");
  var cards = Array.prototype.slice.call(document.querySelectorAll("[data-brief-card]"));
  var count = document.getElementById("brief-visible-count");
  var empty = document.getElementById("brief-empty");

  function applyFilters() {
    var q = search ? search.value.trim().toLowerCase() : "";
    var cc = country ? country.value : "";
    var visible = 0;
    cards.forEach(function (card) {
      var matchesText = !q || (card.getAttribute("data-search") || "").indexOf(q) !== -1;
      var matchesCountry = !cc || card.getAttribute("data-country") === cc;
      var show = matchesText && matchesCountry;
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (count) count.textContent = String(visible);
    if (empty) empty.classList.toggle("visible", visible === 0);
  }

  if (search) search.addEventListener("input", applyFilters);
  if (country) country.addEventListener("change", applyFilters);

  document.querySelectorAll("[data-copy-url]").forEach(function (button) {
    button.addEventListener("click", function () {
      var url = button.getAttribute("data-copy-url") || location.href;
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(url).then(function () {
        var previous = button.textContent;
        button.textContent = "Link copied";
        window.setTimeout(function () { button.textContent = previous; }, 1600);
      });
    });
  });
}());
