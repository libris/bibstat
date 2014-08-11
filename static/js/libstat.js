/**
 * Javascript functions for libstat
 */
$(document).ready(function() {

	/* Open login modal on redirect */
	console.info(window.location.search);
	if($(".show-login-modal").length == 1) {
		var sPageUrl = window.location.search.substring(1);
		var urlParams = {};
		sPageUrl.split("&").forEach(function(p) {
			var key_value = p.split("=");
			urlParams[key_value[0]] = key_value[1];
		})
		if("next" in urlParams) {
			var url = $(".show-login-modal").data("form") + "?next=" + urlParams["next"];
			$("#loginModal").load(url, function() {
				$(this).modal("show");
				var nextInput = $(this).find("input[name=next]");
//				nextInput.attr("value", urlParams["next"]);
			});
		}
	}
	
	/* Login */
	$(".show-login-modal").click(function(e) {
		e.preventDefault();
		var url = $(this).data("form");
		$("#loginModal").load(url, function() {
			$(this).modal("show");
		});
		return false;
	});
	
	/* Make Variables table sortable */
	$(".table.variables").addClass("tablesorter").tablesorter({
		sortList : [ [ 0, 0 ] ]
	});

	/* Make Survey Responses table sortable */
	$(".table.survey_responses").addClass("tablesorter").tablesorter({
		headers: {
			// disable sorting of the first and last column
			0: {
				sorter: false
			},
			5: {
				sorter: false
			}
		},
		sortList : [ [ 3, 0 ] ]
	});
	$(".table.survey_responses .select-all").change(function() {
		var checkboxes = $(".select-one");
		if ($(this).is(":checked")) {
			checkboxes.prop("checked", "checked");
		} else {
			checkboxes.removeAttr("checked");
		}

	});

	/* Edit variable */
	$(".edit-variable").click(function(ev) { // for each edit contact url
		ev.preventDefault(); // prevent navigation
		var url = $(this).data("form"); // get the contact form url
		$("#editVariableModal").load(url, function() { // load the url into the modal
			$(this).modal('show'); // display the modal on url load
		});
		return false; // prevent the click propagation
	});

});