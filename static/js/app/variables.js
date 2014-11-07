define(['jquery', 'underscore', 'typeahead', 'bootstrap.datepicker', 'bootstrap.tokenfield'], function($, _) {
    return {
        'init': function() {
            $(".edit-variable, .create-variable").click(function() {
                var url = $(this).data("form");
                $("#modal-variable").load(url, function() {
                    $(this).modal('show');
                });

                return false;
            });

            $("#modal-variable").on('show.bs.modal', function() {

                var replaceable_variables = new Bloodhound({
                    datumTokenizer: function(item) {
                        return Bloodhound.tokenizers.whitespace(item.value);
                    },
                    queryTokenizer: Bloodhound.tokenizers.whitespace,
                    limit: 20,
                    remote: {
                        url: '/variables/replaceable?q=%QUERY',
                        filter: function(list) {
                            return $.map(list, function(item) {
                                return { label: item.key, value: item.id, description: item.description };
                            });
                        }
                    }
                });

                // kicks off the loading/processing of `local` and `prefetch`
                replaceable_variables.initialize();
                var initial_tokens = function() {
                    var tokens = [];
                    var keysIds = $("#id_replaces_initial").val().split(", ");
                    return $.map(keysIds, function(keyId) {
                        var labelValue = keyId.split(":");
                        return { label: labelValue[0], value: labelValue[1] };
                    });
                };

                $('#id_replaces').tokenfield({
                    typeahead: [null, {
                        displayKey: 'label',
                        source: replaceable_variables.ttAdapter(),
                        templates: {
                            empty: "<div class='suggestion empty'><span class='description'>Inga träffar för sökord</span></div>",
                            suggestion: _.template([
                                "<div class='suggestion'><span class='key'><%- label %></span>",
                                "<span class='description' title='<%- description %>'><%- ellipsis(description, 120-(label.length+1)) %></span></div>"
                            ].join("\n"))
                        }
                    }]
                }).on('tokenfield:createtoken', function(e) {
                    /* Invalid entries have wrong value (same as label). */
                    if(e.attrs.label == e.attrs.value)
                        e.preventDefault();
                }).tokenfield('setTokens', initial_tokens());

                $('#id_replaces').on('tokenfield:initialize', function(event) {
                    $(this).find(".tt-dropdown-menu").attr("style", "position:relative; top:100%; left:0; zIndex:100; display:none;")
                });

                $('.form-group.active_from .input-group.date').datepicker({
                    format: "yyyy-mm-dd",
                    weekStart: 1,
                    language: "sv"
                });
                $('.form-group.active_to .input-group.date').datepicker({
                    format: "yyyy-mm-dd",
                    weekStart: 1,
                    language: "sv"
                });

                $("#replaced_by").click(function(event) {
                    event.preventDefault();
                    var url = $(this).data("form"); // get form
                    $("#modal-variable").load(url, function() { // load the url into the modal
                        $(this).modal('show'); // display the modal on url load
                    });
                    return false; // prevent the click propagation
                });

                $("#save_and_activate").click(function(event) {
                    $("#submit_action").val("save_and_activate");
                });

                $("#delete").click(function(event) {
                    $("#submit_action").val("delete");
                });

                $('.edit-variable-form').submit(function(event) {
                    event.preventDefault();

                    var self = this;
                    $(self).find(".form-group").removeClass("has-feedback has-error");
                    $(self).find(".form-validation").text("");

                    $.ajax({
                        type: $(this).attr('method'),
                        url: this.action,
                        data: $(this).serialize(),
                        context: this,
                        success: function(data, status) {
                            if(data.errors) {
                                $(".form-group").each(function() {
                                    var field = $(this).attr("data-field")
                                    if(data.errors.hasOwnProperty(field)) {
                                        $(this).addClass("has-feedback has-error");
                                        $(this).find(".form-validation").text(data.errors[field]);
                                    }
                                })
                                if(data.errors.hasOwnProperty("__all__")) {
                                    $(".general-errors").text(data.errors["__all__"]);
                                }
                            } else {
                                console.info("saved variable: ", data);
                                $('#modal-variable').modal('hide');
                                window.location.reload(true);
                            }
                        },
                        error: function(data, status) {
                            console.info("An error occured while saving variable!")
                        }
                    });
                    return false;
                });
            });
        }
    }
});