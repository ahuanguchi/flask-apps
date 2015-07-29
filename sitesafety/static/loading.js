(function () {
  "use strict";
  document.getElementById("submit").addEventListener("click", function () {
    var p = "<hr><p>Loading...</p><hr>";
    var results = document.getElementById("results");
    document.getElementsByTagName("form")[0].insertAdjacentHTML("afterend", p);
    if (results) {
      results.innerHTML = "";
    }
  });
}());
