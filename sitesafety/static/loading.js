(function () {
  "use strict";
  document.getElementById("submit").addEventListener("click", function () {
    var p = "<hr><p id='loading'>Loading...</p><hr>";
    var results = document.getElementById("results");
    if (!document.getElementById("loading")) {
      document.getElementById("mainform").insertAdjacentHTML("afterend", p);
    }
    if (results) {
      results.innerHTML = "";
    }
  });
}());
