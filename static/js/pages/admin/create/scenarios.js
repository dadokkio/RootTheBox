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

  /* Popovers */
  $("#scenario-name").popover({ placement: "right", trigger: "hover" });
  $("#description").popover({ placement: "right", trigger: "hover" });
  $("#starter-button").popover({ placement: "right", trigger: "hover" });

  $("#case-enable").click(function () {
    $("#starter").val(1);
    $("#case-enable-icon").removeClass("fa-square-o");
    $("#case-enable-icon").addClass("fa-check-square-o");
    $("#case-disable-icon").removeClass("fa-check-square-o");
    $("#case-disable-icon").addClass("fa-square-o");
  });
  $("#case-disable").click(function () {
    $("#starter").val(0);
    $("#case-disable-icon").removeClass("fa-square-o");
    $("#case-disable-icon").addClass("fa-check-square-o");
    $("#case-enable-icon").removeClass("fa-check-square-o");
    $("#case-enable-icon").addClass("fa-square-o");
  });
});
