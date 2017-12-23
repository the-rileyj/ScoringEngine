function set_form_save(form_name) {
     $("#" + form_name + "-save").on('click', function (e) {
        var url = "/config";
    
        $.ajax({
            type: "POST",
            url: url,
            data: $("#" + form_name + "-form").serialize(),
            success: function(data) {
                alert(data);
            }
        });
        e.preventDefault();
    });
}

$(document).ready(function() {
    set_form_save("team");
    set_form_save("domain");
    set_form_save("web-user");
    set_form_save("service");
    set_form_save("check");
    set_form_save("input");
    set_form_save("checkio");
    set_form_save("credential");
});
