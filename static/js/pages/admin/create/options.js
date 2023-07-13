$(document).ready(function () {
  /* markdown */
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
  $("#option-name").popover({ placement: "right", trigger: "hover" });
  $("#description").popover({ placement: "right", trigger: "hover" });
  $("#scenario-uuid").popover({ placement: "right", trigger: "hover" });
  $("#next-scenario-uuid").popover({ placement: "right", trigger: "hover" });
});
