$(document).ready(function () {
  /* Category Item */
  $("a[id^=edit-news-item-button]").click(function () {
    $("#edit-news-item-uuid").val($(this).data("uuid"));
    $("#edit-news-item-title").val($(this).data("title"));
    $("#edit-news-message").val($(this).data("message"));
    let status = $(this).data("icon");
    $("#icon_url").val(status);
    switch (status) {
      case "SUCCESS":
        $("#icon-url-success-icon").addClass("fa-check-square-o");
        $("#icon-url-success-icon").removeClass("fa-square-o");
        break;
      case "INFO":
        $("#icon-url-info-icon").addClass("fa-check-square-o");
        $("#icon-url-info-icon").removeClass("fa-square-o");
        break;
      case "WARNING":
        $("#icon-url-warning-icon").addClass("fa-check-square-o");
        $("#icon-url-warning-icon").removeClass("fa-square-o");
        break;
      case "ERROR":
        $("#icon-url-error-icon").addClass("fa-check-square-o");
        $("#icon-url-error-icon").removeClass("fa-square-o");
        break;
    }
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

  $("#edit-news-item-submit").click(function () {
    $("#edit-news-item-form").submit();
  });

  $("a[id^=delete-news-button]").click(function () {
    $("#delete-news-uuid").val($(this).data("uuid"));
  });

  $("#delete-news-submit").click(function () {
    $("#delete-news-form").submit();
  });
});
