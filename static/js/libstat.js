/**
 * Javascript functions for libstat
 */
$(document).ready(function() { 
  
	/* Make Variables table sortable */
  $(".table.variables").addClass("tablesorter").tablesorter();
  
  /* Edit variable */
  $(".edit-variable").click(function(ev) { // for each edit contact url
  	console.info("clickety click!")
      ev.preventDefault(); // prevent navigation
      var url = $(this).data("form"); // get the contact form url
      console.info("url is", url)
      $("#editVariableModal").load(url, function() { // load the url into the modal
          $(this).modal('show'); // display the modal on url load
      });
      return false; // prevent the click propagation
  });

  $('.edit-variable-form').on('submit', function() {
      $.ajax({ 
          type: $(this).attr('method'), 
          url: this.action, 
          data: $(this).serialize(),
          context: this,
          success: function(data, status) {
              $('#editVariableModal').html(data);
          }
      });
      return false;
  });
  
}); 