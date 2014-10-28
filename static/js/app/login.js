define(["jquery"], function ($) {
    return {
        init: function () {
            $(".login-form").submit(function (e) {
                e.preventDefault();
                console.log("Submitting login");
                var self = this;
                $(self).find(".errors").text("");
                $.ajax({
                    type: "POST",
                    url: "/login",
                    data: $(self).serialize(),
                    success: function (data) {
                        if (data.errors) {
                            $(self).find(".errors.username").text(data.errors.username);
                            $(self).find(".errors.password").text(data.errors.password);
                            $(self).find(".errors.all").text(data.errors.__all__);
                        }
                        else {
                            window.location = data.next
                        }
                    },
                    error: function () {
                        console.info("An error occurred!")
                    }
                });
                return false;
            });

            /* Open login modal on redirect */
            if($(".show-login-modal").length == 1) {
                var sPageUrl = window.location.search.substring(1);
                var urlParams = {};

                if(sPageUrl.length > 0) {
                    $.each(sPageUrl.split("&"), function(index, p) {
                        var key_value = p.split("=");
                        urlParams[key_value[0]] = key_value[1];
                    });
                }

                if("next" in urlParams) {
                    var url = $(".show-login-modal").data("form") + "?next=" + urlParams["next"];
                    $("#loginModal").load(url, function() {
                        $(this).modal("show");
                        var nextInput = $(this).find("input[name=next]");
                    });
                }
            }

            /* Login */
            $(".show-login-modal").click(function(e) {
                e.preventDefault();
                $("#loginModal").modal("show");
                return false;
            });

            /* Focus username input field when login modal is shown. */
            $("#loginModal").on("shown.bs.modal", function() {
                $("#username").focus();
            });
        }
    }
});