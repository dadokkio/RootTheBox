$(document).ready(function () {
  $(function () {
    var reader = new commonmark.Parser({ smart: true });
    var writer = new commonmark.HtmlRenderer({
      safe: true,
      softbreak: "<br />",
    });
    $('[data-toggle="tooltip"]').tooltip();
    $(".toolbar").markdownToolbar(false, reader, writer);
  });

  $("#icon-url-success").click(function () {
    $("#icon_url").val("SUCCESS");
    $("#icon-url-success-icon").addClass("fa-check-square-o");
    $("#icon-url-success-icon").removeClass("fa-square-o");
    $("#icon-url-info-icon").addClass("fa-square-o");
    $("#icon-url-info-icon").removeClass("fa-check-square-o");
    $("#icon-url-warning-icon").addClass("fa-square-o");
    $("#icon-url-warning-icon").removeClass("fa-check-square-o");
    $("#icon-url-error-icon").addClass("fa-square-o");
    $("#icon-url-error-icon").removeClass("fa-check-square-o");
  });

  $("#icon-url-info").click(function () {
    $("#icon_url").val("INFO");
    $("#icon-url-success-icon").addClass("fa-square-o");
    $("#icon-url-success-icon").removeClass("fa-check-square-o");
    $("#icon-url-info-icon").removeClass("fa-square-o");
    $("#icon-url-info-icon").addClass("fa-check-square-o");
    $("#icon-url-warning-icon").addClass("fa-square-o");
    $("#icon-url-warning-icon").removeClass("fa-check-square-o");
    $("#icon-url-error-icon").addClass("fa-square-o");
    $("#icon-url-error-icon").removeClass("fa-check-square-o");
  });

  $("#icon-url-warning").click(function () {
    $("#icon_url").val("WARNING");
    $("#icon-url-success-icon").addClass("fa-square-o");
    $("#icon-url-success-icon").removeClass("fa-check-square-o");
    $("#icon-url-info-icon").addClass("fa-square-o");
    $("#icon-url-info-icon").removeClass("fa-check-square-o");
    $("#icon-url-warning-icon").removeClass("fa-square-o");
    $("#icon-url-warning-icon").addClass("fa-check-square-o");
    $("#icon-url-error-icon").addClass("fa-square-o");
    $("#icon-url-error-icon").removeClass("fa-check-square-o");
  });

  $("#icon-url-error").click(function () {
    $("#icon_url").val("ERROR");
    $("#icon-url-success-icon").addClass("fa-square-o");
    $("#icon-url-success-icon").removeClass("fa-check-square-o");
    $("#icon-url-info-icon").addClass("fa-square-o");
    $("#icon-url-info-icon").removeClass("fa-check-square-o");
    $("#icon-url-warning-icon").addClass("fa-square-o");
    $("#icon-url-warning-icon").removeClass("fa-check-square-o");
    $("#icon-url-error-icon").removeClass("fa-square-o");
    $("#icon-url-error-icon").addClass("fa-check-square-o");
  });

  /* Popovers */
  $("#news-title").popover({ placement: "right", trigger: "hover" });
  $("#message").popover({ placement: "right", trigger: "hover" });
  $("#icon-url-type-button").popover({ placement: "right", trigger: "hover" });
});
