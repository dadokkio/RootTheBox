/* Add click events */
$(document).ready(function () {
  /* Scenario */
  $("a[id^=edit-scenario-button]").click(function () {
    $("#scenario-uuid").val($(this).data("uuid"));
    $("#scenario-name").val($(this).data("name"));
    $("#scenario-description").val($(this).data("description"));
    let starter = $(this).data("starter");
    switch (starter) {
      case 1:
        $("#starter").val(1);
        $("#case-enable-icon").addClass("fa-check-square-o");
        $("#case-enable-icon").removeClass("fa-square-o");
        $("#case-disable-icon").removeClass("fa-check-square-o");
        $("#case-disable-icon").addClass("fa-square-o");
        break;
      case 0:
        $("#starter").val(0);
        $("#case-enable-icon").removeClass("fa-check-square-o");
        $("#case-enable-icon").addClass("fa-square-o");
        $("#case-disable-icon").addClass("fa-check-square-o");
        $("#case-disable-icon").removeClass("fa-square-o");
        break;
    }
  });

  $("#case-enable").click(function () {
    $("#starter").val(1);
    $("#case-enable-icon").addClass("fa-check-square-o");
    $("#case-enable-icon").removeClass("fa-square-o");
    $("#case-disable-icon").addClass("fa-square-o");
    $("#case-disable-icon").removeClass("fa-check-square-o");
  });

  $("#case-disable").click(function () {
    $("#starter").val(0);
    $("#case-enable-icon").removeClass("fa-check-square-o");
    $("#case-enable-icon").addClass("fa-square-o");
    $("#case-disable-icon").removeClass("fa-square-o");
    $("#case-disable-icon").addClass("fa-check-square-o");
  });

  $("#edit-scenario-submit").click(function () {
    $("#edit-scenario-form").submit();
  });

  $("a[id^=delete-scenario-button]").click(function () {
    $("#delete-scenario-uuid").val($(this).data("uuid"));
  });

  $("#delete-scenario-submit").click(function () {
    $("#delete-scenario-form").submit();
  });

  /* Option */
  $("a[id^=edit-option-button]").click(function () {
    $("#option-uuid").val($(this).data("uuid"));
    $("#option-name").val($(this).data("name"));
    $("#option-description").val($(this).data("description"));
  });

  $("#edit-option-submit").click(function () {
    $("#edit-option-form").submit();
  });

  $("a[id^=delete-option-button]").click(function () {
    $("#delete-option-uuid").val($(this).data("uuid"));
  });

  $("#delete-option-submit").click(function () {
    $("#delete-option-form").submit();
  });
});
