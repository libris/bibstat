/**
 * Javascript functions for libstat
 */
$(document).ready(function() { 
  
	/* Make Variables table sortable */
  $(".table.variables").addClass("tablesorter").tablesorter({
	  sortList: [[0,0]]
  });
  
  /* Make Survey Responses table sortable */
  $(".table.survey_responses").addClass("tablesorter").tablesorter({
	  headers: {
		  // disable sorting of the first column
		  0 : {
			  sorter: false
		  }
	  },
  	  sortList: [[3,0]]
  });
  $(".table.survey_responses .select-all").change(function() {
	  var checkboxes = $(".select-one");
	  if($(this).is(":checked")) {
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