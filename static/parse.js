/* globals $ */

(function () {
  "use strict";
  
  function display(sw) {
    var communityBlock;
    $("#sw-page").html("<a href=\"" + sw.page + "\" target=\"_blank\">Norton Safe Web &ndash; " + sw.url + "</a>");
    if (sw.ico) {
      $("#sw-ico").html(sw.ico);
    } else {
      $("#sw-ico").html("");
    }
    $("#sw-summary").html(sw.summary);
    if (sw.community) {
      if (sw.community.indexOf("0.0") === -1) {
        communityBlock = sw.community;
      } else {
        communityBlock = "<p>Not yet rated</p>";
      }
      if (sw.summary.slice(0, 4) !== "None") {
        communityBlock += "<p><a href=\"http://safeweb.norton.com/reviews?url=" + encodeURIComponent(sw.url) + "\" target=\"_blank\">View community reviews</a></p>";
      }
      $("#sw-community").html(communityBlock);
    } else {
      $("#sw-community").html("");
    }
  }

  $.ajax({
    url: "http://query.yahooapis.com/v1/public/yql",
    jsonp: "callback",
    dataType: "jsonp",
    data: {
      q: "select * from htmlstring where url='http://safeweb.norton.com/report/show?url=" + window.domain + "' and xpath='//div[@id=\"wrap\"]'",
      format: "json",
      env: "store://datatables.org/alltableswithkeys"
    },
    success: function (response) {
      var $data = $(response.query.results.result.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, "").replace(/src=['"].+?['"]/gi, "src=''"));
      var result = {};
      result.page = "http://safeweb.norton.com/report/show?url=" + encodeURIComponent(window.domain);
      result.url = $data.find("a.nolink").eq(0).prop("title");
      if (!result.url) {
        result.summary = "None &ndash; If this was caused by rate limiting, you can click on the link above to visit Norton's report manually.";
        display(result);
        return;
      }
      result.ico = $data.find("div.big_rating_wrapper > img").eq(0).prop("alt").replace("ico", "").replace("NSec", "Norton Sec");
      result.summary = $data.find("div.span10").eq(0).html();
      if (result.summary) {
        result.summary = result.summary.replace(/<\/?b>/gi, "");
      } else {
        result.summary = "None";
        display(result);
        return;
      }
      result.community = $data.find("div.community-text").eq(0).html();
      display(result);
    }
  });
})();
