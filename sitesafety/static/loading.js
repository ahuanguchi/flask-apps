(function () {
  "use strict";
  document.getElementById("submit").addEventListener("click", function () {
    var p = "<p>Loading...</p>";
    var results = document.getElementById("results");
    document.getElementsByTagName("form")[0].insertAdjacentHTML("afterend", p);
    if (results) {
      results.innerHTML = "";
    }
  });
}());
