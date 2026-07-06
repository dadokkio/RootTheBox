$(document).ready(function() {
    var reader = new commonmark.Parser({smart: true});
    var writer = new commonmark.HtmlRenderer({safe: true});

    /* Markdown */
    $(".markdown").each(function() {
        var parsed = reader.parse($(this).text());
        var formatted = writer.render(parsed).trim();
        formatted = formatted.replaceAll("<a href=", '<a target="_blank" href=');
        formatted = rtbRenderShortcodes(formatted);
        $(this).html(formatted);
    });

    /* Shortcode [spawn:challenge] → iframe verso lo spawner */
    function rtbGetOrCreatePlayerId() {
        var pid = localStorage.getItem('ctf_player_id');
        if (pid && /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(pid)) {
            return pid;
        }
        pid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0;
            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
        localStorage.setItem('ctf_player_id', pid);
        return pid;
    }

    function rtbRenderShortcodes(html) {
        var pid = rtbGetOrCreatePlayerId();
        return html.replace(/\[spawn:([a-z0-9_-]+)\]/g, function(match, challenge) {
            return '<iframe src="/spawner/launch?challenge=' + challenge + '&pid=' + pid + '" '
                 + 'style="width:100%;height:240px;border:none;border-radius:8px" '
                 + 'loading="lazy"></iframe>';
        });
    }

    /* Flags */
    $("#capture-file-flag-modal").on('shown.bs.modal', function () {
        $("#flag-file").focus()
    });

    $("a[id^=capture-file-flag-button]").click(function() {
        $("#capture-file-flag-uuid").val($(this).data("uuid"));
    });

    $("#capture-file-flag-submit").click(function() {
        $("#capture-file-flag-form").submit();
    });

    $("#capture-text-flag-modal").on('shown.bs.modal', function () {
        $("#flag-token").focus()
    });

    $("a[id^=capture-text-flag-button]").click(function() {
        $("#capture-text-flag-uuid").val($(this).data("uuid"));
    });

    $("#capture-text-flag-submit").click(function() {
        $("#capture-text-flag-form").submit();
    });

    $("a[id^=capture-choice-flag-button]").click(function() {
        $("#capture-choice-flag-uuid").val($(this).data("uuid"));
        $("#choiceinput").empty();
        var choices = $(this).data("choices");
        for (choice in choices) {
            $("#choiceinput").append('<div><input required name="multichoice" type="radio" style="margin-top: 0;" value="' + choices[choice].replace(/"/g, "__quote__") + '" />&nbsp;&nbsp;' + choices[choice] + "</div><br/>");
        }
    });

    $("#capture-choice-flag-submit").click(function() {
        $("#choice-flag-token").val($('input[name=multichoice]:checked').val());
        $("#capture-choice-flag-form").submit();
    });

    $(".flag-expand").click(function() {
        var isHovered = $('.playstory').filter(function() {
            return $(this).is(":hover");
        });
        if ($('.playstory').length === 0 || isHovered.length === 0) {
            $(this).next(".flag-collapse").toggle();
            $(this).next().next(".flag-collapse").toggle();
        }
    });

    $(".showflag").click(function() {
        $("#showknownname").text($(this).data("name"));
        $("#showknownflag").text("Flag: " + $(this).data("flag"));
    });

    /* Hints */
    $("a[id^=purchase-hint-button]").click(function() { 
        $("#purchase-hint-uuid").val($(this).data("uuid"));
        var price = $(this).data("price");
        hintdialog(price);
    });
    $("a[id^=purchase-flag-hint-button]").click(function() {
        //index is different on flags
        $("#purchase-hint-uuid").val($(this).data("uuid"));
        var price = $(this).data("price");
        hintdialog(price);
    });
    $("#purchase-hint-submit").click(function() {
        $("#purchase-hint-form").submit();
    });

    function hintdialog(price) {
        var bank = $("#hintbanking").val();
        if (price === "0") {
            $("#purchase-hint-text").text("This hint is free.  Would you like to take it?");
        } else if (bank == 'true') {
            $("#purchase-hint-text").text("Would you like to purchase this hint for $"+price+"?");
        } else {
            $("#purchase-hint-text").text("Would you like to take this hint for a deduction of "+price+" points?");
        }
    }
    $('td').on('mouseenter mouseleave', function(e) {
        //Allows the hover background to include the flag hints
        var tbody = $(this).closest("tbody");
        if (tbody.hasClass("flagbody")) {
            if ($(this).hasClass("hidehovercolor")) {
                tbody.css('background-color', $(this).next().css('background-color'));
            } else {
                tbody.css('background-color', $(this).css('background-color'));
            }
        }
    });
    $('tbody').on('mouseleave', function(e) {
        $(this).css('background-color','');
    });

    if($('#box-materials').length > 0)
    {
        var data = {'_xsrf': getCookie("_xsrf")}
        var subdir = $('#box-materials').data("subdir");
        $.post('/materials/' + subdir + "/", data, function(response) {
            $('#box-materials-tree').jstree({
                'core' : {
                    'themes' : { name : 'default-dark' },
                    'data' : $.parseJSON(response)["children"]
                }
            });
        });
    }
    if ( window.history.replaceState ) {
        location.hash = location.hash;
        window.history.replaceState( null, null, window.location.href );
    }
});
